# 部署静态文件服务器

## **运行Nginx容器**：

你可以使用官方的Nginx镜像来运行一个容器。

```bash
$ docker run --name fs-server -v /path/to/your/files:/usr/share/nginx/html:ro -d -p 8080:80 --network nginx-net nginx
```

此命令将把你的文件从`/path/to/your/files`目录挂载到容器的`/usr/share/nginx/html`目录，并将容器的80端口映射到宿主机的8080端口。

## **为Nginx添加基本身份验证**：

首先，你需要为Nginx创建一个`.htpasswd`文件。这可以使用Apache的`htpasswd`工具完成，或者你可以使用在线的.htpasswd生成器。

如果你已经安装了`htpasswd`，可以执行以下命令：

`sudo apt install apache2-utils`

```bash
$ htpasswd -c ./.htpasswd username
```

它会提示你为指定的用户名输入密码。

接下来，你需要更新Nginx的配置来要求身份验证。创建一个新的Nginx配置文件`nginx.conf`：

```nginx
server {
    listen       80;
    server_name  localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
        auth_basic "Restricted Content";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }

    # ... 其他配置 ...
}
```

将此配置和`.htpasswd`文件都挂载到容器中：

```bash
$ docker run --name my-nginx \
    -v /path/to/your/files:/usr/share/nginx/html:ro \
    -v /path/to/your/nginx.conf:/etc/nginx/conf.d/default.conf \
    -v /path/to/your/.htpasswd:/etc/nginx/.htpasswd \
    -d -p 8080:80 nginx
```

现在，当你尝试访问服务器上的文件时，Nginx应该会提示你输入用户名和密码。

> 注意：这里提供的身份验证方法是基于HTTP基本身份验证的，它不是最安全的方法，因为密码是以明文形式发送的。如果你打算在生产环境中使用这种方法，建议使用SSL/TLS来加密传输。
