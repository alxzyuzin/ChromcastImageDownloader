

RETRIEVED_IMAGES_LIST_FILE = "retrievedimages.json"
targetdir =  "C:\\Users\\alxzy\\Pictures\\ChromCast"

import json
import os
retrFilesListName = targetdir + "\\" +RETRIEVED_IMAGES_LIST_FILE
if os.path.exists(retrFilesListName):
    with open(retrFilesListName, "r") as lf:
        retrievedImagesIDs = json.load(lf)
print("Number ID's in {} : {}".format(RETRIEVED_IMAGES_LIST_FILE, len(retrievedImagesIDs)))