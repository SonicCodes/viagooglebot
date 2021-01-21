# [@viagooglebot](https://t.me/viagooglebot)
## [@viagooglebot](https://t.me/viagooglebot) is an [inline telegram-bot](https://core.telegram.org/bots/inline) that uses a multi-threaded (🧵🧵🧵) scrapper to ensure the results are delivered as ⚡️ & 🧹 as possible.

## 🦾 Mechanism of action.
- ### User requests query 🙋
- ### Results are fetched from google page 😜
- ### Beautiful soap is applied on the fetchee 😍
- ### Three Threaded jobs are created 🧵🧵🧵
- ⚡️ Quick Answers 
- 📈 Knowledge Graph 
- 📙 Google Search Results 
- ### Those three results will be 
- Smashed 💥
- Sorted 🧮 
- Delivered 🚚

## 👷 Configuration (config.py).
- mongodbcred = str ```🔗🏬 MongoDB connection url, if you want to track searches or users. you can disable this if you want```
- mongodb = str ```🏬 MongoDB database name```
- serverport = int ```🛬 The port to use for the server```
- analytics_code = str ```📈 Analytics code for [segment.io](https://github.com/segmentio/analytics-python), honestly this was a manic idea I made, you should remove analytics from the bot, it's useless.```
- botcode = str ```🈂️ Telegram bot token```
- boturl = str ```🔗 Telegram webhook url```
- boturlpath = str ```📁 Url path for the server```