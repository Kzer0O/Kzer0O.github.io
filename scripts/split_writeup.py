#!/usr/bin/env python3
"""
Split an active machine's writeup into:
  - {machine}-tips.md  → Tips version (published, no spoilers)
  - {machine}.md       → Full writeup (draft: true, auto-published on retire)
"""

import re, sys, os

def extract_frontmatter(content):
    """Extract YAML frontmatter and body separately."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return "", content

def parse_yaml_field(fm, field):
    """Simple extraction of a field value from YAML frontmatter."""
    match = re.search(rf'^{field}:\s*"?(.+?)"?\s*$', fm, re.MULTILINE)
    return match.group(1).strip('"') if match else ""

def generate_tips(title, body, machine_name):
    """Generate a tips/hints version from the full writeup body."""
    tips_sections = []

    # Extract phases/sections headers
    phases = re.findall(r'^(#{2,3}\s+.+)$', body, re.MULTILINE)

    # Extract key techniques mentioned
    techniques = set()
    tech_keywords = {
        'nmap': 'Port scanning / Service enumeration',
        'gobuster': 'Directory fuzzing',
        'ffuf': 'Fuzzing (directories, parameters, vhosts)',
        'sqlmap': 'SQL Injection tools',
        'sqli': 'SQL Injection',
        'sql injection': 'SQL Injection',
        'rce': 'Remote Code Execution',
        'reverse.shell': 'Reverse Shell',
        'reverse shell': 'Reverse Shell',
        'ssh': 'SSH access',
        'tunnel': 'SSH Tunneling / Port Forwarding',
        'linpeas': 'Linux enumeration (LinPEAS)',
        'winpeas': 'Windows enumeration (WinPEAS)',
        'bloodhound': 'Active Directory enumeration (BloodHound)',
        'kerberos': 'Kerberos attacks',
        'hashcat': 'Password cracking',
        'john': 'Password cracking',
        'password.reuse': 'Password reuse',
        'credential': 'Credential hunting',
        'privilege.escalation': 'Privilege Escalation',
        'privesc': 'Privilege Escalation',
        'suid': 'SUID binary exploitation',
        'sudo': 'Sudo misconfiguration',
        'cve-': 'CVE exploitation',
        'exploit': 'Exploitation',
        'chisel': 'Pivoting / Tunneling',
        'ligolo': 'Pivoting / Tunneling',
        'ldap': 'LDAP enumeration',
        'smb': 'SMB enumeration',
        'ftp': 'FTP enumeration',
        'virtual.host': 'Virtual host discovery',
        'subdomain': 'Subdomain enumeration',
        'burp': 'Web proxy / Request manipulation',
        'xss': 'Cross-Site Scripting (XSS)',
        'lfi': 'Local File Inclusion',
        'rfi': 'Remote File Inclusion',
        'ssrf': 'Server-Side Request Forgery',
        'deserialization': 'Deserialization attack',
        'docker': 'Docker / Container exploitation',
        'jwt': 'JWT token manipulation',
        'api': 'API enumeration / exploitation',
    }

    body_lower = body.lower()
    for keyword, technique in tech_keywords.items():
        if re.search(keyword.replace('.', r'\s*'), body_lower):
            techniques.add(technique)

    # Extract OS info line
    os_line = ""
    os_match = re.search(r'^>.*\*\*OS:\*\*.*$', body, re.MULTILINE)
    if os_match:
        # Redact the IP
        os_line = re.sub(r'\d+\.\d+\.\d+\.\d+', '10.10.XX.XX', os_match.group(0))

    # Extract open ports from tables
    ports = []
    port_matches = re.findall(r'\|\s*(\d+)\s*\|\s*(\w+)\s*\|', body)
    for port, service in port_matches:
        if port.isdigit() and int(port) < 65536:
            ports.append(f"- Port **{port}** → {service}")

    # Build tips content
    tips = f"""{os_line}

---

## Approach

This is a **tips-only** guide — no flags, no copy-paste commands.
The full writeup will be published once the machine retires on HackTheBox.

---

## Reconnaissance Tips

"""

    if ports:
        tips += "Start with a comprehensive port scan. Key services to investigate:\n\n"
        tips += "\n".join(ports[:6]) + "\n\n"
    else:
        tips += "Start with a comprehensive port scan to identify all exposed services.\n\n"

    tips += "## Enumeration Tips\n\n"

    # Look for virtual host / DNS hints
    if 'virtual host' in body_lower or '/etc/hosts' in body_lower or 'vhost' in body_lower:
        tips += "- Don't forget to check for **virtual hosts** and add entries to `/etc/hosts`\n"
    if 'subdomain' in body_lower:
        tips += "- Try **subdomain enumeration** — there may be hidden services\n"
    if 'gobuster' in body_lower or 'ffuf' in body_lower or 'feroxbuster' in body_lower or 'dirsearch' in body_lower:
        tips += "- **Directory fuzzing** reveals interesting paths\n"
    if 'api' in body_lower:
        tips += "- Look carefully at the **API endpoints**\n"

    tips += "\n## Exploitation Tips\n\n"
    tips += "Key techniques involved in this machine:\n\n"
    for t in sorted(techniques):
        tips += f"- {t}\n"

    # Look for CVE references
    cves = re.findall(r'CVE-\d{4}-\d+', body, re.IGNORECASE)
    if cves:
        tips += f"\n> **Hint:** Research known vulnerabilities for the services you find. Public CVEs are relevant here.\n"

    tips += "\n## Privilege Escalation Tips\n\n"

    if 'sudo' in body_lower:
        tips += "- Check what you can run with `sudo -l`\n"
    if 'suid' in body_lower:
        tips += "- Look for **SUID binaries**\n"
    if 'cron' in body_lower:
        tips += "- Monitor **cron jobs** and scheduled tasks\n"
    if 'password reuse' in body_lower or 'password.reuse' in body_lower:
        tips += "- Think about **password reuse** across services\n"
    if 'tunnel' in body_lower or 'port forward' in body_lower or 'chisel' in body_lower or 'ligolo' in body_lower:
        tips += "- Some services may only be accessible **locally** — think tunneling\n"
    if 'config' in body_lower and ('password' in body_lower or 'credential' in body_lower):
        tips += "- Enumerate **configuration files** for hardcoded credentials\n"
    if 'docker' in body_lower:
        tips += "- Pay attention to **Docker/containers** on the system\n"
    if 'bloodhound' in body_lower or 'active directory' in body_lower:
        tips += "- This is an **Active Directory** environment — enumerate thoroughly\n"

    tips += "\n---\n\n"
    tips += "> The **full writeup** with detailed commands and walkthrough will be published when this machine retires.\n"
    tips += "> Until then, try to solve it yourself using these hints!\n"

    return tips


def process_machine(posts_dir, machine):
    """Split a machine writeup into tips + full versions."""
    src = os.path.join(posts_dir, f"{machine}.md")
    tips_file = os.path.join(posts_dir, f"{machine}-tips.md")

    if not os.path.exists(src):
        print(f"[{machine}] No writeup found, skipping")
        return False

    if os.path.exists(tips_file):
        print(f"[{machine}] Tips already exists, skipping")
        return False

    with open(src, 'r') as f:
        content = f.read()

    fm, body = extract_frontmatter(content)
    title = parse_yaml_field(fm, 'title')

    # Generate tips version frontmatter
    tips_fm = fm
    # Change title to add "Tips"
    tips_fm = re.sub(r'(title:\s*")', r'\1[Tips] ', tips_fm)
    # Add tips-specific description
    tips_fm = re.sub(
        r'description:.*',
        'description: "Tips and hints to solve this machine — no spoilers!"',
        tips_fm
    )
    # Update summary
    old_summary = parse_yaml_field(fm, 'summary')
    if old_summary:
        tips_fm = re.sub(
            r'summary:.*',
            f'summary: "{old_summary} | Tips Only"',
            tips_fm
        )
    # Lower weight so tips appear first (more recent)
    old_weight = parse_yaml_field(fm, 'weight')
    if old_weight:
        try:
            tips_fm = re.sub(
                r'weight:\s*\d+',
                f'weight: {int(old_weight) - 1}',
                tips_fm
            )
        except:
            pass

    # Generate tips body
    tips_body = generate_tips(title, body, machine)

    # Write tips file
    with open(tips_file, 'w') as f:
        f.write(f"---\n{tips_fm}\n---\n{tips_body}")

    # Set original writeup to draft
    if 'draft: false' in fm or 'draft: true' not in fm:
        new_fm = re.sub(r'draft:\s*(false|true)', 'draft: true', fm)
        if 'draft:' not in fm:
            new_fm = fm + '\ndraft: true'
        with open(src, 'w') as f:
            f.write(f"---\n{new_fm}\n---\n{body}")

    print(f"[{machine}] Split OK → tips published, writeup set to draft")
    return True


if __name__ == "__main__":
    posts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "posts")

    machines = sys.argv[1:] if len(sys.argv) > 1 else []

    if not machines:
        print("Usage: split_writeup.py <machine1> [machine2] ...")
        sys.exit(1)

    for m in machines:
        process_machine(posts_dir, m.lower())
