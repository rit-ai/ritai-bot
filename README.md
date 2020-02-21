![logo of rit-ai club](docs/bot_logo.png)

# RIT-AI Bot

This is code to run a Slackbot for the RITficial Intelligence club at RIT. If you would like to run it, you will need the Bot User Secret, which the Eboard should be able to provide you.

## Installation

Install requirements.
```
pip install -r requirements.txt
```

Run `export APP_BOT_USER_TOKEN=<your bot token here>`

Then, you can run the app with this command:
```
python3 driver.py
```

This setup is constructed so that the program can also be run easily on a Docker image. 

It runs continuously. So far it has access to these commands, all prepended with @ritai:

* `mnist <image>` -- guesses the number in an image
* `kmeans [k_value] <image>` -- applies color simplification to an image via k-means clustering
* `stylize [style] <image>` -- applies neural style transfer to an image
