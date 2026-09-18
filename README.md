# opseclevel

# Time-Lock Puzzle — Solver's Guide

This is a **Rivest–Shamir–Wagner (RSW) time-lock puzzle**, as described in their 1996 paper
*"Time-lock Puzzles and Timed-release Crypto."* It locks a short text behind a computation
that requires real, unavoidable wall-clock time to solve — there is no shortcut, no key to
find, and no factorization to recover. You just have to do the work.

All public parameters are in `puzzle.json`.

## The construction

Let $n$, $t$, and $C$ (ciphertext) be the values in `puzzle.json`.

### Step 1 — Grind the squaring chain

$$a_0 = 2$$
$$a_{i+1} \equiv a_i^2 \pmod{n}, \quad i = 0, 1, \dots, t-1$$
$$K \equiv a_t \pmod{n}$$

This is **t sequential modular squarings**, starting from 2. Each step depends on the
previous one — it cannot be parallelized across cores. The only way to go faster is to make
each individual squaring faster (e.g. a well-optimized bignum library like GMP, or dedicated
hardware). There is no way to skip ahead unless you know the factorization of $n$, which
only the puzzle's creator had, and which is not published.

### Step 2 — Derive the keystream

Once you have $K$, take its big-endian byte representation, call it $b(K)$. Build a
keystream in SHA-256 counter mode:

$$\text{ks}_j = \text{SHA-256}\big(b(K) \,\|\, j\big), \quad j = 0, 1, 2, \dots$$

where $j$ is a 4-byte big-endian counter, and $\|$ is concatenation. Concatenate blocks
until you have at least as many bytes as the ciphertext, then truncate to that length.

### Step 3 — Recover the plaintext

XOR the ciphertext against the keystream, byte by byte:

$$P_i = C_i \oplus \text{KS}_i$$

Decode $P$ as UTF-8. That's the message.

## Practical notes for implementers

- **Language matters.** Pure Python is slow for this; expect it to run orders of magnitude
  longer than intended. Use PyPy, or port the squaring loop to C with GMP, if you want the
  puzzle's timing estimate to hold.
- **Checkpoint your progress.** If you're running this over a long period, periodically save
  the current $(i, a_i)$ pair so a crash or reboot doesn't cost you from the beginning.
- **No trick, no login, no factorization attack.** $n$ is a product of two large primes
  whose factors were destroyed by the puzzle's creator. This is a pure time-delay
  mechanism, not a cryptographic riddle with a clever shortcut.

— **Also there is no financial incentive here.Take note**
## Reference

Rivest, R., Shamir, A., and Wagner, D. (1996). *Time-lock Puzzles and Timed-release
Crypto.* MIT LCS Technical Report.
