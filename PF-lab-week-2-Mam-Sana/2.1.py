password = "secret"
max_attempts = 3
attempts = 0
while attempts < max_attempts:
    user_password = input("Enter the password: ")
    attempts += 1
    if user_password == password:
        print("Access granted!")
        break
    else:
        print("Incorrect password. Please try again.")
if attempts == max_attempts:
    print("Maximum number of attempts reached. Access denied.")