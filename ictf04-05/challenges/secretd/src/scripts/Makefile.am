# Makefile.am

CLEANFILES = secretdmgr secretdmgr.tmp secretd secretd.tmp
EXTRA_DIST = secretdmgr.in secretd.in getflag.py poundsvc

#bin_SCRIPTS = secretdmgr

# Substitution
edit = sed 's,@bindir\@,$(bindir),'

install-exec-am:
	rm -f secretdmgr secretdmgr.tmp
	$(edit) <$(srcdir)/secretdmgr.in >secretdmgr.tmp
	chmod +x secretdmgr.tmp
	mv secretdmgr.tmp secretdmgr
	$(INSTALL) secretdmgr $(bindir)
	rm -f secretd secretd.tmp
	$(edit) <$(srcdir)/secretd.in >secretd.tmp
	chmod +x secretd.tmp
	mv secretd.tmp secretd

