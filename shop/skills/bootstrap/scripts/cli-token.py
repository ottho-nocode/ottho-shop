#!/usr/bin/env python3
"""
Extrait le token OAuth Shopify caché par `shopify theme dev`.

Usage:
  DOMAIN=ma-boutique.myshopify.com python3 cli-token.py
  → imprime le token (à utiliser comme Authorization: Bearer <token>)

Couvre les scopes par défaut :
  read/write_themes, read/write_products, read/write_files,
  read/write_translations, read/write_orders, read/write_customers, etc.

Ne couvre PAS :
  write_content, write_publications, write_shipping
  → pour ceux-là, utiliser custom-app-token.py
"""
import json
import os
import sys
from pathlib import Path

DOMAIN = os.environ.get("DOMAIN")
if not DOMAIN:
    sys.exit("DOMAIN required (e.g. ma-boutique.myshopify.com)")

CLI_CONFIG = Path.home() / "Library/Preferences/shopify-cli-kit-nodejs/config.json"
if not CLI_CONFIG.exists():
    sys.exit(f"CLI config not found at {CLI_CONFIG}. Lance `shopify theme dev` au moins une fois.")

data = json.loads(CLI_CONFIG.read_text())
session = json.loads(data["sessionStore"])
for acct in session.get("accounts.shopify.com", {}).values():
    for key, app in acct.get("applications", {}).items():
        if key.startswith(f"{DOMAIN}-") and "accessToken" in app:
            print(app["accessToken"])
            sys.exit(0)

sys.exit(f"Pas de token trouvé pour {DOMAIN}. Vérifier que `shopify theme dev` a tourné une fois sur cette boutique.")
