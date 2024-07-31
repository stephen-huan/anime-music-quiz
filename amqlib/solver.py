"""
Problem:
----------
https://animemusicquiz.com/
Given target song T try to identify it from a database of songs D
Abstraction: song is a list of ints (less of an abstraction and more of a fact)

suppose you have an array A of ints of size N
and an array B of size M where M >= N

find the offset i (0 <= i <= M - N)
such that it minimizes \sum^{N - 1}_{j = 0} |A_j - B_{j + i}|
(intuitively, the sum of pointwise differences between the waveform of the songs)
----------
observation #1:
this seems like a two pointer/sliding window problem
(compute the value for a certain window at start, end then compute the delta
for the shifted window start + 1, end + 1)

observation #2:
change |x - y| to (x - y)^2 because the latter is easier to work with
expanding yields x^2 - 2xy + y^2

tracking over the window shifts (s, e) -> (s + 1, e + 1):
sum of x^2 doesn't change  (dx^2 = 0)
sum of y^2 should increase from the new element and decrease from losing the start
(dy^2 = y_{e + 1} - y{s})
how does -2xy change??

observation #3:
this seems very similar to the discrete convolution:
https://en.wikipedia.org/wiki/Convolution
Discrete convolution equal to polynomial multiplication
Calculated in n log n (n = degree of the polynomial) via FFT

construct a polynomial from A
P1(x) = A_0 + A_1 x + A_2 x^2 + ... + A_N x^N

construct a polynomial from B (IN REVERSE)
P2(x) = B_M + B_{M - 1} x + ... + B_0 x^M

why? when computing P1*P2, we're going to look at the coefficients of the polynomial
the coefficients are determined by the degree of the term they're attached to,
e.g. if we constructed P2 like P1 it would look like:
P1*P2 = (A_0 B_0) + (A_0 B_1 + A_1 B_0) x + (A_0 B_2 + A_1 B_1 + A_2 B_0) x^2
for a A_i B_j term, it's attached to x^{i + j} (obviously)
what we WANT is
A_0 B_0 + A_1 B_1 + A_2 B_2
A_0 B_1 + A_1 B_2 + A_2 B_3
A_0 B_2 + A_1 B_3 + A_2 B_4
...
what we HAVE is when i increases, j DECREASES
thus if we reverse the polynomial, j increases as i increases, in line
we can just discard the first N - 1 and the last N - 1 terms,
and read the dot products (the xy we're trying to compute) straight off the coefficients
----------
Example #1:

A = 1 3 2
B = 2 1 4 3 5 2

i = 0: [1, 3, 2]*[2, 1, 4] = 13
i = 1: [1, 3, 2]*[1, 4, 3] = 19
i = 2: [1, 3, 2]*[4, 3, 5] = 23
i = 3: [1, 3, 2]*[3, 5, 2] = 22

compute (1 + 3x + 2x^2)(2 + 5x + 3x^2 + 4x^3 + x^4 + 2x^5)
= 4x^7 + 8x^6 + 13x^5 + 19x^4 + 23x^3 + 22x^2 + 11x + 2
disregarding the last 2 and first 2 terms (they're "incomplete")
= 13x^5 + 19x^4 + 23x^3 + 22x^2 = [13 19 23 22]
----------
What about volume?
Suppose the target song is softer or louder than the songs in our database
abstract away our previous stuff as f(x) - what we computed before was
x = 0, aka no volume changes to the target song
if x = 5, think of that as adding 5 to each number in the target song
and recomputing out DFT

Assume the function is convex (questionable) and treat it as 1D convex min
https://ljk.imag.fr/membres/Anatoli.Iouditski/cours/convex/chapitre_22.pdf
1D convex function optimization - runs in O(log(V/epsilon))
where V is the maximum value of f and epsilon is the wanted precision
V ~= 2^16, epsilon = 1
"""

import subprocess

from amqlib import PATH

from .fft import fft

PATH = PATH[0]


def load_arrays(fname: str) -> tuple:
    """Gets arrays from a file."""
    with open(fname) as f:
        f.readline()
        l1 = list(map(int, f.readline().split()))
        f.readline()
        return l1, list(map(int, f.readline().split()))


def save_arrays(fname: str, l1: list, l2: list) -> None:
    """Dumps arrays to a file."""
    with open(fname, "w") as f:
        f.write(str(len(l1)) + "\n")
        f.write(" ".join(map(str, l1)) + "\n")
        f.write(str(len(l2)) + "\n")
        f.write(" ".join(map(str, l2)) + "\n")


def min_offset(a: list, b: list) -> tuple:
    """Computes the offset that minimizes the l2 norm."""
    N, M = len(a), len(b)
    p = fft(a[::-1], b)[N - 1 :]
    x2, xy, y2 = (
        sum(x * x for x in a),
        p[0],
        sum(b[i] * b[i] for i in range(N)),
    )
    best, l2 = 0, -2 * xy + y2
    for i in range(1, M - N + 1):
        y2 += b[N - 1 + i] * b[N - 1 + i] - b[i - 1] * b[i - 1]
        xy = p[i]
        d = -2 * xy + y2
        if d < l2:
            best, l2 = i, d
    return best, x2 + l2


def max_cosine(a: list, b: list) -> tuple:
    """Computes the offset that maximizes the cosine similarity."""
    N, M = len(a), len(b)
    p = fft(a[::-1], b)[N - 1 :]
    x2, xy, y2 = (
        sum(x * x for x in a),
        p[0],
        sum(b[i] * b[i] for i in range(N)),
    )
    best, cos = 0, xy / y2
    for i in range(1, M - N + 1):
        y2 += b[N - 1 + i] * b[N - 1 + i] - b[i - 1] * b[i - 1]
        xy = p[i]
        d = xy / y2
        if d > cos:
            best, cos = i, d
    return best, 1 - cos / x2  # loss means lower is better


def solve(a: list, b: list) -> tuple:
    """Same thing as min_offset, but with a cpp executable."""
    save_arrays(f"{PATH}/song.in", a, b)
    subprocess.call(["./a.out"], cwd=PATH)
    with open(f"{PATH}/song.out") as f:
        return tuple(map(int, f.readline().split()))


def loss_func(a, b):
    return lambda v: solve((v * a).astype(int), b)[-1]


def one_d_min(f, a, d, epsilon=10**-2):
    while abs(a - d) > epsilon:
        t = (d - a) / 3
        b = a + t
        c = a + 2 * t
        if f(b) < f(c):
            a, d = a, c
        else:
            a, d = b, d
    return (a + d) / 2


if __name__ == "__main__":
    a, b = load_arrays("song.in")
    # print(min_offset(a, b))
    print(solve(a, b))
