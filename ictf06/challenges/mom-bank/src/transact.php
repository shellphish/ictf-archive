<?php
session_start();
require('myfuncs.php');

/* print "transact.php\n";
print_r($_SESSION);
print_r($_COOKIE); */

if (!isset($_SESSION['user'])) {
  session_destroy();	
  diefooter('User not specified');
}
$username = $_SESSION['user'];

if (!isset($_SESSION['winner'])) {
  session_destroy();	
  diefooter('Winner status not specified');
}
$winner = $_SESSION['winner'];

if (!isset($_GET['iban'])) {
  session_destroy();	
  diefooter('IBAN not specified');
}
$iban = $_GET['iban'];

if ((!isset($_SESSION['step'])) || ($_SESSION['step'] != 'third')) {
  session_destroy();	
  print $_SESSION['step'];
  diefooter('How did you get here?');
}



if ($winner == 1) {
  myheader("Y'all is duh winner!!");
  $transaction = "4000 " . $iban;
} else {
  myheader("Duin' duh transfer");
  if (!isset($_GET['amount'])) {
    session_destroy();	
    diefooter('Amount not specified');
  } 
  $amount = $_GET['amount'];

  $filename = "accounts/" . $username;
  $file =  fopen($filename, "r+");
  $balance = fread($file, 1024);

  fclose($file);
  if ($balance < $amount) {
    session_destroy();	
    diefooter('Not enough money.');
  }
  $balance = $balance - $amount;
  $file =  fopen($filename, "w+");
  fwrite($file, $balance);
  fclose($file);
  $transaction = $amount . " " . $iban;
}

  $filename = tempnam("/var/spool/transactions/mom/", "trans");
  $file = fopen($filename, 'w+');
  fwrite($file, $transaction);
  fclose($file);

  session_destroy();
?>

  <p>Duh transacshun has been executd as requestd!</p>
  <p>Now y'all is rich!</p>

<?php




  myfooter();
?>
