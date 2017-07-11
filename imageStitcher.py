from PIL import Image
import os
from math import sqrt, ceil, floor
import json
from copy import deepcopy
import re

dir_path = os.path.dirname(os.path.realpath(__file__))
imagesPath = os.path.join(dir_path, "images")
savePaths = [os.path.join(dir_path, "output")]
backFilePath = os.path.join(os.path.join(imagesPath, "Cards_Back_and_Info"), "GW2-HotM-CCG-Back.jpg")
classList = ["Cards_Professions"]
skillsList = ["Cards_Skills"]
legendaryList = ["Cards_Legendary"]
singleStitchList = ["Cards_Back_and_Info"]
doubleStitchList = ["Cards_Basic", "Cards_Exotic"]
backURL = "http://lukedowding.com/guildwars2-cardgame/game-files/tabletopsim/V1.1/Decks/GW-CCG-Back.jpg"
deckTemplateGlobal = os.path.join(dir_path, "deckTemplate.json")
cardTemplateGlobal = os.path.join(dir_path, "cardTemplate.json")
baseFileURL = "http://lukedowding.com/guildwars2-cardgame/game-files/tabletopsim/V1.1/"
globalCounter = 130


def main():
    global singleStitchList, legendaryList
    stitchLegenderies(legendaryList)
    imageStitch(doubleStitchList, doubleStitch=True)
    imageStitch(singleStitchList)
    stitchClasses(classList)

def stitchClasses(folderList):
    global dir_path, deckTemplateGlobal, backFilePath, cardTemplateGlobal, globalCounter
    deckTemplateOG = json.load(open(deckTemplateGlobal))
    cardTemplateOG = json.load(open(cardTemplateGlobal))
    for folder in folderList:
        deckids = []
        deckTemplate = deepcopy(deckTemplateOG)
        images = []
        cardNames = []
        classNames = []
        professionList = []
        professionCardList = []
        nameCount = 0
        profNameCount = 0
        curentDir = os.path.join(imagesPath, folder)
        for root, dirs, files in os.walk(curentDir):
            print(files)
            print(root)

            for fileName in files:
                professionName = fileName[11:-4]
                classNames.append(professionName)
                professionCardList.append(os.path.join(os.path.join(imagesPath, "Cards_Professions"), fileName))
                professionList.append(os.path.join(os.path.join(imagesPath, "Cards_Skills"), professionName))
                print(professionCardList)
            #images = map(Image.open, fileNameList)

        profCount = 0
        for professionPath in professionList:
            deckTemplate = deepcopy(deckTemplateOG)
            count = 0
            images = []
            for root, dirs, files in os.walk(professionPath):
                images.append(Image.open(professionCardList[profCount]))
                for fileName in files:
                    name = fileName[3:-4]
                    name = name.split("-")[1]
                    name = re.sub(r"(\w)([A-Z])", r"\1 \2", name)
                    print(name)
                    cardNames.append(name)
                    images.append(Image.open(os.path.join(root, fileName)))

            totalCards = len(images) * 2
            height, width = getDimentions(totalCards)
            widths, heights = zip(*(i.size for i in images))

            deckInfo = generateDeckIDInfo(height, width, totalCards)
            deckInfo["FaceURL"] = baseFileURL + "Decks" + "/" + os.path.basename(root) + ".jpg"
            print(baseFileURL + "Decks" + "/" + os.path.basename(root) + ".jpg")

            deckTemplate["ObjectStates"][0]["CustomDeck"].pop("110")
            deckTemplate["ObjectStates"][0]["CustomDeck"][globalCounter] = deckInfo
            deckIDs = generateDeckIDs(totalCards - 1)
            deckTemplate["ObjectStates"][0]["DeckIDs"] = deckIDs

            total_width = sum(widths)
            max_height = max(heights)

            new_im = Image.new('RGB', (widths[0] * width, heights[0] * height))

            x_offset = 0
            xCount = 0
            yCount = 0
            y_offset = 0
            iterCount = 0
            for im in images:
                if iterCount == 0:
                    name = classNames[profCount]
                    if xCount == width:
                        x_offset = 0
                        y_offset += im.size[1]
                        xCount = 0
                    new_im.paste(im, (x_offset, y_offset))
                    x_offset += im.size[0]
                    xCount += 1
                    cardTemplate = deepcopy(cardTemplateOG)
                    name = classNames[profCount]
                    cardTemplate["Nickname"] = name
                    cardTemplate["CardID"] = deckIDs[count]
                    print(deckIDs[count])
                    deckTemplate["ObjectStates"][0]["ContainedObjects"].append(cardTemplate)
                    count += 1
                else:
                    if xCount == width:
                        x_offset = 0
                        y_offset += im.size[1]
                        xCount = 0
                    new_im.paste(im, (x_offset, y_offset))
                    x_offset += im.size[0]
                    xCount += 1
                    cardTemplate = deepcopy(cardTemplateOG)
                    name = cardNames[nameCount]
                    cardTemplate["Nickname"] = name
                    cardTemplate["CardID"] = deckIDs[count]
                    print(deckIDs[count])
                    deckTemplate["ObjectStates"][0]["ContainedObjects"].append(cardTemplate)
                    count += 1

                    if xCount == width:
                        x_offset = 0
                        y_offset += im.size[1]
                        xCount = 0
                    cardTemplate = deepcopy(cardTemplateOG)
                    print(cardNames)
                    name = cardNames[nameCount]
                    nameCount += 1
                    cardTemplate["Nickname"] = name
                    cardTemplate["CardID"] = deckIDs[count]
                    print(deckIDs[count])
                    deckTemplate["ObjectStates"][0]["ContainedObjects"].append(cardTemplate)
                    count += 1
                    new_im.paste(im, (x_offset, y_offset))
                    x_offset += im.size[0]
                    xCount += 1

                iterCount += 1



            im = Image.open(backFilePath)
            new_im.paste(im, (im.size[0] * (width - 1), im.size[1] * (height - 1)))
            with open(os.path.basename(root) + '.json', 'w') as outfile:
                json.dump(deckTemplate, outfile)
                globalCounter += 1
            for path in savePaths:
                print(path)
                os.chdir(path)
                new_im.save(os.path.basename(root) + ".jpg")
            os.chdir(dir_path)
            new_im.save(imagesPath + os.path.basename(root) + ".jpg")
            profCount += 1


def stitchLegenderies(folderList):
    global backFilePath, globalCounter, deckTemplateGlobal, cardTemplateGlobal
    deckTemplateOG = json.load(open(deckTemplateGlobal))
    cardTemplateOG = json.load(open(cardTemplateGlobal))
    for folder in folderList:
        images = []
        deckTemplate = deepcopy(deckTemplateOG)
        curentDir = os.path.join(imagesPath, folder)
        fileNameList = []
        cardNames = []
        for root, dirs, files in os.walk(curentDir):
            if os.path.basename(root) not in folderList:
                print(files)
                print(root)
                fileNameList = []
                for fileName in files:
                    name = fileName[3:-4]
                    name = name.split("-")[0]
                    name = re.sub(r"(\w)([A-Z])", r"\1 \2", name)
                    print(name)
                    cardNames.append(name)
                    fileNameList.append(os.path.join(root, fileName))
                #images = map(Image.open, fileNameList)

                for fileName in fileNameList:
                    images.append(Image.open(fileName))
        totalCards = len(images) + 1
        height, width = getDimentions(totalCards)
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGB', (widths[0] * width, heights[0] * height))


        deckInfo = generateDeckIDInfo(height, width, totalCards)
        deckInfo["FaceURL"] = baseFileURL + "Decks" + "/" + os.path.basename(root) + ".jpg"
        print(baseFileURL + "Decks" + "/" + os.path.basename(root) + ".jpg")

        deckTemplate["ObjectStates"][0]["CustomDeck"].pop("110")
        deckTemplate["ObjectStates"][0]["CustomDeck"][globalCounter] = deckInfo
        deckIDs = generateDeckIDs(totalCards - 1)
        deckTemplate["ObjectStates"][0]["DeckIDs"] = deckIDs

        print(cardNames)

        x_offset = 0
        xCount = 0
        yCount = 0
        y_offset = 0
        count = 0
        nameCount = 0
        for im in images:
            if xCount == width:
                x_offset = 0
                y_offset += im.size[1]
                xCount = 0
            cardTemplate = deepcopy(cardTemplateOG)
            cardTemplate["CardID"] = deckIDs[count]
            name = cardNames[nameCount]
            cardTemplate["Nickname"] = name
            print(name)
            cardTemplate["CardID"] = deckIDs[count]
            print(deckIDs[count])
            deckTemplate["ObjectStates"][0]["ContainedObjects"].append(cardTemplate)
            nameCount += 1
            count += 1
            new_im.paste(im, (x_offset, y_offset))
            x_offset += im.size[0]
            xCount += 1

        im = Image.open(backFilePath)
        new_im.paste(im, (im.size[0] * (width - 1), im.size[1] * (height - 1)))
        with open(os.path.basename(root) + '.json', 'w') as outfile:
            json.dump(deckTemplate, outfile)
            globalCounter += 1
        for path in savePaths:
            print(path)
            os.chdir(path)
            new_im.save(os.path.basename(root) + ".jpg")
        os.chdir(dir_path)
        new_im.save(imagesPath + os.path.basename(root) + ".jpg")


def imageStitch(folderList, doubleStitch=False):
    global imagesPath, savePaths, deckTemplateGlobal, cardTemplateGlobal, baseFileURL, globalCounter
    deckTemplateOG = json.load(open(deckTemplateGlobal))
    cardTemplateOG = json.load(open(cardTemplateGlobal))
    for folder in folderList:
        curentDir = os.path.join(imagesPath, folder)

        for root, dirs, files in os.walk(curentDir):
            if os.path.basename(root) == folder:
                continue
            cardNames = []
            deckids = []
            deckTemplate = deepcopy(deckTemplateOG)
            if True:
                print(files)
                print(root)
                fileNameList = []
                for fileName in files:
                    name = fileName[3:-4]
                    name = name.split("-")[0]
                    name = re.sub(r"(\w)([A-Z])", r"\1 \2", name)
                    print(name)
                    cardNames.append(name)
                    fileNameList.append(os.path.join(root, fileName))
                #images = map(Image.open, fileNameList)
                images = []
                for fileName in fileNameList:
                    images.append(Image.open(fileName))
                if doubleStitch:
                    totalCards = len(images) * 2
                else:
                    totalCards = len(images)
                totalCards += 1
                height, width = getDimentions(totalCards)

                deckInfo = generateDeckIDInfo(height, width, totalCards)
                deckInfo["FaceURL"] = baseFileURL + "Decks" + "/" + os.path.basename(root) + ".jpg"
                print(baseFileURL + "Decks" + "/" + os.path.basename(root) + ".jpg")

                deckTemplate["ObjectStates"][0]["CustomDeck"].pop("110")
                deckTemplate["ObjectStates"][0]["CustomDeck"][globalCounter] = deckInfo
                deckIDs = generateDeckIDs(totalCards - 1)
                deckTemplate["ObjectStates"][0]["DeckIDs"] = deckIDs

                widths, heights = zip(*(i.size for i in images))

                total_width = sum(widths)
                max_height = max(heights)

                new_im = Image.new('RGB', (widths[0] * width, heights[0] * height))

                x_offset = 0
                xCount = 0
                yCount = 0
                y_offset = 0
                count = 0
                nameCount = 0
                print(cardNames)
                for im in images:
                    if xCount == width:
                        x_offset = 0
                        y_offset += im.size[1]
                        xCount = 0
                    cardTemplate = deepcopy(cardTemplateOG)
                    name = cardNames[nameCount]
                    cardTemplate["Nickname"] = name
                    print(name)
                    cardTemplate["CardID"] = deckIDs[count]
                    print(deckIDs[count])
                    deckTemplate["ObjectStates"][0]["ContainedObjects"].append(cardTemplate)
                    count += 1
                    new_im.paste(im, (x_offset, y_offset))
                    x_offset += im.size[0]
                    xCount += 1

                    if doubleStitch:
                        if xCount == width:
                            x_offset = 0
                            y_offset += im.size[1]
                            xCount = 0
                        cardTemplate = deepcopy(cardTemplateOG)
                        cardTemplate["CardID"] = deckIDs[count]
                        name = cardNames[nameCount]
                        cardTemplate["Nickname"] = name
                        print(name)
                        cardTemplate["CardID"] = deckIDs[count]
                        print(deckIDs[count])
                        deckTemplate["ObjectStates"][0]["ContainedObjects"].append(cardTemplate)
                        count += 1
                        new_im.paste(im, (x_offset, y_offset))
                        x_offset += im.size[0]
                        xCount += 1
                    nameCount += 1


                im = Image.open(backFilePath)
                new_im.paste(im, (im.size[0] * (width - 1), im.size[1] * (height - 1)))
                for path in savePaths:
                    print(path)
                    os.chdir(path)
                    new_im.save(os.path.basename(root) + ".jpg")
                os.chdir(dir_path)
                new_im.save(imagesPath + os.path.basename(root) + ".jpg")
                with open(os.path.basename(root) + '.json', 'w') as outfile:
                    json.dump(deckTemplate, outfile)
                    globalCounter += 1

def generateDeckIDInfo(height, width, totalCards):
    global backURL
    returnData = {}
    returnData["BackIsHidden"] = False
    returnData["UniqueBack"] = False
    returnData["BackURL"] = backURL
    returnData["FaceURL"] = ""
    returnData["NumWidth"] = width
    returnData["NumHeight"] = height
    return returnData

def generateDeckIDs(totalCards):
    returnList = []
    for i in range(0, totalCards):
        returnList.append(globalCounter * 100 + i)
    return returnList


def getDimentions(totalCards):
    base = sqrt(totalCards)
    baseCeil = ceil(base)
    baseFloor = floor(base)
    if baseCeil * baseFloor >= totalCards:
        return baseCeil, baseFloor
    return baseCeil, baseCeil

main()
