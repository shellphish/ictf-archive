cp -r nunjucks/ bootstrap/ $DESTDIR/usr/ctf/$SERVICE_USER
install blogger.js dynamicload.js metadata.js loadposts.js blog_template.html curiosity_cat.png run.sh $DESTDIR/usr/ctf/$SERVICE_USER
mkdir $DESTDIR/var/ctf/$SERVICE_USER/flags
mkdir $DESTDIR/var/ctf/$SERVICE_USER/posts
