#### 准备环境变量

```bash
$ kubectl delete cm pkm-env -n geek-apps
$ kubectl create configmap pkm-env -n geek-apps --from-file=.env
$ kubectl get configmap pkm-env -n geek-apps -o yaml
```

#### 构建镜像

```bash
$ docker buildx build --platform linux/amd64 -t jameszhan/pkm:0.0.8 . --push
$ kubectl apply -f deploy/k8s.yml
```

#### 配置服务和Ingress

```bash
$ cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: pkm
  namespace: geek-apps
  labels:
    app.kubernetes.io/name: pkm
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app.kubernetes.io/name: pkm
    app.kubernetes.io/instance: pkm
EOF

$ cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pkm
  namespace: geek-apps
spec:
  ingressClassName: nginx
  tls:
  - hosts:
      - pkm.zizhizhan.com
    secretName: star.zizhizhan.com-tls
  rules:
  - host: pkm.zizhizhan.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: pkm
            port:
              number: 80
EOF
```