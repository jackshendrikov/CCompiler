int main() {
  _Bool b;

  char c;
  unsigned char uc;

  short s;
  unsigned short us;
  unsigned short us_2;

  int i;
  unsigned int ui;

  long l;
  unsigned long ul;

  // Until negative literals are supported, this is how we insert -1.
  int one = 1;

  c = one;
  if(c != one) return 1;

  s = one;
  if(s != one) return 2;
  if(s == 62445) return 3;

  us = one;
  if(us = one - 1) return 4;
  if(us != 0)  return 5;

  ui = one;
  if(ui == 4294965) return 6;

  c = one;
  l = c;
  if(l - 1 != 0) return 7;

  char c1 = 30, c2 = 40, c3 = 10, c4;
  c4 = (c1 * c2) / c3;
  if(c4 != 120) return 8;

  b = 0;
  if(!b) return b+11;

  return 111;
}