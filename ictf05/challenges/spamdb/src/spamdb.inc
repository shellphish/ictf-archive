<?php

	function db_getpath()
	{
		return("/home/spamdb/.db.xml");
	}

	function db_access()
	{
		if ($db = domxml_open_file(db_getpath())) {
		}
		else {
			if ($db = domxml_new_doc("1.0")) {
				$root = $db->create_element("SPAM");
				$root = $db->append_child($root);
			}
		else {
				exit(-1);
			}
		}

		return $db;
	}

	function db_save($db)
	{
		# use true, true so the file is not grepable :-)
		if ($db->dump_file(db_getpath(), true, true)) {
			chmod(db_getpath(), 0600);
		}
		else {
		}
	}

	function db_add_full($db, $email, $passwd, $data, $id)
	{
		$calcX = &$db->xpath_new_context();
		$root = $calcX->xpath_eval("/SPAM");
		$root = $root->nodeset[0];

		$elm = $db->create_element("ITEM");
		$elm = $root->append_child($elm);
		$elm1 = $db->create_element("EMAIL");
		$elm1 = $elm->append_child($elm1);
		$elm1d = $db->create_text_node($email);
		$elm1d = $elm1->append_child($elm1d);
		$elm2 = $db->create_element("PASSWORD");
		$elm2 = $elm->append_child($elm2);
		$elm2d = $db->create_text_node($passwd);
		$elm2d = $elm2->append_child($elm2d);
		$elm3 = $db->create_element("DATA");
		$elm3 = $elm->append_child($elm3);
		$elm3d = $db->create_text_node($data);
		$elm3d = $elm3->append_child($elm3d);
		$elm4 = $db->create_element("ID");
		$elm4 = $elm->append_child($elm4);
		$elm4d = $db->create_text_node($id);
		$elm4d = $elm4->append_child($elm4d);
	}

	function db_add_account($db, $email, $passwd)
	{
		$calcX = &$db->xpath_new_context();
		$root = $calcX->xpath_eval("/SPAM");
		$root = $root->nodeset[0];

		$elm = $db->create_element("ITEM");
		$elm = $root->append_child($elm);
		$elm1 = $db->create_element("EMAIL");
		$elm1 = $elm->append_child($elm1);
		$elm1d = $db->create_text_node($email);
		$elm1d = $elm1->append_child($elm1d);
		$elm2 = $db->create_element("PASSWORD");
		$elm2 = $elm->append_child($elm2);
		$elm2d = $db->create_text_node($passwd);
		$elm2d = $elm2->append_child($elm2d);
	}

	function db_getitem($db, $email, $pass)
	{
		$calcX = &$db->xpath_new_context();
		$res = $calcX->xpath_eval("//ITEM[EMAIL='" . $email . "' and PASSWORD='" . $pass ."']");
		if ($res) {
			return($res->nodeset);
		}
		else {
			return(NULL);
		}
	}

	function db_searchitem($db, $search)
	{
		$calcX = &$db->xpath_new_context();
		$res = $calcX->xpath_eval("//ITEM/EMAIL[contains(text(),'"  . $search . "')]/text()");
		if ($res) {
			return($res->nodeset);
		}
		else {
			return(NULL);
		}
	}

	function item_get_data($db, $email, $pass)
	{
		$calcX = &$db->xpath_new_context();
		$res = $calcX->xpath_eval("//ITEM[EMAIL='" . $email . "' and PASSWORD='" . $pass ."']/DATA/text()");
		if ($res) {
			return($res->nodeset[0]->content);
		}
		else {
			return(NULL);	
		}
	}

	function db_countitems($db)
	{
		$calcX = &$db->xpath_new_context();
		$res = $calcX->xpath_eval("*");
		$count = 0;
		foreach ($res->nodeset as $n) {
			$count++;
		}
		return $count;
	}

	function db_delitem($db, $email)
	{
		$calcX = &$db->xpath_new_context();
		$res = $calcX->xpath_eval("//ITEM[EMAIL='" . $email . "']");
		if ($res) {
			foreach ($res->nodeset as $n) {
				if ($n) {
					$n->unlink_node();
				}
			}
		}
	}
?>
