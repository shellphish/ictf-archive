#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
myheader("Softerror.com - Financial Network");
checkcookie();

$group = sqlite_escape_string($_POST['group']);
$email = sqlite_escape_string($_POST['email']);
$size = intval($_POST['size']);
$username = sqlite_escape_string($_POST['username']);
$password = sqlite_escape_string($_POST['password']);

if (($username == "") || ($password == "")) {
	diefooter("Missing admin's username and/or password.");
}

if (($group == "") || ($email == "")) {
	diefooter("Missing group name and/or contact email."); 
}

/* print "<pre>" . $group . " " . $email . " " . $username . " " . $password . "</pre>";*/
 
if ($db = sqlite_open('level4db', 0666, $err)) {
        $q = @sqlite_query($db, 'SELECT * FROM admins', SQLITE_ASSOC, $error1);
        if ($q == false) {
            sqlite_query($db, 'CREATE TABLE admins(username text, password text, PRIMARY KEY (username)); INSERT INTO admins VALUES ("admin1","baboon"); INSERT INTO admins VALUES ("admin2","wootwoot"); INSERT INTO admins VALUES ("admin3","tsirorret"); INSERT INTO admins VALUES ("admin4","DaBomb");');
        }
        $q = @sqlite_query($db, 'SELECT * FROM groups');
        if ($q == false) {
                sqlite_query($db, 'CREATE TABLE groups (name text, email text, size int, admin text, PRIMARY KEY (name)); INSERT INTO groups VALUES ("The Cell", "cell@thecell.com", 20, "admin2"); INSERT INTO groups VALUES ("Scary Guys", "scary@scarydudes.com", 1021, "admin1");');
        }
} else {
        diefooter($err);
}
$sql = "SELECT * from admins WHERE username='" . $username . "' and password='" . $password . "'";
$q = sqlite_query($db, $sql);
if (sqlite_num_rows($q) <= 0) {
	diefooter("Authentication failed! User/password combination could not be found in admins table");
}
$sql = "INSERT INTO groups VALUES ('" . $group . "', '" . $email . "', " . $size . ", '" . $username . "');";
/* print "<pre>" . $sql . "</pre>";*/
$q = sqlite_query($db, $sql);

print "<p>The contact information has been added.</p>";

?>
<?php
myfooter();
?>
