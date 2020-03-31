import re
def readFile(fileName) :
    file = open(fileName, 'r+')
    fList = file.readlines()
    file.close()
    fList = [s.replace('\n', '') for s in fList]
    return fList;
def makeDirectories():    
    globalTxt = readFile("global_text.txt")
    encodedTxt = readFile("encoded_text.txt")
    globalWords = []
    for gRow in globalTxt:
        globalWords += re.findall(r"\w+", gRow)
    encodedWords = []
    for enRow in encodedTxt:
        encodedWords += re.findall(r"\w+", enRow)
    print(globalWords)
    
makeDirectories()