## Aero

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, Priv Esc, Windows

#### Enumeration
- run nmap 
- only get one open port on port 80 running `http`
- visiting the application we see that its allows a file to be uploaded as a theme
![[file upload.png]]
- click on `Browse` and click on supported types, we see that the application allows `.theme` or `.themepack` to be uploaded 

#### Initial Foothold
- searched online and found a POC that can be run on Linux (https://github.com/Jnnshschl/CVE-2023-38146)
- the POC takes in two parameters the attacker's IP and port number then creates a reverse within the theme file
![[themebleed server.png]]
- Note: if reverse shell no received on the first upload, might have to try couple more times 
![[Medium/Windows/Aero/reverse shell.png]]
 
#### Lateral Movement (If any)

#### Privilege Escalation
- going through the home directory of user `sam.emerson` we find an interesting `pdf` named as `CVE-2023-2825_Summary`
![[interesting file at documents.png]]
- after searching up the CVE we find a POC (https://github.com/fortra/CVE-2023-28252)
- however this POC requires us to modify the payload and rebuild the executable file
- download the `github repo`
- i have created a Windows VM to perform this task
	- first, we need to get `Visual Studio` on the VM 
	- second, install workloads and components 
	![[required components.png]]
- then open `project` and select the `.sln` file from the `github repo`
![[open project.png]]
![[sln file.png]]
- modify the payload, use `Powershell base64`
![[payload.png]]
 - build the project and load the executable to the attacking host
![[executable.png]]
- start a `nc` listener and execute the executable
![[executing the executable.png]]
![[root access.png]]
#### Resources

#### Lesson Learned
