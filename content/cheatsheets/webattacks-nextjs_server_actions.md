---
title: "Next.js Server Actions Exploitation"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Next.js Server Actions Exploitation"
summary: "WebAttacks | Next.js Server Actions Exploitation"
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
Next.js RSC (React Server Components) utilise des "Server Actions" appelées via POST avec un header `Next-Action` contenant un ID hexadécimal de 40 caractères.

## Identifier les Action IDs
```bash
# Récupérer la page et trouver les chunks JS
curl -sk https://target/auth/login | grep -oP '/_next/static/chunks/app/.+?\.js'

# Extraire les IDs des chunks
curl -sk https://target/_next/static/chunks/app/auth/login/page-XXXXX.js | grep -oP '[a-f0-9]{40}'
```

## Appeler une Server Action
```bash
curl -sk https://target/auth/login \
  -H 'Next-Action: 7abc1d84ff816e8d6965b2132e8011685a8c9917' \
  -H 'Content-Type: text/plain' \
  -d '["username","password"]'
```

## Format de réponse RSC
```
0:["$@1",["eMXTkHuLPViqV0QpNTSCV",null]]
1:{"result":{"token":"eyJ..."}}
```

Ou pour les données hexadécimales:
```
2:T<hex_length>,<hex_encoded_data>1:{"result":{"data":["$2"]}}
```

## Notes
- Les IDs sont stables entre les redémarrages (compilés dans le JS bundle)
- Les arguments sont un JSON array passé dans le body
- Le cookie `token` (JWT) est envoyé automatiquement
- Certaines actions nécessitent un JWT avec `withPasskey: true`

## Ref
- Machine: Sorcery (HTB Insane)
