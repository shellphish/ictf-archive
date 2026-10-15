#!/usr/bin/perl

$command =  $ARGV[0];
#print "Command: " . $command . "\n";

if ($command =~ m/gyFGwom/) {
    @pairs = split(/&/,$ENV{'QUERY_STRING'});
    foreach $pair (@pairs) {
	($name, $value) = split(/=/, $pair);
	if ($name eq "command") {
	    print "The command is " . $value ."\n"
	}
    }
}
elsif ($command =~ m/is~kylA/) {
    open (FILE,"guestbook");
  @LINES=<FILE>;
  close(FILE);
  $SIZE=@LINES;
  for ($i=0;$i<=$SIZE;$i++) {
      if ($LINES[$i] =~ m/^PU/) {
	  print $LINES[$i]
      } 
  }
}
elsif ($command =~ m/is~z/) {
    open (FILE,"guestbook");
  @LINES=<FILE>;
  close(FILE);
  $SIZE=@LINES;
  for ($i=0;$i<=$SIZE;$i++) {
      if ($LINES[$i] =~ m/^PR/) {
	  print $LINES[$i]
      } 
  }
}
else {
  print "Unknown command " . $command
}
