#!/usr/bin/php-cgi
<?php
require('variables.php');
require('functions.php');
myheader("Softerror.com - Financial Network");
checkcookie();
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
?>
<div class="floatright">
<p>Search for a group</p>
<form method="get" action="search.php">
<p><input type="text" size="4" name="search" /><input type="submit" value="Search by size" /></p>
</form>
</div>
<p>Add a terrorist group financial contact:</p>
<form method="post" action="add.php">
<p>Group name: <input type="text" name="group" /></p>
<p>Contact email: <input type="text" name="email" /></p>
<p>Size: <input type="text" name="size" /></p>
<p>Admin manager for this entry: <input type="text" name="username" /></p>
<p>Admin password: <input type="password" name="password" /></p>
<p><input type="submit" value="Add the group" /></p>
</form>

<?php
myfooter();
?>
