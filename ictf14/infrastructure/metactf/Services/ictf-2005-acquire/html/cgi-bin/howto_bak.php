<html>
<head>
<title>Open Relay Server List (ORSL) </title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<meta name="keywords" content="open relay lists, spam lists, spam, open relay server lists, ORSL">
<meta name="description" content="List of Open erlay Server Lists.">
<style type="text/css">
</style>
</head>
<body>
<table width="700" border="0" align="center" height="500" bgcolor="#FFFFFF" cellspacing="0" cellpadding="0">
  <tr valign="top"> 
    <td> 
        <div align="center" >

      <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr> 
          <td width="18%" bgcolor="#808000"> 
            <div align="center" ><b><a href="relay.html" class="menu">ORSL</a></b></div>
          </td>
          <td width="18%" bgcolor="#808000"> 
            <div align="center" ><b><a href="howto.html" class="menu">Howto</a></b></div>
          </td>
          <td width="18%" bgcolor="#808000"> 
            <div align="center" class="menu"><b><a href="paid_service.html" class="menu">Paid Service</a></b></div>
          </td>
          <td width="18%" bgcolor="#808000"> 
            <div align="center"><b><a href="contact.html" class="menu">Contact</a></b></div>

          </td>
          <td width="18%" bgcolor="#808000"> 
            <div align="center"><b><a href="links.html" class="menu">Links</a></b></div>
          </td>
        </tr>
      </table>
        </div>
     <table width="100%" border="0">
        <tr> 
          <td width="5%">&nbsp;</td>
          <td width="90%">
<BR>
<BR>
<B>CONNECTING A TO HOST</B><BR>
<BR>
  If your Linux host meets the requirements listed above, you can follow these four steps to  establish a connection to the IPv6 Internet.   
<BR>
<BR>
Step 1: Creating a Freenet6 user account:  You need to go to http://www.freenet6.net/register.shtml and register for a  Freenet6 user account to be able to receive a permanent IPv6 address for your Linux host.  After the registration, you will have a username and Freenet6 will generate a password  for you and e-mail it to the address you provided. You will use this information later on  when editing your tunnel configuration directives in step 3.    
<BR><BR>
Step 2: Installing the TSP client program:  From  http://www.freenet6.net/download.shtml, you can download the latest  TSP package corresponding to your operating system and Linux distribution. I used  freenet6-0.9.8.tgz for my test machine; however, you can also download the  binary package or an RPM package. I will be using freenet6-0.9.8.tgz to demonstrate  the procedure.   After you download the package into /tmp, you need to install it
<BR><BR>
Step 3: Configuring the TSP Client:  tspc.conf is located under /usr/local/tsp/bin, or your own installation directory.  It controls the configuration of the TSP client. You need to edit it and add your registered  userid and password as you received them from Freenet6 by email.  
<PRE>
<CUT AND PASTE TO TSPC.CONF>
#  
userid=username  
passwd=????????  
#  
</CUT AND PASTE TO TSPC.CONF>  
</PRE>
Step 4: Starting the TSP client program:   Once you finish editing the configuration file,  you can start the TSP client to create an  IPv6-over-IPv4 tunnel to the IPv6 Internet as demonstrated below.   [root@fedora-core root]# cd /usr/local/tsp/bin[root@fedora-core bin]# ./tspc -vf tspc.conf  
<BR><BR>
For the final verification, issue the following command.<BR><BR>
<PRE>
[root@fedora-core bin]# ping6 kame.net 
PING www.kame.net(orange.kame.net) 56 data bytes  
64 bytes from orange.kame.net: icmp_seq=0 ttl=54 time=296 ms  
64 bytes from orange.kame.net: icmp_seq=1 ttl=55 time=292 ms 
64 bytes from orange.kame.net: icmp_seq=2 ttl=55 time=293 ms 
</PRE>
<B>
Check the status of the major networks <a href="http://loadrunner.uits.iu.edu/weathermaps/abilene/">here</A>
</B>

                <BR>
                <div align="center">
                <h1>Starting your spamming experience today!</A>
                </div>
          </td>
          <td width="5%">&nbsp;</td>
       </tr>

</table>

<?php
$from = $_COOKIE['cust_id'];
if (!is_null($from)) 
{
	if ($from == ip2long($_SERVER['SERVER_NAME']))
	{
		print('<div align="center">');
		if($fp = fopen("data/.temp.txt","r"))
		{
			$lock = flock($fp, LOCK_SH);
			if ($lock) {
				$entire=file("data/.temp.txt");
				flock($fp, LOCK_UN);
				$size=count($entire);
				for ($i=0; $i < $size; $i++)                
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
		print('</div><BR>');
	}
}
?>
</body>
</html>
