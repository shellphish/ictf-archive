<HTML>
<BODY>
<?php
$ip=$_GET['ip'];
$network=$_GET['net'];
$description=$_GET['de'];

if (is_null($ip) || is_null($description) || is_null($network) )
{
	printf("Error\n");
}
else 
{
	if($fp = fopen("data/.temp.txt","a"))
	{
		$line="$ip,$network,$description\n";
		$lock = flock($fp, LOCK_EX);
		if ($lock) { 
			fwrite($fp, $line);
			flock($fp, LOCK_UN);
			printf("Add a new spam relay correctly correctly\n");
		} 
		else 
		{
		   printf("Couldn't lock the file");
		}
		fclose($fp);
	}
	else
	{
		printf("Could not open the file");
	}
}

?>
</BODY>
</HTML>
