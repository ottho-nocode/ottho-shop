---
name: bootstrap
description: Bootstrap complet d'une boutique Shopify en 11 phases (charte, CLI, Custom App, theme Horizon, produits, blog, shipping, multilingue, POD Printful). Encode les patterns testés et les platform limits avec workarounds. Sans argument → mode interactif. `phase=N` reprend à la phase N. `audit` lance un audit de l'état actuel.
---

Tu es le pilote du workflow `/shop:bootstrap`. Charge le contenu détaillé depuis le skill `bootstrap` du plugin (Skill tool → `bootstrap`) avant la première action.

## Comportement

Sans argument :
- Mode interactif. Tu poses 5-8 questions structurées (audience, niche, naming, charte source, etc.) puis enchaines les phases avec confirmation utilisateur entre chaque.

Avec `phase=N` :
- Reprend à la phase N (ex `phase=4` pour Custom App). Suppose que les phases précédentes sont déjà faites, tu valides l'état avant d'exécuter.

Avec `audit` :
- Audit complet de l'état d'une boutique existante (produits actifs, pages publiées, blog, settings shipping, etc.) via Admin GraphQL. Sortie en tableau récap.

## Phases

1. Brand aspiration (WebFetch d'une URL existante)
2. Niche + naming (Q&A)
3. Shopify account + CLI auth
4. Custom App via Dev Dashboard
5. Theme customization (Horizon + .css.liquid)
6. Pages & blog
7. Settings (taxes, Markets, multilingue)
8. Catalogue produit (designs fal.ai + bulk import)
9. Email transactionnels (platform limit, paste manuelle)
10. Shipping zones (`deliveryProfileUpdate`)
11. POD Printful (UI obligatoire pour les stores Shopify, scripts pour le pré-prep)

Pour chaque phase, vérifie l'effet réel via re-query Admin GraphQL après chaque mutation. Ne te fie pas à `userErrors:[]` (silent fail trap).

Voir `skills/bootstrap/SKILL.md` pour le détail technique, les scripts paramétrables et les templates.
