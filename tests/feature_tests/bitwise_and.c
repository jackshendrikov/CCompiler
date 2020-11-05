int main() {
  int a = 0b11111;
  int  b = 0b10101;
  return a & b & (0b10111 & 0b11100); // 20 = 0b10100
}