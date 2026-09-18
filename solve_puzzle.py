#!/usr/bin/env python3
"""
Rivest-Shamir-Wagner time-lock puzzle solver.

Recovers the plaintext by performing t sequential modular squarings
(no shortcut -- this is the whole point). Run this with a fast
Python (PyPy recommended) or port the squaring loop to C/GMP for speed.

Usage:
    python3 solve_puzzle.py puzzle.json
"""
import hashlib
import json
import sys
import time


def keystream(key_int, length):
    key_bytes = key_int.to_bytes((key_int.bit_length() + 7) // 8, 'big')
    out = b''
    counter = 0
    while len(out) < length:
        out += hashlib.sha256(key_bytes + counter.to_bytes(4, 'big')).digest()
        counter += 1
    return out[:length]


def solve(puzzle_path):
    with open(puzzle_path) as f:
        puzzle = json.load(f)

    n = int(puzzle["n"])
    t = puzzle["t"]
    ciphertext = bytes.fromhex(puzzle["ciphertext_hex"])
    plaintext_len = puzzle["plaintext_length"]

    print(f"Solving: {t:,} sequential squarings mod a {n.bit_length()}-bit number.")
    print("This is intentionally slow -- there is no shortcut without the factors of n.")

    a = 2
    start = time.time()
    report_every = max(t // 100, 1)
    for i in range(t):
        a = (a * a) % n
        if i % report_every == 0 and i > 0:
            elapsed = time.time() - start
            frac = i / t
            eta = elapsed / frac - elapsed
            print(f"  {frac*100:5.1f}%  elapsed={elapsed:,.0f}s  eta={eta:,.0f}s", end="\r")

    K = a
    print("\nDone squaring. Deriving key and decrypting...")

    ks = keystream(K, plaintext_len)
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, ks))

    print("\n--- Recovered text ---\n")
    print(plaintext.decode('utf-8', errors='replace'))

    with open("recovered.txt", "wb") as f:
        f.write(plaintext)
    print("\n(Also written to recovered.txt)")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "puzzle.json"
    solve(path)
