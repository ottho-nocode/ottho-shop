#!/usr/bin/env python3
"""
Vérifie que l'app Printful est bien installée sur ottho-merch et liste l'état
des 10 produits côté Shopify (vendor, metafields Printful, scope sync).

Usage: python3 store/scripts/verify-printful-link.py
"""
import json
import sys
import urllib.request
from pathlib import Path

DOMAIN = "ottho-merch.myshopify.com"
API = f"https://{DOMAIN}/admin/api/2025-10/graphql.json"
CLI_CONFIG = Path.home() / "Library/Preferences/shopify-cli-kit-nodejs/config.json"


def load_cli_token():
    data = json.loads(CLI_CONFIG.read_text())
    session = json.loads(data["sessionStore"])
    for acct in session.get("accounts.shopify.com", {}).values():
        for key, app in acct.get("applications", {}).items():
            if key.startswith(f"{DOMAIN}-") and "accessToken" in app:
                return app["accessToken"]
    sys.exit("CLI token not found. Run `shopify theme dev` once first.")


def gql(token, q, v=None):
    payload = json.dumps({"query": q, "variables": v or {}}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        API,
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


TOKEN = load_cli_token()

# 1) Liste des apps installées (filtre celles avec "printful" ou "Printful" dans le nom)
APPS_QUERY = """
{
  appInstallations(first: 50) {
    nodes {
      app {
        title
        handle
      }
      accessScopes { handle }
    }
  }
}
"""

# 2) Produits avec metafields (Printful pose des metafields sur les produits sync)
PRODUCTS_QUERY = """
{
  products(first: 15) {
    nodes {
      title
      handle
      vendor
      status
      metafields(first: 20) {
        nodes {
          namespace
          key
          value
        }
      }
    }
  }
}
"""


def main():
    print("=" * 60)
    print("VÉRIF APP PRINTFUL")
    print("=" * 60)

    apps = gql(TOKEN, APPS_QUERY)
    if "errors" in apps:
        print(f"ERREUR appInstallations: {apps['errors']}")
        return

    nodes = apps["data"]["appInstallations"]["nodes"]
    printful_apps = [a for a in nodes if "printful" in a["app"]["handle"].lower() or "printful" in a["app"]["title"].lower()]

    if not printful_apps:
        print("❌ Printful n'est PAS installé sur la boutique.")
        print(f"   Apps installées : {[a['app']['title'] for a in nodes]}")
    else:
        for a in printful_apps:
            print(f"✅ Printful installé : {a['app']['title']} (handle: {a['app']['handle']})")
            print(f"   Scopes accordés : {[s['handle'] for s in a['accessScopes']]}")

    print()
    print("=" * 60)
    print("ÉTAT DES 10 PRODUITS (vendor + metafields Printful)")
    print("=" * 60)

    prods = gql(TOKEN, PRODUCTS_QUERY)
    if "errors" in prods:
        print(f"ERREUR products: {prods['errors']}")
        return

    products = prods["data"]["products"]["nodes"]
    sync_count = 0
    for p in products:
        printful_metafields = [
            m for m in p["metafields"]["nodes"]
            if "printful" in m["namespace"].lower() or "printful" in m["key"].lower()
        ]
        synced = "✅ SYNC" if printful_metafields else "⏳ pas encore sync"
        if printful_metafields:
            sync_count += 1
        print(f"  {p['handle']:32s} | vendor={p['vendor']:14s} | {synced}")
        for m in printful_metafields:
            v = m["value"][:60] + "..." if len(m["value"]) > 60 else m["value"]
            print(f"      └─ {m['namespace']}.{m['key']} = {v}")

    print()
    print(f"Résumé : {sync_count}/{len(products)} produits liés à Printful.")
    if sync_count == len(products):
        print("🟢 Sync complet, tu peux passer au test order.")
    elif sync_count > 0:
        print("🟡 Sync partiel, finis les produits restants dans Printful → Stores → Sync products.")
    else:
        print("🔴 Aucun produit n'est sync. Va dans Printful → Stores → ottho-merch → Sync products → Add product.")


if __name__ == "__main__":
    main()
