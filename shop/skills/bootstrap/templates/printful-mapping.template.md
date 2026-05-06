# Mapping Shopify products → Printful catalog (TEMPLATE)

> Référence pour le step 3 de la phase 11 (POD Printful) : choisir le bon Printful base product pour chaque pièce de la boutique. Catalog Printful 2026.

## Stanley/Stella tees + hoodies (premium UE)

| Printful base | product_id | Style # | Coût XL UE | Colors clés |
|---|---|---|---|---|
| **Creator 2.0** (tee) | **456** | STTU169 | ~13,80 € | White, Black, Anthracite, **Desert Dust** (≈cream), French Navy, Heather Grey |
| **Drummer 2.0** (hoodie) | **821** | SASU009 | ~31 € | White, Black, **Desert Dust** (≈cream), Anthracite, French Navy |
| **Cruiser 2.0** (hoodie eco) | **479** | STSU177 | ~26 € | White, Black, Desert Dust, French Navy |
| **Vintage Creator 2.0** | **1472** | SATU041 | ~17,25 € | G. Dyed Stone, Misty Grey, Kaffa Coffee, etc. |

⚠️ "Vintage White" n'existe pas comme couleur dans Stanley/Stella. **Desert Dust** est le proche pour cream off-white (testé visuellement, beige chaud).

## Mugs

| Printful base | product_id | Coût UE |
|---|---|---|
| **11oz White Glossy Mug** | **19** | ~5,50 € (11 oz vid 1320) |
| **11oz Black Glossy Mug** | **300** | ~7,20 € (11 oz vid 9323) |
| 15oz disponibles aussi mais plus chers et moins demandés |  |  |

## Print specs

- Tee chest / Hoodie chest / back : 4500 × 5400 px (15" × 18" @ 300 DPI)
- Tee hem (ourlet bas) : 4500 × 1200 px (15" × 4")
- Mug side print : 1200 × 1050 px (4" × 3.5")
- Mug wrap (full surround) : 2475 × 1050 px (8.25" × 3.5")
- Format : **PNG transparent (RGBA)**, pas JPG

Génère via `scripts/generate-print-files.py` (PIL + Google Fonts).

## Workflow UI Printful (par produit)

1. Stores → <ton store> → Sync products → **Add product**
2. **Sync existing products from Shopify** → sélectionne le produit Shopify
3. **Choose Printful product** → recherche le `product_id` ci-dessus, sélectionne la couleur
4. **Variants** : Printful matche les variantes Shopify automatiquement par taille
5. **Upload print file** : drag le PNG depuis `<project>/store/products/designs/print/<slug>.png`
6. **Adjust placement** : centre poitrine / hem / wrap selon le design
7. **Submit and sync**

Total ~1 min par produit, ~10 min pour 10 produits.

⚠️ La création de sync products via API Printful est bloquée pour les stores type "shopify" (POST /sync/products → 405). L'UI est obligatoire pour la création initiale. Une fois créés, l'API permet `PUT /sync/products/<id>` pour les updates.
