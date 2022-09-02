import cv2
import numpy as np
import pytesseract

def main():
    pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\\tesseract.exe"
    input = cv2.imread("testImages\IMG_1026.JPG") #to be replaced with arg
    
    topleft_C,botright_C,width,hieght = getCard(input)
    
    getCardName(topleft_C,botright_C,width,hieght,input)

    edditionReagion = [[int(topleft_C[0] + width*.75),int(topleft_C[1] + hieght*.50)],
                [int(botright_C[0] ),int(topleft_C[1])+ hieght*.50],
                [int(botright_C[0]),int(botright_C[1] - hieght*.30)],
                [int(topleft_C[0] + width*.75),int(botright_C[1] - hieght*.30)]]

    edditionImg = input[int(edditionReagion[0][1]):int(edditionReagion[2][1]),int(edditionReagion[0][0]):int(edditionReagion[2][0])]
    edditionImg = cv2.cvtColor(edditionImg, cv2.COLOR_BGR2GRAY)
    ret, edditionImg = cv2.threshold(edditionImg, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)

    input = cv2.rectangle(input, [int(edditionReagion[0][0]),int(edditionReagion[0][1])], [int(edditionReagion[2][0]),int(edditionReagion[2][1])], [255,0,0], 5)


    cv2.imshow('input', scaleImage(input,15))
   
    cv2.imshow('edditionImg', scaleImage(edditionImg,50))
    cv2.waitKey(0)

def getCard(input):
    #transforming the image into a binary image for contoure detection
    gray_img = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.adaptiveThreshold(gray_img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,7)

    #generates a "noiser" countor image that is good at finding the edge of the card
    contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[1::] #first contoure is always the entire image so we remove ir
    
    #now we loop thorugh all the contours and fins the largest one, ie the card
    large = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > large:
            cardConture = contour
            large = area

    #now we go through all the countors on the card and fine the top left and bottom right corner
    topleft = 99999999999999 
    botright = 0
    for cords in cardConture:
        temp = (cords[0][0] + cords[0][1])/2
        if(temp < topleft):
            topleft = temp
            topleft_C = cords[0]
        if(temp > botright):
            botright = temp
            botright_C = cords[0]
        
    #using the found corners we draw a squrea and create an array holding all 4 corners
    input = cv2.rectangle(input, topleft_C, botright_C, [0,0,255], 5)
    cardRegion = [[topleft_C[0],topleft_C[1]],[botright_C[0],topleft_C[1]],[botright_C[0],botright_C[1]],[topleft_C[0],botright_C[1]]]

    
    #using the card object we draw a square around a text region and create an array holding all 4 corners
    hieght = cardRegion[2][1] - cardRegion[0][1]
    width = cardRegion[1][0] - cardRegion[0][0]

    return(topleft_C,botright_C,width,hieght)

def getCardName(topleft_C,botright_C,width,hieght,input):
    #generating the rectangle where the computer will look for the title
    textRegion = [[int(topleft_C[0] + width*.05),int(topleft_C[1])],
                [int(botright_C[0] - width*.25),int(topleft_C[1])],
                [int(botright_C[0] - width*.25),int(botright_C[1] - hieght*.89)],
                [int(topleft_C[0] + width*.05),int(botright_C[1] - hieght*.89)]]
    #draws the rectangle on the image
    input = cv2.rectangle(input, [int(textRegion[0][0]),int(textRegion[0][1])], [int(textRegion[2][0]),int(textRegion[2][1])], [0,255,0], 5)
    #creates a new image that is only the reagion and turns it to a binary image
    textHeader = input[int(textRegion[0][1]):int(textRegion[2][1]),int(textRegion[0][0]):int(textRegion[2][0])]
    textHeader = cv2.cvtColor(textHeader, cv2.COLOR_BGR2GRAY)
    ret, textHeader = cv2.threshold(textHeader, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    #passes the binary image into the pytesseract ai to figure out the words
    text = cleanUpText(pytesseract.image_to_string(textHeader))
    print(text)
    return(textHeader, textRegion)

def scaleImage(img, scale_percent):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
  
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return resized

def cleanUpText(input):
    while(True):
        if(input[0].isalpha()):
            break
        else:
            input = input[1::]
    while(True):
        if(input[-1].isalpha()):
            break
        else:
            input = input[:-1]
    return(input)

if __name__ == "__main__":
    main()