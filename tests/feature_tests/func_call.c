int addition(int a, short b) {
  return a + b;
}

int int_ret() {
  int a = 3;
  a = 3 / a;
  return a;
}

int call_function(int f(int, long), int arg1, int arg2) {
  return f(arg1, arg2);
}

const int return_const() {
  return 4;
}


int main() {
  if(add(3, 4) != 7) return 1;
  if(add(helper_ret_5(), 4) != 9) return 2;
  if(add(helper_ret_6(), 5) != 11) return 3;


  int a = return_const();
  if(a != 4) return 5;
}
