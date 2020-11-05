int main() {
  int a = 10;
  if(*(&a) != 10) return 1;

  long b = 20;
  if(*(&b) + 50 != 70) return 2;

  // Assignment of compatible pointer types
  int* c = &a; int *d;
  c = &a;
  c = d;

  // Verify reference operator reverses dereference pointer
  c = &a;
  if(&(*c) != &a) return 5;

  return 16;
}