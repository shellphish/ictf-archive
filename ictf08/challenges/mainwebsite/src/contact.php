<?php
require('variables.php');
require('functions.php');

myheader("Contact Us");

?>

<p>Please send us your ideas for terror-through-software:</p>
<form method="post" action="contact.php">
<input type="hidden" name="whichform" value="submit" />
<p>User: <input type="text" name="username" size="25" /> 
   Email: <input type="text" name="email" size="25" /></p>
<p>Your idea for cyberterror:</p>
<p><textarea rows="4" cols="50" name="idea">My idea is...</textarea></p>
<p><input type="submit" name="Submit" /></p>
</form>

<?php
if (array_key_exists('whichform', $_POST)) {
  if ($_POST['whichform'] == "submit") {
    $username = htmlspecialchars($_POST['username']);
    $email = htmlspecialchars($_POST['email']);
    $idea = htmlspecialchars($_POST['idea']);
    $ideafile = "ideas/idea" . rand() . ".html";
    if (($username == "") || ($email == "")) {
      diefooter("You provided an empty username and/or email address.");
    }
    $fh = fopen($ideafile, 'w+') or diefooter("Cannot save your idea");
    fwrite($fh, $username . " (" . $email . ") says:<br />" . $idea . "\n");
    fclose($fh);
    $ideafilename = base64_encode($ideafile);
?>

<form method="post" action="contact.php">
<input type="hidden" name="whichform" value="view" />
<p>View the ideas that have been proposed so far! 
<input type="submit" value="View" /></p>
</form>

<form method="post" action="contact.php">
<input type="hidden" name="whichform" value="review" />
<input type="hidden" name="lastidea" value="<?php print $ideafilename; ?>" />
<p>Review your latest idea! <input type="submit" value="Review" /></p>
</form>


<?php
  }
  else if ($_POST['whichform'] == "view") {
    print "<div class=\"idea\"><table summary=\"ideas\">";
    $index = 0;
    $rowl = 4;
    foreach (glob("ideas/idea*.html") as $filename) {
      if (($index % $rowl) == 0) {
	print "<tr>";
      }
      print "<td><a href=\"" . $filename . "\">" . basename($filename, ".html") . "</a></td>";
      if (($index % $rowl) == ($rowl - 1)) {
	print "</tr>";
      }
      $index++;
    }
    print "</table></div>";
  }
  else if ($_POST['whichform'] == "review") {
    $lastidea = base64_decode($_POST['lastidea']);
    $fh = fopen($lastidea, 'r') or diefooter ("I cannot access your idea.");
    $data = fread($fh, filesize($lastidea));
    print "<p>This was your latest idea:</p>\n<div class=\"idea\">";
    print $data;
    print "</div>";
  }
  else {
    diefooter("Unknown form");
  }
 }
    
?>

<?php
myfooter();
?>
