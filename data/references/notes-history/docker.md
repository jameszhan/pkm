```bash
# Install
wget https://download.docker.com/mac/stable/Docker.dmg

brew cask install docker

# Uninstall
/Applications/Docker.app/Contents/MacOS/Docker --uninstall
```

```bash
docker --version
# Docker version 18.03.1-ce, build 9ee9f40

docker-compose --version
# docker-compose version 1.21.1, build 5a3f1a3

docker-machine --version
# docker-machine version 0.14.0, build 89b8332
```
#### 测试是否安装成功

```bash
docker run hello-world
```

```bash
docker run -it ubuntu bash
```


#### 修改内容

```bash
docker run -d -p 8088:80 --name webserver nginx
docker exec -it webserver bash
    
    echo '<h1>Hello Genesis!</h1>' > /usr/share/nginx/html/index.html
    
docker diff webserver

docker commit --author "James Zhan <zhiqiangzhan@gmail.com>" --message "webserver test" webserver jameszhan/temp:v0
```

```bash
docker run --name web2 -d -p 8089:80 jameszhan/temp:v0
curl http://localhost:8089
```



#### BusyBox

[BusyBox][easybox] 是一个集成了一百多个最常用 Linux 命令和工具（如 cat、echo、grep、mount、telnet 等）的精简工具箱，它只需要几 MB 的大小，很方便进行各种快速验证，被誉为“Linux 系统的瑞士军刀”。

busybox 镜像虽然小巧，但包括了大量常见的 Linux 命令，读者可以用它快速熟悉 Linux 命令。

```bash
docker run -it -v /james/var:/work:ro busybox

docker run busybox cat /proc/cpuinfo | grep model

docker run busybox cat /proc/version
```

#### Apline

```bash
docker run -v /james/var:/work:ro alpine echo 'Hello World!'

docker run alpine cat /etc/issue
```

#### 快速清除

```bash
docker system prune

docker system prune -a
```

#### 万能 root 

```bash
sudo sh -c su root
```


[apline](http://alpinelinux.org/)
[easybox]: https://www.busybox.net/



### 快速使用Postgres

```bash
docker run -v /james/var/docker/postgres:/var/lib/postgresql/data -p 5432:5432 postgres:10-alpine

psql -h localhost -p 5432 -U postgres
```

### 快速实用Nginx

```bash
docker run --name static-files -v /james/var/webdav:/usr/share/nginx/html -p 80:80 -d nginx:1.15-alpine

curl -i http://localhost/jslinux/

docker run -it nginx:1.15-alpine sh
```

