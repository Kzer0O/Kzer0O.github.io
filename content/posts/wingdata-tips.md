---
title: "[Tips] WingData - HTB Easy"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Tips and hints to solve this machine — no spoilers!"
summary: "Easy |  Linux | Tips Only"
tags:
  - "HTB"
  - "Linux"
  - "Easy"
  - "HackTheBox"
categories:
  - "HackTheBox"
series:
  - "HackTheBox"
weight: 9
ShowToc: true
TocOpen: false

cover:
  image: "/images/covers/machine-wingdata.svg"
  alt: "easy linux writeup"
  relative: false
---
> **OS:** Debian 12 | **Difficulté:** Easy | **IP:** 10.10.XX.XX

---

## Approach

This is a **tips-only** guide — no flags, no copy-paste commands.
The full writeup will be published once the machine retires on HackTheBox.

---

## Reconnaissance Tips

Start with a comprehensive port scan. Key services to investigate:

- Port **22** → SSH
- Port **80** → HTTP

## Enumeration Tips


## Exploitation Tips

Key techniques involved in this machine:

- CVE exploitation
- Credential hunting
- Exploitation
- FTP enumeration
- Password cracking
- Port scanning / Service enumeration
- Remote Code Execution
- Remote File Inclusion
- SSH access
- Sudo misconfiguration

> **Hint:** Research known vulnerabilities for the services you find. Public CVEs are relevant here.

## Privilege Escalation Tips

- Check what you can run with `sudo -l`
- Enumerate **configuration files** for hardcoded credentials

---

> The **full writeup** with detailed commands and walkthrough will be published when this machine retires.
> Until then, try to solve it yourself using these hints!
