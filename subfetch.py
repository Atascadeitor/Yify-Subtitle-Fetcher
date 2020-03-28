import argparse
import requests
import pprint

parser = argparse.ArgumentParser(description='Fetch Yify Subtitles for a movie')
parser.add_argument('file', type=str, help='File name whose subtitle to be fetched')
parser.add_argument('--lang',default='English',help='Subtitle language')
args = parser.parse_args()
file_name = args.file
lang = args.lang

apikey = 'de12b217'
url = f"https://www.omdbapi.com/?apikey={apikey}&s=batman"
r=requests.get(url).json()['Search']

print('Select your movie :')
for i in range(len(r)):
    print("{}. {}".format(i+1,r[i]['Title']))

choice = int(input())-1
print("The movie you selected : {} and its id : {}".format(r[choice]['Title'],r[choice]['imdbID']))