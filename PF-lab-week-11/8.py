for i in range(1, 5):
    for j in range(4-i):
        print("*", end="")
    for j in range(2*i):
        print(i, end="")
    print()
print('____end____')