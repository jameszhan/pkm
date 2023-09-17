







```bash
$ mysqldump -h 192.168.1.6 -P 3306 -u awesome -p pkm > pkm.sql

$ scp jump.zizhizhan.com:/tmp/pkm.sql /opt/var/downloads/

$ mysql -u pkm -p pkm < /opt/var/downloads/pkm.sql
```