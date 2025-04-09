from telegram import Bot

bot = Bot(token='8041382505:AAExVgN0Ty9bXC_Ec0Z66lOW6CYNvvilBQQ')
updates = bot.get_updates()
for update in updates:
    print(update.message.chat.id)
