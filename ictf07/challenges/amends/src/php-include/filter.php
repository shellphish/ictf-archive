<?php

function filter_fname($fname) {
  $clean = false;
  $length = strlen($fname);

  if ($length > 0 and
      $length <= 50 and
      preg_match('/^[A-Za-z \'\-]+$/', $fname)) {
    $clean = $fname;
  }

  return $clean;
}

function filter_lname($lname) {
  $clean = false;
  $length = strlen($lname);

  if ($length > 0 and
      $length <= 50 and
      preg_match('/^[A-Za-z \'\-]+$/', $lname)) {
    $clean = $lname;
  }

  return $clean;
}

function filter_eaddr($eaddr) {
  $clean = false;
  $length = strlen($eaddr);

  if ($length > 0 and
      $length <= 50 and
      preg_match('/^[A-Za-z0-9._%-]+@[A-Za-z0-9._%-]+\.[A-Za-z]{2,4}$/', $eaddr)) {
    $clean = $eaddr;
  }

  return $clean;
}

function filter_price($price) {
  $clean = false;
  $length = strlen($price);

  if ($length > 0 and
      $length <= 10 and
      preg_match('/^\$?[0-9]*\.[0-9]{2}$/', $price)) {
    $clean = $price;
  }

  return $clean;
}

function filter_caseid($caseid) {
  $clean = false;
  $length = strlen($caseid);

  if ($length == 16 and
      preg_match('/^[A-Za-z0-9]{16}$/', $caseid)) {
    $clean = $caseid;
  }

  return $clean;
}

function filter_ltrfmt($ltrfmt) {
  $clean = false;

  if ($ltrfmt == 'pdf' or $ltrfmt == 'txt') {
    $clean = $ltrfmt;
  }

  return $clean;
}

function filter_ccnum($ccnum) {
  $clean = false;
  $length = strlen($ccnum);

  if ($length >= 1 and
      $length <= 51 and
      preg_match('/^[A-Za-z0-9=_\-]{1,51}$/', $ccnum)) {
    $clean = $ccnum;
  }

  return $clean;
}

function filter_error_msg($input, $link) {
  return "<p>You must supply an appropriate <b>$input</b> to register.  Please <a href=\"{$link}\">go back</a> and try again.</p>";
}

?>
