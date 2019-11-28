# RaspicastBot

Telegram bot that controls your Raspicast device.
This bot was created to make it easier to share connection to the Raspicast device without sharing ssh credentials.

# What's new?

- Added omxd (omxplayer Daemon) support. Now when you send link to bot, it will be added to the end of the playlist.
- Added Yandex.Music support (I used https://github.com/MarshalX/yandex-music-api as API). You can send link to one track or playlist and top 20 tracks (can be changed) will be played.
- Also now you can play russian [Adult Swim] analogue -- 2x2 channel in live
- Using /playlist you can see playing queue ([PLAY] shows item that's playing right now) and using /play [id] start any video from queue right now
- Using /yandex [username:password] command you can log into you Yandex account, if you have private account then this is only way you can play your tracks from bot. 
TODO: soon I will add feature to save play history in Yandex.Music account.
- Added new buttons in Control - next and previous to control playlist.
- Changed 'fast forward' button behaviour, now it will skip 10mins of video.
- Added ability to play Live Streams from youtube - in original RaspicastBot you wasn't able to do that.

## Requirements

Before starting this bot on your device, you should configure raspberry Pi as a Chromecast device.  
You can follow the guide here: https://pimylifeup.com/raspberry-pi-chromecast

Also **you have to install omxd**, here's guide: https://github.com/subogero/omxd/blob/master/INSTALL
Then you need to start it by typing ``` omxd ``` in command line. The daemon will be started.
You can add it to crontab ``` crontab -e ``` -> ``` @reboot omxd ```

By default omxd uses hdmi as audio input, if you're not then also add to crontab ``` @reboot echo j > /var/run/omxctl ```

*OPTIONAL*  
You can also configure it as a Spotify Connect client.  
Check the tutorial here: https://github.com/dtcooper/raspotify

After you configured and tested your Raspicast, you are ready to go.

![Screenshot from 2019-04-11 01-19-35](https://user-images.githubusercontent.com/17516391/55922399-d7ad8100-5bf8-11e9-969f-223a8da2650a.png)

Above is an example of the bot response when someone is sending a link to play.

## Proxy

If Telegram **isn't banned in your country** then you need to delete/comment out 52nd line from bot. This is proxy.

Also if you want to use proxy and you see ``` requests.exceptions.ReadTimeout: SOCKSHTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=70) ``` in raspicast.log then public proxy that I used might be dead then you should use another proxy.

-------

## Running the Bot

Please be sure that you have Python 3.6 installed.  

I preffer to run the bot inside of the virtualenv. But you can do as you want and skip this section. 

```
python3.6 -m venv .venv
```
This will create virtualenv inside **.venv** folder.  
```
source .venv/bin/activate
```  
Install all dependencies: 
```
pip install -r requirements.txt
```
Create **apiKey.txt** file in the same folder as the **raspicast_bot.py** script with the bot's API key  
which you retrieved from the BotFather when you created your bot in telegram.

Now you are ready to start the bot.
```
python raspicast_bot.py
```
-----
## Some features/commands of the bot

![Webp net-resizeimage](https://user-images.githubusercontent.com/17516391/56228362-8e818500-606f-11e9-960d-9851ea819a57.jpg)  
RaspicastBot has aditionally a User Management support to restrict access to the bot. Use **/admin** command to add/remove/list users by their telegram username.

Please update the [Admins list line](https://github.com/tmxak/RaspicastBot/blob/44949e9482a5022170d1dd41423952c85cc8d5da/raspicast_bot.py#L36) with your telegram username to get access to the admin (user-management) functions. 
