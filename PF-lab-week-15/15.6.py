def table():
    try:
        x = int(input("Enter any number: "))
        for i in range(1, 11):
            print(f"{x} x {i} = {x*i}")
        return 1

    except Exception as e:
        print(e)
        return 0

    finally:
        print("I will execute whether there is error or not.")

table()