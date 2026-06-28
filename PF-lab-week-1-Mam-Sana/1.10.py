username = input("Enter your username: ")
if (username =="admin" or username =="Admin"):
    print("Welcome, administrator.")
elif (username == "guest" or username == "Guest"):
    print("Welcome, guest.")
else:
    print("Access denied.")