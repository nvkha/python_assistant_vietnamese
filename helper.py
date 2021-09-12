import requests
import dateparser
import datetime
import pytz
import re
import csv
import os
from bs4 import BeautifulSoup
import tabula
import cs50 
from text_to_speech import speak
import datetime
import os.path
import telegram
import hashlib
import hmac
from googlesearch import search # Performing Google searches
from markdown import markdown
from nltk import sent_tokenize
from sys import argv
from speech_to_text import takeCommand
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = b'10a01dcf33762d3a204cb96429918ff6'
API_KEY = '38e8643fb0dc04e8d65b99994d3dafff'

token = os.getenv("TELE_TOKEN")
id = os.getenv("TELE_ID")

s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'

bot = telegram.Bot(token=token)

db = cs50.SQL("sqlite:///database\schedule.db")

# REGEX
REGEX_DATE = r"(3[01]|[12][0-9]|0?[1-9])[-\/:|](1[0-2]|0?[1-9])([-\/:|](2[0-1][0-9][0-9]))"
REGEX_DAY_MONTH = r"(3[01]|[12][0-9]|0?[1-9])[-\/:|](1[0-2]|0?[1-9])"
REGEX_MONTH_YEAR = r"(1[0-2]|0?[1-9])([-\/:|](2[0-1][0-9][0-9]))"

def regex_date(msg, timezone="Asia/Ho_Chi_Minh"):
    ''' use regex to capture date string format '''

    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz=tz)
    temp = msg

    date_str = []
    regex = REGEX_DATE
    regex_day_month = REGEX_DAY_MONTH
    regex_month_year = REGEX_MONTH_YEAR
    pattern = re.compile("(%s|%s|%s)" % (
        regex, regex_month_year, regex_day_month), re.UNICODE)

    matches = pattern.finditer(msg)
    for match in matches:
        _dt = match.group(0)
        _dt = _dt.replace("/", "-").replace("|", "-").replace(":", "-")
        for i in range(len(_dt.split("-"))):
            if len(_dt.split("-")[i]) == 1:
                _dt = _dt.replace(_dt.split("-")[i], "0"+_dt.split("-")[i])
        if len(_dt.split("-")) == 2:
            pos1 = _dt.split("-")[0]
            pos2 = _dt.split("-")[1]
            if 0 < int(pos1) < 32 and 0 < int(pos2) < 13:
                _dt = pos1+"-"+pos2+"-"+str(now.year)
        date_str.append(_dt)
    if not date_str: 
        lst = ["hôm qua", "hôm nay", "ngày mai"]
        temp = temp.replace("mai", "ngày mai")
        temp = temp.replace("qua", "hôm qua")
        temp = temp.replace("mơi", "ngày mai")
        temp = temp.replace("nay", "hôm nay")
        temp = temp.replace("bữa nay", "hôm nay")
        for word in lst:
            if re.findall(word, temp):
                date_str.append(re.findall(word, temp))
                date_str = dateparser.parse(date_str[0][0])
        return date_str
    else:
        return dateparser.parse(date_str[0], date_formats=['%d-%m-%Y'])


def getFile(url, name):  
    # Download pdf file from url
    r = requests.get(url, stream=True)

    with open(os.path.join(os.getcwd(), f'{name}.pdf'), 'wb') as f:
        f.write(r.content)
        return name


def pdfToCsv():

    df = tabula.read_pdf("myfile.pdf", encoding='utf-8', pages='all', lattice=True)
    tabula.convert_into("myfile.pdf", "output.csv", output_format="csv", pages='all')
    
    
    l = ["STT","Thứ","Ngày","Giờ","Số tiết","Phòng","SL","CBGD","Mã MH","Tên môn","Nhóm","Lớp"]
    with open("output.csv", 'r', encoding='utf-8', errors='ignore') as data_file:
        lines = data_file.readlines()
        lines[0]= ",".join(l)+"\n" # replace first line, the "header" with list contents
        with open("output.csv", 'w', encoding='utf-8', errors='ignore') as out_data:
            for line in lines: # write updated lines
                out_data.write(line)
    os.remove("myfile.pdf")
    


def findAndGetSchedule(week_number):
    url = "https://camau.bdu.edu.vn/chuyen-muc/sinh-vien/chinh-quy"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    

    # Tìm link lịch học tuần mới nhất
    for link in soup.find_all('a'):
        if link.get("title"):
            if "lịch học tuần" in link.get("title").lower():
                    if int(regex_date(str(link.get('title'))).date().isocalendar()[1]) == week_number:
                        response = requests.get(link.get('href'))
                        soup = BeautifulSoup(response.content, "html.parser")
                        iframe = soup.find('div', {'class': 'td-post-content'}).find('p').find('iframe')
                        id = iframe.get('src').split('/')[-2]
                        URL = f"https://docs.google.com/uc?id={id}&export=download"
                        getFile(URL, 'myfile')
                        pdfToCsv()
                        save_schedule('output')
                        return True
    return False


def insert_schedule(id, date_time, room, lecturer, subject, name_class, time, week_number):
        db.execute("INSERT INTO schedule(id, date_time, room, lecturer, subject, class, time, week_number)" 
            "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",id, date_time, room, lecturer, subject, name_class, time, week_number)


def save_schedule(filename):
    with open(f"{filename}.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        flag = True
        for row in reader:
            print(row)
            try:
                date = datetime.datetime.strptime(row["Ngày"], '%d/%m/%Y').date()
                if flag == True:
                    week_number = datetime.datetime.strptime(row["Ngày"], '%d/%m/%Y').date().isocalendar()[1]
                    flag = False
                insert_schedule(row["STT"] + str(week_number), date, row["Phòng"], row["CBGD"], row["Tên môn"], row["Lớp"], row["Giờ"], week_number)
            except:
                continue
            
            try:
                if row[None]:
                    db.execute("UPDATE schedule SET class=? WHERE id=?", str(row[None]), row["STT"]+str(week_number))
            except:
                continue
    
    os.remove("output.csv")
    '''
    with open(f"{filename}.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                db.execute("UPDATE schedule SET class=? WHERE id=?", row[None],row["STT"])
            except:
                continue
    ''' 

def get_schedule(class_name, date=None, week_number=None):       
        dayOfWeek = ["Thứ 2", "Thứ 3", "Thứ tư", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
        schedule = []
        # Neu co ngay cu the
        if date:
            week = date.isocalendar()[1]
            rows = db.execute("SELECT * FROM schedule WHERE week_number = ?", week)
            if rows:
                for i in rows:
                    if i["date_time"] == str(date.date()) and class_name in i["class"].lower():
                        schedule.append(i)
            else: 
                if findAndGetSchedule(date.isocalendar()[1]):
                    rows = db.execute("SELECT * FROM schedule WHERE date_time=? AND class LIKE ?", date.date(), "%" + class_name + "%")
                    if rows:
                        schedule = rows              
        if week_number:
            week_number = str(week_number)
            rows = db.execute("SELECT * FROM schedule WHERE week_number=? AND class LIKE ?", week_number, "%" + class_name + "%")
            if rows:
                schedule = rows
            else:
                 if findAndGetSchedule(int(week_number)):
                    rows = db.execute("SELECT * FROM schedule WHERE week_number = ? AND class LIKE ?", week_number, "%" + class_name + "%")
                    if rows:
                        schedule = rows
                    
        if schedule:
            rows = schedule
            for schedule in rows:
                day = datetime.datetime.strptime(schedule['date_time'], '%Y-%m-%d')
                day_of_week = dayOfWeek[day.weekday()]
                time = schedule['time']
                time = time.split("h")
                if len(time) >= 2:
                    if time[1] == "00":
                        time[1] = ""
                speak(f"Bạn có lịch học vào {day_of_week}," 
                    f"ngày {day.day} tháng {day.month} vào lúc {time[0] + ' giờ ' + time[1]}"
                    f"tại phòng {schedule['room']}")
                bot.sendMessage(chat_id=id, text=f"{day_of_week} \n" 
                    f"Ngày {day.day} Tháng {day.month}\nVào lúc: {schedule['time']}\n"
                    f"Phòng: {schedule['room']}", disable_notification=True)
                print(f"Bạn có lịch học vào ngày {day} vào lúc {schedule['time']} tại phòng {schedule['room']}")    
                    
        else:
            speak("Xin lỗi mình không tìm được lịch học của bạn")


def getHash256(a):
    m = hashlib.sha256()
    m.update(a)
    return m.hexdigest()

def getHmac512(str, key):
    h = hmac.new(key, msg=str, digestmod=hashlib.sha512)
    return h.hexdigest()


def predict_answer(model, question, contexts, seq_len=512, debug=False):
    split_context = []
    
    if not isinstance(contexts, list):
        contexts = [contexts]      
    
    for context in contexts:
        for i in range(0, len(context), seq_len):
            split_context.append(context[i:i+seq_len])
            
    split_context = contexts
    
    f_data = []
    
    for i, c in enumerate(split_context):
        f_data.append(
            {'qas': 
              [{'question': question,
               'id': i,
               'answers': [{'text': ' ', 'answer_start': 0}],
               'is_impossible': False}],
              'context': c
            })
        
    prediction = model.predict(f_data)
    if debug:
        for x in prediction[0]:
          print(x['answer'][0])
    preds = [x['answer'][0].lower().strip() for x in prediction[0] if x['answer'][0].strip() != '']
    if preds:
      return max(set(preds), key=preds.count)
    return 'No answer'
  
def query_pages(query, n=1):
    return list(search(query, num_results=n ,lang="vi"))

# Source: https://gist.github.com/lorey/eb15a7f3338f959a78cc3661fbc255fe
def markdown_to_text(markdown_string):
    """ Converts a markdown string to plaintext """

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))

    return text


def format_text(text):
    text = markdown_to_text(text)
    text = text.replace('\n', ' ')
    return text


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def getContent(url):
    try:
        html = requests.get(url, timeout = 3)
        tree = BeautifulSoup(html.text,'lxml')
        for invisible_elem in tree.find_all(['script', 'style']):
            invisible_elem.extract()

        paragraphs = [p.get_text() for p in tree.find_all("p")]

        for para in tree.find_all('p'):
            para.extract()

        for href in tree.find_all(['a','strong']):
            href.unwrap()

        tree = BeautifulSoup(str(tree.html),'lxml')

        text = tree.get_text(separator='\n\n')
        text = re.sub('\n +\n','\n\n',text)

        paragraphs += text.split('\n\n')
        paragraphs = [re.sub(' +',' ',p.strip()) for p in paragraphs]
        paragraphs = [p for p in paragraphs if len(p.split()) > 10]

        for i in range(0,len(paragraphs)):
            sents = []
            text_chunks = list(chunks(paragraphs[i],100000))
            for chunk in text_chunks:
                sents += sent_tokenize(chunk)

            sents = [s for s in sents if len(s) > 2]
            sents = ' . '.join(sents)
            paragraphs[i] = sents
    
        txt = '\n\n'.join(paragraphs)
        if len(txt) > 1000:
            for i in range(len(txt)):
                if i > 800 and txt[i] == ".":
                    return txt[:i + 1].replace(". .", ".")
        return txt.replace(". .", ".")
    except:
        #print('Cannot read ' + url, str(sys.exc_info()[0]))
        return ''

def query_to_text(query):
    txt = ""
    for link in query_pages(query, 2):
        print(link)
        txt = getContent(link)
        txt = format_text(txt)
        if txt:
            return txt
    return ""
    #return text[0]


def getStudentClass(studentClass):
    if not studentClass:
        speak("Trước hết hãy cho mình biết bạn học lớp nào nhé")
        q = takeCommand().lower()
        q = ("").join(q.split(" "))
        if re.findall("\d\d\w\w", q):
            return re.findall("\d\d\w\w", q)[0] 
        else:
            getStudentClass(studentClass)
    return studentClass

    
        
#txt = query_to_text("Số thí sinh tham dự thi đại học năm nay")
#print(txt)


#save_schedule("output")