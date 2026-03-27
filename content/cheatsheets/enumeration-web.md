---
title: "Web Enumeration Cheatsheet"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Web Enumeration Cheatsheet"
summary: "Enumeration | Web Enumeration Cheatsheet"
tags:
  - "Enumeration"
  - "Recon"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "Enumeration"
ShowToc: true
TocOpen: false

cover:
  image: /images/covers/cheatsheet.svg
  alt: "cheatsheet"
  relative: false
---

## Directory Bruteforce
```bash
# Gobuster
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt
gobuster dir -u http://<IP> -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt

# Feroxbuster (récursif)
feroxbuster -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt

# FFuf
ffuf -u http://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt
```

## Subdomain / VHost
```bash
# Subdomain bruteforce
ffuf -u http://FUZZ.<domain> -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
gobuster vhost -u http://<domain> -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Avec filtrage
ffuf -u http://FUZZ.<domain> -w wordlist.txt -fs <taille_à_filtrer>
```

## Technologies
```bash
whatweb http://<IP>
nikto -h http://<IP>
curl -I http://<IP>    # Headers
```

## CMS
```bash
# WordPress
wpscan --url http://<IP> --enumerate u,p,t
wpscan --url http://<IP> --passwords rockyou.txt --usernames admin

# Joomla
joomscan -u http://<IP>

# Drupal
droopescan scan drupal -u http://<IP>
```
