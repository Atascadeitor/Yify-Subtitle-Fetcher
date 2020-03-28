import argparse
import requests
import pprint
import PTN

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
    print("The movie you selected : {} and its id : {}".format(r[choice]['Title'],r[choice]['imdbID']))
    return r[choice]['imdbID']

parser = argparse.ArgumentParser(description='Fetch Yify Subtitles for a movie')
parser.add_argument('file', type=str, help='File name whose subtitle to be fetched')
parser.add_argument('--lang',default='English',help='Subtitle language')
args = parser.parse_args()

movie = getMovieName(args.file)
lang = args.lang
id = fetchId(movie)


