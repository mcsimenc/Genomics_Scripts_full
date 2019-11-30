#!/usr/local/bin/perl
use strict;
use Switch;

# perl convert.pl input.ext output.ext [-f "fmt" -l -u -b -chr -strip "str"]
# genomic interval conversion utility by William Pu
#  where .ext will tell the format of the input and output files
#  and -f fmt is an optional output format to use when the output format extension is not known.
# Known formats: .bed (3-12) .gff .gff3 .gtf .tag
# -l lowercase (chrx), -u uppercase (chrX), -b buffered (chr01), -chr (add chr to chr field if not already present)
# fmt: c1 +3 +4 5 "TEXT" 6 9 2 where numbers indicate columns and items between quotes indicate text to insert
# the c indicates the chromosome field, the + or - indicates add one or subtract one from the number for 0 based or 1 based genomic interval conversions.
# comment lines in files starting with '#' are simply copied to the new file

# examples:
# convert bed to gff:
#     perl convert.pl input.bed output.gff 
# convert bed to bed but change chr to uppercase
#     perl convert.pl input.bed output.bed -u
# use a custom format output string
#     perl convert.pl input.gff output.txt -f "c0 -3 4 2 5 6"
#     where c0 means the first output column is the chromosome field and is the same as the first (zeroth) input column
#     and -3 means that the second output column (the start field) is the same as the fourth (3rd starting from 0) input column, and one is subtracted from the value to change from 1-base to 0-base counting in gff vs bed

# txt: unknown format, rearrange columns according to the format string
# bed: chr start end name score strand thickstart thickend itemRGB blockCount blockSizes blockStarts
# gff: chr source feature start end score strand frame group
# gtf: chr source feature start end score strand frame type/value pairs (type "value"; type1 "value1" etc)
# gff3 chr source feature start end score strand frame type/value pairs (type=value;type1=value1 etc)
# tagalign: chrom chromStart chromEnd sequence(string) score(integer) strand    (+ or -)

# possible conversions: (gff/gtf/gff3 are handled the same)
# bed2bed proc 00	c0 1 2 3 4 5 6 7 8 9 10 11 12
# bed2gff proc 01	c0 bed2gff 3 +1 2 s4 t5 _. 3
# bed2tag proc 02	c0 1 2 _AAAA s4 t5					s is score, t is strand, text after _ is output directly as text
# gff2bed proc 10	c0 -3 4 2 5 6
# gff2gff proc 11	c0 1 2 3 4 5 6 7 8
# gff2tag proc 12	c0 -3 4 _TEXT 5 6
# tag2bed proc 20	c0 1 2 _. 4 5
# tag2gff proc 21	c0 tag2gff . +1 2 4 5 _. _.
# tag2tag proc 22	c0 1 2 3 4 5
# txt2txt rearrange based on format string proc 33
my %filetype= (
	"bed"=>0,
	"gff"=>1,
	"gtf"=>1,
	"gff3"=>1,
	"tag"=>2,
	"txt"=>3,
	);
		
# read parameters, assign output variables
my $infile = $ARGV[0] ;
if ($infile eq "") {
	report_error("invalid input file");
}
my $outfile = $ARGV[1] ;
if ($outfile eq "") {
	report_error("invalid output file");
}
my $case="d";
my $buffer=0;
my $fmt="";
my $chr_prefix="";
my $strip_str = "";
for (my $i=2;$i<@ARGV;$i++) {
	switch($ARGV[$i]) {
		case "-l"	{ $case = "l" }
		case "-u"	{ $case = "u" }
		case "-b"	{ $buffer = 1 }
		case "-f"	{ $i++; $fmt = $ARGV[$i++] }
		case "-chr" { $chr_prefix="chr" }
		case "-strip" { $i++; $strip_str = $ARGV[$i++] }
		else { report_error("invalid parameter " . $ARGV[$i]) }
	}
}

my @array;
my $in_ext;
my $out_ext;
my $proc;

@array = split(/\./, $infile);
$in_ext = $array[@array-1];
if (exists($filetype{$in_ext})) {
	$proc=10*$filetype{$in_ext};
} else {report_error("invalid input file extension ". $in_ext );}

@array = split(/\./, $outfile);
$out_ext = $array[@array-1];
if (exists($filetype{$out_ext})) {
	$proc=$proc+$filetype{$out_ext};
} else {report_error("invalid output file extension ". $out_ext );}

if ($in_ext eq "txt" || $out_ext eq "txt") {
	$proc = 33;
}

# open files
unless ( open( INFILE, $infile ) ) {
		report_error("Could not open file $infile");
	}
unless ( open( OUTFILE, ">",$outfile ) ) {
		report_error("Could not open file $outfile");
	}

my @field;
my $i;
my @f;
my $e;								# $e is the value of the field indicated in the fmt string
my $prefix;
my $outline = "";

switch($proc) {
	case 0	{ $fmt = 'c0 1 2 3 (4 (5 (6 (7 (8 (9 (10 (11 (12'; }
	case 1	{ $fmt = 'c0 _bed2gff 3 +1 2 s4 t5 _. 3'; }
	case 2	{ $fmt = 'c0 1 2 _AAAA s4 t5'; }
	case 10	{ $fmt = 'c0 -3 4 2 5 6'; }
	case 11	{ $fmt = 'c0 1 2 3 4 5 6 7 8'; }
	case 12 { $fmt = 'c0 -3 4 _AAAA 5 6'; }
	case 20	{ $fmt = 'c0 1 2 _. 4 5';}
	case 21	{ $fmt = 'c0 _tag2gff _. +1 2 4 5 _. _.'; }
	case 22	{ $fmt = 'c0 1 2 3 4 5'; }
	case 33 { if ($fmt eq "") {report_error("for txt files you need to specify a fmt string using -f fmt")}}
	else { report_error("unrecognized proc $proc") }
}
@f=split(/ /,$fmt);

while (my $line = <INFILE>) { 		# read a line
	chomp($line);
	if (substr($line,0,1) eq "#" or $line eq "") {	# ignore if first char is # or if line blank
		$outline="\t". $line;
	} else {
		@field=split(/\t/,$line);		# split into fields
		
	# write the line
		for ($i=0; $i<@f; $i++) {			# go through the output format		
			switch(substr($f[$i],0,1)) {
				case "c" {
					$e=$field[substr($f[$i],1)];
					if ($strip_str ne "") {
						$e =~ s/$strip_str//; 
						}	
					if (substr($e,0,3) eq "chr") {
						$prefix = "chr";
						$e = substr($e,3);
					} else {
						$prefix = $chr_prefix;			# if no chr prefix then add one if -chr flag set
					}
					if (substr($e,0,1) =~ /[a-zA-Z]/ )	{ # is it a letter?
						switch($case) {
							case "u" {	$e = uc($e); }				# force upper case
							case "l" {	$e = lc($e); }				# force lower case
						}
					} else {
						if ($buffer == 1 ) {
							$e = substr ("00".$e,-2);				# if it a number and -b flag then buffer to 2 digits
					}	}
					$e = $prefix . $e;
				}
				case "_" {								# output the part of the fmt string following _ as text
					$e=substr($f[$i],1);
				}
				case "+" {								# increment the number by 1
					$e=$field[substr($f[$i],1)]+1;
				}
				case "-" {								# decrement the number by 1
					$e=$field[substr($f[$i],1)]-1;
				}
				case "s" {								# score
					if (substr($f[$i],1) >= @field || substr($f[$i],1) eq "") {		# does the score field exist in the input (eg bed file may not have score)
						$e=0;														# if no then force the score field to be 0
					} else {
						$e=$field[substr($f[$i],1)];								
					}
				}
				case "t" {								# strand
					if (substr($f[$i],1) >= @field || substr($f[$i],1) eq "") {		# does the strand field exist in the input (eg bed file may not have score)
						$e="+";														# if no then force the strand field to be +
					} else {			
						$e=$field[substr($f[$i],1)];								
					}
				}
				case "(" {															# optional field
					if (substr($f[$i],1) >= @field || substr($f[$i],1) eq "") {		# does the optional field exist in the input (eg bed file may not have score)
						$e="";														# if no then leave it blank;
					} else {
						$e=$field[substr($f[$i],1)];								# otherwise force the strand field
					}
				}
				else {									# otherwise just put out the value of the field at the position indicated in the fmt string
					if ($f[$i] =~ /\d+/) {				# make sure fmt string is ok
						$e=$field[$f[$i]];
						if ($e eq "") {					# if the field is empty then output '.'
							$e='.';
						}
					} else {
						report_error("bad format string $fmt");
					}
				}
			}
			if ($e ne "") {
				$outline = $outline . "\t" . $e;
			}
		}
	}
	print OUTFILE substr($outline,1) . "\n";				# removes leading tab;
	$outline = "";
}	
# close files
close INFILE;
close OUTFILE;
exit;

sub report_error {
	print "@_\n";
	print "usage: perl convert.pl input.ext output.ext [-f \"fmt\" -l -u -b -chr -strip \"str\"]\n";
	print "allowed extensions: bed tag gff txt\n";
	print "-f \"fmt\" indicate format of output e.g. \"0 2 1 3 5 4\" ";
	print "-l: force chr to be lower case\n";
	print "-u: force chr to be upper case\n";
	print "-b: buffer chr to 2 digits\n";
	print "-chr: prefix chromosome field with chr\n";
	print "-strip: strip \"str\" from chromosome field";
	die;
}
