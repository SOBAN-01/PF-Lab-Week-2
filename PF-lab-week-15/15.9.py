#Decimal to Hexadecimal UDF

def decimal_to_hex(n):
    try:
        result = hex(n)
        print("UDF call successfully")
        return result
    except TypeError:
        print("Error: please pass a number, not a string")

print(decimal_to_hex(255))
print(decimal_to_hex("255"))