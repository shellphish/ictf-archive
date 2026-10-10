<?
	session_start();
	include("../includes/functions.php");


	if(!isset($_SESSION['auth']))
	{
		$_SESSION['auth'] = 0;
	}

	$error_msg = "";
	if(isset($_GET['user']) && isset($_GET['auth']))
	{
		$user = $_GET['user'];
		$auth = $_GET['auth'];

		if(checkAuth($user, $auth, $error_msg) == 0)
		{
			$_SESSION['auth'] = 1;
		}
	}

	include("../includes/top.php");

	if($_SESSION['auth'] == 1)
	{
?>

	<h4 ALIGN="center">Access granted</h4>
	<p align="center">
		Display current <a href="./show_access_code.php">validation code</a>
	</p>
<?
	}
	else
	{
		$t = time();

		$r = "";
		while(strlen($r) < 10)
		{
			$r = sprintf("%s%d", $r, rand(0, 9));
		}

		$rand="";
		for($i=0;$i<10;$i++)
		{
			$rand = $rand.substr($r, $i, 1).substr($t, $i, 1);
		}
?>
	<h4 align="center"><?php print($error_msg);?></h4>
<!--
	<table align="center" width=200>
	<tr><td class="noborder">
-->
	<p align="center">
		<applet code="login.class" width="200" height="150">
			<param name="rand" value="<? print $rand; ?>">
		</applet>
	</p>
<!--
	</td></tr>
	</table>
-->

<?
	}

	include("../includes/bottom.php");
?>
