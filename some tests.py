# import pyttsx3
# engine = pyttsx3.init()
# #engine.save_to_file('hello i am sasha', "python.ogg")
# engine.setProperty('rate', 145)
# engine.say("hello i am sasha and this is a test text! , do i like you?")
# engine.runAndWait()
from gtts import gTTS
import os
text = "Global warming is the long-term rise in the average temperature of the Earth’s climate system"
speech = gTTS(text = text)
speech.save("123.mp3")





API_TOKEN = open('./secrets/api.txt','r+').readline()
ids=[[451248878,'eng']]
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
if(os.path.isfile('./db/my_ids.pickle')):
    with open('./db/my_ids.pickle', 'rb') as data:
        ids = pickle.load(data)
        data.close()
else:
    with open('./db/my_ids.pickle','wb') as output:
        pickle.dump(ids,output)
        output.close()
vote_cb = CallbackData('vote', 'action')
start_time=time()
temporary_folder_path="./ramdisk/"
filecount=0

async def cvprocess():
    return cv2.imread(temporary_folder_path+"img.jpg",0)
async def pytesseractprocess(img,lang):
    return pytesseract.image_to_string(img, lang=lang)
async def removetempfile(path):
    return os.remove(path)
async def ocr(language):
    try:
        print("ocring")
        global filecount
        filecount+=1
        if(os.path.getsize(temporary_folder_path+'img.jpg')<1000):
            return "Error downloading file"
        try:
            img = await cvprocess()
        except:
            return "There was an error while processing your file"
        text = await pytesseractprocess(img,language)
        await removetempfile(temporary_folder_path + 'img.jpg')
        if(text==""):
            text="ERROR: No text found"
        print("done ocring")
        return text

    except:
        return "There was an error processing Your file"


async def tts(text, msgid, lang):
    language = lang[:-1]
    speech = gTTS(text=text, lang=language, slow=False)
    speech.save(temporary_folder_path + str(msgid) + ".ogg")
    return types.InputFile(temporary_folder_path + str(msgid) + ".ogg")
def get_keyboard():
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton('English \U0001F1EC\U0001F1E7', callback_data=vote_cb.new(action='eng'))).row(
        types.InlineKeyboardButton('Українська \U0001F1FA\U0001F1E6', callback_data=vote_cb.new(action='ukr')),
        types.InlineKeyboardButton('Deutsch \U0001F1E9\U0001F1EA', callback_data=vote_cb.new(action='deu')),
        types.InlineKeyboardButton('中文语言 \U0001F1E8\U0001F1F3', callback_data=vote_cb.new(action='chi_sim'))).row(
        types.InlineKeyboardButton('हिंदुस्तानी \U0001F1EE\U0001F1F3', callback_data=vote_cb.new(action='hin')),
        types.InlineKeyboardButton('Español \U0001F1EA\U0001F1F8', callback_data=vote_cb.new(action='spa')),
        types.InlineKeyboardButton('عربى' + '\U0001F1E6\U0001F1EA', callback_data=vote_cb.new(action='ara'))).row(
        types.InlineKeyboardButton('Русский \U0001F1F7\U0001F1FA', callback_data=vote_cb.new(action='rus')),
        types.InlineKeyboardButton('Portugues \U0001F1F5\U0001F1F9', callback_data=vote_cb.new(action='por')),
        types.InlineKeyboardButton('Française 🇫🇷', callback_data=vote_cb.new(action='fra')),)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await bot.send_message(message.chat.id, "To use this bot, you have to choose a language(/language), send an image PNG/JPG and wait for our bot to process it. The best result can be achieved with text that has a very high contrast compared to its background (Example purely black text on a white background. Also, cropping and aligning the image also helps. Thanks for using our bot!")

@dp.message_handler(commands=['language'])
async def send_welcome(message: types.Message):
        await bot.send_message(message.chat.id,"Choose language",reply_markup=get_keyboard() )


@dp.callback_query_handler(
    vote_cb.filter(action=['eng', 'ukr', 'deu', 'chi_sim', 'hin', 'spa', 'ara', 'rus', 'por', 'fra']))
async def callback_vote_action(query: types.CallbackQuery, callback_data: dict):
    logging.info('Got this callback data: %r', callback_data)
    await query.answer
    callback_data_action = callback_data['action']
    global ids
    used = False
    for n in ids:
        if (query.message.chat.id in n):
            ids[ids.index(n)] = [query.message.chat.id, callback_data_action]
            used = True
            break
        else:
            used = False
    if (used == False):
        ids.append([query.message.chat.id, callback_data_action])
    with open('./db/my_ids.pickle', 'wb') as output:
        pickle.dump(ids, output)


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    if(message.chat.id>=0):
         try:
            global ids
            used=False
            lang = "eng"
            for n in ids:
                if (message.chat.id in n):
                    lang = str(n[1])
                    await message.reply("Your Image is being processed(" + str(n[1]) +")")
                    used = True
                    break
                else:
                    used = False
            if (used == False):
                await message.reply("Your Image is being processed(eng)")
            try:
                await message.photo[-1].download(temporary_folder_path + 'img.jpg')
            except:
                print("error downloading")
            await bot.send_voice(message.chat.id,await tts(await ocr(lang), message.chat.id, lang))
            await removetempfile( temporary_folder_path + str(message.chat.id) + '.ogg')
