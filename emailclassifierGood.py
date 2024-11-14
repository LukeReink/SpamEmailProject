# dictionaries are like lists/arrays, but you can use
# strings as indices - called keys
import random

words = {}
# here the key (index) is "money", and the val is 20


# print(words)

file = "demotxt.txt"

# r is for reading (as opposed to writing)
fileContents = open(file, "r")

file1 = "training.txt"

fileContents1 = open(file1, "r")

file2 = "training.txt"

fileContents2 = open(file1, "r")

file3 = "test_data (1).txt"

fileContents3 = open(file3, "r")

file4 = "training.txt"

fileContents4 = open(file4, "r")

def main():
    emails = []
    emails90percent = []
    emailsRest = []
    emailsFullTraining = []
    emailsTestData = []
    #counter for specific email segregation
    counting = 0
    for line in fileContents4:
        if counting < 31:
            emails.append(line[0:])
        counting += 1
    counting = 0
    # for line in fileContents:
    #     emails.append(line[0:])
    for line in fileContents1:
        if counting < 0.9 * 4888 and counting > 31:
            emails90percent.append(line[0:])
        elif counting > 31:
            emailsRest.append(line[0:])
        counting += 1
    for line in fileContents2:
        emailsFullTraining.append(line[0:])
    for line in fileContents3:
        emailsTestData.append(line[0:])

    repetaWordsSpam = {}
    repetaWordsNotSpam = {}
    # loop through initial testing emails and find words that are repeated among all emails and would not do us any good
    # loop through and look for words that are solely in scam emails too
    # find neutral words that still weigh heavily towards spam
    for email in emails:
        words = email.split()
        if words[0] == "1":
            spam = True
        else:
            spam = False
        for word in words:
            if spam:
                if word in repetaWordsSpam.keys():
                    repetaWordsSpam[word] += 1
                else:
                    repetaWordsSpam[word] = 1
            else:
                if word in repetaWordsNotSpam.keys():
                    repetaWordsNotSpam[word] += 1
                else:
                    repetaWordsNotSpam[word] = 1
    # add words that are in spam a lot but are not in 'not-spam' a lot to this list
    # could also add words that are barely in 'not-spam' and more commonly in spam
    keySpamWords = {}
    # add words that are repeated in both spam and not spam to this list
    keyNotSpamWords = {}
    #words that appear more frequently than numby should be disqualified
    numby = 10
    for word in repetaWordsSpam.keys():
        #1048576 = 2 ^ 20 (if this word is repeated less than 20 times it is good to check for)
        if repetaWordsSpam[word] < numby:
            if word in repetaWordsNotSpam:
                #if word is more often in spam emails by any margain, map its frequency in spam (minus frequency in not spam) to
                #scores of 1 through 20
                if repetaWordsSpam[word] - repetaWordsNotSpam[word] > 0 and not word == "1" and not word == "0" :
                   # print("Spamy word: ", word)
                   keySpamWords[word] = repetaWordsSpam[word] - repetaWordsNotSpam[word]
            #if word is only in spam emails add to list aswell
            else:
                keySpamWords[word] = repetaWordsSpam[word]
                # print("Spamy word: ", word)
    for word in repetaWordsNotSpam:
        if repetaWordsNotSpam[word] < numby:
            if word in repetaWordsSpam:
                if repetaWordsNotSpam[word] - repetaWordsSpam[word] > 0 and not word == "1" and not word == "0":
                    # print("Non-spamy word: ", word)
                    keyNotSpamWords[word] = repetaWordsNotSpam[word] - repetaWordsSpam[word]
            else:
                keyNotSpamWords[word] = repetaWordsNotSpam[word]
                # print("Non-spamy word: ", word)
    print("First 90% of training set:")
    #machine learn with first 90% of training set
    KeySpamWords, KeyNotSpamWords = machineLearn(emails90percent, keySpamWords, keyNotSpamWords, True)
    print("Last 10% of training set:")
    #validate on last 10% of training set
    KeySpamWords, KeyNotSpamWords = machineLearn(emailsRest, KeySpamWords, KeyNotSpamWords, False)
    print("100% of training set:")
    #full test on 100% of training set
    KeySpamWords, KeyNotSpamWords = machineLearn(emailsFullTraining, KeySpamWords, KeyNotSpamWords, True)
    print("Test set:")
    #finally test on the new full test set
    machineLearn(emailsTestData, KeySpamWords, KeyNotSpamWords, True)
    print("Done!")

def machineLearn(emails, keySpamWords, keyNotSpamWords, training):
    # count for total amount of spam and total amount of non spam emails (for calculating percent accuracy once machine is learning)
    spamCount = 0
    nonSpamCount = 0
    totalCount = 0
    # print("HERE WE GO")
    # for word in keySpamWords.keys():
    #     print(word)
    # for word in keyNotSpamWords.keys():
    #     print(word)
    for email in emails:
        words = email.split()
        # print(words[0])
        if words[0] == "1":
            spamCount += 1
        elif words[0] == "0":
            nonSpamCount += 1
        totalCount += 1
    #boolean for done
    done = False
    #initialize
    score = 0
    scamFound = 0
    # begin to machine learn:
    # key words for spam is keySpamWord list
    # stores how likely an email is a scam as a score
    emailScores = []
    #stores what is thought to be a spam email
    for email in emails:
        emailScores.append(0)
    passThru = 0
    while not done:
        passThru += 1
        # index for what email you are on
        index = -1
        numEmailsCorrectlyClassified = 0
        for i in range(len(emailScores)):
            emailScores[i] = 0
        for email in emails:
            index += 1
            words = email.split()
            if words[0] == "1":
                spam = True
            else:
                spam = False
            for word in words:
                if word in keySpamWords.keys():
                    emailScores[index] -= keySpamWords[word]
                if word in keyNotSpamWords.keys():
                    emailScores[index] += keyNotSpamWords[word]
            if emailScores[index] < 0 and spam:
                numEmailsCorrectlyClassified += 1
            elif emailScores[index] >= 0 and not spam:
                numEmailsCorrectlyClassified += 1
            #adjust scores of words in email based on if the classification was correct
            #add or subtract by 'incriment' based on how email was incorrectly identified
            else:
                # once a words has been considered once remove it from further consideration by addding it to this beware list
                wordsToNotConsider = []
                if emailScores[index] < 0 and not spam:
                    incriment = 1
                else:
                    incriment = -1
                for word in words:
                    if word in keySpamWords.keys() and not word in wordsToNotConsider:
                        # print(email)
                        # print("^word 4 above: ", word)
                        wordsToNotConsider.append(word)
                        keySpamWords[word] -= incriment
                        # print(keySpamWords[word], "< weight, word: ", word, " pass thru: ", passThru)
                for word in words:
                    if word in keyNotSpamWords.keys() and not word in wordsToNotConsider:
                        keyNotSpamWords[word] += incriment
                        wordsToNotConsider.append(word)
                        # print(keyNotSpamWords[word], "< weight, word: ", word, " pass thru: ", passThru)
        print("Pass", passThru, "accuracy:", numEmailsCorrectlyClassified/totalCount * 100, "%")
        #if training don't stop untill 100%
        if training:
            if numEmailsCorrectlyClassified/totalCount * 100 == 100:
                #return spamy and not spamy words with optimized weights
                return keySpamWords, keyNotSpamWords
        else:
            #return spamy and not spamy words with optimized weights
            return keySpamWords, keyNotSpamWords
main()
