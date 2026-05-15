import telebot
import time
import threading
import random
import os
import re
import json
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# استيراد البوابات
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
from Donate2 import charge1usd
from Donate3 import charge1usdt

# ==================== الإعدادات ====================
TOKEN = '8490768092:AAFdu9uiwimdB6uvkNGZSYoDpZyDOz22jjQ'
ADMIN_ID = 1489001988
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# ==================== قاعدة البيانات ====================
USERS_FILE = "users_data.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

users_data = load_users()

# متغيرات للتحكم في الفحص
stop_check_flags = {}
pending_mass_cards = {}
current_checks = {}  # تتبع الفحوصات الجارية لكل مستخدم

# ==================== دوال المستخدمين ====================
def get_user(user_id, username=None, first_name=None):
    uid = str(user_id)
    if uid not in users_data:
        users_data[uid] = {
            "name": first_name or "مستخدم",
            "username": username or "",
            "user_id": user_id,
            "total_checks": 0,
            "approved_checks": 0,
            "banned": False,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users_data)
        if user_id != ADMIN_ID:
            bot.send_message(ADMIN_ID, f"🆕 مستخدم جديد:\n👤 {first_name}\n🆔 {user_id}\n📛 @{username or 'لا يوجد'}")
    return users_data[uid]

def is_banned(user_id):
    uid = str(user_id)
    if uid in users_data and users_data[uid].get("banned", False):
        return True
    return False

def update_stats(user_id, approved):
    uid = str(user_id)
    if uid in users_data:
        users_data[uid]["total_checks"] += 1
        if approved:
            users_data[uid]["approved_checks"] += 1
        save_users(users_data)

# ==================== دوال مساعدة ====================
def get_bin_info(bin_code):
    """جلب معلومات BIN"""
    try:
        import requests
        url = f"https://lookup.binlist.net/{bin_code[:6]}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            scheme = data.get('scheme', 'Unknown').upper()
            brand = data.get('brand', 'Unknown')
            type_ = data.get('type', 'Unknown').upper()
            country = data.get('country', {}).get('name', 'Unknown')
            emoji = data.get('country', {}).get('emoji', '')
            bank = data.get('bank', {}).get('name', 'Unknown')
            return f"""[ϟ] 𝐁𝐢𝐧: {scheme} - {type_} - {brand}
[ϟ] 𝐁𝐚𝐧𝐤: {bank} - {emoji}
[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country} [ {emoji} ]"""
    except:
        pass
    return "[ϟ] 𝐁𝐢𝐧: Unknown"

def extract_cards_from_message(text):
    """استخراج البطاقات من النص"""
    cards = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        # البحث عن بطاقات بالصيغة: رقم|شهر|سنة|cvv
        match = re.search(r'(\d{15,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})', line)
        if match:
            card_num = match.group(1)
            month = match.group(2).zfill(2)
            year = match.group(3)
            cvv = match.group(4)
            if len(year) == 2:
                year = f"20{year}"
            cards.append(f"{card_num}|{month}|{year}|{cvv}")
    return cards


# ==================== دوال التنسيق ====================

def format_live_result(gateway_name, card, response, exec_time):
    """تنسيق نتيجة LIVE (تم الخصم)"""
    bin_info = get_bin_info(card[:6])
    return f"""<b>🔥 LIVE - Charged $1 🔥</b>
<b>#{gateway_name}</b>
━━━━━━━━━━━━━━━
<b>CC ➜</b>
<code>{card}</code>
<b>Gateway ➜</b>
{gateway_name}
<b>Response ➜</b>
{response}
━━━━━━━━━━━━━━━
{bin_info}
━━━━━━━━━━━━━━━
<b>Taken ➜</b> <code>{exec_time:.2f}s</code>
━━━━━━━━━━━━━━━
<b>Dev ➜</b> @s3s_a"""

def format_approved_result(gateway_name, card, response, exec_time):
    """تنسيق نتيجة APPROVED (بطاقة صالحة - رصيد غير كافي)"""
    bin_info = get_bin_info(card[:6])
    return f"""<b>✅ APPROVED - Insufficient Funds ✅</b>
<b>#{gateway_name}</b>
━━━━━━━━━━━━━━━
<b>CC ➜</b>
<code>{card}</code>
<b>Gateway ➜</b>
{gateway_name}
<b>Response ➜</b>
{response}
━━━━━━━━━━━━━━━
{bin_info}
━━━━━━━━━━━━━━━
<b>Taken ➜</b> <code>{exec_time:.2f}s</code>
━━━━━━━━━━━━━━━
<b>Dev ➜</b> @s3s_a"""

def format_declined_result(gateway_name, card, response, exec_time):
    """تنسيق نتيجة DECLINED (بطاقة مرفوضة)"""
    bin_info = get_bin_info(card[:6])
    return f"""<b>❌ DECLINED ❌</b>
<b>#{gateway_name}</b>
━━━━━━━━━━━━━━━
<b>CC ➜</b>
<code>{card}</code>
<b>Gateway ➜</b>
{gateway_name}
<b>Response ➜</b>
{response}
━━━━━━━━━━━━━━━
{bin_info}
━━━━━━━━━━━━━━━
<b>Taken ➜</b> <code>{exec_time:.2f}s</code>
━━━━━━━━━━━━━━━
<b>Dev ➜</b> @s3s_a"""

def is_gateway_error(response):
    """التحقق من وجود خطأ في البوابة"""
    error_keywords = [
        "connection", "timeout", "network", "gateway", "Error",
        "could not", "failed", "unreachable", "offline"
    ]
    response_lower = response.lower()
    for keyword in error_keywords:
        if keyword in response_lower:
            return True
    return False

# ==================== دوال الفحص ====================
def check_single_card(message, card, gateway_func, gateway_name):
    """فحص بطاقة فردية"""
    user_id = message.from_user.id
    
    if is_banned(user_id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    
    status_msg = bot.reply_to(message, "⏳ جاري الفحص...")
    
    try:
        start_time = time.time()
        result = str(gateway_func(card))
        exec_time = time.time() - start_time
        
        # تحديد نوع النتيجة
        if "LIVE" in result or "charged" in result.lower():
            msg = format_live_result(gateway_name, card, result, exec_time)
            update_stats(user_id, True)
        elif "Approved" in result or "Insufficient" in result or "insufficient" in result.lower():
            msg = format_approved_result(gateway_name, card, result, exec_time)
            update_stats(user_id, True)
        else:
            msg = format_declined_result(gateway_name, card, result, exec_time)
            update_stats(user_id, False)
        
        bot.edit_message_text(msg, message.chat.id, status_msg.message_id, parse_mode='HTML')
        
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)[:100]}", message.chat.id, status_msg.message_id)

def check_mass_cards(user_id, chat_id, cards, gateway_func, gateway_name, message_id, stop_flag_key):
    """فحص مجموعة بطاقات (للملفات و mass)"""
    total = len(cards)
    approved = 0
    declined = 0
    current_card = "جاري التحميل..."
    current_status = "جاري الفحص..."
    consecutive_errors = 0
    
    # دالة تحديث الواجهة
    def update_display():
        nonlocal current_card, current_status, approved, declined, total
        kb = InlineKeyboardMarkup(row_width=1)
        # اختصار البطاقة لعرضها
        card_preview = current_card[:35] + "..." if len(current_card) > 35 else current_card
        kb.add(
            InlineKeyboardButton(f"💳 CARD → {card_preview}", callback_data="none"),
            InlineKeyboardButton(f"📡 STATUS → {current_status}", callback_data="none"),
            InlineKeyboardButton(f"✅ APPROVED → [{approved}]", callback_data="none"),
            InlineKeyboardButton(f"❌ DECLINED → [{declined}]", callback_data="none"),
            InlineKeyboardButton(f"📊 TOTAL → [{total}]", callback_data="none"),
            InlineKeyboardButton(f"⚡ {gateway_name}", callback_data="none"),
            InlineKeyboardButton("🛑 STOP", callback_data=f"stop_{stop_flag_key}")
        )
        
        # النص الثابت فقط (بدون SobHi)
        msg_text = f"""Wait for processing
by → @s3s_a"""
        
        try:
            bot.edit_message_text(msg_text, chat_id, message_id, reply_markup=kb)
        except:
            pass
    
    # إرسال واجهة البداية
    kb_start = InlineKeyboardMarkup(row_width=1)
    kb_start.add(
        InlineKeyboardButton(f"💳 CARD → جاري التحميل...", callback_data="none"),
        InlineKeyboardButton(f"📡 STATUS → جاري الفحص...", callback_data="none"),
        InlineKeyboardButton(f"✅ APPROVED → [0]", callback_data="none"),
        InlineKeyboardButton(f"❌ DECLINED → [0]", callback_data="none"),
        InlineKeyboardButton(f"📊 TOTAL → [{total}]", callback_data="none"),
        InlineKeyboardButton(f"⚡ {gateway_name}", callback_data="none"),
        InlineKeyboardButton("🛑 STOP", callback_data=f"stop_{stop_flag_key}")
    )
    
    start_text = f"""Wait for processing
by → @s3s_a"""
    
    try:
        bot.edit_message_text(start_text, chat_id, message_id, reply_markup=kb_start)
    except:
        status_msg = bot.send_message(chat_id, start_text, reply_markup=kb_start)
        message_id = status_msg.message_id
    
    # بدء الفحص
    for i, card in enumerate(cards, 1):
        if stop_check_flags.get(stop_flag_key, False):
            update_display()
            bot.send_message(chat_id, "🛑 تم إيقاف الفحص")
            break
        
        current_card = card
        
        try:
            start_time = time.time()
            result = str(gateway_func(card))
            exec_time = time.time() - start_time
            current_status = f"{result[:40]} | {exec_time:.1f}s"
            
            # التحقق من خطأ في البوابة
            if is_gateway_error(result):
                consecutive_errors += 1
                if consecutive_errors >= 5:
                    bot.send_message(chat_id, f"⚠️ تم اكتشاف 5 أخطاء متتالية في البوابة {gateway_name}\n🛑 تم إيقاف الفحص تلقائياً")
                    stop_check_flags[stop_flag_key] = True
                    break
            else:
                consecutive_errors = 0
            
            if "Approved" in result or "✅" in result:
                approved += 1
                # إرسال البطاقة الناجحة فوراً
                msg = format_approved_result(gateway_name, card, result, exec_time)
                bot.send_message(user_id, msg, parse_mode='HTML')
                update_stats(user_id, True)
            else:
                declined += 1
                update_stats(user_id, False)
            
            # تحديث الواجهة
            update_display()
            time.sleep(2)
            
        except Exception as e:
            current_status = f"خطأ: {str(e)[:30]}"
            declined += 1
            update_display()
            time.sleep(1)
    
    # واجهة النهاية
    final_kb = InlineKeyboardMarkup(row_width=1)
    final_kb.add(
        InlineKeyboardButton(f"✅ APPROVED → [{approved}]", callback_data="none"),
        InlineKeyboardButton(f"❌ DECLINED → [{declined}]", callback_data="none"),
        InlineKeyboardButton(f"📊 TOTAL → [{total}]", callback_data="none"),
        InlineKeyboardButton("📋 اكتمل الفحص", callback_data="none")
    )
    
    final_text = f"""Wait for processing
by → @s3s_a

✅ Scan Completed
━━━━━━━━━━━━━━━
✅ APPROVED → [{approved}]
❌ DECLINED → [{declined}]
📊 TOTAL → [{total}]
━━━━━━━━━━━━━━━"""
    
    try:
        bot.edit_message_text(final_text, chat_id, message_id, reply_markup=final_kb)
    except:
        bot.send_message(chat_id, final_text, reply_markup=final_kb)
    
    # تنظيف
    if stop_flag_key in stop_check_flags:
        del stop_check_flags[stop_flag_key]
    if user_id in current_checks:
        del current_checks[user_id]

# ==================== القائمة الرئيسية بالصورة ====================
def send_main_menu(chat_id, message_id=None):
    """إرسال القائمة الرئيسية مع الصورة"""
    # أزرار تفاعلية
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💳 فحص", callback_data="check_menu"),
        InlineKeyboardButton("🎲 توليد فيزات", callback_data="gen_menu")
    )
    kb.add(
        InlineKeyboardButton("🔍 فحص بين", callback_data="bin_menu"),
        InlineKeyboardButton("📄 توليد بيانات شحن", callback_data="fake_menu")
    )
    kb.add(
        InlineKeyboardButton("❓ المساعدة", callback_data="help_menu")
    )
    
    # محاولة إرسال الصورة
    try:
        with open("start.jpg", "rb") as photo:
            # حذف الرسالة القديمة إذا وجدت
            if message_id:
                try:
                    bot.delete_message(chat_id, message_id)
                except:
                    pass
            bot.send_photo(chat_id, photo, caption="✨ <b>مرحباً بك في بوت الفحص</b>\n\n📌 اختر الخدمة من القائمة أدناه", reply_markup=kb, parse_mode='HTML')
    except:
        # إذا لم توجد الصورة
        if message_id:
            try:
                bot.edit_message_text("✨ <b>مرحباً بك في بوت الفحص</b>\n\n📌 اختر الخدمة من القائمة أدناه", chat_id, message_id, reply_markup=kb, parse_mode='HTML')
            except:
                bot.send_message(chat_id, "✨ <b>مرحباً بك في بوت الفحص</b>\n\n📌 اختر الخدمة من القائمة أدناه", reply_markup=kb, parse_mode='HTML')
        else:
            bot.send_message(chat_id, "✨ <b>مرحباً بك في بوت الفحص</b>\n\n📌 اختر الخدمة من القائمة أدناه", reply_markup=kb, parse_mode='HTML')

# ===================== قوائم الأزرار ====================
def get_check_menu():
    """قائمة أوامر الفحص (نص عادي)"""
    return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 <b>أوامر الفحص الفردي</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💳 Stripe Gateways (Auth):</b>

/str1 xxxxxxxxxxxxxxxx|xx|xx|xxx
/str2 xxxxxxxxxxxxxxxx|xx|xx|xxx
/str3 xxxxxxxxxxxxxxxx|xx|xx|xxx
/str4 xxxxxxxxxxxxxxxx|xx|xx|xxx
/str5 xxxxxxxxxxxxxxxx|xx|xx|xxx
/str6 xxxxxxxxxxxxxxxx|xx|xx|xxx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🔷 Braintree Gateways (Auth):</b>

/br1 xxxxxxxxxxxxxxxx|xx|xx|xxx
/br2 xxxxxxxxxxxxxxxx|xx|xx|xxx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>⚡ Charge Gateways (LIVE - $1 Deduct):</b>

/live1 xxxxxxxxxxxxxxxx|xx|xx|xxx
/live2 xxxxxxxxxxxxxxxx|xx|xx|xxx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💝 Donation Gateways:</b>

/donate xxxxxxxxxxxxxxxx|xx|xx|xxx
/chb xxxxxxxxxxxxxxxx|xx|xx|xxx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 <b>ملاحظة:</b> 
• LIVE = تم خصم المبلغ بنجاح
• APPROVED = بطاقة صالحة (رصيد غير كافي)
• DECLINED = بطاقة مرفوضة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def get_file_gateways_menu():
    """قائمة بوابات فحص الملفات"""
    kb = InlineKeyboardMarkup(row_width=2)
    gateways = [
        ("Stripe 1", "file_str1"), ("Stripe 2", "file_str2"),
        ("Stripe 3", "file_str3"), ("Stripe 4", "file_str4"),
        ("Stripe 5", "file_str5"), ("Stripe 6", "file_str6"),
        ("Braintree 1", "file_br1"), ("Braintree 2", "file_br2"),
        ("Braintree Charge", "file_chb"), ("Donate", "file_donate"),
        ("LIVE $1", "file_live1"), ("LIVE $1 (USDT)", "file_live2")
    ]
    for name, callback in gateways:
        kb.add(InlineKeyboardButton(name, callback_data=callback))
    kb.add(InlineKeyboardButton("🔙 رجوع", callback_data="check_menu"))
    return kb

def get_mass_gateways_menu():
    """قائمة بوابات الفحص الجماعي"""
    kb = InlineKeyboardMarkup(row_width=2)
    gateways = [
        ("Stripe 1", "mass_str1"), ("Stripe 2", "mass_str2"),
        ("Stripe 3", "mass_str3"), ("Stripe 4", "mass_str4"),
        ("Stripe 5", "mass_str5"), ("Stripe 6", "mass_str6"),
        ("Braintree 1", "mass_br1"), ("Braintree 2", "mass_br2"),
        ("Braintree Charge", "mass_chb"), ("Donate", "mass_donate"),
        ("LIVE $1", "mass_live1"), ("LIVE $1 (USDT)", "mass_live2")
    ]
    for name, callback in gateways:
        kb.add(InlineKeyboardButton(name, callback_data=callback))
    kb.add(InlineKeyboardButton("🔙 رجوع", callback_data="check_menu"))
    return kb

def get_gen_menu():
    """قائمة توليد البطاقات (3 أزرار)"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🎲 بين واحد", callback_data="gen_single"),
        InlineKeyboardButton("📚 بينات متعددة", callback_data="gen_multi"),
        InlineKeyboardButton("🎭 نمط x", callback_data="gen_pattern"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return kb

def get_fake_country_menu():
    """قائمة دول توليد بيانات الشحن"""
    kb = InlineKeyboardMarkup(row_width=2)
    countries = ["USA", "UK", "Canada", "Germany", "France", "Italy"]
    for country in countries:
        kb.add(InlineKeyboardButton(country, callback_data=f"fake_{country}"))
    kb.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb

# ===================== دوال توليد ====================
def generate_cards(bin_input, count):
    """توليد بطاقات بعدد محدد"""
    import string
    cards = []
    
    def luhn_checksum(num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return (checksum * 9) % 10
    
    bin_prefix = bin_input[:6] if len(bin_input) >= 6 else bin_input
    card_length = 15 if bin_prefix.startswith('3') else 16
    
    for _ in range(count):
        remaining = card_length - len(bin_prefix)
        if remaining > 0:
            random_digits = ''.join(random.choices(string.digits, k=remaining))
            card_num = bin_prefix + random_digits
        else:
            card_num = bin_prefix[:card_length]
        card_num = card_num[:-1] + str(luhn_checksum(card_num[:-1]))
        month = str(random.randint(1, 12)).zfill(2)
        year = str(random.randint(2026, 2031))
        cvv = ''.join(random.choices(string.digits, k=3))
        cards.append(f"{card_num}|{month}|{year}|{cvv}")
    return cards


def process_single_bin(message):
    """معالجة بين واحد مع اختيار العدد"""
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    
    bin_input = message.text.strip()
    if not bin_input or not bin_input[:6].isdigit():
        bot.reply_to(message, "❌ يرجى إدخال BIN صحيح (6-8 أرقام)")
        return
    
    kb = InlineKeyboardMarkup(row_width=3)
    for count in [5, 10, 20, 50, 100, 200]:
        kb.add(InlineKeyboardButton(str(count), callback_data=f"gen_count_{bin_input}_{count}"))
    bot.reply_to(message, f"🎲 اختر عدد البطاقات لـ BIN {bin_input[:6]}:", reply_markup=kb)

def process_multi_bin(message):
    """معالجة بينات متعددة"""
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    
    bins_text = message.text.strip()
    bins = [b.strip() for b in bins_text.split('\n') if b.strip()]
    valid_bins = [b for b in bins if b[:6].isdigit()]
    
    if not valid_bins:
        bot.reply_to(message, "❌ لم يتم العثور على بينات صالحة")
        return
    
    kb = InlineKeyboardMarkup(row_width=3)
    for count in [3, 5, 10, 20]:
        kb.add(InlineKeyboardButton(f"{count} بطاقة لكل بين", callback_data=f"gen_multi_count_{count}_{','.join(valid_bins)}"))
    bot.reply_to(message, f"📚 اختر عدد البطاقات لكل بين من {len(valid_bins)} بين:", reply_markup=kb)

def process_pattern(message):
    """معالجة نمط x"""
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    
    pattern = message.text.strip()
    if '|' not in pattern:
        bot.reply_to(message, "❌ صيغة غير صحيحة\nمثال: 410621xxxx|12|29|xxx")
        return
    
    try:
        parts = pattern.split('|')
        bin_pattern = parts[0].strip()
        month = parts[1].strip().lower()
        year = parts[2].strip().lower()
        cvv_pattern = parts[3].strip().lower()
        
        bin_base = bin_pattern.lower().replace('x', '')
        card_length = 15 if bin_base.startswith('3') else 16
        x_count = bin_pattern.lower().count('x')
        remaining = card_length - len(bin_base)
        
        if x_count == 0:
            count = 1
        elif x_count <= 2:
            count = 10
        elif x_count <= 4:
            count = 20
        else:
            count = 50
        
        cards = []
        for _ in range(min(count, 100)):
            if x_count > 0:
                random_digits = ''.join(random.choices('0123456789', k=remaining))
                card_num = bin_base + random_digits
            else:
                card_num = bin_base
            
            def luhn_checksum(num):
                digits = [int(d) for d in str(num)]
                odd_sum = sum(digits[-1::-2])
                even_sum = sum(sum(divmod(2*d, 10)) for d in digits[-2::-2])
                return (odd_sum + even_sum) % 10
            
            card_num = card_num[:-1] + str(luhn_checksum(card_num[:-1]))
            
            if month == 'xx':
                m = str(random.randint(1, 12)).zfill(2)
            else:
                m = month.zfill(2)
            
            if year == 'xx':
                y = str(random.randint(2026, 2031))
            elif len(year) == 2:
                y = f"20{year}"
            else:
                y = year
            
            if cvv_pattern.lower() == 'xxx':
                cvv = ''.join(random.choices('0123456789', k=3))
            else:
                cvv = cvv_pattern
            
            cards.append(f"{card_num}|{m}|{y}|{cvv}")
        
        if cards:
            msg = f"🎴 <b>تم توليد {len(cards)} بطاقة حسب النمط</b>\n\n" + "\n".join([f"<code>{c}</code>" for c in cards])
            bot.reply_to(message, msg, parse_mode='HTML')
        else:
            bot.reply_to(message, "❌ فشل التوليد")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)[:100]}")


def generate_fake_info(country):
    """توليد بيانات شحن وهمية"""
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
    return f"""🌍 <b>بيانات شحن - {country}</b>
━━━━━━━━━━━━━━━
👤 الاسم: {name}
📧 البريد: {email}
🏠 العنوان: {address}
🌆 المدينة: {city}
📍 الولاية: {state}
📮 الرمز البريدي: {zipcode}
📞 الهاتف: {phone}
━━━━━━━━━━━━━━━
Dev ➜ @s3s_a"""

# ==================== أوامر البوت ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    get_user(user_id, username, first_name)
    send_main_menu(message.chat.id)

@bot.message_handler(commands=['str1'])
def cmd_str1(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/str1', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /str1 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, Stripe1, "Stripe 1")

@bot.message_handler(commands=['str2'])
def cmd_str2(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/str2', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /str2 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, Stripe2, "Stripe 2")

@bot.message_handler(commands=['str3'])
def cmd_str3(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/str3', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /str3 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, Stripe3, "Stripe 3")

@bot.message_handler(commands=['str4'])
def cmd_str4(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/str4', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /str4 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, Stripe4, "Stripe 4")

@bot.message_handler(commands=['str5'])
def cmd_str5(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/str5', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /str5 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, Stripe5, "Stripe 5")

@bot.message_handler(commands=['str6'])
def cmd_str6(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/str6', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /str6 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, Stripe6, "Stripe 6")

@bot.message_handler(commands=['br1'])
def cmd_br1(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/br1', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /br1 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, bra1, "Braintree 1")

@bot.message_handler(commands=['br2'])
def cmd_br2(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/br2', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /br2 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, bra2, "Braintree 2")

@bot.message_handler(commands=['chb'])
def cmd_chb(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/chb', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /chb رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, BraC, "Braintree Charge")

@bot.message_handler(commands=['live1'])
def cmd_live1(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/live1', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /live1 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, charge1usd, "LIVE $1")

@bot.message_handler(commands=['live2'])
def cmd_live2(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/live2', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /live2 رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, charge1usdt, "LIVE $1 (USDT)")

@bot.message_handler(commands=['donate'])
def cmd_donate(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    card = message.text.replace('/donate', '').strip()
    if not card:
        bot.reply_to(message, "⚠️ /donate رقم|شهر|سنة|cvv")
        return
    check_single_card(message, card, Donate, "Donate")

@bot.message_handler(commands=['gen'])
def gen_command(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ /gen <الـ BIN>\nمثال: /gen 528445")
        return
    bin_input = parts[1].strip()
    if not bin_input[:6].isdigit():
        bot.reply_to(message, "⚠️ يرجى إدخال BIN صحيح (6-8 أرقام)")
        return
    
    # إرسال أزرار اختيار العدد
    kb = InlineKeyboardMarkup(row_width=3)
    for count in [5, 10, 20, 50, 100, 200]:
        kb.add(InlineKeyboardButton(str(count), callback_data=f"gen_count_{bin_input}_{count}"))
    bot.reply_to(message, f"🎲 اختر عدد البطاقات لـ BIN {bin_input[:6]}:", reply_markup=kb)

@bot.message_handler(commands=['bin'])
def bin_command(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ /bin <الـ BIN>\nمثال: /bin 528445")
        return
    bin_code = parts[1][:6]
    info = get_bin_info(bin_code)
    bot.reply_to(message, info, parse_mode='HTML')

@bot.message_handler(commands=['fk'])
def fake_command(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    parts = message.text.split()
    country = parts[1].capitalize() if len(parts) > 1 else "USA"
    info = generate_fake_info(country)
    bot.reply_to(message, info, parse_mode='HTML')

@bot.message_handler(commands=['mass'])
def mass_command(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ قم بالرد على رسالة تحتوي على بطاقات\nمثال: رد على رسالة البطاقات ثم /mass")
        return
    
    cards = extract_cards_from_message(message.reply_to_message.text)
    if not cards:
        bot.reply_to(message, "❌ لم يتم العثور على بطاقات صالحة في الرسالة")
        return
    
    pending_mass_cards[message.from_user.id] = cards
    bot.reply_to(message, f"📊 تم العثور على {len(cards)} بطاقة\n🗂️ اختر البوابة:", reply_markup=get_mass_gateways_menu())

@bot.message_handler(content_types=['document'])
def handle_file(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        filename = f"combo_{message.from_user.id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        
        with open(filename, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
            card_count = len(lines)
        
        pending_mass_cards[message.from_user.id] = lines
        bot.reply_to(message, f"📁 تم رفع {card_count} بطاقة\n🗂️ اختر البوابة:", reply_markup=get_file_gateways_menu())
        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)[:100]}")

# ==================== أوامر الأدمن ====================
@bot.message_handler(commands=['users'])
def users_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = "📊 <b>قائمة المستخدمين</b>\n━━━━━━━━━━━━━━━\n"
    for uid, data in users_data.items():
        msg += f"👤 {data['name']}\n🆔 {uid}\n📛 @{data['username'] or 'لا يوجد'}\n✅ {data['approved_checks']} | 📊 {data['total_checks']}\n━━━━━━━━━━━━━━━\n"
    bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['ban'])
def ban_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = message.text.split()[1]
        if user_id in users_data:
            users_data[user_id]["banned"] = True
            save_users(users_data)
            bot.reply_to(message, f"✅ تم حظر المستخدم {user_id}")
            bot.send_message(int(user_id), "🚫 تم حظر حسابك من البوت")
    except:
        bot.reply_to(message, "❌ /ban <user_id>")

@bot.message_handler(commands=['unban'])
def unban_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = message.text.split()[1]
        if user_id in users_data:
            users_data[user_id]["banned"] = False
            save_users(users_data)
            bot.reply_to(message, f"✅ تم فك الحظر عن المستخدم {user_id}")
            bot.send_message(int(user_id), "✅ تم فك الحظر عن حسابك")
    except:
        bot.reply_to(message, "❌ /unban <user_id>")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    total_users = len(users_data)
    total_checks = sum(u.get("total_checks", 0) for u in users_data.values())
    total_approved = sum(u.get("approved_checks", 0) for u in users_data.values())
    banned_users = sum(1 for u in users_data.values() if u.get("banned", False))
    stats = f"""📊 <b>إحصائيات البوت</b>
━━━━━━━━━━━━━━━
👥 المستخدمين: {total_users}
🚫 محظورين: {banned_users}
━━━━━━━━━━━━━━━
💳 إجمالي الفحوصات: {total_checks}
✅ المقبولة: {total_approved}
📈 نسبة النجاح: {(total_approved/total_checks*100) if total_checks > 0 else 0:.1f}%
━━━━━━━━━━━━━━━
Dev ➜ @s3s_a"""
    bot.reply_to(message, stats, parse_mode='HTML')

# ==================== معالج الأزرار ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    
    if data.startswith("copy_"):
        commands = {
            "copy_str1": "/str1 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_str2": "/str2 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_str3": "/str3 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_str4": "/str4 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_str5": "/str5 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_str6": "/str6 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_br1": "/br1 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_br2": "/br2 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_chb": "/chb xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_donate": "/donate xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_live1": "/live1 xxxxxxxxxxxxxxxx|xx|xx|xxx",
            "copy_live2": "/live2 xxxxxxxxxxxxxxxx|xx|xx|xxx",
        }
        if data in commands:
            bot.answer_callback_query(call.id, commands[data], show_alert=True)
        return
    
    if data == "back_main":
        send_main_menu(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    elif data == "check_menu":
        check_text = get_check_menu()
        try:
            bot.edit_message_text(check_text, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        except:
            bot.send_message(call.message.chat.id, check_text, parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    elif data == "gen_menu":
        try:
            bot.edit_message_text("🎲 <b>اختر طريقة التوليد</b>", call.message.chat.id, call.message.message_id, reply_markup=get_gen_menu())
        except:
            bot.send_message(call.message.chat.id, "🎲 <b>اختر طريقة التوليد</b>", reply_markup=get_gen_menu())
        bot.answer_callback_query(call.id)
        return
    
    elif data == "bin_menu":
        try:
            bot.edit_message_text("🔍 أرسل الـ BIN\nمثال: <code>/bin 528445</code>", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        except:
            bot.send_message(call.message.chat.id, "🔍 أرسل الـ BIN\nمثال: <code>/bin 528445</code>", parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    elif data == "fake_menu":
        try:
            bot.edit_message_text("🌍 <b>اختر الدولة</b>", call.message.chat.id, call.message.message_id, reply_markup=get_fake_country_menu())
        except:
            bot.send_message(call.message.chat.id, "🌍 <b>اختر الدولة</b>", reply_markup=get_fake_country_menu())
        bot.answer_callback_query(call.id)
        return
    
    elif data == "help_menu":
        help_text = """❓ <b>دليل استخدام البوت</b>
━━━━━━━━━━━━━━━
💳 أوامر الفحص: /str1 إلى /str6, /br1, /br2, /chb, /donate, /live1, /live2
📁 فحص الملفات: أرسل ملف txt
📊 الفحص الجماعي: رد على رسالة البطاقات بـ /mass
🎲 التوليد: /gen 528445
🔍 فحص BIN: /bin 528445
📄 بيانات شحن: /fk USA
━━━━━━━━━━━━━━━
Dev ➜ @s3s_a"""
        try:
            bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 رجوع", callback_data="back_main")), parse_mode='HTML')
        except:
            bot.send_message(call.message.chat.id, help_text, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 رجوع", callback_data="back_main")), parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    elif data == "file_upload":
        try:
            bot.edit_message_text("📁 أرسل ملف <code>.txt</code>", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        except:
            bot.send_message(call.message.chat.id, "📁 أرسل ملف <code>.txt</code>", parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    elif data == "gen_single":
        try:
            bot.edit_message_text("🎲 أرسل الـ BIN (6-8 أرقام)\nمثال: 528445", call.message.chat.id, call.message.message_id)
        except:
            bot.send_message(call.message.chat.id, "🎲 أرسل الـ BIN (6-8 أرقام)\nمثال: 528445")
        bot.register_next_step_handler(call.message, process_single_bin)
        bot.answer_callback_query(call.id)
        return
    
    elif data == "gen_multi":
        try:
            bot.edit_message_text("📚 أرسل البينات كل بين في سطر\nمثال:\n528445\n518928\n410621", call.message.chat.id, call.message.message_id)
        except:
            bot.send_message(call.message.chat.id, "📚 أرسل البينات كل بين في سطر\nمثال:\n528445\n518928\n410621")
        bot.register_next_step_handler(call.message, process_multi_bin)
        bot.answer_callback_query(call.id)
        return
    
    elif data == "gen_pattern":
        try:
            bot.edit_message_text("🎭 أرسل النمط\nمثال: 410621xxxx|12|29|xxx", call.message.chat.id, call.message.message_id)
        except:
            bot.send_message(call.message.chat.id, "🎭 أرسل النمط\nمثال: 410621xxxx|12|29|xxx")
        bot.register_next_step_handler(call.message, process_pattern)
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("gen_count_"):
        parts = data.replace("gen_count_", "").split("_")
        bin_input = parts[0]
        count = int(parts[1])
        cards = generate_cards(bin_input, count)
        if cards:
            msg = "🎴 <b>تم توليد " + str(len(cards)) + " بطاقة</b>\n\n" + "\n".join([f"<code>{c}</code>" for c in cards])
            try:
                bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
            except:
                bot.send_message(call.message.chat.id, msg, parse_mode='HTML')
        else:
            try:
                bot.edit_message_text("❌ فشل التوليد", call.message.chat.id, call.message.message_id)
            except:
                bot.send_message(call.message.chat.id, "❌ فشل التوليد")
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("gen_multi_count_"):
        parts = data.replace("gen_multi_count_", "").split("_")
        count = int(parts[0])
        bins = parts[1].split(',')
        all_cards = []
        for bin_prefix in bins:
            cards = generate_cards(bin_prefix[:6], count)
            all_cards.extend(cards)
        if all_cards:
            msg = "🎴 <b>تم توليد " + str(len(all_cards)) + " بطاقة</b>\n\n" + "\n".join([f"<code>{c}</code>" for c in all_cards[:50]])
            if len(all_cards) > 50:
                msg += f"\n\n... و {len(all_cards) - 50} بطاقة أخرى"
            try:
                bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
            except:
                bot.send_message(call.message.chat.id, msg, parse_mode='HTML')
        else:
            try:
                bot.edit_message_text("❌ فشل التوليد", call.message.chat.id, call.message.message_id)
            except:
                bot.send_message(call.message.chat.id, "❌ فشل التوليد")
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("fake_"):
        country = data.replace("fake_", "")
        info = generate_fake_info(country)
        try:
            bot.edit_message_text(info, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        except:
            bot.send_message(call.message.chat.id, info, parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("file_"):
        if user_id not in pending_mass_cards:
            bot.answer_callback_query(call.id, "❌ لم يتم العثور على بطاقات", show_alert=True)
            return
        cards = pending_mass_cards[user_id]
        stop_key = f"{user_id}_{int(time.time())}"
        stop_check_flags[stop_key] = False
        current_checks[user_id] = stop_key
        gateways = {
            "file_str1": (Stripe1, "Stripe 1"), "file_str2": (Stripe2, "Stripe 2"),
            "file_str3": (Stripe3, "Stripe 3"), "file_str4": (Stripe4, "Stripe 4"),
            "file_str5": (Stripe5, "Stripe 5"), "file_str6": (Stripe6, "Stripe 6"),
            "file_br1": (bra1, "Braintree 1"), "file_br2": (bra2, "Braintree 2"),
            "file_chb": (BraC, "Braintree Charge"), "file_donate": (Donate, "Donate"),
            "file_live1": (charge1usd, "LIVE $1"), "file_live2": (charge1usdt, "LIVE $1 (USDT)")
        }
        if data in gateways:
            gateway_func, gateway_name = gateways[data]
            try:
                bot.edit_message_text(f"⏳ بدء فحص {len(cards)} بطاقة على {gateway_name}...", call.message.chat.id, call.message.message_id)
            except:
                bot.send_message(call.message.chat.id, f"⏳ بدء فحص {len(cards)} بطاقة على {gateway_name}...")
            threading.Thread(target=check_mass_cards, args=(user_id, call.message.chat.id, cards, gateway_func, gateway_name, call.message.message_id, stop_key)).start()
            del pending_mass_cards[user_id]
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("mass_"):
        if user_id not in pending_mass_cards:
            bot.answer_callback_query(call.id, "❌ لم يتم العثور على بطاقات", show_alert=True)
            return
        cards = pending_mass_cards[user_id]
        stop_key = f"{user_id}_{int(time.time())}"
        stop_check_flags[stop_key] = False
        current_checks[user_id] = stop_key
        gateways = {
            "mass_str1": (Stripe1, "Stripe 1"), "mass_str2": (Stripe2, "Stripe 2"),
            "mass_str3": (Stripe3, "Stripe 3"), "mass_str4": (Stripe4, "Stripe 4"),
            "mass_str5": (Stripe5, "Stripe 5"), "mass_str6": (Stripe6, "Stripe 6"),
            "mass_br1": (bra1, "Braintree 1"), "mass_br2": (bra2, "Braintree 2"),
            "mass_chb": (BraC, "Braintree Charge"), "mass_donate": (Donate, "Donate"),
            "mass_live1": (charge1usd, "LIVE $1"), "mass_live2": (charge1usdt, "LIVE $1 (USDT)")
        }
        if data in gateways:
            gateway_func, gateway_name = gateways[data]
            try:
                bot.edit_message_text(f"⏳ بدء فحص {len(cards)} بطاقة على {gateway_name}...", call.message.chat.id, call.message.message_id)
            except:
                bot.send_message(call.message.chat.id, f"⏳ بدء فحص {len(cards)} بطاقة على {gateway_name}...")
            threading.Thread(target=check_mass_cards, args=(user_id, call.message.chat.id, cards, gateway_func, gateway_name, call.message.message_id, stop_key)).start()
            del pending_mass_cards[user_id]
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("stop_"):
        stop_key = data.replace("stop_", "")
        if stop_key in stop_check_flags:
            stop_check_flags[stop_key] = True
            bot.answer_callback_query(call.id, "🛑 جاري إيقاف الفحص...")
        else:
            bot.answer_callback_query(call.id, "❌ لا يوجد فحص نشط")
        return
    
    elif data == "none":
        bot.answer_callback_query(call.id)
        return
    
    elif data == "help_menu":
        help_text = """❓ <b>دليل استخدام البوت</b>
━━━━━━━━━━━━━━━

💳 <b>أوامر الفحص الفردي:</b>
/str1, /str2, /str3, /str4, /str5, /str6
/br1, /br2, /chb, /donate

📁 <b>فحص الملفات:</b>
أرسل ملف txt ثم اختر البوابة

📊 <b>الفحص الجماعي:</b>
رد على رسالة البطاقات بـ /mass

🎲 <b>توليد فيزات:</b>
/gen 528445

🔍 <b>فحص BIN:</b>
/bin 528445

📄 <b>توليد بيانات شحن:</b>
/fk USA

━━━━━━━━━━━━━━━
Dev ➜ @s3s_a"""
        try:
            bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, 
                                  reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 رجوع", callback_data="back_main")), 
                                  parse_mode='HTML')
        except:
            bot.send_message(call.message.chat.id, help_text, 
                             reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 رجوع", callback_data="back_main")), 
                             parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    elif data == "file_upload":
        try:
            bot.edit_message_text("📁 أرسل ملف <code>.txt</code>\nكل سطر يحتوي على بطاقة بالصيغة:\n<code>رقم|شهر|سنة|cvv</code>", 
                                  call.message.chat.id, call.message.message_id, parse_mode='HTML')
        except:
            bot.send_message(call.message.chat.id, "📁 أرسل ملف <code>.txt</code>\nكل سطر يحتوي على بطاقة بالصيغة:\n<code>رقم|شهر|سنة|cvv</code>", parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    # فحص الملفات
    elif data.startswith("file_"):
        if user_id not in pending_mass_cards:
            bot.answer_callback_query(call.id, "❌ لم يتم العثور على بطاقات", show_alert=True)
            return
        
        cards = pending_mass_cards[user_id]
        stop_key = f"{user_id}_{int(time.time())}"
        stop_check_flags[stop_key] = False
        current_checks[user_id] = stop_key
        
        gateways = {
            "file_str1": (Stripe1, "Stripe 1"), "file_str2": (Stripe2, "Stripe 2"),
            "file_str3": (Stripe3, "Stripe 3"), "file_str4": (Stripe4, "Stripe 4"),
            "file_str5": (Stripe5, "Stripe 5"), "file_str6": (Stripe6, "Stripe 6"),
            "file_br1": (bra1, "Braintree 1"), "file_br2": (bra2, "Braintree 2"),
            "file_chb": (BraC, "Braintree Charge"), "file_donate": (Donate, "Donate")
        }
        
        if data in gateways:
            gateway_func, gateway_name = gateways[data]
            try:
                bot.edit_message_text(f"⏳ بدء فحص {len(cards)} بطاقة على {gateway_name}...", 
                                      call.message.chat.id, call.message.message_id)
            except:
                bot.send_message(call.message.chat.id, f"⏳ بدء فحص {len(cards)} بطاقة على {gateway_name}...")
            threading.Thread(target=check_mass_cards, args=(user_id, call.message.chat.id, cards, gateway_func, gateway_name, call.message.message_id, stop_key)).start()
            del pending_mass_cards[user_id]
        bot.answer_callback_query(call.id)
        return
    
    # الفحص الجماعي (رد على الرسائل)
    elif data.startswith("mass_"):
        if user_id not in pending_mass_cards:
            bot.answer_callback_query(call.id, "❌ لم يتم العثور على بطاقات", show_alert=True)
            return
        
        cards = pending_mass_cards[user_id]
        stop_key = f"{user_id}_{int(time.time())}"
        stop_check_flags[stop_key] = False
        current_checks[user_id] = stop_key
        
        gateways = {
            "mass_str1": (Stripe1, "Stripe 1"), "mass_str2": (Stripe2, "Stripe 2"),
            "mass_str3": (Stripe3, "Stripe 3"), "mass_str4": (Stripe4, "Stripe 4"),
            "mass_str5": (Stripe5, "Stripe 5"), "mass_str6": (Stripe6, "Stripe 6"),
            "mass_br1": (bra1, "Braintree 1"), "mass_br2": (bra2, "Braintree 2"),
            "mass_chb": (BraC, "Braintree Charge"), "mass_donate": (Donate, "Donate")
        }
        
        if data in gateways:
            gateway_func, gateway_name = gateways[data]
            try:
                bot.edit_message_text(f"⏳ بدء فحص {len(cards)} بطاقة على {gateway_name}...", 
                                      call.message.chat.id, call.message.message_id)
            except:
                bot.send_message(call.message.chat.id, f"⏳ بدء فحص {len(cards)} بطاقة على {gateway_name}...")
            threading.Thread(target=check_mass_cards, args=(user_id, call.message.chat.id, cards, gateway_func, gateway_name, call.message.message_id, stop_key)).start()
            del pending_mass_cards[user_id]
        bot.answer_callback_query(call.id)
        return
    
    # إيقاف الفحص
    elif data.startswith("stop_"):
        stop_key = data.replace("stop_", "")
        if stop_key in stop_check_flags:
            stop_check_flags[stop_key] = True
            bot.answer_callback_query(call.id, "🛑 جاري إيقاف الفحص...")
        else:
            bot.answer_callback_query(call.id, "❌ لا يوجد فحص نشط")
        return
    
    # توليد البطاقات
    elif data.startswith("gen_count_"):
        count = int(data.replace("gen_count_", ""))
        try:
            bot.edit_message_text("🎲 أرسل الـ BIN (6-8 أرقام)", 
                                  call.message.chat.id, call.message.message_id)
        except:
            bot.send_message(call.message.chat.id, "🎲 أرسل الـ BIN (6-8 أرقام)")
        bot.register_next_step_handler(call.message, lambda m: process_gen(m, count))
        bot.answer_callback_query(call.id)
        return
    
    # توليد بيانات شحن
    elif data.startswith("fake_"):
        country = data.replace("fake_", "")
        info = generate_fake_info(country)
        try:
            bot.edit_message_text(info, call.message.chat.id, call.message.message_id, parse_mode='HTML')
        except:
            bot.send_message(call.message.chat.id, info, parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    elif data == "none":
        bot.answer_callback_query(call.id)
        return

def process_gen(message, count):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "🚫 أنت محظور")
        return
    
    bin_input = message.text.strip()
    if not bin_input or not bin_input[:6].isdigit():
        bot.reply_to(message, "❌ يرجى إدخال BIN صحيح (6-8 أرقام)")
        return
    
    cards = generate_cards(bin_input, count)
    if cards:
        msg = f"🎴 <b>تم توليد {count} بطاقة من BIN {bin_input[:6]}</b>\n\n" + "\n".join([f"<code>{c}</code>" for c in cards])
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        bot.reply_to(message, "❌ فشل التوليد")

# ==================== تشغيل البوت ====================
if __name__ == "__main__":
    print("✅ البوت يعمل...")
    print(f"👥 عدد المستخدمين: {len(users_data)}")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True, timeout=20)