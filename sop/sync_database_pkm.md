





## 迁移数据库

```bash
$ mysqldump -h 192.168.1.6 -P 3306 -u awesome -p pkm > pkm.sql

$ scp jump.zizhizhan.com:/tmp/pkm.sql /opt/var/downloads/

$ mysql -u pkm -p pkm < /opt/var/downloads/pkm.sql
```

## 备份数据库

```bash
$ mysqldump -h 192.168.1.110 -P 3306 --lock-all-tables --set-gtid-purged=OFF -u pkm -p pkm > pkm-20231109.sql
```