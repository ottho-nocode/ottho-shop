# ottho-shop

> Marketplace Claude Code pour le cours [academy.ottho.co/claude-shopify](https://academy.ottho.co/claude-shopify) « Claude + Shopify ».

## Installation

Dans Claude Code :

```
/plugin marketplace add ottho-nocode/ottho-shop
/plugin install shop@ottho-shop
```

Une fois installé, le plugin expose la commande `/shop:bootstrap`.

## Plugin `shop`

Bootstrap complet d'une boutique Shopify en 11 phases :

1. **Brand aspiration** — extraction palette + tonalité depuis une URL existante
2. **Niche + naming** — Q&A guidée (capture créatif vs opérationnel)
3. **Shopify account + CLI auth** — récupération du token CLI caché
4. **Custom App via Dev Dashboard** — pour les scopes `write_content`, `write_publications`, `write_translations`, `write_shipping`
5. **Theme customization** — Horizon (theme Shopify 2026 par défaut) + injection CSS via `.css.liquid`
6. **Pages & blog** — création via Admin GraphQL (`pageCreate`, `articleCreate`)
7. **Settings** — taxes, Markets, primary language, multilingue (Translate & Adapt)
8. **Catalogue produit** — designs visuels via fal.ai Nano Banana 2, bulk import via `productSet`
9. **Email transactionnels** — ⚠️ platform limit Shopify, paste manuelle dans admin (templates HTML fournis)
10. **Shipping zones** — `deliveryProfileUpdate` avec gestion du piège `zonesToDelete` top-level
11. **POD Printful** — install app + sync via UI obligatoire (platform limit pour stores Shopify-integrated), scripts pour le pré-prep

## Platform limits documentés

Le plugin encode et contourne les 2 vrais blockers du couple Shopify + Printful :

- **Shopify** : aucune API ne permet de modifier les templates email (vérifié par introspection GraphQL Admin 2025-10). Les 6 templates HTML sont fournis ready-to-paste dans `templates/`.
- **Printful** : pour les stores type "shopify", `POST /sync/products` est bloqué (405). La création initiale du mapping doit passer par l'UI. L'API permet `GET` (audit) et `PUT` (updates ultérieures).

Tout le reste est scriptable via Admin GraphQL + Printful API.

## Scripts inclus

Le skill `bootstrap` embarque 7 scripts Python paramétrables (env vars) :

- `cli-token.py` — extrait le token OAuth caché par `shopify theme dev`
- `custom-app-token.py` — génère un token via OAuth `client_credentials` grant
- `delivery-profile-update.py` — configure shipping zones avec re-query post-mutation
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
- `printful-mapping.template.md` — table de mapping Shopify ↔ Stanley/Stella catalog
- `theme-css-liquid.template` — injection CSS personnalisée pour Horizon

## Public visé

Élèves Ottho ayant déjà suivi les cours « Claude + Site » et « Claude + Blog ». Maîtrise du prompting, structure de fichiers, déploiement Vercel, fal.ai, MCP basiques. Découvrent : Shopify, POD, Stripe, copy e-commerce, recherche de niche/winner.

## Cours associé

[academy.ottho.co/claude-shopify](https://academy.ottho.co/claude-shopify) — 16 leçons sur 4 chapitres + bonus, ~3-5h de pratique réelle pour une boutique fonctionnelle de bout en bout.

## License

MIT
