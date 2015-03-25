#!/usr/bin/perl
use locale;
use warnings;
use Encode qw(encode decode);
use open qw(:std :utf8);
use utf8;

print "Enter the file with the functional words\n";
#$fwords = <STDIN>;
$fwords = 'functional words.txt';
chomp $fwords;
open FWORDS, "$fwords";
@farray = <FWORDS>;
foreach (@farray) {
                chomp;
		s/Σ$/ς/g;		# converts to greek final -s 
		$_ = lc $_;	# converts to lower case
              }

print "Enter the path where the text files are:\nRemember to put double slashes (\\\\) or backslash (/)\n";
#$dir = <STDIN>;
$dir = ".\\Tokenized corpus";
chomp $dir;
opendir(BIN, $dir) or die "Can't open $dir: $!";
open OUTFILE, ">Result.csv"  or die "Can't open $dir: $!";

print OUTFILE ("Filename\tWords\tHL\tDL\tD_H\tAWL\tLD\tYuleK\tEntropy\tRelEntr\t1LW\t2LW\t3LW\t4LW\t5LW\t6LW\t7LW\t8LW\t9LW\t10LW\t11LW\t12LW\t13LW\t14LW\tα\tά\tε\tέ\tι\tί\tυ\tύ\tη\tή\tο\tό\tω\tώ\tβ\tγ\tδ\tζ\tθ\tκ\tλ\tμ\tν\tξ\tπ\tρ\tς\tσ\tτ\tφ\tχ\tψ\n");
while(defined ($file = readdir BIN)) {
			  next if $file =~ /^\.\.?$/;
			  next if $file =~ /pl$/;
			  next if $file =~ /pbp$/;
			  next if $file =~ /^Results\.txt/;
			  next if $file =~ /^fwords\.txt/;
  			  open(MYFILE, "$dir\\$file");
			  print $file;
              
 @array = ();
 %freqarray = ();
 %freqhash = ();
 %myconc = ();
 $word = 0;
 $freq = 0;
 $wordfr = 0;
 $M2 = 0;
 $M1 = 0;
 $Yule = 0;
 $times = 0;
 $p_i = 0;
 $logp_i = 0;
 $Entr = 0;
 $log_MaxE = 0;
 $RelEntr = 0;
 
              @array = <MYFILE>;
              foreach (@array) {
              	chomp;
		s/Σ$/ς/g;		# converts to greek final -s 
		$_ = lc $_;	# converts to lower case
              }
                foreach $word (@array) {        #creates a hash (myconc) with the frequency list of the array. 
                		$myconc{$word}++;
                }
$wordcount = @array;        
 while (($word, $freq) = each %myconc){           #search each value word - freq.
                                push @freqarray, $freq; #creates a hash with keys the frequency of a word and value the times this frequency occurs
				$freqhash{$freq}++;
				$p_i = $freq/$wordcount;	#calculates the p for each type
				$logp_i = log($p_i)/log(10);	#calculates the log(p) for each type
				$Entr += -($p_i * $logp_i);	# calculates the Entropy of the text
			  }
			  $log_MaxE = log ($wordcount) / log (10);	#calculates the maximum entropy of a text (that is if all the types occured once)
			  $RelEntr = 100*($Entr/$log_MaxE);	#Relative entropy = (Entropy of text / Maximum entropy) * 100


while (($wordfr, $times) = each %freqhash){           #search each value word - freq.
                               $M2 += $times * ($wordfr * $wordfr);
			       $M1 += $wordfr * $times;
			       }
 $Yule = 10000 * (($M2 - $M1)/($M1 * $M1));
 
 
 
 $hapax = 0;
 $dis = 0;
               while (($word, $freq) = each %myconc){           #search each value word - freq and if freq equal 1 (hapax legomeno) counts it in the $hapax. Same for the dislegomena ($dis)
                                if ($freq == 1) {
                                                $hapax +=1;
                                }
                                if ($freq == 2) {
                                                $dis +=1;
                                }
               
                } 

$hapax_norm= ($hapax*100)/$wordcount;
$dis_norm= ($dis*100)/$wordcount;
$d_h= $dis/$hapax;


                         
                         
			  $text = join ("", @array);
$term = 0;
foreach (@farray) {
             $fw = $_;
			  for ($index = 1; $index <= $wordcount; $index++) { 
                                if ($array[$index-1] eq $fw) {
                                $term+=1;
                                }
			  }
}
$ld= ($wordcount - $term)/($term);			  
			  	

			  $char = 0;
			  $w1 = 0;
			  $w2 = 0;
			  $w3 = 0;
			  $w4 = 0;
			  $w5 = 0;
                          $w6 = 0;
                          $w7 = 0;
			  $w8 = 0;
			  $w9 = 0;
			  $w10 = 0;
			  $w11 = 0;
                          $w12 = 0;
                          $w13 = 0;
			  $w14 = 0;
			  $pw1 = 0;
			  $pw2 = 0;
			  $pw3 = 0;
			  $pw4 = 0;
			  $pw5 = 0;
                          $pw6 = 0;
                          $pw7 = 0;
			  $pw8 = 0;
			  $pw9 = 0;
			  $pw10 = 0;
			  $pw11 = 0;
                          $pw12 = 0;
                          $pw13 = 0;
			  $pw14 = 0;
			
                        for ($indexcount = 1; $indexcount <= $wordcount; $indexcount++) {	#Loops n times, where n the total number of the tokens
                		$x = length($array[$indexcount -1]); #Stores the length of each token in the variable x
                		   if ($x == 1) {	# The following if's check if the word length of x equals to a specified length
                		   $w1+=1;
                		   }
                		   if ($x == 2) {
                		   $w2+=1;
                		   }
                		   if ($x == 3) {
                		   $w3+=1;
                		   }
                		   if ($x == 4) {
                		   $w4+=1;
                		   }
                		   if ($x == 5) {
                		   $w5+=1;
                		   }
                		   if ($x == 6) {
                		   $w6+=1;
                		   }
                		   if ($x == 7) {
                		   $w7+=1;
                		   }
                		   if ($x == 8) {
                		   $w8+=1;
                		   }
                		   if ($x == 9) {
                		   $w9+=1;
                		   }
                		    if ($x == 10) {
                		   $w10+=1;
                		   }
                		   if ($x == 11) {
                		   $w11+=1;
                		   }
                		   if ($x == 12) {
                		   $w12+=1;
                		   }
                		   if ($x == 13) {
                		   $w13+=1;
                		   }
                		   if ($x == 14) {
                		   $w14+=1;
                		   }
                		$char += $x;	#Sums the lengths
                		}

$pw1 = ($w1 * 100) / $wordcount;
$pw2 = ($w2 * 100) / $wordcount;
$pw3 = ($w3 * 100) / $wordcount;
$pw4 = ($w4 * 100) / $wordcount;
$pw5 = ($w5 * 100) / $wordcount;
$pw6 = ($w6 * 100) / $wordcount;
$pw7 = ($w7 * 100) / $wordcount;
$pw8 = ($w8 * 100) / $wordcount;
$pw9 = ($w9 * 100) / $wordcount;
$pw10 = ($w10 * 100) / $wordcount;
$pw11 = ($w11 * 100) / $wordcount;
$pw12 = ($w12 * 100) / $wordcount;
$pw13 = ($w13 * 100) / $wordcount;
$pw14 = ($w14 * 100) / $wordcount;


$awl = $char/$wordcount;
                
			  $a = ($text =~ tr/α//);
			  $as = ($text =~ tr/ά//);
                          $e = ($text =~ tr/ε//);
			  $es = ($text =~ tr/έ//);
			  $i = ($text =~ tr/ι//);
			  $is = ($text =~ tr/ί//);
			  $u = ($text =~ tr/υ//);
			  $us = ($text =~ tr/ύ//);
			  $h = ($text =~ tr/η//);
			  $hs = ($text =~ tr/ή//);
			  $o = ($text =~ tr/ο//);
			  $os = ($text =~ tr/ό//);
			  $w = ($text =~ tr/ω//);
			  $ws = ($text =~ tr/ώ//);
			  $b = ($text =~ tr/β//);
			  $g = ($text =~ tr/γ//);
			  $d = ($text =~ tr/δ//);
			  $z = ($text =~ tr/ζ//);
			  $th = ($text =~ tr/θ//);
			  $k = ($text =~ tr/κ//);
			  $l = ($text =~ tr/λ//);
			  $m = ($text =~ tr/μ//);
			  $n = ($text =~ tr/ν//);
			  $ks = ($text =~ tr/ξ//);
			  $p = ($text =~ tr/π//);
			  $r = ($text =~ tr/ρ//);
			  $sf = ($text =~ tr/ς//);
			  $s = ($text =~ tr/σ//);
			  $t =($text =~ tr/τ//);
			  $f = ($text =~ tr/φ//);
			  $x = ($text =~ tr/χ//);
			  $ps = ($text =~ tr/ψ//);
			  
			  

$chartotal = $a+$as+$e+$es+$i+$is+$u+$us+$h+$hs+$o+$os+$w+$ws+$b+$g+$d+$z+$th+$k+$l+$m+$n+$ks+$p+$r+$sf+$s+$t+$f+$x+$ps;
                          $p_a = ($a*100)/$chartotal;
			  $p_as = ($as*100)/$chartotal;
			  $p_e = ($e*100)/$chartotal;
			  $p_es = ($es*100)/$chartotal;
			  $p_ii = ($i*100)/$chartotal;
			  $p_is = ($is*100)/$chartotal;
			  $p_u = ($u*100)/$chartotal;
			  $p_us = ($us*100)/$chartotal;
			  $p_h = ($h*100)/$chartotal;
			  $p_hs = ($hs*100)/$chartotal;
			  $p_o = ($o*100)/$chartotal;
			  $p_os = ($os*100)/$chartotal;
			  $p_w = ($w*100)/$chartotal;
			  $p_ws = ($ws*100)/$chartotal;
			  $p_b = ($b*100)/$chartotal;
			  $p_g = ($g*100)/$chartotal;
			  $p_d = ($d*100)/$chartotal;
			  $p_z = ($z*100)/$chartotal;
			  $p_th = ($th*100)/$chartotal;
			  $p_k = ($k*100)/$chartotal;
			  $p_l = ($l*100)/$chartotal;
			  $p_m = ($m*100)/$chartotal;
			  $p_n = ($n*100)/$chartotal;
			  $p_ks = ($ks*100)/$chartotal;
			  $p_p = ($p*100)/$chartotal;
			  $p_r = ($r*100)/$chartotal;
			  $p_sf = ($sf*100)/$chartotal;
			  $p_s = ($s*100)/$chartotal;
			  $p_t =($t*100)/$chartotal;
			  $p_f = ($f*100)/$chartotal;
			  $p_x = ($x*100)/$chartotal;
			  $p_ps = ($ps*100)/$chartotal;

print OUTFILE ("$file\t$wordcount\t$hapax_norm\t$dis_norm\t$d_h\t$awl\t$ld\t$Yule\t$Entr\t$RelEntr\t$pw1\t$pw2\t$pw3\t$pw4\t$pw5\t$pw6\t$pw7\t$pw8\t$pw9\t$pw10\t$pw11\t$pw12\t$pw13\t$pw14\t$p_a\t$p_as\t$p_e\t$p_es\t$p_ii\t$p_is\t$p_u\t$p_us\t$p_h\t$p_hs\t$p_o\t$p_os\t$p_w\t$p_ws\t$p_b\t$p_g\t$p_d\t$p_z\t$p_th\t$p_k\t$p_l\t$p_m\t$p_n\t$p_ks\t$p_p\t$p_r\t$p_sf\t$p_s\t$p_t\t$p_f\t$p_x\t$p_ps\n");

}


close OUTFILE;
closedir(BIN);