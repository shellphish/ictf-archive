#! /bin/sh
#: Set up search servlet

# Get settings
cd /root/setup/servlet || exit 1
. servlet.properties || exit 1

# Get flags, passwords
if [ -z "$1" -o -z "$2" -o -z "$3" -o -z "$4" ]; then
  echo "usage: setup <initial flag> <servlet password> <database password>"
  exit 1
fi

IPADDR=$1
SERVLET_FLAG=$2
SERVLET_PASSWORD=$3
SERVLET_DBPASSWORD=$4

echo ">>> Setting initial flag to $SERVLET_FLAG"
echo ">>> Setting servlet password to $SERVLET_PASSWORD"
echo ">>> Setting database password to $SERVLET_DBPASSWORD"

# Transform servlet password
SERVLET_PASSWORD=`./transform $SERVLET_PASSWORD`

# Unpack webapp
echo ">>> Unpacking webapp into $WEBAPPDIR"
rm -rf $WEBAPPDIR
(cd $WEBAPPINSTDIR && tar zxf $WEBAPPPKG) || exit 1

# Patch and copy init script
echo ">>> Patching init script"
sed "s,@@SERVLET_DBPASSWORD@@,$SERVLET_DBPASSWORD,g" <init_servlet.in |
  sed "s,@@WEBAPPDIR@@,$WEBAPPDIR,g" |
  sed "s,@@SCRIPTSDIR@@,$SCRIPTSDIR,g" >init_servlet
chmod +x init_servlet || exit 1

echo ">>> Copying init script to scripts directory"
cp init_servlet $SCRIPTSDIR || exit 1
cp servlet.properties $SCRIPTSDIR || exit 1

# Link init script
echo ">>> Linking init script"
ln -sf $SCRIPTSDIR/init_servlet /etc/init.d/servlet || exit 1
ln -sf /etc/init.d/servlet /etc/rc3.d/S92servlet || exit 1

# Patch source
for src in $WEBAPPTMPLDIR/*.java; do
  file=`basename $src`

  echo ">>> Patching $file..."

  sed "s,@@SERVLET_PASSWORD@@,$SERVLET_PASSWORD,g" <$src |
    sed "s,@@SERVLET_DBPASSWORD@@,$SERVLET_DBPASSWORD,g" >$WEBAPPSRCDIR/ctf/$file
done

# Build source
echo ">>> Building webapp"
(cd $WEBAPPDIR && $ANT dist) || exit 1

# Copy distribution to HTML directory
echo ">>> Copying $WEBAPPWAR to $WEBAPPHTDIR"
chattr -i $WEBAPPHTDIR/*.war
rm -rf $WEBAPPHTDIR
mkdir -p $WEBAPPHTDIR || exit 1
chmod 755 $WEBAPPHTDIR || exit 1
cp $WEBAPPWAR $WEBAPPHTDIR || exit 1
chmod 644 $WEBAPPHTDIR/*.war || exit 1
chattr +i $WEBAPPHTDIR/*.war || exit 1

# Remove source
echo ">>> Removing source directories"
rm -rf $WEBAPPSRCDIR/ctf

# Copy database sql to web app dir
echo ">>> Copying servlet SQL to $WEBAPPDIR"
cat <<EOF >$SERVLET_DBSQL
drop table kb;
drop sequence kb_id_seq;
create sequence kb_id_seq;
create table kb(
  id integer primary key default nextval('kb_id_seq'),
  title text not null,
  info text not null
);
grant all on table kb to kb;
grant all on kb_id_seq to kb;

insert into kb(title, info)
  values('"Suspicious" registry key: NSA-$SERVLET_FLAG', '
The registry key NSA-$SERVLET_FLAG references vital data
for the proper functioning of Windows, and should not under
any circumstances be deleted.  If you know what''s good for you.
');

insert into kb(title, info)
  values('New Linux-based Windows servers too stable', '
Some users have reported that our new product line which
incorporates a Linux-based kernel is too stable, resulting
in decreased TCO and the firing of useless MCSE-certified
sysadmins. Suggested solutions to this issue includes
loading any Microsoft applications, installing Kazaa, Gator,
or related spyware, utilizing uncooled Athlon processors
under heavy CPU load, or similar methods to reduce system
stability.
');

insert into kb(title, info)
  values('Value of MCSE certification negatively impacted', '
Some MCSE-certified system administrators have complained
that their "hard-earned" MCSE certifications are now
worthless, as they have been taught how to click buttons
instead of the actual concepts behind managing networks of
servers. Suggested solutions include switching to another
industry or learning how to think on your own. Otherwise,
an affected administrator Must Consult Someone Experienced.
');

EOF

# Restart
/etc/init.d/servlet || exit 1

