int main() {
  // error: expression on left of '=' is not assignable
  if(3 = 5) {
    return 1;
  }

  // error: use of undeclared identifier 'a'
  if(a = 5) {
    return 2;
  }

  // error: use of undeclared identifier 'a'
  3 + 4 = a;

  // error: two or more data types in declaration specifiers
  int long a;

  // error: both signed and unsigned in declaration specifiers
  unsigned signed int a;

  // error: integer literal too large to be represented by any integer type
  1000000000000000000000000000;

  // error: operand of increment operator not a modifiable lvalue
  4--;

  return 0;
}
