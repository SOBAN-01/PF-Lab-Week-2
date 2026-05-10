stu=int(input("Enter number of students:"))
n=1
while n<=stu:
    name=input("Enter Student name:")
    roll_no=(input("Enter Roll no:"))
    obt=int(input("Enter Obtained marks:"))
    t=300
    per=(obt/t)*100
    print("Name:",name)
    print("Roll Number:",roll_no)
    print("Obtained Marks:",obt)
    print("Percentage:",per)
    if per>90:
        print("A")
    elif per>85:
        print("-A")
    elif per>80:
        print("B")
    elif per>75:
        print("-B")
    elif per>70:
        print("C")
    elif per>65:
        print("-C")
    elif per>60:
        print("D")
    elif per>55:
        print("-D")
    else:
        print("F")
    n=n+1


