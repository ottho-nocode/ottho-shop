#!/usr/bin/env python3
"""
Configure les zones de livraison via Shopify Admin GraphQL.

⚠️ PIÈGE GRAPHQL : zonesToDelete est au TOP-LEVEL de DeliveryProfileInput.
Si tu le mets dans locationGroupsToUpdate.zonesToDelete (intuition logique),
GraphQL accepte la mutation, retourne userErrors:[] (success), mais ne supprime rien.

Toujours re-query les zones après mutation pour vérifier l'effet réel.

Usage :
  TOKEN=shpat_... DOMAIN=... python3 delivery-profile-update.py

Préreq :
  - Token avec scope write_shipping (Custom App, pas le CLI token)

Customise les ZONES ci-dessous selon ton modèle business.
"""
import json
import os
import sys
import urllib.request

TOKEN = os.environ.get("TOKEN")
DOMAIN = os.environ.get("DOMAIN")
if not TOKEN or not DOMAIN:
    sys.exit("TOKEN + DOMAIN required")

API = f"https://{DOMAIN}/admin/api/2025-10/graphql.json"


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


# 1. Récupérer le profil + location group existants
profile_query = """
{
  deliveryProfiles(first: 5) {
    nodes {
      id
      name
      profileLocationGroups {
        locationGroup { id }
        locationGroupZones(first: 10) {
          nodes { zone { id name } }
        }
      }
    }
  }
}
"""
res = gql(profile_query)
profile = res["data"]["deliveryProfiles"]["nodes"][0]
profile_id = profile["id"]
loc_group_id = profile["profileLocationGroups"][0]["locationGroup"]["id"]
existing_zones = [z["zone"]["id"] for z in profile["profileLocationGroups"][0]["locationGroupZones"]["nodes"]]

print(f"Profile: {profile_id}")
print(f"Location Group: {loc_group_id}")
print(f"Zones existantes: {len(existing_zones)}")

# 2. Définir les nouvelles zones (à customiser selon ton business)
NEW_ZONES = [
    {
        "name": "France",
        "countries": [{"code": "FR", "includeAllProvinces": True}],
        "methodDefinitionsToCreate": [
            {
                "name": "Standard",
                "rateDefinition": {"price": {"amount": "4.99", "currencyCode": "EUR"}},
            }
        ],
    },
    {
        "name": "Union européenne (hors France)",
        "countries": [
            {"code": "DE"}, {"code": "ES"}, {"code": "IT"}, {"code": "BE"},
            {"code": "NL"}, {"code": "PT"}, {"code": "AT"}, {"code": "IE"},
        ],
        "methodDefinitionsToCreate": [
            {
                "name": "Standard UE",
                "rateDefinition": {"price": {"amount": "8.99", "currencyCode": "EUR"}},
            }
        ],
    },
]

# 3. Mutation deliveryProfileUpdate
# zonesToDelete au TOP-LEVEL, locationGroupsToUpdate.zonesToCreate niché
update_mutation = """
mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile, leaveLegacyModeProfiles: false) {
    profile { id }
    userErrors { field message }
  }
}
"""
variables = {
    "id": profile_id,
    "profile": {
        "zonesToDelete": existing_zones,  # TOP-LEVEL — pas dans locationGroupsToUpdate
        "locationGroupsToUpdate": [{
            "id": loc_group_id,
            "zonesToCreate": NEW_ZONES,
        }],
    },
}

print(f"\nUpdate en cours (delete {len(existing_zones)} + create {len(NEW_ZONES)})...")
res = gql(update_mutation, variables)
errs = res.get("data", {}).get("deliveryProfileUpdate", {}).get("userErrors", [])
if errs:
    print(f"⚠️ userErrors: {errs}")
else:
    print("Mutation OK (userErrors:[]).")

# 4. ⚠️ TOUJOURS RE-QUERY pour vérifier l'effet réel
print("\nRe-query du profile pour vérification...")
res = gql(profile_query)
new_profile = res["data"]["deliveryProfiles"]["nodes"][0]
new_zones = [z["zone"] for z in new_profile["profileLocationGroups"][0]["locationGroupZones"]["nodes"]]
print(f"Zones après update : {len(new_zones)}")
for z in new_zones:
    print(f"  - {z['name']} ({z['id']})")

if len(new_zones) == len(NEW_ZONES):
    print("\n✅ Configuration shipping appliquée correctement.")
else:
    print(f"\n⚠️ Mismatch : attendu {len(NEW_ZONES)} zones, trouvé {len(new_zones)}. Suspecter un silent fail GraphQL.")
