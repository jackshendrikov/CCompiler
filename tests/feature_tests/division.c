int main() {
  int a = 5, b = 10;

  int c = b / a; // c = 2
  int d = b / c; // d = 5
  int e = b / d; // e = 2
  int f = e / 2; // f = 1
  int g = f / 2; // g = 1

  if(g != 0) return 1;

  int h = 30, i = 3, j = 5;

  int k = h / i / j; // k = 2
  if(k != 2) return 2;

  int l = k / k;  // l = 1
  if(l != 1) return 3;

  int m = 3;
  m = m / m; // m = 1
  if(m != 1) return 4;

  return 30 + (b / a) * h; // 30 + 2 * 30 = 90
}