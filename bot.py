import aiohttp
import asyncio
import subprocess
import threading
import re
import time
from datetime import datetime, timedelta, date
from threading import Lock
from bs4 import BeautifulSoup
import requests 
import tempfile
import subprocess, sys
import random
import json
import os
import sqlite3
import hashlib
import zipfile
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import urljoin, urlparse, urldefrag
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

THỜI_GIAN_CHỜ = timedelta(seconds=300)
FREE_GIỚI_HẠN_CHIA_SẺ = 400
VIP_GIỚI_HẠN_CHIA_SẺ = 1000
viptime = 100
ALLOWED_GROUP_ID = -4269071081   # ID BOX
admin_diggory = "light" # ví dụ : để user name admin là @diggory347 bỏ dấu @ đi là đc
ADMIN = "LÊ HOÀNG GIANG"
ZALO = "0783920611"
allowed_group_id = -4269071081 # ID BOX
users_keys = {}
key = ""
freeuser = []
auto_spam_active = False
last_sms_time = {}
allowed_users = []
processes = []
ADMIN_ID =  6854314324 # ID ADMIN
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()
last_command_time = {}


user_cooldowns = {}
share_count = {}
global_lock = Lock()
admin_mode = False
share_log = []
tool = 'no'
BOT_LINK = 'https://t.me/spamvippp'
TOKEN = '8160438179:AAE_3vzKR9KCRu8_h7BFZk5AN5hdjUqpUfs'  
bot = TeleBot(TOKEN)

ADMIN_ID = 6854314324  # id admin
admins = {6854314324}
bot_admin_list = {}
cooldown_dict = {}
allowed_users = []
muted_users = {}

def get_time_vietnam():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
def check_command_cooldown(user_id, command, cooldown):
    current_time = time.time()
    
    if user_id in last_command_time and current_time - last_command_time[user_id].get(command, 0) < cooldown:
        remaining_time = int(cooldown - (current_time - last_command_time[user_id].get(command, 0)))
        return remaining_time
    else:
        last_command_time.setdefault(user_id, {})[command] = current_time
        return None

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''') 
connection.commit()

def send_intro_video(chat_id):
    video_url = "https://files.catbox.moe/c0i8pl.mp4"
    try:
        bot.send_video(chat_id, video=video_url)
    except Exception as e:
        print(f"[❌] Lỗi gửi video: {e}")
        
def TimeStamp():
  now = str(date.today())
  return now


def load_users_from_database():
  cursor.execute('SELECT user_id, expiration_time FROM users')
  rows = cursor.fetchall()
  for row in rows:
    user_id = row[0]
    expiration_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
    if expiration_time > datetime.now():
      allowed_users.append(user_id)


def save_user_to_database(connection, user_id, expiration_time):
  cursor = connection.cursor()
  cursor.execute(
    '''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
  connection.commit()
###

def is_admin(user_id):
    try:
        with open("admins.txt", "r") as f:
            admin_ids = [int(x.strip()) for x in f if x.strip().isdigit()]
        return user_id in admin_ids
    except:
        return False

def admin_only(func):
    def wrapper(message):
        if not is_admin(message.from_user.id):
            return bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return func(message)
    return wrapper

###
####
start_time = time.time()

import subprocess
import threading
import re
import datetime

# Nếu có biến môi trường RELOAD_CHAT_ID thì gửi lại thông báo
reload_chat_id = os.environ.get("RELOAD_CHAT_ID")
reload_start_time = os.environ.get("RELOAD_TIME")

if reload_chat_id:
    try:
        # Tính thời gian reload nếu có
        if reload_start_time:
            diff = time.time() - float(reload_start_time)
            ms = int(diff * 1000)
            formatted_time = (
                f"{ms // 3600000:02}:{(ms % 3600000) // 60000:02}:"
                f"{(ms % 60000) // 1000:02}:{ms % 1000:03}"
            )
        else:
            formatted_time = "unknown"

        bot.send_message(
            reload_chat_id,
            f"<b>✅ Reload successfully!</b>\n<blockquote>⏱ Time reloading: <code>{formatted_time}</code>\n💖Chúc Bạn Trải Nghiệm Bot Vui Vẻ💖</blockquote>",
            parse_mode="HTML"
        )
    except Exception as e:
        print("❌ Failed to notify reload:", e)
def is_admin(user_id):
    try:
        with open("admins.txt", "r") as f:
            admin_ids = [int(x.strip()) for x in f if x.strip().isdigit()]
        return user_id in admin_ids
    except:
        return False

def admin_only(func):
    def wrapper(message):
        if not is_admin(message.from_user.id):
            return bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return func(message)
    return wrapper
     
def load_allowed_users():
    try:
        with open('admin_vip.txt', 'r') as file:
            allowed_users = [int(line.strip()) for line in file]
        return set(allowed_users)
    except FileNotFoundError:
        return set()

vip_users = load_allowed_users()

async def share_post(session, token, post_id, share_number):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'connection': 'keep-alive',
        'content-length': '0',
        'host': 'graph.facebook.com'
    }
    try:
        url = f'https://graph.facebook.com/me/feed'
        params = {
            'link': f'https://m.facebook.com/{post_id}',
            'published': '0',
            'access_token': token
        }
        async with session.post(url, headers=headers, params=params) as response:
            res = await response.json()
            print(f"Chia sẻ bài viết thành công: {res}")
    except Exception as e:
        print(f"Lỗi khi chia sẻ bài viết: {e}")

async def get_facebook_post_id(session, post_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        async with session.get(post_url, headers=headers) as response:
            response.raise_for_status()
            text = await response.text()

        soup = BeautifulSoup(text, 'html.parser')
        meta_tag = soup.find('meta', attrs={'property': 'og:url'})

        if meta_tag and 'content' in meta_tag.attrs:
            linkpost = meta_tag['content'].split('/')[-1]
            async with session.post('https://scaninfo.vn/api/fb/getID.php?url=', data={"link": linkpost}) as get_id_response:
                get_id_post = await get_id_response.json()
                if 'success' in get_id_post:
                    post_id = get_id_post["id"]
                return post_id
        else:
            raise Exception("Không tìm thấy ID bài viết trong các thẻ meta")

    except Exception as e:
        return f"Lỗi: {e}"

ACTIVE_GROUP_FILE = 'active_groups.txt'

def load_active_groups():
    try:
        with open(ACTIVE_GROUP_FILE, 'r') as f:
            return set(int(line.strip()) for line in f if line.strip().isdigit())
    except FileNotFoundError:
        return set()

def save_active_groups(groups):
    with open(ACTIVE_GROUP_FILE, 'w') as f:
        for gid in groups:
            f.write(f"{gid}\n")

# Load danh sách nhóm đã bật bot khi khởi động
active_groups = load_active_groups()
            
# Gửi thông báo khởi động lại đến nhóm nếu có biến môi trường truyền vào
restart_chat_id = os.environ.get("RESTART_CHAT_ID")

if restart_chat_id:
    try:
        time_now = datetime.now().strftime("%H:%M:%S")
        msg = f"<pre>✅ Bot successfully restarted!</pre>\n<blockquote>🕒 Time restarted: {time_now}</blockquote>"
        bot.send_message(int(restart_chat_id), msg, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Không gửi được thông báo restart đến nhóm: {e}")
# Danh sách nhóm đang bật bot
active_groups = load_active_groups()




ddos_log_buffer = []  # Chứa các dòng log mới nhất (tối đa 20 dòng)



import qrcode
import io
from telebot import types

import qrcode
import io
from telebot import types

import qrcode
import io
import json
import base64
from telebot import types

import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from PIL import Image
from io import BytesIO

@bot.message_handler(commands=['stk'])
def make_sticker(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    if not message.reply_to_message or not message.reply_to_message.photo:
        return bot.reply_to(message, "<code>📸 Reply Photo!</code>", parse_mode="HTML")

    try:
        # Lấy file ảnh gốc từ reply
        file_id = message.reply_to_message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Resize ảnh về 512x512 max, nền trong suốt
        img = Image.open(BytesIO(downloaded_file)).convert("RGBA")
        img.thumbnail((512, 512))

        bio = BytesIO()
        bio.name = 'sticker.png'
        img.save(bio, 'PNG')
        bio.seek(0)

        # Gửi lại sticker
        bot.send_sticker(message.chat.id, bio)
        bot.reply_to(message, f"<blockquote>✅ Success Sticker Photo</blockquote>", parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi tạo sticker: {e}")

import json, os, random
from telebot.types import ReplyKeyboardMarkup

users_file = "users.json"
login_file = "login.json"
code_file = "codes.json"
register_temp = {}
admin_id = [6854314324]  # Thay bằng Telegram ID admin

def load_json(file):
    if not os.path.exists(file): open(file, "w").write("{}")
    with open(file) as f: return json.load(f)

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f)

@bot.message_handler(commands=["taixiu"])
def taixiu_menu(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    text = (
        
        "<pre>"
        "╭────[🎮 MENU TAIXIU]─────╮\n"
        "│ /dangky\n"
        "│ /dangnhap\n"
        "│ /thongtin\n"
        "│ /tangxu\n"
        "│ /batdau\n"
        "│ /top10\n"
        "│ /showcode\n"
        "│ /code\n"
        "╰────────────────────╯\n"
        "👉 Gõ lệnh hoặc bấm để chơi 🎲"
        "</pre>"
        "<blockquote>"
        "<code>"
        "🖥️Menu Admin\n"
        " /regcode"
        "</code>"
        "</blockquote>"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=["dangky"])
def dangky(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    uid = message.from_user.id
    try:
        bot.send_message(uid, "<b>📌 Bắt đầu đăng ký tài khoản</b>\n\n<blockquote>Gửi lệnh: /tk [tên đăng nhập]</blockquote>", parse_mode="HTML")
        register_temp[uid] = {"step": "tk"}
        if message.chat.type != "private":
            bot.reply_to(message, "📩 Mình đã nhắn tin riêng, kiểm tra tin nhắn riêng để tiếp tục đăng ký!")
    except Exception as e:
        bot.reply_to(message, "⚠️ Vui lòng nhấn /start bot ở tin nhắn riêng trước khi đăng ký!")

@bot.message_handler(commands=["tk"])
def nhap_tk(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    uid = message.from_user.id
    if uid in register_temp and register_temp[uid]["step"] == "tk":
        ten = message.text.split(" ", 1)[-1]
        register_temp[uid]["tk"] = ten
        register_temp[uid]["step"] = "mk"
        bot.send_message(uid, "<b>🔒 Nhập mật khẩu:</b>\nGửi lệnh: <blockquote>/mk [mật khẩu]</blockquote>", parse_mode="HTML")

@bot.message_handler(commands=["mk"])
def nhap_mk(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    uid = message.from_user.id
    users = load_json(users_file)
    if uid in register_temp and register_temp[uid]["step"] == "mk":
        tk = register_temp[uid]["tk"]
        mk = message.text.split(" ", 1)[-1]
        if tk in users:
            bot.send_message(uid, "❌ Tài khoản đã tồn tại!")
        else:
            users[tk] = {"matkhau": mk, "xu": 1000, "win": 0, "lose": 0, "cuoc": 0, "uid": uid}
            save_json(users_file, users)
            bot.send_message(uid, f"✅ Đăng ký thành công với tài khoản <code>{tk}</code>!\nBạn có thể đăng nhập bằng lệnh:\n<blockquote>/dangnhap {tk} {mk}</blockquote>", parse_mode="HTML")
        del register_temp[uid]

@bot.message_handler(commands=["dangnhap"])
def dangnhap(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    try:
        _, tk, mk = message.text.split()
        users = load_json(users_file)
        uid = str(message.from_user.id)

        if tk in users and users[tk]["matkhau"] == mk:
            login = load_json(login_file)
            login[uid] = tk
            save_json(login_file, login)

            # Nhắn riêng thông báo đăng nhập
            bot.send_message(message.from_user.id,
                f"✅ <b>Đăng nhập thành công!</b>\n\n"
                f"<blockquote>👤 Username: <code>{tk}</code>\n💰 Số Dư: <code>{users[tk]['xu']} VND</code></blockquote>",
                parse_mode="HTML")

            # Nếu trong nhóm thì báo thành công
            if message.chat.type != "private":
                bot.reply_to(message, "📩 Đăng nhập thành công! Kiểm tra tin nhắn riêng để bắt đầu chơi 🎮")
        else:
            bot.send_message(message.from_user.id, "❌ Tài khoản hoặc mật khẩu sai!")
    except:
        try:
            bot.send_message(message.from_user.id, "❗ Dùng đúng cú pháp: <code>/dangnhap tk mk</code>", parse_mode="HTML")
        except:
            bot.reply_to(message, "⚠️ Vui lòng nhấn /start bot trong tin nhắn riêng trước khi đăng nhập!")

@bot.message_handler(commands=["thongtin"])
def thongtin(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    login = load_json(login_file)
    users = load_json(users_file)
    args = message.text.split()

    if len(args) == 1:
        # Xem chính mình
        uid = str(message.from_user.id)
        if uid not in login:
            bot.reply_to(message, "❌ Bạn chưa đăng nhập!")
            return
        username = login[uid]
    else:
        # Xem người khác
        username = args[1]
        if username not in users:
            bot.reply_to(message, f"❌ Không tìm thấy người dùng \"{username}\"!")
            return

    u = users[username]
    reply = (f"<b>🎭 Thông Tin</b>\n<blockquote>👤 Username: {username}\n💰 Số Dư: {u['xu']}\n💸 Đã Cược: {u['cuoc']}\n🎯Thắng: {u['win']}\n🪦 Thua: {u['lose']}</blockquote>"
    )
    bot.reply_to(message, reply, parse_mode="HTML")

@bot.message_handler(commands=["batdau"])
def batdau(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    uid = str(message.from_user.id)
    login = load_json(login_file)
    if uid not in login:
        return bot.reply_to(message, "❗ Vui lòng /dangnhap trước.")
    bot.send_message(message.chat.id, "<blockquote>💵 Nhập Số Tiền Cược</blockquote>", parse_mode="HTML")
    bot.register_next_step_handler(message, lambda m: nhan_tien(m, login[uid]))

def nhan_tien(message, tk):
    try:
        tien = int(message.text)
        users = load_json(users_file)
        if tien <= 0 or tien > users[tk]["xu"]:
            return bot.reply_to(message, "❌ Số Tiền Không Hợp Lệ!")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Tài", "Xỉu")
        bot.send_message(message.chat.id, "<blockquote>🎯 Chọn Tài hoặc Xỉu</blockquote>", reply_markup=markup, parse_mode="HTML")
        bot.register_next_step_handler(message, lambda m: ketqua(m, tk, tien))
    except:
        bot.reply_to(message, "❗ Xu phải là số!")

def ketqua(message, tk, tien):
    chon = message.text.lower()
    if chon not in ["tài", "xỉu"]:
        return bot.reply_to(message, "❌ Chỉ được chọn Tài hoặc Xỉu!")
    dice = [random.randint(1, 6) for _ in range(3)]
    tong = sum(dice)
    kq = "tài" if tong >= 11 else "xỉu"
    users = load_json(users_file)
    msg = f"🎲 Kết quả: {kq.upper()}\n"
    if chon == kq:
        users[tk]["xu"] += tien
        users[tk]["win"] += 1
        msg += f"<blockquote>🎉 Bạn thắng! +{tien}VND</blockquote>"
    else:
        users[tk]["xu"] -= tien
        users[tk]["lose"] += 1
        msg += f"<pre>😥 Bạn thua! -{tien}VND</pre>"
    users[tk]["cuoc"] += tien
    save_json(users_file, users)
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=["tangxu"])
def tangxu(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    login = load_json(login_file)
    users = load_json(users_file)
    uid = str(message.from_user.id)

    if uid not in login:
        return bot.reply_to(message, "❌ Bạn chưa đăng nhập!")

    try:
        _, tk_nhan, so_xu = message.text.split()
        tk_gui = login[uid]
        so_xu = int(so_xu)

        if tk_nhan not in users:
            return bot.reply_to(message, "❗ Người nhận không tồn tại!")

        if users[tk_gui]["xu"] < so_xu:
            return bot.reply_to(message, "❌ Bạn không đủ Tiền để tặng!")

        # Thực hiện chuyển xu
        users[tk_gui]["xu"] -= so_xu
        users[tk_nhan]["xu"] += so_xu
        save_json(users_file, users)

        # Gửi phản hồi đẹp
        bot.reply_to(message,
            f"<b>🎁 Tặng Tiền Thành Công</b>\n"
            f"<blockquote>"
            f"👤 Người Gửi: <code>{tk_gui}</code>\n"
            f"👤 Người Nhận: <code>{tk_nhan}</code>\n"
            f"💸 Số Tiền: <code>{so_xu} Vnd</code>"
            f"</blockquote>",
            parse_mode="HTML")

    except:
        bot.reply_to(message, "❗ Cú pháp đúng: <code>/tangxu ten_nguoi_nhan so_tien</code>", parse_mode="HTML")

@bot.message_handler(commands=["code"])
def code_nhap(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    login = load_json(login_file)
    codes = load_json(code_file)
    uid = str(message.from_user.id)
    if uid not in login:
        return bot.reply_to(message, "❌ Bạn chưa đăng nhập!")
    try:
        _, code = message.text.split()
        tk = login[uid]
        users = load_json(users_file)
        if code in codes:
            xu = codes.pop(code)
            users[tk]["xu"] += xu
            save_json(code_file, codes)
            save_json(users_file, users)
            bot.reply_to(message, f"<blockquote>🎁 Nhập Code Thành Công\n💰 Số Dư: +{xu} Vnd!\n✅ Chúc Mừng Bạn Đã Nhập Code Thành Công, Chúc Bạn Chơi Game Vui Vẻ Và May Mắn!</blockquote>", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ Code không hợp lệ hoặc đã dùng!")
    except:
        bot.reply_to(message, "❗ Dùng: /code <mã>")

@bot.message_handler(commands=["regcode"])
def regcode(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    if message.from_user.id not in admin_id:
        return
    try:
        _, code, xu = message.text.split()
        codes = load_json(code_file)
        if code in codes:
            return bot.reply_to(message, "⚠️ Code đã tồn tại!")
        codes[code] = int(xu)
        save_json(code_file, codes)
        bot.reply_to(message, f"<blockquote>✅ Tạo Code Thành Công\n🎁 Code: {code}\n💰 Giá Trị: {xu}Vnd\n💳 Bạn Là 1 Admin Tốt Bụng, Quản Bot Tốt Nhé</blockquote>", parse_mode="HTML")
    except:
        bot.reply_to(message, "❗ Dùng: /regcode <code> <xu>")


@bot.message_handler(commands=["showcode"])
def showcode(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    codes = load_json(code_file)
    if not codes:
        return bot.reply_to(message, "📭 Hiện Tại File Code Đang Rỗng")

    msg = "<blockquote>"
    for i, (c, x) in enumerate(codes.items(), 1):
        msg += f"{i}. <code>{c}</code>  {x}Vnd\n"
    msg += "</blockquote>"

    bot.reply_to(message, msg, parse_mode="HTML")

@bot.message_handler(commands=["top10"])
def top10(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    users = load_json(users_file)
    if not users:
        return bot.reply_to(message, "❌ Chưa có người chơi nào!")
    sorted_users = sorted(users.items(), key=lambda x: x[1].get("xu", 0), reverse=True)
    msg = "🏆 <b>Top 10 Con Nghiện</b>\n"
    for i, (tk, data) in enumerate(sorted_users[:10], 1):
        msg += f"<blockquote>{i}. {tk} {data['xu']} xu\n</blockquote>"
    bot.reply_to(message, msg, parse_mode="HTML")

@bot.message_handler(commands=['sharefile'])
@admin_only
def handle_sharefile(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    folder = "share"
    if not os.path.exists(folder):
        return bot.reply_to(message, "📂 Folder 'share/' does not exist.")

    files = os.listdir(folder)
    if not files:
        return bot.reply_to(message, "📁 No files found in 'share/'.")

    markup = InlineKeyboardMarkup(row_width=2)
    for filename in files:
        markup.add(InlineKeyboardButton(filename, callback_data=f"sendfile:{filename}"))

    bot.reply_to(message, "<pre>📦 Select a file to send:</pre>", reply_markup=markup, parse_mode="HTML")
    
@bot.callback_query_handler(func=lambda call: call.data.startswith("sendfile:"))
def handle_file_send(call):
    if not is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "🚫 You are not admin!")

    filename = call.data.split(":", 1)[1]
    filepath = os.path.join("share", filename)

    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption=f"<blockquote>📎 File: {filename}</blockquote>", parse_mode="HTML")
    else:
        bot.answer_callback_query(call.id, "❌ File not found!")
        
@bot.message_handler(commands=['checkhost'])
def check_host_command(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return 
    args = message.text.split()
    if len(args) != 2:
        return bot.reply_to(message, "📌 Usage: /checkhost <url>")

    url = args[1].strip()

    # CSRF token bạn sao chép sẵn từ link của bạn (có thể expire sau vài phút)
    csrf_token = "c5032c683fc4fde85ca915494ee27cc1b332325c"

    check_link = f"https://check-host.net/check-http?host={url}&csrf_token={csrf_token}"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔎 View Check Result", url=check_link))

    bot.send_message(
        message.chat.id,
        f"🌐 Host: <code>{url}</code>\n🧪 Click below to view check-host result:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

import requests


import json
import base64
import qrcode
import io

@bot.message_handler(commands=['loveqr'])
def create_love_qr(message):
    # Nếu trong nhóm thì kiểm tra đã kích hoạt chưa
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return

    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return bot.reply_to(message,
            "<blockquote>💘 Cách dùng:</blockquote>\n<pre>/loveqr Light Love Suu💖</pre>",
            parse_mode="HTML"
        )

    user_text = args[1].strip()

    # Tạo payload base64
    payload = {
        "t": [user_text],
        "a": "nnca"
    }
    b64_data = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    final_url = f"https://taoanhdep.com/love/?b={b64_data}"

    # Tạo QR
    qr = qrcode.make(final_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    # Gửi QR kèm caption (giữ nguyên text cũ + đóng khung)
    caption = (
        "<blockquote>"
        f"<code>💗 Success Reg Qrcode Love Text: {user_text}</code>\n\n"
        f"🌐 <a href='{final_url}'> {final_url}</a>"
        "</blockquote>"
    )

    bot.send_photo(message.chat.id, photo=buffer, caption=caption, parse_mode="HTML")
    
import os
import time

START_TIME_FILE = "start_time.txt"

def get_start_time():
    if os.path.exists(START_TIME_FILE):
        with open(START_TIME_FILE) as f:
            return float(f.read())
    else:
        now = time.time()
        with open(START_TIME_FILE, "w") as f:
            f.write(str(now))
        return now
 
@bot.message_handler(commands=['time'])
def uptime_handler(message):
    if message.chat.type in ['group', 'supergroup'] and message.chat.id not in active_groups:
        return

    uptime = int(time.time() - get_start_time())
    h = uptime // 3600
    m = (uptime % 3600) // 60
    s = uptime % 60

    video_url = "https://files.catbox.moe/c0i8pl.mp4"
    caption = f"<blockquote>⏱ Uptime: <code>{h:02}:{m:02}:{s:02}</code></blockquote>"

    try:
        bot.send_video(
            chat_id=message.chat.id,
            video=video_url,
            caption=caption,
            parse_mode="HTML"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Không gửi được video:\n<code>{e}</code>", parse_mode="HTML")
#tiktok
def fetch_tiktok_data(url):
    api_url = f'https://api.sumiproject.net/tiktok?video={url}'
    api_hi = f'https://api.ffcommunity.site/randomvideo.php'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching TikTok data: {e}")
        return None
def fetch_ff_info(uid):
    try:
        response = requests.get(f"https://sumiproject.net/api/ffcheck.php?uid={uid}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print("Lỗi khi gọi API FF:", e)
        return None


import os

# ====== Hàm xử lý file ======
def save_active_groups(group_ids, filename="active_groups.txt"):
    with open(filename, "w") as f:
        for gid in group_ids:
            f.write(str(gid) + "\n")

def load_active_groups(filename="active_groups.txt"):
    if not os.path.exists(filename):
        return set()
    with open(filename, "r") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())

# ====== Load khi khởi động bot ======
active_groups = load_active_groups()

# ====== Bật bot trong nhóm ======
@bot.message_handler(commands=['bot.on'])
def enable_bot_in_group(message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        group_name = message.chat.title or "Unnamed Group"

        if chat_id not in active_groups:
            active_groups.add(chat_id)
            save_active_groups(active_groups)
            bot.reply_to(message, f"<pre>✅ Bot has been enabled for group: {group_name}</pre>", parse_mode="HTML")
        else:
            bot.reply_to(message, "⚠️ Bot is already enabled in this group.")

# ====== Tắt bot trong nhóm ======
@bot.message_handler(commands=['bot.off'])
def disable_bot_in_group(message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        group_name = message.chat.title or "Unnamed Group"

        if chat_id in active_groups:
            active_groups.remove(chat_id)
            save_active_groups(active_groups)
            bot.reply_to(message, f"<pre>🚫 Bot has been disabled for group: {group_name}</pre>", parse_mode="HTML")
        else:
            bot.reply_to(message, "⚠️ Bot is already disabled in this group.")
from telebot import types

import telebot
import requests
from io import BytesIO

def get_info(uid, region="ID"):
    url = f"https://api.xlanznet.site/stalk/freefire?uid={uid}&region={region}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"[LỖI] Status code: {res.status_code} | Nội dung: {res.text}")
    except Exception as e:
        print(f"[LỖI] Exception khi gọi API: {e}")
    return None

@bot.message_handler(commands=['infoff'])
def handle_i4ff(message):
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "<blockquote>❌ VD: /infoff 12345678</blockquote>", parse_mode="HTML")

    uid = args[1]
    region = args[2] if len(args) > 2 else "ID"

    bot.reply_to(message, "<pre>🔍 Check Profile...</pre>", parse_mode="HTML")

    data = get_info(uid, region)
    if not data or "basicInfo" not in data:
        return bot.reply_to(message, "❌ Error")

    basic = data["basicInfo"]
    clan = data.get("clanBasicInfo", {})
    captain = data.get("captainBasicInfo", {})
    pet = data.get("petInfo", {})
    social = data.get("socialInfo", {})
    profile = data.get("profileInfo", {})

    # Gửi avatar (nếu có link headPic hoặc avatarId có thể sinh URL, tùy theo tài liệu)
    avatar_id = profile.get("avatarId")
    if avatar_id:
        avatar_url = f"https://media.freefireapi.com/avatar/{avatar_id}.png"
        try:
            img = requests.get(avatar_url, timeout=10).content
            photo = BytesIO(img); photo.name = 'avatar.png'
            bot.send_photo(message.chat.id, photo)
        except:
            pass

    # Soạn nội dung trả về
    text = f"""<pre>📄 Thông tin Free Fire:

👤 Nickname: {basic.get("nickname", "N/A")}
🆔 UID: {basic.get("accountId", uid)}
⭐ Cấp độ: {basic.get("level", "N/A")}
🏅 Rank: {basic.get("rank", "N/A")}
⚔️ Rank Tử Chiến: {basic.get("csRank", "N/A")}
🎯 Điểm BR: {basic.get("rankingPoints", "N/A")}
🎯 Điểm CS: {basic.get("csRankingPoints", "N/A")}
❤️ Lượt thích: {basic.get("liked", 0)}
📅 Tạo lúc: {basic.get("createAt", "Không rõ")}
🕒 Đăng nhập gần nhất: {basic.get("lastLoginAt", "N/A")}

🛡️ Quân đoàn: {clan.get("clanName", "Không có")}
🎖️ Cấp: {clan.get("clanLevel", "N/A")}
👥 Thành viên: {clan.get("memberNum", "N/A")}/{clan.get("capacity", "N/A")}
👑 Đội trưởng: {captain.get("nickname", "Không rõ")} (Lv {captain.get("level", "?" )})

🐾 Pet: ID {pet.get("id", "?" )}, Level {pet.get("level", "?" )}
🧠 Kỹ năng trang bị: {', '.join(map(str, profile.get('equipedSkills', [])))}

💬 Chữ ký: {social.get("signature", "Không có")}
🗣️ Ngôn ngữ: {social.get("language", "?" )}
🔍 Mode ưu thích: {social.get("modePrefer", "?" )}
</pre>
"""

    bot.send_message(message.chat.id, text, parse_mode="HTML")
    
import requests
from telebot import types

import requests
from telebot import types
import requests
from datetime import datetime

import requests
from datetime import datetime
import requests
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re

from googlesearch import search
import requests
import re
from bs4 import BeautifulSoup

from googlesearch import search
import requests
import re
from bs4 import BeautifulSoup

@bot.message_handler(commands=["search"])
def gg_search(message):
    try:
        query = re.split(r"\s+", message.text, 1)[1]
    except:
        return bot.reply_to(message, "❌ Cú pháp đúng: /search từ khóa cần tìm")

    bot.reply_to(message, "🔍 Đang tìm kiếm Google...", parse_mode="HTML")
    results = []

    try:
        for url in search(query, num_results=10):
            try:
                # Lấy tiêu đề trang
                r = requests.get(url, timeout=5)
                soup = BeautifulSoup(r.text, "html.parser")
                title = soup.title.string.strip() if soup.title else "Không có tiêu đề"
            except:
                title = "Không thể lấy tiêu đề"
            results.append((title, url))
    except Exception as e:
        return bot.reply_to(message, f"❌ Lỗi: {e}")

    if not results:
        return bot.reply_to(message, "❌ Không tìm thấy kết quả.")

    # Tạo message HTML với blockquote
    msg = f"<b>🔎 Kết quả cho:</b> <code>{query}</code>\n<blockquote>"
    for i, (title, link) in enumerate(results, 1):
        msg += f"{i}. {title}\n<a href='{link}'>{link}</a>\n\n"
    msg += "</blockquote>"

    bot.send_message(message.chat.id, msg, parse_mode="HTML", disable_web_page_preview=False)


from datetime import datetime
import requests

@bot.message_handler(commands=['tiktokdl'])
def tiktokdl_handler(message):
    try:
        if len(message.text.split()) < 2:
            return bot.reply_to(message, "❌ Sai cú pháp\nVí dụ: /tiktokdl <link video>")

        link = message.text.split(maxsplit=1)[1]
        bot.reply_to(message, "⏳ Đang tải video...", parse_mode="HTML")

        try:
            res = requests.get("https://tikwm.com/api/", params={"url": link}, timeout=30)
            data = res.json()
        except requests.exceptions.Timeout:
            return bot.reply_to(message, "⚠️ Kết nối máy chủ quá lâu. Thử lại sau.")
        except Exception:
            return bot.reply_to(message, "❌ Không thể kết nối API TikTok.")

        if not data.get("data") or not data["data"].get("play"):
            return bot.reply_to(message, "❌ Không thể lấy thông tin video!")

        d = data["data"]
        video_url = d["play"]
        author = d.get("author", {})

        try:
            video_data = requests.get(video_url, timeout=120).content
        except requests.exceptions.Timeout:
            return bot.reply_to(message, "⚠️ Tải video quá lâu. Có thể video nặng hoặc mạng yếu.")
        except Exception:
            return bot.reply_to(message, "❌ Lỗi khi tải video.")

        # Xử lý thông tin phụ
        created_time = datetime.fromtimestamp(d.get("create_time", 0)).strftime("%d/%m/%Y %H:%M")

        # Duration
        duration_sec = d.get("duration", 0)
        duration_str = f"{duration_sec//60}:{duration_sec%60:02}"

        # Dung lượng
        dung_luong = len(video_data) / (1024 * 1024)
        dung_luong_str = f"{dung_luong:.2f} MB"

        # Tên bài hát
        music_title = d.get("music_info", {}).get("title") or "Không có"

        # Quốc tịch không có trong API nên để mặc định
        country = author.get("region", "Không rõ")

        caption = (
            f"<b>🎬 TikTok Video</b>\n"
            f"<blockquote>"
            f"👤 Tác giả: <code>{author.get('nickname', 'N/A')}</code>\n"
            f"🆔 ID: <code>{author.get('unique_id', 'N/A')}</code>\n"
            f"🌐 Quốc tịch: {country}\n"
            f"🎵 Nhạc: {music_title}\n"
            f"📝 Mô tả: {d.get('title', 'Không có')}\n"
            f"⏱️ Thời lượng: {duration_str}\n"
            f"💾 Dung lượng: {dung_luong_str}\n"
            f"❤️ Tym: {d.get('digg_count', 0):,}\n"
            f"💬 Bình luận: {d.get('comment_count', 0):,}\n"
            f"🔁 Chia sẻ: {d.get('share_count', 0):,}\n"
            f"👁️ Lượt xem: {d.get('play_count', 0):,}\n"
            f"📅 Đăng ngày: {created_time}\n"
            f"</blockquote>"
        )

        bot.send_video(message.chat.id, video_data, caption=caption, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi không xác định:\n<code>{e}</code>", parse_mode="HTML")

import yt_dlp
import requests
from telebot.types import InputMediaPhoto

import yt_dlp

import requests
from telebot import TeleBot
import os

@bot.message_handler(commands=['sourcehtml'])
def view_source(message):
    try:
        args = message.text.split(" ", 1)
        if len(args) < 2:
            bot.reply_to(message, "❗ Vui lòng nhập URL. Ví dụ: /sourcehtml https://google.com")
            return
        
        url = args[1].strip()

        if not url.startswith("http"):
            url = "http://" + url

        response = requests.get(url, timeout=10)
        html = response.text

        file_path = f"/data/data/com.termux/files/usr/tmp/source.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        with open(file_path, "rb") as f:
            bot.send_document(message.chat.id, f, caption=f"📄 Mã nguồn của: {url}")

        os.remove(file_path)

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi lấy mã nguồn:\n{e}")
        
@bot.message_handler(commands=['ifvdytb'])
def youtube_info(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    if len(message.text.split()) < 2:
        return bot.reply_to(message, "📌 Dùng như sau:\n/ytb https://youtube.com/...")
    
    url = message.text.split(maxsplit=1)[1]
    msg = bot.reply_to(message, "⏳ Đang lấy thông tin video...\n<blockquote>😥 Bot Lấy Thông Tin Hơi Lâu Xin Bạn Đợi Trong Giây Lát ( Xin Lỗi Về Sự Bất Tiện Này )</blockquote>", parse_mode="HTML")

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Trích xuất thông tin
        title = info.get('title', 'Không rõ')
        views = info.get('view_count', 0)
        likes = info.get('like_count', 0)
        comments = info.get('comment_count', 0)
        upload_date = info.get('upload_date', 'Không rõ')
        upload_date = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[0:4]}" if upload_date != 'Không rõ' else 'Không rõ'
        channel = info.get('uploader', 'Không rõ')
        channel_url = info.get('uploader_url', '')
        subscribers = info.get('channel_follower_count', 'Không rõ')
        thumbnail = info.get('thumbnail')

        # Caption hiển thị đẹp
        caption = f"""<blockquote>
🎬 {title}
📺 Kênh: <a href="{channel_url}">{channel}</a>
👥 Người đăng ký: {subscribers:,}
👁️ Lượt xem: {views:,}
👍 Lượt thích: {likes:,}
💬 Bình luận: {comments:,}
📅 Ngày đăng: {upload_date}
🔗 <a href="{url}">Xem trên YouTube</a> </blockquote>
""".strip()

        bot.send_photo(
            chat_id=message.chat.id,
            photo=thumbnail,
            caption=caption,
            parse_mode="HTML"
        )

    except Exception as e:
        bot.edit_message_text(f"❌ Lỗi: {e}", chat_id=message.chat.id, message_id=msg.message_id)
        

#6854314324
#8160438179:AAE_3vzKR9KCRu8_h7BFZk5AN5hdjUqpUfs
#bot.send_message(message.chat.id, "✅ GPT đã bật.")
import g4f
from telebot import TeleBot
import telebot
import html

@bot.message_handler(commands=['gpt'])
def handle_gpt(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    try:
        prompt = message.text.split(" ", 1)[1]
    except:
        return bot.send_message(message.chat.id, "❗Dùng: /gpt &lt;nội dung hỏi&gt;", parse_mode='HTML')

    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        safe_response = html.escape(response)  # Escape HTML nguy hiểm
        bot.reply_to(message, f"<i>🤖 GPT Trả Lời:</i>\n<blockquote>{safe_response}</blockquote>", parse_mode='HTML')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Lỗi: {e}")
@bot.message_handler(commands=['start', 'command', 'main', 'help', 'menu'])
def send_welcome(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return  # Bot chưa bật trong nhóm này

    import random, psutil

    username = message.from_user.username or "user"

    # CPU Usage
    cpu_usage = round(random.uniform(10.0, 80.0), 2)
    if cpu_usage > 70:
        cpu_color = "🔴"
    elif cpu_usage > 40:
        cpu_color = "🟡"
    else:
        cpu_color = "🟢"
    cpu_text = f"{cpu_color} <b>{cpu_usage}%</b>"

    # RAM Usage thực tế
    ram = psutil.virtual_memory()
    ram_usage = round(ram.percent, 2)
    if ram_usage > 70:
        ram_color = "🔴"
    elif ram_usage > 40:
        ram_color = "🟡"
    else:
        ram_color = "🟢"
    ram_text = f"{ram_color} <b>{ram_usage}%</b>"

    # Nội dung chào
    xinchao = f"""<blockquote>🚀Welcome To Bot🚀</blockquote>
<pre>┌────── ⌬ Command ⌬ ──────>
│👋 Hello @{username}
│🎮 Total Menu: <b>18</b>
│🚀 Bot Update: <b>V1.1</b>
│💻 CPU: {cpu_text}
│📦 RAM: {ram_text}
│──────────────────────────
│» /menu : Command Menu
│» /admin : List Admin
│» /profileadmin : Profile admin
│» /infome : Info You
│» /infogroup : Infogroup
│» /time : Check Time
│» /voice : Text => Voice
│» /checkweb : Check Web
│» /qrtext : Qrcode Text
│» /loveqr : Qrcode Love
│» /infoff : Info Free Fire
│» /ifvdytb : Info Video Ytb
│» /checkhost : Check Host
│» /stk : Reg Sticker Photo
│» /tiktokdl : Info Video TikTok
│» /search : Search Google
│» /statusddos : Status DDoS
│» /menu2 : Command Menu 2
└──────────────────────────>
</pre>
<blockquote>      🎮Menu Games
» /taixiu
</blockquote>
<pre>     ⚡Command Admin⚡
🚀 Total Menu: 9

» /addadmin : Add List Admin
» /removeadmin : Remove ID Admin
» /bot.on : Online Bot Group
» /bot.off : Offline Bot Group
» /reload : Reloading Bot
» /ddos : Bot DDoS L7
» /sharefile : Share Tool
» /war : Bot War Tag
» /stopwar : Bot Stop War Tagg
</pre>
"""

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("👤 Admin", url="https://t.me/lightxgiang"),
        types.InlineKeyboardButton("🤖 Bot", url="https://t.me/lightxgiang"),
        types.InlineKeyboardButton("🌟 Group Zalo", url="https://zalo.me/g/ebzmch893")
    )

    video_url = "https://files.catbox.moe/c0i8pl.mp4"
    bot.send_video(message.chat.id, video_url, caption=xinchao, parse_mode='HTML', reply_markup=keyboard)

@bot.message_handler(commands=['start2', 'help2', 'command2', 'main2', 'menu2'])
def send_welcome(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return  # Bot chưa bật trong nhóm này

    import random, psutil

    username = message.from_user.username or "user"

    # CPU Usage
    cpu_usage = round(random.uniform(10.0, 80.0), 2)
    if cpu_usage > 70:
        cpu_color = "🔴"
    elif cpu_usage > 40:
        cpu_color = "🟡"
    else:
        cpu_color = "🟢"
    cpu_text = f"{cpu_color} <b>{cpu_usage}%</b>"

    # RAM Usage thực tế
    ram = psutil.virtual_memory()
    ram_usage = round(ram.percent, 2)
    if ram_usage > 70:
        ram_color = "🔴"
    elif ram_usage > 40:
        ram_color = "🟡"
    else:
        ram_color = "🟢"
    ram_text = f"{ram_color} <b>{ram_usage}%</b>"

    # Nội dung chào
    xinchao = f"""<i>🖥️Welcometo Command 2</i>
<pre>┌────── ⌬ Command Two ⌬ ──────>
│👋 Hello @{username}
│🎮 Total Menu: <b>6</b>
│🚀 Menu Number: 2
│💻 CPU: {cpu_text}
│📦 RAM: {ram_text}
│──────────────────────────
│» /dichtv : Text Vietnam => English
│» /dichta : Text English => Vietnam
│» /gpt : Ask Anything
│» /statusddos : Check Status DDoS
│» /server : Server Info
│» /img : Create AI image in English
│» /sourcehtml : Full Source Html
└──────────────────────────>
</pre>
"""

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("👤 Admin", url="https://t.me/lightxgiang"),
        types.InlineKeyboardButton("🤖 Bot", url="https://t.me/lightxgiang"),
        types.InlineKeyboardButton("🌟 Group Zalo", url="https://zalo.me/g/ebzmch893")
    )

    video_url = "https://files.catbox.moe/c0i8pl.mp4"
    bot.send_video(message.chat.id, video_url, caption=xinchao, parse_mode='HTML', reply_markup=keyboard)
    
import os
import yt_dlp
import requests
from telebot import types

@bot.message_handler(commands=['music'])
def search_music(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    try:
        query = message.text.split(" ", 1)[1]
    except IndexError:
        return bot.reply_to(message, "❗ Dùng: /music <tên bài nhạc>")

    msg = bot.reply_to(message, "🔎 Đang tìm và tải bài hát...")

    # Tạo thư mục nếu chưa có
    if not os.path.exists("downloads"):
        os.mkdir("downloads")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': 'downloads/song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '192',
        }],
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            video = info['entries'][0]

            title = video.get("title", "Unknown")
            channel = video.get("uploader", "Unknown")
            duration = video.get("duration", 0)
            views = video.get("view_count", 0)
            publish = video.get("upload_date", "")
            thumb_url = video.get("thumbnail")

            # Format thông tin
            duration_min = f"{duration//60}:{duration%60:02d}"
            views_fmt = f"{views:,}"
            publish_fmt = f"{publish[:4]}-{publish[4:6]}-{publish[6:]}" if publish else "Unknown"

            caption = f"""🎵 <b>{title}</b>
👤 Channel: {channel}
⏱ Duration: {duration_min}
👁 Views: {views_fmt}
📅 Published: {publish_fmt}
🔗 https://youtu.be/{video.get('id')}"""

            # Tải ảnh thumbnail
            thumb_path = "downloads/thumb.jpg"
            if thumb_url:
                with open(thumb_path, "wb") as img:
                    img.write(requests.get(thumb_url).content)

            # Gửi voice với ảnh
            with open("downloads/song.opus", "rb") as voice_file:
                bot.send_photo(
                    message.chat.id,
                    photo=open(thumb_path, 'rb') if os.path.exists(thumb_path) else None,
                    caption=caption,
                    parse_mode='HTML'
                )
                bot.send_voice(message.chat.id, voice=voice_file)

            bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, msg.message_id)
    finally:
        try:
            os.remove("downloads/song.opus")
            os.remove("downloads/thumb.jpg")
        except:
            pass

import os, requests
import yt_dlp
from pydub import AudioSegment
from telebot import types

YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"

def search_youtube(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&maxResults=1&type=video"
    res = requests.get(url)
    data = res.json()

    if "items" not in data or not data["items"]:
        return None, None

    video_id = data["items"][0]["id"]["videoId"]
    title = data["items"][0]["snippet"]["title"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_url, title


import requests

def react_to_message(chat_id, message_id, emoji="❤️"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
        "is_big": False  # để True nếu muốn icon lớn
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Không thể thả icon: {e}")
        
@bot.message_handler(commands=['profileadmin'])
def diggory(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
     
    username = message.from_user.username
    diggory_chat = f"""
<pre>
┌────── ⌬ Profile ⌬ ──────>
│
│👤 ADMIN: Light x Congz
│💻 Zalo: 0783920611
│🪡 Telegram: @lightxgiang
│🌐 Youtube: @LightToolLHG [off]
│🔎 TikTok: [off]
│⚔️ Nationality: VietNamese🇻🇳
└────────────────────────>
</pre>
    """
    bot.send_message(message.chat.id, diggory_chat, parse_mode='HTML')
    
    react_to_message(message.chat.id, message.message_id, "🔥")  # Thả reaction vào tin nhắn /start


last_usage = {}

from deep_translator import GoogleTranslator
from translatepy import Translator

@bot.message_handler(commands=['dichtv'])
def auto_translate(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    try:
        text = message.text.split(" ", 1)[1]
    except:
        return bot.reply_to(message, "❗Usage: /dich <text to translate>")

    try:
        translator = Translator()
        result = translator.translate(text, "English")  # auto detect nguồn
        src_lang = str(result.source_language).capitalize()
        tgt_lang = str(result.destination_language).capitalize()
        bot.reply_to(message, f"<i>🌐 Vietnamese ➤ English</i>\n<pre>{result.result}</pre>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")
from deep_translator import GoogleTranslator
import requests
import html

import requests
import html

def correct_english(text):
    # Sử dụng LanguageTool để sửa chính tả tiếng Anh
    url = "https://api.languagetool.org/v2/check"
    data = {
        "text": text,
        "language": "en-US"
    }
    res = requests.post(url, data=data).json()
    for match in res.get("matches", []):
        if match["replacements"]:
            offset = match["offset"]
            length = match["length"]
            replacement = match["replacements"][0]["value"]
            text = text[:offset] + replacement + text[offset + length:]
            break  # chỉ sửa lỗi đầu tiên để tránh lệch chỉ số
    return text

import subprocess

import os
import subprocess
import shutil
import socket

@bot.message_handler(commands=['server'])
def server_info(message):
    try:
        # Uptime
        uptime_output = subprocess.getoutput("uptime -p")
        uptime_str = uptime_output.replace("up ", "") if uptime_output else "N/A"

        # RAM
        meminfo = subprocess.getoutput("cat /proc/meminfo")
        total = int([line for line in meminfo.splitlines() if "MemTotal" in line][0].split()[1]) // 1024
        free = int([line for line in meminfo.splitlines() if "MemAvailable" in line][0].split()[1]) // 1024
        used = total - free

        # Disk
        total_disk, used_disk, _ = shutil.disk_usage("/")
        disk_total = round(total_disk / (1024 ** 3), 1)
        disk_used = round(used_disk / (1024 ** 3), 1)
        disk_percent = f"{disk_used / disk_total * 100:.1f}%"

        # CPU & Android info
        cpuinfo = subprocess.getoutput("getprop ro.hardware")
        cores = subprocess.getoutput("grep -c ^processor /proc/cpuinfo")
        model = subprocess.getoutput("getprop ro.product.model")
        brand = subprocess.getoutput("getprop ro.product.brand")
        android = subprocess.getoutput("getprop ro.build.version.release")
        arch = subprocess.getoutput("getprop ro.product.cpu.abi")

        # Battery
        battery_raw = subprocess.getoutput("dumpsys battery")
        level = "?" 
        charging = "?"
        for line in battery_raw.splitlines():
            if "level" in line:
                level = line.strip().split(":")[-1].strip()
            if "powered" in line:
                charging = line.strip().split(":")[-1].strip()
        charging = "🔌 Charging" if charging == "true" else "🔋 Not Charging"

        # IP
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "Unavailable"

        # App count
        app_count = len(subprocess.getoutput("pm list packages").splitlines())

        # Google account list
        google_accounts_raw = subprocess.getoutput("dumpsys account | grep '@gmail.com'")
        google_accounts = "\n".join(set(line.strip() for line in google_accounts_raw.splitlines())) or "None"

        # Bot size
        bot_path = os.path.abspath(__file__)
        size = round(os.path.getsize(bot_path) / (1024 * 1024), 2)

        # Final message
        msg = f"""<b>📟 SERVER INFO:</b>
<pre>Device : {brand} {model}
Android : {android}
RAM : {used}/{total} MB (Free: {free} MB)
Disk : {disk_used}/{disk_total} GB ({disk_percent})
CPU : {cpuinfo}
Cores : {cores}
Arch : {arch}
Uptime : 4 Years, 7 Month
Battery : {level}% - {charging}
Local IP : {ip}
Bot Size : {size} MB</pre>"""

        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Lỗi lấy server info:\n<code>{e}</code>", parse_mode="HTML")

import requests
from bs4 import BeautifulSoup
import os

import requests
import os

import tempfile
import yt_dlp
import os, tempfile, yt_dlp
from telebot import TeleBot, types

search_cache = {}

@bot.message_handler(commands=["nhac"])
def nhac_search(message):
    query = message.text.replace("/nhac", "").strip()
    if not query:
        return bot.reply_to(message, "❌ Vui lòng nhập tên bài hát. Ví dụ:\n/nhac Tự hào màu áo lính")

    msg = bot.reply_to(message, f"🔍 Đang tìm: <b>{query}</b>...", parse_mode="HTML")

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            search = ydl.extract_info(f"ytsearch10:{query}", download=False)
            results = search.get("entries", [])

            if not results:
                return bot.edit_message_text("❌ Không tìm thấy bài hát.", msg.chat.id, msg.message_id)

            text = "<b>🎵 Chọn bài hát:</b>\n\n"
            buttons = types.InlineKeyboardMarkup()
            search_cache[message.from_user.id] = results

            for i, entry in enumerate(results, 1):
                title = entry.get("title", "Không rõ")[:50]
                buttons.add(types.InlineKeyboardButton(f"{i}. {title}", callback_data=f"play_{i}_{message.from_user.id}"))
                text += f"{i}. {title}\n"

            bot.edit_message_text(text, msg.chat.id, msg.message_id, reply_markup=buttons, parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text(f"❌ Lỗi:\n<code>{e}</code>", msg.chat.id, msg.message_id, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("play_"))
def handle_play_selection(call):
    _, idx, uid = call.data.split("_")
    if int(uid) != call.from_user.id:
        return bot.answer_callback_query(call.id, "❌ Không phải lệnh của bạn.")

    index = int(idx) - 1
    results = search_cache.get(call.from_user.id)
    if not results or index >= len(results):
        return bot.answer_callback_query(call.id, "❌ Lỗi khi chọn bài.")

    info = results[index]
    url = info["webpage_url"]
    title = info.get("title", "Không rõ")
    thumbnail = info.get("thumbnail")

    msg = bot.edit_message_text(f"📥 Đang tải: <b>{title}</b>\n🔗 <a href='{url}'>YouTube</a>", call.message.chat.id, call.message.message_id, parse_mode="HTML", disable_web_page_preview=True)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(url, download=True)
                audio_file = ydl.prepare_filename(data)

            if thumbnail:
                bot.send_photo(call.message.chat.id, thumbnail, caption=f"🎵 <b>{title}</b>\n🔗 <a href='{url}'>YouTube</a>", parse_mode="HTML")

            with open(audio_file, "rb") as f:
                bot.send_audio(call.message.chat.id, f, title=title)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Không tải được nhạc: <code>{e}</code>", parse_mode="HTML")

  
import requests
from telebot import types

from huggingface_hub import InferenceClient
import requests

from telebot import TeleBot
from huggingface_hub import InferenceClient
from io import BytesIO
from PIL import Image
import traceback

client = InferenceClient(model="black-forest-labs/FLUX.1-dev", token="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")

@bot.message_handler(commands=['img'])
def generate_ai_image(message):
    try:
        prompt = message.text.replace('/img', '').strip()
        if not prompt:
            return bot.reply_to(message, "❌ Nhập mô tả để tạo ảnh.\nVí dụ: /img một ngôi làng trong tuyết")

        wait_msg = bot.reply_to(message, "🎨 Đang tạo ảnh AI...")

        # Tạo ảnh bằng HuggingFace
        image = client.text_to_image(prompt=prompt, guidance_scale=7)

        # Chuyển ảnh PIL.Image thành bytes
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)

        # Gửi ảnh
        bot.send_photo(message.chat.id, photo=image_io, caption=f"🖼️ <b>Prompt:</b> <code>{prompt}</code>", parse_mode="HTML")
        bot.delete_message(message.chat.id, wait_msg.message_id)

    except Exception as e:
        traceback.print_exc()
        bot.reply_to(message, f"❌ Lỗi tạo ảnh AI:\n<code>{e}</code>", parse_mode="HTML")


import html
from telebot.types import Message

# 🧠 Danh sách các kiểu Unicode (hỗ trợ in hoa nếu có)
unicode_styles = {
    "Bubble": {
        "a": "ⓐ", "b": "ⓑ", "c": "ⓒ", "d": "ⓓ", "e": "ⓔ", "f": "ⓕ", "g": "ⓖ", "h": "ⓗ", "i": "ⓘ",
        "j": "ⓙ", "k": "ⓚ", "l": "ⓛ", "m": "ⓜ", "n": "ⓝ", "o": "ⓞ", "p": "ⓟ", "q": "ⓠ", "r": "ⓡ",
        "s": "ⓢ", "t": "ⓣ", "u": "ⓤ", "v": "ⓥ", "w": "ⓦ", "x": "ⓧ", "y": "ⓨ", "z": "ⓩ",
        "A": "Ⓐ", "B": "Ⓑ", "C": "Ⓒ", "D": "Ⓓ", "E": "Ⓔ", "F": "Ⓕ", "G": "Ⓖ", "H": "Ⓗ",
        "I": "Ⓘ", "J": "Ⓙ", "K": "Ⓚ", "L": "Ⓛ", "M": "Ⓜ", "N": "Ⓝ", "O": "Ⓞ", "P": "Ⓟ",
        "Q": "Ⓠ", "R": "Ⓡ", "S": "Ⓢ", "T": "Ⓣ", "U": "Ⓤ", "V": "Ⓥ", "W": "Ⓦ", "X": "Ⓧ",
        "Y": "Ⓨ", "Z": "Ⓩ"
    },
    "Square": {
        "a": "🄰", "b": "🄱", "c": "🄲", "d": "🄳", "e": "🄴", "f": "🄵", "g": "🄶", "h": "🄷",
        "i": "🄸", "j": "🄹", "k": "🄺", "l": "🄻", "m": "🄼", "n": "🄽", "o": "🄾", "p": "🄿",
        "q": "🅀", "r": "🅁", "s": "🅂", "t": "🅃", "u": "🅄", "v": "🅅", "w": "🅆", "x": "🅇",
        "y": "🅈", "z": "🅉",
        "A": "🄰", "B": "🄱", "C": "🄲", "D": "🄳", "E": "🄴", "F": "🄵", "G": "🄶", "H": "🄷",
        "I": "🄸", "J": "🄹", "K": "🄺", "L": "🄻", "M": "🄼", "N": "🄽", "O": "🄾", "P": "🄿",
        "Q": "🅀", "R": "🅁", "S": "🅂", "T": "🅃", "U": "🅄", "V": "🅅", "W": "🅆", "X": "🅇",
        "Y": "🅈", "Z": "🅉"
    },
    "Tiny": {
        "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ᶦ",
        "j": "ʲ", "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "ᑫ", "r": "ʳ",
        "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ"
        # Không hỗ trợ in hoa
    },
    "Full Width": {
        "a": "ａ", "b": "ｂ", "c": "ｃ", "d": "ｄ", "e": "ｅ", "f": "ｆ", "g": "ｇ", "h": "ｈ", "i": "ｉ",
        "j": "ｊ", "k": "ｋ", "l": "ｌ", "m": "ｍ", "n": "ｎ", "o": "ｏ", "p": "ｐ", "q": "ｑ", "r": "ｒ",
        "s": "ｓ", "t": "ｔ", "u": "ｕ", "v": "ｖ", "w": "ｗ", "x": "ｘ", "y": "ｙ", "z": "ｚ",
        "A": "Ａ", "B": "Ｂ", "C": "Ｃ", "D": "Ｄ", "E": "Ｅ", "F": "Ｆ", "G": "Ｇ", "H": "Ｈ",
        "I": "Ｉ", "J": "Ｊ", "K": "Ｋ", "L": "Ｌ", "M": "Ｍ", "N": "Ｎ", "O": "Ｏ", "P": "Ｐ",
        "Q": "Ｑ", "R": "Ｒ", "S": "Ｓ", "T": "Ｔ", "U": "Ｕ", "V": "Ｖ", "W": "Ｗ", "X": "Ｘ",
        "Y": "Ｙ", "Z": "Ｚ"
    }
}

# 🔁 Hàm chuyển đổi ký tự
def stylize(text, style_dict):
    result = ""
    for c in text:
        result += style_dict.get(c, style_dict.get(c.lower(), c))
    return result

# 🧠 Lưu style của từng user Telegram
user_unicode_style = {}

# 🟢 Lệnh khởi động chọn kiểu chữ
@bot.message_handler(commands=["unicode"])
def unicode_command(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    demo_text = "demo"
    msg = "<b>✨ Chọn kiểu chữ Unicode bạn muốn (trả lời số):</b>\n\n"
    for i, (name, style_dict) in enumerate(unicode_styles.items(), 1):
        demo = stylize(demo_text, style_dict)
        msg += f"<pre>{i}. <code>{name}</code>: <b>{html.escape(demo)}</b>\n</pre>"
    bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_to_message_id=message.message_id)

# 🟡 Người dùng chọn số
@bot.message_handler(func=lambda m: m.reply_to_message and "Chọn kiểu chữ Unicode" in m.reply_to_message.text)
def handle_unicode_choice(message: Message):
    try:
        index = int(message.text.strip()) - 1
        if index < 0 or index >= len(unicode_styles):
            return bot.reply_to(message, "❌ Số không hợp lệ.")

        style_name = list(unicode_styles.keys())[index]
        user_unicode_style[message.from_user.id] = style_name
        bot.reply_to(message, f"✅ Đã chọn kiểu: <b>{style_name}</b>\n➡️ Bây giờ hãy <b>reply tin nhắn này</b> với nội dung bạn muốn chuyển đổi.", parse_mode="HTML")
    except:
        bot.reply_to(message, "❌ Vui lòng nhập số hợp lệ.")

# 🔵 Người dùng nhập nội dung cần chuyển
@bot.message_handler(func=lambda m: m.reply_to_message and m.from_user.id in user_unicode_style)
def handle_text_to_unicode(message: Message):
    style_name = user_unicode_style.get(message.from_user.id)
    style_dict = unicode_styles.get(style_name, {})
    styled = stylize(message.text, style_dict)
    bot.reply_to(message, f"<b>Kết quả:</b>\n<code>{html.escape(styled)}</code>", parse_mode="HTML")
@bot.message_handler(commands=['dichta'])
def translate_en_vi(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    try:
        text = message.text.split(" ", 1)[1]
    except:
        return bot.reply_to(message, "❗Usage: /dichta <text to translate>")

    try:
        corrected = correct_english(text)  # sửa chính tả trước khi dịch
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "vi",
            "dt": "t",
            "q": corrected
        }
        res = requests.get("https://translate.googleapis.com/translate_a/single", params=params)
        translated = res.json()[0][0][0]
        translated = html.unescape(translated)

        bot.reply_to(message, f"<i>🌐English ➤ Vietnamese</i>\n<pre>{translated}</pre>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")
from gtts import gTTS
import tempfile
import os

@bot.message_handler(commands=['voice'])
def text_to_voice(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return

    # Lấy nội dung văn bản sau lệnh /voice
    text = message.text[len('/voice '):].strip()

    if not text:
        bot.reply_to(message, "<blockquote>🎙️ Enter Command /voice + Text To Make Bot Work\nExample: /voice hello I am Giang</blockquote>", parse_mode='HTML')
        return

    temp_file_path = tempfile.mktemp(suffix='.mp3')

    try:
        tts = gTTS(text, lang='vi')
        tts.save(temp_file_path)

        with open(temp_file_path, 'rb') as audio_file:
            bot.send_voice(chat_id=message.chat.id, voice=audio_file)

    except Exception as e:
        bot.reply_to(message, f"❗Bot Error: {e}")

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

import qrcode

# Tệp lưu danh sách admin bot
ADMIN_FILE = 'bot_admins.txt'

def load_admins():
    try:
        with open(ADMIN_FILE, 'r') as f:
            return set(int(line.strip()) for line in f if line.strip().isdigit())
    except FileNotFoundError:
        return set()

def save_admins(admin_set):
    with open(ADMIN_FILE, 'w') as f:
        for uid in admin_set:
            f.write(f"{uid}\n")

def is_admin(user_id):
    return user_id in admins

# Load admin khi khởi động bot
admins = load_admins()

@bot.message_handler(commands=['addadmin'])
def add_admin_cmd(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "⛔ You Do Not Have Permission to Use This Command")

    if not message.reply_to_message:
        return bot.reply_to(message, "❤️ Reply Person Needs More Admin Rights")

    new_admin_id = message.reply_to_message.from_user.id
    if new_admin_id in admins:
        return bot.reply_to(message, "⚠️ It's Admin, What More?")

    admins.add(new_admin_id)
    save_admins(admins)
    bot.reply_to(message, f"<blockquote>✅ Success Add {new_admin_id} Go to Admin Bot List</blockquote>", parse_mode='HTML')
        
@bot.message_handler(commands=['removeadmin'])
def remove_admin_cmd(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return

    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "⛔ You do not have permission to use this command.")

    args = message.text.split()
    if len(args) != 2:
        return bot.reply_to(message, "❗ Usage: /removeadmin <user_id>")

    try:
        remove_id = int(args[1])
    except ValueError:
        return bot.reply_to(message, "❌ Invalid user ID!")

    if remove_id not in admins:
        return bot.reply_to(message, "❌ This user is not in the admin list.")

    admins.remove(remove_id)
    save_admins(admins)

    bot.reply_to(message, f"<blockquote>🗑️ Successfully removed <code>{remove_id}</code> from the admin list.</blockquote>", parse_mode='HTML')
    
@bot.message_handler(commands=['admin'])
def list_admins(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return

    if not admins:
        return bot.reply_to(message, "📭 No admins have been set.")

    list_text = "📋 <b>Bot Admin List</b>\n\n"
    for uid in admins:
        try:
            user = bot.get_chat(uid)
            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"
            if user.username:
                name += f" (@{user.username})"
        except:
            name = "Unknown Name"
        list_text += f"<blockquote>👤 {name}\n🆔 <code>{uid}</code></blockquote>\n"

    bot.reply_to(message, list_text, parse_mode="HTML")
    
@bot.message_handler(commands=['qrtext'])
def generate_qr(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    # Tách từ khóa nhập vào lệnh
    input_text = message.text.split(maxsplit=1)
    
    if len(input_text) > 1:
        input_text = input_text[1]  # Lấy phần từ khóa sau /qr
        # Tạo QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(input_text)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        bio = BytesIO()
        bio.name = 'qr.png'
        img.save(bio, 'PNG')
        bio.seek(0)

        # Gửi ảnh QR tới người dùng
        bot.send_photo(message.chat.id, photo=bio, caption=f"<blockquote>QR Text: {input_text}</blockquote>",parse_mode="HTML")
    else:
        bot.reply_to(message, "❗ Text to Create Qrcode")
        
        

  
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    for new_member in message.new_chat_members:
        # Lấy tên người dùng mới (username) hoặc tên hiển thị (first name)
        username = new_member.username
        first_name = new_member.first_name
        
        # Tạo thông điệp chào mừng
        if username:
            user_info = f"@{username}"
        else:
            user_info = first_name
        
        # Nội dung tin nhắn chào mừng với thẻ <pre>
        welcome_text = f'''
<blockquote>
🎉 Chào mừng {user_info} đến với nhóm! 🎉
Hy vọng bạn sẽ có khoảng thời gian vui vẻ ở đây!
Nhập /help để xem danh sách lệnh !!!
</blockquote>
        '''
        
        # Gửi tin nhắn chào mừng
        bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')
import requests
@bot.message_handler(commands=['checkweb'])
def check_hot_web(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    # Kiểm tra xem lệnh có đủ tham số không (URL của trang web cần kiểm tra)
    if len(message.text.split()) < 2:
        bot.reply_to(message, '<blockquote>Please provide the URL of the website to check (eg: /check https://example.com)</blockquote>',parse_mode='HTML')
        return
    
    # Lấy URL từ lệnh
    url = message.text.split()[1]

    try:
        # Gửi yêu cầu HTTP GET đến URL
        response = requests.get(url, timeout=10)
        
        # Kiểm tra trạng thái của trang web
        if response.status_code == 200:
            bot.reply_to(message, f"<blockquote>🔗 web {url} is working properly (Status: 200 OK).</blockquote>", parse_mode='HTML')
        else:
            bot.reply_to(message, f"<blockquote>⚠️ web {url} there's a problem (Status: {response.status_code}).</blockquote>", parse_mode='HTML')
    except requests.exceptions.RequestException as e:
        # Xử lý lỗi nếu không thể kết nối tới trang web
        bot.reply_to(message, f"<blockquote>❌ Unable to connect to website {url}. Error: {e}</blockquote>", parse_mode='HTML')
      


@bot.message_handler(func=lambda message: message.text.isdigit())
def copy_user_id(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    bot.send_message(message.chat.id, f"Your ID has been copied: `{message.text}`", parse_mode='Markdown')
ADMIN_NAME = "lightxgiang"
from telebot.apihelper import ApiTelegramException
import time
import os

import threading
import time
import os

active_wars = {}
war_stop_flags = {}

@bot.message_handler(commands=['war'])
def war_with_file_and_delay(message):
    if message.chat.type not in ['group', 'supergroup']:
        return bot.reply_to(message, "⛔ Group only.")
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "🚫 You are not authorized to use this command.")

    args = message.text.split()
    if len(args) < 4:
        return bot.reply_to(message,
            "📌 <b>Usage:</b>\n"
            "<code>/war @user1 @user2 1.5 roast.txt</code>\n\n"
            "📄 <b>Note:</b> File must exist in bot directory.",
            parse_mode="HTML")

    *user_tags, delay_str, filename = args[1:]

    try:
        delay = float(delay_str)
    except:
        return bot.reply_to(message, "⚠️ <code>Delay must be a number.</code>", parse_mode="HTML")

    tags = [u for u in user_tags if u.startswith("@")]
    if not tags:
        return bot.reply_to(message, "❗ <b>You must tag at least one user.</b>", parse_mode="HTML")

    if not os.path.isfile(filename):
        return bot.reply_to(message, f"❌ <b>File not found:</b> <code>{filename}</code>", parse_mode="HTML")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        return bot.reply_to(message, f"❌ Error reading file: {e}")

    tag_text = " ".join(tags)
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        f"<pre>🔥 WAR MODE ACTIVATED</pre>\n<blockquote>🎯 Target: {tag_text}\n📂 File: {filename}\n⏱ Delay: {delay}s\n🔥 Preparing war...</blockquote>",
        parse_mode="HTML"
    )

    # Dừng war cũ nếu có
    if chat_id in war_stop_flags:
        war_stop_flags[chat_id] = True
        time.sleep(1)

    war_stop_flags[chat_id] = False

    def run_war():
        for line in lines:
            if war_stop_flags.get(chat_id):
                bot.send_message(chat_id, "🛑 War stopped by admin.", parse_mode="HTML")
                return
            try:
                bot.send_message(
                    chat_id,
                    f"<pre>{line}</pre>\n<b>{tag_text}</b>",
                    parse_mode="HTML"
                )
                time.sleep(delay)
            except Exception as e:
                continue
        bot.send_message(chat_id, f"<b>✅ War complete!</b>\n🎯 Target: {tag_text}", parse_mode="HTML")
        war_stop_flags.pop(chat_id, None)

    thread = threading.Thread(target=run_war)
    thread.start()
    active_wars[chat_id] = thread


@bot.message_handler(commands=['stopwar'])
def stop_war_command(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    chat_id = message.chat.id
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "🚫 You are not authorized to use this command.")

    if war_stop_flags.get(chat_id):
        return bot.reply_to(message, "⚠️ No war is currently active in this group.")

    war_stop_flags[chat_id] = True
    bot.send_message(chat_id, "🛑 War stopping...", parse_mode="HTML")
@bot.message_handler(commands=['infome'])
def handle_check(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    
    # Hiển thị biểu tượng đợi
    waiting = bot.reply_to(message, "🔎")
    
    # Lấy thông tin người dùng
    user_photos = bot.get_user_profile_photos(user.id)
    chat_info = bot.get_chat(user.id)
    chat_member_status = bot.get_chat_member(message.chat.id, user.id).status
    
    bio = chat_info.bio or "Không có bio"
    user_first_name = user.first_name
    user_last_name = user.last_name or ""
    user_username = f"@{user.username}" if user.username else "No username"
    user_language = user.language_code or 'Error'
    
    # Định nghĩa trạng thái người dùng
    status_dict = {
        "creator": "Admin chính",
        "administrator": "Admin",
        "member": "Thành viên",
        "restricted": "Bị hạn chế",
        "left": "Rời nhóm",
        "kicked": "Bị đuổi khỏi nhóm"
    }
    status = status_dict.get(chat_member_status, "Không xác định")
    
    # Soạn tin nhắn gửi đi
    caption = (
        "<pre>┌────── ⌬ Profile ⌬ ──────>\n"
        f"│» 🆔 UID: {user.id}\n"
        f"│» 👤Name: {user_first_name} {user_last_name}\n"
        f"│» 👉Username: {user_username}\n"
        f"│» 🔰Language: {user_language}\n"
        f"│» 🏴Status: {status}\n"
        f"│» ✍️Bio: {bio}\n"
        f"│» 🤳Avatar: {'Success avatar' if user_photos.total_count > 0 else 'No Avatar'}\n"
        "└──────────────────────></pre>"
    )
    
    # Gửi ảnh hoặc tin nhắn văn bản
    if user_photos.total_count > 0:
        bot.send_photo(message.chat.id, user_photos.photos[0][-1].file_id, caption=caption, parse_mode='HTML', reply_to_message_id=message.message_id)
    else:
        bot.reply_to(message, caption, parse_mode='HTML')
    
    # Xóa tin nhắn chờ sau khi hoàn tất
    def xoatn(message, delay):
        try:
            bot.delete_message(message.chat.id, waiting.message_id)
        except Exception as e:
            print(f"Lỗi khi xóa tin nhắn: {e}")
    
    threading.Thread(target=xoatn, args=(message, 0)).start()

@bot.message_handler(commands=['groupinfo', 'infogroup', 'idgroup'])
def group_info(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id not in active_groups:
            return
    try:
        chat = bot.get_chat(message.chat.id)
        members_count = bot.get_chat_members_count(chat.id)

        # Lấy chủ nhóm (nếu bot là admin)
        owner = None
        try:
            admins = bot.get_chat_administrators(chat.id)
            for admin in admins:
                if admin.status == "creator":
                    owner = admin.user
                    break
        except:
            pass

        group_name = chat.title or "Không xác định"
        group_id = chat.id

        info = f"""
<i>📢 Thông tin nhóm</i>
<blockquote>
📛 Group Name: {group_name}
🆔 Group ID: {group_id}
👥 Member Number: {members_count}
👑 Group Owner: {owner.full_name if owner else 'Không lấy được'}
</blockquote>
"""
        bot.send_message(chat.id, info, parse_mode="HTML")
    
    except Exception as e:
        bot.reply_to(message, f"❌ Unable to get group information")
####################
import time

import sys, os, subprocess, time
import telebot

def restart_program(chat_id=None):
    python = sys.executable
    script = os.path.abspath(__file__)

    if chat_id:
        os.environ["RESTART_CHAT_ID"] = str(chat_id)

    try:
        subprocess.Popen([python, script], env=os.environ.copy())
    except Exception as e:
        print(f"❌ Khởi động lại thất bại: {e}")
    finally:
        time.sleep(1)
        sys.exit()

# Gửi tin nhắn xác nhận sau khi khởi động lại
if "RESTART_CHAT_ID" in os.environ:
    try:
        bot.send_message(
            int(os.environ["RESTART_CHAT_ID"]),
            "<b>✅ Bot has restarted successfully!</b>",
            parse_mode="HTML"
        )
        del os.environ["RESTART_CHAT_ID"]
    except Exception as e:
        print(f"Không thể gửi tin nhắn sau restart: {e}")

import os
import sys
import subprocess

import psutil

def kill_self():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['pid'] != current_pid and 'python' in proc.info['cmdline'] and 'bot.py' in ' '.join(proc.info['cmdline']):
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

@bot.message_handler(commands=['reload'])
def handle_reload(message):
    video_url = "https://files.catbox.moe/c0i8pl.mp4"
    
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ You don't have permission.")

    # Ghi lại chat_id và thời gian để sau khởi động xong gửi lại
    os.environ["RELOAD_CHAT_ID"] = str(message.chat.id)
    os.environ["RELOAD_TIME"] = str(time.time())

    # Gửi video kèm caption thông báo restart
    bot.send_video(
        chat_id=message.chat.id,
        video=video_url,
        caption="<i>♻️ Restarting bot...</i>",
        parse_mode="HTML"
    )

    # Tiến hành restart script
    python = sys.executable
    script = os.path.abspath(__file__)
    
    try:
        subprocess.Popen([python, script], env=os.environ.copy(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Restart failed: <code>{e}</code>", parse_mode="HTML")
    finally:
        os._exit(0)


if __name__ == "__main__":
    bot_active = True
import time

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=20)
    except Exception as e:
        print(f"⚠️ Bot crashed or disconnected: {e}")
        time.sleep(5)  # đợi 5s rồi thử lại