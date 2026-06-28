def area(l,b):
    print(f"Length:{l}")
    print(f"Breadth:{b}")
    Area=l*b
    print(f"Area:{Area}")
    return

def perimeter(l,b):
    print(f"Length:{l}")
    print(f"Breadth:{b}")
    Perimeter=2*(l+b)
    print(f"Perimeter:{Perimeter}")
    return

length=int(input("Enter Length of Rectangle "))
Breadth=int(input("Enter Breadth of Rectangle "))
area(b=Breadth,l=length)
perimeter(l=length,b=Breadth)