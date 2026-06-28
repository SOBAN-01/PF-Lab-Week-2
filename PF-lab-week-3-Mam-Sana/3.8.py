def area(*dimentions):
    print(f"Length:{dimentions[0]}")
    print(f"Breadth:{dimentions[1]}")
    Area=dimentions[0]*dimentions[1]
    print(f"Area:{Area}")
    return

length=int(input("Enter Length of Rectangle "))
Breadth=int(input("Enter Breadth of Rectangle "))
dimentions=(length,Breadth)
area(*dimentions)
