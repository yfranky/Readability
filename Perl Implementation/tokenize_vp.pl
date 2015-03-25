#!/usr/bin/perl
use open ':utf8';

#$dir = "C:\\Users\\George\\Desktop\\Test";
$dir = "C:\\Users\\vpouli\\Documents\\Apps\\courses\\Texnoglwssia\\examhno2\\Mikros\\corpus_all";
#print "Text files in $dir are:\n";
#print $dir;
#binmode STDOUT, ":encoding(utf8)";
opendir(BIN, $dir) or die "Can't open $dir: $!";
binmode STDOUT, ':utf8';
while(defined ($file = readdir BIN)) {
			  next if $file =~ /^\.\.?$/;
			  next if $file =~ /^*pl$/;
			  next if $file =~ /^*pbp$/;
			  
			  #unless (open(MYFILE, "$file")) {
			  unless (open(MYFILE, "<:encoding(UCS-2LE)", "$file")) {
  			  	   #unless (open(MYFILE, "<:encoding(UTF-16)", "$file")) {
				  #unless (open(MYFILE, "<:encoding((iso-8859-7)", "$file")) {
  		 		   die ("cannot open input file $file\n");
				   }
							#print $file;							
                            while (<MYFILE>) {
							
								$text .= $_;   #reads the text and stores it in a variable
                            }
                            $_ = $text;
							close MYFILE;
							open OUTFILE, ">$file";
							 
                            
							s/\s+/\n/g;                       #switches all the spaces for newlines
                            # print $_;
                            s/([.,!?:;])\n/\n$1\n$2/g;        #puts all the punct on a separate line
                            # print $_;
                            s/([^\n])([\"\'\`])\n/$1\n$2\n/g; #puts final quotes on separate line
                            s/\n([\"\'\`])([^\n])/\n$1\n$2/g; #puts initial quotes on separate line
                            s/([^\n])([.,])\n/$1\n$2\n/g;     # put punctuation before " on separate line
                            # print $_;
                            s/\n([A-Z])\n\./\n$1./g;          # take care of initials in names
                            # print $_;
                            s/\n\.\n([^\"A-Z])/\.\n$1/g;      # put periods behind abbreviations
                            s/(\.[A-Z]+)\n\.\n/$1.\n/g;       # put periods behind abbreviations
                            s/([^\n])\'s\n/$1\n\'s\n/g;       # move final 's to separate line
                            s/([^\n])n\'t\n/$1\nn\'t\n/g;     # move final n't to separate line
                            s/([^\n])\'re\n/$1\n\'re\n/g;     # move final 're to separate line
                            # print $_;
                            s/\n\$([^\n])/\n\$\n$1/g;         # move initial $ to separate line
                            s/([^\n])%\n/$1\n%\n/g;           # move final % to separate line
                            s/Mr\n\.\n/Mr.\n/g;               # frequent abbreviation error    
                            s/κ\n\.\n/κ.\n/g;				  # as above but in Greek k.
                            s/<p>|<\/p>//g;				  	  # Delete paragraph marks
                            s/[.,!?:;·""«»­()'\\\-\+\*\{\}\[\]\$\^\]\@]//g;	# removes punctuation
                            s/\n+/\n/g;  					  #removes blank lines
                            s/^\s*//;						  # removes lines with spaces
							print OUTFILE;
							close OUTFILE;
							$_=0; 		  			#Clears the system variable
							$text="";				#Clears the text
							
 					}	
binmode STDOUT, ':utf8';
closedir(BIN);