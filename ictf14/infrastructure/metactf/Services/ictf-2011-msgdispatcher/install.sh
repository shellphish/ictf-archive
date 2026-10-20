python -m py_compile msgdispatcher.py libs.py
install libs.pyc msgdispatcher.pyc msgdispatcher_main $DESTDIR/usr/ctf/$SERVICE_USER/
mkdir $DESTDIR/var/ctf/msgdispatcher/messages $DESTDIR/var/ctf/msgdispatcher/command
touch $DESTDIR/var/ctf/msgdispatcher/command/__init__.py
