int main() {
    int a = 0;
    int b = 1;

    if (a)
        a = 2;
    else
        a = 3; // true, a = 3

    if (b)
        b = 4; // true, b = 4
    else
        b = 5;

    return a + b; // 3 + 4 = 7
}