from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
import pandas as pd
import time
import csv
from datetime import datetime
from tqdm import tqdm

date = str(datetime.date(datetime.now()))
outName = date + '-TV.csv'

idList = list(range(1, 150001))

def handleEmptyGet(tag, getString):
    if(tag != None):
        return tag.get(getString)
    else:
        return None

data = pd.DataFrame(columns=['tvId', 'title', 'release', 'userRating', 'synopsis',\
                             'genres', 'thumbnailUrl', 'Original Language', 'cast',\
                             'trailerOrPromoUrl', 'isIndianOTT', 'backdropUrl', 'keywords', 'watch','seasonData'])

data.to_csv(outName, index=False)

with open(outName, 'a', encoding="utf-8") as newFile:
    newFileWriter = csv.writer(newFile)
    j = 1
    start = time.time()
    for i in tqdm(idList):

        try:
            uClient = uReq("https://www.themoviedb.org/tv/" + str(i))
            bs = soup(uClient.read(), "html.parser")
            uClient.close()
            tvId = i

            isIndianOTT = False
            container = bs.find("div", {"class": "title ott_false"})
            if(container == None):
                container = bs.find("div", {"class": "title ott_true"})
                if(container != None):
                    isIndianOTT = True

            title = container.find("h2").find("a").getText()

            release = container.find("span").getText().replace(
                "(", "").replace(")", "")
            if(len(release) != 4):
                release = None

            userRating = handleEmptyGet(
                bs.find("div", {"class": "user_score_chart"}), "data-percent")

            synopsis = bs.find(
                "div", {"class": "overview"}).find("p").getText()

            genres = []
            for genreTag in bs.find("span", {"class": "genres"}).findAll("a"):
                genres.append(genreTag.getText())

            thumbnailUrl = handleEmptyGet(
                bs.find("img", {"class": "poster lazyload"}), "data-src")

            section = bs.find("section", {"class": "facts"})
            language = section.find(
                "bdi", string="Original Language").parent.parent.getText()
            if(language != None):
                language = language.replace("Original Language ", "")

            temp = bs.find("ol", {"class": "people scroller"})
            temp = bs.findAll("li", {"class": "card"})
            cast = []
            for cur in temp:
                actorUrl = 'https://www.themoviedb.org' + \
                    handleEmptyGet(cur.a, "href")
                actor = handleEmptyGet(cur.img, "alt")
                actorImageUrl = handleEmptyGet(cur.img, "data-src")
                character = cur.find("p", {"class": "character"}).getText()
                cast.append(
                    {"actor": actor, "actorImageUrl": actorImageUrl, "character": character})

            trailerUrlId = handleEmptyGet(
                bs.find("a", {"class": "no_click play_trailer"}), "data-id")
            trailerUrl = None
            if(trailerUrlId != None):
                trailerUrl = 'www.youtube.com/watch?v=' + str(trailerUrlId)

            backdropUrl = handleEmptyGet(
                bs.find("img", {"class": "backdrop"}), "data-src")

            keywordsFetch = bs.find("section", {"class": "keywords"})
            keywords = []
            if(keywordsFetch != None):
                for a in keywordsFetch.find_all("a"):
                    keywords.append(a.getText())
            
            watchList=[]
            if(isIndianOTT):
                try:
                    uClient = uReq(
                        "https://www.themoviedb.org/tv/" + str(i) + "/watch")
                    bsWatch = soup(uClient.read(), "html.parser")
                    uClient.close()
                    print(str(i) + " Watch")
                    if(bsWatch.find("p", {"class": "no_offers"}) == None):
                        providers = bsWatch.find_all(
                            "div", {"class": "ott_provider"})
                        for provider in providers:
                            otts = provider.find_all(
                                "li", {"class": "ott_filter_best_price"})
                            temp = []
                            nature = provider.h3.getText()
                            for ott in otts:
                                a = ott.div.a
                                description = handleEmptyGet(a, "title")
                                split = description.split("on ")
                                if nature == 'Stream':
                                    val = {"description": description, "link": handleEmptyGet(a, "href"), "source": split[len(
                                        split)-1], "sourceImageUrl": handleEmptyGet(a.img, "src")}
                                else:
                                    price = provider.find(
                                        "span", {"class": "price"})
                                    if price != None:
                                        price = price.getText()
                                    quality = provider.find(
                                        "span", {"class": "presentation_type"})
                                    if quality != None:
                                        quality = quality.getText()
                                    val = {"description": description, "link": handleEmptyGet(a, "href"), "source": split[len(
                                        split)-1], "sourceImageUrl": handleEmptyGet(a.img, "src"), "price": price, "quality": quality}
                                temp.append(val)
                            watchList.append({nature: temp})
                except Exception as e2:
                    print("Watch Fetch Error")
                    watchList = []
                    
            seasonData = []
            
            try:
                uClient2 = uReq("https://www.themoviedb.org/tv/" + str(i) + "/seasons")
                bs2 = soup(uClient2.read(), "html.parser")
                uClient2.close()

                seasons = bs2.find_all("div",{"class":"season"})

                for season in seasons:
                    currSeason = {}
                    currSeason["seasonName"] = season.find("h2").getText()
                    currSeason["seasonYear"] = season.find("h4").getText().split("|")[0].replace(" ","")
                    currSeason["episodeNo"] = int(season.find("h4").getText().split("|")[1].split()[0])
                    currSeason["ps"] = season.findAll("p")
                    if len(currSeason["ps"]) == 0:
                        currSeason["seasonDesc"] = season.find("div",{"class":"season_overview"}).getText()
                        currSeason["seasonReleaseSentence"] = None
                    else:
                        currSeason["seasonReleaseSentence"] = currSeason["ps"][0].getText()
                        currSeason["seasonDesc"] = None
                        if len(currSeason["ps"])>=2:
                            currSeason["seasonDesc"] = currSeason["ps"][1].getText()
                    currSeason["seasonImgUrl"] = handleEmptyGet(season.find("img"), "src")
                    if not (currSeason["seasonImgUrl"] == None):
                        currSeason["seasonImgUrl"] = 'themoviedb.org' + currSeason["seasonImgUrl"]
                    seasonData.append(currSeason)
            except Exception as ef:
                print(f"Season Fetch Error at {i} : {str(ef)}")

            data = data.append({'tvId': tvId, 'title': title, 'release': release, 'userRating': userRating, 'synopsis': synopsis,\
                                'genres': genres, 'thumbnailUrl': thumbnailUrl, 'Original Language': language, 'cast': cast, 'trailerOrPromoUrl': trailerUrl,\
                                'isIndianOTT': isIndianOTT, 'backdropUrl': backdropUrl, 'keywords': keywords,\
                                'watch': watchList, 'seasonData': seasonData}, ignore_index=True)

            #print(tvId, title)

            if j > 300:
                j = 1
                print("Writing to CSV")
                newFileWriter.writerows(data.values)
                data = pd.DataFrame(columns=['tvId', 'title', 'release', 'userRating', 'synopsis',
                                             'genres', 'thumbnailUrl', 'Original Language', 'cast', 'trailerOrPromoUrl', 'isIndianOTT', 'backdropUrl', 'keywords', 'watch','seasonData'])

            else:
                j += 1
                
        except Exception as e:
            eString = str(e)

            if "404" in eString:
                print(str(i) + ": No TV Show")
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