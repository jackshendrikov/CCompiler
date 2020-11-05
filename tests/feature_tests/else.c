int main() {
  int a = 0;

  if(0) { // false
    return 1;
  } else {
    a = 10; // true -> a = 10
  }

  if(a != 10) return 2; else {

    // Verify proper dangling-else parsing
    if(1) if(0) return 14; else return 115; // first if true -> next if false -> else -> return 115

    return 0;
  }

  return 6;
}