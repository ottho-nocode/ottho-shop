# ottho-shop

> Marketplace Claude Code pour les plugins du cours [academy.ottho.co/claude-shopify](https://academy.ottho.co/claude-shopify) « Claude + Shopify ».

## Plugins disponibles

### `shop` — Compagnon du cours « Claude + Shopify »

Bootstrap complet d'une boutique Shopify de A à Z (CLI + Custom App). Aspiration de charte, customisation du theme Horizon, création produits/pages/blog en bulk via Admin GraphQL, shipping zones, multilingue, POD Printful avec gestion des platform limits documentés (notifications email côté Shopify, sync products côté Printful pour stores Shopify-integrated).

- **`/shop:bootstrap`** — **MASTER** : orchestre les 11 phases du cours de A à Z (charte → CLI → Custom App → theme → produits → blog → shipping → multilingue → POD), avec checkpoint à chaque phase, reprenable
- `/shop:bootstrap audit` — audit complet de l'état d'une boutique existante (produits actifs, pages publiées, blog, settings shipping, sync Printful) via Admin GraphQL, sortie en tableau récap
- `/shop:bootstrap phase=N` — reprend à la phase N spécifique (ex `phase=4` pour Custom App, `phase=8` pour catalogue produit, `phase=11` pour POD Printful)

Détail complet : [shop/README.md](./shop/README.md)

## Installation

Dans Claude Code :

```
/plugin marketplace add ottho-nocode/ottho-shop
/plugin install shop@ottho-shop
```

Pour démarrer le parcours complet en une seule commande :

```
/shop:bootstrap
```

Cette commande pose 5-8 questions structurées (audience, niche, naming, charte source) puis enchaine les 11 phases avec confirmation utilisateur entre chaque. Compter ~3-5h pour une boutique fonctionnelle de bout en bout.

## Les 11 phases

| # | Phase | Ce que ça fait |
|---|---|---|
| 1 | Brand aspiration | WebFetch d'une URL existante → palette + tonalité + typo |
| 2 | Niche + naming | Q&A guidée (capture créatif vs opérationnel) |
| 3 | Shopify account + CLI auth | Récupération du token CLI caché par `shopify theme dev` |
| 4 | Custom App via Dev Dashboard | Token via OAuth `client_credentials` grant pour scopes `write_content`, `write_publications`, `write_translations`, `write_shipping` |
| 5 | Theme customization | Horizon (theme Shopify 2026 par défaut) + injection CSS via `.css.liquid` |
| 6 | Pages & blog | `pageCreate`, `articleCreate`, attachement images via `articleUpdate` |
| 7 | Settings | Taxes, Markets, primary language, multilingue (Translate & Adapt avant pull theme) |
| 8 | Catalogue produit | Designs visuels via fal.ai Nano Banana 2, bulk import via `productSet` |
| 9 | Email transactionnels | ⚠️ platform limit Shopify, paste manuelle dans admin (6 templates HTML fournis) |
| 10 | Shipping zones | `deliveryProfileUpdate` avec gestion du piège `zonesToDelete` top-level |
| 11 | POD Printful | Install app + sync via UI obligatoire (platform limit), scripts pour le pré-prep |

## Pré-requis

- Avoir suivi (ou lu) les cours [Claude + Site web](https://academy.ottho.co/claude-site-web) et [Claude + Blog](https://academy.ottho.co/claude-blog), ce plugin en est le prolongement
- Compte Shopify (Trial gratuit, puis 1$/mois × 3 mois sur certains forfaits)
- Compte Printful gratuit (créé lors de la phase 11)
- Compte fal.ai pour les designs visuels (~0,40 € pour 10 mockups produit en NB2)

## Pré-requis MCP

Le plugin n'utilise **pas de MCP** : tout passe par les SDK CLI Shopify, l'API REST Printful, et fal.ai en HTTP direct. Auth via :

- Token OAuth Shopify caché dans `~/Library/Preferences/shopify-cli-kit-nodejs/config.json` (récupéré par `cli-token.py`)
- Token Custom App Shopify généré via `client_credentials` grant (script `custom-app-token.py`)
- Token API Printful Private créé sur [developers.printful.com](https://developers.printful.com/)
- Clé API fal.ai en variable d'env

## Platform limits documentés

Le plugin encode et contourne les 2 vrais blockers du couple Shopify + Printful :

- **Shopify** : aucune API ne permet de modifier les templates email (vérifié par introspection GraphQL Admin 2025-10). Les 6 templates HTML sont fournis ready-to-paste dans `templates/`.
- **Printful** : pour les stores type "shopify", `POST /sync/products` est bloqué (405). La création initiale du mapping doit passer par l'UI. L'API permet `GET` (audit) et `PUT` (updates ultérieures).

Tout le reste est scriptable via Admin GraphQL + Printful API.

## Scripts inclus

Le skill `bootstrap` embarque 7 scripts Python paramétrables (env vars) :

- `cli-token.py` — extrait le token OAuth caché par `shopify theme dev`
- `custom-app-token.py` — génère un token via OAuth `client_credentials` grant
- `delivery-profile-update.py` — configure shipping zones avec re-query post-mutation (gestion du silent fail trap)
- `printful-store-info.py` — récupère le store_id Printful + audit connectivité
- `printful-verify.py` — audit post-sync : produits Shopify avec metafields Printful
- `staged-upload.py` — upload binaire vers Shopify CDN via `stagedUploadsCreate` + S3 PUT
- `generate-print-files.py` — génère N PNG transparents (4500×5400 / 2475×1050) via PIL + Google Fonts (Instrument Serif + Geist Mono)

## Templates inclus

8 templates ready-to-use :

- `email-01-order-confirmation.html` à coller dans `Settings → Notifications → Order confirmation`
- `email-02-shipping-confirmation.html`
- `email-03-order-delivered.html`
- `email-04-customer-welcome.html`
- `email-05-abandoned-cart.html`
- `email-06-refund.html`
- `printful-mapping.template.md` — table de mapping Shopify ↔ Stanley/Stella catalog (Creator 2.0 = #456, Drummer 2.0 = #821, Mug 11oz White = #19, Black = #300)
- `theme-css-liquid.template` — injection CSS personnalisée pour Horizon (variables Liquid + sélecteurs `[id*="hero_"]` parents)

## Coût indicatif

| Action | Coût LLM | Avec assets fal.ai |
|---|---|---|
| `/shop:bootstrap` (full) | ~0,80 € | ~1,20 € (10 mockups produit + 1 hero image) |
| `/shop:bootstrap phase=8` (catalogue) | ~0,30 € | ~0,70 € |
| `/shop:bootstrap audit` | ~0,05 € | 0,05 € |

Boutique complète 10 produits + blog 6 articles + emails + POD : **~1,50 €** en LLM + fal.ai (vs développement custom ~2 000-5 000 €).

## Public visé

Élèves Ottho ayant déjà suivi les cours « Claude + Site » et « Claude + Blog ». Maîtrise du prompting, structure de fichiers, déploiement Vercel, fal.ai, MCP basiques. Découvrent : Shopify, POD, Stripe, copy e-commerce, recherche de niche/winner.

## Cours associé

[academy.ottho.co/claude-shopify](https://academy.ottho.co/claude-shopify) — 16 leçons sur 4 chapitres + bonus, ~3-5h de pratique réelle pour une boutique fonctionnelle de bout en bout. Chaque chapitre du cours mobilise une phase du plugin.

## License

MIT
