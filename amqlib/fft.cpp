#include <bits/stdc++.h>
using namespace std;

// renames
#define add insert
#define append push_back
#define pop pop_back
#define popleft pop_front
#define list vector
#define dict unordered_map
#define mp make_pair
#define fi first
#define se second
#define mt make_tuple
#define last back()
#define el '\n'
#define arg const &
#define elif else if
#define True true
#define False false
#define None void

// change to long if you run out of memory
typedef unsigned long long ll;
typedef string str;
typedef unsigned char uchar;
typedef list<ll> li;
typedef list<li> mat;
typedef dict<ll, ll> di;
typedef unordered_set<ll> st;
typedef dict<ll, li> adj;
typedef pair<ll, ll> pi;

// loops
#define For(x, n) for (auto &x : n)
// __VA_ARGS__ expands to an argument list, causing GET_MACRO to choose a different macro
#define GET_MACRO(_1, _2, _3, _4, NAME, ...) NAME
#define range(...) GET_MACRO(__VA_ARGS__, RANGE4, RANGE3, RANGE2)(__VA_ARGS__)
#define RANGE2(i, n) for (ll i = 0; i < n; i++)
#define RANGE3(i, start, n) for (ll i = start; i < n; i++)
// account for negative increment
#define RANGE4(i, start, n, inc) for (ll i = start; ((inc > 0) ? 1 : -1)*i < ((inc > 0) ? 1 : -1)*n; i += inc)

// input-output (IO)
#define print(x) cout << x << '\n'
#define write(x) fout << x << '\n'
#define input(x) cin >> x
#define read(x) fin >> x
#define printnum(x) cout << fixed << setprecision(17) << x << '\n';

// misc
#define len(l) ((int) l.size())
#define in(x, s) (s.find(x) != s.end())

// infinity, but not really
const ll inf = std::numeric_limits<ll>::max() >> 1;

#define M 30
#define W 125
#define P 3221225473

// #define MAXN 100001
// ll dp[MAXN];

inline
ll msb(ll a) {
  return 63 - __builtin_clzll(a);
}

ll gcd(ll a, ll b) {
  ll t;
  while (b != 0) {
    t = a;
    a = b;
    b = t % b;
  }
  return a;
}

tuple<ll, ll, ll> extended_gcd(ll a, ll b) {
  ll x, xp, y, yp, r, rp, q, tx, ty, tr;
  x = 0; xp = 1;
  y = 1; yp = 0;
  r = b; rp = a;

  while (r != 0) {
    q = rp/r;
    tx = x; ty = y; tr = r;
    r = rp - q*r; rp = tr;
    x = xp - q*x; xp = tx;
    y = yp - q*r; yp = ty;
  }

  return mt(rp, xp, yp);
}

ll inv(ll x, ll m) {
  return (get<1>(extended_gcd(x, m)) + m) % m;
}

ll mod_mult(ll a, ll b, ll m) {
  // "grade school" multiplication, in binary form
  ll rtn = 0;

  while (b > 0) {
    if ((b & 1) == 1) {
      rtn = (rtn + a) % m;
    }
    a = (2*a) % m;
    b >>= 1;
  }
  return rtn;
}

ll mod_exp(ll b, ll e, ll m) {
  if (m == 1) {
    return 0;
  }

  ll rtn = 1;
  b %= m;
  while (e > 0) {
    if ((e & 1) == 1) {
      rtn = (rtn*b) % m;
    }
    e >>= 1;
    b = (b*b) % m;
  }
  return rtn;
}

bool prime(ll n) {
  if (n == 1 || (n % 2 == 0 and n != 2)) {
    return false;
  }
  for (ll i = 3; i*i <= n; i += 2) {
    if (n % i == 0) {
      return false;
    }
  }
  return true;
}

pi find_kp(ll n) {
  ll k, p;
  k = 1;
  p = n + 1;
  while (not prime(p)) {
    k++;
    p += n;
  }
  return mp(k, p);
}

ll find_generator(ll n, ll k, ll p) {
  li prime_factors = {2};
  if (prime(k)) {
    prime_factors.append(k);
  }
  range(i, p) {
    if (gcd(i, p) == 1) {
      bool gen = true;
      For(factor, prime_factors) {
        if (mod_exp(i, k*n/factor, p) == 1) {
          gen = false;
          break;
        }
      }
      if (gen) {
        return i;
      }
    }
  }
  return -1;
}

pi find_wp(ll n) {
  ll k, p, g;
  tie(k, p) = find_kp(n);
  g = find_generator(n, k, p);
  return mp(mod_exp(g, k, p), p);
}

ll get_w(ll w, ll n, ll m, ll p) {
  return mod_exp(w, ((ll) 1) << (n - m + 1), p);
}

ll rev_increment(ll c, ll m) {
  ll i = ((ll) 1) << (m - 1);
  while ((c & i) > 0) {
    c ^= i;
    i >>= 1;
  }
  return c ^ i;
}

li bit_rev_copy(li arg a) {
  li A;
  ll n, m, c;
  n = len(a);
  m = msb(n);
  range(i, n) {
    A.append(0);
  }
  c = 0;
  range(i, n) {
    A[c] = a[i];
    c = rev_increment(c, m);
  }

  return A;
}

li int_fft(li arg a, ll wn, ll p) {
  ll n, lgn, m, wm, w, t, u;
  n = len(a);
  lgn = msb(len(a)) + 1;
  li A = bit_rev_copy(a);
  range(s, 1, lgn) {
    m = 1 << s;
    wm = mod_exp(wn, 1 << (lgn - s - 1), p);
    for (ll k = 0; k < n; k += m) {
      w = 1;
      range(j, (m >> 1)) {
        t = (w*A[k + j + (m >> 1)]) % p;
        u = A[k + j];
        A[k + j] = (u + t) % p;
        A[k + j + (m >> 1)] = (u - t + p) % p;
        w = (w*wm) % p;
      }
    }
  }

  return A;
}

li inv_int_fft(li arg a, ll wn, ll p) {
  ll n1 = inv(len(a), p);
  li ap, rtn;
  ap = int_fft(a, inv(wn, p), p);
  For(x, ap) {
    rtn.append((x*n1) % p);
  }

  return rtn;
}

li mirror(li &a) {
  ll n, np;
  n = a.size();
  np = 1 << ((int) ceil(log2(n)));
  range(i, np - n) {
    a.append(0);
  }
  return a;
}

li poly_mult(li arg a, li arg b, ll w, ll p) {
  ll n = max(len(a), len(b));
  li ap, bp;
  ap = a;
  range(i, 2*n - len(a)) {
    ap.append(0);
  }
  bp = b;
  range(i, 2*n - len(b)) {
    bp.append(0);
  }
  ap = mirror(ap);
  bp = mirror(bp);

  ll wn = get_w(w, M, msb(len(ap)) + 1, p);
  ap = int_fft(ap, wn, p);
  bp = int_fft(bp, wn, p);

  li c;
  range(i, len(ap)) {
    c.append((ap[i]*bp[i]) % p);
  }

  return inv_int_fft(c, wn, p);
}

li reverse(li arg l) {
  li rtn;
  for (ll i = len(l) - 1; i > 0; i--) {
    rtn.append(l[i]);
  }
  rtn.append(l[0]);
  return rtn;
}

pi min_offset(li arg a, li arg b) {
  ll n, m, x2, xy, y2, best, l2, d;
  n = len(a);
  m = len(b);
  li p = poly_mult(reverse(a), b, W, P);
  x2 = 0;
  For(x, a) {
    x2 += x*x;
  }
  xy = p[n - 1];
  y2 = 0;
  range(i, n) {
    y2 += b[i]*b[i];
  }
  best = 0;
  l2 = -2*xy + y2;
  range(i, 1, m - n + 1) {
    y2 += b[n - 1 + i]*b[n - 1 + i] - b[i - 1]*b[i - 1];
    xy = p[n - 1 + i];
    d = -2*xy + y2;
    if (d < l2) {
      best = i;
      l2 = d;
    }
  }

  return mp(best, x2 + l2);
}

pi max_cosine(li arg a, li arg b) {
  ll n, m, x2, xy, y2, best; double cosine, d;
  n = len(a);
  m = len(b);
  li p = poly_mult(reverse(a), b, W, P);
  x2 = 0;
  For(x, a) {
    x2 += x*x;
  }
  xy = p[n - 1];
  y2 = 0;
  range(i, n) {
    y2 += b[i]*b[i];
  }
  best = 0;
  cosine = 1.0*xy/y2;
  range(i, 1, m - n + 1) {
    y2 += b[n - 1 + i]*b[n - 1 + i] - b[i - 1]*b[i - 1];
    xy = p[n - 1 + i];
    d = 1.0*xy/y2;
    if (d > cosine) {
      best = i;
      cosine = d;
    }
  }

  return mp(best, 100000000000000000.0*(1 - cosine/x2));
}

int main(void) {
  ios::sync_with_stdio(false); cin.tie(NULL); // fast cin
  ifstream fin("song.in"); ofstream fout("song.out");

  // ll w, p
  // tie(w, p) = find_wp(((ll) 1) << M);

  ll N, v, pos, l2;
  li a, b;
  fin >> N;

  range(i, N) {
    fin >> v;
    a.append(v);
  }
  fin >> N;
  range(i, N) {
    fin >> v;
    b.append(v);
  }

  tie(pos, l2) = min_offset(a, b);
  fout << pos << " " << l2 << el;

  return 0;
}
