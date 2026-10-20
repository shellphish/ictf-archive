<html>
<head>
<title>Open Relay Server List (ORSL): Paid Service</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<meta name="keywords" content="open relay lists, spam lists, spam, open relay server lists, ORSL">
<link rel="stylesheet" href="/acquire/spam.css" type="text/css">
</head>

<body>
  <div class="banner">
      <h1>Buy It Today!</h1>
</div>
 <div class="sidebar">
      <h2>Menu</h2>

      <ul>
        <li><a href="index.php">ORSL</a></li>

        <li><a href="howto.php">Howto</a></li>

        <li><a href="paid_service.php">Paid Service</a></li>

        <li><a href="contact.php">Contact</a></li>

        <li><a href="links.php">Links</a></li>
      </lu>
    </div>

    <div class="main">

    <p>We offer the <B>ultimate</b> spam resource!  Hundreds of fast and
    reliable open relays are available to you for just $80!  Don't put up with
    slow relay servers anymore... BUY TODAY!</p>

    <p>Please follow these directions carefully:</p>

    <ol>
	<li>Click on the Contact tab</li>

	<li>Use the PGP key you find on that page to send an email to
	admin@spam4nerds.com</li>

	<li>Please include in the email your Credit Card Number, Expiration
	Date, and the check digits on the back of the card!  Please also
	include your public key!</li> 

	<li>Once your order is processed (within
	72 hours), we will send an email encrypted using your public key! And
	your status will become "paid"!</li>
		
      </ol>

<?php
$status=$_GET['status'];
print('<div align="center">');
if ($status == "paid")
{
    if($fp = fopen("data/.temp.txt","r"))
    {
        $lock = flock($fp, LOCK_SH);
        if ($lock) {
            $entire=file("data/.temp.txt");
            flock($fp, LOCK_UN);

            $size=count($entire);
            for ($i=0; $i < $size && $i < 15; $i++)
				printf("%s<BR>",$entire[$i]);
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
print('</div><BR>');
?>

    </div>
     <div class="footer">


Supported by the <a href="/~aqs/">Association for Quality SPAM</a>!
     </div>
</body>
</html>
