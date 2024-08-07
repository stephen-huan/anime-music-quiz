import math


def gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> tuple:
    """Returns (gcd(a, b), x, y) such that ax + by = gcd(a, b)."""
    x, xp = 0, 1
    y, yp = 1, 0
    r, rp = b, a

    while r != 0:
        q = rp // r
        rp, r = r, rp - q * r
        xp, x = x, xp - q * x
        yp, y = y, yp - q * y

    return rp, xp, yp


def inv(x: int, m: int) -> int:
    """Returns the inverse y such that xy mod m = 1."""
    return extended_gcd(x, m)[1] % m


def mod_exp(b: int, e: int, m: int) -> int:
    """Returns b^e % m"""
    if m == 1:
        return 0
    rtn = 1
    b %= m
    while e > 0:
        # bit on in the binary representation of the exponent
        if e & 1 == 1:
            rtn = (rtn * b) % m
        e >>= 1
        b = (b * b) % m
    return rtn


def prime(n: int) -> bool:
    if n == 1 or (n % 2 == 0 and n != 2):
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def find_kp(n: int) -> tuple:
    """Finds the smallest k such that p = kn + 1 is prime.
    pi(n) = n/log n, so the probability of a random number being prime is 1/log n,
    expect to try log n numbers until finding a prime - expected O((sqrt n)(log n)).
    """
    k, p = 1, n + 1
    while not prime(p):
        k += 1
        p += n
    return k, p


def find_generator(n: int, k: int, p: int) -> int:
    """Euler's totient function phi(n) gives the order of a
    modulo multiplicative group mod p.
    phi(p) = p - 1 = kn
    prime factors of kn are 2, maybe k
    expected O(log^8 ish n)
    """
    prime_factors = [2] + ([k] if prime(k) else [])
    for i in range(p):
        # coprime and thus in the group
        if gcd(i, p) == 1:
            if all(
                mod_exp(i, k * n // factor, p) != 1 for factor in prime_factors
            ):
                return i
    raise ValueError(f"{p} does not have a primitive root.")


def find_wp(n: int) -> tuple:
    """Returns w, the principal nth root of unity
    and p, the prime determining the mod."""
    k, p = find_kp(n)
    g = find_generator(n, k, p)
    return mod_exp(g, k, p), p


def get_w(w: int, N: int, n: int, p: int) -> int:
    """Returns w, the principal nth root of unity for n."""
    return mod_exp(w, 1 << (N - n + 1), p)


def rev_increment(c: int, m: int) -> int:
    """Increments a reverse binary counter."""
    i = 1 << (m - 1)
    while c & i > 0:
        c ^= i
        i >>= 1
    return c ^ i


def bit_rev_copy(a: list) -> list:
    """Constructs an initial order from a by reversing the bits of the index."""
    n, m = len(a), len(a).bit_length() - 1
    A = [0] * n
    c = 0
    for i in range(n):
        A[c] = a[i]
        c = rev_increment(c, m)
    return A


def int_fft(a: list, wn: int, p: int) -> list:
    """Computes the DFT iteratively with modulo instead of complex numbers."""
    n, lgn = len(a), len(a).bit_length()
    A = bit_rev_copy(a)
    for s in range(1, lgn):
        m = 1 << s
        wm = mod_exp(wn, 1 << (lgn - s - 1), p)
        for k in range(0, n, m):
            w = 1
            for j in range(m >> 1):
                t = w * A[k + j + (m >> 1)]
                u = A[k + j]
                A[k + j] = (u + t) % p
                A[k + j + (m >> 1)] = (u - t) % p
                w = (w * wm) % p
    return A


def inv_int_fft(a: list, wn: int, p: int) -> list:
    """Computes the inverse DFT of a."""
    wn, n1 = inv(wn, p), inv(len(a), p)
    return [(x * n1) % p for x in int_fft(a, wn, p)]


def mirror(a: list) -> list:
    """Mirrors a such that the resulting list has a length which is a power of 2."""
    n, np = len(a), 1 << math.ceil(math.log2(len(a)))
    a += [0] * (np - n)
    # for i in range(np - n):
    #     a[n + i] = a[n - i - 2]
    return a


def poly_mult(a: list, b: list, w: int, p: int) -> list:
    """Multiplies two polynomials via the modular FFT."""
    n = max(len(a), len(b))
    # make both lists the same size and degree bound 2n instead of n
    ap = mirror(a + [0] * (n - len(a)) + [0] * n)
    bp = mirror(b + [0] * (n - len(b)) + [0] * n)
    w = get_w(w, N, len(ap).bit_length(), p)
    ap, bp = int_fft(ap, w, p), int_fft(bp, w, p)
    return inv_int_fft([ap[i] * bp[i] % p for i in range(len(ap))], w, p)


# N = 51
N = 30
# w, p = find_wp(1 << N)
# w, p = 4782969, 31525197391593473
w, p = 125, 3221225473

fft = lambda a, b: poly_mult(a, b, w, p)  # noqa: E731
