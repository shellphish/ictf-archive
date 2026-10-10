<?
	session_start();
	include("../includes/functions.php");


	$_SESSION['auth'] = 0;

	header('Location: /') ;


	include("../includes/bottom.php");
?>
