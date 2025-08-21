import aiohttp
import asyncio
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
admin_diggory = "taiki" # ví dụ : để user name admin là @diggory347 bỏ dấu @ đi là đc
name_bot = "Minh Vũ Music"
zalo = "0923932075"
tiktok = "https://tiktok.com/@_m.vu210_/"
facebook = "https://www.facebook.com/share/1BJtJjzca1/"
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
TOKEN = '7948484764:AAGN8ObPMvwfYKy0eq2EBZ39l6uf35NWNwA'  
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



###
####
start_time = time.time()

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


@bot.message_handler(commands=['time'])
def handle_time(message):
    uptime_seconds = int(time.time() - start_time)
    
    uptime_minutes, uptime_seconds = divmod(uptime_seconds, 60)
    bot.reply_to(message, f'Bot đã hoạt động được: {uptime_minutes} phút, {uptime_seconds} giây')
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

@bot.message_handler(commands=['tiktok'])
def tiktok_command(message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        url = command_parts[1].strip()
        data = fetch_tiktok_data(url)
        
        if data and 'code' in data and data['code'] == 0:
            video_title = data['data'].get('title', 'N/A')
            video_url = data['data'].get('play', 'N/A')
            music_title = data['data']['music_info'].get('title', 'N/A')
            music_url = data['data']['music_info'].get('play', 'N/A')
            
            reply_message = f"Tiêu đề Video: {video_title}\nĐường dẫn Video: {video_url}\n\nTiêu đề Nhạc: {music_title}\nĐường dẫn Nhạc: {music_url}"
            bot.reply_to(message, reply_message)
        else:
            bot.reply_to(message, "Không thể lấy dữ liệu từ TikTok.")
    else:
        bot.reply_to(message, "Hãy cung cấp một đường dẫn TikTok hợp lệ.")






    

@bot.message_handler(commands=['buff'])
def handle_buff(message):
    try:
        # Tách username từ tin nhắn
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Vui lòng nhập username. Ví dụ: /buff kvna.208")
            return
        
        username = args[1]

        # Gọi API có username
        api_url = f"https://anhcode.click/anhcode/api/fltt.php?key=anhcode&username={username}"
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()

        if data.get("success"):
            reply = (
                f"**{data['message']}**\n\n"
                f"• Username: `{data['username']}`\n"
                f"• Nickname: {data['nickname']}\n"
                f"• Follower trước: {data['followers_truoc']}\n"
                f"• Follower sau: {data['followers_sau']}\n"
                f"• Đã tăng: +{data['followers_tang']} followers"
            )
        else:
            reply = f"Lỗi: {data.get('message', 'Không rõ lỗi')}"

        bot.reply_to(message, reply, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"Lỗi khi gọi API: {str(e)}")




@bot.message_handler(commands=['videogai'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Video, Vui Lòng Chờ...")

    api_url = "https://api.ffcommunity.site/randomvideo.php"

    try:
        response = requests.get(api_url)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Video By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy video.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       
        
@bot.message_handler(commands=['videosex'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Video, Vui Lòng Chờ...")

    api_url = "https://api.sumiproject.net/video/videosex"

    try:
        response = requests.get(api_url)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Video By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy video.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       
@bot.message_handler(commands=['anhgai'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Ảnh, Vui Lòng Chờ...")

    api_url = "https://api.sumiproject.net/images/girl"

    try:
        response = requests.get(api_url)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Video By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy ảnh.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       
@bot.message_handler(commands=['anhtrai'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Ảnh, Vui Lòng Chờ...")

    api_urlr = "https://api.sumiproject.net/images/trai"

    try:
        response = requests.get(api_urlr)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Ảnh By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy ảnh.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       
@bot.message_handler(commands=['anhanime'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Ảnh, Vui Lòng Chờ...")

    api_url = "https://api.sumiproject.net/images/anime"

    try:
        response = requests.get(api_url)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Ảnh By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy ảnh.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       
@bot.message_handler(commands=['anhvu'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Ảnh, Vui Lòng Chờ...")

    api_url = "https://api.sumiproject.net/images/du"

    try:
        response = requests.get(api_url)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Ảnh By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy ảnh.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       
@bot.message_handler(commands=['anhlon'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Ảnh, Vui Lòng Chờ...")

    api_url = "https://api.sumiproject.net/images/lon"

    try:
        response = requests.get(api_url)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Ảnh By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy ảnh.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       
@bot.message_handler(commands=['anhcu'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Ảnh, Vui Lòng Chờ...")

    api_url = "https://api.sumiproject.net/images/cu"

    try:
        response = requests.get(api_url)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Ảnh By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy ảnh.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       
@bot.message_handler(commands=['anhnude'])
def send_video(message):
    wait_message = bot.reply_to(message, "Đang Tải Ảnh, Vui Lòng Chờ...")

    api_url = "https://api.sumiproject.net/images/nude"

    try:
        response = requests.get(api_url)
        video_data = response.json()
        video_url = video_data.get("url")

        if video_url:
            bot.delete_message(message.chat.id, wait_message.message_id)
            bot.send_video(message.chat.id, video_url, caption="<b>Random Ảnh By @anhcode</b>", reply_to_message_id=message.message_id, parse_mode="HTML")
        else:
            bot.reply_to(message, "Không tìm thấy ảnh.")

    except:
        bot.reply_to(message, "Có lỗi xảy ra, thử lại sau!")
       




@bot.message_handler(commands=['tool'])
def send_tool_links(message):
    markup = types.InlineKeyboardMarkup()
    
    tool_links = [
        ("https://link4m.com/B0YqtQ", "Tool Buff View"),
        ("https://link4m.com/otgWia", "Tool Buff Fl Tiktok"),
        ("https://link4m.com/0qck0B65", "Tool Bot Zalo")
    ]
    
    for link, desc in tool_links:
        markup.add(types.InlineKeyboardButton(text=desc, url=link))
    
    bot.reply_to(message, "Chọn một tool từ bên dưới(2 cũng đc):", reply_markup=markup)
####
#####
video_url = 'https://v16m-default.akamaized.net/b7650db4ac7f717b7be6bd6a04777a0d/66a418a5/video/tos/useast2a/tos-useast2a-ve-0068-euttp/o4QTIgGIrNbkAPGKKLKteXyLedLE7IEgeSzeE2/?a=0&bti=OTg7QGo5QHM6OjZALTAzYCMvcCMxNDNg&ch=0&cr=0&dr=0&lr=all&cd=0%7C0%7C0%7C0&cv=1&br=2576&bt=1288&cs=0&ds=6&ft=XE5bCqT0majPD12cy-773wUOx5EcMeF~O5&mime_type=video_mp4&qs=0&rc=Mzk1OzY7PGdpZjxkOTQ3M0Bpajh1O2w5cmlzbzMzZjgzM0AuNWJgLi02NjMxLzBgXjUyYSNzNmptMmRjazFgLS1kL2Nzcw%3D%3D&vvpl=1&l=202407261543513F37EAD38E23B6263167&btag=e00088000'
@bot.message_handler(commands=['add', 'adduser'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'BẠN KHÔNG CÓ QUYỀN SỬ DỤNG LỆNH NÀY')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'VUI LÒNG NHẬP ID NGƯỜI DÙNG')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.now() + timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    # Gửi video với tiêu đề
    caption_text = (f'NGƯỜI DÙNG CÓ ID {user_id}                                ĐÃ ĐƯỢC THÊM VÀO DANH SÁCH ĐƯỢC PHÉP SỬ DỤNG LỆNH /spamvip')
    bot.send_video(
        message.chat.id,
        video_url,
        caption=caption_text
    )

load_users_from_database()

def is_key_approved(chat_id, key):
    if chat_id in users_keys:
        user_key, timestamp = users_keys[chat_id]
        if user_key == key:
            current_time = datetime.datetime.now()
            if current_time - timestamp <= datetime.timedelta(hours=2):
                return True
            else:
                del users_keys[chat_id]
    return False

def fetch_data(user_id):
    try:
        url = f'https://ff-community-api.vercel.app/ff.Info?uid={user_id}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
@bot.message_handler(commands=['ff'])
def handle_command(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "<blockquote>Sử dụng: /ff ID\nVí dụ: /ff 1910606206</blockquote>", parse_mode="HTML")
        return
    
    command, user_id = parts
    if not user_id.isdigit():
        bot.reply_to(message, "<blockquote>ID không hợp lệ. Vui lòng nhập ID số.</blockquote>", parse_mode="HTML")
        return

    try:
        data = fetch_data(user_id)
        if data is None:
            bot.reply_to(message, "<blockquote>❌ Server API đang bảo trì hoặc quá tải. Vui lòng thử lại sau.</blockquote>", parse_mode="HTML")
            return
            
        basic_info = data
        clan_info = data.get('Guild Information', {})
        leader_info = data.get('Guild Leader Information', {})
        avatar_url = basic_info.get('Account Avatar Image', 'Không có')

        def get_value(key, data_dict):
            return data_dict.get(key, "Không có thông tin")

        info_text = f"""
<blockquote>
<b>Thông tin cơ bản:</b>
Avatar: <a href="{avatar_url}">Nhấn để xem</a>
Nickname: {get_value('AccountName',basic_info)}
Cấp độ: {get_value('AccountLevel', basic_info)}
Khu vực: {get_value('AccountRegion', basic_info)}
Xếp hạng Sinh Tồn: {get_value('BrRank', basic_info)}
Tổng Sao Tử Chiến: {get_value('CsRank', basic_info)}
Số lượt thích: {get_value('AccountLikes', basic_info)}
Lần đăng nhập gần nhất: {get_value('AccountLastLogin (GMT 0530)', basic_info)}
Ngôn ngữ: {get_value('AccountLanguage', basic_info)}
Tiểu sử game: {get_value('AccountSignature', basic_info)}

<b>Thông tin quân đoàn:</b>
Tên quân đoàn: {get_value('GuildName', clan_info)}
Cấp độ quân đoàn: {get_value('GuildLevel', clan_info)}
Sức chứa: {get_value('GuildCapacity', clan_info)}
Số thành viên hiện tại: {get_value('GuildMember', clan_info)}
Chủ quân đoàn: {get_value('LeaderName', leader_info)}
Cấp độ chủ quân đoàn: {get_value('LeaderLevel', leader_info)}

<b>Thông tin balabla:</b>
Kỹ năng nhân vật : {get_value('EquippedSkills', basic_info)}
Name Pet : {get_value('PetName', basic_info)}
Lever Pet : {get_value('PetLevel', basic_info)}
                
</blockquote>
"""

        bot.reply_to(message, info_text, parse_mode='HTML')

    except Exception as e:
        bot.reply_to(message, "<blockquote>Đã xảy ra lỗi</blockquote>", parse_mode="HTML")
        









@bot.message_handler(commands=['share'])
def share(message):
    global bot_active, global_lock, admin_mode
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = datetime.now()


    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return

    if chat_id != ALLOWED_GROUP_ID:
        msg = bot.reply_to(message, 'Làm Trò Gì Khó Coi Vậy')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'Chế độ admin hiện đang bật, đợi tí đi.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    try:
        global_lock.acquire()  
        
        args = message.text.split()
        if user_id not in allowed_users and user_id not in freeuser:
            bot.reply_to(message, 'bot chỉ hoạt động khi bạn mua key và get key bằng lệnh /laykey')
            return
        if len(args) != 3:
            msg = bot.reply_to(message, '''
╔══════════════════
║<|> /laykey trước khi sài hoặc mua
║<|> /key <key> để nhập key 
║<|> ví dụ /key ABCDXYZ
║<|> /share {link_buff} {số lần chia sẻ}
╚══════════════════''')
            time.sleep(10)
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Error deleting message: {e}")
            return

        post_id, total_shares = args[1], int(args[2])

        # Kiểm tra người dùng VIP hoặc Free
        if user_id in allowed_users:
            handle_vip_user(message, user_id, post_id, total_shares, current_time)
        elif user_id in freeuser:
            handle_free_user(message, user_id, post_id, total_shares, current_time)
            
    except Exception as e:
        msg = bot.reply_to(message, f'Lỗi: {e}')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")

    finally:
        if global_lock.locked():
            global_lock.release()  

def handle_vip_user(message, user_id, post_id, total_shares, current_time):
    if user_id in user_cooldowns:
        last_share_time = user_cooldowns[user_id]
        if current_time < last_share_time + timedelta(seconds=viptime):
            remaining_time = (last_share_time + timedelta(seconds=viptime) - current_time).seconds
            msg = bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.\nvip Delay')
            time.sleep(10)
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            return
    if total_shares > VIP_GIỚI_HẠN_CHIA_SẺ:
        msg = bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {VIP_GIỚI_HẠN_CHIA_SẺ} lần.')
        time.sleep(10)
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
     #phân file token khác nhau
    file_path = 'token.txt'
    with open(file_path, 'r') as file:
        tokens = file.read().split('\n')

    total_live = len(tokens)

    sent_msg = bot.reply_to(message,
        f'Bot Chia Sẻ Bài Viết\n\n'
        f'║Số Lần Chia Sẻ: {total_shares}\n'
        f'║Free Max 400 Share\n'
        f'║{message.from_user.username} Đang Dùng Vip',
        parse_mode='HTML'
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#check live token
    if total_live == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Không có token nào hoạt động.')
        return

    share_log.append({
        'username': message.from_user.username,
        'user_id': user_id,
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'post_id': post_id,
        'total_shares': total_shares
    })

    async def share_with_delay(session, token, post_id, count):
        await share_post(session, token, post_id, count)
        await asyncio.sleep(1)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                tasks.append(share_with_delay(session, token, post_id, share_number))
            await asyncio.gather(*tasks)

    asyncio.run(main())

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Đơn của bạn đã hoàn thành')

def handle_free_user(message, user_id, post_id, total_shares, current_time):
    if user_id in user_cooldowns:
        last_share_time = user_cooldowns[user_id]
        if current_time < last_share_time + THỜI_GIAN_CHỜ:
            remaining_time = (last_share_time + THỜI_GIAN_CHỜ - current_time).seconds
            msg = bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.')
            time.sleep(10)
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            return

    if total_shares > FREE_GIỚI_HẠN_CHIA_SẺ:
        msg = bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {FREE_GIỚI_HẠN_CHIA_SẺ} lần.')
        time.sleep(10)
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
    #token free
    file_path = 'token.txt'
    with open(file_path, 'r') as file:
        tokens = file.read().split('\n')

    total_live = len(tokens)

    sent_msg = bot.reply_to(message,
        f'Bot Chia Sẻ Bài Viết\n\n'
        f'║Số lần share: {total_shares}\n'
        f'║Vip Max 1000 Share\n'
        f'║{message.from_user.username} Đang Share Free',
        parse_mode='HTML'
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if total_live == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Không có token nào hoạt động.')
        return

    share_log.append({
        'username': message.from_user.username,
        'user_id': user_id,
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'post_id': post_id,
        'total_shares': total_shares
    })

    async def share_with_delay(session, token, post_id, count):
        await share_post(session, token, post_id, count)
        await asyncio.sleep(1)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                tasks.append(share_with_delay(session, token, post_id, share_number))
            await asyncio.gather(*tasks)

    asyncio.run(main())

    user_cooldowns[user_id] = current_time

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Đơn của bạn đã hoàn thành')
@bot.message_handler(commands=['vip'])
def handle_vip(message):
    chat_id = message.chat.id
    if message.from_user.id not in vip_users:
        bot.reply_to(message, "Bạn không phải là thành viên VIP.")
        return

   
@bot.message_handler(commands=['infofb'])
def get_facebook_info(message):
    try:
        # Tách uid từ lệnh
        uid = message.text.split()[1]
        # URL API
        url = f"https://api.lhpcloud.com/uid.php?id={uid}"
        # Gửi yêu cầu GET tới API
        response = requests.get(url)
        # Kiểm tra xem yêu cầu có thành công không
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                fb_data = data.get('data', {})
                # Tạo tin nhắn trả về
                reply_message = (
                    "```INFO-FACEBOOK\n ╭───────〈 INFO  〉──────⭓\n"
                    f" │ ➢ 𝙸𝙳:〘{fb_data.get('id')}〙\n"
                    f" │ ➢ 𝙽𝙰𝙼𝙴: {fb_data.get('name')}\n"
                    f" │ ➢ 𝚄𝚂𝙴𝚁??𝙰𝙼𝙴:  {fb_data.get('username')}\n"
                    f" │ ➢ 𝚅𝙴𝚁𝙸𝙵𝙴𝙳: {'Yes' if fb_data.get('is_verified') else 'No'}\n"
                    f" │ ➢ 𝙲𝚁𝙴𝙰𝚃𝙴𝙳 𝚃𝙸𝙼𝙴: {fb_data.get('created_time')}\n"
                    f" │ ➢ ꭲꮖꮇꭼꮓꮎꮑꭼ: {fb_data.get('timezone')}\n"
                    f" │ ➢ 𝙻𝙾𝙲𝙰𝙻𝙴: {fb_data.get('locale')}\n"
                    f" │ ➢ 𝙶𝙴𝙽𝙳𝙴𝚁: {fb_data.get('gender')}\n"
                    f" │ ➢ ꮤꭼᏼꮪꮖꭲꭼ : {fb_data.get('website')}\n"
                    f" │ ➢ 𝙻𝙸𝚁𝙺: {fb_data.get('link')}\n"
                    f" │ ➢ 𝙵𝙾𝙻𝙻𝙾𝚆𝚂: {fb_data.get('subscribers', {}).get('summary', {}).get('total_count')}\n"
                    f" │ ➢ 𝙷𝙾𝙼𝙴𝚃𝙾𝚆𝙽: {fb_data.get('hometown', {}).get('name')}\n"
                    f" │ ➢ ????𝙲𝙰𝚃𝙸𝙾𝙽: {fb_data.get('location', {}).get('name')}\n ╰─────────────۰۪۪۫۫●۪۫۰"
                    "```"
                )
            else:
                reply_message = "Không tìm thấy thông tin hoặc UID không hợp lệ."
        else:
            reply_message = "Lỗi khi truy cập API."

        bot.reply_to(message, reply_message, parse_mode='Markdown')
    except IndexError:
        bot.reply_to(message, "Vui lòng cung cấp UID hợp lệ. Ví dụ: /infofb 100030236827904", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Đã có lỗi xảy ra: {str(e)}", parse_mode='Markdown')
        

@bot.message_handler(commands=['ls'])
def sharelog(message):
    if message.from_user.id in admins:
        if not share_log:
            bot.reply_to(message, 'chưa ai sử dụng hết')
            return
        
        log_text = "Danh sách người đã sử dụng lệnh share:\n"
        for log in share_log:
            log_text += f"<blockquote>Lịch_Sử\n- User: {log['username']} (ID: {log['user_id']})\n- vào lúc {log['time']}\n- Post LINK: <a href='{log['post_id']}'>link</a>\n- Số lần chia sẻ: {log['total_shares']}\n</blockquote>"
        
        bot.reply_to(message, log_text, parse_mode='HTML')
    else:
        bot.reply_to(message, 'admin mới xem đc á m')
@bot.message_handler(commands=['admod'])
def handle_on(message):
    global admin_mode
    if message.from_user.id in admins:
        admin_mode = True
        bot.reply_to(message, "Chế độ admin đã bật.")
    else:
        bot.reply_to(message, "Bạn không có quyền bật chế độ admin.")

@bot.message_handler(commands=['laykey'])
def laykey(message):
    bot.reply_to(message, text='VUI LÒNG ĐỢI TRONG GIÂY LÁT!')

    with open('key.txt', 'a') as f:
        f.close()

    user_id = message.from_user.id  
    string = f'GL-{user_id}+{TimeStamp()}'  
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())[:10]
    print(key)
    
    url_key = requests.get(f'https://link4m.co/api-shorten/v2?api=674701e4b29cad72ca685685&url=https://link.anhcode.click/keytool.php?key={key}').json()['shortenedUrl']
    
    text = f'''
- KEY CỦA BẠN {get_time_vietnam()}
- DÙNG LỆNH /key {{key}} ĐỂ TIẾP TỤC -
 [Lưu ý: mỗi key chỉ có 1 người dùng]
    '''

    keyboard = InlineKeyboardMarkup()
    url_button = InlineKeyboardButton(text="Get Key", url=url_key)
    admin_button = InlineKeyboardButton(text="WED TẢI ALL TOOL", url="https://anhcode.click/")
    keyboard.add(url_button, admin_button)
    
    bot.reply_to(message, text, reply_markup=keyboard)
    
    admin_message = f"Key Của {user_id}: {key}\n bạn có thể đưa key này cho id người nhận"
    bot.send_message(ADMIN_ID, admin_message)

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'CHƯA NHẬP KEY MÀ')
        return

    user_id = message.from_user.id
    
    key = message.text.split()[1]
    string = f'GL-{user_id}+{TimeStamp()}'  
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())[:10]
    if key == expected_key:
        freeuser.append(user_id)
        bot.reply_to(message, 'KEY ĐÚNG BẠN CÓ THỂ TIẾP TỤC SỬ DỤNG LỆNH')
    else:
        bot.reply_to(message, 'KEY SAI R GET LẠI THỬ XEM HOẶC IB CHO ADMIN')


@bot.message_handler(commands=['unadmod'])
def handle_off(message):
    global admin_mode
    if message.from_user.id in admins:
        admin_mode = False
        bot.reply_to(message, "Chế độ admin đã tắt.")
    else:
        bot.reply_to(message, "Bạn không có quyền tắt chế độ admin.")
@bot.message_handler(commands=['off'])
def bot_off(message):
    global bot_active
    if message.from_user.id in admins:
        bot_active = False
        bot.reply_to(message, 'Bot đã được tắt.')
    else:
        bot.reply_to(message, 'Bạn không có quyền thực hiện thao tác này.')
@bot.message_handler(commands=['on'])
def bot_on(message):
    global bot_active
    if message.from_user.id in admins:
        bot_active = True
        bot.reply_to(message, 'Bot đã được bật.')
    else:
        bot.reply_to(message, 'Bạn không có quyền thực hiện thao tác này.')
@bot.message_handler(commands=['code'])
def handle_code_command(message):
    # Tách lệnh và URL từ tin nhắn
    command_args = message.text.split(maxsplit=1)

    # Kiểm tra xem URL có được cung cấp không
    if len(command_args) < 2:
        bot.reply_to(message, "Vui lòng cung cấp url sau lệnh /code. Ví dụ: /code https://xnxx.com")
        return

    url = command_args[1]
    domain = urlparse(url).netloc
    file_name = f"{domain}.txt"
    
    try:
        # Lấy nội dung HTML từ URL
        response = requests.get(url)
        response.raise_for_status()  # Xảy ra lỗi nếu có lỗi HTTP

        # Lưu nội dung HTML vào file
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response.text)

        # Gửi file về người dùng
        with open(file_name, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=f"HTML của trang web {url}")

        # Phản hồi tin nhắn gốc
        bot.reply_to(message, "Đã gửi mã nguồn HTML của trang web cho bạn.")

    except requests.RequestException as e:
        bot.reply_to(message, f"Đã xảy ra lỗi khi tải trang web: {e}")

    finally:
        # Đảm bảo xóa file sau khi gửi
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception as e:
                bot.reply_to(message, f"Đã xảy ra lỗi khi xóa file: {e}")
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
   
   
    username = message.from_user.username
    bot.reply_to(message, f'''
┌───⭓ {name_bot}
│» Xin chào @{username}
│» /help : Lệnh trợ giúp
│» /admin : Thông tin admin
│» /spam : Spam SMS FREE
│» /spamvip : Spam SMS VIP - Mua Vip 30k/Tháng
│» /share : Free 400 - Vip 1k share trên lần
│» /id : Lấy ID Tele Của Bản Thân
│» /videosex : Video 🔞
│» /anhlon : Ảnh Lonnn 🔞
│» /anhvu : Ảnh Vuuuu 🔞
│» /anhanime : Ảnh anime 
│» /anhnude : Ảnh nude 
│» /anhtrai : Ảnh Trai 
│» /anhgai : Ảnh Gái
│» /tiktok : Check Thông Tin - Tải Video Tiktok.
│» /videogai : Random Video Gái
│» /time : check thời gian hoạt động
│» /voice : Chuyển văn bản thành giọng nói
│» /check : check web hoạt động không
│» /checkip : check thông tin ip
│» /qr : Tạo qr với nội dung văn bản
│» /ff : Check id free fire
│» /ad : có bao nhiêu admin
│» /fltt :Follow tiktok
│» /code : Lấy Code html của web
│» /tv : Đổi Ngôn Ngữ Sang Tiếng Việt
│» /infofb : Check thông tin facebook
│» /napvip : Nạp mua vip 30/1 tháng
│» Lệnh Cho ADMIN
│» /rs : Khởi Động Lại
│» /add : Thêm người dùng sử dụng /spamvip
└───────────⧕
    ''')
@bot.message_handler(commands=['admin'])
def diggory(message):
     
    username = message.from_user.username
    diggory_chat = f'''
┌───⭓ {name_bot}
│» Xin chào @{username}
│» Bot Spam : Minh Vũ Music🇻🇳
│» Zalo: {zalo}
│» tiktok: {tiktok}
│» facebook: {facebook}
│» Telegram: @{admin_diggory}
└──────────────
    '''
    bot.send_message(message.chat.id, diggory_chat)


last_usage = {}

@bot.message_handler(commands=['spam'])
def spam(message):
    user_id = message.from_user.id
    current_time = time.time()
    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'có lẽ admin đang fix gì đó hãy đợi xíu')
    if user_id in last_usage and current_time - last_usage[user_id] < 100:
        bot.reply_to(message, f"Vui lòng đợi {100 - (current_time - last_usage[user_id]):.1f} giây trước khi sử dụng lệnh lại.")
        return

    last_usage[user_id] = current_time

    # Phân tích cú pháp lệnh
    params = message.text.split()[1:]
    if len(params) != 2:
        bot.reply_to(message, "/spam sdt số_lần như này cơ mà - vì lý do server treo bot hơi cùi nên đợi 100giây nữa dùng lại nhé")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "Số lần spam không hợp lệ. Vui lòng chỉ nhập số.")
        return

    count = int(count)

    if count > 5:
        bot.reply_to(message, "/spam sdt số_lần tối đa là 5 - đợi 100giây sử dụng lại.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    diggory_chat3 = f'''
┌──────⭓ {name_bot}
│ Spam: Thành Công 
│ Số Lần Spam Free: {count}
│ Đang Tấn Công : {sdt}
│ Spam 5 Lần Tầm 1-2p mới xong 
│ Hạn Chế Spam Nhé !  
└─────────────
    '''

    script_filename = "dec.py"  # Tên file Python trong cùng thư mục
    try:
        # Kiểm tra xem file có tồn tại không
        if not os.path.isfile(script_filename):
            bot.reply_to(message, "Không tìm thấy file script. Vui lòng kiểm tra lại.")
            return

        # Đọc nội dung file với mã hóa utf-8
        with open(script_filename, 'r', encoding='utf-8') as file:
            script_content = file.read()

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(script_content.encode('utf-8'))
            temp_file_path = temp_file.name

        # Chạy file tạm thời
        process = subprocess.Popen(["python", temp_file_path, sdt, str(count)])
        bot.send_message(message.chat.id, diggory_chat3)
    except FileNotFoundError:
        bot.reply_to(message, "Không tìm thấy file.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi xảy ra: {str(e)}")



blacklist = ["112", "113", "114", "115", "116", "117", "118", "119", "0", "1", "2", "3", "4"]


# Xử lý lệnh /spamvip
@bot.message_handler(commands=['spamvip'])
def supersms(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, 'Hãy Mua Vip Để Sử Dụng.')
        return
    
    current_time = time.time()
    if user_id in last_usage and current_time - last_usage[user_id] < 1:
        bot.reply_to(message, f"Vui lòng đợi {250 - (current_time - last_usage[user_id]):.1f} giây trước khi sử dụng lệnh lại.")
        return
    
    last_usage[user_id] = current_time

    params = message.text.split()[1:]

    if len(params) != 2:
        bot.reply_to(message, "/spamvip sdt số_lần như này cơ mà ")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "Số lần spam không hợp lệ. Vui lòng nhập một số nguyên dương.")
        return
    
    count = int(count)
    
    if count > 30:
        bot.reply_to(message, "/spamvip sdt 30 thôi nhé - đợi 250giây sử dụng lại.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    diggory_chat3 = f'''
┌──────⭓ {name_bot}
│ Spam: Thành Công 
│ Số Lần Spam Vip: {count}
│ Đang Tấn Công : {sdt}
│ Spam 30 Lần Tầm 5-10p mới xong 
│ Hạn Chế Spam Nhé !  
└─────────────
    '''

    script_filename = "dec.py"  # Tên file Python trong cùng thư mục
    try:
        if os.path.isfile(script_filename):
            with open(script_filename, 'r', encoding='utf-8') as file:
                script_content = file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                temp_file.write(script_content.encode('utf-8'))
                temp_file_path = temp_file.name

            process = subprocess.Popen(["python", temp_file_path, sdt, str(count)])
            bot.send_message(message.chat.id, diggory_chat3)
        else:
            bot.reply_to(message, "Tập tin không tìm thấy.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi xảy ra: {str(e)}")



# Xử lý lệnh /voice
from gtts import gTTS
import tempfile
import os
@bot.message_handler(commands=['voice'])
def text_to_voice(message):
    # Lấy nội dung văn bản sau lệnh /voice
    text = message.text[len('/voice '):].strip()

    # Nếu không có văn bản, trả lời hướng dẫn sử dụng
    if not text:
        bot.reply_to(message, "🤖 MUSIC-BOT\nUsage: /voice <Text>")
        return

    # Tạo tệp tạm thời để lưu file .mp3 với tên "elven"
    temp_file_path = tempfile.mktemp(suffix='elven.mp3')

    try:
        # Chuyển văn bản thành giọng nói bằng gTTS
        tts = gTTS(text, lang='vi')
        tts.save(temp_file_path)

        # Mở và gửi file âm thanh .mp3 với tên "elven"
        with open(temp_file_path, 'rb') as audio_file:
            bot.send_voice(chat_id=message.chat.id, voice=audio_file)

    except Exception as e:
        bot.reply_to(message, "🤖 MUSIC-BOT\nError Bot")
    
    finally:
        # Xóa tệp âm thanh tạm thời sau khi gửi
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

from telegram.ext import CallbackContext
from telegram import Update, ChatMember
import qrcode
@bot.message_handler(commands=['qr'])
def generate_qr(message):
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
        bot.send_photo(message.chat.id, photo=bio, caption=f"<blockquote>QR của chữ: {input_text}</blockquote>",parse_mode="HTML")
    else:
        bot.reply_to(message, "🤖 MUSIC-BOT\n🤖 Usage: /qr <Chữ Cần Tạo QR>")
        
        
@bot.message_handler(commands=['napvip'])
def bank_info(message):


    # Lấy ID người gõ lệnh
    user_id = message.from_user.id
    
    # Nội dung văn bản cần gửi cùng với ảnh
    bank_info_text = f'''
<blockquote>Thông Tin Thanh Toán 🏦
├ Ngân Hàng : MB Bank 🏦
├ STK : 1042469410
├ Chủ TK: KIEU VAN NHAT ANH
├ ND : muavip_{user_id}
├ Số Tiền : 30.000đ
├ HSD : 30 Ngày !
├ GỬI BILL CHO AD ĐỂ ĐƯỢC NÂNG VIP
├ LƯU Ý : PHẢI CÓ NỘI DUNG CHUYỂN KHOẢN
└ 💬 Liên Hệ : @taiki
</blockquote>
'''

    bot.send_message(message.chat.id, bank_info_text, parse_mode='HTML')
    


  
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
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
@bot.message_handler(commands=['check'])
def check_hot_web(message):
    # Kiểm tra xem lệnh có đủ tham số không (URL của trang web cần kiểm tra)
    if len(message.text.split()) < 2:
        bot.reply_to(message, '<blockquote>Vui lòng cung cấp URL của trang web cần kiểm tra (VD: /check https://example.com).</blockquote>',parse_mode='HTML')
        return
    
    # Lấy URL từ lệnh
    url = message.text.split()[1]

    try:
        # Gửi yêu cầu HTTP GET đến URL
        response = requests.get(url, timeout=10)
        
        # Kiểm tra trạng thái của trang web
        if response.status_code == 200:
            bot.reply_to(message, f"<blockquote>🔗 Trang web {url} đang hoạt động bình thường (Status: 200 OK).</blockquote>", parse_mode='HTML')
        else:
            bot.reply_to(message, f"<blockquote>⚠️ Trang web {url} có vấn đề (Status: {response.status_code}).</blockquote>", parse_mode='HTML')
    except requests.exceptions.RequestException as e:
        # Xử lý lỗi nếu không thể kết nối tới trang web
        bot.reply_to(message, f"<blockquote>❌ Không thể kết nối tới trang web {url}. Lỗi: {e}</blockquote>", parse_mode='HTML')
      
@bot.message_handler(commands=['checkip'])
def check_ip(message):
    # Lấy các tham số từ lệnh
    params = message.text.split()
    
    if len(params) < 2:
        bot.reply_to(message, 'Vui lòng cung cấp địa chỉ IP cần kiểm tra (VD: /checkip 8.8.8.8).')
        return
    
    ip_address = params[1]

    try:
        # Gửi yêu cầu tới dịch vụ API để lấy thông tin chi tiết về địa chỉ IP
        response = requests.get(f'https://ipinfo.io/{ip_address}/json', timeout=10)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        
        # Lấy dữ liệu từ phản hồi
        ip_data = response.json()

        # Trích xuất thông tin chi tiết
        city = ip_data.get('city', 'Không xác định')
        region = ip_data.get('region', 'Không xác định')
        country = ip_data.get('country', 'Không xác định')
        org = ip_data.get('org', 'Không xác định')
        loc = ip_data.get('loc', 'Không xác định')
        
        # Tạo thông tin để gửi cho người dùng
        ip_info = (f"<blockquote>🌐 Địa chỉ IP: {ip_address}\n"
                   f"📍 Thành phố: {city}\n"
                   f"🏛 Khu vực: {region}\n"
                   f"🌎 Quốc gia: {country}\n"
                   f"🏢 Tổ chức: {org}\n"
                   f"📍 Vị trí (Lat, Lng): {loc}</blockquote>")
        
        # Gửi thông tin địa chỉ IP tới người dùng
        bot.reply_to(message, ip_info, parse_mode='HTML')
    except requests.exceptions.RequestException as e:
        # Xử lý lỗi nếu không thể kết nối đến dịch vụ API
        bot.reply_to(message, f"<blockquote>❌ Không thể kết nối tới dịch vụ kiểm tra IP. Lỗi: {e}</pre>", parse_mode='blockquote')
    except Exception as e:
        # Xử lý các lỗi khác
        bot.reply_to(message, f"<blockquote>❌ Đã xảy ra lỗi khi kiểm tra IP. Lỗi: {e}</pre>", parse_mode='blockquote')
        


@bot.message_handler(commands=['ad'])
def send_admin_info(message):
    bot.send_message(
        message.chat.id, 
        f"Only One => Is : {ADMIN_NAME}\nID: `{ADMIN_ID}`", 
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text.isdigit())
def copy_user_id(message):
    bot.send_message(message.chat.id, f"ID của bạn đã được sao chép: `{message.text}`", parse_mode='Markdown')
ADMIN_NAME = "Taiki"
@bot.message_handler(commands=['id'])
def get_user_id(message):
    if len(message.text.split()) == 1:  
        user_id = message.from_user.id
        bot.reply_to(message, f"ID của bạn là: `{user_id}`", parse_mode='Markdown')
    else:  
        username = message.text.split('@')[-1].strip()
        try:
            user = bot.get_chat(username)  # Lấy thông tin người dùng từ username
            bot.reply_to(message, f"ID của {user.first_name} là: `{user.id}`", parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, "Không tìm thấy người dùng có username này.")
@bot.message_handler(commands=['ID'])
def handle_id_command(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"ID của nhóm này là: {chat_id}")
####################
import time

def restart_program():
    """Khởi động lại script chính và môi trường chạy."""
    python = sys.executable
    script = sys.argv[0]
    # Khởi động lại script chính từ đầu
    try:
        subprocess.Popen([python, script])
    except Exception as e:
        print(f"Khởi động lại không thành công: {e}")
    finally:
        time.sleep(10)  # Đợi một chút để đảm bảo instance cũ đã ngừng hoàn toàn
        sys.exit()

@bot.message_handler(commands=['rs'])
def handle_reset(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "Bot đang khởi động lại...")
        restart_program()
    else:
        bot.reply_to(message, "Bạn không có quyền truy cập vào lệnh này!")
####
@bot.message_handler(commands=['tv'])
def tieng_viet(message):
    chat_id = message.chat.id
    message_id = message.message_id
    
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton("Tiếng Việt 🇻🇳", url='https://t.me/setlanguage/abcxyz')
    keyboard.add(url_button)
    
    bot.send_message(chat_id, 'Click Vào Nút "<b>Tiếng Việt</b>" để đổi thành tv VN in đờ bét.', reply_markup=keyboard, parse_mode='HTML')
    
    # Delete user's command message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        bot.send_message(chat_id, f"Không thể xóa tin nhắn: {e}", parse_mode='HTML')

############
if __name__ == "__main__":
    bot_active = True
    bot.infinity_polling()