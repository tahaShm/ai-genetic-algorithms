import re
from random import shuffle
from random import randrange
import random
import math
import time

def readFile(fileName) :
    file = open(fileName, 'r+')
    fList = file.readlines()
    file.close()
    return fList;

def getDictionary(words):
    wordDic = {}
    for word in words :
        if (word in wordDic) :
            wordDic[word] += 1
        else: 
            wordDic[word] = 1
    return wordDic           

def getWords(context) :
    words = re.split('[^a-zA-Z]', context)
    words = list(filter(None, words))
    return words

def getListWords(context) :
    words = [] 
    for row in context:
        row = row.lower()
        words += re.split('[^a-zA-Z]', row)
        words = list(filter(None, words))
    words = getDictionary(words)
    return words
def makeDefaultDictionary() :
    encodedTxt = readFile("encoded_text.txt")
    encodedTxt = ''.join(encodedTxt)
    return encodedTxt
def makeDictoinaries():    
    globalTxt = readFile("global_text.txt")
    encodedTxt = readFile("encoded_text.txt")
    for i in range(len(encodedTxt)) :
        encodedTxt[i] = encodedTxt[i].lower()
    globalWords = getListWords(globalTxt)
    return [globalWords, encodedTxt]

def sortSecond(val): 
    return val[1]

class Decoder:
    def __init__(self, encodedTxt, defaultEncodedTxt) : 
        self.encodedTxt = ''.join(encodedTxt)
        self.defaultEncodedTxt = defaultEncodedTxt
        self.numOfWords = len(getWords(self.encodedTxt))
        self.restartLimitation = 120
        self.popSize = 500
        self.crossoverPoints = 5
        self.elitismPercentage = 16
        self.pc = 0.65
        self.pm = 0.2
        self.chromosomeSet = {}
        self.chromosomes = self.getInitialChromosomes() #[0]: chromosome string, [1]: fitness value
        self.chromosomes.sort(key = sortSecond, reverse = True)
        
        
    def getInitialChromosomes(self) :
        chromosomes = []
        s = "abcdefghijklmnopqrstuvwxyz"
        newS = s
        for i in range(self.popSize):
            newS = ''.join(random.sample(newS,len(newS)))
            fitnessScore = self.getFitness(newS)
            chromosomes.append([newS, fitnessScore])
            self.chromosomeSet[newS] = fitnessScore
        return chromosomes
    
    def calculateFitness(self, words):
        fitness = 0
        for word in words :
            if (word in globalWords) :
                fitness += 1
        return fitness
                
    def getFitness(self, s) :
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        tempEncoded = self.encodedTxt
        for i in range(len(s)):
            tempEncoded = tempEncoded.replace(alphabet[i], (s[i]).upper())
        tempEncoded = tempEncoded.lower()
        tempWords = getWords(tempEncoded)
        fitnessScore = self.calculateFitness(tempWords)
        return fitnessScore
    
    def getNewParent(self, sumOfFitnesses) : 
        randNum = randrange(sumOfFitnesses)
        sumOfFitnesses = 0
        for i in range(self.popSize) : 
            sumOfFitnesses += self.chromosomes[i][1]
            if sumOfFitnesses >= randNum : 
                return self.chromosomes[i]
            
        index = randrange(self.popSize)
        return self.chromosomes[index]     
        
    def chooseParants(self) : 
        parents = []
        elitism = int(self.elitismPercentage/100 * self.popSize)
        sumOfFitnesses = 0
        for i in range(self.popSize) : 
            sumOfFitnesses += self.chromosomes[i][1]
        for i in range(self.popSize - elitism) : 
            newParent = self.getNewParent(sumOfFitnesses)
            parents.append(newParent)
        shuffle(parents)
        return parents
    
    def getcrossedStr(self, p1, p2, points):
        usedChars1 = set()
        child1 = [0] * len(p1)
        for i in points : 
            child1[i] = p1[i]
            usedChars1.add(p1[i])
        i2 = 0
        iChild = 0
        while (len(usedChars1) <= len(p1)) : 
            if len(usedChars1) == len(p1) : 
                break
            if (child1[iChild] != 0):
                iChild += 1
                continue
            if (p2[i2] not in usedChars1) :
                child1[iChild] = p2[i2]
                usedChars1.add(p2[i2])
                iChild += 1
                i2 += 1
                continue
            if (p2[i2] in usedChars1) :
                i2 += 1
                continue
        newChild = ''.join(child1)
        return newChild
    
    def crossover(self, p1, p2) :
        randomNum = random.uniform(0, 1)
        if (randomNum <= self.pc) :    
            points = random.sample(range(0, len(p1)), self.crossoverPoints)
            child1 = self.getcrossedStr(p1, p2, points)
            child2 = self.getcrossedStr(p2, p1, points)
            return [child1, child2]
        else:
            return [p1, p2]
        
    def mutate(self, child) :
        childList = re.findall(r"[\w']", child)
        newRand = random.uniform(0, 1)
        if (newRand <= self.pm) :
            points = random.sample(range(0, len(child)), 2)
            tempChar = childList[points[0]]
            childList[points[0]] = childList[points[1]]
            childList[points[1]] = tempChar
        newChild = ''.join(childList)
        return newChild
    def checkChild(self, child):
        if (child in self.chromosomeSet) :
            return [child, self.chromosomeSet[child]]
        else :
            return -1
        
    def mutateNewChild(self, child) :
        newChild = self.mutate(child)  
        repetitiveChild = self.checkChild(newChild)
        newFitness = 0
        if (repetitiveChild == -1) :
            newFitness = self.getFitness(newChild)
        else :
            newFitness = repetitiveChild[1]
        return [newChild, newFitness]
                
    def mateParentsAndGetChilds(self, parents) :
        newGeneration = []
        elitism = int(self.elitismPercentage/100 * self.popSize)
        for i in range(elitism) : 
            newGeneration.append(self.chromosomes[i])
        for i in range(int((self.popSize - elitism) / 2)) :
            parent1 = parents[(i * 2) % (self.popSize)][0]
            parent2 = parents[(i * 2 + 1) % (self.popSize)][0]
            newChildren = self.crossover(parent1, parent2)
            child1 = self.mutateNewChild(newChildren[0])
            child2 = self.mutateNewChild(newChildren[1])
            newGeneration.append(child1)
            newGeneration.append(child2)   
        newGeneration.sort(key = sortSecond, reverse = True)
        return newGeneration
    
    def generateNewGeneration(self) : 
        newParents = self.chooseParants()
        self.chromosomes = self.mateParentsAndGetChilds(newParents)
    
    
    def printDecodedTxt(self, iteration) :
        print("**** done ****")
        print("number of generations: ", iteration)
        print("chromosome: ", self.chromosomes[0][0])
        print("decoded text: ")
        print()
        defaultList = list(self.defaultEncodedTxt)
        
        s = self.chromosomes[0][0]
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        tempEncoded = self.encodedTxt
        for i in range(len(s)):
            tempEncoded = tempEncoded.replace(alphabet[i], (s[i]).upper())
        tempEncoded = tempEncoded.lower()
        
        answerList = s = list(tempEncoded)
        
        for i in range(len(defaultList)) : 
            if defaultList[i].isupper() :
                answerList[i] = answerList[i].upper()
        ansTxt = ''.join(answerList)
        print(ansTxt)
    
    def printPercentage(self, previousMatched, currentMatched) : 
        prevPercentage = int (previousMatched / self.numOfWords * 100)
        currPrecentage = int (currentMatched / self.numOfWords * 100)
        progress = 0
        if (currPrecentage >= 90 and prevPercentage < 90) : 
            progress = 90
        elif (currPrecentage >= 80 and prevPercentage < 80) : 
            progress = 80 
        elif (currPrecentage >= 70 and prevPercentage < 70) : 
            progress = 70 
        elif (currPrecentage >= 60 and prevPercentage < 60) : 
            progress = 60 
        elif (currPrecentage >= 50 and prevPercentage < 50) : 
            progress = 50 
        elif (currPrecentage >= 40 and prevPercentage < 40) : 
            progress = 40 
        elif (currPrecentage >= 30 and prevPercentage < 30) : 
            progress = 30 
        elif (currPrecentage >= 20 and prevPercentage < 20) : 
            progress = 20 
        elif (currPrecentage >= 10 and prevPercentage < 10) : 
            progress = 10 
        if (progress > 0) :
            print(progress, "%")
         
    def decode(self):
        matchedWords = self.chromosomes[0][1]
        iteration = 0
        repeated = 0
        print("decoding...")
        while (matchedWords < self.numOfWords) :
            self.printPercentage(matchedWords, self.chromosomes[0][1])
            if (self.chromosomes[0][1] == matchedWords) :
                repeated += 1
            else: 
                repeated = 0
            if (repeated == self.restartLimitation) :
                repeated = 0
                print("restart...")
                self.chromosomes = self.getInitialChromosomes()
                self.chromosomes.sort(key = sortSecond, reverse = True)
            matchedWords = self.chromosomes[0][1]
            self.generateNewGeneration()
            iteration += 1
        self.printDecodedTxt(iteration)
            
                
globalWords = makeDictoinaries()[0]
encodedTxt = makeDictoinaries()[1]
defaultEncodedTxt = makeDefaultDictionary()
d = Decoder(encodedTxt, defaultEncodedTxt)
start = time.time()
d.decode()
end = time.time()
print("time: ", '%.2f'%(end - start), 'sec')
