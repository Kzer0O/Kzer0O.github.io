---
title: "Nmap - Complete Scanning Cheatsheet"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Nmap - Complete Scanning Cheatsheet"
summary: "Enumeration | Nmap - Complete Scanning Cheatsheet"
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

## Scans de base
```bash
# Scan rapide tous ports
nmap -p- --min-rate 5000 -sS <IP>

# Scan détaillé sur ports trouvés
nmap -sCV -p <ports> <IP>

# Scan UDP (top 100)
nmap -sU --top-ports 100 <IP>

# Scan complet + scripts vuln
nmap -sCV -p- --script vuln <IP>
```

## Scans spécifiques
```bash
# Scan furtif
nmap -sS -T2 -f <IP>

# Scan avec OS detection
nmap -O -sV <IP>

# Scan réseau entier
nmap -sn 10.10.10.0/24

# Scripts spécifiques
nmap --script=smb-enum-shares,smb-enum-users -p 445 <IP>
nmap --script=http-enum -p 80 <IP>
```

## Output
```bash
nmap -oA scan_results <IP>    # Tous formats
nmap -oN scan.txt <IP>        # Format normal
nmap -oG scan.gnmap <IP>      # Format greppable
```
