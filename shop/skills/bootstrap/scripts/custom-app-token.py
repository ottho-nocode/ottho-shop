#!/usr/bin/env python3
"""
Génère un Shopify Admin API token depuis un Custom App via OAuth client_credentials grant.

Préreq :
  - Custom App créé via admin Shopify (Settings → Apps and sales channels → Develop apps → Create app)
  - Scopes accordés : write_content, write_publications, write_translations, write_shipping
  - Client ID + Client Secret notés

Usage :
  CLIENT_ID=<your_client_id> CLIENT_SECRET=<your_client_secret> \
  DOMAIN=ma-boutique.myshopify.com python3 custom-app-token.py
  → imprime le token shpat_*

Doc : https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets
"""
import json
import os
import sys
import urllib.request

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
DOMAIN = os.environ.get("DOMAIN")

if not all([CLIENT_ID, CLIENT_SECRET, DOMAIN]):
    sys.exit("CLIENT_ID, CLIENT_SECRET, DOMAIN required")

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

with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read())

if "access_token" not in data:
    sys.exit(f"Pas de access_token dans la réponse : {data}")

print(data["access_token"])
