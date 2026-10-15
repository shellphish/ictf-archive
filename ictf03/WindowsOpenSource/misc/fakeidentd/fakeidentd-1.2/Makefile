# The username that identd should answer on request
# This does not have to be an existing user.
USER="username"
 
# full path to copy utility.
CP=/bin/cp

# full path to link utility.
LN=/bin/ln

# full path to remove utility.
RM=/bin/rm

# Directory where your init scripts are.
# Is /etc/init.d in most distributions.
# Use /sbin/init.d if you run SuSE Linux.
# Use /etc/rc.d/init.d if you run RedHat Linux.
INITD=/etc/init.d

# Directory where the rc subdirectorys are (rc0.d, rc1.d, ...)
# Is /etc in most distributions.
# Use /sbin/init.d if you run SuSE Linux. 
# Use /etc/rc.d if you run RedHat Linux.
RCD=/etc

# C Compiler. gcc should work.
CC=gcc

## End of configuration

all:	build

build:
	${CC} -g -o identd identd.c 
	@echo ${USER} > identuser
	@echo
	@echo "Build complete. Now type 'make install' to install identd"
	@echo "as a standalone daemon."
	@echo "Type 'make install-inetd' to make identd run via inetd."
 
	
clean:
	${RM} identd
	${RM} identuser

install: all 
	${CP} identd /sbin
	${CP} fakeidentd ${INITD}
	${LN} -s ${INITD}/fakeidentd ${RCD}/rc2.d/S45fakeidentd
	${LN} -s ${INITD}/fakeidentd ${RCD}/rc0.d/K45fakeidentd
	${LN} -s ${INITD}/fakeidentd ${RCD}/rc6.d/K45fakeidentd
	${CP} identuser /etc/ 
	@# If you change this directory change the init script, too!
	@echo
	@echo "Install complete!"
	@echo Type \"${INITD}/fakeidentd start\" to start identd now.

uninstall:
	${RM} /sbin/identd
	${RM} ${INITD}/fakeidentd
	${RM} ${RCD}/rc2.d/S45fakeidentd
	${RM} ${RCD}/rc0.d/K45fakeidentd
	${RM} ${RCD}/rc6.d/K45fakeidentd
 
install-inetd: all
	${CP} identd /sbin
	@echo ident stream tcp wait nobody /sbin/identd ${USER} >> /etc/inetd.conf
	@echo
	@echo "Install complete!"
	@echo "You should now restart inetd to finish installation."
