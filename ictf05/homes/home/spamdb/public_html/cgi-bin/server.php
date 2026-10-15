#!/usr/bin/php-cgi
<?php

	include("lib/xmlrpc.inc");
	include("lib/xmlrpcs.inc");
	include("spamdb.inc");

	class xmlrpc_server_methods_container
	{
		function phpwarninggenerator($m)
		{
			$a = $b;
			return new xmlrpcresp(new xmlrpcval(1, 'boolean'));
		}
	}

	$echo_sig = array(array($xmlrpcString, $xmlrpcString));
	$echo_doc = 'Echo test.';
	function echotest($params)
	{
		global $xmlrpcerruser, $counter;
		$err = "";
		$p1 = $params->getParam(0);

		if (isset($p1) && ($p1->scalartyp() == "string")) {
			$p1_val = $p1->scalarval();
		}
		else {
			$err = "Error";
		}

		if ($err) {
			return new xmlrpc(0, $xmplrpcerruser, $err);
		}
		else {
			return new xmlrpcresp(new xmlrpcval($p1_val));
		}
	}

	$create_account_sig =array(array($xmlrpcString, $xmlrpcString));
	$create_account_doc = "Create new account and return password.";
	function create_account($params)
	{
		global $xmlrpcerruser;
		$err = "";
		$password = "";
		$p1 = $params->getParam(0);

		if (isset($p1) && ($p1->scalartyp() == "string")) {
			$email = $p1->scalarval();
			$password = gen_passwd();
			$db = db_access();
			db_add_account($db, $email, $password);
			db_save($db);
		}
		else {
			$err = "parameter error";
		}
		
		if ($err) {
			return new xmlrpc(0, $xmplrpcerruser, $err);
		}
		else {
			return new xmlrpcresp(new xmlrpcval($password));
		}
	}

	$db_size_sig = array(array($xmlrpcInt));
	$db_size_doc = 'Get number of items in database.';
	function db_size()
	{
		global $xmlrpcerruser;
		$err = "";

		$db = db_access();
		$num = db_countitems($db);

		return new xmlrpcresp(new xmlrpcval($num));
	}

	$upload_data_sig = array(array($xmlrpcString, $xmlrpcString, $xmlrpcString, $xmlrpcString));
	$upload_data_doc = "Upload email data, use login and password to select account.";
	function upload_data($params)
	{
		global $xmlrpcerruser;
		$err = "";
		$p1 = $params->getParam(0);
		$p2 = $params->getParam(1);
		$p3 = $params->getParam(2);

		if (isset($p1) && ($p1->scalartyp() == "string") &&
				isset($p2) && ($p2->scalartyp() == "string") &&
				isset($p3) && ($p3->scalartyp() == "string")) {

			$email = $p1->scalarval();
			$password = $p2->scalarval();
			$data = $p3->scalarval();
			$db = db_access();
			$acc = db_getitem($db, $email, $password);
			if ($acc) {
				db_delitem($db, $email, $password);
				db_add_full($db, $email, $password, $data, date("U"));
				db_save($db);
			}
			else {
				$err = "ERR";
			}
		}
		else {
			$err = "parameter error";
		}
		
		if ($err) {
			return new xmlrpc(0, $xmplrpcerruser, $err);
		}
		else {
			return new xmlrpcresp(new xmlrpcval("OK"));
		}
	}

	$veryfy_data_sig = array(array($xmlrpcString, $xmlrpcString, $xmlrpcString));
	$veryfy_data_doc = "Veryfy uploaded data by reading it back.";
	function gen_passwd() { return("staticpassword"); }
	function veryfy_data($params)
	{
		global $xmlrpcerruser;
		$err = "";
		$data = "";
		$p1 = $params->getParam(0);
		$p2 = $params->getParam(1);

		if (isset($p1) && ($p1->scalartyp() == "string") &&
				isset($p2) && ($p2->scalartyp() == "string")) {

			$email = $p1->scalarval();
			$password = $p2->scalarval();
			$db = db_access();
			$acc = db_getitem($db, $email, $password);
			if ($acc) {
				$data = item_get_data($db, $email, $password);
			}
		}
		else {
			$err = "parameter error";
		}
		
		if ($err) {
			return new xmlrpc(0, $xmplrpcerruser, $err);
		}
		else {
			return new xmlrpcresp(new xmlrpcval($data));
		}
	}

	$check_queue_sig = array(array($xmlrpcString, $xmlrpcString));
	$check_queue_doc = "Check spam queue for domain.";
	function check_queue($params)
	{
		global $xmlrpcerruser;
		$err = "";
		$data = "";
		$p1 = $params->getParam(0);

		if (isset($p1) && ($p1->scalartyp() == "string")) {
			if (strlen($p1) > 3) {
				$db = db_access();
				$res = db_searchitem($db, $p1->scalarval());
				if ($res) {
					foreach ($res as $r) {
						$data = $data . $r->content . ",";
					}
				}
			}
			else {
				$err = "parameter error";
			}
		}
		else {
			$err = "parameter error";
		}

		if ($err) {
			return new xmlrpc(0, $xmplrpcerruser, $err);
		}
		else {
			return new xmlrpcresp(new xmlrpcval($data));
		}
	}

	$spam_test_sig = array(array($cmlrpcInt, $xmlrpcString, $xmlrpcString));
	$spam_test_doc = "Check data for spam.";
	function spam_test($params)
	{
		global $xmlrpcerruser;
		$err = "";
		$data = "";
		$p1 = $params->getParam(0);
		$p2 = $params->getParam(1);

		if (isset($p1) && ($p1->scalartyp() == "string") &&
				isset($p2) && ($p2->scalartyp() == "string")) {

			$email = $p1->scalarval();
			$password = $p2->scalarval();
			$db = db_access();
			$acc = db_getitem($db, $email, $password);
			if ($acc) {
				$data = item_get_data($db, $email, $password);
				if (stristr($data, "spam")) $data = 1;
				else $data = 0;
			}
		}
		else {
			$err = "parameter error";
		}

		if ($err) {
			return new xmlrpc(0, $xmplrpcerruser, $err);
		}
		else {
			return new xmlrpcresp(new xmlrpcval($data));
		}
	}

	$delete_account_sig = array(array($xmlrpcString, $xmlrpcString, $xmlrpcString));
	$delete_account_doc = "Delete account.";
	function delete_account($params)
	{
		global $xmlrpcerruser;
		$err = "";
		$data = "";
		$p1 = $params->getParam(0);
		$p2 = $params->getParam(1);

		if (isset($p1) && ($p1->scalartyp() == "string") &&
				isset($p2) && ($p2->scalartyp() == "string")) {

			$email = $p1->scalarval();
			$password = $p2->scalarval();
			$db = db_access();
			$acc = db_getitem($db, $email, $password);
			if ($acc) {
				db_delitem($db, $user, $password);
				db_save($db);
			}
		}
		else {
			$err = "parameter error";
		}

		if ($err) {
			return new xmlrpc(0, $xmplrpcerruser, $err);
		}
		else {
			return new xmlrpcresp(new xmlrpcval($data));
		}
	}

	$o = new xmlrpc_server_methods_container;

	$a = array(
		"spamdb.echo" => array(
			"function"  => "echotest",
			"signature" => $echo_sig,
			"docstring" => $echo_doc
		),
		"spamdb.db_size" => array(
			"function"  => "db_size",
			"signature" => $db_size_sig,
			"docstring" => $db_size_doc
		),
		"spamdb.create_account" => array(
			"function"  => "create_account",
			"signature" => $create_account_sig,
			"docstring" => $create_account_doc
		),
		"spamdb.delete_account" => array(
			"function"  => "delete_account",
			"signature" => $delete_account_sig,
			"docstring" => $delete_account_doc
		),
		"spamdb.upload_data" => array(
			"function"  => "upload_data",
			"signature" => $upload_data_sig,
			"docstring" => $upload_data_doc
		),
		"spamdb.veryfy_data" => array(
			"function"  => "veryfy_data",
			"signature" => $veryfy_data_sig,
			"docstring" => $veryfy_data_doc
		),
		"spamdb.check_queue" => array(
			"function"  => "check_queue",
			"signature" => $check_queue_sig,
			"docstring" => $check_queue_doc
		),
		"spamdb.spam_test" => array(
			"function"  => "spam_test",
			"signature" => $spam_test_sig,
			"docstring" => $spam_test_doc
		)
	);

	$s = new xmlrpc_server($a, false);
	$s->setdebug(3);
	$s->allow_system_funcs = true;
	$s->compress_response = true;
	$s->service();

?>
