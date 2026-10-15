# Determines the IP address

myip=`ifconfig eth0 | grep "inet addr:" | awk '{print $2}' | sed 's/addr://'`

# Message
echo "Setting up firewall rules for IP address" $myip

# Sets the default input policy to REJECT 
ipchains -P input REJECT
ipchains -F input
 
# Opens loopback interface
ipchains -A input -i lo -j ACCEPT

# Allows DNS traffic
ipchains -A input -j ACCEPT -p udp -s 128.111.41.10 53 -d $myip
ipchains -A input -j ACCEPT -p udp -s 128.111.1.1 53 -d $myip
ipchains -A input -j ACCEPT -p udp -s 128.111.1.2 53 -d $myip

# Opens ssh to the world
ipchains -A input -j ACCEPT -p tcp -s 0.0.0.0/0 -d $myip 22

# Opens everything to  128.111.54
ipchains -A input -j ACCEPT -p all -s 128.111.54.0/24 -d $myip 

# Opens everything to  128.111.49
ipchains -A input -j ACCEPT -p all -s 128.111.49.0/24 -d $myip 

# Opens everything to  128.111.43
ipchains -A input -j ACCEPT -p all -s 128.111.43.0/24 -d $myip 

# Opens everything to  128.111.51
ipchains -A input -j ACCEPT -p all -s 128.111.51.0/24 -d $myip 

# Opens everything to  128.111.48
ipchains -A input -j ACCEPT -p all -s 128.111.48.0/24 -d $myip 

# Allows TCP non-setup traffic
ipchains -A input -j ACCEPT -p tcp ! --syn -s 0.0.0.0/0 -d $myip

