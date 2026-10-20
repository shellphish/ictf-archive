chown -R $SERVICE_USER.$SERVICE_USER /opt/prison/
chmod 4755 /opt/prison/bin/toilet
chmod 711 /opt/prison/jailcell/toilet/tunnel
chmod 700 /opt/prison/warden

# restart xinetd
service xinetd restart
