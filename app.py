from flask import Flask, request, abort
from bs4 import BeautifulSoup
import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

import os

app = Flask(__name__)

line_bot_api = LineBotApi('WfudWEWlHzmnvYnUmIax+uIAZCuF7IZTL3/d7kUc1I+Ej61Rhr86M51lmBq20ghEjJ9deoGr4p7lh3Us6I9PAySXa4IMBbuTwflCfR3eFD6kVP6iRTvQC9QmnG2PexEiFmaNaiH5i2zIYqwTJKaSpwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ab2e67f643ca640db7aacd728efda5ef')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text
    message_arr = []
    
    if(input_text == "三立"):
        html = requests.get('https://www.setn.com/ViewAll.aspx').text
        soup  = BeautifulSoup(html,'html.parser')
        newList = soup.find("div",class_="row NewsList")
        newList = newList.find_all("div", class_="col-sm-12 newsItems", limit=3)

        for i in newList:
            div = i.find("div")
            h3 = div.find("h3")
            a = h3.find("a")
            if ('https' in a.get('href')): 
                message_arr.append(TextSendMessage(a.get('href')))
            else :
                message_arr.append(TextSendMessage("https://www.setn.com/" + a.get('href')))
    elif(input_text == "中時"):
        html = requests.get('https://www.chinatimes.com/realtimenews/?chdtv').text
        soup  = BeautifulSoup(html,'html.parser')
        newList = soup.find("ul", class_="vertical-list list-style-none")
        newList = newList.find_all("h3", limit=3)

        for i in newList :
            a = i.find("a")
            if ('https' in a.get('href')): 
                message_arr.append(TextSendMessage(a.get('href')))
            else :
                message_arr.append(TextSendMessage("https://www.chinatimes.com" + a.get('href')))
    elif(input_text == "公視"):
        html = requests.get('https://news.pts.org.tw/dailynews.php').text
        soup  = BeautifulSoup(html,'html.parser')
        newList = soup.find("ul",class_="list-unstyled news-list")
        newList = newList.find_all("li", class_="d-flex", limit=3)
        
        for i in newList :
            figure = i.find("figure")
            a = figure.find("a")
            if ('https' in a.get('href')): 
                message_arr.append(TextSendMessage(a.get('href')))
            else :
                message_arr.append(TextSendMessage("https://news.pts.org.com" + a.get('href')))
    else:
        message_arr.append(TextSendMessage("如果要看三立新聞網 請輸入\"三立\"\n如果要看中時新聞網 請輸入\"中時\"\n如果要看公視新聞網 請輸入\"公視\""))
        
    line_bot_api.reply_message(event.reply_token, message_arr)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
