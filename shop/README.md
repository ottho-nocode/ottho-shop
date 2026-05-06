# shop

> Plugin compagnon du cours [academy.ottho.co/claude-shopify](https://academy.ottho.co/claude-shopify).
> Bootstrap complet d'une boutique Shopify de A à Z avec Claude Code — sans jamais quitter ton terminal sauf pour les actions UI résiduelles (creation account, OAuth approval, paste email templates).

## À qui ça s'adresse

Ce plugin est le 3ème volet du parcours Ottho après *Claude + Site web* et *Claude + Blog*. Si tu maîtrises déjà Claude Code et que tu veux monter une boutique e-commerce vraie de chez vraie en quelques heures :

- Aspiration de charte depuis un site existant (palette, typo, tonalité)
- Theme Horizon (Shopify 2026) customisé via injection CSS Liquid, pas via fork du theme
- Création des produits/pages/blog en bulk via Admin GraphQL (`productSet`, `pageCreate`, `articleCreate`)
- Designs visuels via fal.ai Nano Banana 2 (mockups + hero images + print files transparents pour POD)
- Shipping zones configurées par script Python (avec gestion du piège `zonesToDelete` top-level)
- Multilingue via Translate & Adapt (timing critique documenté)
- POD Printful linké, sync products préparées (designs PNG transparent + mapping Stanley/Stella + URLs Shopify CDN)

**Pré-requis :**
- Avoir suivi (ou lu) les cours *Claude + Site web* et *Claude + Blog*
- Compte Shopify (Trial gratuit puis 1$/mois × 3 sur certains forfaits)
- Compte Printful gratuit (créé en phase 11)
- Clé API fal.ai pour les visuels

## Installation

Dans Claude Code :

```
/plugin marketplace add ottho-nocode/ottho-shop
/plugin install shop@ottho-shop
```

Vérification : tape `/` dans Claude Code, tu dois voir `/shop:bootstrap` apparaitre dans l'autocomplétion.

## Pré-requis MCP

Le plugin **n'utilise aucun MCP**. Tout passe par les SDK CLI Shopify, l'API REST Printful, et fal.ai en HTTP direct :

| Outil | Rôle | Auth |
|---|---|---|
| **Shopify CLI** | Theme management + token OAuth caché | `shopify theme dev` au moins une fois (le token est extrait du config CLI par `cli-token.py`) |
| **Custom App Shopify** | Scopes `write_content`, `write_publications`, `write_translations`, `write_shipping` | Token via `client_credentials` grant (script `custom-app-token.py`) |
| **Printful API** | Catalog, sync products audit, orders | Token Private créé sur [developers.printful.com](https://developers.printful.com/) |
| **fal.ai** | Designs visuels Nano Banana 2 | Clé API en variable d'env `FAL_KEY` |

Zéro `npm install`, zéro MCP install, juste les SDK natifs et l'auth standard.

## La commande `/shop:bootstrap`

Une seule commande pilote tout le parcours. Trois modes :

### Mode interactif (par défaut)

```
/shop:bootstrap
```

Pose 5-8 questions structurées :
1. URL de la charte source (site existant à aspirer)
2. Niche cible (apparel, accessoires, food, etc.)
3. Naming + tagline (capture verbatim, pas de biais)
4. Audience (B2C / B2B / mix)
5. Multilingue (mono ou bilingue FR/EN)
6. POD (Printful UE / US / autre, ou pas de POD)
7. Test order (oui / non en phase 11)
8. Domaine custom (oui / non, on configure plus tard)

Puis enchaine les 11 phases avec confirmation utilisateur entre chaque. Reprenable si tu coupes la session (l'état de chaque phase est tracé dans Admin GraphQL, pas dans un fichier local).

### Mode audit

```
/shop:bootstrap audit
```

Audit complet d'une boutique existante via Admin GraphQL. Sortie en tableau :

- Produits actifs (`status: ACTIVE`) avec compteur de variantes et metafields Printful
- Pages publiées (`isPublished: true`)
- Blog articles avec image attachée
- Shipping zones par profile + location group
- Sync products côté Printful (via API v2)

À utiliser quand tu reprends le travail sur une boutique deja ébauchée, ou pour vérifier que les phases précédentes ont laissé l'état attendu.

### Mode reprise

```
/shop:bootstrap phase=N
```

Reprend à la phase N spécifique. Cas typiques :

- `phase=4` — Custom App créé hors-cycle, on enchaine direct sur le theme
- `phase=8` — produits seuls (pour rajouter une collection à une boutique existante)
- `phase=10` — shipping zones seules (changement de tarif, ajout de pays)
- `phase=11` — POD Printful seul (le reste de la boutique est déjà en prod)

Vérifie l'état des phases précédentes avant d'exécuter (audit interne automatique).

## Les 11 phases en détail

### Phase 1, brand aspiration (10 min)

WebFetch d'une URL existante. Extrait :

- **Palette** : 15+ hex codes du CSS rendu, top 5 dominants
- **Typographies** : font-family CSS (serif / sans-serif / mono détectés)
- **Tonalité** : 3-5 phrases-clés du copy
- **Composition** : asymétrie, marges, hiérarchie typographique

Sauve dans `<project>/store/brand/charte.md` (format markdown standard, prêt à être référencé par le theme).

### Phase 2, niche + naming (Q&A guidée)

Distinction critique entre choix créatif et choix opérationnel :

- **Choix créatif** (naming, tagline, concept) : capture verbatim de tes réponses comme case study, c'est du contenu pédagogique réutilisable
- **Choix opérationnel** (forfait Shopify, B2C/B2B) : enseigne le cadre de décision sans biaiser avec ta réponse perso

### Phase 3, Shopify CLI auth (5 min)

Tu lances `shopify theme dev` une fois en local, le token OAuth est caché par le CLI dans `~/Library/Preferences/shopify-cli-kit-nodejs/config.json`. Le script `cli-token.py` l'extrait pour les scripts suivants.

Couvre : `read/write_themes`, `read/write_products`, `read/write_files`, `read/write_translations`.

⚠️ Ne couvre pas : `write_content`, `write_publications`, `write_shipping`. → Custom App phase 4.

### Phase 4, Custom App via Dev Dashboard (5 min)

User crée une app dans `https://admin.shopify.com/store/<store>/settings/apps/development`. Scopes accordés : `write_content`, `write_publications`, `write_translations`, `write_shipping`. Token généré via OAuth `client_credentials` grant (pas de OAuth dance complète).

Doc référence : [shopify.dev/docs/apps/build/authentication-authorization/client-secrets](https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets)

### Phase 5, theme customization (15 min)

Theme par défaut Shopify 2026 = **Horizon** (a remplacé Dawn ~2024). Custom CSS via fichier `assets/<brand>.css.liquid` (l'extension `.css.liquid` permet d'utiliser des variables Liquid dans le CSS).

⚠️ Limites Horizon documentées :
- Top-level DOM dans rich text doit être `<p>` ou `<h1-6>` (sinon sanitizer strip)
- Classes CSS sur les sections sont strippées, utilise des sélecteurs parents `[id*="hero_xxxxxx"]`
- Padding settings cap à 100, pas plus

### Phase 6, pages & blog (10 min)

Création via Admin GraphQL :
- `pageCreate` pour les pages statiques (À propos, Contact, FAQ, CGV, Politique de confidentialité)
- `blogCreate` puis `articleCreate` pour le blog
- `articleUpdate` pour attacher une hero image (champ `image: { url, altText }`, vérifié par introspection — pas `src` ni `originalSource`)

### Phase 7, settings (5 min)

⚠️ **Translate & Adapt timing critique** : active la traduction du theme AVANT le pull, sinon corruption serveur Shopify et 404 globaux.

Ordre safe :
1. Activer Translate & Adapt + langues secondaires
2. Pull theme local
3. Customize CSS Liquid + sections
4. Push theme

### Phase 8, catalogue produit (30 min selon volume)

`productSet` est une mutation upsert (idempotent par handle). Préféré à `productCreate` pour les bulk imports car re-runnable sans erreur.

Designs visuels via fal.ai endpoint `https://fal.run/fal-ai/nano-banana-2` (Nano Banana 2). Aspect ratio "1:1" ou "16:9", resolution "2K".

Smart collections via `collectionCreate` avec `ruleSet.rules` (ex: tag = "tee", appliedDisjunctively false).

### Phase 9, email transactionnels (10 min) — PLATFORM LIMIT

⚠️ Aucune API ne permet de modifier les templates email. Vérifié par introspection GraphQL Admin 2025-10 :
- 6 mutations email existent, toutes "send-only" (`customerSendAccountInviteEmail`, etc.)
- 0 type `EmailTemplate`, `Notification`, `NotificationTemplate`

→ User colle manuellement les 6 templates HTML fournis dans `templates/email-*.html` dans `https://admin.shopify.com/store/<store>/settings/notifications`.

### Phase 10, shipping zones (10 min)

`deliveryProfileUpdate` avec gestion du piège **silent fail GraphQL** : `zonesToDelete` est au TOP-LEVEL de `DeliveryProfileInput`, pas niché sous `locationGroupsToUpdate`. Si tu le mets au mauvais endroit, GraphQL accepte, retourne `userErrors:[]`, mais ne supprime rien.

Le script `delivery-profile-update.py` re-query toujours après mutation pour vérifier l'effet réel.

### Phase 11, POD Printful (15 min) — PLATFORM LIMIT

⚠️ Pour les stores type "shopify" :
- `POST /sync/products` → 405 GET-only
- `POST /store/products` → 400 "Manual Order / API platform only"
- `POST /v2/sync-products` → 404

→ Création des sync products = obligatoirement dans l'UI Printful.

**Workaround pratique scripté** :
1. `generate-print-files.py` : génère les PNG transparents (4500×5400 pour tee/hoodie chest, 2475×1050 pour mug wrap) via PIL + Google Fonts (Instrument Serif Italic + Geist Mono)
2. `staged-upload.py` : upload sur Shopify CDN pour avoir des URLs publiques (au cas où Printful UI accepte le paste URL)
3. `printful-mapping.template.md` : Stanley/Stella catalog refs (Creator 2.0 = #456, Drummer 2.0 = #821, Mug 11oz White = #19, Black = #300)
4. User drag-drop les PNG locaux dans Printful UI en suivant le mapping (~10 min)
5. `printful-verify.py` : audit post-sync via Admin GraphQL (vendor + metafields Printful)

## Garde-fous non-négociables

- **Re-query post-mutation** : ne pas se fier à `userErrors:[]`, toujours vérifier l'effet réel via re-query GraphQL (le silent fail trap est documenté dans `feedback_shopify_graphql_silent_fails.md` du projet utilisateur)
- **Translate & Adapt avant pull theme** : sinon corruption serveur (le timing critique est documenté dans `feedback_translate_adapt_timing.md`)
- **CLI token vs Custom App token** : le CLI token NE couvre PAS les scopes content/publications/shipping. Phase 4 obligatoire avant d'agir sur ces ressources
- **Designs print PNG transparent**, pas JPG : Printful DTG imprime le fond du fichier, JPG = fond blanc imprimé sur tee cream → catastrophe

## Coût indicatif

| Action | Coût LLM | Avec assets fal.ai |
|---|---|---|
| Phase 1 (charte aspirate) | ~0,02 € | 0,02 € |
| Phase 5 (theme custom) | ~0,10 € | ~0,15 € (1 hero image) |
| Phase 8 (10 produits) | ~0,20 € | ~0,60 € (10 mockups NB2) |
| Phase 11 (10 print files) | ~0,05 € | 0,05 € (PIL local, pas de fal.ai) |
| `/shop:bootstrap` complet | **~0,80 €** | **~1,20 €** |

Boutique 10 produits + blog 6 articles + emails + POD : **~1,50 €** total.

## Cours associé

[academy.ottho.co/claude-shopify](https://academy.ottho.co/claude-shopify) — 16 leçons sur 4 chapitres + bonus, ~3-5h de pratique réelle. Chaque chapitre du cours mobilise une phase du plugin :

- **Chapitre 1, Cadrage et niche** → phases 1-2
- **Chapitre 2, Setup Shopify** → phases 3-7
- **Chapitre 3, Catalogue produit** → phase 8
- **Chapitre 4, Paiement, livraison, emails** → phases 9-10
- **Bonus, POD et winners** → phase 11 + framework de recherche de produits winners
