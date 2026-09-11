# Random Number Generator: LCG + OS Entropy

## 1. LCG — Linear Congruential Generator

An **LCG** is a deterministic pseudo-random number generator.

### Formula

```text
X(n+1) = (a × X(n) + c) mod m
```

Where:

* `X` → current state
* `a` → multiplier
* `c` → increment
* `m` → modulus
* `X₀` → seed

### Python

```python
class LCG:
    def __init__(self, seed):
        self.state = seed

    def next(self):
        self.state = (
            1664525 * self.state + 1013904223
        ) % (2 ** 32)

        return self.state

    def randint(self, low, high):
        return low + self.next() % (high - low + 1)


rng = LCG(seed=42)

for _ in range(5):
    print(rng.randint(1, 100))
```

### Characteristics

```text
Fast          → Yes
Deterministic → Yes
Reproducible  → Yes
Unpredictable → No
Secure        → No
```

Same seed → same sequence:

```text
seed = 42
   ↓
X1 → X2 → X3 → X4 → ...
```

**Use:** simulations, testing, simple applications.

---

# 2. OS Entropy

For security-sensitive randomness, start with randomness supplied by the **operating system**.

Linux exposes a CSPRNG through:

```text
/dev/urandom
```

### Get random bytes

```python
with open("/dev/urandom", "rb") as f:
    data = f.read(32)

print(data.hex())
```

Example:

```text
OS
 ↓
/dev/urandom
 ↓
32 random bytes
```

These bytes are generated using the OS's cryptographically secure random subsystem.

---

# 3. Generate a Random Integer

```python
import os

def random_uint32():
    data = os.urandom(4)
    return int.from_bytes(data, "big")


print(random_uint32())
```

`os.urandom()` is preferable to manually reading `/dev/urandom` because Python provides the OS CSPRNG through this API.

---

# 4. Random Integer in a Range

A simple version:

```python
import os

def randint(low, high):
    value = int.from_bytes(os.urandom(8), "big")
    return low + value % (high - low + 1)


print(randint(1, 100))
```

However, `%` can introduce **modulo bias**.

For production code, use:

```python
import secrets

print(secrets.randbelow(100) + 1)
```

---

# 5. LCG vs OS Entropy

| Property                 | LCG       | OS Entropy / CSPRNG           |
| ------------------------ | --------- | ----------------------------- |
| Deterministic            | Yes       | No from user's perspective    |
| Seed required            | Yes       | OS handles entropy            |
| Reproducible             | Yes       | No                            |
| Predictable              | Yes       | Designed to resist prediction |
| Speed                    | Very fast | Fast                          |
| Security                 | ❌         | ✅                             |
| Use for passwords/tokens | ❌         | ✅                             |

## Mental Model

```text
LCG

Seed
 ↓
Mathematical formula
 ↓
X1 → X2 → X3 → X4
       ↑
  predictable
```

```text
OS CSPRNG

OS entropy
    ↓
Cryptographic state
    ↓
CSPRNG
    ↓
Random bytes
    ↓
Random integers
```

## Key Takeaway

**LCG creates pseudo-randomness from a deterministic formula.**

**OS entropy provides unpredictable input to a cryptographic random generator.**

For real applications:

```python
import secrets

number = secrets.randbelow(100) + 1
```

Use **LCG for learning/simulation** and **`secrets`/OS CSPRNG for security**.