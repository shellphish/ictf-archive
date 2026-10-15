#!/usr/bin/php-cgi
<?php setcookie('cust_id', ip2long($_SERVER['REMOTE_ADDR']),time() +(60*60*24*7)); ?>
<html>
  <head>
    <title>Open Relay Server List (ORSL)</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <meta name="keywords" content="open relay lists, spam lists, spam, open relay server lists, ORSL">
    <meta name="description" content="List of Open erlay Server Lists.">
    <link rel="stylesheet" href="/~acquire/spam.css" type="text/css">
  </head>
  <body>
    <div class="banner">
      <h1>Open Relay Server Lists (ORSL)</h1>
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

      <p>This page lists <B>FREE</B> open relays that you can use for spamming!</p>

      <p>However, we strongly recommend that you use our paid service which gives you hundreds of 
      <b>high-quality</b> mail servers!  The cost is only $80!</p>

      <p>Please select the Paid Service tab in the menu start your spamming experience!</p>

      <p>If you are not sure about how to take advantage of these servers, please go to the howto page!  
         It provides detailed information and network status of these hosts!</p>

      <p>In order to prevent anti-spam websites from finding this page, we have taken the ":" out of the IPv6 addresses!</p>
	</p> 
        <table width="80%" border="1">
          <tr> 
                <td width="50%"><b>IPv6 Address (128 bits) </b></td>
                <td width="22%"><b>Service Provider</b></td>
                <td width="28%"><b>Description</b></td>
           </tr>
              <tr valign="top"> 
                <td height="33">3ffe050100080000026097fffe40efab</a></td>
                <td height="33">Abilene</td>
                <td height="33">Maintained by UCLA GG Lab</td>
              </tr>
              <tr valign="top">  
                <td height="33">3ffe0501000a0000026c97fffe40efab</a></td>
                <td height="33">Abilene</td> 
                <td height="33">Maintained by UCR GSA</td>
              </tr>
              <tr valign="top">  
                <td height="33">3ffe050100080e00026a97fffe40efab</a></td>
                <td height="33">Abilene</td> 
                <td height="33">Maintained by CMU CyLab</td>
              </tr>
              <tr valign="top">  
                <td height="33">esd7050400080700026097fffe40efab</a></td>
                <td height="33">HiNet</td> 
                <td height="33">Maintained by NTU Taiwan</td>
              </tr>
              <tr valign="top">  
                <td height="33">3ffe050100080027026097fffe40efab</a></td>
                <td height="33">Brit. Telecomm.</td> 
                <td height="33">Maintained by UCE, UK</td>
              </tr>
              <tr valign="top">  
                <td height="33">42fa050100480010026096fff740efab</a></td>
                <td height="33">Quest</td> 
                <td height="33">SpamISus</td>
              </tr>
              <tr valign="top">  
                <td height="33">750a0aa100b80010026096fff740efab</a></td>
                <td height="33">gov2</td> 
                <td height="33">NIST</td>
              </tr>
              <tr valign="top">  
                <td height="33">3b95050de00cc0000026097ffe40efab</a></td>
                <td height="33">PRISA</td> 
                <td height="33">BlackHat.com</td>
              </tr>
              <tr valign="top">  
                <td height="33">45cd050de00cc00dd026097fffe40efa</a></td>
                <td height="33">WorldCom</td> 
                <td height="33">Elite!</td>
              </tr>
              <tr valign="top">  
                <td height="33">866050de00cc0000026795fffe49efab</a></td>
                <td height="33">gov2</td> 
                <td height="33">Department of Interior</td>
              </tr>
	</table>
     </div>
     <div class="footer">


Supported by the <a href="/~aqs/">Association for Quality SPAM</a>!
     </div>
  </body>
</html>
