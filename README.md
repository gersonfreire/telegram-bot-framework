<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/FxL5qM0.jpg" alt="Bot logo"></a>
</p>

<h3 align="center">Telegram Bot Framework</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> 🤖 Application-level library for building bots in Telegram.
    <br> 
</p>

[Project&#39;s Telegram group](https://t.me/TlgBotFwk)

[Demo Bot](https://t.me/TecVitoriaBot)

## 📝 Table of Contents

- [About](#about)
- [How it works](#working)
- [Usage](#usage)
- [Getting Started](#getting_started)
- [Authors](#authors)

## 🧐 About

You can find many libraries and modules ready to build bots on Telegram, but none of them cover the basic functionalities that are almost indispensable, such as creating a help menu automatically from commands, registering users, generating a log in the Telegram administrator and others. The purpose of this library is to fill these gaps and allow Telegram bot developers to quickly create powerful, stable and secure bots in just a few lines of code. This work is still in its early stages, but I invite you to help me explore and conquer the fascinating world of Telegram bots by collaborating and using this library.

## 💭 How it works

Basically, we build a class called TlgBotFwk, which inherits from the Application class, implemented by the telegram.ext library, provided by the python-telegram-bot package, version 21 or greater ([https://github.com/python-telegram-bot/python-telegram-bot]()). In this child class, we implement some default methods to handle the universal commands /start, /help and other unrecognized commands. However, the developer can implement their own command handlers without losing the built-in functionality. I recommend reading the source code for more details. I also recommend Python 3.12 version.

## 🎈 Usage

To use this class, just create a simple script with bellow lines of code and the bot will run:

```
if __name__ == '__main__':
  
    app = TlgBotFwk()  
    app.run()
```

Don´t forget to create a .env file, because the framework will load settings like Telegram Token and Admin user Id from it. You will find a sample.env file on project root, with this content, which could be got as explained bellow

```
DEFAULT_BOT_TOKEN=<PUT YOUR BOT TOKEN HERE> 
DEFAULT_BOT_OWNER=<PUT HERE YOUR TELEGRAM ID> 
```

To get a Telegram bot token from BotFather to use in a Python bot script, follow these steps:

1. **Start a Chat with BotFather** :

* Open Telegram and search for “BotFather”.
* Start a conversation by clicking the “Start” button.

1. **Create a New Bot** :

* Type `/newbot` and send the message.
* BotFather will ask for a name for your bot. Choose a name that ends with “Bot”, like “MyAwesomeBot”.

1. **Choose a Username** :

* After naming the bot, BotFather will ask for a unique username for your bot. It must end in “bot” (e.g., `AwesomeBot` or `MyAwesomeBot_bot`).

1. **Receive the Token** :

* Once you’ve provided a valid username, BotFather will generate a token for your bot.
* The token will look something like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`.

1. **Save the Token** :

* This token is essential for accessing the Telegram Bot API. Copy and save it somewhere secure, as you’ll need it to authenticate your bot in your Python script.

1. **Using the Token in .env** :

* In your .env file, you can use this token replacing it on `<PUT YOUR BOT TOKEN HERE>`.

To get your telegram Id and replace `<PUT YOUR TELEGRAM ID HERE>`, follow these steps:

 **Start a Chat with a Bot that Reveals User ID** :

* Search for a bot like [userinfobot](https://t.me/userinfobot) or any other similar bot in Telegram.
* Start the chat by clicking "Start."
* Get the number after "Id:" and replace it on .env

## 🏁 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them.

```
-A Python IDE like VS Code or PyCharm (I recommend VS Code)
-Local Python 3.12 or above installed
-pip 24 or above installed
```

### Installing

A step by step series of examples that tell you how to get a development env running.

Clone this entire repository

```
git clone https://github.com/gersonfreire/tlgfwk.git
```

Install dependencies

```
pip -r requirements.txt
```

Run main function of base class

```
python tlgfwk.py
```

## TODOs:

* [X] Last Stable Version: 0.1.7 *✓*
* [X] Deploy a demo instance - Bot running on [Demo Bot](https://t.me/TecVitoriaBot) ✓
* [X] Add handlers to telegram menu commands ✓
* [X] Auto-update by git pull ✓
* [X] Command to restart the bot ✓
* [X] Encrypt/decrypt the bot token from/to .env file ✓
* [X] Optional disable_encryption parameter on class creation to Encrypt/decrypt .env file ✓
* [X] Create an empty .env file at run time if it does not exist ✓
* [X] Ask the bot owner to input a token in case the token is not valid ✓
* [X] Encrypt .env fixed ✓
* [ ] Show embedded help html page
* [ ] Create a command to encrypt and decrypt strings
* [ ] Add a way to save the bot token for next run
* [ ] Add persistence for user and bot data
* [ ] Allow more than one owner
* [ ] Logger to Telegram
* [ ] Add a way to get or change the bot token
* [ ] Add a way to get the bot owner id
* [ ] Add a way to get the bot name
* [ ] Add a way to get the bot version
* [ ] Add a way to get the bot hostname
* [ ] Add a way to get the bot script path
* [ ] Add a way to get the bot main script path
* [ ] Add a way to get the bot log folder
* [ ] Add a way to get the bot log file
* [ ] Add a way to get the bot log level

# TODO: Show ebedded help html page

# TODO: Show ebedded help html page

## ✍️ Authors

- [@gersonfreire](https://github.com/kylelobo) - Idea & Initial work

Engage yourself entering the  [Project&#39;s Telegram group](https://t.me/TlgBotFwk) and see also the list of contributors who participated in this project
Please, feel free to join us and let´s build a full and powerfull real framework for bots.
