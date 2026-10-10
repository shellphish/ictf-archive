<?

function checkAuth($user, $auth, &$msg)
{
	if((strlen($user) == 0) || (strlen($auth) == 0))
	{
		$msg = "Please enter user and password";
		return -1;
	}

	$key = "";
	// Extract hashed password from db
	if(getHashedPasswordFromUser($user, $key) < 0)
	{
		$msg = "Invalid user";
		return -1;
	}

	// Decode le paramètre d'authentification
	$auth = rc4Decode(base64_decode($auth), $key);

	// Vérifie que le paramètre d'authentification est conforme
	if(preg_match("/^([^:]+):([^:]+):([^:]+):([^:]+)$/", $auth, $matches) == 0)
	{
		$msg = "Invalid password";
		return -1;
	}

	// Extract parameters
	$timerand_c = $matches[1];
	$user_c = $matches[2];
	$pass_c = $matches[3];
	$crc_c = $matches[4];

	// Vérifie le CRC
	$s = sprintf("%x", crc32($timerand_c.":".$user_c.":".$pass_c));

	while(strlen($crc_c) < 8)
		$crc_c = "0".$crc_c;

	while(strlen($s) < 8)
		$s = "0".$s;

	if(strcmp($crc_c, $s))
	{
		$msg = "Invalid cookie";
		return -1;
	}

	// Vérifie que le user est bien conforme
	if((strcmp($user, $user_c) != 0) || (strcmp(sha1($key), $pass_c) != 0))
	{
		$msg = "Invalid cookie";
		return -1;
	}

	// Vérifie la validité dans le temps du cookie
	$t = "";
	for($i=0;$i<20;$i+=2)
	{
		$t = $t.substr($timerand_c, 1+$i, 1);
	}

	if($t > time())
	{
		$msg = "Invalid cookie";
		return -1;
	}

	if(time()-$t > 60)
	{
		$msg = "Cookie out of date, re-enter user and pass";
		return -1;
	}

	return 0;
}

function getHashedPasswordFromUser($user, &$hpass)
{
	mysql_connect("localhost", "raccess", 'akfok(dk_fzeljf90jkf=');
	if(!mysql_select_db("_USERS_"))
		return -1;

	$query = "SELECT password FROM _AUTH_TB_ WHERE (username = '$user')";
	$result = mysql_query($query);
	if($result)
	{
		if(mysql_num_rows($result) == 1)
		{
			$row = mysql_fetch_row($result);
			$hpass = $row[0];
			mysql_close();
			return 0;
		}
	}
	mysql_close();
	return -1;
}

function str2array($s)
{
	$l = strlen($s);
	$arr = array();
	for($i=0;$i<$l;$i++)
	{
		$c = substr($s, $i, 1);
		array_push($arr, $c);
	}

	return $arr;
}

function rc4Decode($msg, $key)
{
	$klen = strlen($key);
	$keyArray = str2array($key);

	$S = array();
	$j = 0;

	// Rempli le tableau S
	for($i=0;$i<256;$i++)
	{
		$S[$i]=$i;
	}

	// Initialisation du tableau S
	$j = 0;
	for($i=0;$i<256;$i++)
	{
		$j = ($j+$S[$i]+ord($keyArray[$i%$klen]))%256;
		$t = $S[$i];
		$S[$i] = $S[$j];
		$S[$j] = $t;
	}

	$mlen = strlen($msg);
	$msgArray = str2array($msg);

	$i = 0;
	$j = 0;
	$output="";
	for($k=0;$k<$mlen;$k++)
	{
		$i = ($i+1)%256;
		$j = ($j+$S[$i])%256;
		$t = $S[$i];
		$S[$i] = $S[$j];
		$S[$j] = $t;
		$output .= chr($S[($S[$i]+$S[$j])%256]^ord($msgArray[$k]));
	}

	return $output;
}


