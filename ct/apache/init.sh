#!/bin/bash

#start apache2
a2ensite website-ssl
a2enmod ssl
a2enmod rewrite
a2enmod proxy
a2enmod proxy_http
a2enmod proxy_connect
/etc/init.d/apache2 start


#initial sync
echo "Initial directory sync"
cp -r /tmp/src/* /var/www/html && \
chown -R www-data:www-data /var/www/html


#sync new changes
while true
do

	inotifywait -e modify,create,delete -r /tmp/src && \
	echo "Directory change detected. Syncing files to serve in apache"
	cp -r /tmp/src/* /var/www/html && \
	chown -R www-data:www-data /var/www/html

done

#keep container away 
while true
do
	tail -f /dev/null
done
