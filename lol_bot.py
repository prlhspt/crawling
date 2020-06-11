from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup
import requests
import os
import telegram

TELEGRAM_TOKEN = '1101178096:AAHBFH15tQyTzhFoaIOOQqmcaIS4zNjmaZc'

bot = telegram.Bot(token=TELEGRAM_TOKEN)

LOLALARMCHANNEL = -1001159561160


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


def recentGameOPGG(Name):
    url = 'https://www.op.gg/summoner/userName=' + Name
    req = requests.get(url, headers=hdr)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')

    Container = {}
    Container['Name'] = soup.find("div", {"class": "SummonerName"}).text
    champ = soup.find("div", {"class": "ChampionImage"})
    champ = champ.find("a").attrs['href']
    Container["Champion"] = champ.replace("/champion/", '').replace("/statistics", '').capitalize()

    i = soup.select('h2.Text')[0]
    Container['MatchInfo'] = i.text.replace('\n', '').replace('\t', '')

    i = soup.select('div.Right')[0]
    Container['Time'] = i.text.replace('\n', '').replace('\t', '')

    i = soup.select('div.KDA span.Kill')[0]
    j = soup.select('div.KDA span.Death')[0]
    k = soup.select('div.KDA span.Assist')[0]
    Container['KDA'] = i.text + '/' + j.text + '/' + k.text

    i = soup.select('div.KDARatio')[0]
    Container['KDARatio'] = i.text.replace('\n', '').replace('\t', '')

    i = soup.select('div.Stats')[0]
    Container['Stats'] = i.text.replace('\n', '').replace('\t', '')

    return Container





def renewalOPGG(Name):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(options=options)
    url = 'https://www.op.gg/summoner/userName=' + Name
    action = ActionChains(driver)
    driver.get(url)

    try:
        driver.find_element_by_css_selector('.Button.SemiRound.Blue').click()
        action.send_keys(Keys.ENTER)
        time.sleep(1)
        driver.get_screenshot_as_file('opgg.png')
    except Exception as ex:
        print("exception: ", ex)
        driver.quit()
    driver.quit()


def ingameOPGG(Name):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    url = 'https://www.op.gg/summoner/userName=' + Name

    driver.get(url)
    Container = {}

    driver.find_element_by_css_selector('.SpectateTabButton').click()
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    link = soup.find("link").attrs['href']

    Container['Link'] = link

    ingameInfo = soup.find("div", {"class" : "tabItem Content SummonerLayoutContent summonerLayout-spectator"})

    names = ingameInfo.find_all("td", {"class" : "SummonerName Cell"})
    Container['Names'] = []

    if len(names) == 0:
        return Container

    for name in names:
        Container['Names'].append(name.text.strip())

    champions = ingameInfo.find_all("td", {"class" : "ChampionImage Cell"})
    Container['Champions'] = []
    for champion in champions:
        champ = str(champion.find("a").attrs['href'])
        champ = champ.replace("/champion/", '').replace("/statistics", '').capitalize()
        Container['Champions'].append(champ)

    tiers = ingameInfo.find_all("td", {"class" : "CurrentSeasonTierRank Cell"})
    Container['Tiers'] = []
    for tier in tiers:
        Container['Tiers'].append(tier.text.strip())

    ratios = ingameInfo.find_all("td", {"class" : "RankedWinRatio Cell"})
    Container['Ratios'] = []
    for ratio in ratios:
        Container['Ratios'].append(ratio.text.replace('\n', '').replace('\t', '').strip())

    champRatios = ingameInfo.find_all("td", {"class" : "ChampionInfo Cell"})
    Container['Champion Ratios'] = []
    for champRatio in champRatios:
        Container['Champion Ratios'].append(champRatio.text.replace(' ', '').replace('\n', '').replace('\t', '').strip())

    driver.quit()

    return Container

def sendRecentOpgg(Name, idx):

    recentGameInfo = recentGameOPGG(Name)

    if latest_time[idx] != recentGameInfo['Time']:
        latest_time[idx] = recentGameInfo['Time']
        i = recentGameInfo['Stats'].index("CS")
        j = recentGameInfo['KDARatio'].index("평점")
        k = recentGameInfo['Time'].index("초")
        message = '🎮 {Name}\n{MatchInfo}\n{Champ} {Time}\nKDA {KDA} {KDARatio} {Stats}\n'.format(Name = recentGameInfo['Name'], MatchInfo=recentGameInfo['MatchInfo'],
                                                                                                  Champ=recentGameInfo['Champion'],
                                                                                                  Time=(recentGameInfo['Time'][:k+1] + ' ' + recentGameInfo['Time'][k+1:]) ,
                                                                                                  KDA=recentGameInfo['KDA'], KDARatio=recentGameInfo['KDARatio'][:j-1],
                                                                                                  Stats=recentGameInfo['Stats'][i:])
        message += 'https://www.op.gg/summoner/userName=' + Name.replace(' ', '')
        bot.sendMessage(LOLALARMCHANNEL, message)

def sendIngameOPGG(Name, idx):
    ingameInfo = ingameOPGG(Name)

    if latest_names[idx] == ingameInfo['Names']:
        return
    message = ''
    if len(ingameInfo.keys()) < 3:
        return
    else:
        latest_names[idx] = ingameInfo['Names']
        for i in range(5):
            j = 2 * i
            message += '💧 ' + ingameInfo['Names'][i] + '\n' + ingameInfo['Tiers'][i] + ' '  +  ingameInfo['Ratios'][i] + ' ' + ingameInfo['Champions'][i] + ' ' + ingameInfo['Champion Ratios'][j] + ' ' + ingameInfo['Champion Ratios'][j+1]
            message += '\n'
        message += '___________________________________________________\n\n'

        for i in range(5, 10):
            j = 2 * i
            message += '🔥 ' + ingameInfo['Names'][i] + '\n' + ingameInfo['Tiers'][i] + ' '  +  ingameInfo['Ratios'][i] + ' ' + ingameInfo['Champions'][i] + ' ' + ingameInfo['Champion Ratios'][j] + ' ' + ingameInfo['Champion Ratios'][j+1]
            message += '\n'

        bot.sendMessage(LOLALARMCHANNEL, message)

    return message

if __name__ == "__main__":

    Names = ['강찬밥']
    global latest_time, latest_names

    latest_time = ['' for _ in range(len(Names)) ]
    latest_names = [['' for _ in range(10)] for _ in range(len(Names))]

    for i in range(len(Names)):
        renewalOPGG(Names[i])   #갱신 눌러줌
        os.system('cls')
        print(Names[i], ' 갱신 완료')
        time.sleep(1)

        sendRecentOpgg(Names[i], i)    #최근 전적 변화 있을 시 전송
        os.system('cls')
        print(Names[i], ' 최근 게임 전송 완료')
        time.sleep(1)

        message = sendIngameOPGG(Names[i], i)
        os.system('cls')
        print(Names[i], ' 인게임 전송 완료')
        time.sleep(1)

print(message)
