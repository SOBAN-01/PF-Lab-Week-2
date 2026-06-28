def area(l=5,b=6):
    Area=l*b
    return Area

def perimeter(l=5,b=6):
    Perimeter=2*(l+b)
    return Perimeter

length=int(input("Enter Length of Rectangle "))
Breadth=int(input("Enter Breadth of Rectangle "))
rect_area=area()
rect_perimeter=perimeter()
print(f"Length:{length} Breadth:{Breadth} Area:{rect_area}")
print(f"Length:{length} Breadth:{Breadth} Area:{rect_perimeter}")
rect_area=area(length,Breadth)
rect_perimeter=perimeter(length,Breadth)
print(f"Length:{length} Breadth:{Breadth} Area:{rect_area}")
print(f"Length:{length} Breadth:{Breadth} Area:{rect_perimeter}")