sentence = input("Enter a sentence: ")
if "Python" in sentence:
    if sentence.startswith("Python"):
        print("The sentence starts with 'Python'")
    elif sentence.endswith("Python"):
        print("The sentence ends with 'Python'")
    else:
        print("The sentence contains 'Python'")
else:
    print("The sentence does not contain 'Python'")