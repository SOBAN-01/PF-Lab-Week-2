for i in range(1, 5):
    for j in range(5-i):
        print("*", end="")
    for j in range(2*i):
        print(i, end="")
    for j in range(5-i):
        print("*", end="")
    print()
print('____end____')