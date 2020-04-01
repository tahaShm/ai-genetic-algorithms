import re
from random import shuffle
from random import randrange
import random
import math

def readFile(fileName) :
    file = open(fileName, 'r+')
    fList = file.readlines()
    file.close()
    fList = [s.replace('\n', '') for s in fList]
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
    words = re.findall(r"\w+", context)
    return words

def getListWords(context) :
    words = [] 
    for row in context:
        row = row.lower()
        words += re.findall(r"\w+", row)
    words = getDictionary(words)
    return words

def makeDirectories():    
    globalTxt = readFile("global_text.txt")
    encodedTxt = readFile("encoded_text.txt")
    for i in range(len(encodedTxt)) :
        encodedTxt[i] = encodedTxt[i].lower()
    globalWords = getListWords(globalTxt)
    return [globalWords, encodedTxt]

def sortSecond(val): 
    return val[1]

class Decoder:
    def __init__(self, encodedTxt) : 
        self.encodedTxt = ''.join(encodedTxt)
        self.numOfWords = len(getWords(self.encodedTxt))
        print(getWords(self.encodedTxt))
        print(self.numOfWords)
        self.numOfGenerations = 1000
        self.popSize = 500
        self.tournamentSize = 500
        self.crossoverPoints = 13
        self.elitismPercentage = 15
        self.pc = 0.90
        self.pm = 0.8
        self.chromosomeSet = {}
        self.chromosomes = self.getInitialChromosomes() #[0]: chromosome string, [1]: fitness value, [2]: sqrt of fitness value
        self.chromosomes.sort(key = sortSecond, reverse = True)
        # print(self.chromosomes)
        # print("____________________________________________________________")
        # print("____________________________________________________________")
        
        
    def getInitialChromosomes(self) :
        chromosomes = []
        s = "abcdefghijklmnopqrstuvwxyz"
        newS = s
        for i in range(self.popSize):
            newS = ''.join(random.sample(newS,len(newS)))
            fitnessScore = self.getFitness(newS)
            chromosomes.append([newS, fitnessScore, int(math.sqrt(fitnessScore))])
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
    
    def getNewParent(self) : 
        sumOfFitnesses = 0
        for i in range(self.popSize) : 
            sumOfFitnesses += self.chromosomes[i][1]
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
        elitism = self.elitismPercentage/100 * self.popSize
        for i in range(self.popSize) : 
            if (i < elitism) : 
                parents.append(self.chromosomes[i])
            else :
                newParent = self.getNewParent()
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
            # print(points)
            child1 = self.getcrossedStr(p1, p2, points)
            child2 = self.getcrossedStr(p2, p1, points)
            # print(child1)
            # print(child2)
            return [child1, child2]
        else:
            return [p1, p2]
        
    def mutate(self, child) :
        childList = re.findall(r"[\w']", child)
        for i in range(len(childList)) : 
            newRand = random.uniform(0, 1)
            if (newRand <= self.pm) :
                # print(i)
                newRandIndex = randrange(len(childList))
                while (newRandIndex == i) : 
                    newRandIndex = randrange(len(childList))
                tempChar = childList[i]
                childList[i] = childList[newRandIndex]
                childList[newRandIndex] = tempChar
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
        return [newChild, newFitness, int(math.sqrt(newFitness))]
                
    def mateParentsAndGetChilds(self, parents) :
        newGeneration = []
        for i in range(int(self.popSize / 2)) :
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
    
            
    def decode(self):
        matchedWords = self.chromosomes[0][1]
        iteration = 0
        # while (matchedWords < self.numOfWords and iteration <= 30) :
        #     self.generateNewGeneration()
        #     print("generation:", iteration)
        #     print("best chromosome: ", self.chromosomes[0][0])
        #     print("matched words: ", self.chromosomes[0][1])
        #     print()
        #     iteration += 1
        # print("finally: ")
        # print("best chromosome: ", self.chromosomes[0][0])
        # print("matched words: ", self.chromosomes[0][1])
        # print("decoded text: ")
        # alphabet = "abcdefghijklmnopqrstuvwxyz"
        # tempEncoded = self.encodedTxt
        # for i in range(26):
        #     tempEncoded = tempEncoded.replace(alphabet[i], (self.chromosomes[0][0][i]).upper())
        # tempDecoded = tempEncoded.lower()
        # print(tempDecoded)
        
            
        
        
    
    
globalWords = makeDirectories()[0]
encodedTxt = makeDirectories()[1]
d = Decoder(encodedTxt)
# d.generateNewGeneration()
d.decode()
