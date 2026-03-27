---
title: "[Tips] CCTV - HTB Easy"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Tips and hints to solve this machine — no spoilers!"
summary: "Easy |  Linux | SQL Injection | Tips Only"
tags:
  - "HTB"
  - "Linux"
  - "Easy"
  - "SQLi"
  - "HackTheBox"
categories:
  - "HackTheBox"
series:
  - "HackTheBox"
weight: 10
ShowToc: true
TocOpen: false

cover:
  image: "/images/covers/machine-cctv.svg"
  alt: "easy linux writeup"
  relative: false
---
> **OS:** Ubuntu 24.04 | **Difficulté:** Easy | **IP:** 10.10.XX.XX

---

## Approach

This is a **tips-only** guide — no flags, no copy-paste commands.
The full writeup will be published once the machine retires on HackTheBox.

---

## Reconnaissance Tips

Start with a comprehensive port scan. Key services to investigate:

- Port **22** → SSH
- Port **80** → HTTP
- Port **3306** → MySQL

## Enumeration Tips

- Don't forget to check for **virtual hosts** and add entries to `/etc/hosts`
- Look carefully at the **API endpoints**

## Exploitation Tips

Key techniques involved in this machine:

- API enumeration / exploitation
- CVE exploitation
- Credential hunting
- Exploitation
- Password cracking
- Password reuse
- Port scanning / Service enumeration
- Remote Code Execution
- Reverse Shell
- SQL Injection
- SQL Injection tools
- SSH Tunneling / Port Forwarding
- SSH access
- Sudo misconfiguration
- Virtual host discovery

> **Hint:** Research known vulnerabilities for the services you find. Public CVEs are relevant here.

## Privilege Escalation Tips

- Check what you can run with `sudo -l`
- Think about **password reuse** across services
- Some services may only be accessible **locally** — think tunneling
- Enumerate **configuration files** for hardcoded credentials

---

> The **full writeup** with detailed commands and walkthrough will be published when this machine retires.
> Until then, try to solve it yourself using these hints!
