```bash
cp -al old_dir new_dir

# 很多文件系统不支持硬链接目录
ln old_dir new_dir
```
`cp -al` 只有目录是不同 `inode`，而文件才是同一个 `inode`。


```bash
mount -o bind old_dir new_dir
mount --bind old_dir new_dir
```


`mount` 本身是用来挂载目录与硬盘，比方说 `/root` 这是一个挂载名称，它挂载到一个硬盘的分区 `/dev/sha1`，我们就可以在 `/root` 里进行读写操作。

`mount` 有一个 `bind` 选项，`man` 里面的解释。

```txt
The bind mounts.
      Since Linux 2.4.0 it is possible to remount part of the file hierarchy somewhere else.  The call is:

             mount --bind olddir newdir

      or by using this fstab entry:

             /olddir /newdir none bind

      After  this  call the same contents are accessible in two places.  One can also remount a single file (on a single file).  It's also possible to use the bind mount to create a
      mountpoint from a regular directory, for example:

             mount --bind foo foo

      The bind mount call attaches only (part of) a single filesystem, not possible submounts.  The entire file hierarchy including submounts is attached a second place by using:

             mount --rbind olddir newdir

      Note that the filesystem mount options will remain the same as those on the original mount point.

      mount(8) since v2.27 allow to change the options by passing the -o option along with --bind for example:

             mount --bind,ro foo foo

      This feature is not supported by Linux kernel and it is implemented in userspace by additional remount mount(2) syscall. This solution is not atomic.

      The alternative (classic) way to create a read-only bind mount is to use remount operation, for example:

             mount --bind olddir newdir
             mount -o remount,ro,bind olddir newdir

      Note that read-only bind will create a read-only mountpoint (VFS entry), but the original filesystem superblock will still  be  writable,  meaning  that  the  olddir  will  be
      writable, but the newdir will be read-only.

      It's impossible to change mount options recursively (for example b  -o rbind,ro).
```
