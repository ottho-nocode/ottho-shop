---
name: shopify-bootstrap
description: Bootstrap une boutique Shopify de A à Z avec Claude Code (CLI + Custom App). Aspire la charte, customise le theme, crée les produits via Admin GraphQL, configure shipping/taxes/multilingue, intègre Printful POD. Trigger via /shopify-bootstrap.
license: Personal use
---

# /shopify-bootstrap — Setup boutique Shopify complet via Claude Code

Skill issu de la session shopishop (Ottho Mojo, mai 2026). Encode les patterns testés en réel + les platform limits identifiés.

## Quand l'invoquer

L'utilisateur veut créer une nouvelle boutique Shopify et la configurer programmatiquement (theme, produits, pages, emails, shipping, POD). Tu pilotes le workflow, l'utilisateur fait les actions UI résiduelles (account creation, OAuth approval, paste email templates).

## Ce que ce skill couvre

11 phases, ~3-5h pour une boutique complète selon volumes :

1. **Brand aspiration** — webfetch d'une URL existante pour extraire palette + tonalité + typo
2. **Niche + naming** — Q&A guidée (capture créatif vs opérationnel)
3. **Shopify account + CLI auth** — user crée le compte, claude trouve le CLI token
4. **Custom App via Dev Dashboard** — pour les scopes que CLI n'a pas
5. **Theme customization** — Horizon par défaut, CSS injection via `.css.liquid`
6. **Pages & blog** — Admin GraphQL `pageCreate` + `articleCreate` + images
7. **Settings** — taxes, Markets, primary language, multilingue
8. **Catalogue produit** — designs via fal.ai NB2, bulk import via `productSet`
9. **Email transactionnels** — platform limit, paste manuelle dans admin
10. **Shipping zones** — `deliveryProfileUpdate` (attention `zonesToDelete` top-level)
11. **POD Printful** — install app + sync via UI obligatoire (platform limit)

## Arguments

`/shopify-bootstrap` (sans argument) → mode interactif, je guide phase par phase
`/shopify-bootstrap audit` → audit complet de l'état actuel d'une boutique existante
`/shopify-bootstrap phase=N` → reprend à la phase N (ex `phase=4` pour le custom app)

## Référence : scripts réutilisables

Tous les scripts paramétrables sont dans `~/.claude/skills/shopify-bootstrap/scripts/`. Tu les copies dans `<project>/store/scripts/` et tu les adaptes au domain de la boutique cible.

| Script | Rôle |
|---|---|
| `cli-token.py` | Lit le token OAuth caché par `shopify theme dev` |
| `custom-app-token.py` | Génère un token via OAuth `client_credentials` grant |
| `productset-bulk.py` | Crée N produits via `productSet` mutation (upsert) |
| `staged-upload.py` | Upload binaire vers Shopify CDN via `stagedUploadsCreate` |
| `delivery-profile-update.py` | Configure shipping zones par pays |
| `publishable-publish.py` | Publie un produit sur un sales channel |
| `printful-store-info.py` | Récupère le store_id Printful via API |
| `printful-verify.py` | Audit post-sync : produits avec metafields Printful |
| `generate-print-files.py` | Génère N PNG transparent via PIL + Google Fonts |

## Référence : templates

Templates dans `~/.claude/skills/shopify-bootstrap/templates/` :

- `email-01-order-confirmation.html` à coller dans Shopify admin → Settings → Notifications
- `email-02-shipping-confirmation.html`
- `email-03-order-delivered.html`
- `email-04-customer-welcome.html`
- `email-05-abandoned-cart.html`
- `email-06-refund.html`
- `printful-mapping.template.md` table de mapping Shopify ↔ Stanley/Stella
- `theme-css-liquid.template` injection CSS personnalisée pour Horizon

## Workflow détaillé

### Phase 1, brand aspiration (10 min)

L'utilisateur fournit une URL (site existant). Tu fais un WebFetch + capture :

- Palette (15+ hex codes, top 5 dominants)
- Typographies (font-family CSS détectés, serif/sans/mono)
- Tonalité (3-5 phrases-clés du copy)
- Composition (asymétrie, marges, hiérarchie)

Sauvegarde dans `<project>/store/brand/charte.md`.

### Phase 2, niche + naming (Q&A)

Pose 5-8 questions structurées. Pour chaque réponse :
- **Choix créatif** (naming, tagline, concept) → capture verbatim, c'est du contenu pédagogique réutilisable
- **Choix opérationnel** (forfait, B2C/B2B) → enseigne le cadre de décision sans biaiser

### Phase 3, Shopify account + CLI

User crée le compte Shopify, choix forfait. Une fois le wizard fini, lance dans son terminal :

```bash
mkdir -p store/theme
cd store/theme
shopify theme init  # ou shopify theme pull si theme existant
shopify theme dev   # ouvre le browser pour OAuth, token caché
```

Le token OAuth est caché dans :

```
~/Library/Preferences/shopify-cli-kit-nodejs/config.json
```

Extraction Python :

```python
import json
from pathlib import Path
data = json.loads((Path.home() / "Library/Preferences/shopify-cli-kit-nodejs/config.json").read_text())
session = json.loads(data["sessionStore"])
for acct in session.get("accounts.shopify.com", {}).values():
    for key, app in acct.get("applications", {}).items():
        if key.startswith(f"{DOMAIN}-") and "accessToken" in app:
            print(app["accessToken"])
```

Couvre : read/write_themes, read/write_products, read/write_files, read/write_translations.
NE couvre PAS : write_content (pages, blog), write_publications, write_shipping. Pour ça → Custom App phase 4.

### Phase 4, Custom App (5 min)

User va dans `https://admin.shopify.com/store/<store>/settings/apps/development`. Crée une app, scopes :
- `write_content` (pages, blogs, articles)
- `write_publications` (publishablePublish)
- `write_translations` (Translate & Adapt)
- `write_shipping` (delivery profiles)

Une fois la app créée, récupère **client_id + client_secret**. Génère le token via OAuth `client_credentials` :

```python
import json, urllib.request
payload = json.dumps({
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
}).encode()
req = urllib.request.Request(
    f"https://{DOMAIN}/admin/oauth/access_token",
    data=payload,
    headers={"Content-Type": "application/json"},
)
APP_TOKEN = json.loads(urllib.request.urlopen(req).read())["access_token"]
```

Pas d'OAuth dance complète nécessaire — `client_credentials` est documenté à `https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets`.

### Phase 5, theme customization

Theme par défaut Shopify 2026 = **Horizon** (a remplacé Dawn). Pour customiser sans toucher aux fichiers de base :

```liquid
{# assets/<brand>.css.liquid #}
{{ 'fonts.googleapis.com/css2?family=...' | stylesheet_tag }}

[id*="hero_"] {
  background-color: var(--color-cream, #F5F3F7);
}
.italic-violet {
  font-style: italic;
  color: var(--color-accent, #7C4DFF);
}
```

L'extension `.css.liquid` permet d'utiliser des variables Liquid dans le CSS.

⚠️ Limites Horizon :
- Le top-level DOM doit être `<p>` ou `<h1-6>` (textes wrapped)
- Les classes CSS sur les sections sont strippées par le sanitizer
- Pour styler une section spécifique, utilise un sélecteur parent comme `[id*="hero_jVaWmY"]`
- Padding section schema cap à 100 (pas plus)

### Phase 6, pages & blog

```python
PAGE_MUTATION = """
mutation pageCreate($page: PageCreateInput!) {
  pageCreate(page: $page) {
    page { id handle }
    userErrors { field message }
  }
}
"""
```

Idem pour `articleCreate`, `blogCreate`. Pour les images dans articles :

```python
ARTICLE_UPDATE = """
mutation articleUpdate($id: ID!, $article: ArticleUpdateInput!) {
  articleUpdate(id: $id, article: $article) {
    article { id image { url altText } }
    userErrors { field message }
  }
}
"""
# Champ image: { url, altText } — PAS src, PAS originalSource (vérifié par introspection)
```

### Phase 7, settings

⚠️ **Translate & Adapt timing critique** : si tu actives la traduction du theme APRÈS l'avoir customisé, tu corromps le serveur Shopify et provoques des 404 globaux. **Active la traduction AVANT le pull theme.**

Ordre safe :
1. Activer Translate & Adapt + langues secondaires
2. Pull theme
3. Customize
4. Push theme

### Phase 8, catalogue produit

```python
PRODUCT_SET = """
mutation productSet($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
  productSet(input: $input, identifier: $identifier, synchronous: true) {
    product { id handle }
    userErrors { field message }
  }
}
"""
```

`productSet` est upsert (crée ou met à jour) sur identifier (handle). Préféré à `productCreate` pour idempotence.

Pour les images : `stagedUploadsCreate` → S3 PUT → `productCreateMedia` avec `mediaContentType: IMAGE`.

Designs visuels via fal.ai endpoint `https://fal.run/fal-ai/nano-banana-2` (NB2, le bon model pour mockups produit). Aspect ratio "1:1" ou "16:9", resolution "2K", "safety_tolerance": "4".

Smart collections via `collectionCreate` avec rules :

```python
COLLECTION_CREATE = """
mutation collectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection { id handle }
    userErrors { field message }
  }
}
"""
# input.ruleSet = { appliedDisjunctively: false, rules: [{column, relation, condition}] }
```

### Phase 9, email transactionnels — PLATFORM LIMIT

⚠️ **Aucune API ne permet de modifier les templates email**. Vérifié par introspection GraphQL Admin 2025-10 :
- 6 mutations email existent, toutes "send-only" (`customerSendAccountInviteEmail`, `customerPaymentMethodSendUpdateEmail`, etc.)
- 0 type `EmailTemplate`, `Notification`, `NotificationTemplate`
- 0 endpoint REST notifications

→ User doit COLLER manuellement les 6 templates HTML dans `https://admin.shopify.com/store/<store>/settings/notifications`.

Templates ready-to-paste dans `~/.claude/skills/shopify-bootstrap/templates/email-*.html`. Variables Liquid Shopify supportées : `{{ shop_name }}`, `{{ order_name }}`, `{{ customer.first_name }}`, `{{ tracking_number }}`, etc.

⚠️ Limite Shopify : les emails ne peuvent pas charger Google Fonts. Utiliser des fallbacks système (`Georgia, serif` au lieu d'Instrument Serif, `ui-monospace` au lieu de Geist Mono).

### Phase 10, shipping zones

```python
DELIVERY_PROFILE_UPDATE = """
mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile, leaveLegacyModeProfiles: false) {
    profile { id }
    userErrors { field message }
  }
}
"""
```

⚠️ **Silent fail trap** : `zonesToDelete` est au TOP-LEVEL de DeliveryProfileInput, pas niché sous `locationGroupsToUpdate`. Si tu le mets au mauvais endroit, GraphQL accepte la mutation, retourne `userErrors: []` (success), mais ne supprime rien.

Bon payload :

```python
payload = {
    "profile": {
        "zonesToDelete": [...],          # top-level, ICI
        "locationGroupsToUpdate": [{
            "id": LOC_GROUP,
            "zonesToCreate": [...],
        }]
    }
}
```

**Toujours re-query après mutation pour vérifier l'effet réel.** Ne pas se fier à `userErrors: []`.

### Phase 11, Printful POD

⚠️ **Platform limit Printful pour les stores type "shopify"** :
- `POST /sync/products` → 405 (GET only)
- `POST /store/products` → 400 "Manual Order / API platform only"
- `POST /v2/sync-products` → 404

→ Création des sync products = obligatoirement dans l'UI Printful (Stores → Sync products → Add product → Sync existing from Shopify).

**Workaround pratique** :
1. Pré-générer les print files via PIL + Google Fonts (`generate-print-files.py`)
2. Pré-uploader sur Shopify CDN via `stagedUploadsCreate` (URLs publiques)
3. Pré-écrire le mapping Shopify ↔ Stanley/Stella catalog (`printful-mapping.template.md`)
4. User drag-drop les PNG dans Printful UI en suivant le mapping
5. API utile post-sync : `GET /v2/sync-products` (audit), `PUT /sync/products/{id}` (updates)

**Token API Printful** : créé sur `https://developers.printful.com/` (Developer Portal séparé), pas le dashboard store.

**Stanley/Stella catalog references** :
- Tee Creator 2.0 STTU169 = product_id **456** (15 colors, manque "Vintage White", proche = "Desert Dust" pour cream off-white)
- Hoodie Drummer 2.0 SASU009 = product_id **821** (7 colors, Black + Desert Dust pour cream)
- Mug 11oz White Glossy = product_id **19**
- Mug 11oz Black Glossy = product_id **300**

**Print file specs** :
- Tee chest / Hoodie chest / back : 4500 × 5400 px (15" × 18" @ 300 DPI)
- Tee hem (ourlet bas) : 4500 × 1200 px (15" × 4")
- Mug side : 1200 × 1050 px (4" × 3.5")
- Mug wrap : 2475 × 1050 px (8.25" × 3.5")
- Format : PNG transparent (RGBA), pas JPG

## Memories à charger

Avant chaque phase, vérifie ces memories du projet utilisateur :

- `feedback_shopify_cli_token_trick.md` (phase 3)
- `feedback_translate_adapt_timing.md` (phase 5/7)
- `feedback_shopify_graphql_silent_fails.md` (phase 10)
- `feedback_printful_shopify_api_limit.md` (phase 11)
- `feedback_capture_creatif_vs_operationnel.md` (phase 2)
- `reference_printful_api_keys.md` (phase 11)

## Audit final

Après chaque phase, vérifie via Admin GraphQL :

```python
{
  shop { name primaryDomain { url } }
  products(first: 50) { nodes { handle status totalVariants vendor } }
  pages(first: 20) { nodes { handle isPublished } }
  blogs(first: 5) { nodes { handle articles(first: 10) { nodes { handle isPublished image { url } } } } }
  deliveryProfiles(first: 5) { nodes { name profileLocationGroups { locationGroupZones(first: 5) { nodes { zone { name } } } } } }
}
```

Si quelque chose manque, ne déclare pas la phase done. Re-query, suspecte ta structure d'abord, l'API ensuite.

## Output utilisateur

À chaque phase complétée, donne un récap court :

```
✅ Phase X — <titre>
  - <action 1>
  - <action 2>
  - Vérifié via API : <count> ressources créées
  - Reste à faire en UI : <action si applicable>
```

Pas de blabla. L'utilisateur doit pouvoir lire les statuts en 5 secondes par phase.
