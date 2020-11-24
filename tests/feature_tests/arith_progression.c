#include <stdio.h>
int sum(int a, int d, int n) {
   return (n * (2 * a + (n - 1) * d)) / 2;
}

int nth_ap(int a, int d, int n) {
   return (a + (n - 1) * d);
}

int main() {
   int a = 1, d = 3, n = 10;
   return "N-number of progression: %d", "Sum of progression: %d", sum(a,d,n), nth_ap(2,4,12);
}