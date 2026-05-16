a=int(input("Enter your marks"))
t=int(input("Enter total marks"))
per=(a/t)*100
print(per)
if per > 90:
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
