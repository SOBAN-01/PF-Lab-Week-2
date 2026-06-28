try:
    # Statements which could generate exception
    x = int(input("Enter Any Number: "))

    if x % 2 == 0:
        print(f"{x} is Even")
    else:
        print(f"{x} is Odd")

except:
    # Solution of generated exception
    print("Some error occurred!")

else:
    # Statements when no error occurs
    print("Your code has no error!")