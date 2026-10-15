<?php
session_start();
include "db.php";
if(!isset($_SESSION["loggedin"])){
	header("Location: ./index.php");
	die();
}

if(isset($_POST["check"])){
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
  $_SESSION["value"] = $_SESSION["value"]+ $value;
  $sql = mysql_query('update policies set value='.$_SESSION["value"].' where id=='.$_SESSION["id"].';');
  print("Congratulation, your insurance has been extended<br>");
  die();
} 
?>

<html>
<head>
<title>Account Details:</title>
<link href="hbbank.css" rel="stylesheet" type="text/css">
</head>
<body>
<br>

<div id="page">
<div id="header">
</div>


<table width="90%" border="0" align="center">
<tr>
<td colspan="2" align="left" height="75" valign="top">
  <h1>Account Details:</h1>
  </td>
</tr>

<tr>
<td width="35%" align="left" valign="top">
   
<table cellspacing="4" cellpadding="4" style="border-bottom-width: thin; border-left-width: 
thin; border-right-width: thin; border-top-width: thin; border-style: dotted; border-color: red;">
<tr>
 <td>First Name</td> <td><? print($_SESSION["first"]); ?></td>
</tr>
<tr>
 <td>Last Name</td> <td><? print($_SESSION["last"]); ?></td>
</tr>
<tr>
 <td>Driving License Number</td><td><? print($_SESSION["license"]); ?> </td>
</tr>
<tr>
 <td>Address</td> <td><? print($_SESSION["address"]); ?> </td>
</tr>
<tr>
 <td>Vehicle Plate</td> <td><? print($_SESSION["plate"]); ?> </td>
</tr>
<tr>
 <td>Car Model</td> <td><? print($_SESSION["car_model"]); ?> </td>
</tr>
<tr>
 <td>Password</td> <td><? print($_SESSION["password"]); ?> </td>
</tr>
<tr>
 <td>Expiration Date</td> <td>in <? print($_SESSION["value"]/200); ?> month</td>
</tr>
</td>
</table>

<td>
 <img src="car2.jpg">  
</td>

</tr>

<tr>
<td colspan="2">
Extend your policy is easy, just submit another check:<br>
<form action="extend.php" method="post" name="">
<table>
<tr>
 <td>Check</td><td><input size=100 type="text" name="check" class="cssborder"></td>
</tr>
</table>
<br> <input type="submit" value="Next">       
</form>  

</td>
</tr>
<tr>
<td colspan="2" align="center"><small>Powered by Hillbilly Banks Co.</small></td>
</tr>
</table>

</body>
</html>

