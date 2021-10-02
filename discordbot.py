from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os import getenv
import discord
import time
import re

client = discord.Client()
channel_sent = None
last_update = None


def scrape_publish_date():
    # driver_path = "./chromedriver"
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument('--proxy-server="direct://"')
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    driver.get("https://comic-days.com/episode/13932016480031248230")

    title = driver.find_element_by_class_name("episode-header-title")
    driver.execute_script("arguments[0].scrollIntoView();", title)

    time.sleep(5)

    next_update_date = driver.find_element_by_xpath("//p[@class='episode-read-date']")
    return next_update_date.text


@client.event
async def on_message(message):
    # 送信者がbotである場合は弾く
    if message.author.bot:
        return
    if message.content == "/lastUpdate":
        await message.channel.send(last_update)


@tasks.loop(minutes=10)
async def loop():
    if channel_sent is not None:
        global last_update
        publish_date = re.sub(r"\D", "", scrape_publish_date())

        if last_update != publish_date:
            await channel_sent.send(
                "@everyone 今日はクッキングパパの更新日だぞ！\nhttps://comic-days.com/episode/13932016480031248230"
            )
            last_update = publish_date
        else:
            await channel_sent.send("今日は違います")


@client.event
async def on_ready():
    global channel_sent
    channel_id = getenv("CHANNEL_ID")
    channel_sent = client.get_channel(channel_id)

    global last_update
    last_update = re.sub(r"\D", "", scrape_publish_date())
    loop.start()


token = getenv("DISCORD_BOT_TOKEN")
client.run(token)
