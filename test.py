import requests
from bs4 import BeautifulSoup

Name = 'drx deft'

hdr = {'Accept-Language': 'ko_KR,en;q=0.8', 'User-Agent': (
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Mobile Safari/537.36')}


def parseOPGG(Name):
    Container = {}
    Tier = []
    LP = []
    Wins = []
    Losses = []
    Ratio = []
    SummonerName = ""
    ranking = ""

    url = 'https://www.op.gg/summoner/userName=' + Name
    req = requests.get(url, headers=hdr)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')

    for i in soup.select('div[class=SummonerName]'):
        SummonerName = i.text
    Container['SummonerName'] = SummonerName

    for i in soup.select('span[class=ranking]'):
        Ranking = i.text
    Container['Ranking'] = Ranking

    for i in soup.select('div[class=Tier]'):
        Tier.append(i.text.strip())
    Container['Tier'] = Tier

    for i in soup.select('div[class=LP]'):
        LP.append(i.text)
    Container['LP'] = LP

    for i in soup.select('div[class=WinLose] > span[class=Wins]'):
        Wins.append(i.text)
    Container['Wins'] = Wins

    for i in soup.select('div[class=WinLose] > span[class=Losses]'):
        Losses.append(i.text)
    Container['Losses'] = Losses

    for i in soup.select('span[class=Ratio]'):
        Ratio.append(i.text)
    Container['Ratio'] = Ratio
    return Container

def printSummonerInfo(Container):
    rankCase = ['솔로', '자유']
    for i in range(len(Container['Tier'])):
        if Container['SummonerName'] != '':
            print("==========================")
            if (len(Container['Tier'])):
                print(Container['SummonerName'] + "님의" + rankCase[i] + "랭크 정보입니다.")
                print("==========================")
                print("티어 : " + Container['Tier'][i])
                print("LP : " + Container['LP'][i])
                print("승/패 : " + Container['Wins'][i] + "/" + Container['Losses'][i])
                print("승률 : " + Container['Ratio'][i])
            else:
                print(Container['SummonerName'] + "님은 Unranked 입니다.")
                print("==========================")


if __name__ == "__main__":
    printSummonerInfo(parseOPGG("DRX Deft"))
