from platform import system
from tqdm import tqdm
from time import sleep
import pandas as pd
import numpy as np
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

peopleIds = []

with open('peopleIds.txt', 'r') as filehandle:
    for line in filehandle:
        currentPlace = line[:-1]
        peopleIds.append(int(currentPlace))
        
ite = 3
if not (ite==20):
    peopleIds = peopleIds[((ite-1)*100000):(ite*100000)]
else:
    peopleIds = peopleIds[((ite-1)*100000):len(peopleIds)]

PATH = "C:\Program Files (x86)\chromedriver.exe" if ("Windows" in system()) else "/usr/bin/chromedriver"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(PATH, options=chrome_options)

outName = f"peopleRecs-{ite}.csv"

df = pd.DataFrame(columns=["peopleId","Recommendations"]) if ( not ( os.path.exists(outName) ) ) else pd.read_csv(outName)

peopleIds = [ide for ide in peopleIds if ide not in [int(ida) for ida in list(df.peopleId.values)]]

cmd = f"aws s3 cp {outName} s3://rnrecos/"
j = 0
for i in tqdm(peopleIds):
    j += 1
    if ( (j%5000) == 0 ):
        df.to_csv(outName,index=False)
    try:
        if ( type(i)  in [np.int, np.int0, np.int16, np.int32, np.int64, np.int8, np.intc, np.integer, type(1)] ):
            recos = []
            print(i,"\n")
            driver.get(f"https://www.themoviedb.org/person/{i}")
            #driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            resc = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "known_for_scroller")))
            if not ( resc == None ):
                rescdivs = resc.find_elements_by_tag_name("a")
                if not (rescdivs == None):
                    if ( len(rescdivs) > 0 ):
                        for hr in rescdivs:
                            if not ( hr == None ):
                                a = hr.get_attribute("href")
                                if not ( a == None ):
                                    sp = a.split("/")[-2:]
                                    print(sp,"\n")
                                    if (len(sp) == 2):
                                        recos.append(sp)
                                    else:
                                        print("Href Split Length Error\n")
                                else:
                                    print("No Href in a Tag\n")
                            else:
                                print("No a Tag Recommendation Card\n")
                        if (len(recos)>0):
                            df = df.append({"peopleId":i,"Recommendations":recos},ignore_index=True)
                        else:
                            df = df.append({"peopleId":i,"Recommendations":None},ignore_index=True)
                    else:
                        print("Number of a s in Recommendation Scroller is 0\n")
                        df = df.append({"peopleId":i,"Recommendations":None},ignore_index=True)
                else:
                    print("No a s in Recommendation Scroller\n")
                    df = df.append({"peopleId":i,"Recommendations":None},ignore_index=True)
            else:
                print("No Recommendation Scroller\n")
                df = df.append({"peopleId":i,"Recommendations":None},ignore_index=True)
    except TimeoutException:
        print("No Recommendations due to timeout\n")
        df = df.append({"peopleId":i,"Recommendations":None},ignore_index=True)
    except Exception as e:
        eStr = str(e)
        if ("known_for_scroller" in eStr):
            print("No Recommendations\n")
            df = df.append({"peopleId":i,"Recommendations":None},ignore_index=True)
        else:
            print("New Error: ", eStr, "\n")
            df = df.append({"peopleId":i,"Recommendations":None},ignore_index=True)
            sleep(20)

df.to_csv(outName,index=False)
if not ("Windows" in system()):
    os.system(cmd)