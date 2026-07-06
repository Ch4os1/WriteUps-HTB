## Lab Details
- Difficulty: Easy
- OS: Windows

## Summary
- Initial access: Kiosk Escape 
- Privilege escalation: Password Extraction, UAC Bypass

## Enumeration
#### Steps
- run `nmap`
```
$ nmap -A -v 10.129.234.51
<SNIP>
PORT STATE SERVICE VERSION
3389/tcp open ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2025-07-11T13:21:45+00:00; +15m58s from scanner time.
| ssl-cert: Subject: commonName=Escape
| Issuer: commonName=Escape
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-04-10T06:20:36
| Not valid after: 2025-10-10T06:20:36
| MD5: 537c:865a:3efe:6f4d:de82:fe44:139f:c112
|_SHA-1: f441:df53:0b96:0581:64d6:2350:591d:3ec5:7d46:2c4e
| rdp-ntlm-info:
| Target_Name: ESCAPE
| NetBIOS_Domain_Name: ESCAPE
| NetBIOS_Computer_Name: ESCAPE
| DNS_Domain_Name: Escape
| DNS_Computer_Name: Escape
| Product_Version: 10.0.19041
|_ System_Time: 2025-07-11T13:21:40+00:00
</SNIP>
```
- From the nmap scan only port 3389 is open
- Attempt to login via RDP anonymously 
```
$xfreerdp  /v:10.129.12.145 -sec-nla
```
- We get a notification stating login as KioskUser0 without password 
![[Pasted image 20260706123727.png]]
- Click on the only option and login with `KioskUsers` as username and leave password plank
![[Pasted image 20260706125154.png]]
- We are presented as a screen `Busan Expo`
![[Pasted image 20260706125231.png]]

## Foothold

#### Steps

- Hit `Windows` Key will bring up the start menu 
![[Pasted image 20260706125256.png]]
- Search and execute different apps like `cmd.exe`, `powershell.exe` however unable to launch 
- Able to launch edge 
- In the search bar enter `file:///C://` leads to the root of `C:\`
![[Pasted image 20260706144838.png]]
- Visit `powershell` directory and click on `powershell.exe` which downloads `powershell`
![[Pasted image 20260706144854.png]]
- `ctrl + a` to change the name to `msedge`
![[Pasted image 20260706144917.png]]
- Click on `msedge` will open a `powershell` window 
![[Pasted image 20260706144950.png]]
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Enumerate the file system and found `_admin`
```
PS C:\> get-childitem -force


    Directory: C:\


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d--hs-          2/4/2024  12:52 AM                $Recycle.Bin
d--h--         6/24/2025   8:23 AM                $WinREAgent
d--hsl          2/3/2024  11:32 AM                Documents and Settings
d-----          2/3/2024   3:11 AM                inetpub
d-----         12/7/2019   1:14 AM                PerfLogs
d-r---         4/10/2025  11:29 PM                Program Files
d-r---          2/3/2024   3:03 AM                Program Files (x86)
d--h--         6/24/2025   8:06 AM                ProgramData
d--hs-         10/1/2024  11:40 PM                Recovery
d--hs-         6/16/2025   4:42 AM                System Volume Information
d-r---          2/3/2024   3:43 AM                Users
d-----         6/24/2025   1:24 PM                Windows
d--h--          2/3/2024   3:05 AM                _admin
-a-hs-          2/4/2024   1:35 AM           8192 DumpStack.log
-a-hs-          7/5/2026   9:50 PM           8192 DumpStack.log.tmp
-a-hs-         10/1/2024  11:48 PM     2093002752 hiberfil.sys
-a-hs-          7/5/2026   9:50 PM     1476395008 pagefile.sys
-a-hs-          7/5/2026   9:50 PM       16777216 swapfile.sys
```
- Found a profiles.xml file 
```
PS C:\> cd _admin
PS C:\_admin> ls


    Directory: C:\_admin


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          2/3/2024   3:04 AM                installers
d-----          2/3/2024   3:05 AM                passwords
d-----          2/3/2024   3:05 AM                temp
-a----          2/3/2024   3:03 AM              0 Default.rdp
-a----          2/3/2024   3:04 AM            574 profiles.xml


PS C:\_admin> cat .\profiles.xml
<?xml version="1.0" encoding="utf-16"?>
<!-- Remote Desktop Plus -->
<Data>
  <Profile>
    <ProfileName>admin</ProfileName>
    <UserName>127.0.0.1</UserName>
    <Password>JWqkl6IDfQxXXmiHIKIP8ca0G9XxnWQZgvtPgON2vWc=</Password>
    <Secure>False</Secure>
  </Profile>
</Data>
```
- Enumerate installed application and found Remote Desktop Plus 
```
PS C:\Program Files (x86)> ls


    Directory: C:\Program Files (x86)


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         12/7/2019   1:31 AM                Common Files
d-----         6/24/2025   1:19 PM                Internet Explorer
d-----          2/3/2024   3:14 AM                Microsoft
d-----         12/7/2019   1:31 AM                Microsoft.NET
d-----          2/3/2024   3:03 AM                Remote Desktop Plus
d-----         6/24/2025  10:10 AM                Windows Defender
d-----          2/3/2024   3:07 AM                Windows Mail
d-----         6/24/2025  10:10 AM                Windows Media Player
d-----         6/24/2025   1:19 PM                Windows Multimedia Platform
d-----         12/7/2019   1:50 AM                Windows NT
d-----         6/24/2025  10:10 AM                Windows Photo Viewer
d-----         6/24/2025   1:19 PM                Windows Portable Devices
d-----         12/7/2019   1:31 AM                WindowsPowerShell


PS C:\Program Files (x86)> cd '.\Remote Desktop Plus\'
PS C:\Program Files (x86)\Remote Desktop Plus> ls


    Directory: C:\Program Files (x86)\Remote Desktop Plus


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         3/13/2018  10:47 PM         267264 rdp.exe
```
- Execute the program will open Remote Desktop Plus 
```
PS C:\Program Files (x86)\Remote Desktop Plus> ./rdp.exe
```
![[Pasted image 20260706140833.png]]
- Click on `Manage profiles` and `Import profiles `
![[Pasted image 20260706140823.png]]
- We will need to copy it to the download folder `C:\Users\kioskUser0\Downloads`
```
PS C:\_admin> cp .\profiles.xml ~/
PS C:\Users\kioskUser0> ls


    Directory: C:\Users\kioskUser0


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-r---          2/3/2024   3:10 AM                3D Objects
d-r---          2/3/2024   3:10 AM                Contacts
d-r---         6/24/2025   7:31 AM                Desktop
d-r---          7/5/2026  11:07 PM                Documents
d-r---          7/5/2026  11:06 PM                Downloads
d-r---          2/3/2024   3:10 AM                Favorites
d-r---          2/3/2024   3:10 AM                Links
d-r---          2/3/2024   3:10 AM                Music
d-r---          2/3/2024   3:10 AM                Pictures
d-r---          2/3/2024   3:10 AM                Saved Games
d-r---          2/3/2024   3:10 AM                Searches
d-r---          2/3/2024   3:10 AM                Videos
-a----          2/3/2024   3:04 AM            574 profiles.xml

```
- After we have import the `xml` file we can see the password is showing in stars 
![[Pasted image 20260706141205.png]]
- We can install BulletsPassView a program to decode the password in stars, download it here: https://www.nirsoft.net/utils/bullets_password_view.html
![[Pasted image 20260706141723.png]]
- **NOTE**: Ensure that Remote Desktop Plus is in the edit profile window while using `BulletsPassView`
- We get the plaintext password 
```
Twisting3021
```
- Use `runas` to open a new `powershell` window as the admin user 
```
runas /user:admin powershell
```
- Howerver we are unable to access the administrator folder due to UAC restriction 
- Run `start-process` to bypass that 
```
$ start-process powershell.exe -verb runas
```

![[Pasted image 20260706144731.png]]

![[Pasted image 20260706144610.png]]
- After click on the left button of the pop up a new `powershell` window opens with the proper permissions 
![[Pasted image 20260706144635.png]]
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: