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
USERS_FILE = "users_data.json"
REFERRAL_FILE = "referrals.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
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

users_data = load_users()
referrals_data = load_referrals()

# متغيرات مؤقتة
pending_mass_cards = {}
pending_user_files = {}
pending_gen_count = {}
pending_gateway = {}
stop_check = {}

# ===================================================================
# ========================== إدارة المستخدمين ==========================
# ===================================================================

def create_user(user_id, username, first_name, referrer_id=None):
    if str(user_id) not in users_data:
        # الأدمن يبدأ بـ 0 نقاط ومفيش خصم
        initial_points = 0 if user_id == ADMIN_ID else 10
        users_data[str(user_id)] = {
            "name": first_name,
            "username": username,
            "points": initial_points,
            "total_checks": 0,
            "approved_checks": 0,
            "banned": False,
            "vip": False,
            "referral_code": f"REF{user_id}{random.randint(1000,9999)}",
            "referred_by": referrer_id,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users_data)
        
        if referrer_id and str(referrer_id) in users_data and referrer_id != ADMIN_ID:
            users_data[str(referrer_id)]["points"] += 5
            save_users(users_data)
            if str(referrer_id) not in referrals_data:
                referrals_data[str(referrer_id)] = []
            referrals_data[str(referrer_id)].append({"user_id": user_id, "username": username})
            save_referrals(referrals_data)
            bot.send_message(referrer_id, f"🎉 مبروك! {first_name} سجل بكودك\n✨ +5 نقاط")
        
        bot.send_message(ADMIN_ID, f"🆕 مستخدم جديد: {first_name}\n🆔 {user_id}")
        return True
    return False

def check_points(user_id, required_points=1):
    if user_id == ADMIN_ID:
        return True
    user_id_str = str(user_id)
    if user_id_str not in users_data:
        create_user(user_id, None, "مستخدم", None)
    user = users_data[user_id_str]
    if user.get("banned", False):
        bot.send_message(user_id, "🚫 أنت محظور")
        return False
    if user.get("points", 0) >= required_points:
        users_data[user_id_str]["points"] -= required_points
        save_users(users_data)
        return True
    else:
        bot.send_message(user_id, f"❌ رصيدك غير كافي!\n⭐ رصيدك: {user.get('points', 0)} نقطة")
        return False

def record_check_result(user_id, approved):
    user_id_str = str(user_id)
    if user_id_str in users_data:
        users_data[user_id_str]["total_checks"] += 1
        if approved:
            users_data[user_id_str]["approved_checks"] += 1
        save_users(users_data)

# ===================================================================
# ========================== القوائم ==========================
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
        types.InlineKeyboardButton("🔐 Auth", callback_data="auth_menu"),
        types.InlineKeyboardButton("💳 Charge", callback_data="charge_menu"),
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
    for i in range(1, 7):
        markup.add(types.InlineKeyboardButton(f"Stripe{i}", callback_data=f"gateway_st{i}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="auth_menu"))
    return markup

def braintree_auth_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Braintree 1", callback_data="gateway_br1"),
        types.InlineKeyboardButton("Braintree 2", callback_data="gateway_br2"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="auth_menu")
    )
    return markup

def charge_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Donate", callback_data="gateway_donate"),
        types.InlineKeyboardButton("Braintree Charge", callback_data="gateway_chk1"),
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
    for i in range(1, 7):
        markup.add(types.InlineKeyboardButton(f"Stripe{i}", callback_data=f"file_st{i}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="file_auth_menu"))
    return markup

def file_braintree_list():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Braintree 1", callback_data="file_br1"),
        types.InlineKeyboardButton("Braintree 2", callback_data="file_br2"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="file_auth_menu")
    )
    return markup

def file_charge_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Donate", callback_data="file_donate"),
        types.InlineKeyboardButton("Braintree Charge", callback_data="file_chk1"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="file_menu")
    )
    return markup

def mass_gateway_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    gateways = ["Stripe1","Stripe2","Stripe3","Stripe4","Stripe5","Stripe6","Braintree1","Braintree2","Donate","BraintreeCharge"]
    for gw in gateways:
        markup.add(types.InlineKeyboardButton(gw, callback_data=f"mass_{gw}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return markup

def help_menu_content():
    return """
📖 دليل استخدام البوت
━━━━━━━━━━━━━━━━━━━━━
/start - القائمة الرئيسية
/str1 إلى /str6 - فحص Stripe
/br1 , /br2 - فحص Braintree
/donate - فحص Donate
/chb - فحص Braintree Charge
/gen - توليد بطاقات
/mass - فحص جماعي
━━━━━━━━━━━━━━━━━━━━━
👨‍💻 المطور: @s3s_a
"""

def profile_menu(user_id):
    user_id_str = str(user_id)
    if user_id_str not in users_data:
        create_user(user_id, None, "مستخدم", None)
    user = users_data[user_id_str]
    return f"""
👤 ملفي الشخصي
━━━━━━━━━━━━━━━
📛 الاسم: {user.get('name', 'غير معروف')}
⭐ النقاط: {user.get('points', 0)}
📊 إجمالي الفحوصات: {user.get('total_checks', 0)}
✅ المقبولة: {user.get('approved_checks', 0)}
🎫 كود الإحالة: {user.get('referral_code', 'لا يوجد')}
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
    
    if user_input.isdigit() and len(user_input) >= 6 and '|' not in user_input:
        bin_prefix = user_input[:6]
        for _ in range(count):
            month = str(random.randint(1, 12)).zfill(2)
            year = str(random.randint(2026, 2031))
            cvv = ''.join(random.choices(string.digits, k=3))
            cards.append(generate_single_card(bin_prefix, month, year, cvv))
        return cards
    
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
        url = f"https://bins.antipublic.cc/bins/{bin_code[:6]}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            d = r.json()
            brand = d.get('brand', 'Unknown')
            card_type = d.get('type', 'Unknown').upper()
            level = d.get('level', 'Unknown')
            bank = d.get('bank', 'Unknown')
            country = d.get('country_name', 'Unknown')
            flag = d.get('country_flag', '')
            return f"[ϟ] 𝐁𝐢𝐧: {brand} - {card_type} - {level}\n[ϟ] 𝐁𝐚𝐧𝐤: {bank} - {flag}\n[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country} [ {flag} ]"
    except:
        pass
    return "[ϟ] 𝐁𝐢𝐧: Unknown"

def get_fake_info(country):
    countries_data = {
        "USA": {"first": ["John","James","Robert"], "last":["Smith","Johnson","Williams"], "address":["6200 Phyllis Dr"], "city":["Cypress"], "state":["CA"], "zip":["90630"], "phone":["+15416450372"]},
        "UK": {"first":["James","David","John"], "last":["Smith","Jones","Taylor"], "address":["221 Baker St"], "city":["London"], "state":["London"], "zip":["NW1 6XE"], "phone":["+442079460958"]},
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
    return f"""🌍 بيانات شحن - {country}
━━━━━━━━━━━━━━━
👤 الاسم: {name}
📧 البريد: {email}
🏠 العنوان: {address}
🌆 المدينة: {city}
📍 الولاية: {state}
📮 الرمز البريدي: {zipcode}
📞 الهاتف: {phone}
━━━━━━━━━━━━━━━"""

# ===================================================================
# ========================== دوال الفحص ==========================
# ===================================================================

def check_is_approved(response):
    """التحقق إذا كانت البطاقة ناجحة"""
    response_lower = response.lower()
    keywords = ["approved", "success", "added", "charged", "captured", "succeeded"]
    return any(keyword in response_lower for keyword in keywords)

def format_success_result(gateway_name, card, response, bin_info, exec_time):
    """تنسيق نتيجة البطاقة الناجحة فقط"""
    return f"""<b>#{gateway_name} 🔥</b>
- - - - - - - - - - - - - - - - - - - - - - -
[ϟ] 𝐂𝐚𝐫𝐝: <code>{card}</code>
[ϟ] 𝐒𝐭𝐚𝐭𝐮𝐬: Approved ✅
[ϟ] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{response[:100]}</code>
- - - - - - - - - - - - - - - - - - - - - - -
{bin_info}
- - - - - - - - - - - - - - - - - - - - - - -
[⌥] 𝐓𝐢𝐦𝐞: <code>{exec_time:.2f}'s</code>
[⌤] 𝐃𝐞𝐯: @s3s_a</b>"""

def start_file_check(call, user_id, filename, check_func, gateway_name):

    try:

        with open(filename, 'r', encoding='utf-8') as f:
            lines = [x.strip() for x in f if x.strip()]

        if not lines:
            bot.edit_message_text(
                "❌ الملف فارغ",
                call.message.chat.id,
                call.message.message_id
            )
            return

        total = len(lines)

        session_id = f"{user_id}_{int(time.time())}"

        stop_check[session_id] = False

        approved = 0
        declined = 0

        current_card = "Waiting..."
        current_status = "Starting..."

        # ================= KEYBOARD =================

        def build_checker_keyboard():

            kb = types.InlineKeyboardMarkup(row_width=1)

            kb.add(
                types.InlineKeyboardButton(
                    f"💳 CURRENT ➜ {current_card[:30]}",
                    callback_data="current"
                )
            )

            kb.add(
                types.InlineKeyboardButton(
                    f"📡 STATUS ➜ {current_status[:40]}",
                    callback_data="status"
                )
            )

            kb.add(
                types.InlineKeyboardButton(
                    f"✅ APPROVED ➜ [ {approved} ]",
                    callback_data="approved"
                )
            )

            kb.add(
                types.InlineKeyboardButton(
                    f"❌ DECLINED ➜ [ {declined} ]",
                    callback_data="declined"
                )
            )

            kb.add(
                types.InlineKeyboardButton(
                    f"👻 TOTAL ➜ [ {total} ]",
                    callback_data="total"
                )
            )

            kb.add(
                types.InlineKeyboardButton(
                    f"⚡ GATEWAY ➜ {gateway_name}",
                    callback_data="gateway"
                )
            )

            kb.add(
                types.InlineKeyboardButton(
                    "🛑 STOP",
                    callback_data=f"stop_{session_id}"
                )
            )

            return kb

        # ================= START MESSAGE =================

        msg = bot.send_message(
            call.message.chat.id,
            "⏳ STARTED CHECKING...",
            reply_markup=build_checker_keyboard()
        )

        bot.answer_callback_query(call.id)

        # ================= THREAD =================

        def run():

            nonlocal approved
            nonlocal declined
            nonlocal current_card
            nonlocal current_status

            for card in lines:

                if stop_check.get(session_id):

                    try:

                        stop_kb = types.InlineKeyboardMarkup(row_width=1)

                        stop_kb.add(
                            types.InlineKeyboardButton(
                                "🛑 STOPPED",
                                callback_data="stopped"
                            )
                        )

                        stop_kb.add(
                            types.InlineKeyboardButton(
                                f"✅ APPROVED ➜ [ {approved} ]",
                                callback_data="approved"
                            )
                        )

                        stop_kb.add(
                            types.InlineKeyboardButton(
                                f"❌ DECLINED ➜ [ {declined} ]",
                                callback_data="declined"
                            )
                        )

                        stop_kb.add(
                            types.InlineKeyboardButton(
                                f"👻 TOTAL ➜ [ {total} ]",
                                callback_data="total"
                            )
                        )

                        bot.edit_message_reply_markup(
                            call.message.chat.id,
                            msg.message_id,
                            reply_markup=stop_kb
                        )

                    except:
                        pass

                    return

                try:

                    current_card = card

                    result = str(check_func(card))

                    current_status = result[:40]

                    is_live = check_is_approved(result)

                    if is_live:

                        approved += 1

                        bin_info = get_bin_info(card[:6])

                        live_text = f"""
🔥 LIVE CARD

💳 <code>{card}</code>

📡 <code>{result[:100]}</code>

{bin_info}
"""

                        bot.send_message(
                            user_id,
                            live_text,
                            parse_mode="HTML"
                        )

                    else:

                        declined += 1

                    try:

                        bot.edit_message_reply_markup(
                            call.message.chat.id,
                            msg.message_id,
                            reply_markup=build_checker_keyboard()
                        )

                    except Exception as e:

                        if "message is not modified" not in str(e):
                            print(e)

                    time.sleep(2)

                except Exception as e:

                    current_status = f"ERROR: {str(e)[:30]}"

                    declined += 1

                    try:

                        bot.edit_message_reply_markup(
                            call.message.chat.id,
                            msg.message_id,
                            reply_markup=build_checker_keyboard()
                        )

                    except:
                        pass

                    print(e)

            # ================= FINAL =================

            try:

                final_kb = types.InlineKeyboardMarkup(row_width=1)

                final_kb.add(
                    types.InlineKeyboardButton(
                        "✅ COMPLETED",
                        callback_data="done"
                    )
                )

                final_kb.add(
                    types.InlineKeyboardButton(
                        f"✅ APPROVED ➜ [ {approved} ]",
                        callback_data="approved"
                    )
                )

                final_kb.add(
                    types.InlineKeyboardButton(
                        f"❌ DECLINED ➜ [ {declined} ]",
                        callback_data="declined"
                    )
                )

                final_kb.add(
                    types.InlineKeyboardButton(
                        f"👻 TOTAL ➜ [ {total} ]",
                        callback_data="total"
                    )
                )

                bot.edit_message_reply_markup(
                    call.message.chat.id,
                    msg.message_id,
                    reply_markup=final_kb
                )

            except:
                pass

            if os.path.exists(filename):
                os.remove(filename)

            if user_id in pending_user_files:
                del pending_user_files[user_id]

        threading.Thread(target=run).start()

    except Exception as e:

        bot.edit_message_text(
            f"❌ Error: {str(e)}",
            call.message.chat.id,
            call.message.message_id
        )

def check_single_card_msg(message, check_func, gateway_name):
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
            bot.edit_message_text("❌ صيغة غير صحيحة", message.chat.id, status_msg.message_id)
            return
        start_time = time.time()
        result = str(check_func(card))
        exec_time = time.time() - start_time
        bin_info = get_bin_info(card[:6])
        
        if check_is_approved(result):
            status = "Approved ✅"
            record_check_result(user_id, True)
        else:
            status = "Declined ❌"
            record_check_result(user_id, False)
        
        msg = f"""<b>#{gateway_name} 🔥</b>
- - - - - - - - - - - - - - - - - - - - - - -
[ϟ] 𝐂𝐚𝐫𝐝: <code>{card}</code>
[ϟ] 𝐒𝐭𝐚𝐭𝐮𝐬: {status}
[ϟ] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{result[:100]}</code>
- - - - - - - - - - - - - - - - - - - - - - -
{bin_info}
- - - - - - - - - - - - - - - - - - - - - - -
[⌥] 𝐓𝐢𝐦𝐞: <code>{exec_time:.2f}'s</code>
[⌤] 𝐃𝐞𝐯: @s3s_a</b>"""
        bot.edit_message_text(msg, message.chat.id, status_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)[:100]}", message.chat.id, status_msg.message_id)

# ===================================================================
# ========================== دالة فحص الجماعي (Mass) ==========================
# ===================================================================

def start_mass_check(call, user_id, cards, check_func, gateway_name):
    session_id = f"mass_{user_id}_{int(time.time())}"
    stop_check[session_id] = False
    
    total = len(cards)
    msg = bot.send_message(
        call.message.chat.id,
        f"""Wait for processing\nby → @s3s_a\n\n━━━━━━━━━━━━━━━━\n📊 MASS CHECK\n━━━━━━━━━━━━━━━━\nAPPROVED ✅ → [0]\nDECLINED ❌ → [0]\nTOTAL 🥺 → [{total}]\n━━━━━━━━━━━━━━━━\n⏱️ جاري الفحص...""",
        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("[STOP]", callback_data=f"stop_{session_id}"))
    )
    bot.answer_callback_query(call.id)
    
    def run():
        approved = 0
        declined = 0
        for i, card in enumerate(cards, 1):
            if stop_check.get(session_id):
                bot.edit_message_text(f"⏹️ تم الإيقاف عند {i-1}/{total}", call.message.chat.id, msg.message_id)
                break
            try:
                start_time = time.time()
                result = str(check_func(card))
                exec_time = time.time() - start_time
                if check_is_approved(result):
                    approved += 1
                    bin_info = get_bin_info(card[:6])
                    success_msg = format_success_result(gateway_name, card, result, bin_info, exec_time)
                    bot.send_message(user_id, success_msg, parse_mode="HTML")
                    record_check_result(user_id, True)
                else:
                    declined += 1
                    record_check_result(user_id, False)
                
                try:
                    bot.edit_message_text(
                        f"""Wait for processing\nby → @s3s_a\n\n━━━━━━━━━━━━━━━━\n📊 MASS CHECK\n━━━━━━━━━━━━━━━━\nAPPROVED ✅ → [{approved}]\nDECLINED ❌ → [{declined}]\nTOTAL 🥺 → [{total}]\n━━━━━━━━━━━━━━━━\n⏱️ آخر فحص: {exec_time:.2f}s""",
                        call.message.chat.id, msg.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("[STOP]", callback_data=f"stop_{session_id}"))
                    )
                except:
                    pass
                time.sleep(5)
            except Exception as e:
                declined += 1
                record_check_result(user_id, False)
        bot.send_message(user_id, f"✅ اكتمل الفحص\n✅ {approved} | ❌ {declined}")
        if user_id in pending_mass_cards:
            del pending_mass_cards[user_id]
    threading.Thread(target=run).start()

# ===================================================================
# ========================== الأوامر ==========================
# ===================================================================

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    referrer_id = None
    if len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        for uid, data in users_data.items():
            if data.get("referral_code") == ref_code and int(uid) != user_id:
                referrer_id = int(uid)
                break
    create_user(user_id, message.from_user.username, message.from_user.first_name, referrer_id)
    welcome_msg = f"✨ مرحبا بك {message.from_user.first_name}\n⭐ رصيدك: {users_data.get(str(user_id), {}).get('points', 10)} نقاط"
    bot.send_message(message.chat.id, welcome_msg, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text.startswith(('/str1', '.str1')))
def cmd_str1(m): check_single_card_msg(m, Stripe1, "Stripe1")
@bot.message_handler(func=lambda m: m.text.startswith(('/str2', '.str2')))
def cmd_str2(m): check_single_card_msg(m, Stripe2, "Stripe2")
@bot.message_handler(func=lambda m: m.text.startswith(('/str3', '.str3')))
def cmd_str3(m): check_single_card_msg(m, Stripe3, "Stripe3")
@bot.message_handler(func=lambda m: m.text.startswith(('/str4', '.str4')))
def cmd_str4(m): check_single_card_msg(m, Stripe4, "Stripe4")
@bot.message_handler(func=lambda m: m.text.startswith(('/str5', '.str5')))
def cmd_str5(m): check_single_card_msg(m, Stripe5, "Stripe5")
@bot.message_handler(func=lambda m: m.text.startswith(('/str6', '.str6')))
def cmd_str6(m): check_single_card_msg(m, Stripe6, "Stripe6")
@bot.message_handler(func=lambda m: m.text.startswith(('/br1', '.br1')))
def cmd_br1(m): check_single_card_msg(m, bra1, "Braintree1")
@bot.message_handler(func=lambda m: m.text.startswith(('/br2', '.br2')))
def cmd_br2(m): check_single_card_msg(m, bra2, "Braintree2")
@bot.message_handler(func=lambda m: m.text.startswith(('/donate', '.donate')))
def cmd_donate(m): check_single_card_msg(m, Donate, "Donate")
@bot.message_handler(commands=['chb'])
def cmd_chb(m): check_single_card_msg(m, BraC, "BraintreeCharge")

@bot.message_handler(commands=['gen'])
def gen_command(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ أرسل البين أو النمط\n/gen 528445\n/gen 400519,528445,518928\n/gen 410621xxxx|12|29|xxx")
        return
    pending_gen_count[message.from_user.id] = parts[1]
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
    if not check_points(message.from_user.id, len(cards)):
        return
    pending_mass_cards[message.from_user.id] = cards
    bot.reply_to(message, f"📊 تم العثور على {len(cards)} بطاقة", reply_markup=mass_gateway_menu())

@bot.message_handler(commands=['addpoints'])
def add_points_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        points = int(parts[2])
        if str(user_id) in users_data:
            users_data[str(user_id)]["points"] += points
            save_users(users_data)
            bot.send_message(user_id, f"✅ تم إضافة {points} نقطة\n⭐ رصيدك: {users_data[str(user_id)]['points']}")
            bot.reply_to(message, f"✅ تم إضافة {points} نقطة")
    except:
        bot.reply_to(message, "❌ /addpoints <user_id> <points>")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        filename = f"combo_{user_id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        with open(filename, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
            card_count = len(lines)
        if not check_points(user_id, card_count):
            os.remove(filename)
            return
        pending_user_files[user_id] = filename
        bot.reply_to(message, f"📁 تم رفع {card_count} بطاقة\n🎫 سيتم خصم {card_count} نقطة", reply_markup=file_auth_menu())
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

@bot.message_handler(func=lambda m: m.text and m.text.isdigit() and 6 <= len(m.text) <= 8)
def bin_command(message):
    bot.reply_to(message, get_bin_info(message.text[:6]))

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["usa", "uk", "canada", "germany", "france", "italy"])
def fake_info_command(message):
    bot.reply_to(message, get_fake_info(message.text.capitalize()))

# ===================================================================
# ========================== معالج الأزرار ==========================
# ===================================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data
    user_id = call.from_user.id
    
    # قوائم التنقل
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
        bot.edit_message_text(help_menu_content(), call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")))
    elif data == "profile_menu":
        bot.edit_message_text(profile_menu(user_id), call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")))
    elif data == "referral_menu":
        user = users_data.get(str(user_id), {})
        ref_code = user.get("referral_code", "")
        bot.edit_message_text(f"🎁 كود الإحالة: {ref_code}\n🔗 t.me/{bot.get_me().username}?start={ref_code}", call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")))
    elif data == "stats_menu":
        user = users_data.get(str(user_id), {})
        total = user.get("total_checks", 0)
        approved = user.get("approved_checks", 0)
        bot.edit_message_text(f"📊 إجمالي الفحوصات: {total}\n✅ المقبولة: {approved}", call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")))
    elif data == "file_auth_menu":
        bot.edit_message_text("📁 اختر نوع Auth:", call.message.chat.id, call.message.message_id, reply_markup=file_auth_menu())
    elif data == "file_charge_menu":
        bot.edit_message_text("📁 اختر نوع Charge:", call.message.chat.id, call.message.message_id, reply_markup=file_charge_menu())
    elif data == "file_stripe_list":
        bot.edit_message_text("💰 اختر بوابة Stripe:", call.message.chat.id, call.message.message_id, reply_markup=file_stripe_list())
    elif data == "file_braintree_list":
        bot.edit_message_text("💳 اختر بوابة Braintree:", call.message.chat.id, call.message.message_id, reply_markup=file_braintree_list())
    
    # أزرار التوليد
    elif data == "gen_single":
        bot.edit_message_text("🎲 أرسل الـ BIN", call.message.chat.id, call.message.message_id)
        pending_gen_count[user_id] = "single"
        bot.answer_callback_query(call.id)
    elif data == "gen_multi":
        bot.edit_message_text("📚 أرسل البينات مفصولة بفواصل", call.message.chat.id, call.message.message_id)
        pending_gen_count[user_id] = "multi"
        bot.answer_callback_query(call.id)
    elif data == "gen_pattern":
        bot.edit_message_text("🎭 أرسل النمط: 410621xxxx|12|29|xxx", call.message.chat.id, call.message.message_id)
        pending_gen_count[user_id] = "pattern"
        bot.answer_callback_query(call.id)
    
    elif data.startswith("gen_count_"):
        count = int(data.replace("gen_count_", ""))
        pattern = pending_gen_count.get(user_id, "")
        if pattern not in ["single", "multi", "pattern"]:
            cards = generate_cards_advanced(pattern, count)
            if cards:
                bot.edit_message_text(f"🎴 تم توليد {len(cards)} بطاقة:\n" + "\n".join(cards[:20]), call.message.chat.id, call.message.message_id)
            else:
                bot.edit_message_text("❌ صيغة غير صحيحة", call.message.chat.id, call.message.message_id)
    
    # بوابات Auth
    elif data.startswith("gateway_st"):
        num = data.replace("gateway_st", "")
        gateways = {"1": Stripe1, "2": Stripe2, "3": Stripe3, "4": Stripe4, "5": Stripe5, "6": Stripe6}
        names = {"1": "Stripe1", "2": "Stripe2", "3": "Stripe3", "4": "Stripe4", "5": "Stripe5", "6": "Stripe6"}
        if num in gateways:
            bot.edit_message_text(f"✅ تم اختيار {names[num]}\nأرسل البطاقة:", call.message.chat.id, call.message.message_id)
            pending_gateway[user_id] = (gateways[num], names[num])
    elif data == "gateway_br1":
        bot.edit_message_text("✅ Braintree1\nأرسل البطاقة:", call.message.chat.id, call.message.message_id)
        pending_gateway[user_id] = (bra1, "Braintree1")
    elif data == "gateway_br2":
        bot.edit_message_text("✅ Braintree2\nأرسل البطاقة:", call.message.chat.id, call.message.message_id)
        pending_gateway[user_id] = (bra2, "Braintree2")
    elif data == "gateway_donate":
        bot.edit_message_text("✅ Donate\nأرسل البطاقة:", call.message.chat.id, call.message.message_id)
        pending_gateway[user_id] = (Donate, "Donate")
    elif data == "gateway_chk1":
        bot.edit_message_text("✅ BraintreeCharge\nأرسل البطاقة:", call.message.chat.id, call.message.message_id)
        pending_gateway[user_id] = (BraC, "BraintreeCharge")
    
    # فحص الملفات
    elif data.startswith("file_st"):
        num = data.replace("file_st", "")
        gateways = {"1": Stripe1, "2": Stripe2, "3": Stripe3, "4": Stripe4, "5": Stripe5, "6": Stripe6}
        names = {"1": "Stripe1", "2": "Stripe2", "3": "Stripe3", "4": "Stripe4", "5": "Stripe5", "6": "Stripe6"}
        if user_id in pending_user_files and num in gateways:
            start_file_check(call, user_id, pending_user_files[user_id], gateways[num], names[num])
    elif data == "file_br1" and user_id in pending_user_files:
        start_file_check(call, user_id, pending_user_files[user_id], bra1, "Braintree1")
    elif data == "file_br2" and user_id in pending_user_files:
        start_file_check(call, user_id, pending_user_files[user_id], bra2, "Braintree2")
    elif data == "file_donate" and user_id in pending_user_files:
        start_file_check(call, user_id, pending_user_files[user_id], Donate, "Donate")
    elif data == "file_chk1" and user_id in pending_user_files:
        start_file_check(call, user_id, pending_user_files[user_id], BraC, "BraintreeCharge")
    
    # فحص جماعي
    elif data.startswith("mass_"):
        gw_name = data.replace("mass_", "")
        gateways = {
            "Stripe1": Stripe1, "Stripe2": Stripe2, "Stripe3": Stripe3, "Stripe4": Stripe4, "Stripe5": Stripe5, "Stripe6": Stripe6,
            "Braintree1": bra1, "Braintree2": bra2, "Donate": Donate, "BraintreeCharge": BraC
        }
        if user_id in pending_mass_cards and gw_name in gateways:
            start_mass_check(call, user_id, pending_mass_cards[user_id], gateways[gw_name], gw_name)
    
    # إيقاف الفحص
    elif data.startswith("stop_"):
        session_id = data.replace("stop_", "")
        if session_id in stop_check:
            stop_check[session_id] = True
            bot.answer_callback_query(call.id, "✅ تم إيقاف الفحص")
    else:
        bot.answer_callback_query(call.id)

# ===================================================================
# ========== معالج استقبال بيانات التوليد من الأزرار ==========
# ===================================================================

@bot.message_handler(func=lambda m: m.from_user.id in pending_gen_count)
def handle_gen_from_buttons(message):
    user_id = message.from_user.id
    gen_type = pending_gen_count.get(user_id)
    pattern = message.text.strip()
    
    if gen_type == "single":
        cards = generate_cards_advanced(pattern, 10)
    elif gen_type == "multi":
        cards = generate_cards_advanced(pattern, 10)
    elif gen_type == "pattern":
        cards = generate_cards_advanced(pattern, 10)
    else:
        cards = None
    
    if cards:
        bot.reply_to(message, f"🎴 تم توليد {len(cards)} بطاقة:\n" + "\n".join(cards[:10]))
    else:
        bot.reply_to(message, "❌ صيغة غير صحيحة")
    del pending_gen_count[user_id]

# ===================================================================
# ========== معالج الرسائل للفحص المؤقت ==========
# ===================================================================

@bot.message_handler(func=lambda m: m.from_user.id in pending_gateway)
def handle_pending_gateway(message):
    user_id = message.from_user.id
    check_func, gateway_name = pending_gateway[user_id]
    check_single_card_msg(message, check_func, gateway_name)
    del pending_gateway[user_id]

# ===================================================================
# ========================== تشغيل البوت ==========================
# ===================================================================

if __name__ == "__main__":
    print("✅ البوت يعمل...")
    print(f"📊 تم تحميل {len(users_data)} مستخدم")
    time.sleep(2)
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(skip_pending=True, timeout=20)