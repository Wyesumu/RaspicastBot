#!.venv/bin/python3

import telebot
from telebot import types
from telebot.types import Message, Update
import random, logging, sys, os, time, logging
from tinydb import TinyDB, Query
#import pexpect
import youtube_dl
from yandex_music.client import Client
from requests import get as requests_get

queue = []
YA_COUNT = 20 #amout of tracks to get from yandex playlist
URL = 't.me/raspicast_bot'
BOT_NAME = 'RaspicastBot'

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
keyfile = open(os.path.join(__location__, 'apiKey.txt'), "r")
TOKEN = keyfile.read().replace('\n', '')
STICKERS_APPROVED = [
    'CAADBAADQAADyIsGAAE7MpzFPFQX5QI',
    'CAADBAADGQADyIsGAAFl6KYZBflVyQI',
    'CAADBQADbgMAAukKyAN8NA8_2uwEbQI',
    'CAADBQADiQMAAukKyAPZH7wCI2BwFwI',
    'CAADBQADbwMAAukKyAOvzr7ZArpddAI',
    'CAADBQADrAMAAukKyAOwtKgu24enOwI',
    'CAADBQADpgMAAukKyAN5s5AIa4Wx9AI',
    'CAADBAAEAgAC4nLZAAE7R15Jpzl7cAI'
]
STICKERS_DONTKNOW = [
    'CAADBQADqgMAAukKyAOMMrddotAFYQI',
    'CAADBQADwwMAAukKyAPFFlt0dg1c3wI',
    'CAADBQADhAMAAukKyAPQ5EQgpjzLMwI',
    'CAADBQADnAMAAukKyAPo8e_mkstdpQI',
    'CAADBQADfgMAAukKyAMythx0wTDJDAI'
]

BOT_USERS_DB = os.path.join(__location__, 'bot_userlist.json')
ADMIN_USER = ['WarScout']
CURRENT_UNIX_DATE = int(time.time())

logging.basicConfig(
    filename=os.path.join(__location__, 'raspicast.log'),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger("RaspberryCast")

telebot.apihelper.proxy = {'https': 'socks5://107032675:WvlVdfo3@grsst.s5.opennetwork.cc:999'}

bot = telebot.TeleBot(TOKEN)
db = TinyDB(BOT_USERS_DB)
query = Query()

HELP_MESSAGE = """To play a video just send a link to me anytime without any commands
                
                This is a list of commands available.
                /controls - Show video controls
                /playlist - Show current playlist
                /play [id] - Play item from playlist by it's id
                /admin - Show additional admin menu
                /shutdown - Power-off the Raspicast
                /reboot - Reboot the device
                /2x2 - Start 2x2 live stream
                /yandex <username>:<password> - log in to your yandex account
                /yandex - to get your token
                
                Pick one bellow"""

@bot.message_handler(commands=['2x2'])
def zxz(message):
    response = str(requests_get('https://bl.zxz.su/live/317805/HLS/4614144_3,2883584_1,1153024_2/1565365354/7f8af41900de19bdc17d60ec3cc113ca/playlist.m3u8').content)
    #found this link on official 2x2 site, parced it from network requests by their player.
    #every amount of time this site generates new link to chunklist.m3u8 file
    url = response[response.find('https://'):response.find('chunklist.m3u8')+14]
    if url != '':
        bot.send_sticker(message.chat.id, random.choice(STICKERS_APPROVED))
        controls(message)
        launchvideo(url, '2x2 live')
    else:
        bot.send_message(message.chat.id, "Wasn't able to fetch a link, here's response: " + response)

@bot.message_handler(commands=['yandex'])
def yandex(message):
    if len(message.text) > 7: #if command has some arguments
        login = message.text[8:message.text.find(':')]
        password = message.text[message.text.find(':')+1::]

        client = Client.from_credentials(login, password) #log in with login and password
        db.update({'ya_token':client.token}, query.username == message.from_user.username) #then get user's token and save it into db
        bot.send_message(message.chat.id, 'New login and password: ' + str(login) + ' ' + str(password))
    else:
        user = db.search(query.username == message.from_user.username)
        if user[0]['ya_token'] == '-':
            bot.send_message(message.chat.id, 'You are not logged into your Yandex account. Please, type /yandex <username>:<password>')
        bot.send_message(message.chat.id,'You are logged in with token ' + user[0]['ya_token'])

@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        bot.reply_to(message, """Hi %s, what would you like me to play?
        Use /help to check all my potential""" % message.from_user.first_name)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        itembtn1 = types.KeyboardButton('/help')
        itembtn2 = types.KeyboardButton('/controls')
        itembtn3 = types.KeyboardButton('/playlist')
        markup.add(itembtn1, itembtn2, itembtn3)
        bot.send_message(message.chat.id, "Choose the option:", reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        bot.send_message(message.chat.id, HELP_MESSAGE)
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        itembtn1 = types.KeyboardButton('/shutdown')
        itembtn2 = types.KeyboardButton('/reboot')
        itembtn3 = types.KeyboardButton('/playlist')
        itembtn4 = types.KeyboardButton('/admin')
        itembtn5 = types.KeyboardButton('/controls')
        itembtn6 = types.KeyboardButton('/2x2')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
        bot.send_message(message.chat.id, "Choose the option:", reply_markup=markup)

@bot.message_handler(commands=['shutdown'])
def send_poweroff(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    elif not db.search(query.username == message.from_user.username):
        bot.reply_to(message, """Sorry. Permission denied""")
    else:
        bot.reply_to(message, f"""{BOT_NAME} is going down for POWER-OFF. 
        To start it back please plug the power cable again""")
        logger.info('Power-off signal received.')
        os.system('sudo shutdown -h now')


@bot.message_handler(commands=['reboot'])
def send_reboot(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    elif not db.search(query.username == message.from_user.username):
        bot.reply_to(message, """Sorry. Permission denied""")
    else:
        bot.reply_to(message, f"""{BOT_NAME} is going for REBOOT """)
        logger.info('Reboot signal received.')
        os.system('sudo reboot')

@bot.message_handler(commands=['admin'])
def admin(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        logger.info('Admin menu signal received.')
        bot.reply_to(message, f"""{BOT_NAME} admin menu.""")
        admin_pannel(message)

@bot.message_handler(commands=['controls'])
def show_controls(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        controls(message)

@bot.message_handler(commands=['play'])
def go_to(message): #play video from playlist by id
    try:
        id = int(message.text[5:])
        os.system('echo g ' + str(id) + ' > /var/run/omxctl')
        bot.send_message(message.chat.id, 'Playing ' + queue[id]['title'])
    except ValueError:
        bot.send_message(message.chat.id, 'The number you send is not integer')

@bot.message_handler(commands=['playlist'])
def playlist(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        if queue:
            result = ''
            with open('/var/log/omxstat', 'r') as file:
                stat = file.read() #in this file stored info about current state of player and also link to video or track which is playing now

            for id, element in enumerate(queue): #create user-friendly list of elements in playlist
                result += str(id) + ' ' + element['title']

                if element['url'] in stat: #add [PLAY] if url can be found in omxstat file
                    result += ' [PLAY]'
                result += '\n'

            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, 'Playlist is empty')

@bot.message_handler(content_types=['text'])
def message(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    elif not db.search(query.username == message.from_user.username) and (message.from_user.username not in ADMIN_USER):
        bot.reply_to(message, """Sorry. Permission denied""")
        logger.info(f'Got permission denied for user {message.from_user.username}')
    else:
        url = message.text
        if url.startswith('http'):
            bot.send_sticker(message.chat.id, random.choice(STICKERS_APPROVED))
            controls(message)
            launchvideo(url, message)

        if '+ vol' in message.text:
            logger.info('Volume increase signal received.')
            os.system("echo + > /var/run/omxctl")
        if '- vol' in message.text:
            logger.info('Volume decrease signal received.')
            os.system("echo - > /var/run/omxctl")
        if 'pause/resume' in message.text:
            logger.info('Pause/Resume signal received.')
            os.system("echo p  > /var/run/omxctl")
        if 'stop' in message.text:
            logger.info('Stop video signal received.')
            os.system("echo X > /var/run/omxctl")
            global queue
            queue.clear()
        if '-30 seconds' in message.text:
            logger.info('-30 seconds signal received.')
            os.system("echo r > /var/run/omxctl")
        if '+30 seconds' in message.text:
            logger.info('+30 seconds signal received.')
            os.system("echo f > /var/run/omxctl")
        if 'fast forward' in message.text:
            logger.info('Fast forward signal received.')
            os.system("echo F > /var/run/omxctl")
        if 'previous' in message.text:
            logger.info('Previous item signal received.')
            os.system("echo N > /var/run/omxctl")
        if 'next' in message.text:
            logger.info('Next item signal received.')
            os.system("echo n > /var/run/omxctl")
        # Admin Commands
        if 'Add User' in message.text:
            if message.from_user.username not in ADMIN_USER:
                bot.reply_to(message, """Sorry. Permission denied""")
                logger.info(f'Got ADMIN permission denied for user {message.from_user.username}')
            else:
                bot.send_message(message.chat.id, """Give me a telegram username to add user""")
                bot.register_next_step_handler(message, add_username)
        if 'Delete User' in message.text:
            if message.from_user.username not in ADMIN_USER:
                bot.reply_to(message, """Sorry. Permission denied""")
                logger.info(f'Got ADMIN permission denied for user {message.from_user.username}')
            else:
                bot.send_message(message.chat.id, """Give me a telegram username to delete from users list""")
                bot.register_next_step_handler(message, delete_username)
        if 'List Users' in message.text:
            if message.from_user.username not in ADMIN_USER:
                bot.reply_to(message, """Sorry. Permission denied""")
                logger.info(f'Got ADMIN permission denied for user {message.from_user.username}')
            else:
                bot.send_message(message.chat.id, """Here is the list of users""")
                list_users(message)

def add_username(message: Message):
    try:
        username = message.text
        db.insert({'username': username, 'ya_token': '-' })
        bot.reply_to(message, f'User {username} successfully added')
    except Exception as e:
        bot.reply_to(message, 'oooops')

def delete_username(message: Message):
    try:
        username = message.text
        db.remove(query.username == username)
        bot.reply_to(message, f'User {username} successfully deleted')
    except Exception as e:
        bot.reply_to(message, 'oooops')

def list_users(message: Message):
    try:
        bot.send_message(message.chat.id, str(db.all()))
    except Exception as e:
        bot.reply_to(message, 'oooops')

def start_process(videourl, info=None):
    global queue
    if info is None: #if title isn't given then use link
        info = videourl

    os.system("echo A '" +  videourl + "' > /var/run/omxctl") #send url to player
    queue.append({'url':videourl, 'title':info}) #and add it to playlist
    logger.info('Added ' + info)

def controls(message: Message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('+ vol')
    itembtn2 = types.KeyboardButton('stop')
    itembtn3 = types.KeyboardButton('pause/resume')
    itembtn4 = types.KeyboardButton('- vol')
    itembtn5 = types.KeyboardButton('-30 seconds')
    itembtn6 = types.KeyboardButton('+30 seconds')
    itembtn7 = types.KeyboardButton('fast forward')
    itembtn8 = types.KeyboardButton('previous')
    itembtn9 = types.KeyboardButton('next')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9)
    bot.send_message(message.chat.id, "Controls:", reply_markup=markup)

def admin_pannel(message: Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
    itembtn1 = types.KeyboardButton('Add User')
    itembtn2 = types.KeyboardButton('Delete User')
    itembtn3 = types.KeyboardButton('List Users')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id,"Here are available Admin Controls", reply_markup=markup)

def get_yandex_direct(track): #get direct link for yandex.Music track
    for file in track.get_download_info(get_direct_links=True):
        if file.codec == 'mp3':
            return file.direct_link

def launchvideo(url, message):
    logger.info(f"Parsing source url for {url}")
    #if got direct link to video
    if ((url[-4:] in (".avi", ".mkv", ".mp4", ".mp3")) or (".googlevideo.com/" in url)):
        logger.info('Direct video URL, no need to use youtube-dl.')
        start_process(url)
    #if got yandex music
    elif 'music.yandex.ru' in url:
        user = db.search(query.username == message.from_user.username)
        if user[0]['ya_token'] == '-':
            client = Client()
        else:
            client = Client.from_token(user[0]['ya_token'])

        if 'album' in url and 'track' in url: #if got link to one track
            album_id = url[url.find('album')+6:url.find('track')-1]
            track_id = url[url.find('track')+6::]

            track = client.tracks(track_id + ':' + album_id)[0]
            bot.send_message(message.chat.id, 'Playing ' + track.title + ' by ' + track.artists[0].name)
            start_process(get_yandex_direct(track), track.title + ' - ' + track.artists[0].name)

        else: #if got link to playlist
            username = url[url.find('users')+6:url.find('playlists')-1]
            playlist_id = url[url.find('playlists')+10::]

            playlist = client.users_playlists(kind=playlist_id, user_id = username)[0]
            bot.send_message(message.chat.id, 'Now playing '+ playlist['title'])

            if len(playlist.tracks) < YA_COUNT: #get specific amount of tracks from playlist
                length = len(playlist.tracks)
            else:
                length = YA_COUNT

            for i in range(0,length):
                track = client.tracks(playlist.tracks[i].id)[0]
                logger.info('now getting direct link for ' + track.title + ' by ' + track.artists[0].name)
                start_process(get_yandex_direct(track), track.title + ' - ' + track.artists[0].name)
                logger.info('finished')

    #everything else
    else:
        #init youtube DL
        ydl = youtube_dl.YoutubeDL(
            {
                'logger': logger,
                'noplaylist': True,
                'ignoreerrors': True,
            })  # Ignore errors in case of error in long playlists

        with ydl:  # Downloading youtub-dl infos. We just want to extract the info
            result = ydl.extract_info(url, download=False)

        if result is None:
            bot.send_message(message.chat.id, 'Error fetching url')
            logger.error(
                "Result is none, returning none. Cancelling following function.")
            return None

        if 'entries' in result:  # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            video = result  # Just a video

        if "youtu" in url:
            logger.info('''CASTING: Youtube link detected.
                Extracting url in maximal quality.''')
            for fid in ('22', '18', '36', '95', '94', '93'): # also 137,136, but these are only videos #95,94,93 is for live streams
                for i in video['formats']:
                    if i['format_id'] == fid:
                        logger.info(
                            'CASTING: Playing highest video quality ' +
                            i['format_note'] + '(' + fid + ').'
                        )
                        start_process(i['url'], video['title'])
                        return None

        elif "vimeo" in url:
            logger.info('Vimeo link detected, extracting url in maximal quality.')
            start_process(video['url'],  video['title'])
        else:
            logger.info('''Video not from Youtube or Vimeo.
                Extracting url in maximal quality.''')
            start_process(video['url'], video['title'])

bot.polling(timeout=60)

'''
## About
Send your video link to the Raspicast device from anywhere and from multiple users without sharing the ssh connection.
## Description
This is a Telegram bot that runs on top of a configured Raspicast device(https://pimylifeup.com/raspberry-pi-chromecast/) and listens for video links and commands to control it.
## Commands to be set in BotFather
start - start the bot
controls - show video controls
admin - admin menu
playlist - create a playlist
shutdown - power-off the device
reboot - reboot the device
'''
