<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta name="Author" content="Z4n4rd1" />
  <meta name="keywords" content="Candidates" />
  <link href="../un.css" rel="stylesheet" type="text/css" />
  <title>Feedback Page</title>
</head>

<body>

  <div class="banner">
      <table width="100%" border="0" summary="table">
        <tr>
          <td width="10%"><a href="candidates.php"><img alt = "UN" border="0" src="../unlogo.gif" /></a></td>

          <td width="100%"><h1>Feedback Page</h1></td>

          <td width="10%"><a href="candidates.php"><img alt="UN" border="0" src="../unlogo.gif" /></a></td>

	</tr>
      </table>
  </div>
  <div class="main">
<p>Your feedback so far is the following:</p>

<?php
$debug = 0;
$admin = 0;
$name = $_POST['name'];
$comment = $_POST['comment'];
$candidate = $_POST['candidate'];
if (!file_exists("feedback"))
{
  mkdir ("feedback", 0777);
}
if ($debug)
{
  echo "<p>Debugging $name's comments on candidate $candidate: $comment.</p>\n";
}
else
{
  include("feedback/postprocess.php");
  $file = fopen("feedback/$name", "a");
  fwrite($file, "<p>About $candidate: $comment</p>\n");
  fclose($file);
  $contents = file_get_contents("feedback/$name");
  echo "$contents";
}
?>


    </div>
  </div>

  <div class="footer">
    <hr />
    Administered by <a href="candidates.php">The Die-Bald Corporation</a>
  </div>
</body>
</html>
