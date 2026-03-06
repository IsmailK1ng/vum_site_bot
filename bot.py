from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import asyncio
from database import Base, engine, SessionLocal
from models.user_model import User
from config import BOT_TOKEN, ADMIN_ID
from datetime import datetime

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
from config import BOT_TOKEN, ADMIN_ID

# print("ADMIN ID:", ADMIN_ID)
# print("TYPE:", type(ADMIN_ID))
# ================= REGIONS =================

UZ_REGIONS = {
    "Toshkent shahri": ["Yunusobod", "Chilonzor", "Olmazor", "Yashnobod", "Mirzo Ulug‘bek", "Sergeli", "Bektemir"],
    "Toshkent viloyati": ["Zangiota", "Chinoz", "Parkent", "Bo‘ka", "Ohangaron", "Oqqo‘rg‘on", "Bekobod"],
    "Samarqand": ["Urgut", "Kattaqo‘rg‘on", "Bulung‘ur", "Narpay", "Toyloq", "Qo‘shrabot", "Ishtixon"],
    "Andijon": ["Asaka", "Shahrixon", "Xo‘jaobod", "Qo‘rg‘ontepa", "Baliqchi", "Ulug‘nor", "Oltinko‘l", "Andijon"],
    "Farg‘ona": ["Qo‘qon", "Marg‘ilon", "Farg‘ona", "Oltiariq", "Beshariq", "Quva", "Rishton"],
    "Namangan": ["Chust", "Kosonsoy", "Namangan", "Pop", "To‘raqo‘rg‘on", "Uychi", "Mingbuloq"],
    "Buxoro": ["G‘ijduvon", "Kogon", "Buxoro", "Vobkent", "Peshku", "Romitan", "Shofirkon"],
    "Xorazm": ["Urganch", "Xiva", "Shovot", "Gurlan", "Yangiariq", "Bog‘ot", "Xonqa"],
    "Qashqadaryo": ["Qarshi", "Shahrisabz", "G‘uzor", "Chiroqchi", "Koson", "Kitob", "Dehqonobod"],
    "Surxondaryo": ["Termiz", "Denov", "Boysun", "Muzrabot", "Sariosiyo", "Qumqo‘rg‘on", "Sherobod"],
    "Jizzax": ["Zomin", "G‘allaorol", "Zarbdor", "Do‘stlik", "Yangiobod", "Arnasoy", "Baxmal"],
    "Sirdaryo": ["Guliston", "Yangiyer", "Sirdaryo", "Oqoltin", "Shirin", "Boyovut"],
    "Navoiy": ["Zarafshon", "Karmana", "Navoiy", "Qiziltepa", "Tomdi", "Xatirchi", "Konimex"],
    "Qoraqalpog‘iston": ["Nukus", "Xo‘jayli", "Kegeyli", "Chimboy", "Taxtako‘pir", "Beruniy", "Qo‘ng‘irot"]
}

# ================= LANGUAGE =================

LANG_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
    ],
    resize_keyboard=True
)

ADMIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Foydalanuvchilar ro‘yxati")]
    ],
    resize_keyboard=True
)

MESSAGES = {
    "uz": {
        "choose_lang": "Tilni tanlang 🌐",
        "send_phone": "Telefoningizni yuboring 📞",
        "send_first_name": "Ismingizni kiriting",
        "send_last_name": "Familiyangizni kiriting",
        "send_birth": "Tug‘ilgan sanangizni kiriting (YYYY-MM-DD)",
        "choose_region": "Viloyatingizni tanlang",
        "choose_district": "Tumaningizni tanlang",
        "saved": "Ma'lumotlaringiz saqlandi ✅",
        "wrong_format": "Format noto‘g‘ri ❌\nYYYY-MM-DD shaklida kiriting",
        "choose_from_list": "Iltimos ro‘yxatdan tanlang"
    },
    "ru": {
        "choose_lang": "Выберите язык 🌐",
        "send_phone": "Отправьте ваш номер телефона 📞",
        "send_first_name": "Введите имя",
        "send_last_name": "Введите фамилию",
        "send_birth": "Введите дату рождения (YYYY-MM-DD)",
        "choose_region": "Выберите область",
        "choose_district": "Выберите район",
        "saved": "Ваши данные сохранены ✅",
        "wrong_format": "Неверный формат ❌\nВведите в формате YYYY-MM-DD",
        "choose_from_list": "Пожалуйста выберите из списка"
    }
}

# ================= INIT =================

Base.metadata.create_all(bind=engine)

# bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

user_state = {}
user_lang = {}

# ================= START =================

@dp.message(Command("start"))
async def start(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    # 👑 ADMIN
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 Admin panel", reply_markup=ADMIN_KEYBOARD)
        return

    if not user:
        user_state[message.from_user.id] = "lang"
        await message.answer(MESSAGES["uz"]["choose_lang"], reply_markup=LANG_KEYBOARD)
    else:
        await message.answer("Xush kelibsiz 👋")

# ================= LANGUAGE =================

@dp.message(F.text.startswith("🇺🇿") | F.text.startswith("🇷🇺"))
async def choose_language(message: types.Message):
    db = next(get_db())

    lang = "uz" if message.text.startswith("🇺🇿") else "ru"
    user_lang[message.from_user.id] = lang

    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not user:
        user = User(telegram_id=message.from_user.id)
        db.add(user)

    user.language = lang
    db.commit()

    user_state[message.from_user.id] = "phone"

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Telefon yuborish", request_contact=True)]],
        resize_keyboard=True
    )

    await message.answer(MESSAGES[lang]["send_phone"], reply_markup=kb)

# ================= CONTACT =================

@dp.message(F.contact)
async def save_phone(message: types.Message):
    db = next(get_db())
    lang = user_lang.get(message.from_user.id, "uz")

    if message.contact.user_id != message.from_user.id:
        await message.answer("❌")
        return

    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    user.phone = message.contact.phone_number
    user.username = message.from_user.username
    db.commit()

    user_state[message.from_user.id] = "first_name"
    await message.answer(MESSAGES[lang]["send_first_name"], reply_markup=ReplyKeyboardRemove())

# ================= MAIN PROCESS =================

@dp.message()
async def register_process(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    state = user_state.get(message.from_user.id)
    lang = user_lang.get(message.from_user.id, "uz")

    if not user:
        return

    if state == "first_name":
        user.first_name = message.text
        db.commit()
        user_state[message.from_user.id] = "birth_date"
        await message.answer(MESSAGES[lang]["send_birth"])


    elif state == "birth_date":
        try:
            birth = datetime.strptime(message.text, "%Y%m%d").date()
            user.birth_date = birth
            db.commit()

            user_state[message.from_user.id] = "region"

            region_kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=r)] for r in UZ_REGIONS.keys()],
                resize_keyboard=True
            )

            await message.answer(MESSAGES[lang]["choose_region"], reply_markup=region_kb)

        except:
            await message.answer(MESSAGES[lang]["wrong_format"])

    elif state == "region":
        if message.text in UZ_REGIONS:
            user.city = message.text
            db.commit()

            districts = UZ_REGIONS[message.text]
            district_kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=d)] for d in districts],
                resize_keyboard=True
            )

            user_state[message.from_user.id] = "district"
            await message.answer(MESSAGES[lang]["choose_district"], reply_markup=district_kb)
        else:
            await message.answer(MESSAGES[lang]["choose_from_list"])

    elif state == "district":
        user.city = f"{user.city}, {message.text}"
        db.commit()

        user_state.pop(message.from_user.id)
        await message.answer(MESSAGES[lang]["saved"], reply_markup=ReplyKeyboardRemove())

# ================= ADMIN USERS LIST =================


@dp.message(F.text == "📋 Foydalanuvchilar ro‘yxati", F.from_user.id == ADMIN_ID)
async def show_users(message: types.Message):

    db = next(get_db())
    users = db.query(User).all()

    if not users:
        await message.answer("Foydalanuvchilar yo‘q ❌")
        return

    text = "📊 <b>Foydalanuvchilar ro‘yxati:</b>\n\n"

    for user in users:
        birth_date = user.birth_date.strftime("%Y-%m-%d") if user.birth_date else "-"

        text += (
            f"🆔 <b>{user.telegram_id}</b>\n"
            f"👤 {user.first_name or '-'}\n"
            f"📞 {user.phone or '-'}\n"
            f"🌍 {user.language or '-'}\n"
            f"🏙 {user.city or '-'}\n"
            f"🎂 {birth_date}\n"
            f"━━━━━━━━━━━━━━━\n"
        )

    await message.answer(text, parse_mode="HTML")


# ================= RUN =================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
