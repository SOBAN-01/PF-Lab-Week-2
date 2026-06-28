#Bio Data Validation

try:
    name = input("Enter Name: ")
    if any(ch.isdigit() for ch in name):
        raise ValueError("Name should not contain digits")

    address = input("Enter Address: ")
    if len(address) < 3:
        raise ValueError("Address must be at least 3 characters long")

    contact = input("Enter Contact No.: ")
    if any(ch.isalpha() for ch in contact):
        raise ValueError("Contact number should not contain alphabets")

    age = int(input("Enter Age: "))
    if age < 0 or age > 150:
        raise ValueError("Age must be between 0 and 150")

    gender = input("Enter Gender (male/female): ").lower()
    if gender not in ("male", "female"):
        raise ValueError("Gender must be 'male' or 'female'")

    print("All bio data is valid!")
    print(f"Name: {name}, Address: {address}, Contact: {contact}, Age: {age}, Gender: {gender}")

except ValueError as e:
    print("Error:", e)