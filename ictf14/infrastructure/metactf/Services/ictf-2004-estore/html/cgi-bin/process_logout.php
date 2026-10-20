#!/usr/bin/php4-cgi
<?php 
require('DB.php');
require('myfuncs.php');
$mysql_url = "mysql://estoreuser:retard@localhost/estore";
myheader("Logout");

$debug = $_GET['debug'];
$decision = $_GET['decision'];

if (${debug}) {
  print "<p>DEBUG: MySQL url: ${mysql_url}</p>";
  print "<p>Decision: ${decision}</p>";
}

/* Connects to database */
$db = DB::connect(${mysql_url});
if (DB::isError($db)) {
  diefooter($db->getMessage());
}

/* Checks the cookie */
$cookie = ${HTTP_COOKIE_VARS}['auth'];
$username = checkcookie($db, $cookie);

if ($debug) {
  print "<p>DEBUG: Logging out user ${username}</p>\n";
}

/* Cancel purchase */
if (${decision} == "Cancel Purchase and Logout") {
  if (${debug}) {
    print "<p>DEBUG: Canceling user purchases</p>\n";
  }
  $st = $db->prepare("UPDATE items SET buyer=NULL WHERE buyer='${username}' AND paid=0");
  if (DB::isError($st)) {
    diefooter($st->getMessage());
  }
  $rs = $db->execute($st);
  if (DB::isError($rs)) {
    diefooter($rs->getMessage());
  }
} else if (${decision} == "Buy Items and Logout") {
  if (${debug}) {
    print "<p>DEBUG: charging user for purchases</p>\n";
  }

  /* Retrieves the items for this user */
  $st = $db->prepare("SELECT * FROM items WHERE buyer='${username}' AND paid=0");
  if (DB::isError($st)) {
    diefooter($st->getMessage());
  }
  $rs = $db->execute($st);
  if (DB::isError($rs)) {
    diefooter($rs->getMessage());
  }
  /* Computes the total price */
  $totalprice = 0;
  while ($row = $rs->fetchRow(DB_FETCHMODE_ASSOC)) {
    if ($debug) {
      print "<p>DEBUG: charging user ${username} ${row['price']} for item ${row['name']} sold by ${row['seller']}</p>\n";
    }
    /* Inserts a charge */
    $seller = $row['seller'];
    $price = $row['price'];

    $st2 = $db->prepare("INSERT INTO charges (buyer, seller, price) VALUES ('${username}', '${seller}', '${price}')");
    if (DB::isError($st2)) {
      diefooter($st2->getMessage());
    }
    $rs2 = $db->execute($st2);
    if (DB::isError($rs2)) {
      diefooter($rs2->getMessage());
    }
    /* Update the paid flag for the item */
    $id = $row['id'];
    $st2 = $db->prepare("UPDATE items SET paid=1 WHERE id='${id}'");
    if (DB::isError($st2)) {
      diefooter($st2->getMessage());
    }
    $rs2 = $db->execute($st2);
    if (DB::isError($rs2)) {
      diefooter($rs2->getMessage());
    }
    
    $totalprice = $totalprice + $row['price'];
  }
  print "<p>You have have been charged ${totalprice} for your items.</p>";

  $rs->free();
} else {
  diefooter("Unknown decision: ${decision}");
}

/* Logs out the user */
$st = $db->prepare("UPDATE users SET cookie=NULL WHERE username='${username}'");
if (DB::isError($st)) {
  diefooter($st->getMessage());
}
$rs = $db->execute($st);
if (DB::isError($rs)) {
  diefooter($rs->getMessage());
}

print "<p>You have have been successfully logged out.</p>";

myfooter();
?>


