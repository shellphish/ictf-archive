<?
session_start();
include "db.php";
if(!isset($_SESSION["loggedin"])){
	header("Location: ./index.php");
}
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
<br>

<div id="page">
<div id="header">
</div>


<?
  $get_vars = array('desc', 'date', 'damage');
  $ok = true;
  foreach($get_vars as $gv){
	if (!isset($_POST[$gv])){
		$ok = false;
		break;
	}
  }

  if ($ok){

  	$damage = $_POST["damage"];
	if($damage > $value){
		print('<table align="center" cellspacing="4" cellpadding="4" style="border-bottom-width: thin;');
		print('border-left-width:thin; border-right-width: thin; border-top-width: thin; border-style: dotted; border-color: red;"><tr><td>');
		print('In the first three months of membership you are not allowed to submit a claim for a value greater of the amount you paid for the insurance.');
		print('Claim: '.$damage.'  Thresold: '.$value);
		print('</td></tr></table>');
		die();
        }
	else{
	$sql = mysql_query('select SUM(amount) from claims where policy='.$_SESSION["id"].';');
	$totr = mysql_fetch_row($sql);
	$tot = $totr[0];
	if($damage+$tot > $value){
		print('<table align="center" cellspacing="4" cellpadding="4" style="border-bottom-width: thin;');
		print('border-left-width:thin; border-right-width: thin; border-top-width: thin; border-style: dotted; border-color: red;"><tr><td>');
		print('The sum of your claim values excedes the maximum amount allowed in the first three months of membership.<br>');
		print('Total Claim: '.($damage+$tot).'  Thresold: '.$value);
		print('</td></tr></table>');
		die();
        }	
	}
	$handle = fopen("/var/spool/transactions/ins/".rand(10000,99999), "w");
	fwrite($handle, "".$damage." ".$_SESSION["iban"]);
	fclose($handle);

  	$sql = "INSERT INTO claims (policy, description, amount) VALUES ( ".$_SESSION["id"].", '".$_POST["desc"]."' , ".$damage."  );";
 	$sql = mysql_query($sql);

  
	print('<table align="center" cellspacing="4" cellpadding="4" style="border-bottom-width: thin;');
	print('border-left-width:thin; border-right-width: thin; border-top-width: thin; border-style: dotted; border-color: red;"><tr><td>');
	print('Claim submitted.');
	print('</td></tr></table>');
	die();
  }
?>
	
	


<table width="90%" border="0" align="center">
<tr>
<td align="center" height="75" valign="top">
  <h1>Report a claim</h1>
</td>
</tr>

<tr>
<td>
<table cellspacing="4" cellpadding="4" style="border-bottom-width: thin; 
border-left-width:thin; border-right-width: thin; border-top-width: thin; border-style: dotted; border-color: red;">
<tr><td>
Please remember that in the first three months of membership you
are not allowed to submit a claim for a value greater of the amount
you paid for the insurance.
</td></tr>
</table>
</td>
</tr>

<tr>
<td align="center">
  <img src="car1.jpg">
</td>
</tr>

<tr>
<td align="center">
<form action="claim.php" method="post" name="">
<table cellspacing="4" cellpadding="4" style="border-bottom-width: thin; border-left-width: 
thin; border-right-width: thin; border-top-width: thin; border-style: dotted; border-color: red;">
<tr>
 <td>Description</td> <td><input type="text" name="desc" class="cssborder"></td>
</tr>
<tr>
 <td>Date</td> <td><input type="text" name="date" class="cssborder"></td>
</tr>
<tr>
 <td>Amount of Damage (in $)</td> <td><input type="text" name="damage" class="cssborder"></td>
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



