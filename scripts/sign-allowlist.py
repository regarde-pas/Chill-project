#!/usr/bin/env python3
"""Allowlist Generator & Signer for Cinnabar (like xdpdl/cbr-releases).
Produces signed allowlist.json containing authorized machine codes.
"""
import base64
import json
import os
import sys

# Import keygen functions
try:
    from keygen import public_key_from_seed, sign
except ImportError:
    from scripts.keygen import public_key_from_seed, sign


def create_allowlist(codes, seed_b64, key_id="chill1"):
    seed = base64.b64decode(seed_b64)
    
    payload_dict = {"codes": codes}
    payload_json = json.dumps(payload_dict, separators=(', ', ': '))
    payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
    
    # Sign payload bytes
    sig = sign(payload_b64.encode('utf-8'), seed)
    sig_b64 = base64.b64encode(sig).decode('utf-8')
    
    envelope = {
        "key_id": key_id,
        "payload": payload_b64,
        "signature": sig_b64
    }
    return json.dumps(envelope, indent=2)


def main():
    if len(sys.argv) < 3:
        print("Usage: python sign-allowlist.py <PRIVATE_SEED_B64> <CODE1> [CODE2 ...]")
        print("Exemple: python sign-allowlist.py <SEED> 16BD-A905-5B8A-D597 42CB-84E7-F002-A756")
        return

    seed_b64 = sys.argv[1]
    codes = sys.argv[2:]
    result = create_allowlist(codes, seed_b64)
    
    with open("allowlist.json", "w", encoding="utf-8") as f:
        f.write(result)
        
    print("allowlist.json généré avec succès !")
    print(result)


if __name__ == "__main__":
    main()
