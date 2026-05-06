#!/usr/bin/env python3
"""
Upload un fichier binaire vers Shopify CDN via stagedUploadsCreate + S3 PUT.

Workflow :
1. stagedUploadsCreate → URL S3 + parameters
2. PUT le binaire vers S3
3. retourne la resourceUrl publique (utilisable comme src dans articles, products, etc.)

Usage :
  TOKEN=shpat_... DOMAIN=... python3 staged-upload.py <file_path>
  → imprime l'URL publique sur shopify-staged-uploads.storage.googleapis.com
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

TOKEN = os.environ.get("TOKEN")
DOMAIN = os.environ.get("DOMAIN")
if not TOKEN or not DOMAIN:
    sys.exit("TOKEN + DOMAIN required")
if len(sys.argv) < 2:
    sys.exit("Usage: staged-upload.py <file_path>")

fpath = Path(sys.argv[1])
if not fpath.exists():
    sys.exit(f"File not found: {fpath}")

API = f"https://{DOMAIN}/admin/api/2025-10/graphql.json"
MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
}.get(fpath.suffix.lower(), "application/octet-stream")


def gql(q, v=None):
    payload = json.dumps({"query": q, "variables": v or {}}).encode()
    req = urllib.request.Request(
        API,
        data=payload,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


STAGED = """
mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { field message }
  }
}
"""

file_size = fpath.stat().st_size
res = gql(STAGED, {
    "input": [{
        "filename": fpath.name,
        "mimeType": MIME,
        "httpMethod": "PUT",
        "resource": "FILE",
        "fileSize": str(file_size),
    }]
})

target = res["data"]["stagedUploadsCreate"]["stagedTargets"][0]
body = fpath.read_bytes()
req = urllib.request.Request(
    target["url"],
    data=body,
    headers={"Content-Type": MIME, "Content-Length": str(len(body))},
    method="PUT",
)
with urllib.request.urlopen(req, timeout=120) as resp:
    if resp.status not in (200, 201, 204):
        sys.exit(f"PUT échoué : {resp.status}")

print(target["resourceUrl"])
