stu=int(input("Enter number of students:"))
for i in range(int(stu)):
    name=input("Student:")
    roll_no=(input("Roll no:"))
    obt=int(input("Obtained marks:"))
    t=300
    per=(obt/t)*100
    print(per)
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
