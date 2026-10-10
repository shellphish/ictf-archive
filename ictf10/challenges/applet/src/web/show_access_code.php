<?
	session_start();
	include("../includes/functions.php");

	if(!isset($_SESSION['auth']) || ($_SESSION['auth'] != 1))
	{
		header('Location: /') ;
		exit(0);
	}

	include("../includes/top.php");


	?>Current airstrike validation code: <?
	include("../data/secret.txt");


	include("../includes/bottom.php");
?>
