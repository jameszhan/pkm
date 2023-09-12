
```bash
$ conda create -n pkm python=3.9

# To activate this environment, use
$ conda activate pkm
# To deactivate an active environment, use
$ conda deactivate
```

```bash
$ conda install django=4.1.7
$ conda install python-dotenv
$ conda install django-taggit
$ conda install mysqlclient

$ conda uninstall django-countries
$ pip install django-countries
$ conda uninstall django-reversion
$ pip install django-reversion
```

```sql
CREATE DATABASE IF NOT EXISTS `pkm` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
GRANT ALL PRIVILEGES ON pkm.* TO 'awesome'@'192.168.1.%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

```bash
$ django-admin startproject pkm

$ cd pkm
$ python3 manage.py startapp book

$ python3 manage.py makemigrations
$ python3 manage.py migrate

$ python3 manage.py createsuperuser

$ python3 manage.py runserver 0.0.0.0:8000
```


```bash
$ python3 manage.py shell
```

```bash
$ python manage.py test
```

#### 查看SQL

```bash
$ python manage.py showmigrations
```


