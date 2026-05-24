i = 0
while i <= 7:
    j = 0
    while j <= (7-i):
        print(" ", end="")
        j = j+1
    k = 0
    while k <= i:
        print("*", end=" ")
        k = k+1
    print()
    i = i+2
print('____end____')