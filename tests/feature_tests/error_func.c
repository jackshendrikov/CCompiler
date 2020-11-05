int sum(int a, int b) {
  return 0;
}

void test_no_args() { }

void redefine_func() { }

// error: redefinition of 'redefine_func'
void redefine_func() { }

void return_expr() {
  // error: function with void return type cannot return value
  return 2;
}

int no_return_expr() {
  // error: function with non-void return type must return value
  return;
}

int func_argument(int f(int, short)) {
  return f(0,0);
}

// error: function definition provided for non-function type
int not_func {
  return 0;
}

// error: function definition missing parameter name
void missing_param(int) { }

void repeat_def(int a) {
  // error: redefinition of 'a'
  int a;
}


const int func() {
  return 4;
}

// error: redefinition of 'a'
void repeat_param(int a, int a) { }


int main() {
  // error: incorrect number of arguments for function call (expected 2, have 3)
  sum(1,2,3);

  char* p;
  // error: invalid conversion between types
  sum(1, p);

  // error: incorrect number of arguments for function call (expected 0, have 1)
  test_no_args(1);

  // error: conversion from incompatible pointer type
  func_argument(sum);
}
