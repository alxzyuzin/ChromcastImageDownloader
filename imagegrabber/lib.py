HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'

#BASE_URL = "https://clients3.google.com/cast/chromecast/home"
RETRIEVED_IMAGES_LIST_FILE = "retrievedimages.json"
MAX_IMAGE_REPEAT_COUNTER = 10
#RETRIEVE_TIMEOUT = 100
CONSTANT_FILE_NAME_PART = "ChromCastImage_"


from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import os
import json
import time

class grabber:
    saveErrorMsg = "Can't save list of downloaded images"
    restoreErrorMsg = "Can't restore list of downloaded images"
    noPermissionErrorMsg = 'No permissions to read file "{}" {}'
    OSErrorMsg = 'OS error "{}", file "{}"'
    
    
    
    def __init__(self):
        self.retrievedImagesIDs = {}
        self._parseArgs()
        self.retrFilesListName = self.target_dir + "\\" +RETRIEVED_IMAGES_LIST_FILE

    def open(self, url):
        
        try:
            self.webdrv = webdriver.Chrome()
            self.webdrv.get( url)
            
        except WebDriverException as ex:
            print('Can not open Chromcast Home site.')
            print("StrError:{} WinError".format(ex.msg))
            print("Check network connection.")
            print("Application exited.")
            self.webdrv.close()
            return False

        # Restore list of downloaded images
        # File retrievedimages.json contains dictionary where keys are ids
        # of downloaded images and values are file names
        # If this file exist load this list first
        if os.path.exists(self.retrFilesListName):
            try:
                with open(self.retrFilesListName, "r") as lf:
                    self.retrievedImagesIDs = json.load(lf)
            except PermissionError as pe:
                print(self.restoreErrorMsg)
                print(self.noPermissionErrorMsg.format(self.retrFilesListName, pe.strerror))
                return False
            except OSError as oe:
                print(self.restoreErrorMsg)
                print(self.OSErrorMsg.format(oe.strerror, self.retrFilesListName))
                return False

        return True

    def close(self):
        # Save dictionary of retrieved images iD's and file names
        try:
            with open(self.retrFilesListName, "w") as lf:
                json.dump(self.retrievedImagesIDs, lf)
            print("Close webdriver.")    
            self.webdrv.close()
            return True
        except PermissionError as pe:
                print(self.saveErrorMsg)
                print(self.noPermissionErrorMsg.format(self.retrFilesListName, pe.strerror))
                return False
        except OSError as oe:
                print(self.saveErrorMsg)
                print(self.OSErrorMsg.format(oe.strerror, self.retrFilesListName))
                return False

    def printTimeSpan(self,st, et):
        timeSpan = et - st
        h = int((timeSpan) / 3600)
        ms = timeSpan % 3600
        m = int(ms / 60)
        s = int(ms % 60)
        print("Download time: {}h {}m {}s".format(h, m, s))

    def _parseArgs(self):
        '''
        Parse command line arguments
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
        self.target_dir = args.p
        self.n_of_fles = args.n
        self.use_metadata = args.m
        td = "Current directory."
        # Remove traling slashes from destination path (target_dir)
        if self.target_dir != "":
            while self.target_dir[len(self.target_dir) - 1] == "\\":
                self.target_dir = self.target_dir[:len(self.target_dir)-1]
  
    def downloadImages(self):
        if self.target_dir == "":
            td = "Current directory"
        else:
            td = self.target_dir
        print("\nGrabber started\n")
        print("Target directory:{}\nNumber of images to download: {}.".format(td, self.n_of_fles ))
        if self.use_metadata:
            print("Image metadata will be pasted into filenames.\n")

        filesDownloaded = 0
        print(HIDE_CURSOR, end="")
        filesDownloaded = self._grabImages()
        print(SHOW_CURSOR, end = "")
        return filesDownloaded
        
    def _extractImageURL(self, webpage):
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

    def _getMetadataLine2(self):
        '''
        Get tag content with id = "metadata-line-2
            Return:
            Tag content : String
        '''
        page = self.webdrv.page_source
        metadata = page[page.find('<div id="metadata-line-2"'):]
        metadata = metadata[:metadata.find("</div>")]
        metadata = metadata[metadata.find(">")+1:]
        return metadata.replace(" ","")

    def _getNewImageURL(self, oldImageURL ):
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
            imageURL = self._extractImageURL(self.webdrv.page_source)
            if oldImageURL != imageURL:
                break          
            print(".", end = "", flush = True)
            time.sleep(1)
        return imageURL

    def _downloadOneImage(self, img_url, filename):
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

        import requests
        from requests.exceptions import HTTPError, ConnectTimeout, ConnectionError
        
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

    def _grabImages(self):
        imgIDRepeatCounter = 0
        img_ID_2 = None
        retrievedImagesIDs = {}
        imageGrabbed = 0
            
        fnumber = len(self.retrievedImagesIDs)
        image_url = ""
    
        while imageGrabbed < self.n_of_fles:
            image_url = self._getNewImageURL( image_url)

            metadata = ""
            if self.use_metadata:
                metadata = self._getMetadataLine2()
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
                if self._downloadOneImage(image_url_with_pars, self.target_dir + "\\" + filename): # File sucsessfully downloaded and saved
                    imageGrabbed+=1
                    fnumber+=1
                    self.retrievedImagesIDs[img_ID] = filename
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
        
        return imageGrabbed