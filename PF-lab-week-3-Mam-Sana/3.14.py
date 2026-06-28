avg = lambda x, y, z: (x + y + z) / 3

def square(a=avg(3,4,5)):
    return a * a

print(square())