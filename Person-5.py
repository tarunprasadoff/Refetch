from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
import pandas as pd
import time
import csv
from datetime import datetime
from tqdm.notebook import tqdm

date = str(datetime.date(datetime.now()))
outName = date + '-People-5.csv'

idList = list(range(1000001,1250001))

def handleEmptyGet(tag, getString):
    if(tag != None):
        return tag.get(getString)
    else:
        return None

data = pd.DataFrame(columns=['personId','name','about','imgUrl'])

data.to_csv(outName, index=False)

with open(outName, 'a', encoding="utf-8") as newFile:
    newFileWriter = csv.writer(newFile)
    j = 1
    start = time.time()
    for i in tqdm(idList):

        try:
            uClient = uReq("https://www.themoviedb.org/person/" + str(i))
            bs = soup(uClient.read(), "html.parser")
            uClient.close()
            personId = i
            
            nameTag = bs.find("h2",{"class":"title"})
            if not (nameTag == None):
                name = nameTag.getText()
            else:
                name = None
                
            aboutDiv = bs.find("div",{"class": "content fade_text"})
            about = []
            if not (aboutDiv == None):
                aboutPs = aboutDiv.findAll("p")
                for p in aboutPs:
                    about.append(p.getText())
                    
            imgDivTag = bs.find("div",{"class":"image_content"})
            if not (imgDivTag == None):
                imgTag = imgDivTag.find("img")
                if not (imgTag == None):
                    imgUrl = handleEmptyGet(imgTag,"data-src")
                    if not (imgUrl == None):
                        imgUrl = ('https://www.themoviedb.org' + imgUrl)

            data = data.append({'personId': personId,'name':name,'about':about,'imgUrl':imgUrl}, ignore_index=True)

            print(personId, name)

            if j > 300:
                j = 1
                print("Writing to CSV")
                newFileWriter.writerows(data.values)
                pd.DataFrame(columns=['personId','name','about','imgUrl'])
            else:
                j += 1
                
        except Exception as e:
            eString = str(e)

            if "404" in eString:
                print(str(i) + ": No Movie")
            elif "429" in str(e):
                print("Too many Requests Error at index " +
                      str(i) + ". Sleeping for 30 seconds")
                time.sleep(30)
                i = i-1
            elif "104" in str(e):
                print("Connection Reset by Peer Error at index " +
                      str(i) + ". Sleeping for 30 seconds")
                time.sleep(30)
                i = i-1
            elif "10060" in str(e):
                print("Connection Reset by Peer Error at index " +
                      str(i) + ". Sleeping for 30 seconds")
                time.sleep(30)
                i = i-1
            else:
                print("New Error: " + eString)
                time.sleep(30)

            continue
        finally:
            i += 1

    print("Writing to CSV")
    newFileWriter.writerows(data.values)
    print(f"Runtime of the program is {time.time() - start}")


import os
os.system('aws s3 cp ./' + outName + 's3://rollinowscrape/')