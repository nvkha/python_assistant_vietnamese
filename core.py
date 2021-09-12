import datetime
from text_to_speech import speak
from speech_to_text import takeCommand
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import wolframalpha
from geopy.geocoders import Nominatim
import datetime
from helper import regex_date, getHash256, getHmac512, API_KEY, SECRET_KEY
import os
import random
import json 
import helper
import telegram
import re
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
#!pip install squarify
import squarify 
from pygame import mixer
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
from selenium import webdriver

load_dotenv()
mixer.init()


token = os.getenv("TELE_TOKEN")
id = os.getenv("TELE_ID")


bot = telegram.Bot(token=token)


wolframalpha_app_id = os.getenv("WOLFRAMALPHA_APP_ID")
geolocator = Nominatim(user_agent="my_app")


API_URL = os.getenv("API_URL")
headers = {"Authorization": os.getenv("HUNGGINGFACE_API_KEY")}


def hello():
    lst = ["Chào bạn, tôi có thể giúp gì được cho bạn ?", "Xin chào, rất vui được gặp bạn", "Chào bạn, chúc bạn một ngày tốt lành",
    f"Xin chào bạn, bây giờ là {datetime.datetime.now().strftime('%H:%M')}, chúc bạn một ngày tốt lành"] 
    text = random.choice(lst)
    speak(text)

def time_():
    # Get current time
    time = datetime.datetime.now().strftime("%H:%M")
    speak(f"Thời gian là {time}") 

def bye():
    quit()

def date_():
    lst = ["Thứ 2", "Thứ 3", "Thứ tư", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    weekday = datetime.datetime.today().weekday()

    if month == 4:
        month = "tư"
    text = f"Hôm nay là {lst[weekday]}, ngày {day} tháng {month} năm {year}" 
    speak(text)

# Advanced features 

# Example: Tin tức thể thao hôm nay
def get_news(query, limit=5):
        if "tin tức" in query:
            category = ''
            categories = ["thế giới", "sức khỏe", "đời sống", "thời sự", "du lịch", "kinh doanh", 
            "khoa học", "giải trí", "xe", "thể thao", "pháp luật", "giáo dục", "công nghệ", "game", 
            "đời sống", "làm đẹp"]
            for item in categories:
                if item in query:
                    category = item
            
            if category == '':
                speak("Bạn muốn tin tức về chủ đề gì ạ")
                category = takeCommand().lower()

            try:
                url  = f"https://news.google.com/rss/search?q={category}&hl=vi&gl=VN&ceid=VN"

                response = requests.get(url)
                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all("item")
                for item in items[:limit]:
                    title = str(item.title.text).lower().replace("vietnamnet.vn", "việt nam net")
                    title = title.replace("baotintuc.vn", "báo tin tức")
                    title = title.replace("cafef.vn", "cà phê f")
                    link = item.link.text
                    speak(title)
                    bot.sendMessage(chat_id=id, text=link, disable_notification=True)
            except Exception:
                print(Exception)
                speak("Có lỗi xảy ra, bạn thử lại sau nhé")
        elif "văn bản" in query:
            try: 
                query = query.replace("văn bản", "")
                url = f"https://www.binhduong.gov.vn/chinhquyen/Pages/Van-ban-Quy-pham-Phap-luat.aspx?k={query}"
                response_url = requests.get(url)
                soup = BeautifulSoup(response_url.content,"html.parser")
                content = soup.find_all("tr",class_="ms-itmhover")
                if len(content) == 0: 
                    speak("Xin lỗi. Tôi không tìm được văn bản bạn yêu cầu")
                    return     
                for i in content[:5]:
                    for i2 in i.select("td:nth-of-type(4) a[href]"):
                        title = i2.text
                        link= f"https://www.binhduong.gov.vn{i2.get('href')}"
                    for i3 in i.select("td:nth-of-type(2) a[href]"):
                        number = i3.text
                        print(number)
                        speak(number.replace("NQ", "nờ quy").replace("QĐ", "quy đê") + "." + title)
                        bot.sendMessage(chat_id=id, text=number + "\n" + link, disable_notification=True)
            except Exception:
                print(Exception)
                speak("Có lỗi xảy ra, bạn thử lại sau nhé")

        else:
            try: 
                query = query.replace("thủ tục", "")
                url = f"https://dichvucong.gov.vn/p/home/dvc-dich-vu-cong-truc-tuyen-ds.html?pkeyWord={query}"
                driver =  webdriver.Chrome("chromedriver")
                driver.get(url)
                elements = driver.find_elements_by_css_selector("#content_DVCTT_List li")
                if len(elements) == 0: 
                    speak("Xin lỗi. Tôi không tìm được thủ tục bạn yêu cầu")
                    return
                for element in elements[:5]:
                    link = element.find_element_by_css_selector("a").get_attribute("href")
                    title = element.find_element_by_css_selector("a").text
                    speak(title)
                    bot.sendMessage(chat_id=id, text=link, disable_notification=True)
            except Exception:
                print(Exception)
                speak("Có lỗi xảy ra, bạn thử lại sau nhé")


get_news("văn bản dịch bệnh")
    
# Example: Việt Nam có bao nhiêu tỉnh
def wiki(question):
    try:
        qs = {
                "inputs": {
                "question": question,
                "context": helper.query_to_text(question),
                }
            }
        data = json.dumps(qs)
        response = requests.request("POST", API_URL, headers=headers, data=data)
        answer = json.loads(response.content.decode("utf-8"))
        print(answer)
    
        if "answer" in answer:
            if answer['answer'].lower() == "no answer":
                speak("Xin lỗi bạn mình không thể trả lời câu hỏi này")
            else:
                speak(answer['answer'])
        elif "error" in answer:
            speak("Xin lỗi bạn model của bạn đang được tải, bạn chờ một tí nhé")
    except:
        speak("Xin lỗi bạn mình không thể trả lời câu hỏi này")      


# Example: 1 + 1 bằng bao nhiêu 
def calculate(query):
    try: 
        client = wolframalpha.Client(wolframalpha_app_id)
        query = query.replace("bằng mấy", "").replace("bằng bao nhiêu", "").replace("=", "").replace("tính", "").replace("bao nhiêu", "").replace("bằng", "")
        print(query)
        res = client.query(query)
        answer = next(res.results).text
        speak("Bằng" + answer)
        
    except Exception as e:
        print(e)
        speak("Xin lỗi bạn tôi không thể thực hiện phép tính này")

# Example: Thời tiết Cà Mau ngày mai thế nào
def weatherForecast(query):
    date = regex_date(query)

    if "nay" in query or not date:
        dayWeather = 0
    elif "mai" in query:
        dayWeather = 1
    else:
        date = regex_date(query)
        date = datetime.datetime.now()
        current_date = datetime.datetime.now().day
        dayWeather = date.day - current_date
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = None

    f = open('database\local.json', encoding="utf-8")
    local = json.load(f)
    for i in local:
        if local[i]["name"].lower() in query.lower():
            city = local[i]["name"].lower()
            break
    f.close()
    
    if not city:
        speak("Bạn muốn dự báo thời tiết cho tỉnh nào nhỉ")
        city = takeCommand()
            
    location = geolocator.geocode(city)
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={location.latitude}&lon={location.longitude}&exclude=hourly,minutely,current&appid={api_key}&lang=vi&units=metric"    

    try:
        response = requests.get(url)
        forecast = response.json()
        weather = forecast['daily'][dayWeather]
        sp = f"Nhiệt độ {weather['temp']['day']} độ và {weather['weather'][0]['description']} tại {city.title()}"
        if "ngày mai" in query:
           sp = f"Dự báo thời tiết ngày mai tại {city.title()}, nhiệt độ {weather['temp']['day']} độ và {weather['weather'][0]['description']}"
        
        bot.sendMessage(chat_id=id, text=sp, disable_notification=True)
        bot.sendLocation(chat_id=id, latitude=location.latitude, longitude=location.longitude) 
        speak(sp)
    except Exception as e:
        print(e)
        speak(f"Có lỗi xảy ra, bạn thử lại sau nhé")

# Example: Thông tin dịch covid-19
def getInfoCovid():
    urls = ["https://api.covid19api.com/summary", "https://ncov.moh.gov.vn/"]
    

    payload={}
    headers = {}

    try: 
        response_api = requests.request("GET", urls[0], headers=headers, data=payload)
        response_gov = requests.request("GET", urls[1], headers=headers, data=payload, verify=False)
        soup = BeautifulSoup(response_gov.content, "html")
        span = soup.find_all("span", class_="font24")
        recovered = [i.text for i in span]


        data = response_api.json()
        world = data['Global']
        countries = data['Countries']
        for country in countries:
            if country["CountryCode"] == "VN":
                vn = country
                break

        bot.sendMessage(chat_id=id, text="Thông tin dịch covid-19 thế giới: \n" + 
                f"Số ca nhiểm mới: {world['NewConfirmed']} \n" + 
                f"Tổng số ca nhiễm: {world['TotalConfirmed']} \n" +
                f"Tổng số ca tử vong: {world['TotalDeaths']} \n" + 
                f"Tổng số ca đã khỏi: {recovered[6]} ", disable_notification=True)

        speak("Thông tin dịch covid-19 thế giới, " + 
                f"Số ca nhiểm mới: {world['NewConfirmed']}, " + 
                f"Tổng số ca nhiễm: {world['TotalConfirmed']}, " +
                f"Tổng số ca tử vong: {world['TotalDeaths']} , " + 
                f"Tổng số ca đã khỏi: {recovered[6]} ")
        
        bot.sendMessage(chat_id=id, text="Thông tin dịch covid-19 Việt Nam: \n" + 
                f"Số ca nhiểm mới: {vn['NewConfirmed']} \n" + 
                f"Tổng số ca nhiễm: {vn['TotalConfirmed']} \n" +
                f"Tổng số ca tử vong: {vn['TotalDeaths']} \n" + 
                f"Tổng số ca đã khỏi: {recovered[2]} ", disable_notification=True)
        
        speak("Thông tin dịch covid-19 Việt Nam, " + 
                f"Số ca nhiểm mới: {vn['NewConfirmed']}, " + 
                f"Tổng số ca nhiễm: {vn['TotalConfirmed']}, " +
                f"Tổng số ca tử vong: {vn['TotalDeaths']} , " + 
                f"Tổng số ca đã khỏi: {recovered[2]} ")
    except Exception:
        print(Exception)
        speak("Có lỗi xảy ra, bạn vui lòng thử lại sau nhé")


# Example: Giá tiền điện tử hôm nay
def getPriceCrypto():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'10',
    'convert':'USD'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.getenv("COIN_API_KEY"),
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        #print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    
    df = pd.json_normalize(data["data"])
    cols_to_keep = ['name','symbol','cmc_rank','quote.USD.price','quote.USD.percent_change_24h','quote.USD.market_cap',]
    df_final = df[cols_to_keep]
    #rename columns
    df_final.columns = ['name','symbol','cmc_rank','USD_price','USD_percent_change_24h','USD_market_cap',]
    #print the table
    #load data
    sizes=df_final["USD_market_cap"]
    label=df_final["name"]
    # color scale on the price development 
    # min and max values
    cmap = matplotlib.cm.RdYlGn #RedYellowGreen
    mini=min(df_final["USD_percent_change_24h"])
    maxi=max(df_final["USD_percent_change_24h"])
    norm = matplotlib.colors.Normalize(vmin=mini, vmax=maxi)
    colors = [cmap(norm(value)) for value in df_final["USD_percent_change_24h"]]

    # labels in treemap squares
    labels = ["%s\n%0.2f USD\n%0.2f%%" % (label) for label in zip(df_final.symbol, df_final["USD_price"], df_final["USD_percent_change_24h"])]

    # make plot
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111, aspect="auto")
    ax = squarify.plot(df_final["USD_market_cap"], color=colors, label=labels,  alpha=.8)
    ax.set_title("Cryptomarket price change last 24 hours\n", fontsize=18)

    # plot title and color bar
    img = plt.imshow([df_final["USD_percent_change_24h"]], cmap=cmap)
    img.set_visible(True)
    fig.colorbar(img, orientation="vertical", shrink=.96)
    fig.text(.76, .9, "Percentage change", fontsize=14)

    # if you want to export the figure
    plt.savefig("crypto_price.png")
    try:
        bot.sendPhoto(chat_id=id, caption="Treemaps top 10 cryptocurrency prices", photo=open("crypto_price.png", "rb"))
        speak("Đã gửi giá tiền điện tử hôm nay")
        os.remove("crypto_price.png")
    except:
        fig.show()

# Example: Mở bài hát Em gái mưa
def get_song(query):
    if ("tắt" or "dừng") in query:
        try:
            mixer.music.stop()
            mixer.music.unload()
            return 
        except:
            return

    if ("mở bài" or "mở bài hát" or "hát bài") in query:
        query = query.replace("mở", "").replace("bài", "").replace("hát", "")
    else:
        speak("Bạn muốn nghe bài nào ạ")
        query = takeCommand()
    url_info = f'http://ac.mp3.zing.vn/complete?type=artist,song,key,code&num=500&query={query}'

    try:
        response = requests.get(url_info)
        song_info = response.json()
        song_info = song_info['data'][0]['song'][0]
        id = song_info['id']
        #print(response.json())
    except:
        speak("Xin lỗi! Tôi không tìm thấy bài hát bạn yêu cầu")
        return
    
    ctime = datetime.datetime.now().timestamp()
    url = 'https://zingmp3.vn/api/song/get-song-info?'
    a = f'ctime={ctime}id={id}'    
    path = '/song/get-song-info' + getHash256(a.encode())
    sig = getHmac512(path.encode(), SECRET_KEY)
    complete_url = url + f"id={id}&ctime={ctime}&sig={sig}&api_key={API_KEY}"

    a_session = requests.Session()
    a_session.get(complete_url)
    cookies = a_session.cookies

    try:
        #cookies = browser_cookie3.load(domain_name='zingmp3.vn')
        response = requests.get(complete_url, verify=False, cookies=cookies)
        
        data = response.json()
        song_url = data['data']['streaming']['default']['128']
        song = requests.get("http:" + song_url)
        song = song.content
        f = open("sounds\song.mp3", "wb")
        f.write(song)
        f.close()
        mixer.music.load("sounds\song.mp3")
        mixer.music.play()
    except Exception: 
        print(Exception)
        speak("Có lỗi xảy ra, bạn thử lại sau nhé")

# Example: Lịch học 22th ngày mai 
def get_schedule(query):
    week_number = datetime.datetime.now().isocalendar()[1]

    a = [int(s) for s in query.split() if s.isdigit()]
    if len(a) >= 2:
        if a[1] < 10:
            month = "0" + str(a[1])
            query = query.replace(" tháng" + " " + str(a[1]),"/" + str(month))
    query = query.replace(" tháng ", "/")
    print(query)
    student_class = ""
    
    if re.findall("\d\d\w\w",query):
        student_class = (re.findall("\d\d\w\w", query)[0]).lower()
    else:
        student_class = helper.getStudentClass(student_class)
    print(student_class)
    
    if "tuần sau" in query:   
        helper.get_schedule(class_name=student_class, week_number=week_number + 1)
    elif "tuần này" in query:
        helper.get_schedule(class_name=student_class, week_number=week_number)
    elif regex_date(query):
        helper.get_schedule(class_name=student_class, date=regex_date(query))
    else:
        speak("Mình không tìm được lịch học của bạn")


def getInfoFood(query):
    with open("database/foods.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for food in data["items"]:
            if food["title"].lower() in query:
                speak(food["description"])

#get_schedule("Lịch học ngày 17 tháng 7 22TH")
