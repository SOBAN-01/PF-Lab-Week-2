
i = 0
while i <= 4:
    j = 0
    while j <= (4-i):
        print(" ", end="")
        j = j+1
    k = 0
    while k <= i:
        print("*", end=" ")
        k = k+1
    print()
    i = i+1
print('____end____')