<?php 
include "vars.php";
?>

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
 <h1><? echo "$title"; ?></h1>
 <i>The best insurance for your farm tractor</i>
 </div>  

<br>

<?
if (isset($_GET["action"])){
	if ($_GET["action"]=="logout"){
		session_start();		
		$_SESSION["loggedin"]=false;
	}
}
?>

<table width="80%" border="0" align="center">
<tr>
<td width="35%" align="left" valign="top">
<? include "nav.php"; ?>
</td>
<td>
 <img width="90%" src="./hbcar.jpg">  
</td>

</tr>
<tr>
<td colspan="2" align="center"><small>Powered by Hillbilly Banks Co.</small></td>
</tr>
</table>
</div>
</body>
</html>
