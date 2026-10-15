<?php 

if ($_SESSION["loggedin"] == "1"){
print("<a href=\"claim.php\"><strong>Submit a Claim</strong></a><br>");
print("<a href=\"extend.php\"><strong>Extend Coverage</strong></a><br>");
print("<a href=\"index.php?action=logout\"><strong>Logout</strong></a><br>");
}
else{
print("<a href=\"buy.php\"><strong>Buy Auto Insurance</strong></a><br>");
print("<a href=\"login.php\"><strong>Login</strong></a><br>");
}

?>

