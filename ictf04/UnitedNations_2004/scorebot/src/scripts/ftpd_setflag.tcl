#!/usr/bin/expect --

proc random {args} {
    global _ran
    global _mod
     
    if {[llength ${args}] > 1} {
        set _mod [lindex ${args} 0]
        set _ran [lindex ${args} 1]
    } else {
        set period 233280
        if {[info exists _ran]} {
            set _ran [expr {(${_ran}*9301+49297)%${period}}]
        } else {
            set _ran [expr {[clock seconds] % ${period}}]
        }
	if {![info exists _mod]} {
            set _mod 10
        }
        return [expr {int(${args}*(${_ran}/double(${period})))%${_mod}}]
    }
}


puts "$argc $argv";
if ([ expr $argc < 2]) {
    puts "Need at least IP and flag";
    exit;
}

# sets random num generator
set seed [clock seconds]
random 100000 $seed

set behavior "setonly";

set ipaddr [lindex ${argv} 0]

set flag [lindex ${argv} 1]

if ([expr $argc >= 3]) {
    set cookie [lindex ${argv} 2];
    set behavior "getset";
} else {
    set cookie "";
}

puts [random [clock seconds]]
puts [random [clock seconds]]
set one [clock clicks -milliseconds]
set two [random [clock seconds]]
set new_cookie "$one.$two" 

puts "Using IP $ipaddr flag $flag cookie $cookie newfile $new_cookie";
 
set timeout 5


spawn ftp ${ipaddr}
 
expect "Name*:" {} timeout {exit 1}

send "ftp\r"

expect "assword:" {} timeout {exit 1}

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

# Prepares the flag file
set fd [open $new_cookie "w+"]
puts $fd $flag
close $fd

send "put ${new_cookie}\r"

expect "226*complete\r\n" {} timeout {exit 1}

file delete ${new_cookie}

if {![string compare $behavior "getset"]} {
    puts "FLAG:$gotit"
} else {
    puts "FLAG:"
}
puts "COOKIE:${new_cookie}"

send "quit\r"

exit 0
