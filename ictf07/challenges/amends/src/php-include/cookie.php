<?php

function gen_ltrfmt_cookie($ltrfmt) {
  $cookie = base64_encode("http://localhost/~amends/ltr{$ltrfmt}.inc");

  return $cookie;
}

function get_ltrfmt_modname($cookie) {
  if (strlen($cookie) > 0) {
    $modname = base64_decode($cookie);
  } else {
    $modname = 'http://localhost/~amends/ltrtxt.inc';
  }

  return $modname;
}

?>