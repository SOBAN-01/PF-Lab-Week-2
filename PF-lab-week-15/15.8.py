#2×2 Matrix Inverse

try:
    a = float(input("Enter a: "))
    b = float(input("Enter b: "))
    c = float(input("Enter c: "))
    d = float(input("Enter d: "))

    det = a * d - b * c
    inverse = [[d/det, -b/det], [-c/det, a/det]]

    print("Inverse Matrix:")
    print(inverse[0])
    print(inverse[1])

except ValueError:
    print("Error: please enter numeric values only")
except ZeroDivisionError:
    print("Error: determinant is 0, matrix has no inverse")