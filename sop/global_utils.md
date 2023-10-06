
#### 创建共享模块

```bash
$ python3 manage.py startapp global_utils
$ rm global_utils/admin.py
$ rm global_utils/apps.py
$ rm global_utils/models.py
$ rm global_utils/tests.py
$ rm global_utils/views.py
$ rm -r global_utils/migrations
```

等价于

```bash
$ touch global_utils/__init__.py
```