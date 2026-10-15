<?
 $con = mysql_connect('localhost', 'ins', 'abracadabra');
 if (!mysql_select_db('insurance', $con)) {
     die('Database connection problem: ' . mysql_error());
 }
?>
