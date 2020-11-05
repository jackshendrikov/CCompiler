int main() {
  int a = 5, b = 10;

  int c = a + b;
  if(c != 15) return 1;

  int d = c + 5;
  if(d != 20) return 2;

  int e = 2 + 4;
  if(e != 6) return 3;

  int f = e + d;
  if(f != 26) return 4;

  int g = f + f + e;
  if(g != 58) return 5;

  int i = g + g;
  i = i + i;

  if(i != 232) return 6;

  int sum;
  sum = 0;

  short val1;
  val1 = 40;

  short val2 = 40;
  val1 = val2 + 40;
  if(val1 != 40 + 40) return 7;

  short val3 = 70;
  val1 = 70 + val3;
  if(val1 != 70 + 70) return 8;

  val1 = val3 - 10;
  if(val1 != 30 + 30) return 9;
  if(30 + 30 != val1) return 10;

  sum = sum + val1 + val2;
  return sum;
}