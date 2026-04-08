# bot/strings.py

STRINGS = {
    "uz": {
        "welcome": "Assalomu alaykum! Men faqat dasturlash va IT sohasiga oid savollarga javob beruvchi botman. Menga savolingizni yozishingiz, yoki guruhlarga qo'shib ishlatishingiz mumkin.",
        "lang_select": "Iltimos, muloqot tilini tanlang:",
        "lang_updated": "Til o'zgartirildi: O'zbek tili ✅",
        "only_it": "Kechirasiz, men faqat dasturlash va IT sohasiga oid savollarga javob bera olaman. 💻",
        "processing": "Savolingiz tahlil qilinmoqda... 🤔",
        "maintenance": "Hozirda texnik ishlar ketyapti. 🛠",
        "question_count_prefix": "#{count}-savolga javob:\n\n",
    },
    "ru": {
        "welcome": "Здравствуйте! Я бот, который отвечает только на вопросы, связанные с программированием и ИТ. Вы можете написать мне свой вопрос или добавить меня в группы.",
        "lang_select": "Пожалуйста, выберите язык общения:",
        "lang_updated": "Язык изменен: Русский ✅",
        "only_it": "Извините, я могу отвечать только на вопросы, связанные с программированием и ИТ. 💻",
        "processing": "Ваш вопрос анализируется... 🤔",
        "maintenance": "В настоящее время ведутся технические работы. 🛠",
        "question_count_prefix": "Ответ на вопрос #{count}:\n\n",
    },
    "en": {
        "welcome": "Hello! I am a bot that only answers questions related to programming and IT. You can write your question to me or add me to groups.",
        "lang_select": "Please select your communication language:",
        "lang_updated": "Language updated: English ✅",
        "only_it": "I'm sorry, I can only answer questions related to programming and IT. 💻",
        "processing": "Analyzing your question... 🤔",
        "maintenance": "Technical maintenance is currently underway. 🛠",
        "question_count_prefix": "Answer to question #{count}:\n\n",
    }
}

def get_string(key, lang="uz"):
    return STRINGS.get(lang, STRINGS["uz"]).get(key, STRINGS["uz"][key])
