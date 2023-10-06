## Git 配置

### 配置 Git LFS

```bash
git lfs install

git lfs track "*.zip"
git lfs track "*.tar.gz"
git lfs track "*.mat"

git lfs track "data/passwords/password-parts/passwords_*"

git lfs track

git lfs ls-files
```

### 删除 GIT 库中大文件

```bash
git ls-files -z | xargs -0 stat -f '%z %N' | sort -n -r
git filter-branch --index-filter 'git rm -r --cached --ignore-unmatch data/passwords/password-parts/' -- --all
git filter-branch --index-filter 'git rm -r --cached --ignore-unmatch data/passwords/passwords.tar.gz' HEAD
```

**回收空间**

```bash
rm -rf .git/refs/original/ 
git reflog expire --expire=now --all
git gc --prune=now
git gc --aggressive --prune=now
```

## 合并两个分支的历史记录

```bash
git remote add notes-history2 ../notes-history2
git fetch notes-history2
git merge --allow-unrelated-histories notes-history2/master

git remote remove notes-history2
```

**fatal: mll/data/train.csv：smudge 过滤器 lfs 失败 **

```bash
// Skip smudge - We'll download binary files later in a faster batch
git lfs install --skip-smudge

git fetch

// Fetch all the binary files in the new clone
git lfs pull

// Reinstate smudge
git lfs install --force
```