print()
s1 = {1, 2, 3, 4}
s2 = {4, 5, 6, 7}
s3 = {7, 8, 9}
print(s1)
s1.update(s2)
s2.update(s3)
s3.update(s1)
print(s1)
print(s2)
print(s3)