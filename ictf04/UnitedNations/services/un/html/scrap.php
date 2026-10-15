srand((double)microtime()*1000000); 
$displayed = 0;
$candidates = "";

while ($displayed < 5)
{
  $candidate = rand(0,4);
  echo $(candidate);  
  echo $(displayed);
  if (strstr($candidates, "$candidate"))
    {
      continue;
    }
  $candidates = $candidates + " $candidate";
  $displayed++; 
  echo $candidates;

  switch($candidate) {
  case "0":
    include("austrian.html");
    break;
  case "1":
    include("german.html");
    break;
  case "2":
    include("italian.html");
    break;
  case "3":
    include("norwegian.html");
    break;
  case "4":
    include("american.html");
    break;
  }
}
