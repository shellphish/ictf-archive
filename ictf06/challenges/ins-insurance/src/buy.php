<?
session_start();
include "db.php";
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
<body>

<div id="page">
<div id="header">
</div>



<br>

<table width="90%" border="0" align="center">
<tr>
<td align="center" height="75" valign="top">
  <h1>Insurance Subscription</h1>
</td>
</tr>
<tr>
<td align="center" valign="center">
<?
$get_vars = array('first', 'last', 'address', 'plate', 'car_model', 'id', 'password', 'iban');
$ok = true;
foreach($get_vars as $gv){
	if (!isset($_POST[$gv])){
		$ok = false;
		break;
	}
}

if ($ok){
	foreach(array_keys($_POST) as $gv){
		$_SESSION[$gv]=strip_tags($_POST[$gv]);
	}
	$_SESSION["step1"] = true;
	print('The Insurance for you vehicle costs 200$ a month.<br>Please pay with an electronic check:<br>');
	print('<form action="buy.php" method="post" name="">');
	print('<table width="60%" cellspacing="4" cellpadding="4" style="border-bottom-width: thin; 
	        border-left-width: thin; border-right-width: thin; border-top-width: thin;  
		border-style: dotted; border-color: red;">');
	print('<tr><td>Check</td><td><input size=100 type="text" name="check" class="cssborder"></td></tr></table>');
	print('<br> <input type="submit" value="Buy">');
	print('</form>');
	die();
}

if (isset($_POST["check"]) && isset($_SESSION["step1"])){
  if (strlen($_POST["check"]) != 172){
	  print('<b>Invalid Check</b>.<br>');
	  die();   	
  }
  $handle = popen('/usr/bin/ccheck '.escapeshellarg($_POST["check"]), 'r');
  $value = fread($handle, 10);
 
  pclose($handle);

  $value = $value +0;
  if ($value < 0){
	  print('<b>Invalid Check</b>.<br>');
	  die();   	
  }
    
  $months = $value / 200;
  $policy = rand(1000000, 9999999); 

      
  $sql = "INSERT INTO policies VALUES ( 
         ".mysql_real_escape_string($policy).
         ",'".mysql_real_escape_string($_SESSION["first"]).
	 "','".mysql_real_escape_string($_SESSION["last"]).
	 "','".mysql_real_escape_string($_SESSION["address"]).
	 "','".mysql_real_escape_string($_SESSION["id"]).
	 "','".mysql_real_escape_string($_SESSION["plate"]).
         "','".mysql_real_escape_string($_SESSION["car_model"]).
         "','".mysql_real_escape_string($_SESSION["password"]).
         "','".mysql_real_escape_string($_SESSION["iban"]).
         "',".mysql_real_escape_string($value).
	 ",".time().");";
 
  $sql = mysql_query($sql);
  $_SESSION["loggedin"] = false;
  
  print('Congratulations.<br>');
  print('Your insurance number is: '.$policy."<br>");
  print('Your insurance expires in '.$months.' months.<br>');
  print('Go back to the <a href="index.php">homepage</a>');
  die();
}

?>


<form action="buy.php" method="post" name="">
<table cellspacing="4" cellpadding="4" style="border-bottom-width: thin; border-left-width: 
thin; border-right-width: thin; border-top-width: thin; border-style: dotted; border-color: red;">
<tr>
 <td>First Name</td> <td><input type="text" name="first" class="cssborder"></td>
</tr>
<tr>
 <td>Last Name</td> <td><input type="text" name="last" class="cssborder"></td>
</tr>
<tr>
 <td>Driving License Number</td> <td><input type="text" name="id" class="cssborder"></td>
</tr>
<tr>
 <td>Address</td> <td><input type="text" name="address" class="cssborder"></td>
</tr>
<tr>
 <td>Vehicle Plate</td> <td><input type="text" name="plate" class="cssborder"></td>
</tr>
<tr>
 <td>Car Model</td> <td><input type="text" name="car_model" class="cssborder"></td>
</tr>
<tr>
 <td>Password</td> <td><input type="password" name="password" class="cssborder"></td>
</tr>
<tr>
 <td>Internation Bank Account Number</td> <td><input size=90 type="text" name="iban" class="cssborder"></td>
</tr>
</table>
<br> <input type="submit" value="Next">       
</form>
</td>
</tr>
<tr>
<td align="center"><small>Powered by Hillbilly Banks Co.</small></td>
</tr>
</table>




