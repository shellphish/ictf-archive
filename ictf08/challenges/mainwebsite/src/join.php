<?php
require('variables.php');
require('functions.php');

myheader("Join Us");
?>

<p><!-- " -->
<p>Join us! You can help us making this world a worse place by developing
evil code to support evil causes.</p>

<p>To apply you can fill in the form below. After a rigorous screening
process, you will be allowed to log in into our web forum, where you can start
your work.</p>

<form method="post" action="createaccount.php">
<p>First: <input type="text" name="first" size="25" /> Last: <input type="text" name="last" size="25" /><p>
<p>Email: <input type="text" name="email" size="25" /> 
Password: <input type="password" name="password" /></p>
<p>Credit Card: <input type="text" name="cc" size="18" /> 
Exp: <input type="text" name="exp" size="18" /><p>
<p><input type="submit" value="Join the terror" /></p>
</form>

<p>If you already have an account, login here:</p>
<form method="post" action="login.php">
<p>Email: <input type="text" name="email" size="25" /></p>
<p>Password: <input type="password" name="password" /></p>
<p><input type="submit" value="Login" /></p>
</form>

<?php>
myfooter();
?>
