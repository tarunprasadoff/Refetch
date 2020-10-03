from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
import pandas as pd
import time
import csv
from datetime import datetime

date = str(datetime.date(datetime.now()))
outName = date + '-TV.csv'

#listName = 'TV-List.csv'
#data = pd.read_csv(listName)

fileName = date + '-TV-html.csv'
df = pd.DataFrame(columns = ['tvId', 'html'])
df.to_csv(fileName, index=False)

watchName = date + '-TV-watch-html.csv'
df.to_csv(watchName, index=False)

newList = pd.DataFrame(columns = ['tvId'])

idList = list(range(1,120001))
# def remId(i):
#     print(i,"rem")
#     try:
#         idList.remove(i)
#     except Exception as e:
#         print("Error: ", str(e))
# data.apply(lambda row : remId(row['tvId']), axis = 1)

with open(fileName, 'a', encoding="utf-8") as newFile:
    newFileWriter = csv.writer(newFile)
    j = 1
    start = time.time()
    for i in idList:

        try:
            uClient = uReq("https://www.themoviedb.org/tv/" + str(i))
            page_soup = soup(uClient.read(), "html.parser")
            uClient.close()
            print(str(i))
            df = df.append({'tvId': i, 'html': page_soup},
                           ignore_index=True)
            newList = newList.append({'tvId': i},
                           ignore_index=True)
            if j > 300:
                j = 1
                print("Writing to CSV")
                newFileWriter.writerows(df.values)
                df = pd.DataFrame(columns=['tvId', 'html'])
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
    newFileWriter.writerows(df.values)
    df = pd.DataFrame(columns=['tvId', 'html'])
    print(f"Runtime of the program is {time.time() - start}")

#pd.read_csv(listName).append(newList,ignore_index=True).to_csv(listName, index=False)

with open(watchName, 'a', encoding="utf-8") as newFile:
    newFileWriter = csv.writer(newFile)
    j = 1
    start = time.time()
    for i in pd.read_csv(fileName)['tvId']:

        try:
            uClient = uReq("https://www.themoviedb.org/tv/" + str(i) + "/watch")
            page_soup = soup(uClient.read(), "html.parser")
            uClient.close()
            print(str(i) + 'Watch')
            df = df.append({'tvId': i, 'html': page_soup},
                           ignore_index=True)
            if j > 300:
                j = 1
                print("Writing to CSV")
                newFileWriter.writerows(df.values)
                df = pd.DataFrame(columns=['tvId', 'html'])
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
                print("WinError " +
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
    newFileWriter.writerows(df.values)
    print(f"Runtime of the program is {time.time() - start}")

data = pd.DataFrame(columns=['tvId', 'title', 'release', 'userRating', 'synopsis',
                             'genres', 'thumbnailUrl', 'Original Language', 'cast', 'trailerOrPromoUrl', 'isIndianOTT', 'backdropUrl', 'keywords', 'watch'])

dfMain = pd.read_csv(fileName)
dfWatch = pd.read_csv(watchName)

def handleEmptyGet(tag, getString):
    if(tag != None):
        return tag.get(getString)
    else:
        return None

for i in range(0, len(dfMain.index)):

    bs = soup(dfMain.loc[i].html, "html.parser")
    tvId = dfMain.loc[i].tvId

    container = bs.find("div", {"class": "title ott_false"})
    if(container == None):
        container = bs.find("div", {"class": "title ott_true"})

    title = container.find("h2").find("a").getText()

    release = container.find("span").getText().replace(
        "(", "").replace(")", "")
    if(len(release) != 4):
        release = None

    userRating = handleEmptyGet(
        bs.find("div", {"class": "user_score_chart"}), "data-percent")

    synopsis = bs.find("div", {"class": "overview"}).find("p").getText()

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
        actorUrl = 'https://www.themoviedb.org' + handleEmptyGet(cur.a, "href")
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

    isIndianOTT = False
    watchCurr = dfWatch[dfWatch.tvId == tvId]
    if(len(watchCurr) == 0):
        watchList = []
    else:
        bsWatch = soup(watchCurr.iloc[0].html, "html.parser")
        if(bsWatch.find("p", {"class": "no_offers"}) == None):
            providers = bsWatch.find_all("div", {"class": "ott_provider"})
            watchList = []
            if(len(providers) > 0):
                isIndianOTT = True
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
                        price = provider.find("span", {"class": "price"})
                        if price != None:
                            price = price.getText()
                            print(price)
                        quality = provider.find(
                            "span", {"class": "presentation_type"})
                        if quality != None:
                            quality = quality.getText()
                            print(quality)
                        val = {"description": description, "link": handleEmptyGet(a, "href"), "source": split[len(
                            split)-1], "sourceImageUrl": handleEmptyGet(a.img, "src"), "price": price, "quality": quality}
                    temp.append(val)
                watchList.append({nature: temp})
        else:
            watchList = []

    data = data.append({'tvId': tvId, 'title': title, 'release': release, 'userRating': userRating, 'synopsis': synopsis,
                        'genres': genres, 'thumbnailUrl': thumbnailUrl, 'Original Language': language, 'cast': cast, 'trailerOrPromoUrl': trailerUrl, 'isIndianOTT': isIndianOTT, 'backdropUrl': backdropUrl, 'keywords': keywords, 'watch': watchList}, ignore_index=True)

    print(tvId, title)

writeName = date + "-TV.csv"
data.to_csv(writeName, index=False)

