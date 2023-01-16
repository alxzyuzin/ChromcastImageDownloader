#-----------------------------------------------------------------------
# Copyright (c) 2023, Alexander Zyuzin.
#
# This file is part of  Chromcast Image Downloader.
#
# Contains application functions.      .
# --------------------------------------------------------------------------

BASE_URL = "https://clients3.google.com/cast/chromecast/home"
RETRIEVED_IMAGES_LIST_FILE = "retrievedimages.json"
MAX_IMAGE_REPEAT_COUNTER = 10
RETRIEVE_TIMEOUT = 100
CONSTANT_FILE_NAME_PART = "ChromCastImage_"

HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import requests
import os.path
import time
import json
import sys
from requests.exceptions import HTTPError, ConnectTimeout, ConnectionError
#from progress.bar import Bar
#from progress.spinner import Spinner


def removeTrailedSlashes( instr):
    if instr != None:
        res = instr + ""
        while res[len(res) - 1] == "\\":
             res = res[:len(res)-1]
    return res
def writeData(fname, data):
    with open(fname, 'w') as f:
        f.write(str(data))

def getMetadataLine2( _webdrv ):
    '''
    Get tag content with id = "metadata-line-2
    Parameter
        page : String
    Return:
        Tag content : String
    '''
    page = _webdrv.page_source
    metadata = page[page.find('<div id="metadata-line-2"'):]
    metadata = metadata[:metadata.find("</div>")]
    metadata = metadata[metadata.find(">")+1:]
    #metadata = metadata[:metadata.find("<"):]
    return metadata.replace(" ","")

def extractImageURL(webpage):
    '''
    Extract extract image URL from web page
    Parameter
        webpage : String  web pge content
    Return
        Image URL : String URL of image for downloading
    '''
    # Extract img tag content from page
    imgTagData = webpage[webpage.find('<img id="picture-background"'):]
    imgTagData = imgTagData[:imgTagData.find(">")]

    # Convert img tag attributes to dictionary
    imgTagAttribsLst = imgTagData.split(" ")
    attribs = {}
    for atr in imgTagAttribsLst[1:]:
        if "=" in atr:
            atrpair = atr.split("=")
            attribs[atrpair[0]] = atrpair[1].replace('"',"")
         
    # image URL is value of keys src and ng-src
    return attribs["ng-src"]


def getNewImageURL(_webdrv, _oldImageURL):
    '''
    Wait until browser update image an return URL of new image
    
    Parameters:
        _webdrw: Object  - WEb driver
        _oldImageURL : String - URL of allready downloaded image
    
    Return:
        String - URL of new image 
    '''  
    # Wait while image in browser will be refreshed
    print("Wait for next image", end = "")
    while True:
        imageURL = extractImageURL(_webdrv.page_source)
        if _oldImageURL != imageURL:
            break          
        print(".", end = "", flush = True)
        time.sleep(1)
    return imageURL


    
def downloadImage(img_url, filename):
    '''
    Download image and save it in designated directory
    for image file name used last part of URL 
    Parameters:
        img_url : String - image URL to download 
        fileNumber : Integer - number file to save 
        save_dir : String - directory where to save image file
                 if  save_dir is None function save 
                 file in current directory
    Return 
        file_ID if file downloaded
        else None
    '''
    
    
    # File ID = last part of file URL
    # sometime this part is too long to be used as file name
    # so we save file id in the list of ID's retrieved files
    # We use this list to check if file allready downloaded
    #file_ID = img_url.split("/")[-1]
    #mtdt  = metadata.replace(" ","")
    #filename = "ChromCastImage_" + mtdt + str(fileNumber) + ".jpg" 
    #pathAndFilename = save_dir + "\\" + filename
    print("File name : {}".format(filename))
    try:
        img_data = requests.get(img_url).content
    except ConnectTimeout as ct:
        print("ConnectTimeout")
        return False
    except ConnectionError as ce:
        print("ConnectionError")
        return False
    except HTTPError as he:
        print("HTTPError")
        return False
    except Exception as ex:
        print('Error retrieving image "{}"'.format(img_url))
        print(ex)
        print("StrError:{} WinError {}".format(ex.strerror, ex.winerror))
        return False
    else:
        try:
            with open(filename, 'wb') as handler:
                handler.write(img_data)
                print("File {} saved".format(filename))
                return True
        except  IOError as ex:
            print('Error saving file "{}"'.format(filename))
            print("StrError:{} WinError {}".format(ex.strerror, ex.winerror))
            return False
        
def grabImages(targetdir, noffles, usemetadata):
    imgIDRepeatCounter = 0
    img_ID_2 = None
    retrievedImagesIDs = {}
    
    try:
        webdrv = webdriver.Chrome()
        webdrv.get(BASE_URL)
    except WebDriverException as ex:
        print('Can not open Chromcast Home site.')
        print("StrError:{} WinError".format(ex.msg))
        print("Check network connection.")
        print("Application exited.")
        webdrv.close()
        return 0
    # First time wait 20 sec while browser refresh image and fill
    # metadata placeholder with real data
    #time.sleep(20)
    imageGrabbed = 0
   # File retrievedimages.json contains dictionary where keys are ids
   # of downloaded images and values are file names
   # So  if this file exist load this list first
    retrFilesListName = targetdir + "\\" +RETRIEVED_IMAGES_LIST_FILE
    if os.path.exists(retrFilesListName):
        with open(retrFilesListName, "r") as lf:
            retrievedImagesIDs = json.load(lf)
            
    fnumber = len(retrievedImagesIDs)
    image_url = ""
    
    while imageGrabbed < noffles:
        image_url = getNewImageURL(webdrv, image_url)

        metadata = ""
        if usemetadata:
            metadata = getMetadataLine2(webdrv)
            if len(metadata) > 0:
                metadata += "_"
           
        print("\nImage url : {}.".format(image_url))
        print("Image metadata : {}.".format( metadata))
        # Check if file already downloaded and saved
        img_ID = image_url.split("/")[-1]
        if img_ID not in retrievedImagesIDs:  # if file with this ID was not downloade and saved      
            filename = CONSTANT_FILE_NAME_PART + metadata + str(fnumber) + ".jpg" 
            # Add some parameters to image URL and download image
            image_url_with_pars = image_url + "=w1920-h1080-p-k-no-nd-mv"          
            if downloadImage(image_url_with_pars, targetdir + "\\" + filename): # File sucsessfully downloaded and saved
                imageGrabbed+=1
                fnumber+=1
                retrievedImagesIDs[img_ID] = filename
                # Check if max try of downloading the same image exided or not            
                if img_ID_2 == img_ID:
                    imgIDRepeatCounter += 1
                    if imgIDRepeatCounter > MAX_IMAGE_REPEAT_COUNTER:
                        print("Repeated images counter exeed maximum value.\nCheck internet connection.")
                        break
                else:
                    img_ID_2 = img_ID
                    imgIDRepeatCounter = 0
            else:
                print("Check network connection.")
                print("Application exited.")
                break
        
    # Save dictionaey of retrieved images iD's and file names
    with open(retrFilesListName, "w") as lf:
        json.dump(retrievedImagesIDs, lf)
    webdrv.close()
    return imageGrabbed



def parseArgsAndStart():
    '''
    Parse command line arguments and start image downloading
    '''
    import argparse
    arser = argparse.ArgumentParser(
                    prog = 'grabber',
                    description = 'This program download images from Chromcast web site and save it to the designatet directory',
                    )

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", action="store_true", help = "Paste metadata into filenames of saved images")
    parser.add_argument("-n", type=int, default = "10", help = "Number of new images for download (default = 10)")
    parser.add_argument("-p", type=str, default="", help = "Path where to save downloaded images. If omitted images will be saved in directory where script started.")

    #image size parameters
    #parser.add_argument("-w", type=int, default = "1920", help = "Downloaded image width (default = 1920)")
    #parser.add_argument("-h", type=str, default = "1080", help = "Downloaded image height (default = 1080).")

    args = parser.parse_args()
    target_dir = args.p
    n_of_fles = args.n
    use_metadata = args.m
    td = "Current directory."
    if target_dir != "":
        while target_dir[len(target_dir) - 1] == "\\":
            target_dir = target_dir[:len(target_dir)-1]
                
    print("\nGrabber started\n")
    print("Target directory:{}\nNumber of images to download: {}.".format(target_dir, n_of_fles ))
    if use_metadata:
        print("Image metadata will be pasted into filenames.\n")

    i=0
    print(HIDE_CURSOR, end="")
    i = grabImages(target_dir, n_of_fles, use_metadata)
    print(SHOW_CURSOR, end = "")
    print("Job completed.")
    print("{} files downloaded\n.".format(i))