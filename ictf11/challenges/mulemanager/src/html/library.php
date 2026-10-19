<?php 

$mysql_host = "localhost";
$mysql_db = "mulemanager";
$mysql_user = "mulemanager";
$mysql_password = "grabthiswhileyoucan";
$test_fail_condition = "";
$data_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 +()-:.,;_@~/#%!?|$^<>'";
$admin_user = "admin";
$dispatcher = "localhost";
$dispatcher_port = 31337;
$ticket_dir = "/home/muleadmin/tickets";

if (isset($_SERVER) and array_key_exists('SERVER_NAME', $_SERVER)) {
  $server_name = $_SERVER['SERVER_NAME'];
 }
 else {
   $server_name = "localhost";
 }
$home_page = "/main.php";
$login_page = "/login.php";

$username = "";
$cookie = "";
$db = mysqli_connect($mysql_host, $mysql_user, $mysql_password, $mysql_db);
if ($db == false) {
  error_log("Database error 5112: Cannot connect to the database");
  diefooter("Database error 5112. Please contact the administrator.");
}

if (isset($_COOKIE["mulesession"])) {
  $cookie = $_COOKIE["mulesession"];
  $username = get_username($db, $cookie);
}

$style_pars_store = $_GET;
  
/**
 * Prints the page header
 * @param string $page The page title
 */
function myheader($page, $stylesheets=array(), $javascripts=array()) 
{
  global $home_page;
  global $login_page;
  global $server_name;
  global $username;

  print '
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head profile="http://gmpg.org/xfn/11">
    <meta http-equiv="Content-Type" content="text/html" charset="UTF-8" />
    <meta http-equiv="Pragma" content="no-cache"> 
    <meta name="language" content="en" />
    <link rel="stylesheet" type="text/css" media="all" href="http://' . $server_name . ':7899/style/main.css" />
';
  foreach($stylesheets as $stylesheet) {
    print '   <link rel="stylesheet" type="text/css" media="all" href="http://' . $server_name . ':7899/style/' . $stylesheet . '" />
';
  }
  print '
    <title>' . $page . '</title>
';
  foreach($javascripts as $javascript) {
    print '   <script src="' . $javascript . '" type="text/javascript"></script>
';
  }
  print '

  <body>
    <div id="container">
      <div id="header">
        <div id="header_preface">
        </div>
        <div id="header_content">
          <table id="title_table">
            <tr>
              <td id="title_logo_cell"><div id="title_logo"><a href="/"><img alt="The Logo" src="http://' . $server_name . ':7899/images/logo_small.png" /></a></div></td>
              <td id="title_text_cell"><div id="title_text_box"><span id="title_text">'. $page . '</span></div></td>
            </tr>
          </table>
        </div>
        <div id="header_postface">
          <div id="header_nav">
            <ul>
              <li><a href="/main.php"><span class="header_nav_item">Home</span></a></li>
              <li><a href="/mission.php"><span class="header_nav_item">Mission</span></a></li>
              <li><a href="/profile.php"><span class="header_nav_item">Profile</span></a></li>
              <li><a href="/send.php"><span class="header_nav_item">Send Message</span></a></li>
              <li><a href="/contact.php"><span class="header_nav_item">Contact Us</span></a></li>
              <li><a href="/logout.php"><span class="header_nav_item">Log Out</span></a></li>
            </ul>
          </div><!-- nav -->
        </div><!-- header_postface -->
      </div><!-- header -->
      <div id="main">
        <div id="main_preface">
';
  if ($username == "admin") {
    
    print '
          <div id="admin_nav">
            <ul>
              <li><a href="/~muleadmin/cgi-bin/users"><span class="admin_nav_item">Manage Users</span></a></li>
              <li><a href="/~muleadmin/cgi-bin/groups"><span class="admin_nav_item">Manage Groups</span></a></li>
            </ul>
          </div><!-- nav -->
';
  }
  print '
        </div><!-- main_preface -->
        <div id="main_content">
';
}


/**
 * Prints the page footer
 * @param string $page The page title
 */
function myfooter($page="") 
{
  print '        
        </div><!-- main_content -->
        <div id="main_postface"></div>
      </div><!-- main -->
      <div id="footer">
        <div id="footer_preface"></div>
        <div id="footer_content">
          <span id="copyright">&copy; 2011 MuleMaster, Inc., mulemaster.com - All rights reserved worldwide.</span>
        </div>
        <div id="footer_postface"></div>
      </div><!-- footer -->
    </div><!-- container -->
  </body>
</html>
';
}


function error_msg($msg) {
  print '
        <div class="error"><span class="error_txt">An error occurred: ' . $msg . '</span></div>
';
}

function app_msg($msg) {
  print '
        <div class="message"><span class="app_msg_txt">' . $msg . '</span></div>
';
}


function diefooter($msg) 
{
  error_msg($msg);

  myfooter("Error");
  die();
}


function get_page_url()
{
  $pageURL = 'http';
  if ($_SERVER["HTTPS"] == "on") {
    $pageURL .= "s";
  }

  $pageURL .= "://";
  $pageURL .= $_SERVER["SERVER_NAME"];

  if ($_SERVER["SERVER_PORT"] != "80" && $_SERVER["SERVER_PORT"] != "443") {
    $pageURL .= ":".$_SERVER["SERVER_PORT"];
  }

  $pageURL .= $_SERVER["REQUEST_URI"];

  return $pageURL;
}


function sanitize_data($data) 
{
  global $data_chars;

  if ($data == "") {
    return "";
  }

  $char_array = str_split($data);
  foreach ($char_array as $c) {
    if ($c != "") {
      if (strpos($data_chars, $c) === false) {
        return false;
      }
    }
  }

  return $data;
}


function sanitize_r_data($key, $array) 
{
  if (!array_key_exists($key, $array)) {
    return "";
  }
  return sanitize_data($array[$key]);
}


function get_username($db, $cookie) 
{
  $username = "";

  $st = mysqli_prepare($db, "SELECT username FROM users WHERE cookie=?"); 
  if ($st == false) {
    $err = mysqli_error($db);
    error_log("Database error 5112: $err");
    return $username;
  }

  $rs = mysqli_stmt_bind_param($st, "s", $cookie);
  if ($rs == false) {
    $err = mysqli_stmt_error($st);
    error_log("Database error 5232: $err");
    return $username;
  }
 
  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_stmt_error($st);
    error_log("Database error 5244: $err");
    return $username;
  }
  mysqli_stmt_store_result($st);
  if (mysqli_stmt_num_rows($st) != 1) {
    return $username;
  }
  mysqli_stmt_bind_result($st, $username);
  mysqli_stmt_fetch($st);
  mysqli_stmt_close($st);

  return $username;
}


function del_cookie($db, $username) 
{
  $st = mysqli_prepare($db, "UPDATE users SET cookie=NULL WHERE username=?");

  if ($st == false) {
    $err = mysqli_error($db);
    error_log("Database error 5143: $err");
    return;
  }

  $rs = mysqli_stmt_bind_param($st, "s", $username);
  if ($rs == false) {
    $err = mysqli_stmt_error($st);
    error_log("Database error 5235: $err");
    return;
  }

  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_stmt_error($st);
    error_log("Database error 5277: $err");
    return $username;
  }
  mysqli_stmt_close($st);
}

function new_cookie($db, $username) 
{
  global $cookie_secret;
  $new = md5($username . time() . getmypid() );

  $st = mysqli_prepare($db, "UPDATE users SET cookie=? WHERE username=?");

  if ($st == false) {
    $err = mysqli_error($db);
    error_log("Database error 5142: $err");
    return;
  }

  $rs = mysqli_stmt_bind_param($st, "ss", $new, $username);
  if ($rs == false) {
    $err = mysqli_stmt_error($st);
    error_log("Database error 5232: $err");
    return;
  }

  $rs = mysqli_stmt_execute($st);
  if ($rs == false) {
    $err = mysqli_stmt_error($st);
    error_log("Database error 5244: $err");
    return $username;
  }
  mysqli_stmt_close($st);
  
  return $new;
}

$browser_regex = "/[.-:]/"; /* allows only for ".", "-", and ":" */

function get_browser_name($agent_string)
{
  global $browser_regex;

  $browser="";
  $browser_data = end(explode(" ", $agent_string));
  $char_array = str_split($browser_data);
  foreach ($char_array as $c) {
    if (ctype_alnum($c) === false) {
      /* Makes sure that only the allowed special characters get through */
      $res = preg_match($browser_regex, " $c ");
      if ($res ==  0) {
	error_log("Character $c did not match the filtering regex ($agent_string)");
	return $browser;
      }
    }
    $browser = $browser . $c;
  }
  return $browser;
}

function ticket_log($ticket, $msg) 
{
  global $ticket_dir;
  $fname = $ticket_dir . "/" . $ticket;
  error_log("Logging to $fname");
  $fd = fopen($fname, "a");
  if ($fd == false) {
    error_log("Failed to write ticket log $fname");
    return false;
  }
  fprintf($fd, "%s\n", $msg);
  fclose($fd);
  return true;
}

function ticket_dump($ticket) 
{
  global $ticket_dir;

  $fname = $ticket_dir . "/" . $ticket;
  error_log("Reading from $fname");
  $fd = fopen($fname, "r");
  if ($fd == false) {
    error_log("Failed to write ticket log $fname");
    return false;
  }
  print '
<ul>
';
  $line = fgets($fd, 4096);
  print '<li class="ticket_log">' . $line . '</li>';
  print '
</ul>
';
  fclose($fd);
  return;
}


$option_countries = '
<option value="United States">United States</option> 
<option value="United Kingdom">United Kingdom</option> 
<option value="Afghanistan">Afghanistan</option> 
<option value="Albania">Albania</option> 
<option value="Algeria">Algeria</option> 
<option value="American Samoa">American Samoa</option> 
<option value="Andorra">Andorra</option> 
<option value="Angola">Angola</option> 
<option value="Anguilla">Anguilla</option> 
<option value="Antarctica">Antarctica</option> 
<option value="Antigua and Barbuda">Antigua and Barbuda</option> 
<option value="Argentina">Argentina</option> 
<option value="Armenia">Armenia</option> 
<option value="Aruba">Aruba</option> 
<option value="Australia">Australia</option> 
<option value="Austria">Austria</option> 
<option value="Azerbaijan">Azerbaijan</option> 
<option value="Bahamas">Bahamas</option> 
<option value="Bahrain">Bahrain</option> 
<option value="Bangladesh">Bangladesh</option> 
<option value="Barbados">Barbados</option> 
<option value="Belarus">Belarus</option> 
<option value="Belgium">Belgium</option> 
<option value="Belize">Belize</option> 
<option value="Benin">Benin</option> 
<option value="Bermuda">Bermuda</option> 
<option value="Bhutan">Bhutan</option> 
<option value="Bolivia">Bolivia</option> 
<option value="Bosnia and Herzegovina">Bosnia and Herzegovina</option> 
<option value="Botswana">Botswana</option> 
<option value="Bouvet Island">Bouvet Island</option> 
<option value="Brazil">Brazil</option> 
<option value="British Indian Ocean Territory">British Indian Ocean Territory</option> 
<option value="Brunei Darussalam">Brunei Darussalam</option> 
<option value="Bulgaria">Bulgaria</option> 
<option value="Burkina Faso">Burkina Faso</option> 
<option value="Burundi">Burundi</option> 
<option value="Cambodia">Cambodia</option> 
<option value="Cameroon">Cameroon</option> 
<option value="Canada">Canada</option> 
<option value="Cape Verde">Cape Verde</option> 
<option value="Cayman Islands">Cayman Islands</option> 
<option value="Central African Republic">Central African Republic</option> 
<option value="Chad">Chad</option> 
<option value="Chile">Chile</option> 
<option value="China">China</option> 
<option value="Christmas Island">Christmas Island</option> 
<option value="Cocos (Keeling) Islands">Cocos (Keeling) Islands</option> 
<option value="Colombia">Colombia</option> 
<option value="Comoros">Comoros</option> 
<option value="Congo">Congo</option> 
<option value="Congo, The Democratic Republic of The">Congo, The Democratic Republic of The</option> 
<option value="Cook Islands">Cook Islands</option> 
<option value="Costa Rica">Costa Rica</option> 
<option value="Cote D&ivoire">Cote D&#39;ivoire</option> 
<option value="Croatia">Croatia</option> 
<option value="Cuba">Cuba</option> 
<option value="Cyprus">Cyprus</option> 
<option value="Czech Republic">Czech Republic</option> 
<option value="Denmark">Denmark</option> 
<option value="Djibouti">Djibouti</option> 
<option value="Dominica">Dominica</option> 
<option value="Dominican Republic">Dominican Republic</option> 
<option value="Ecuador">Ecuador</option> 
<option value="Egypt">Egypt</option> 
<option value="El Salvador">El Salvador</option> 
<option value="Equatorial Guinea">Equatorial Guinea</option> 
<option value="Eritrea">Eritrea</option> 
<option value="Estonia">Estonia</option> 
<option value="Ethiopia">Ethiopia</option> 
<option value="Falkland Islands (Malvinas)">Falkland Islands (Malvinas)</option> 
<option value="Faroe Islands">Faroe Islands</option> 
<option value="Fiji">Fiji</option> 
<option value="Finland">Finland</option> 
<option value="France">France</option> 
<option value="French Guiana">French Guiana</option> 
<option value="French Polynesia">French Polynesia</option> 
<option value="French Southern Territories">French Southern Territories</option> 
<option value="Gabon">Gabon</option> 
<option value="Gambia">Gambia</option> 
<option value="Georgia">Georgia</option> 
<option value="Germany">Germany</option> 
<option value="Ghana">Ghana</option> 
<option value="Gibraltar">Gibraltar</option> 
<option value="Greece">Greece</option> 
<option value="Greenland">Greenland</option> 
<option value="Grenada">Grenada</option> 
<option value="Guadeloupe">Guadeloupe</option> 
<option value="Guam">Guam</option> 
<option value="Guatemala">Guatemala</option> 
<option value="Guinea">Guinea</option> 
<option value="Guinea-bissau">Guinea-bissau</option> 
<option value="Guyana">Guyana</option> 
<option value="Haiti">Haiti</option> 
<option value="Heard Island and Mcdonald Islands">Heard Island and Mcdonald Islands</option> 
<option value="Holy See (Vatican City State)">Holy See (Vatican City State)</option> 
<option value="Honduras">Honduras</option> 
<option value="Hong Kong">Hong Kong</option> 
<option value="Hungary">Hungary</option> 
<option value="Iceland">Iceland</option> 
<option value="India">India</option> 
<option value="Indonesia">Indonesia</option> 
<option value="Iran, Islamic Republic of">Iran, Islamic Republic of</option> 
<option value="Iraq">Iraq</option> 
<option value="Ireland">Ireland</option> 
<option value="Israel">Israel</option> 
<option value="Italy">Italy</option> 
<option value="Jamaica">Jamaica</option> 
<option value="Japan">Japan</option> 
<option value="Jordan">Jordan</option> 
<option value="Kazakhstan">Kazakhstan</option> 
<option value="Kenya">Kenya</option> 
<option value="Kiribati">Kiribati</option> 
<option value="Korea, Democratic People&#39;s Republic of">Korea, Democratic People&#39;s Republic of</option> 
<option value="Korea, Republic of">Korea, Republic of</option> 
<option value="Kuwait">Kuwait</option> 
<option value="Kyrgyzstan">Kyrgyzstan</option> 
<option value="Lao People&#39;s Democratic Republic">Lao People&#39;s Democratic Republic</option> 
<option value="Latvia">Latvia</option> 
<option value="Lebanon">Lebanon</option> 
<option value="Lesotho">Lesotho</option> 
<option value="Liberia">Liberia</option> 
<option value="Libyan Arab Jamahiriya">Libyan Arab Jamahiriya</option> 
<option value="Liechtenstein">Liechtenstein</option> 
<option value="Lithuania">Lithuania</option> 
<option value="Luxembourg">Luxembourg</option> 
<option value="Macao">Macao</option> 
<option value="Macedonia, The Former Yugoslav Republic of">Macedonia, The Former Yugoslav Republic of</option> 
<option value="Madagascar">Madagascar</option> 
<option value="Malawi">Malawi</option> 
<option value="Malaysia">Malaysia</option> 
<option value="Maldives">Maldives</option> 
<option value="Mali">Mali</option> 
<option value="Malta">Malta</option> 
<option value="Marshall Islands">Marshall Islands</option> 
<option value="Martinique">Martinique</option> 
<option value="Mauritania">Mauritania</option> 
<option value="Mauritius">Mauritius</option> 
<option value="Mayotte">Mayotte</option> 
<option value="Mexico">Mexico</option> 
<option value="Micronesia, Federated States of">Micronesia, Federated States of</option> 
<option value="Moldova, Republic of">Moldova, Republic of</option> 
<option value="Monaco">Monaco</option> 
<option value="Mongolia">Mongolia</option> 
<option value="Montserrat">Montserrat</option> 
<option value="Morocco">Morocco</option> 
<option value="Mozambique">Mozambique</option> 
<option value="Myanmar">Myanmar</option> 
<option value="Namibia">Namibia</option> 
<option value="Nauru">Nauru</option> 
<option value="Nepal">Nepal</option> 
<option value="Netherlands">Netherlands</option> 
<option value="Netherlands Antilles">Netherlands Antilles</option> 
<option value="New Caledonia">New Caledonia</option> 
<option value="New Zealand">New Zealand</option> 
<option value="Nicaragua">Nicaragua</option> 
<option value="Niger">Niger</option> 
<option value="Nigeria">Nigeria</option> 
<option value="Niue">Niue</option> 
<option value="Norfolk Island">Norfolk Island</option> 
<option value="Northern Mariana Islands">Northern Mariana Islands</option> 
<option value="Norway">Norway</option> 
<option value="Oman">Oman</option> 
<option value="Pakistan">Pakistan</option> 
<option value="Palau">Palau</option> 
<option value="Palestinian Territory, Occupied">Palestinian Territory, Occupied</option> 
<option value="Panama">Panama</option> 
<option value="Papua New Guinea">Papua New Guinea</option> 
<option value="Paraguay">Paraguay</option> 
<option value="Peru">Peru</option> 
<option value="Philippines">Philippines</option> 
<option value="Pitcairn">Pitcairn</option> 
<option value="Poland">Poland</option> 
<option value="Portugal">Portugal</option> 
<option value="Puerto Rico">Puerto Rico</option> 
<option value="Qatar">Qatar</option> 
<option value="Reunion">Reunion</option> 
<option value="Romania">Romania</option> 
<option value="Russian Federation">Russian Federation</option> 
<option value="Rwanda">Rwanda</option> 
<option value="Saint Helena">Saint Helena</option> 
<option value="Saint Kitts and Nevis">Saint Kitts and Nevis</option> 
<option value="Saint Lucia">Saint Lucia</option> 
<option value="Saint Pierre and Miquelon">Saint Pierre and Miquelon</option> 
<option value="Saint Vincent and The Grenadines">Saint Vincent and The Grenadines</option> 
<option value="Samoa">Samoa</option> 
<option value="San Marino">San Marino</option> 
<option value="Sao Tome and Principe">Sao Tome and Principe</option> 
<option value="Saudi Arabia">Saudi Arabia</option> 
<option value="Senegal">Senegal</option> 
<option value="Serbia and Montenegro">Serbia and Montenegro</option> 
<option value="Seychelles">Seychelles</option> 
<option value="Sierra Leone">Sierra Leone</option> 
<option value="Singapore">Singapore</option> 
<option value="Slovakia">Slovakia</option> 
<option value="Slovenia">Slovenia</option> 
<option value="Solomon Islands">Solomon Islands</option> 
<option value="Somalia">Somalia</option> 
<option value="South Africa">South Africa</option> 
<option value="South Georgia and The South Sandwich Islands">South Georgia and The South Sandwich Islands</option> 
<option value="Spain">Spain</option> 
<option value="Sri Lanka">Sri Lanka</option> 
<option value="Sudan">Sudan</option> 
<option value="Suriname">Suriname</option> 
<option value="Svalbard and Jan Mayen">Svalbard and Jan Mayen</option> 
<option value="Swaziland">Swaziland</option> 
<option value="Sweden">Sweden</option> 
<option value="Switzerland">Switzerland</option> 
<option value="Syrian Arab Republic">Syrian Arab Republic</option> 
<option value="Taiwan, Province of China">Taiwan, Province of China</option> 
<option value="Tajikistan">Tajikistan</option> 
<option value="Tanzania, United Republic of">Tanzania, United Republic of</option> 
<option value="Thailand">Thailand</option> 
<option value="Timor-leste">Timor-leste</option> 
<option value="Togo">Togo</option> 
<option value="Tokelau">Tokelau</option> 
<option value="Tonga">Tonga</option> 
<option value="Trinidad and Tobago">Trinidad and Tobago</option> 
<option value="Tunisia">Tunisia</option> 
<option value="Turkey">Turkey</option> 
<option value="Turkmenistan">Turkmenistan</option> 
<option value="Turks and Caicos Islands">Turks and Caicos Islands</option> 
<option value="Tuvalu">Tuvalu</option> 
<option value="Uganda">Uganda</option> 
<option value="Ukraine">Ukraine</option> 
<option value="United Arab Emirates">United Arab Emirates</option> 
<option value="United Kingdom">United Kingdom</option> 
<option value="United States">United States</option> 
<option value="United States Minor Outlying Islands">United States Minor Outlying Islands</option> 
<option value="Uruguay">Uruguay</option> 
<option value="Uzbekistan">Uzbekistan</option> 
<option value="Vanuatu">Vanuatu</option> 
<option value="Venezuela">Venezuela</option> 
<option value="Viet Nam">Viet Nam</option> 
<option value="Virgin Islands, British">Virgin Islands, British</option> 
<option value="Virgin Islands, U.S.">Virgin Islands, U.S.</option> 
<option value="Wallis and Futuna">Wallis and Futuna</option> 
<option value="Western Sahara">Western Sahara</option> 
<option value="Yemen">Yemen</option> 
<option value="Zambia">Zambia</option> 
<option value="Zimbabwe">Zimbabwe</option>
';

?>
