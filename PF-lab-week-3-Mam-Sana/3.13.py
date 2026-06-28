b = lambda x: "Even" if x % 2 == 0 else "Odd"

num = int(input("Enter a number: "))

print(f"{num} is {b(num)}")