
#-----------------------------------------------------------------------
# Copyright (c) 2023, Alexander Zyuzin.
#
# This file is part of  Chromcast Image Downloader.
#
#
# Purpose:
#      Start application.
#
# --------------------------------------------------------------------------
BASE_URL = "https://clients3.google.com/cast/chromecast/home"

import time
from imagegrabber.lib import grabber

grb = grabber()
grb.open(BASE_URL)
startTime = time.time()
number_of_files_downloaded = grb.grabImages()
print("Requested number of files reached.")
grb.close()
print("{} files downloaded\n.".format(number_of_files_downloaded))
grb.printTimeSpan(startTime, time.time())
print("Job completed.")