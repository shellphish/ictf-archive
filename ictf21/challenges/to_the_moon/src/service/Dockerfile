from ubuntu:20.04

run apt-get update
run apt-get install -y xinetd
run useradd -m chall -u 31337

copy xinetd /etc/xinetd.d/to_the_moon
cmd ["/usr/sbin/xinetd", "-dontfork"]
