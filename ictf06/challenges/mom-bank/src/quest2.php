<?php
session_start();
require('myfuncs.php');
myheader("Become ah membuh (2)");

$_SESSION['q1'] = $_GET['q1'];
$_SESSION['q2'] = $_GET['q2'];
$_SESSION['q3'] = $_GET['q3'];
$_SESSION['q4'] = $_GET['q4'];
$_SESSION['user'] = $_GET['user'];
$_SESSION['step'] = 'first';

/* print_r($_SESSION); */
?>

<form method="get" action="quest3.php"> 

<ol start="5">

<li>
Got y'all evuh fought loudly with ah significant othuh in ah public place?<br/>
<input type="radio" name="q5" value="0" />Yep, but only once<br />
<input type="radio" name="q5" value="1" />Yep, mo then once<br />
<input type="radio" name="q5" value="2" />Nope, Ah nevuh had ah significant othuh<br />
</li>

<li>
Got y'all been engagd tuh people y'all did not marry mo then twice?<br/>
<input type="radio" name="q6" value="0" />Yep<br />
<input type="radio" name="q6" value="1" />Nope<br />
</li>

<li>
Got y'all evuh voluntarily gone without bathin' fer mo then five days?<br/>
<input type="radio" name="q7" value="0" />Yep<br />
<input type="radio" name="q7" value="1" />Nope<br />
<input type="radio" name="q7" value="2" />Define voluntarily<br />
</li>

<li>Do y'all own ah gasoline buggy which is dilapidatd, discolord, and rarely workin'? If this gasoline buggy is in ah garage, ore is otherwise hidden from traffic, y'all c'n click "Nope".<br/>
<input type="radio" name="q8" value="0" />Yep<br />
<input type="radio" name="q8" value="1" />Nope<br />
<input type="radio" name="q8" value="2" />Yep, and tis up on ah ramp<br />
<input type="radio" name="q8" value="3" />Yep, and tis up on cinduh blocks<br />
<input type="radio" name="q8" value="4" />Yep, and tis in mah backward<br /></li>
</ol>

<input type="submit" value="Submit" />

</form>

<?php
myfooter();
?>
