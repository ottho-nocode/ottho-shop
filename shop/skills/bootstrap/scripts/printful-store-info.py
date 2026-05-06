#!/usr/bin/env python3
"""
Récupère les infos store Printful via API + audit la connectivité.

Usage:
  PF_TOKEN=... python3 printful-store-info.py
  → imprime store_id, name, type (shopify/manual_order/etc.) + sync products count

Préreq:
  - Token API Printful Private (créé sur https://developers.printful.com/)
  - Pour les stores type "shopify", le store doit déjà être lié via l'app Shopify
"""
import json
import os
import sys
import urllib.error
import urllib.request

PF_TOKEN = os.environ.get("PF_TOKEN")
if not PF_TOKEN:
    sys.exit("PF_TOKEN required")

API = "https://api.printful.com"


def get(path):
    req = urllib.request.Request(
        f"{API}{path}",
        headers={"Authorization": f"Bearer {PF_TOKEN}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode("utf-8", errors="ignore")}


# 1. Liste les stores du compte (v2 endpoint)
print("=== Stores ===")
stores = get("/v2/stores")
for s in stores.get("data", []):
    print(f"  store_id={s['id']:10d} | type={s['type']:12s} | {s['name']}")

# 2. Sync products
print("\n=== Sync products ===")
sync = get("/v2/sync-products")
total = sync.get("paging", {}).get("total", 0)
print(f"  Total sync products : {total}")
for sp in sync.get("data", [])[:10]:
    print(f"  #{sp['id']} | {sp.get('name', 'untitled')}")

# 3. Si store type=shopify, signaler le platform limit
print("\n=== Platform limits ===")
for s in stores.get("data", []):
    if s["type"] == "shopify":
        print(f"  Store '{s['name']}' est de type 'shopify'.")
        print(f"  → POST /sync/products bloqué (UI obligatoire pour création)")
        print(f"  → API permet : GET /v2/sync-products, PUT /sync/products/<id>, GET/POST /orders")
        print(f"  → Workaround : pré-uploader les print files sur Shopify CDN, puis drag-drop dans Printful UI")
