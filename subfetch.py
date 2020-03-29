import argparse
import requests
import PTN
from bs4 import BeautifulSoup 
from zipfile import ZipFile
from io import BytesIO
import os

def cleanEntries(entries):
    """Parses the html code into subtitle name and its respective location in the database"""
    filtered = list()
    for entry in entries:
        sub_name = entry.find_all('td')[2].text.strip('\n').replace('subtitle ','')
        subtitle_location = entry.select('[href]')[0]['href'].replace('subtitles','subtitle')
        filtered.append((sub_name,subtitle_location))
    return filtered


def getMovieName(fileName):
    """Get movie name from the file name"""
    info = PTN.parse(fileName)
    return info['title']

def fetchId(movie):
    """Fetch IMDb Id of the movie"""
    apikey = 'de12b217'
    url = f"https://www.omdbapi.com/?apikey={apikey}&s={movie}"
    try:
        r = requests.get(url).json()['Search']
    except:
        print("No movie found with the name : ",movie)
        exit()
    movies = list()
    for item in r:
        if item['Type'] == 'movie': # Filter only the movies
            movies.append(item)
    print('Select your movie : (Please select first option if you are unsure)')
    for i in range(len(movies)):
        print("{}. {}, {}".format(i+1,movies[i]['Title'],movies[i]['Year']))

    choice = int(input())-1
    print("The movie you selected : {} and its id : {}\n".format(movies[choice]['Title'],movies[choice]['imdbID']))
    return movies[choice]['imdbID']

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
try:
    table = soup.find_all(class_='other-subs')[0]
except:
        print("Subtitle not found for the movie '"+movie+"' in Yify Database")
        exit()
entries = table.find_all('tr')
lang_entries = list()
for entry in entries[1:]:
    # Filtering by the language
    if f'"sub-lang">{lang}' in str(entry):
        lang_entries.append(entry)

lang_entries = cleanEntries(lang_entries)
print("Select a subtitle : Language =",lang)
index = 1
for entry in lang_entries:
    print("{}. {}".format(index,entry[0]))
    index += 1

choice = int(input())-1
print("The subtitle you selected : ",lang_entries[choice][0])

zip_url = "https://www.yifysubtitles.com"+lang_entries[choice][1]+".zip"
zip_page = requests.get(zip_url)
if zip_page.status_code != 200:
    print(f"Subtitle file not found")
    exit()

with ZipFile(BytesIO(zip_page.content)) as zip_file:    # Read the zip file in memory itself without writing into storage
    for contained_file in zip_file.namelist():
        if(contained_file.endswith('.srt')):            # Select the .srt file
            with open(os.path.join(os.path.dirname(args.file),'.'.join(args.file.split('.')[:-1])+'.srt'), 'wb') as f:   #filename.srt
                f.write(zip_file.open(contained_file).read())   

print("\nSaved in ",os.path.join(os.path.dirname(args.file),'.'.join(args.file.split('.')[:-1])+'.srt'))