<?
session_start();
?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title><? echo "$title"; ?></title>
<meta name="keywords" content="<? echo $keywords; ?>">
<meta name="description" content="<? echo $description; ?>">
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link href="hbbank.css" rel="stylesheet" type="text/css">
</head>
<body bgcolor="#aaaaaa" leftmargin="10" topmargin="10" marginwidth="0">
<br>
<div id="page">
<div id="header">
</div>

<table width="90%" border="0" align="center">
<tr>
<td align="center" height="75" valign="top">
  <h1>Login</h1>
</td>
</tr>

<tr>
<td align="center">
<img src="car3.jpg">
<td>
</tr>



<tr>
<td align="center" valign="center">

<?
if (isset($_GET["pnum"]) && isset($_GET["pass"])){
 	include "db.php";
	$sql = 'select * from policies where id="'.mysql_real_escape_string($_GET["pnum"]).'" 
	       and password = "'.mysql_real_escape_string($_GET["pass"]).'";';

	$sql = mysql_query($sql);
	if (!$sql || mysql_num_rows($sql)==0){
		print("Login failed, try again");
	}
	else{
		$row = mysql_fetch_array($sql, MYSQL_ASSOC);
		foreach(array_keys($row) as $r){
			$_SESSION[$r]=$row[$r];
		}
		$_SESSION["loggedin"] = true;
		print('Welcome <b>'.$_SESSION["first"]." ".$_SESSION["last"]."</b>.<br>");
		print('Go back to the <a href="index.php">home page</a><br>');
		die();
	}
}

?>

<form action="login.php" method="get" name="">
<table cellspacing="4" cellpadding="4" style="border-bottom-width: thin; border-left-width: 
thin; border-right-width: thin; border-top-width: thin; border-style: dotted; border-color: red;">
<tr>
 <td>Policy Number</td><td><input type="text" name="pnum" class="cssborder"></td>
</tr>
<tr>
 <td>Password</td><td><input type="password" name="pass" class="cssborder"></td>
</tr>
</table>
<br> <input type="submit" value="login">       
</form>
</td>
</tr>
<tr>
<td align="center"><small>Powered by Hillbilly Banks Co.</small></td>
</tr>
</table>

