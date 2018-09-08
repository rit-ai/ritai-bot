This is code to run a Slackbot for the RITficial Intelligence club at RIT. If you would like to run it, you will need the Bot User Secret, which the Eboard should be able to locate for you.

Create a .sh file with these three lines:

```
export APP_ACCESS_TOKEN='<app_secret>'
export APP_BOT_USER_TOKEN='<bot_user_secret>'
python3 bot.py
```

Then, you can run this file using the command:

```
./bot.sh
```

It runs continuously. So far it has access to these commands, all prepended with @ritai:

* kmeans [image_url] [k_value] -- takes an image and applies image simplification via kmeans
