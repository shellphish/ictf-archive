#!/usr/bin/php4-cgi
<?PHP
require('DB.php');
require('myfuncs.php');

$debug = $_GET['debug'];
$mysql_url = "mysql://estoreuser:retard@localhost/estore";

$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

$username = mysql_real_escape_string($_GET['username']);
$password = $_GET['password'];

$token = rand();
$expiration = time()+3600;
$cookie = "${username}:${password}:${expiration}:${token}";

/* This has to happen before the header is generated */
/* setcookie("auth", $cookie, ${expiration}, "/", "", 0);*/
setcookie("auth", $cookie);


myheader("Login");

if ($debug) {
  print "<p>DEBUG: username: ${username}</p>\n";
  print "<p>DEBUG: password: ${password}</p>\n";
  print "<p>DEBUG: cookie: ${cookie}</p>\n";
}


$st = $db->prepare("SELECT * FROM users WHERE username='${username}' AND password='${password}'");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}
if ($rs->numRows() == 0) {
  diefooter("<p>Username/password combination is invalid.</p>");
}
print "<p>User successfully authenticated.</p>";

$st = $db->prepare("UPDATE users SET cookie='${cookie}' WHERE username='${username}'");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}

myfooter();
?>
