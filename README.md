# Daily-Programmer

Programming Question Bot is a powerful and easy-to-use bot that retrieves a daily programming question from an email using the Gmail API and then sends it to a Discord channel. Designed for communities of all sizes, it is especially tailored for large groups, easily handling channels with 1000+ members.

<img width="720" alt="Screenshot 2023-10-20 at 2 42 16 AM" src="https://github.com/ritessshhh/Discord-Daily-Programming/assets/81812754/680551f7-d4c3-4c30-b8be-eae2119c1675">

## Features

- **Daily Questions:** A new programming question is sent to your Discord channel every day, ensuring your community stays engaged and challenged.
- **Gmail Integration:** Seamlessly retrieves emails containing the questions using the Gmail API.
- **Scalable:** Optimized for performance, efficiently serving large communities with 1000+ members.
- **Customizable:** Easily configurable to meet the specific needs of your community.

## Prerequisites

Ensure you have the following installed on your machine before running the bot:

- google-api-python-client==2.33.0
- google-auth==2.3.3
- google-auth-oauthlib==0.4.10
- google-auth-httplib2==0.1.0
- Discord

Also, make sure to set up a Google Cloud Project, enable the Gmail API, and get the `credentials.json` file. You will also need to create a Discord bot and invite it to your server.

## Installation

Clone this repository:

```sh
git clone https://github.com/your-username/programming-question-bot.git
cd programming-question-bot
