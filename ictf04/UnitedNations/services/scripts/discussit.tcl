#!/usr/bin/expect --

puts "$argc $argv";
if ([ expr $argc < 2]) {
    puts "Need at least IP and flag";
    exit;
}

set behavior "setonly";

set ipaddr [lindex ${argv} 0]

set flag [lindex ${argv} 1]

if ([expr $argc >= 3]) {
    set cookie [lindex ${argv} 2];
    set behavior "getset";
} else {
    set cookie "";
}

puts "Using IP $ipaddr flag $flag cookie $cookie newfile $new_cookie";
 
set timeout 5

# Prepares the flag file
spawn nc ${ipaddr} 7413 
 
send "$operator $flag\n"

if ([string compare $behavior "getset"]) {
    expect -re "Last time we were talking about (.+)\n" {} timeout {exit 1}
} else {
    expect "Last time we were talking about" {} timeout {exit 1}
}

send "exit\n";


send "nobody@nowhere\r"

expect "230*\r\n" {} timeout {exit 1}

send "passive\r"

expect "Passive*off.\r\n" {} timeout {exit 1}

send "cd incoming\r"

expect "200*changed\r\n" {} timeout {exit 1}

if {![string compare $behavior "getset"]} {

    send "get ${cookie}\r"
    expect "226*complete\r\n" {} timeout {exit 1}
    set fd [open ${cookie} "r"]
    set gotit [read -nonewline $fd]
    close $fd
    file delete ${cookie}
}
send "put ${new_cookie}\r"

expect "226*complete\r\n" {} timeout {exit 1}

file delete ${new_cookie}

if {![string compare $behavior "getset"]} {
    puts "FLAG: $gotit"
} else {
    puts "FLAG:"
}
puts "COOKIE: ${new_cookie}"

send "quit\r"

exit 0
