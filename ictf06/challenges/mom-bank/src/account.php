<?php
session_start();
require('myfuncs.php');
/* print_r($_SESSION); */
if (!isset($_SESSION['user'])) {
  print "Error when creating a new account\n";
  diefooter("User is not set.");
}

$username = $_SESSION['user'];

if (!isset($_SESSION['step']) || ($_SESSION['step'] != 'second')) {
  diefooter("How did you get here?");
}

$_SESSION['step'] = 'third';

myheader("Create an account");
?>

  <p>Create ah new account in ore bank, mah friend</p>
    <form method="get" action="newaccount.php">
    <p>First Name: <input type="text" name="firstname" />
       Last Name: <input type="text" name="lastname" /></p>
    <p>Email: <input type="text" name="email" size="32" /></p>
    <p>Initial funds: <input type="text" name="check" size="32" /></p>
    <p><input type="submit" value="Do it!" /></p>
  </form>

<?php
myfooter();
?>
