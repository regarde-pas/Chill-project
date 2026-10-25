#!/usr/bin/env python3
"""Pure-Python RFC 8032 Ed25519 Key Generator for Cinnabar Update Signing.
No external dependencies required (only standard library hashlib and secrets).
"""
import base64
import hashlib
import os
import secrets
import sys

# RFC 8032 Ed25519 parameters
P = 2**255 - 19
A = -1
D = (-121665 * pow(121666, P - 2, P)) % P
Q = 2**252 + 27742317777372353535851937790883648493


def inv(x):
    return pow(x, P - 2, P)


# Base point B = (Bx, By)
By = (4 * inv(5)) % P
# Solve Bx^2 = (By^2 - 1) / (D*By^2 + 1)
u = (By * By - 1) % P
v = (D * By * By + 1) % P
x2 = (u * inv(v)) % P
Bx = pow(x2, (P + 3) // 8, P)
if (Bx * Bx - x2) % P != 0:
    Bx = (Bx * pow(2, (P - 1) // 4, P)) % P
if Bx % 2 != 0:
    Bx = P - Bx
B = (Bx, By)


def point_add(P1, P2):
    x1, y1 = P1
    x2, y2 = P2
    x3 = (x1 * y2 + y1 * x2) * inv(1 + D * x1 * x2 * y1 * y2) % P
    y3 = (y1 * y2 - A * x1 * x2) * inv(1 - D * x1 * x2 * y1 * y2) % P
    return (x3, y3)


def point_mul(s, P1):
    R = (0, 1)  # neutral element
    Q = P1
    while s > 0:
        if s & 1:
            R = point_add(R, Q)
        Q = point_add(Q, Q)
        s >>= 1
    return R


def public_key_from_seed(seed: bytes) -> bytes:
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    A_point = point_mul(a, B)
    # Encode point
    x, y = A_point
    s = bytearray(y.to_bytes(32, "little"))
    if x & 1:
        s[31] |= 0x80
    return bytes(s)


def sign(message: bytes, seed: bytes) -> bytes:
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    pub = public_key_from_seed(seed)
    
    # r = SHA-512(h[32:] + message) mod L
    L = 2**252 + 27742317777372353535851937790883648493
    prefix = h[32:]
    r_hash = hashlib.sha512(prefix + message).digest()
    r = int.from_bytes(r_hash, "little") % L
    
    R_point = point_mul(r, B)
    rx, ry = R_point
    R_bytes = bytearray(ry.to_bytes(32, "little"))
    if rx & 1:
        R_bytes[31] |= 0x80
    R_bytes = bytes(R_bytes)
    
    # k = SHA-512(R + pub + message) mod L
    k_hash = hashlib.sha512(R_bytes + pub + message).digest()
    k = int.from_bytes(k_hash, "little") % L
    
    S = (r + k * a) % L
    S_bytes = S.to_bytes(32, "little")
    return R_bytes + S_bytes


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "keygen":
        seed = secrets.token_bytes(32)
        pub = public_key_from_seed(seed)
        seed_b64 = base64.b64encode(seed).decode("utf-8")
        pub_b64 = base64.b64encode(pub).decode("utf-8")
        print("=== CINNABAR ED25519 KEYPAIR ===")
        print(f"Key ID: chill1")
        print(f"Public key (base64): {pub_b64}")
        print(f"Private seed (base64): {seed_b64}")
        print("\n--- GitHub Configuration ---")
        print(f"1. In GitHub Repository -> Settings -> Secrets and variables -> Actions -> Variables:")
        print(f"   Name:  UPDATE_TRUSTED_KEYS")
        print(f"   Value: chill1:{pub_b64}")
        print(f"\n2. In GitHub Repository -> Settings -> Secrets and variables -> Actions -> Secrets:")
        print(f"   Name:  CINNABAR_UPDATE_SIGNING_KEY")
        print(f"   Value: {seed_b64}")
        return

    print("Usage: python keygen.py keygen")


if __name__ == "__main__":
    main()
