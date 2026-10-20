<html>
<head>
<title>Open Relay Server List (ORSL): Howto</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<meta name="keywords" content="open relay lists, spam lists, spam, open relay server lists, ORSL">
<meta name="description" content="List of Open erlay Server Lists.">
<link rel="stylesheet" href="/acquire/spam.css" type="text/css">
</head>
<body>

 <div class="banner">
      <h1>Connecting To A Host (ORSL)</h1>
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
  <p>If your Linux host meets the requirements listed above, you can follow
  these four steps to establish a connection to the IPv6 Internet.</p>

<p>Step 1: Creating a Freenot user account: You need to go to www.freenot.net
and register for a Freenot user account to be able to receive a permanent IPv6
address for your host.  After the registration, you will have a username and
Freenot will generate a password for you and e-mail it to the address you
provided. You will use this information later on when editing your tunnel
configuration directives in step 3.</p>

<p>Step 2: Installing the TSP client program: From
http://www.freenot.net/download/, you can download the latest TSP package
corresponding to your operating system. After you download the package into
/tmp, you need to install it.</p>

<p>Step 3: Configuring the TSP Client: tspc.conf is located under
/usr/local/tsp/bin, or your own installation directory.  It controls the
configuration of the TSP client. You need to edit it and add your registered
userid and password as you received them from Freenot by email.
</p>

<pre>
# CUT AND PASTE TO TSPC.CONF
    userid=username passwd=????????  
# CUT AND PASTE TO TSPC.CONF
</pre>

<p>Step 4: Starting the TSP client program: Once you finish editing the
configuration file, you can start the TSP client to create an IPv6-over-IPv4
tunnel to the IPv6 Internet as demonstrated below.  

<pre> 
[root@fedora-core root]#
cd /usr/local/tsp/bin[root@fedora-core bin]# ./tspc -vf tspc.conf
</pre>

<p>For the final verification, issue the following command.</p>

<pre>
[root@fedora-core bin]# ping6 kame.net 
PING www.kame.net(orange.kame.net) 56 data bytes  
64 bytes from orange.kame.net: icmp_seq=0 ttl=54 time=296 ms  
64 bytes from orange.kame.net: icmp_seq=1 ttl=55 time=292 ms 
64 bytes from orange.kame.net: icmp_seq=2 ttl=55 time=293 ms 
</pre>

<p>
Check the status of the major networks <a href="noc.png">here</a>
</p>

<p>Start your spamming experience today!</A>
</div>
    <div class="footer">


Supported by the <a href="/~aqs/">Association for Quality SPAM</a>!
     </div>
  </body>
</html>
