from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, Filters, MessageHandler, InlineQueryHandler
import telegram
import re
import os
from telegram.ext.dispatcher import run_async
import requests
import json
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import six
import random
import sys
import lxml.html as lh
import uuid
from pymongo import MongoClient
from telegram.ext import ChosenInlineResultHandler
from googleCode import Compose,GenerateKgMessage
from config import mongodbcred, mongodb, serverport, analytics_code, botcode, boturl, boturlpath
client = MongoClient(mongodbcred)
mdb = client.get_database(mongodb)
Searches = mdb.Searches



PORT = serverport


import analytics

analytics.write_key = analytics_code

def on_error(error, items):
    print("Analytics error occured:", error)


analytics.debug = False
analytics.on_error = on_error



@run_async
def inlinequery(update:telegram.Update, context):
    query = update.inline_query.query
    searchresult = Compose(query)
    nick= update.effective_user.username
    userid = update.effective_user.id
    try:
        b = 1
        results = []
        for i in searchresult:
            if(i["@type"] == "kgraph"):
                try:
                    results.append(telegram.InlineQueryResultPhoto(
                    id=b, photo_url=i['images'][0], thumb_url=i['images'][-1], title="📙 "+telegram.utils.helpers.escape_markdown(i["title"][0:90]), caption=i['subtitle'] or i['specificdefine'][:100], input_message_content=telegram.InputTextMessageContent(GenerateKgMessage(i), parse_mode=telegram.ParseMode.HTML)))
                except:
                    pass
                results.append(telegram.InlineQueryResultArticle(
                    id=b*999, title="📙 "+telegram.utils.helpers.escape_markdown(i["title"][0:90]), description=i['subtitle'] or i['specificdefine'][:100], input_message_content=telegram.InputTextMessageContent(GenerateKgMessage(i), parse_mode=telegram.ParseMode.HTML)))
            elif(i["@type"] == "quickie"):    
                results.append(telegram.InlineQueryResultArticle(id=b,title="ℹ️ "+telegram.utils.helpers.escape_markdown(i["result"][0:90])+"...", input_message_content=telegram.InputTextMessageContent(f"*{telegram.utils.helpers.escape_markdown(query)}*\n{telegram.utils.helpers.escape_markdown(i['result'])}\n",disable_web_page_preview=True,parse_mode=telegram.ParseMode.MARKDOWN)))
            else:
                results.append(telegram.InlineQueryResultArticle(id=b,title=telegram.utils.helpers.escape_markdown("🔗 "+i['title'][0:90]+"..."),description=telegram.utils.helpers.escape_markdown(i['description'][0:90])+"...", input_message_content=telegram.InputTextMessageContent(f"*{telegram.utils.helpers.escape_markdown(i['title'])}*\n{telegram.utils.helpers.escape_markdown(i['description'])}\n{telegram.utils.helpers.escape_markdown(i['link'])}\n",disable_web_page_preview=True,parse_mode=telegram.ParseMode.MARKDOWN)))
            b += 1
        bot.answerInlineQuery(update.inline_query.id, results)
        analytics.track(str("ANONYMOUS"), 'Searching', {
         'query': query,
         'resultLength': len(results),
         'startTime' if query == "" else "continueTime": datetime.datetime.now().strftime("{%H:%M:%S}")
        })
    except Exception as err:
        print(f"\n-----------\nError happened while searching made by {nick} for {query}\n--------\n")
        analytics.track(str("ANONYMOUS"), 'Search Error', {
         'query': query,
         'failTime':  datetime.datetime.now().strftime("{%H:%M:%S}"),
         'errorString': str(err)
        })
        raise err
import datetime
def on_result_chosen(update:telegram.Update,context):
    result = update.chosen_inline_result
    result_id = result.result_id
    query = result.query
    userid = result.from_user.id
    nick= result.from_user.username
    Searches.insert_one({"time": datetime.datetime.now(),"query":query})
    analytics.track(str("ANONYMOUS"), 'Search Completed', {
         'query': query,
         'resultId': result_id,
         'completeTime': datetime.datetime.now().strftime("{%H:%M:%S}")
    })



def searchesHandler(update, context):
    userid = update.effective_user.id
    keyboard = telegram.InlineKeyboardMarkup(
        inline_keyboard=[
            [telegram.InlineKeyboardButton(text=u'🔍  Search Now', switch_inline_query='What is the biggest star in the universe?')]
        ],
    )
    update.message.reply_text(str(Searches.count())+" Anonymous searches made till now & it's all because of you, thanks!", reply_markup=keyboard)

def startHandler(update:telegram.Update, context):
    keyboard = telegram.InlineKeyboardMarkup(
        inline_keyboard=[
            [telegram.InlineKeyboardButton(text=u'🔍  Search Now', switch_inline_query='What is the biggest star in the universe?')]
        ],
    )
    update.message.reply_text("""Hi there, I am Google Inline, invented by @ScaleAI.
/searches - For seeing the success of this bot.
    
https://www.youtube.com/watch?v=7R6DD0Djdpw
    """, reply_markup=keyboard)





def main():
    global bot
    updater=Updater(
        botcode, use_context=True)
    dp=updater.dispatcher
    dp.add_handler(InlineQueryHandler(inlinequery))
    bot=updater.bot
    dp.add_handler(CommandHandler("searches",searchesHandler))
    dp.add_handler(CommandHandler("start",startHandler))
    result_chosen_handler = ChosenInlineResultHandler(on_result_chosen)
    dp.add_handler(result_chosen_handler)
    updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=boturlpath)
    updater.bot.set_webhook(url=boturl)
    updater.idle()


if __name__ == '__main__':
    main()
