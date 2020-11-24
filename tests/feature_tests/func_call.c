int sum(int a, int b) {
  return a + b;
}

int counter(int i) {
  return ++i;
}

int int_ret() {
  int a = 3;
  a = 3 / a;
  return a;
}

int call_function(int f(int a, int b), int arg1, int arg2) {
  return f(arg1, arg2);
}

const int return_const() {
  return 4;
}

int main() {
  if(sum(3, 4) != 7) return 1;
  if(sum(0b101, 0b010) != 0b111) return 2;

  if(counter(5) != 6) return 4;
  else if(int_ret() != 1) return 5;

  int a = return_const();
  if(a != 4) return 10;

  if(call_function(sum, 7, 7) == 14) return 222;
}
