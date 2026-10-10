<?php
session_start();
require('myfuncs.php');

$_SESSION['q5'] = $_GET['q5'];
$_SESSION['q6'] = $_GET['q6'];
$_SESSION['q7'] = $_GET['q7'];
$_SESSION['q8'] = $_GET['q8'];
/* print_r($_SESSION); */
$total = $_SESSION['q1'] + $_SESSION['q2'] + 
  $_SESSION['q3'] + $_SESSION['q4'] +
  $_SESSION['q5'] + $_SESSION['q6'] +
  $_SESSION['q7'] + $_SESSION['q8'];

if (!isset($_SESSION['user'])) {
  session_destroy();
  diefooter("User is not set");
}
$username = $_SESSION['user'];

if (!isset($_SESSION['step']) || ($_SESSION['step'] != 'first')) {
  session_destroy();
  diefooter("How did you get here?");
}
$_SESSION['step'] = 'second';

myheader("Become ah membuh (3)");

$filename = "accounts/" . $username;
$file = fopen($filename, "w+");
fwrite($file, $total);
fclose($file);

if (file_exists("accounts/counter.txt")) {
  $file = fopen("accounts/counter.txt", "r");
  $counter = fread($file, 1024);
  $counter = $counter + 1;
  fclose($file);
} else {
  $counter = 1;
}

$file = fopen("accounts/counter.txt", "w+");
fwrite($file, $counter);
fclose($file);

if (($counter % 100) == 0) {
  $_SESSION['winner'] = 1;
  $_SESSION['step'] = 'third';
?>

  <p>Y'all is ore 10000 user!!!</p>
  <p>We will transfuh ah big amount uv money tuh ah account uv yore choice.</p>

  <form method="get" action="transact.php" >Enter the IBAN: <input type="text" name="iban" />
  <input type="submit" value="Submit" />
  </form>

<?php
} else {
  $_SESSION['winner'] = 0;

  if ($total > 5) {
    print "<p>$user, y'all is one uv us. Click <a href=\"account.php\">heuh</a> tuh open ah account</p>";
  } else {
    print "<p>Y'all is not one uv us. Y'all ortta go tuh anothuh bank, like for nurmal people...</p>";
    session_destroy();  
  } 
}
myfooter();
?>
