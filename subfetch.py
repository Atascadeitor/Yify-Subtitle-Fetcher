import argparse
import requests
import PTN
from bs4 import BeautifulSoup 
from zipfile import ZipFile
from io import BytesIO
import os

def cleanEntries(entries):
    filtered = dict()
    for entry in entries:
        sub_name = entry.find_all('td')[2].text.strip('\n').replace('subtitle ','')
        subtitle_location = entry.select('[href]')[0]['href'].replace('subtitles','subtitle')
        filtered[sub_name] = subtitle_location
    return filtered


def getMovieName(fileName):
    info = PTN.parse(fileName)
    return info['title']

def fetchId(movie):
    apikey = 'de12b217'
    url = f"https://www.omdbapi.com/?apikey={apikey}&s={movie}"
    try:
        r = requests.get(url).json()['Search']
    except:
        print("No movie found with the name : ",movie)
        exit()
    print('Select your movie : (Please select first option if you are unsure)')
    for i in range(len(r)):
        print("{}. {}".format(i+1,r[i]['Title']))
    choice = int(input())-1
    print("The movie you selected : {} and its id : {}\n".format(r[choice]['Title'],r[choice]['imdbID']))
    return r[choice]['imdbID']

parser = argparse.ArgumentParser(description='Fetch Yify Subtitles for a movie')
parser.add_argument('file', type=str, help='File name whose subtitle to be fetched')
parser.add_argument('--lang',default='English',help='Subtitle language')
args = parser.parse_args()

movie = getMovieName(args.file.split(os.path.sep)[-1])
lang = args.lang.capitalize()
id = fetchId(movie)

print("Fetching subtitle list...")
yify_url = f"https://yifysubtitles.com/movie-imdb/{id}"
page = requests.get(yify_url)

if page.status_code != 200:
    print(f"Subtitle for {movie} doesnt exist in Yify Subtitles Database")
    exit()

print("Done")
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find_all(class_='other-subs')[0]
entries = table.find_all('tr')
lang_entries = list()
for entry in entries[1:]:
    if f'"sub-lang">{lang}' in str(entry):
        lang_entries.append(entry)

lang_entries = cleanEntries(lang_entries)
print("Select a subtitle :")
index = 1
for k,v in lang_entries.items():
    print("{}. {}".format(index,k))
    index += 1

choice = int(input())-1
print("The subtitle you selected : ",list(lang_entries)[choice])

zip_url = "https://www.yifysubtitles.com"+lang_entries[list(lang_entries)[choice]]+".zip"
zip_page = requests.get(zip_url)
if zip_page.status_code != 200:
    print(f"Subtitle file not found")
    exit()

with ZipFile(BytesIO(zip_page.content)) as zip_file:
    for contained_file in zip_file.namelist():
        if(contained_file.endswith('.srt')):
            with open(os.path.join(os.path.dirname(args.file),'.'.join(args.file.split('.')[:-1])+'.srt'), 'wb') as f:   #filename.srt
                f.write(zip_file.open(contained_file).read())   

print("\nSaved in ",os.path.join(os.path.dirname(args.file),'.'.join(args.file.split('.')[:-1])+'.srt'))