# from platform import system
# from tqdm import tqdm
# from time import sleep
# import pandas as pd
# import numpy as np
# import os

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# movieIds = []

# with open('movieIds.txt', 'r') as filehandle:
#     for line in filehandle:
#         currentPlace = line[:-1]
#         movieIds.append(int(currentPlace))
        
# ite = 1
# if not (ite==6):
#     movieIds = movieIds[((ite-1)*100000):(ite*100000)]
# else:
#     movieIds = movieIds[((ite-1)*100000):len(movieIds)]

# PATH = "C:\Program Files (x86)\chromedriver.exe" if ("Windows" in system()) else "/usr/bin/chromedriver"

# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--window-size=1920x1080")
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')

# driver = webdriver.Chrome(PATH, options=chrome_options)

# outName = f"movieRecs-{ite}.csv"

# df = pd.DataFrame(columns=["movieId","Recommendations"]) if ( not ( os.path.exists(outName) ) ) else pd.read_csv(outName)

# movieIds = [ide for ide in movieIds if ide not in [int(ida) for ida in list(df.movieId.values)]]

# cmd = f"aws s3 cp {outName} s3://rnrecos/"
# j = 0
# for i in tqdm(movieIds):
#     j += 1
#     if ( (j%5000) == 0 ):
#         df.to_csv(outName,index=False)
#     try:
#         if ( type(i)  in [np.int, np.int0, np.int16, np.int32, np.int64, np.int8, np.intc, np.integer, type(1)] ):
#             recos = []
#             print(i,"\n")
#             driver.get(f"https://www.themoviedb.org/movie/{i}")
#             driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
#             resc = WebDriverWait(driver, 1.5).until(EC.presence_of_element_located((By.ID, "recommendation_scroller")))
#             if not ( resc == None ):
#                 rescdivs = resc.find_elements_by_tag_name("div")
#                 if not (rescdivs == None):
#                     if ( len(rescdivs) > 0 ):
#                         ds = [d for d in rescdivs if (d.get_attribute("class") == 'item mini backdrop mini_card')]
#                         if not (ds == None):
#                             if ( len(ds) > 0 ):
#                                 hrs = [dsi.find_element_by_tag_name("a") for dsi in ds]
#                                 for hr in hrs:
#                                     if not ( hr == None ):
#                                         a = hr.get_attribute("href")
#                                         if not ( a == None ):
#                                             sp = a.split("/")[-2:]
#                                             print(sp,"\n")
#                                             if (len(sp) == 2):
#                                                 recos.append(sp)
#                                             else:
#                                                 print("Href Split Length Error\n")
#                                         else:
#                                             print("No Href in a Tag\n")
#                                     else:
#                                         print("No a Tag Recommendation Card\n")
#                                 if (len(recos)>0):
#                                     df = df.append({"movieId":i,"Recommendations":recos},ignore_index=True)
#                                 else:
#                                     df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#                             else:
#                                 print("No of Recommendation Cards is 0\n")
#                                 df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#                         else:
#                             print("No Recommendation Card\n")
#                             df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#                     else:
#                         print("Number of Divs in Recommendation Scroller is 0\n")
#                         df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#                 else:
#                     print("No Divs in Recommendation Scroller\n")
#                     df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#             else:
#                 print("No Recommendation Scroller\n")
#                 df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#     except TimeoutException:
#         print("No Recommendations due to timeout\n")
#         df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#     except Exception as e:
#         eStr = str(e)
#         if ("recommendation_scroller" in eStr):
#             print("No Recommendations\n")
#             df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#         else:
#             print("New Error: ", eStr, "\n")
#             df = df.append({"movieId":i,"Recommendations":None},ignore_index=True)
#             sleep(20)

# df.to_csv(outName,index=False)
# if not ("Windows" in system()):
#     os.system(cmd)
from os import listdir
from os import system

for nam in listdir():                     
    if (("Recs" in nam) and (".csv" in nam)):
        system(f"aws s3 cp {nam} s3://rnrecos/")