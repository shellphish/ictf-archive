<?php
session_start(); 
unset($_SESSION['user']);
unset($_SESSION['step']);

require('myfuncs.php');
myheader("Become ah membuh");
?>

<p>Befouh y'all c'n become ah membuh y'all got tuh answuh this simple
questionaniuh.</p>

<form method="get" action="quest2.php"> 
<p>Tell me yah name: <input name="user" type="text" /></p>
<ol>

<li>Got y'all evuh livd in ah mobile home, trailuh, ore any device with ah trailuh hitch?<br />
<input type="radio" name="q1" value="0" />Nope<br />
<input type="radio" name="q1" value="1" />Yep, but only while on vacashun/tour<br />
<input type="radio" name="q1" value="2" />Double-wide. Ye Dawgies!!!<br />
</li>

<li>Complete this sentence: Shirts with sleeves cut off uv 'em is<br/>
<input type="radio" name="q2" value="0" />Fer losers<br />
<input type="radio" name="q2" value="1" />Bitchin`<br />
<input type="radio" name="q2" value="2" />Sexy on mah maw<br />

</li>

<li>Do y'all got ah mullet?<br/>
<input type="radio" name="q3" value="0" />Nope<br />
<input type="radio" name="q3" value="1" />Yep<br />
</li>

<li>Got y'all evuh taken yore shirt off while confrontd by duh constable?<br/>
<input type="radio" name="q4" value="0" />Nope<br />
<input type="radio" name="q4" value="1" />Yep<br />
</li>

</ol>
<input type="submit" value="Submit" />
</form>


<?php
myfooter();
?>
