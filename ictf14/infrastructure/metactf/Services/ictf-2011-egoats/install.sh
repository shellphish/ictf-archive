cp -r script/ config/ db/ app/ $DESTDIR/usr/ctf/$SERVICE_USER
install config.ru Gemfile Gemfile.lock Rakefile $DESTDIR/usr/ctf/$SERVICE_USER/
