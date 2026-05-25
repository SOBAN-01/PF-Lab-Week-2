height = 5
for i in range(1, height + 1):
    s = ' ' * (height - i)
    n = '*' * (2 * i - 1)
    print(s + n)