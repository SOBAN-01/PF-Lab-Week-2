#Factorial with Exception Handling

def factorial(n):
    assert isinstance(n, int) and n >= 0, "Enter a non-negative integer"
    return 1 if n == 0 else n * factorial(n - 1)

try:
    num = int(input("Enter a number: "))
    print("Factorial:", factorial(num))
except ValueError:
    print("Error: please enter a valid number, not a string")
except AssertionError as e:
    print("Error:", e)