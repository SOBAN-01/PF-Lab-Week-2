try:
    x = int(input("Enter Any Number: "))

    if x % 2 == 0:
        print(f"{x} is Even")
    else:
        print(f"{x} is Odd")

except:
    print("Some error occurred!")

else:
    print("Your code has no error!")