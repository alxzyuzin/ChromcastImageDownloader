BASE_URL = "https://clients3.google.com/cast/chromecast/home"
#from urllib import requests
import requests
import json

def writeData(fname, data):
    with open(fname, 'w') as f:
        f.write(str(data))



def main():

    responce  = requests.get("https://ccp-lh.googleusercontent.com/proxy/Zs1xvtR8Pnbsw9VhaX04NIGjsJVpRvxZM_2eOE7xfotFD9gB98pwVrn-Rw5zllAaJ6x59ROn0XLAo1i6kDYjfEPvJ2IbO7_SB41YoDBoztiKBoYj9y76pogQvvJKdd2dhNe2Kn-zloSLXmLEvGSjW9gHS_R3UDCf-1bU6ivvsyEOS0j5LTmK-xr7M84dkx3xCqy9NoZl0pj-xAXaA2Z0igwVLQtCowmk8pY=w1920-h1080-p-k-no-nd-mv")
    #responce = request.urlopen(BASE_URL)
    content = responce.content
    with open("image.jpg","wb") as hp:
        hp.write(content)
    #constdic = getScriptConstants(pagecontent)
    #imgdata = getImageData(constdic["initialStateJson"])
    print("Work is done")

if __name__ == "__main__":
    main()