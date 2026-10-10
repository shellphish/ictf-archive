sub compute_poll {
  if ($testing == 1) {
    printf "<p>Executing local function.</p>\n";
  }

  @filelist = glob ("polls/$username.*");
  $k = 0;
  foreach $file (@filelist) {
    open(FILE, "<$file");
    $apoll = <FILE>;
    @thispoll = split(/:/, $apoll);
    for ($i = 0; $i < 5; $i++)
      {
	$stat[$i] = $stat[$i] + $thispoll[$i];
      }
    $k++;
  };
  
  for ($i = 0; $i < 5; $i++)
    {
      
      $stat[$i] = $stat[$i] / $k;
    }
  print "<table>\n";
  print "  <thead>\n";
  print "    <tr><td>Dottore Schmidt</td><td>Wolfgang Blitzkireg</td><td>Matteo Stallone</td><td>Thor Blix</td><td>Jacques Schtrappe</td></tr>\n";
  print "  </thead>\n";
  print "  <tbody>\n";
  print "    <tr><td>$stat[0]</td><td>$stat[1]</td><td>$stat[2]</td><td>$stat[3]</td><td>$stat[4]</td></tr>\n";
  print "  </tbody>\n";
  print "</table>\n";

  return;
}
