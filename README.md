<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/FxL5qM0.jpg" alt="Bot logo"></a>
</p>

<h3 align="center">Telegram Bot Framework</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-reddit-orange.svg)](https://www.reddit.com/user/Wordbook_Bot)
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](https://github.com/kylelobo/The-Documentation-Compendium/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](https://github.com/kylelobo/The-Documentation-Compendium/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> 🤖 Application-level library for building bots in Telegram.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Demo / Working](#demo)
- [How it works](#working)
- [Usage](#usage)
- [Getting Started](#getting_started)
- [Deploying your own bot](#deployment)
- [Built Using](#built_using)
- [TODO](../TODO.md)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

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

Don´t forget to create a .env file, because the framework will load settings like Telegram Token and Admin user Id from it. You will find a sample.env file on project root, with this content:

```
DEFAULT_BOT_TOKEN=8076729431:AAE95s3Q_QKkEtVxnProc5BRxdqxKo_S7w1
DEFAULT_BOT_OWNER=138429124
```

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

End with an example of getting some data out of the system or using it for a little demo.

## ✍️ Authors 

- [@gersonfreire](https://github.com/kylelobo) - Idea & Initial work

See also the list of contributors who participated in this project.
Please, feel free to join us and let´s build a full and powerfull real framework for bots.
