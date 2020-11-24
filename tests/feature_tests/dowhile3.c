int main()
{
    int i = 1, counter = 0;

    do {
        if (i % 3 == 0) counter += 1;
        i++;
    } while(i < 100);

    return counter;
}