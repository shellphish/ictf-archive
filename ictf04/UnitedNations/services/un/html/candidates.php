<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta name="Author" content="Z4n4rd1" />
  <meta name="keywords" content="Candidates" />
  <link href="un.css" rel="stylesheet" type="text/css" />
  <title>The World President Candidates</title>
</head>

<body>

  <div class="banner">
      <table width="100%" border="0" summary="table">
        <tr>
          <td width="10%"><a href="index.html"><img alt = "UN" src="unlogo.gif" /></a></td>

          <td width="100%"><h1>The World President Candidates</h1></td>

          <td width="10%"><a href="index.html"><img alt="UN" src="unlogo.gif" /></a></td>

	</tr>
      </table>
  </div>

  <div class="main">
    <p>The World President Candidates have been chosen among the best
    politicians in the world by a complex system of caucuses, statistical
    polls, coin flipping, and spitball fights.</p>

    <p>The four top candidates are from the countries of Austria, Germany, Italy,
    Norway, and the United States of America.</p>

    <p>To prevent any form of implied order, the candidates are presented in a
    random order every time this page is loaded.</p>

    <p>Please feel free to provide feedback on the candidates' programs.</p>

<table summary="candidates" border="2">
<?php
srand((double)microtime()*1000000); 
$displayed = 0;
$candidates = "";

while ($displayed < 5)
{
  $candidate = rand(1,5);
  if (strstr($candidates, "$candidate"))
    {
      continue;
    }
  $candidates = "$candidates $candidate";
  //  echo "Candidate $candidate Candidates $candidates\n<br>";  

  $displayed++; 
  switch($candidate) {
  case "1":
    include("austrian.html");
    break;
  case "2":
    include("german.html");
    break;
  case "3":
    include("italian.html");
    break;
  case "4":
    include("norwegian.html");
    break;
  case "5":
    include("american.html");
    break;
  }
  echo "<tr><td colspan=\"2\"><form action=\"feedback.php\" method=\"post\">\n";
  echo "        <p>Name: <input type=\"text\" name=\"name\"></p>\n";
  echo "        <p>Comments: <textarea name=\"comment\" rows=\"3\" cols=\"40\">\n";
  echo "Your comments here\n";
  echo "</textarea></p>\n";
  echo "<p><input type=\"hidden\" name=\"candidate\" value=\"$candidate\"></p>\n";
  echo "<p><input type=\"submit\" value=\"Submit Comments\"></p>\n";
  echo "</form></td></tr>\n";
}
?>
</table>

    </div>
  </div>

  <div class="footer">
    <hr />
    Administered by <a href="/diebald">The Die-Bald Corporation</a>
  </div>
</body>
</html>
