# ChromcastImageDownloader
The application is designed to upload images from the Google Image Collection. These images are shown by Google Chromecast on the TV while the user is not playing content on it. Shuffle shows the images in random order. I wanted to use some of these images as references for my artwork but had difficulty getting a specific image so I decided to develop applications to be able to upload them all locally to my computer.
How to use the application
First of all, you need to have Python installed on your computer.
Create a directory for the application
Enter the directory
Download the imagerabber.zip file to this directory and unzip it. You should get the imagegrabber folder and startgrabber.py and requirements.txt files in your directory.
I highly recommend that you create a virtual environment for this application with the command

python -m venv venv

After creating the virtual environment, activate it with the command

venv\Scripts\Activate

The next step is to install the packages necessary for the application to work. Type a command 

pip install -r requirements.txt

and press Enter.
Application is ready to use
The application is launched by the command

python startgrabber.py

You can use next parameters when start application
-  -h, --help  show this help message and exit
-  -m         Paste metadata into filenames of saved images\
              Some images accompanied with photographer name. If you add this parameter then photographer name will be included into file name with saved image
              
-  -n N        Number of new images for download (default = 10)\
              This parameter defines ho many images will be downloaded while single program execution.
              Image collection very big and it takes a lot of time to download all images in one session. You can do it starting application several times and downloading imeges by small portions (for example 20 or 50 imeges)
              Application creates a track of dowloaded images in file retrievedimages.json so it doesn't download the same image twice.
-  -p P       Path where to save downloaded images. If omitted images will be saved in directory    
              where script started.\
              Path where you want to save downloaded images. File retrievedimages.json will be created in the same directory
-  -v V        Verbose level.(default = 0, possible: 0, 1)

Command example:\
python imagegrabber.py -m -n 40 -p C:\Users\Username\Pictures\Chromcast -v 0
