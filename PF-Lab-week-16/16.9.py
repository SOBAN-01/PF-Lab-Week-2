def lyrics_to_frequencies(lyrics):
    myDict = {}
    for word in lyrics:
        if word in myDict:
            myDict[word] += 1
        else:
            myDict[word] = 1
    return myDict

list = ["ali", "is", "is", "a", "very", "good", "boy"]
print(lyrics_to_frequencies(list))