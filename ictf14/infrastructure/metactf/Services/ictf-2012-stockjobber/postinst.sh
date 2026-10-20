touch /var/ctf/$SERVICE_USER/USERS.DAT /var/ctf/$SERVICE_USER/USERDATA.DAT
chown $SERVICE_USER.$SERVICE_USER /var/ctf/$SERVICE_USER/USERS.DAT /var/ctf/$SERVICE_USER/USERDATA.DAT

ln -sf /var/ctf/$SERVICE_USER /usr/ctf/$SERVICE_USER/data

service xinetd restart
