from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
import pandas as pd
import time
import csv
from datetime import datetime
from tqdm import tqdm

date = str(datetime.date(datetime.now()))
outName = date + '-Movie-6.csv'

idList = list(range(600001, 720001))

def handleEmptyGet(tag, getString):
    if(tag != None):
        return tag.get(getString)
    else:
        return None


def handleEmptyCleanGetText(tag):
    value = None
    if(tag != None):
        value = tag.getText().replace("\n", "").replace("\r", "").replace(" ", "")
    return value


data = pd.DataFrame(columns=['movieId', 'title', 'release', 'releaseCountry', 'certification', 'userRating', 'tagline', 'synopsis',
                             'genres', 'duration', 'thumbnailUrl', 'backdropUrl',  'Original Language', 'cast', 'crew', 'keywords', 'budget', 'revenue', 'trailerUrl', 'watch', 'isIndianOTT'])

data.to_csv(outName, index=False)

with open(outName, 'a', encoding="utf-8") as newFile:
    newFileWriter = csv.writer(newFile)
    j = 1
    start = time.time()
    for i in tqdm(idList):

        try:
            uClient = uReq("https://www.themoviedb.org/movie/" + str(i))
            bs = soup(uClient.read(), "html.parser")
            uClient.close()
            movieId = i

            isIndianOTT = False
            container = bs.find("div", {"class": "title ott_false"})
            if(container == None):
                container = bs.find("div", {"class": "title ott_true"})
                if(container != None):
                    isIndianOTT = True

            title = container.find("h2").find("a").getText()

            release = handleEmptyCleanGetText(
                bs.find("span", {"class": "release"}))
            
            releaseCountry = None
            if not (release == None):
                if ( ("(" in release) and (")" in release) ):
                    releaseCountry = release.split("(")[1].replace(")","")
                    release = release.split("(")[0]

            certification = handleEmptyCleanGetText(
                bs.find("span", {"class": "certification"}))

            userRating = handleEmptyGet(
                bs.find("div", {"class": "user_score_chart"}), "data-percent")

            taglineFetch = bs.find("h3", {"class": "tagline"})
            tagline = None
            if(taglineFetch != None):
                tagline = taglineFetch.getText()

            synopsis = bs.find(
                "div", {"class": "overview"}).find("p").getText()

            genres = []
            for genreTag in bs.find("span", {"class": "genres"}).findAll("a"):
                genres.append(genreTag.getText())

            duration = handleEmptyCleanGetText(
                bs.find("span", {"class": "runtime"}))

            thumbnailUrl = handleEmptyGet(
                bs.find("img", {"class": "poster lazyload"}), "data-src")

            backdropUrl = handleEmptyGet(
                bs.find("img", {"class": "backdrop"}), "data-src")

            section = bs.find("section", {"class": "facts"})

            language = None
            budget = None
            revenue = None

            if(section != None):
                language = section.find(
                    "bdi", string="Original Language").parent.parent.getText()
                if(language != None):
                    language = language.replace("Original Language ", "")

                budget = section.find(
                    "bdi", string="Budget").parent.parent.getText()
                if(budget != None):
                    budget = budget.replace("Budget ", "")

                revenue = section.find(
                    "bdi", string="Revenue").parent.parent.getText()
                if(revenue != None):
                    revenue = revenue.replace("Revenue ", "")

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

            crew = []
            for member in bs.find_all("li", {"class": "profile"}):
                name = member.a.getText()
                role = member.find("p", {"class": "character"}).getText()
                crew.append({"name": name, "role": role})

            keywordsFetch = bs.find("section", {"class": "keywords"})
            keywords = []
            if(keywordsFetch != None):
                for a in keywordsFetch.find_all("a"):
                    keywords.append(a.getText())

            trailerUrlId = handleEmptyGet(
                bs.find("a", {"class": "no_click play_trailer"}), "data-id")
            trailerUrl = None
            if(trailerUrlId != None):
                trailerUrl = 'www.youtube.com/watch?v=' + trailerUrlId
            
            watchList = []
            if(isIndianOTT):
                try:
                    uClient = uReq(
                        "https://www.themoviedb.org/movie/" + str(i) + "/watch")
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

            data = data.append({'movieId': movieId, 'title': title, 'release': release, 'releaseCountry': releaseCountry, 'certification': certification, 'userRating': userRating, 'tagline': tagline, 'synopsis': synopsis,
                                'genres': genres, 'duration': duration, 'thumbnailUrl': thumbnailUrl, 'backdropUrl': backdropUrl, 'Original Language': language, 'cast': cast, 'crew': crew, 'keywords': keywords, 'budget': budget, 'revenue': revenue, 'trailerUrl': trailerUrl, 'watch': watchList, 'isIndianOTT': isIndianOTT}, ignore_index=True)

            #print(movieId, title)

            if j > 300:
                j = 1
                print("Writing to CSV")
                newFileWriter.writerows(data.values)
                data = pd.DataFrame(columns=['movieId', 'title', 'release', 'releaseCountry', 'certification', 'userRating', 'tagline', 'synopsis',
                                             'genres', 'duration', 'thumbnailUrl', 'backdropUrl',  'Original Language', 'cast', 'crew', 'keywords', 'budget', 'revenue', 'trailerUrl', 'watch', 'isIndianOTT'])

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