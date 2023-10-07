## 更换Foreign Key

要将 `ManagedFile` 与 `UniqueFile` 通过 `digest` 字段进行关联，而不是通过 `id`，我们需要进行以下几个步骤：

1. **备份数据库**：这是一个重要的操作。在进行任何可能改变数据的操作之前，始终进行备份。
  
2. **添加新的关联字段**：在 `ManagedFile` 模型中为 `digest` 添加一个外键字段。例如，我们可以命名为 `unique_file_digest`。

3. **迁移数据**：将 `unique_file_id` 的数据迁移到新的 `unique_file_digest` 字段。

4. **删除旧的关联字段**：删除 `unique_file` 字段。

5. **重命名新的关联字段**：将 `unique_file_digest` 重命名为 `unique_file`。

6. **更新数据库**：使用 Django 的迁移工具更新数据库。

## 具体操作如下：

### **备份数据库**

```bash
$ mysqldump -h 127.0.0.1 -P 3306 -u pkm -p pkm > 20231007-pkm.sql
```

### 更新模型：

```python
class ManagedFile(models.Model):
    original_path = models.CharField(max_length=255, unique=True)
    file_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_file = models.ForeignKey(UniqueFile, on_delete=models.CASCADE)
    unique_file_digest = models.CharField(max_length=64, null=True)
```

### 运行迁移：

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

### 更新数据：

```bash
$ python manage.py shell
```

```python
from knowledge_map.models import ManagedFile

for managed_file in ManagedFile.objects.prefetch_related('unique_file').all():
    managed_file.unique_file_digest = managed_file.unique_file.digest
    managed_file.save(update_fields=['unique_file_digest'])
```

```sql
UPDATE km_managed_file
SET unique_file_digest = (SELECT digest FROM km_unique_file WHERE km_unique_file.id = km_managed_file.unique_file_id)
WHERE unique_file_digest IS NULL;
```

### 再次更新模型：

```python
class ManagedFile(models.Model):
    original_path = models.CharField(max_length=255, unique=True)
    file_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_file = models.ForeignKey(UniqueFile, to_field='digest', on_delete=models.CASCADE, related_name='managed_files', db_column='unique_file_digest')
```

### 编写迁移文件：

```bash
$ python manage.py makemigrations knowledge_map --empty
```

#### 更新Migration字段

```python
...
operations = [
    # Step 1: Convert unique_file_digest into a ForeignKey
    migrations.AlterField(
        model_name='managedfile',
        name='unique_file_digest',
        field=models.ForeignKey(
            to='knowledge_map.UniqueFile',
            to_field='digest',
            on_delete=models.CASCADE,
            related_name='managed_files',
            db_column='unique_file_digest'
        ),
    ),
    # Step 2: Remove the old ForeignKey (optional, can be done in a separate migration)
    migrations.RemoveField(
        model_name='managedfile',
        name='unique_file',
    ),
]
```

#### 运行迁移：

```bash
$ python manage.py migrate

$ python manage.py makemigrations                                                                                                                 1:02:59 
Was managedfile.unique_file_digest renamed to managedfile.unique_file (a ForeignKey)? [y/N]y
$ python manage.py migrate
```

### 完成！

这样，您就将关联从 `id` 更改为 `digest`，而不会丢失任何数据。

## 附录

### 回滚操作

#### **回滚迁移**：

使用以下命令回滚到 `0004`：

```bash
$ python manage.py showmigrations

$ python manage.py migrate knowledge_map 0004
```

这将撤消所有超过 `0004` 的迁移。

> 如果报错，可以尝试注释掉后续migrations中的所有operations

#### **删除迁移文件**：

删除从 `0005` 开始的所有迁移文件。例如：

```bash
$ rm knowledge_map/migrations/0005_*.py
$ rm knowledge_map/migrations/0006_*.py
$ rm knowledge_map/migrations/0007_*.py
```

根据您的实际迁移文件数量和名称，这可能需要调整。

#### **重新生成迁移（如果需要）**：

如果您对模型进行了更改并希望生成新的迁移，可以执行：

```bash
$ python manage.py makemigrations
```

#### **应用新的迁移（如果有）**：

如果您生成了新的迁移，可以应用它：

```bash
$ python manage.py migrate
```

同样，**请确保在进行上述操作之前备份数据库**，以防止意外丢失数据。