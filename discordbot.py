from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os import getenv
import discord
import time

client = discord.Client()
last_update = None


def scrape_publish_date():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument('--proxy-server="direct://"')
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    driver.get("https://comic-days.com/episode/13932016480031248230")

    title = driver.find_element_by_class_name("episode-header-title")
    driver.execute_script("arguments[0].scrollIntoView();", title)

    time.sleep(5)

    next_update_date = driver.find_element_by_xpath("//p[@class='episode-read-date']")
    return next_update_date.text


async def reply(message):
    """
    botに対するリプライをハンドリングします。
    """
    if "使い方" in message.content:
        reply = (
            "コミックデイズにてクッキングパパの無料公開がされた事をみんなに伝えるbotだぞ！\n`次の更新日は?`とリプライすると次の更新日を教えるぞ！うむ！"
        )
        await message.channel.send(reply)
    elif "次の更新日は?" in message.content:
        await message.channel.send(f"{last_update}だぞ！")
    else:
        await message.channel.send(f"{message.author.mention} 腹が減ったのか？")


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if client.user in message.mentions:
        await reply(message)


@tasks.loop(minutes=5)
async def loop():
    global last_update
    publish_date = scrape_publish_date()

    channel_id = int(getenv("CHANNEL_ID"))
    channel_sent = client.get_channel(channel_id)

    if last_update is None:
        last_update = publish_date
    elif last_update != publish_date:
        last_update = publish_date
        await channel_sent.send(
            "@everyone 今日はクッキングパパの更新日だぞ！\nhttps://comic-days.com/episode/13932016480031248230"
        )


@client.event
async def on_ready():
    loop.start()


token = getenv("DISCORD_BOT_TOKEN")
client.run(token)
