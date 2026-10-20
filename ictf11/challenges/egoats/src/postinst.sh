rails || gem install rails -v 3.1.1
cd /usr/ctf/egoats/
bundle install
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "DROP DATABASE IF EXISTS egoats_development;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE egoats_development;"
mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "GRANT ALL PRIVILEGES ON egoats_development.* TO 'egoats'@'localhost'";
bundle exec rake db:migrate
