import telebot
import time
import threading
import random
import os
import re
import string
import requests
import json
from datetime import datetime
from telebot import types

# ===================================================================
# ========================== ملفات البوابات ==========================
# ===================================================================
from reg import reg
from Strip import Stripe1
from strip_Auth2 import Stripe2
from strip_Auth3 import Stripe3
from strip_Auth4 import Stripe4
from strip_Auth5 import Stripe5
from strip_Auth6 import Stripe6
from braintree1 import bra1
from braintree2 import bra2
from braintree_charge import BraC
from freedom_donate import Donate

# ===================================================================
# ========================== إعدادات البوت ==========================
# ===================================================================
TOKEN = '8490768092:AAF9j7wyL_NI7Fx5jGEn0h3VxuMxeAM2s0I'
ADMIN_ID = 1489001988
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ===================================================================
# ========================== قاعدة البيانات ==========================
# ===================================================================
USERS_FILE = "users_data.json"  # ملف لحفظ بيانات المستخدمين
REFERRAL_FILE = "referrals.json"  # ملف للإحالات
INCIDENTS_FILE = "incidents.json"  # ملف للمشاكل

def load_users():
    """تحميل بيانات المستخدمين من الملف"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """حفظ بيانات المستخدمين في الملف"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_referrals():
    if os.path.exists(REFERRAL_FILE):
        with open(REFERRAL_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_referrals(refs):
    with open(REFERRAL_FILE, 'w') as f:
        json.dump(refs, f, indent=4)

def load_incidents():
    if os.path.exists(INCIDENTS_FILE):
        with open(INCIDENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_incidents(incs):
    with open(INCIDENTS_FILE, 'w') as f:
        json.dump(incs, f, indent=4)

# تحميل البيانات
users_data = load_users()
referrals_data = load_referrals()
incidents_data = load_incidents()

# متغيرات مؤقتة
pending_cards = {}
pending_mass_cards = {}
pending_user_files = {}
pending_gen_count = {}
pending_gateway = {}
stop_check = {}
command_usage = {}

# ===================================================================
# ========================== إدارة المستخدمين ==========================
# ===================================================================

def create_user(user_id, username, first_name, referrer_id=None):
    """إنشاء مستخدم جديد"""
    if str(user_id) not in users_data:
        users_data[str(user_id)] = {
            "name": first_name,
            "username": username,
            "points": 10,  # 10 نقاط مجانية للبداية
            "total_checks": 0,
            "approved_checks": 0,
            "banned": False,
            "vip": False,
            "vip_until": None,
            "referral_code": f"REF{user_id}{random.randint(1000,9999)}",
            "referred_by": referrer_id,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users_data)
        
        # معالجة الإحالة
        if referrer_id and str(referrer_id) in users_data:
            # إضافة نقاط للمستخدم القديم
            users_data[str(referrer_id)]["points"] += 5
            save_users(users_data)
            
            # تسجيل الإحالة
            if str(referrer_id) not in referrals_data:
                referrals_data[str(referrer_id)] = []
            referrals_data[str(referrer_id)].append({
                "user_id": user_id,
                "username": username,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_referrals(referrals_data)
            
            # إشعار للمستخدم القديم
            bot.send_message(referrer_id, f"🎉 مبروك! {first_name} سجل باستخدام كودك\n✨ تم إضافة 5 نقاط إلى رصيدك")
        
        # إشعار للأدمن بمستخدم جديد
        bot.send_message(
            ADMIN_ID,
            f"🆕 **مستخدم جديد**\n━━━━━━━━━━━━━━━━\n"
            f"📛 **الاسم:** {first_name}\n"
            f"🆔 **اليوزر:** @{username or 'لا يوجد'}\n"
            f"🆔 **الايدي:** `{user_id}`\n"
            f"🎫 **كود الإحالة:** `{users_data[str(user_id)]['referral_code']}`\n"
            f"📅 **التاريخ:** {users_data[str(user_id)]['join_date']}"
        )
        return True
    return False

def check_points(user_id, required_points=1):
    """التحقق من النقاط وخصمها"""
    user_id = str(user_id)
    
    if user_id == str(ADMIN_ID):
        return True
    
    if user_id not in users_data:
        create_user(user_id, None, "مستخدم", None)
    
    user = users_data[user_id]
    
    if user.get("banned", False):
        bot.send_message(int(user_id), "🚫 **أنت محظور من استخدام البوت**\nللتواصل مع الدعم: @s3s_a")
        return False
    
    if user.get("points", 0) >= required_points:
        users_data[user_id]["points"] -= required_points
        save_users(users_data)
        return True
    else:
        bot.send_message(
            int(user_id), 
            f"❌ **رصيدك غير كافي!**\n━━━━━━━━━━━━━━━━\n"
            f"⭐ رصيدك الحالي: {user.get('points', 0)} نقطة\n"
            f"🎫 المطلوب: {required_points} نقطة\n\n"
            f"💎 **طرق الشحن:**\n"
            f"• استخدام كود إحالة صديق\n"
            f"• شراء نقاط: تواصل @s3s_a\n"
            f"• انتظار عروض VIP"
        )
        return False

def add_points(user_id, points, reason=""):
    """إضافة نقاط للمستخدم"""
    user_id = str(user_id)
    if user_id in users_data:
        users_data[user_id]["points"] += points
        save_users(users_data)
        bot.send_message(int(user_id), f"✅ تم إضافة {points} نقطة إلى رصيدك\n📝 السبب: {reason}\n⭐ رصيدك الحالي: {users_data[user_id]['points']}")
    return False

def record_check_result(user_id, approved):
    """تسجيل نتيجة الفحص"""
    user_id = str(user_id)
    if user_id in users_data:
        users_data[user_id]["total_checks"] += 1
        if approved:
            users_data[user_id]["approved_checks"] += 1
        save_users(users_data)

def report_gateway_issue(gateway_name, error_msg):
    """الإبلاغ عن مشكلة في بوابة"""
    issue_id = f"{gateway_name}_{int(time.time())}"
    incidents_data[issue_id] = {
        "gateway": gateway_name,
        "error": error_msg,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "resolved": False
    }
    save_incidents(incidents_data)
    
    # إشعار فوري للأدمن
    bot.send_message(
        ADMIN_ID,
        f"⚠️ **مشكلة في بوابة**\n━━━━━━━━━━━━━━━━\n"
        f"🔌 **البوابة:** {gateway_name}\n"
        f"❌ **الخطأ:** {error_msg[:200]}\n"
        f"🆔 **المعرف:** `{issue_id}`\n"
        f"📅 **الوقت:** {incidents_data[issue_id]['time']}"
    )

# ===================================================================
# ========================== القوائم الرئيسية ==========================
# ===================================================================

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 فحص فيزا", callback_data="check_menu"),
        types.InlineKeyboardButton("🃏 توليد فيزات", callback_data="gen_menu"),
        types.InlineKeyboardButton("🔍 فحص بين", callback_data="bin_menu"),
        types.InlineKeyboardButton("📄 بيانات شحن", callback_data="fake_menu"),
        types.InlineKeyboardButton("📁 رفع ملف", callback_data="file_menu"),
        types.InlineKeyboardButton("📊 فحص جماعي", callback_data="mass_check_menu"),
        types.InlineKeyboardButton("🎁 إحالة", callback_data="referral_menu"),
        types.InlineKeyboardButton("📈 إحصائياتي", callback_data="stats_menu"),
        types.InlineKeyboardButton("ℹ️ المساعدة", callback_data="help_menu"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="profile_menu")
    )
    return markup

def check_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔐 Auth (تحقق)", callback_data="auth_menu"),
        types.InlineKeyboardButton("💳 Charge (دفع)", callback_data="charge_menu"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def auth_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 Braintree", callback_data="braintree_auth_menu"),
        types.InlineKeyboardButton("💰 Stripe", callback_data="stripe_auth_menu"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="check_menu")
    )
    return markup

def stripe_auth_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    gateways = [
        ("Stripe1", "st1"), ("Stripe2", "st2"), ("Stripe3", "st3"),
        ("Stripe4", "st4"), ("Stripe5", "st5"), ("Stripe6", "st6")
    ]
    for name, code in gateways:
        markup.add(types.InlineKeyboardButton(f"🔹 {name}", callback_data=f"gateway_st_{code}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="auth_menu"))
    return markup

def braintree_auth_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔹 Braintree 1", callback_data="gateway_br_br1"),
        types.InlineKeyboardButton("🔹 Braintree 2", callback_data="gateway_br_br2"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="auth_menu")
    )
    return markup

def charge_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💝 Donate (تبرع)", callback_data="gateway_ch_donate"),
        types.InlineKeyboardButton("🔹 Braintree Charge", callback_data="gateway_ch_braintree"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="check_menu")
    )
    return markup

def gen_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎲 بين واحد", callback_data="gen_single"),
        types.InlineKeyboardButton("📚 بينات متعددة", callback_data="gen_multi"),
        types.InlineKeyboardButton("🎭 نمط x", callback_data="gen_pattern"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def file_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔐 Auth", callback_data="file_auth_menu"),
        types.InlineKeyboardButton("💳 Charge", callback_data="file_charge_menu"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def file_auth_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💰 Stripe", callback_data="file_stripe_list"),
        types.InlineKeyboardButton("💳 Braintree", callback_data="file_braintree_list"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="file_menu")
    )
    return markup

def file_stripe_list():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for name, code in [("Stripe1","st1"),("Stripe2","st2"),("Stripe3","st3"),("Stripe4","st4"),("Stripe5","st5"),("Stripe6","st6")]:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"file_start_st_{code}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="file_auth_menu"))
    return markup

def file_braintree_list():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Braintree 1", callback_data="file_start_br_br1"),
        types.InlineKeyboardButton("Braintree 2", callback_data="file_start_br_br2"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="file_auth_menu")
    )
    return markup

def file_charge_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Donate", callback_data="file_start_ch_donate"),
        types.InlineKeyboardButton("Braintree Charge", callback_data="file_start_ch_braintree"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="file_menu")
    )
    return markup

def mass_gateway_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    gateways = [
        ("Stripe1", "mass_st1"), ("Stripe2", "mass_st2"), ("Stripe3", "mass_st3"),
        ("Stripe4", "mass_st4"), ("Stripe5", "mass_st5"), ("Stripe6", "mass_st6"),
        ("Donate", "mass_donate"), ("Braintree1", "mass_br1"),
        ("Braintree2", "mass_br2"), ("BraintreeCharge", "mass_chk1")
    ]
    for name, code in gateways:
        markup.add(types.InlineKeyboardButton(name, callback_data=code))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return markup

def help_menu_content():
    return """
📖 **دليل استخدام البوت**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔰 **الأوامر السريعة:**
┌ `/start` - القائمة الرئيسية
├ `/str1` → `/str6` - فحص Stripe
├ `/br1` - فحص Braintree 1  
├ `/br2` - فحص Braintree 2
├ `/donate` - فحص Donate
├ `/chb` - فحص Braintree Charge
├ `/gen` - توليد بطاقات
└ `/mass` - فحص جماعي

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎴 **طريقة التوليد:**



📇 **صيغة البطاقة:**
`4168321234567890|12|2029|123`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ **نظام النقاط:**
• نقطة مجانية لكل مستخدم جديد
• كل فحص = 1 نقطة
• كود الإحالة = 5 نقاط إضافية
• VIP باشتراك شهري = فحص غير محدود

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍💻 **المطور:** @s3s_a
"""

def profile_menu(user_id):
    user_id = str(user_id)
    if user_id not in users_data:
        create_user(int(user_id), None, "مستخدم", None)
    
    user = users_data[user_id]
    success_rate = 0
    if user.get("total_checks", 0) > 0:
        success_rate = (user.get("approved_checks", 0) / user.get("total_checks", 1)) * 100
    
    return f"""
👤 **ملفي الشخصي**
━━━━━━━━━━━━━━━━
📛 **الاسم:** {user.get('name', 'غير معروف')}
🆔 **اليوزر:** @{user.get('username', 'لا يوجد')}
⭐ **النقاط:** {user.get('points', 0)}
📊 **حالة VIP:** {'✅ نشط' if user.get('vip', False) else '❌ غير نشط'}
━━━━━━━━━━━━━━━━
📈 **إحصائيات الفحص:**
▫️ إجمالي الفحوصات: {user.get('total_checks', 0)}
▫️ بطاقات مقبولة: {user.get('approved_checks', 0)}
▫️ نسبة النجاح: {success_rate:.1f}%
━━━━━━━━━━━━━━━━
🎫 **كود الإحالة:** `{user.get('referral_code', 'لا يوجد')}`
👥 **عدد الإحالات:** {len(referrals_data.get(user_id, []))}
━━━━━━━━━━━━━━━━
🎁 كل شخص يسجل بكودك يمنحك 5 نقاط!
"""

# ===================================================================
# ========================== دوال مساعدة ==========================
# ===================================================================

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return (checksum * 9) % 10

def generate_single_card(bin_prefix, month, year, cvv):
    if bin_prefix.startswith('3'):
        total_len = 15
    else:
        total_len = 16
    remaining = total_len - len(bin_prefix)
    if remaining > 0:
        random_digits = ''.join(random.choices(string.digits, k=remaining))
        card_num = bin_prefix + random_digits
    else:
        card_num = bin_prefix[:total_len]
    card_num = card_num[:-1] + str(luhn_checksum(card_num[:-1]))
    if month == 'xx':
        month = str(random.randint(1, 12)).zfill(2)
    if year == 'xx':
        year = str(random.randint(2026, 2031))
    elif len(year) == 2 and year != 'xx':
        year = f"20{year}"
    if cvv.lower() == 'xxx':
        cvv = ''.join(random.choices(string.digits, k=3))
    return f"{card_num}|{month}|{year}|{cvv}"

def generate_cards_advanced(user_input, count=10):
    cards = []
    user_input = user_input.strip()
    
    # بينات متعددة (كل بين في سطر)
    if '\n' in user_input and '|' not in user_input:
        bins = [b.strip() for b in user_input.split('\n') if b.strip().isdigit() and len(b.strip()) >= 6]
        if bins:
            for _ in range(count):
                chosen_bin = random.choice(bins)
                month = str(random.randint(1, 12)).zfill(2)
                year = str(random.randint(2026, 2031))
                cvv = ''.join(random.choices(string.digits, k=3))
                cards.append(generate_single_card(chosen_bin[:6], month, year, cvv))
            return cards
    
    # بينات متعددة مفصولة بفواصل
    if ',' in user_input and '|' not in user_input:
        bins = [b.strip() for b in user_input.split(',') if b.strip()]
        if bins:
            for _ in range(count):
                chosen_bin = random.choice(bins)
                month = str(random.randint(1, 12)).zfill(2)
                year = str(random.randint(2026, 2031))
                cvv = ''.join(random.choices(string.digits, k=3))
                cards.append(generate_single_card(chosen_bin[:6], month, year, cvv))
            return cards
    
    # بين واحد
    if user_input.isdigit() and len(user_input) >= 6 and '|' not in user_input:
        bin_prefix = user_input[:6]
        for _ in range(count):
            month = str(random.randint(1, 12)).zfill(2)
            year = str(random.randint(2026, 2031))
            cvv = ''.join(random.choices(string.digits, k=3))
            cards.append(generate_single_card(bin_prefix, month, year, cvv))
        return cards
    
    # نمط x
    if '|' in user_input:
        parts = user_input.split('|')
        if len(parts) >= 4:
            card_pattern = parts[0].strip()
            month = parts[1].strip().lower()
            year = parts[2].strip().lower()
            cvv_pattern = parts[3].strip().lower()
            bin_prefix = card_pattern.lower().replace('x', '')
            for _ in range(count):
                temp_bin = bin_prefix
                if bin_prefix.startswith('3'):
                    total_len = 15
                else:
                    total_len = 16
                if 'x' in card_pattern.lower():
                    x_count = card_pattern.lower().count('x')
                    needed = total_len - (len(card_pattern) - x_count)
                    if needed > 0:
                        random_digits = ''.join(random.choices(string.digits, k=needed))
                        temp_bin = bin_prefix + random_digits
                cards.append(generate_single_card(temp_bin, month, year, cvv_pattern))
            return cards
    
    return None

def extract_cards_from_message(text):
    cards = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        patterns = [
            r'(\d{15,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',
            r'(\d{15,16})\|(\d{1,2})\|(\d{2})\|(\d{3,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                card_num = match.group(1)
                month = match.group(2).zfill(2)
                year = match.group(3)
                cvv = match.group(4)
                if len(year) == 2:
                    year = f"20{year}"
                cards.append(f"{card_num}|{month}|{year}|{cvv}")
                break
    return cards

def get_bin_info(bin_code):
    try:
        url = f"https://bins.antipublic.cc/bins/{bin_code}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            d = r.json()
            brand = d.get('brand', 'Unknown')
            card_type = d.get('type', 'Unknown').upper()
            level = d.get('level', 'Unknown')
            bank = d.get('bank', 'Unknown')
            country = d.get('country_name', 'Unknown')
            flag = d.get('country_flag', '')
            return f"""[ϟ] 𝐁𝐢𝐧: {brand} - {card_type} - {level}
[ϟ] 𝐁𝐚𝐧𝐤: {bank} - {flag}
[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country} [ {flag} ]"""
    except:
        pass
    
    try:
        url = f"https://lookup.binlist.net/{bin_code}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            d = r.json()
            scheme = d.get('scheme', 'Unknown')
            brand = scheme.upper() if scheme else 'UNKNOWN'
            card_type = d.get('type', 'UNKNOWN').upper()
            bank = d.get('bank', {}).get('name', 'Unknown')
            country = d.get('country', {}).get('name', 'Unknown')
            flag = d.get('country', {}).get('emoji', '')
            return f"""[ϟ] 𝐁𝐢𝐧: {brand} - {card_type}
[ϟ] 𝐁𝐚𝐧𝐤: {bank} - {flag}
[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country} [ {flag} ]"""
    except:
        pass
    
    return "[ϟ] 𝐁𝐢𝐧: Unknown"

def get_fake_info(country):
    countries_data = {
        "USA": {"first": ["John","James","Robert"], "last":["Smith","Johnson","Williams"], "address":["6200 Phyllis Dr"], "city":["Cypress"], "state":["CA"], "zip":["90630"], "phone":["+15416450372"]},
        "UK": {"first":["James","David","John"], "last":["Smith","Jones","Taylor"], "address":["221 Baker St"], "city":["London"], "state":["London"], "zip":["NW1 6XE"], "phone":["+442079460958"]},
        "Canada": {"first":["Liam","Noah","William"], "last":["Smith","Brown","Tremblay"], "address":["123 Queen St"], "city":["Toronto"], "state":["ON"], "zip":["M5V 2T6"], "phone":["+14165551234"]},
        "Germany": {"first":["Max","Alexander","Paul"], "last":["Müller","Schmidt","Schneider"], "address":["Hauptstrasse 1"], "city":["Berlin"], "state":["Berlin"], "zip":["10115"], "phone":["+49301234567"]},
        "France": {"first":["Lucas","Louis","Jules"], "last":["Martin","Bernard","Dubois"], "address":["10 Rue de la Paix"], "city":["Paris"], "state":["Paris"], "zip":["75001"], "phone":["+33123456789"]},
        "Italy": {"first":["Leonardo","Francesco","Alessandro"], "last":["Rossi","Russo","Ferrari"], "address":["Via Roma 1"], "city":["Rome"], "state":["RM"], "zip":["00100"], "phone":["+39061234567"]},
    }
    
    if country not in countries_data:
        country = "USA"
    
    d = countries_data[country]
    first = random.choice(d["first"])
    last = random.choice(d["last"])
    name = f"{first} {last}"
    address = random.choice(d["address"])
    city = random.choice(d["city"])
    state = random.choice(d["state"]) if isinstance(d["state"], list) else d["state"]
    zipcode = random.choice(d["zip"]) if isinstance(d["zip"], list) else d["zip"]
    phone = random.choice(d["phone"]) if isinstance(d["phone"], list) else d["phone"]
    email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@gmail.com"
    
    return f"""🌍 **بيانات شحن - {country}**
━━━━━━━━━━━━━━━━
👤 **الاسم:** {name}
📧 **البريد:** {email}
🏠 **العنوان:** {address}
🌆 **المدينة:** {city}
📍 **الولاية:** {state}
📮 **الرمز البريدي:** {zipcode}
📞 **الهاتف:** {phone}
━━━━━━━━━━━━━━━━"""

def format_result(gateway_name, card, status, response, bin_info, exec_time):
    """تنسيق نتيجة الفحص"""
    status_emoji = "✅" if "Approved" in status else "❌"
    return f"""<b>#{gateway_name} 🔥</b>
- - - - - - - - - - - - - - - - - - - - - - -
[ϟ] 𝐂𝐚𝐫𝐝: <code>{card}</code>
[ϟ] 𝐒𝐭𝐚𝐭𝐮𝐬: {status_emoji} {status}
[ϟ] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: {response}
- - - - - - - - - - - - - - - - - - - - - - -
{bin_info}
- - - - - - - - - - - - - - - - - - - - - - -
[⌥] 𝐓𝐢𝐦𝐞: <code>{exec_time:.2f}'s</code>
[⌤] 𝐃𝐞𝐯: @s3s_a</b>"""

def check_single_card_msg(message, check_func, gateway_name):
    """فحص بطاقة مفردة"""
    user_id = message.from_user.id
    
    if not check_points(user_id):
        return
    
    status_msg = bot.reply_to(message, "⏳ جاري الفحص...")
    
    try:
        if message.reply_to_message:
            text = message.reply_to_message.text
        else:
            text = message.text
            text = re.sub(r'^/[a-z0-9]+', '', text).strip()
        
        card = reg(text)
        if not card:
            bot.edit_message_text("❌ صيغة غير صحيحة\nالصيغة: XXXXXXXXXXXXXXXX|MM|YYYY|CVV", message.chat.id, status_msg.message_id)
            return
        
        start = time.time()
        try:
            result = str(check_func(card))
            exec_time = time.time() - start
            status = "Approved" if ("Approved" in result or "✅" in result) else "Declined"
            bin_info = get_bin_info(card[:6])
            msg = format_result(gateway_name, card, status, result, bin_info, exec_time)
            
            # تسجيل النتيجة
            record_check_result(user_id, "Approved" in status)
            
        except Exception as e:
            error_msg = str(e)
            exec_time = time.time() - start
            msg = format_result(gateway_name, card, "Error", error_msg[:100], get_bin_info(card[:6]), exec_time)
            record_check_result(user_id, False)
            
            # الإبلاغ عن مشكلة في البوابة
            if "ConnectionError" in error_msg or "Timeout" in error_msg or "block" in error_msg.lower():
                report_gateway_issue(gateway_name, error_msg)
        
        bot.edit_message_text(msg, message.chat.id, status_msg.message_id, parse_mode="HTML")
        
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", message.chat.id, status_msg.message_id)

def check_multiple_cards(message, check_func, gateway_name):
    """فحص عدة بطاقات من رسالة"""
    user_id = message.from_user.id
    cards = extract_cards_from_message(message.reply_to_message.text)
    
    if not cards:
        bot.reply_to(message, "❌ لم يتم العثور على بطاقات")
        return
    
    if not check_points(user_id, len(cards)):
        return
    
    status_msg = bot.reply_to(message, f"🚀 جاري فحص {len(cards)} بطاقة...")
    
    def run():
        approved = 0
        for i, card in enumerate(cards, 1):
            try:
                start = time.time()
                result = str(check_func(card))
                exec_time = time.time() - start
                status = "Approved" if ("Approved" in result or "✅" in result) else "Declined"
                if "Approved" in status:
                    approved += 1
                bin_info = get_bin_info(card[:6])
                msg = format_result(gateway_name, card, status, result, bin_info, exec_time)
                bot.send_message(message.chat.id, msg, parse_mode="HTML")
                record_check_result(user_id, "Approved" in status)
                bot.send_message(message.chat.id, f"📊 تقدم: {i}/{len(cards)} | ✅ {approved}")
                time.sleep(5)
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ خطأ في {card}: {str(e)}")
                record_check_result(user_id, False)
        
        bot.edit_message_text(f"✅ اكتمل الفحص\n✅ مقبولة: {approved}\n❌ مرفوضة: {len(cards)-approved}", message.chat.id, status_msg.message_id)
    
    threading.Thread(target=run).start()

# ===================================================================
# ========================== الأوامر ==========================
# ===================================================================

    
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # التحقق من وجود كود إحالة
    referrer_id = None

    if len(message.text.split()) > 1:
        ref_code = message.text.split()[1]

        # البحث عن المستخدم صاحب الكود
        for uid, data in users_data.items():
            if data.get("referral_code") == ref_code and int(uid) != user_id:
                referrer_id = int(uid)
                break
    
    # إنشاء المستخدم
    create_user(user_id, username, first_name, referrer_id)
    
    welcome_msg = f"""
✨ **مرحبا بك {first_name}** ✨
━━━━━━━━━━━━━━━━━━━━━━━
🇪🇬 بوت فحص فيزات متطور
💳 يدعم 6 بوابات Stripe + 2 Braintree
⚡ فحص فردي + فحص جماعي + توليد
━━━━━━━━━━━━━━━━━━━━━━━
⭐ **رصيدك الابتدائي:** 10 نقاط
🎫 **كود الإحالة الخاص بك:** `{users_data[str(user_id)]['referral_code']}`
━━━━━━━━━━━━━━━━━━━━━━━
📌 استخدم الأزرار أدناه للبدء
"""
    bot.send_message(message.chat.id, welcome_msg, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text.startswith(('/str1', '.str1')))
def cmd_str1(m):
    check_single_card_msg(m, Stripe1, "Stripe1")

@bot.message_handler(func=lambda m: m.text.startswith(('/str2', '.str2')))
def cmd_str2(m):
    check_single_card_msg(m, Stripe2, "Stripe2")

@bot.message_handler(func=lambda m: m.text.startswith(('/str3', '.str3')))
def cmd_str3(m):
    check_single_card_msg(m, Stripe3, "Stripe3")

@bot.message_handler(func=lambda m: m.text.startswith(('/str4', '.str4')))
def cmd_str4(m):
    check_single_card_msg(m, Stripe4, "Stripe4")

@bot.message_handler(func=lambda m: m.text.startswith(('/str5', '.str5')))
def cmd_str5(m):
    check_single_card_msg(m, Stripe5, "Stripe5")

@bot.message_handler(func=lambda m: m.text.startswith(('/str6', '.str6')))
def cmd_str6(m):
    check_single_card_msg(m, Stripe6, "Stripe6")

@bot.message_handler(func=lambda m: m.text.startswith(('/br1', '.br1')))
def cmd_br1(m):
    check_single_card_msg(m, bra1, "Braintree1")

@bot.message_handler(func=lambda m: m.text.startswith(('/br2', '.br2')))
def cmd_br2(m):
    check_single_card_msg(m, bra2, "Braintree2")

@bot.message_handler(func=lambda m: m.text.startswith(('/donate', '.donate')))
def cmd_donate(m):
    check_single_card_msg(m, Donate, "Donate")

@bot.message_handler(commands=['chb'])
def cmd_chb(m):
    check_single_card_msg(m, BraC, "BraintreeCharge")

@bot.message_handler(commands=['gen'])
def gen_command(message):
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ أرسل البين أو النمط\nمثال:\n`/gen 528445`\n`/gen 400519,528445,518928`\n`/gen 410621xxxx|12|29|xxx`", parse_mode="Markdown")
        return
    
    pattern = parts[1].strip()
    pending_gen_count[user_id] = pattern
    markup = types.InlineKeyboardMarkup(row_width=2)
    for count in [5, 10, 20, 50, 100]:
        markup.add(types.InlineKeyboardButton(f"{count} بطاقة", callback_data=f"gen_count_{count}"))
    bot.reply_to(message, "📊 اختر عدد البطاقات:", reply_markup=markup)

@bot.message_handler(commands=['mass'])
def mass_command(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ قم بالرد على رسالة تحتوي على بطاقات")
        return
    
    cards = extract_cards_from_message(message.reply_to_message.text)
    if not cards:
        bot.reply_to(message, "❌ لم يتم العثور على بطاقات")
        return
    
    # التحقق من النقاط قبل عرض القائمة
    if not check_points(message.from_user.id, len(cards)):
        return
    
    pending_mass_cards[message.from_user.id] = cards
    bot.reply_to(message, f"📊 تم العثور على {len(cards)} بطاقة\nاختر بوابة الفحص:", reply_markup=mass_gateway_menu())

@bot.message_handler(commands=['addpoints'])
def add_points_command(message):
    """أمر خاص للأدمن لإضافة نقاط"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        points = int(parts[2])
        reason = " ".join(parts[3:]) if len(parts) > 3 else "شحن رصيد"
        add_points(user_id, points, reason)
        bot.reply_to(message, f"✅ تم إضافة {points} نقطة للمستخدم {user_id}")
    except:
        bot.reply_to(message, "❌ الاستخدام: /addpoints <user_id> <points> <reason>")

@bot.message_handler(commands=['ban'])
def ban_command(message):
    """حظر مستخدم"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        parts = message.text.split()
        user_id = str(parts[1])
        if user_id in users_data:
            users_data[user_id]["banned"] = True
            save_users(users_data)
            bot.reply_to(message, f"✅ تم حظر المستخدم {user_id}")
            bot.send_message(int(user_id), "🚫 تم حظر حسابك من البوت")
    except:
        bot.reply_to(message, "❌ الاستخدام: /ban <user_id>")

@bot.message_handler(commands=['unban'])
def unban_command(message):
    """رفع الحظر عن مستخدم"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        parts = message.text.split()
        user_id = str(parts[1])
        if user_id in users_data:
            users_data[user_id]["banned"] = False
            save_users(users_data)
            bot.reply_to(message, f"✅ تم فك الحظر عن المستخدم {user_id}")
            bot.send_message(int(user_id), "✅ تم فك الحظر عن حسابك")
    except:
        bot.reply_to(message, "❌ الاستخدام: /unban <user_id>")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """إحصائيات البوت للأدمن"""
    if message.from_user.id != ADMIN_ID:
        return
    
    total_users = len(users_data)
    total_checks = sum(u.get("total_checks", 0) for u in users_data.values())
    total_approved = sum(u.get("approved_checks", 0) for u in users_data.values())
    vip_users = sum(1 for u in users_data.values() if u.get("vip", False))
    banned_users = sum(1 for u in users_data.values() if u.get("banned", False))
    
    stats = f"""
📊 **إحصائيات البوت**
━━━━━━━━━━━━━━━━
👥 **المستخدمين:** {total_users}
⭐ **VIP:** {vip_users}
🚫 **محظورين:** {banned_users}
━━━━━━━━━━━━━━━━
💳 **إجمالي الفحوصات:** {total_checks}
✅ **الفحوصات المقبولة:** {total_approved}
📈 **نسبة النجاح:** {(total_approved/total_checks*100) if total_checks > 0 else 0:.1f}%
━━━━━━━━━━━━━━━━
⚠️ **مشاكل البوابات:** {len(incidents_data)}
"""
    bot.reply_to(message, stats)

@bot.message_handler(func=lambda m: m.text and ('|' in m.text) and len(m.text.split('|')) >= 3)
def auto_detect_card(message):
    """كشف تلقائي للبطاقة وعرض خيارات الفحص"""
    cards = extract_cards_from_message(message.text)
    if cards:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔐 Auth", callback_data=f"quick_auth_{message.message_id}"),
            types.InlineKeyboardButton("💳 Charge", callback_data=f"quick_charge_{message.message_id}")
        )
        bot.reply_to(message, "💳 تم اكتشاف بطاقة/بطاقات\nاختر نوع الفحص:", reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        filename = f"combo_{user_id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        
        # حساب عدد البطاقات في الملف
        with open(filename, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
            card_count = len(lines)
        
        # التحقق من النقاط
        if not check_points(user_id, card_count):
            os.remove(filename)
            return
        
        pending_user_files[user_id] = filename
        bot.reply_to(message, f"📁 تم رفع الملف\n📊 عدد البطاقات: {card_count}\n🎫 سيتم خصم {card_count} نقطة\nاختر نوع البوابات:", reply_markup=file_auth_menu())
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["usa", "uk", "canada", "germany", "france", "italy"])
def fake_info_command(message):
    bot.reply_to(message, get_fake_info(message.text.capitalize()), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.isdigit() and 6 <= len(m.text) <= 8)
def bin_command(message):
    bin_code = message.text[:6]
    bot.reply_to(message, get_bin_info(bin_code), parse_mode="HTML")

# ===================================================================
# ========================== معالج الأزرار ==========================
# ===================================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data
    user_id = call.from_user.id
    
    # ========== قوائم التنقل ==========
    if data == "back_main":
        bot.edit_message_text("✨ القائمة الرئيسية", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    
    elif data == "check_menu":
        bot.edit_message_text("🔍 اختر نوع الفحص:", call.message.chat.id, call.message.message_id, reply_markup=check_menu())
    
    elif data == "auth_menu":
        bot.edit_message_text("🔐 اختر بوابة Auth:", call.message.chat.id, call.message.message_id, reply_markup=auth_menu())
    
    elif data == "charge_menu":
        bot.edit_message_text("💳 اختر بوابة Charge:", call.message.chat.id, call.message.message_id, reply_markup=charge_menu())
    
    elif data == "braintree_auth_menu":
        bot.edit_message_text("💳 بوابات Braintree Auth:", call.message.chat.id, call.message.message_id, reply_markup=braintree_auth_menu())
    
    elif data == "stripe_auth_menu":
        bot.edit_message_text("💰 بوابات Stripe Auth:", call.message.chat.id, call.message.message_id, reply_markup=stripe_auth_menu())
    
    elif data == "gen_menu":
        bot.edit_message_text("🎴 اختر طريقة التوليد:", call.message.chat.id, call.message.message_id, reply_markup=gen_menu())
    
    elif data == "bin_menu":
        bot.edit_message_text("🔍 أرسل الـ BIN (6-8 أرقام)", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    elif data == "fake_menu":
        bot.edit_message_text("🌍 أرسل اسم الدولة:\nUSA - UK - Canada - Germany - France - Italy", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    elif data == "file_menu":
        bot.edit_message_text("📁 أرسل ملف txt يحتوي على بطاقات", call.message.chat.id, call.message.message_id, reply_markup=file_menu())
    
    elif data == "mass_check_menu":
        bot.edit_message_text("📊 قم بالرد على رسالة تحتوي على بطاقات ثم ارسل /mass", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    elif data == "help_menu":
        bot.edit_message_text(help_menu_content(), call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")))
    
    elif data == "profile_menu":
        bot.edit_message_text(profile_menu(user_id), call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")))
    
    elif data == "referral_menu":
        user = users_data.get(str(user_id), {})
        ref_code = user.get("referral_code", "")
        bot.edit_message_text(
            f"🎁 **نظام الإحالات**\n━━━━━━━━━━━━━━━━\n"
            f"📋 **كود الإحالة الخاص بك:**\n`{ref_code}`\n\n"
            f"🔗 **رابط الإحالة:**\n`https://t.me/{bot.get_me().username}?start={ref_code}`\n\n"
            f"⭐ **المكافأة:** 5 نقاط لكل مستخدم يسجل بكودك\n"
            f"👥 **عدد إحالاتك:** {len(referrals_data.get(str(user_id), []))}",
            call.message.chat.id, call.message.message_id, parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        )
    
    elif data == "stats_menu":
        user = users_data.get(str(user_id), {})
        success_rate = 0
        total = user.get("total_checks", 0)
        approved = user.get("approved_checks", 0)
        if total > 0:
            success_rate = (approved / total) * 100
        
        bot.edit_message_text(
            f"📈 **إحصائياتي**\n━━━━━━━━━━━━━━━━\n"
            f"📊 إجمالي الفحوصات: {total}\n"
            f"✅ الفحوصات المقبولة: {approved}\n"
            f"❌ الفحوصات المرفوضة: {total - approved}\n"
            f"📈 نسبة النجاح: {success_rate:.1f}%\n"
            f"⭐ النقاط المتبقية: {user.get('points', 0)}\n"
            f"👥 عدد الإحالات: {len(referrals_data.get(str(user_id), []))}",
            call.message.chat.id, call.message.message_id,
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        )
    
    elif data == "file_auth_menu":
        bot.edit_message_text("📁 اختر نوع Auth:", call.message.chat.id, call.message.message_id, reply_markup=file_auth_menu())
    
    elif data == "file_charge_menu":
        bot.edit_message_text("📁 اختر نوع Charge:", call.message.chat.id, call.message.message_id, reply_markup=file_charge_menu())
    
    elif data == "file_stripe_list":
        bot.edit_message_text("💰 اختر بوابة Stripe:", call.message.chat.id, call.message.message_id, reply_markup=file_stripe_list())
    
    elif data == "file_braintree_list":
        bot.edit_message_text("💳 اختر بوابة Braintree:", call.message.chat.id, call.message.message_id, reply_markup=file_braintree_list())
    
    # ========== توليد البطاقات ==========
    elif data.startswith("gen_count_"):
        count = int(data.replace("gen_count_", ""))
        pattern = pending_gen_count.get(user_id, "")
        if pattern:
            cards = generate_cards_advanced(pattern, count)
            if cards:
                pending_cards[user_id] = cards
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("📤 عرض في الشات", callback_data="send_chat"),
                    types.InlineKeyboardButton("📁 حفظ كملف", callback_data="save_file")
                )
                bot.edit_message_text(f"🎴 تم توليد {len(cards)} بطاقة\nاختر طريقة العرض:", call.message.chat.id, call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text("❌ صيغة غير صحيحة", call.message.chat.id, call.message.message_id)
    
    elif data == "send_chat":
        if user_id in pending_cards:
            cards = pending_cards[user_id]
            msg = "\n".join([f"<code>{c}</code>" for c in cards])
            if len(msg) > 4000:
                filename = f"cards_{user_id}.txt"
                with open(filename, "w") as f:
                    f.write("\n".join(cards))
                with open(filename, "rb") as f:
                    bot.send_document(call.message.chat.id, f)
                os.remove(filename)
            else:
                bot.send_message(call.message.chat.id, f"🎴 **البطاقات المولدة**\n{msg}", parse_mode="HTML")
            bot.answer_callback_query(call.id, "✅ تم الإرسال")
    
    elif data == "save_file":
        if user_id in pending_cards:
            cards = pending_cards[user_id]
            filename = f"cards_{user_id}_{int(time.time())}.txt"
            with open(filename, "w") as f:
                f.write("\n".join(cards))
            with open(filename, "rb") as f:
                bot.send_document(call.message.chat.id, f)
            os.remove(filename)
            bot.answer_callback_query(call.id, "✅ تم الحفظ")
    
    # ========== بوابات Auth ==========
    elif data.startswith("gateway_st_"):
        code = data.replace("gateway_st_", "")
        gateways = {"st1": Stripe1, "st2": Stripe2, "st3": Stripe3, "st4": Stripe4, "st5": Stripe5, "st6": Stripe6}
        names = {"st1": "Stripe1", "st2": "Stripe2", "st3": "Stripe3", "st4": "Stripe4", "st5": "Stripe5", "st6": "Stripe6"}
        if code in gateways:
            bot.edit_message_text(f"✅ تم اختيار {names[code]}\nأرسل البطاقة للفحص:\n`XXXX|MM|YYYY|CVV`\n\nأو قم بالرد على رسالة تحتوي على بطاقات", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
            pending_gateway[user_id] = (gateways[code], names[code])
    
    elif data.startswith("gateway_br_"):
        code = data.replace("gateway_br_", "")
        gateways = {"br1": bra1, "br2": bra2}
        names = {"br1": "Braintree1", "br2": "Braintree2"}
        if code in gateways:
            bot.edit_message_text(f"✅ تم اختيار {names[code]}\nأرسل البطاقة للفحص:\n`XXXX|MM|YYYY|CVV`\n\nأو قم بالرد على رسالة تحتوي على بطاقات", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
            pending_gateway[user_id] = (gateways[code], names[code])
    
    elif data.startswith("gateway_ch_"):
        code = data.replace("gateway_ch_", "")
        if code == "donate":
            bot.edit_message_text(f"✅ تم اختيار Donate\nأرسل البطاقة للفحص:\n`XXXX|MM|YYYY|CVV`", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
            pending_gateway[user_id] = (Donate, "Donate")
        elif code == "braintree":
            bot.edit_message_text(f"✅ تم اختيار BraintreeCharge\nأرسل البطاقة للفحص:\n`XXXX|MM|YYYY|CVV`", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
            pending_gateway[user_id] = (BraC, "BraintreeCharge")
    
    # ========== فحص الملفات ==========
    elif data.startswith("file_start_st_"):
        code = data.replace("file_start_st_", "")
        gateways = {"st1": Stripe1, "st2": Stripe2, "st3": Stripe3, "st4": Stripe4, "st5": Stripe5, "st6": Stripe6}
        names = {"st1": "Stripe1", "st2": "Stripe2", "st3": "Stripe3", "st4": "Stripe4", "st5": "Stripe5", "st6": "Stripe6"}
        if user_id in pending_user_files and code in gateways:
            start_file_check(call, user_id, pending_user_files[user_id], gateways[code], names[code])
    
    elif data.startswith("file_start_br_"):
        code = data.replace("file_start_br_", "")
        gateways = {"br1": bra1, "br2": bra2}
        names = {"br1": "Braintree1", "br2": "Braintree2"}
        if user_id in pending_user_files and code in gateways:
            start_file_check(call, user_id, pending_user_files[user_id], gateways[code], names[code])
    
    elif data.startswith("file_start_ch_"):
        code = data.replace("file_start_ch_", "")
        if code == "donate" and user_id in pending_user_files:
            start_file_check(call, user_id, pending_user_files[user_id], Donate, "Donate")
        elif code == "braintree" and user_id in pending_user_files:
            start_file_check(call, user_id, pending_user_files[user_id], BraC, "BraintreeCharge")
    
    # ========== فحص جماعي ==========
    elif data.startswith("mass_"):
        gw_code = data.replace("mass_", "")
        gateways = {
            "st1": Stripe1, "st2": Stripe2, "st3": Stripe3, "st4": Stripe4, "st5": Stripe5, "st6": Stripe6,
            "donate": Donate, "br1": bra1, "br2": bra2, "chk1": BraC
        }
        names = {
            "st1": "Stripe1", "st2": "Stripe2", "st3": "Stripe3", "st4": "Stripe4", "st5": "Stripe5", "st6": "Stripe6",
            "donate": "Donate", "br1": "Braintree1", "br2": "Braintree2", "chk1": "BraintreeCharge"
        }
        if user_id in pending_mass_cards and gw_code in gateways:
            start_mass_check(call, user_id, pending_mass_cards[user_id], gateways[gw_code], names[gw_code])
    
    # ========== إيقاف الفحص ==========
    elif data.startswith("stop_"):
        session_id = data.replace("stop_", "")
        if session_id in stop_check:
            stop_check[session_id] = True
            bot.answer_callback_query(call.id, "✅ تم إيقاف الفحص")
    
    else:
        bot.answer_callback_query(call.id)

# ========== دوال مساعدة للفحص ==========

def start_file_check(call, user_id, filename, check_func, gateway_name):
    """بدء فحص الملف"""
    try:
        with open(filename, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        if not lines:
            bot.edit_message_text("❌ الملف فارغ", call.message.chat.id, call.message.message_id)
            return
        
        session_id = f"{user_id}_{int(time.time())}"
        stop_check[session_id] = False
        
        msg = bot.send_message(call.message.chat.id, f"🚀 بدء فحص {len(lines)} بطاقة على {gateway_name}...")
        
        def run():
            approved = 0
            for i, card in enumerate(lines, 1):
                if stop_check.get(session_id):
                    bot.edit_message_text(f"⏹️ تم الإيقاف عند {i-1}/{len(lines)}", call.message.chat.id, msg.message_id)
                    break
                
                try:
                    start = time.time()
                    result = str(check_func(card))
                    exec_time = time.time() - start
                    
                    status = "Approved" if ("Approved" in result or "✅" in result) else "Declined"
                    if "Approved" in status:
                        approved += 1
                    
                    bin_info = get_bin_info(card[:6])
                    result_msg = format_result(gateway_name, card, status, result, bin_info, exec_time)
                    bot.send_message(user_id, result_msg, parse_mode="HTML")
                    record_check_result(user_id, status == "Approved")
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("⏹️ إيقاف", callback_data=f"stop_{session_id}"))
                    bot.edit_message_text(f"📊 تقدم: {i}/{len(lines)} | ✅ {approved}\n⏱️ {exec_time:.2f}s", call.message.chat.id, msg.message_id, reply_markup=markup)
                    
                    time.sleep(7)
                except Exception as e:
                    bot.send_message(user_id, f"❌ خطأ في {card[:20]}...: {str(e)}")
                    record_check_result(user_id, False)
                    time.sleep(5)
            
            bot.edit_message_text(f"✅ اكتمل الفحص\n✅ مقبولة: {approved}\n❌ مرفوضة: {len(lines)-approved}", call.message.chat.id, msg.message_id)
            os.remove(filename)
            if user_id in pending_user_files:
                del pending_user_files[user_id]
        
        threading.Thread(target=run).start()
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", call.message.chat.id, call.message.message_id)

def start_mass_check(call, user_id, cards, check_func, gateway_name):
    """بدء الفحص الجماعي"""
    session_id = f"mass_{user_id}_{int(time.time())}"
    stop_check[session_id] = False
    
    bot.edit_message_text(f"🚀 بدء فحص {len(cards)} بطاقة على {gateway_name}...", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    
    def run():
        approved = 0
        for i, card in enumerate(cards, 1):
            if stop_check.get(session_id):
                bot.send_message(user_id, f"⏹️ تم الإيقاف عند {i-1}/{len(cards)}")
                break
            
            try:
                start = time.time()
                result = str(check_func(card))
                exec_time = time.time() - start
                
                status = "Approved" if ("Approved" in result or "✅" in result) else "Declined"
                if "Approved" in status:
                    approved += 1
                
                bin_info = get_bin_info(card[:6])
                result_msg = format_result(gateway_name, card, status, result, bin_info, exec_time)
                bot.send_message(user_id, result_msg, parse_mode="HTML")
                record_check_result(user_id, status == "Approved")
                bot.send_message(user_id, f"📊 تقدم: {i}/{len(cards)} | ✅ {approved}")
                time.sleep(5)
            except Exception as e:
                bot.send_message(user_id, f"❌ خطأ في {card}: {str(e)}")
                record_check_result(user_id, False)
        
        bot.send_message(user_id, f"✅ اكتمل الفحص\n✅ مقبولة: {approved}\n❌ مرفوضة: {len(cards)-approved}")
        if user_id in pending_mass_cards:
            del pending_mass_cards[user_id]
    
    threading.Thread(target=run).start()

# ========== معالج الرسائل للفحص المؤقت ==========
@bot.message_handler(func=lambda m: m.from_user.id in pending_gateway)
def handle_pending_gateway(message):
    """معالج البوابات المختارة من القائمة"""
    user_id = message.from_user.id
    check_func, gateway_name = pending_gateway[user_id]
    
    if message.reply_to_message and '\n' in message.reply_to_message.text:
        # فحص متعدد
        cards = extract_cards_from_message(message.reply_to_message.text)
        if cards:
            if not check_points(user_id, len(cards)):
                del pending_gateway[user_id]
                return
            
            status_msg = bot.reply_to(message, f"🚀 جاري فحص {len(cards)} بطاقة...")
            
            def run():
                approved = 0
                for i, card in enumerate(cards, 1):
                    try:
                        start = time.time()
                        result = str(check_func(card))
                        exec_time = time.time() - start
                        status = "Approved" if ("Approved" in result or "✅" in result) else "Declined"
                        if "Approved" in status:
                            approved += 1
                        bin_info = get_bin_info(card[:6])
                        msg = format_result(gateway_name, card, status, result, bin_info, exec_time)
                        bot.send_message(message.chat.id, msg, parse_mode="HTML")
                        record_check_result(user_id, status == "Approved")
                        time.sleep(5)
                    except:
                        pass
                bot.edit_message_text(f"✅ اكتمل\n✅ {approved} | ❌ {len(cards)-approved}", message.chat.id, status_msg.message_id)
            
            threading.Thread(target=run).start()
    else:
        # فحص فردي
        check_single_card_msg(message, check_func, gateway_name)
    
    del pending_gateway[user_id]

# ========== تشغيل البوت ==========
# ========== نهاية الكود ==========
if __name__ == "__main__":
    print("✅ البوت يعمل...")
    print(f"📊 تم تحميل {len(users_data)} مستخدم")
    
    time.sleep(3)
    bot.remove_webhook()
    time.sleep(2)
    print("🚀 Polling started...")
    bot.infinity_polling(skip_pending=True, timeout=20)