from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command,and_f
from aiogram import F
from aiogram.types import Message,ChatPermissions,input_file
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands  import set_default_commands
from baza.sqlite import Database
from filtersd.admin import IsBotAdminFilter
from filtersd.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext
from middlewares.throttling import ThrottlingMiddleware #new
from states.reklama import Adverts
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time 
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message:Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name,telegram_id=telegram_id)
        await message.answer(text="Assalomu alaykum, botimizga hush kelibsiz")
    except:
        await message.answer(text="Assalomu alaykum")


@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message:Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index,channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
    inline_channel.adjust(1,repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)





#Admin panel uchun
@dp.message(Command("admin"),IsBotAdminFilter(ADMINS))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)

@dp.message(Command("help"),IsBotAdminFilter(ADMINS))
async def ishf_admin(message:Message):
    await message.answer(text="Bu bot gruhlarni tartibga solib turadi")


@dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
async def users_count(message:Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text=="Reklama yuborish",IsBotAdminFilter(ADMINS))
async def advert_dp(message:Message,state:FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message:Message,state:FSMContext):
    
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = await db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],from_chat_id=from_chat_id,message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.5)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()


@dp.message(F.new_chat_member)
async def new_member(message:Message):
    user = message.new_chat_member.get("first_name")
    await message.answer(f"{user} Guruhga xush kelibsiz!")
    await message.delete()

@dp.message(F.left_chat_member)
async def new_member(message:Message):
    # print(message.new_chat_member)
    user = message.left_chat_member.full_name
    await message.answer(f"{user} Xayr!")
    await message.delete()

@dp.message(and_f(F.reply_to_message,F.text=="/ban"))
async def ban_user(message:Message):
    user_id =  message.reply_to_message.from_user.id
    await message.chat.ban_sender_chat(user_id)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhdan chiqarilib yuborildingiz.")

@dp.message(and_f(F.reply_to_message,F.text=="/unban"))
async def unban_user(message:Message):
    user_id =  message.reply_to_message.from_user.id
    await message.chat.unban_sender_chat(user_id)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga qaytishingiz mumkin.")

from time import time
@dp.message(and_f(F.reply_to_message,F.text=="/mute"))
async def mute_user(message:Message):
    user_id =  message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=False)

    until_date = int(time()) + 300 # 1minut guruhga yoza olmaydi
    await message.chat.restrict(user_id=user_id,permissions=permission,until_date=until_date)
    await message.answer(f"{message.reply_to_message.from_user.first_name} 5 minutga blocklandingiz")

@dp.message(and_f(F.reply_to_message,F.text=="/unmute"))
async def unmute_user(message:Message):
    user_id =  message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=True)
    await message.chat.restrict(user_id=user_id,permissions=permission)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga yoza olasiz")


# import time

# @dp.message(and_f(F.reply_to_message,F.text.startswith('/mute')))
# async def mute_user(message:Message):
#     member = await message.chat.get_member(message.from_user.id)
    
#     if member.status in ("administrator","creator"):
#         try:
#             minut = int(message.text.split("/mute")[1])
#         except:
#             minut = 1
        
#         until_date = time.time() + minut*60
#         user_id =  message.reply_to_message.from_user.id
#         permission = ChatPermissions(can_send_messages=False)

#         await message.chat.restrict(user_id=user_id,permissions=permission,until_date=until_date)
#         await message.answer(f"{message.reply_to_message.from_user.first_name} {minut} minutga blocklandingiz")
#         await message.reply_to_message.delete()
#     else:
#         await message.answer("Siz admin emassiz")

    
# @dp.message(and_f(F.reply_to_message,F.text=="/unmute"))
# async def unmute_user(message:Message):
#     user_id =  message.reply_to_message.from_user.id
#     permisins = ChatPermissions(can_send_messages=True)
#     await message.chat.restrict(user_id=user_id,permissions=permisins)
#     await message.answer(f"{message.reply_to_message.from_user.first_name} blokdan olindingiz")



from time import time
xaqoratli_sozlar = {"tentak","jinni,to'poy,axmoq"}
@dp.message(and_f(F.chat.func(lambda chat: chat.type == "supergroup"),F.text ))
async def tozalash(message:Message):
    text = message.text
    print(text)
    for soz in xaqoratli_sozlar:
        print(soz,text.lower().find(soz))
        if text.lower().find(soz)!=-1 :
            user_id =  message.from_user.id
            until_date = int(time()) + 300 # 1minut guruhga yoza olmaydi
            permission = ChatPermissions(can_send_messages=False)
            await message.chat.restrict(user_id=user_id,permissions=permission,until_date=until_date)
            await message.answer(text=f"{message.from_user.mention_html()} guruhda so'kinganingiz uchun 5 minutga blokga tushdingiz")
            await message.delete() 
            break
    

@dp.message(and_f(F.chat.func(lambda chat: chat.type == "supergroup"),F.animation))
async def git_yuborma(message:Message):
    user_id =  message.from_user.id
    await message.chat.ban_sender_chat(user_id)
    await message.answer(f"{message.from_user.mention_html()} Siz katta xato qildingiz va 1 soatga bloklandingiz😔 ")
    await message.delete()

          
@dp.message(and_f(F.chat.func(lambda chat: chat.type == "supergroup"),F.photo))
async def gef_yuborma(message:Message):
            user_id =  message.from_user.id
            await message.chat.ban_sender_chat(user_id)
            await message.answer_photo(f"{message.from_user.mention_html()} E bolla katta xato qilding rasm tashlab 1 soatga bliklanding 😔")
            await message.delete()

@dp.message(and_f(F.chat.func(lambda chat: chat.type == "supergroup"),F.video))
async def gef_yuborma(message:Message):
            user_id =  message.from_user.id
            await message.chat.ban_sender_chat(user_id)
            await message.answer_video(f"{message.from_user.mention_html()} E bolla katta xato qilding vidyo tashlab 1 soatga bloklanding 😔")
            await message.delete()
          


@dp.message(and_f(F.reply_to_message,F.text=="/setphoto"))
async def setphoto_group(message:Message):
    photo =  message.reply_to_message.photo[-1].file_id
    file = await bot.get_file(photo)
    file_path = file.file_path
    file = await bot.download_file(file_path)
    file = file.read()
    await message.chat.set_photo(photo=input_file.BufferedInputFile(file=file,filename="asd.jpg"))
    await message.answer("Gruh rasmi uzgardi")


@dp.message(F.text.startswith('/setname'))
async def set_name(message: Message):
    text = message.text.split("/setname")[1]
    print(text)
    if text:
        await message.chat.set_title(text)



@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishga tushdi")
            # await bot.restrict_chat_member(-1002143843957,6208545740,ChatPermissions(can_send_messages=True))
        except Exception as err:
        
            logging.exception(err)
            # @dp.startup()

   

#bot ishga tushganini xabarini yuborish
@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)




async def main() -> None:
    global bot,db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    db = Database(path_to_db="main.db")
    db.create_table_users()
    await set_default_commands(bot)
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    await dp.start_polling(bot)
    




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())
