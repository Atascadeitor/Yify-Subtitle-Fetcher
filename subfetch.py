import requests
import pprint

apikey = 'de12b217'
url = f"https://www.omdbapi.com/?apikey={apikey}&s=batman"
r=requests.get(url).json()['Search']

print('Select your movie :')
for i in range(len(r)):
    print("{}. {}".format(i+1,r[i]['Title']))

choice = int(input())-1
print("The movie you selected : {} and its id : {}".format(r[choice]['Title'],r[choice]['imdbID']))