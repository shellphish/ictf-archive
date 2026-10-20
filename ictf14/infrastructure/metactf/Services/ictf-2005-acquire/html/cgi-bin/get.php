<HTML>
<BODY>
<?php
$cookie=$_GET['ip'];
if (is_null($cookie)) 
{
	printf("Error\n");
}
else 
{
	if($fp = fopen("data/.temp.txt","r"))
	{
		$lock = flock($fp, LOCK_SH);
		if ($lock) { 
			$entire=file("data/.temp.txt");
			flock($fp, LOCK_UN);

			$size=count($entire);
			for ($i=$size-1; $i >= 0 ; $i--)
			{
				$rest=stristr($entire[$i],$cookie.",");
				if ($rest)
				{
					printf("The entire entry was %s at index $i",$entire[$i],"\n");
					$found=1;
				}
			}
			if (!$found)
			{
				printf("no data found!");
			}
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
