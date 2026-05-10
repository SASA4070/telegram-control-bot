import telebot
import time
import threading
from telebot import types
import requests
import random
import os
import re
from datetime import datetime
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

# ==================== توكن البوت ====================
token = '8490768092:AAF_GAGrBWUmY4u3NAFATaYwNJDKLjEViLQ'
bot = telebot.TeleBot(token, parse_mode="HTML")

# ==================== بيانات ====================
admin = 1489001988
stopuser = {}
command_usage = {}
user_file = {}
pending_gateway = {}

# ==================== دالة BIN ====================
def dato(zh):
	try:
		api_url = requests.get("https://bins.antipublic.cc/bins/"+zh, verify=False).json()
		brand = api_url["brand"]
		card_type = api_url["type"]
		level = api_url["level"]
		bank = api_url["bank"]
		country_name = api_url["country_name"]
		country_flag = api_url["country_flag"]
		mn = f'''[ϟ] 𝐁𝐢𝐧: <code>{brand} - {card_type} - {level}</code>
[ϟ] 𝐁𝐚𝐧𝐤: <code>{bank} - {country_flag}</code>
[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country_name} [ {country_flag} ]</code>'''
		return mn
	except:
		return 'No info'

# ==================== دالة BIN متطورة ====================
def check_bin_advanced(bin_code):
	bin_code = str(bin_code)[:6]
	try:
		url = f"https://bins.antipublic.cc/bins/{bin_code}"
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			return f"""🔍 **BIN CHECK** | antipublic
━━━━━━━━━━━━━━━━
💳 **BIN:** `{bin_code}`
🏷️ **Brand:** {d.get('brand', 'Unknown')}
📌 **Type:** {d.get('type', 'Unknown').upper()}
⭐ **Level:** {d.get('level', 'Unknown')}
🏦 **Bank:** {d.get('bank', 'Unknown')}
🌍 **Country:** {d.get('country_name', 'Unknown')} {d.get('country_flag', '')}"""
	except:
		pass
	try:
		url = f"https://lookup.binlist.net/{bin_code}"
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			bank = d.get('bank', {}).get('name', 'Unknown')
			country = d.get('country', {}).get('name', 'Unknown')
			flag = d.get('country', {}).get('emoji', '')
			return f"""🔍 **BIN CHECK** | binlist
━━━━━━━━━━━━━━━━
💳 **BIN:** `{bin_code}`
🏷️ **Brand:** {d.get('scheme', 'Unknown')}
📌 **Type:** {d.get('type', 'Unknown').upper()}
🏦 **Bank:** {bank}
🌍 **Country:** {country} {flag}"""
	except:
		pass
	return "⚠️ Could not fetch BIN info"

# ==================== دالة توليد بطاقات Luhn ====================
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

def generate_card_from_input(user_input, count=1):
	try:
		parts = user_input.split('|')
		if len(parts) != 4:
			return None
		card_pattern = parts[0].strip()
		month = parts[1].strip()
		year = parts[2].strip()
		cvv_pattern = parts[3].strip()
		match = re.match(r'^(\d+)(x+)$', card_pattern, re.IGNORECASE)
		if match:
			bin_part = match.group(1)
			random_needed = 16 - len(bin_part)
			if random_needed < 0:
				random_needed = 0
		else:
			bin_part = card_pattern
			random_needed = 16 - len(bin_part)
			if card_pattern.startswith('3'):
				random_needed = 15 - len(bin_part)
		cards = []
		for _ in range(count):
			if random_needed > 0:
				random_digits = ''.join(str(random.randint(0, 9)) for __ in range(random_needed))
				full_number = bin_part + random_digits
			else:
				full_number = bin_part[:16]
			final_number = full_number[:-1] + str(luhn_checksum(full_number[:-1]))
			if cvv_pattern.lower() in ['xxx', '***']:
				final_cvv = str(random.randint(100, 999))
			else:
				final_cvv = cvv_pattern
			cards.append(f"{final_number}|{month}|{year}|{final_cvv}")
		return cards
	except:
		return None

# ==================== دالة معلومات وهمية ====================
def get_fake_info(country):
	countries_data = {
		"USA": {"first": ["John","James","Robert"], "last":["Smith","Johnson","Williams"], "address":["6200 Phyllis Dr"], "city":["Cypress"], "state":["CA"], "zip":["90630"], "phone":["+15416450372"]},
		"UK": {"first":["James","David","John"], "last":["Smith","Jones","Taylor"], "address":["221 Baker St"], "city":["London"], "state":["London"], "zip":["NW1 6XE"], "phone":["+442079460958"]},
		"Canada": {"first":["Liam","Noah","William"], "last":["Smith","Brown","Tremblay"], "address":["123 Queen St"], "city":["Toronto"], "state":["ON"], "zip":["M5V 2T6"], "phone":["+14165551234"]},
		"Germany": {"first":["Max","Alexander","Paul"], "last":["Müller","Schmidt","Schneider"], "address":["Hauptstrasse 1"], "city":["Berlin"], "state":["Berlin"], "zip":["10115"], "phone":["+49301234567"]},
		"France": {"first":["Lucas","Louis","Jules"], "last":["Martin","Bernard","Dubois"], "address":["10 Rue de la Paix"], "city":["Paris"], "state":["Paris"], "zip":["75001"], "phone":["+33123456789"]},
		"Italy": {"first":["Leonardo","Francesco","Alessandro"], "last":["Rossi","Russo","Ferrari"], "address":["Via Roma 1"], "city":["Rome"], "state":["RM"], "zip":["00100"], "phone":["+39061234567"]},
		"Netherlands": {"first":["Daan","Sem","Lucas"], "last":["de Jong","Jansen","de Vries"], "address":["Damrak 1"], "city":["Amsterdam"], "state":["NH"], "zip":["1012AB"], "phone":["+31201234567"]},
		"India": {"first":["Aarav","Vihaan","Vivaan"], "last":["Kumar","Sharma","Singh"], "address":["MG Road 1"], "city":["Mumbai"], "state":["MH"], "zip":["400001"], "phone":["+91221234567"]},
		"Pakistan": {"first":["Muhammad","Ali","Hamza"], "last":["Khan","Malik","Butt"], "address":["Gulberg 1"], "city":["Karachi"], "state":["SD"], "zip":["74000"], "phone":["+92211234567"]},
		"China": {"first":["Wei","Ming","Li"], "last":["Wang","Li","Zhang"], "address":["Chang'an Avenue 1"], "city":["Beijing"], "state":["BJ"], "zip":["100000"], "phone":["+86101234567"]},
		"Russia": {"first":["Alexander","Dmitry","Maxim"], "last":["Ivanov","Smirnov","Kuznetsov"], "address":["Tverskaya Street 1"], "city":["Moscow"], "state":["MOW"], "zip":["101000"], "phone":["+74951234567"]},
		"Switzerland": {"first":["Liam","Noah","Luca"], "last":["Meier","Müller","Schmid"], "address":["Bahnhofstrasse 1"], "city":["Zurich"], "state":["ZH"], "zip":["8000"], "phone":["+41441234567"]},
		"South Korea": {"first":["Min-jun","Seo-jun","Ha-joon"], "last":["Kim","Lee","Park"], "address":["Gangnam-daero 1"], "city":["Seoul"], "state":["Seoul"], "zip":["04524"], "phone":["+82212345678"]},
		"Japan": {"first":["Haruto","Sota","Yuto"], "last":["Sato","Suzuki","Takahashi"], "address":["Shibuya 1-1-1"], "city":["Tokyo"], "state":["Tokyo"], "zip":["100-0001"], "phone":["+81312345678"]}
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
	return f"""🌍 **Fake Info - {country}**
━━━━━━━━━━━━━━━━
👤 **Name:** {name}
📧 **Email:** {email}
🏠 **Address:** {address}
🌆 **City:** {city}
📍 **State:** {state}
📮 **Postal:** {zipcode}
📞 **Phone:** {phone}
━━━━━━━━━━━━━━━━"""

# ==================== القوائم ====================
def main_menu():
	m = types.InlineKeyboardMarkup(row_width=2)
	m.add(
		types.InlineKeyboardButton("🔐 Card Checker", callback_data="menu_checker"),
		types.InlineKeyboardButton("🃏 Generator", callback_data="menu_generator"),
		types.InlineKeyboardButton("🔍 BIN Checker", callback_data="menu_bin"),
		types.InlineKeyboardButton("🆔 Fake Info", callback_data="menu_fake")
	)
	return m

def checker_menu():
	m = types.InlineKeyboardMarkup(row_width=2)
	m.add(
		types.InlineKeyboardButton("💰 Stripe", callback_data="stripe_menu"),
		types.InlineKeyboardButton("💳 Braintree", callback_data="braintree_menu"),
		types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
	)
	return m

def stripe_list():
	m = types.InlineKeyboardMarkup(row_width=2)
	for name, code in [("Stripe1","st1"),("Stripe2","st2"),("Stripe3","st3"),("Stripe4","st4"),("Stripe5","st5"),("Stripe6","st6"),("Donate","donate")]:
		m.add(types.InlineKeyboardButton(name, callback_data=f"gw_{code}"))
	m.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_checker"))
	return m

def braintree_list():
	m = types.InlineKeyboardMarkup(row_width=2)
	for name, code in [("Braintree1","br1"),("Braintree2","br2"),("BraintreeCharge","chk1")]:
		m.add(types.InlineKeyboardButton(name, callback_data=f"gw_{code}"))
	m.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_checker"))
	return m

def combo_type_menu():
	m = types.InlineKeyboardMarkup(row_width=2)
	m.add(
		types.InlineKeyboardButton("💰 Stripe", callback_data="combo_stripe"),
		types.InlineKeyboardButton("💳 Braintree", callback_data="combo_braintree"),
		types.InlineKeyboardButton("❌ Cancel", callback_data="combo_cancel")
	)
	return m

# ==================== الأوامر ====================
@bot.message_handler(commands=["start"])
def handle_start(message):
	sent_message = bot.send_message(chat_id=message.chat.id, text="💥 Starting...")
	time.sleep(1)
	name = message.from_user.first_name
	bot.edit_message_text(
		chat_id=message.chat.id,
		message_id=sent_message.message_id,
		text=f"Hi {name}, Welcome To Auth Checker",
		reply_markup=main_menu()
	)

# ==================== معالج القائمة ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_menu(call):
	data = call.data
	
	if data == "menu_checker":
		bot.edit_message_text("Select gateway type:", call.message.chat.id, call.message.message_id, reply_markup=checker_menu())
	elif data == "menu_generator":
		bot.send_message(call.message.chat.id, "🃏 Send pattern: `410621xxxx|12|29|xxx`\nThen number (default 10)", parse_mode="Markdown")
		bot.answer_callback_query(call.id)
	elif data == "menu_bin":
		bot.send_message(call.message.chat.id, "🔍 Send BIN: `410621`")
		bot.answer_callback_query(call.id)
	elif data == "menu_fake":
		bot.send_message(call.message.chat.id, "🆔 Send country: USA, UK, Canada, Germany, France, Italy, Netherlands, India, Pakistan, China, Russia, Switzerland, South Korea, Japan")
		bot.answer_callback_query(call.id)
	elif data == "back_main":
		bot.edit_message_text("✨ Choose option:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
	elif data == "back_checker":
		bot.edit_message_text("Select gateway type:", call.message.chat.id, call.message.message_id, reply_markup=checker_menu())
	elif data == "stripe_menu":
		bot.edit_message_text("Select Stripe:", call.message.chat.id, call.message.message_id, reply_markup=stripe_list())
	elif data == "braintree_menu":
		bot.edit_message_text("Select Braintree:", call.message.chat.id, call.message.message_id, reply_markup=braintree_list())
	elif data.startswith("gw_"):
		gw = data.replace("gw_", "")
		names = {"st1":"Stripe1","st2":"Stripe2","st3":"Stripe3","st4":"Stripe4","st5":"Stripe5","st6":"Stripe6","donate":"Donate","br1":"Braintree1","br2":"Braintree2","chk1":"BraintreeCharge"}
		bot.send_message(call.message.chat.id, f"📇 Send card for {names.get(gw,gw)}:\n`XXXX|MM|YYYY|CVV`", parse_mode="Markdown")
		pending_gateway[str(call.from_user.id)] = gw
		bot.answer_callback_query(call.id)
	elif data.startswith("combo_"):
		handle_combo_selection(call)
	elif data.startswith("start_combo_"):
		start_combo_check(call)
	elif data.startswith("stop_"):
		session_id = data.replace("stop_", "")
		if session_id in stopuser:
			stopuser[session_id]['status'] = 'stop'
			bot.answer_callback_query(call.id, "✅ Stopped this checker only!")
		else:
			bot.answer_callback_query(call.id, "❌ Not found")
	elif data in ['none', 'u8', 'x']:
		bot.answer_callback_query(call.id)

# ==================== معالج الكومبو ====================
def handle_combo_selection(call):
	user = str(call.from_user.id)
	data = call.data
	
	if user not in user_file:
		bot.answer_callback_query(call.id, "No file found")
		return
	
	if data == "combo_stripe":
		markup = types.InlineKeyboardMarkup(row_width=2)
		gateways = [("Stripe1","st1"),("Stripe2","st2"),("Stripe3","st3"),("Stripe4","st4"),("Stripe5","st5"),("Stripe6","st6"),("Donate","donate")]
		for name, code in gateways:
			markup.add(types.InlineKeyboardButton(name, callback_data=f"start_combo_{code}"))
		markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="combo_back"))
		bot.edit_message_text("Select Stripe:", call.message.chat.id, call.message.message_id, reply_markup=markup)
	elif data == "combo_braintree":
		markup = types.InlineKeyboardMarkup(row_width=2)
		gateways = [("Braintree1","br1"),("Braintree2","br2"),("BraintreeCharge","chk1")]
		for name, code in gateways:
			markup.add(types.InlineKeyboardButton(name, callback_data=f"start_combo_{code}"))
		markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="combo_back"))
		bot.edit_message_text("Select Braintree:", call.message.chat.id, call.message.message_id, reply_markup=markup)
	elif data == "combo_back":
		bot.edit_message_text("Select gateway type:", call.message.chat.id, call.message.message_id, reply_markup=combo_type_menu())
	elif data == "combo_cancel":
		if user in user_file:
			f = user_file[user]
			if os.path.exists(f):
				os.remove(f)
			del user_file[user]
		bot.edit_message_text("❌ Cancelled", call.message.chat.id, call.message.message_id)
	bot.answer_callback_query(call.id)

# ==================== بدء فحص الكومبو ====================
def start_combo_check(call):
	user = str(call.from_user.id)
	gw = call.data.replace("start_combo_", "")
	
	if user not in user_file:
		bot.answer_callback_query(call.id, "File expired")
		return
	
	gw_map = {
		"st1": Stripe1, "st2": Stripe2, "st3": Stripe3, "st4": Stripe4, "st5": Stripe5, "st6": Stripe6,
		"donate": Donate, "br1": bra1, "br2": bra2, "chk1": BraC
	}
	name_map = {
		"st1": "Stripe1", "st2": "Stripe2", "st3": "Stripe3", "st4": "Stripe4", "st5": "Stripe5", "st6": "Stripe6",
		"donate": "Donate", "br1": "Braintree1", "br2": "Braintree2", "chk1": "BraintreeCharge"
	}
	
	if gw not in gw_map:
		bot.answer_callback_query(call.id, "Invalid gateway")
		return
	
	filename = user_file[user]
	msg = bot.send_message(call.message.chat.id, f"🚀 Starting on {name_map[gw]}...\n📁 {os.path.basename(filename)}")
	session_id = f"{user}_{gw}_{int(time.time())}_{random.randint(1000,9999)}"
	
	def run():
		approved = 0
		declined = 0
		stopuser[session_id] = {'status': 'start'}
		
		try:
			with open(filename, 'r') as f:
				lines = [l.strip() for l in f if l.strip()]
				total = len(lines)
				
				for idx, cc in enumerate(lines):
					if stopuser.get(session_id, {}).get('status') == 'stop':
						bot.edit_message_text(f"⏹️ Stopped\n✅{approved} ❌{declined}", call.message.chat.id, msg.message_id)
						return
					
					try:
						start = time.time()
						result = str(gw_map[gw](cc))
						exec_time = time.time() - start
						
						mes = types.InlineKeyboardMarkup(row_width=1)
						mes.add(
							types.InlineKeyboardButton(f"• {cc[:20]}... •", callback_data='none'),
							types.InlineKeyboardButton(f"- Status! : {result[:30]} •", callback_data='none'),
							types.InlineKeyboardButton(f"- Approved! ✅ : [ {approved} ] •", callback_data='none'),
							types.InlineKeyboardButton(f"- Declined! ❌ : [ {declined} ] •", callback_data='none'),
							types.InlineKeyboardButton(f"- Total! : [ {total} ] •", callback_data='none'),
							types.InlineKeyboardButton("[ Stop Checker! ]", callback_data=f"stop_{session_id}")
						)
						
						bot.edit_message_text(f"- Checker To {name_map[gw]} ☑️\n- Time: {exec_time:.2f}s", call.message.chat.id, msg.message_id, reply_markup=mes)
						
						if 'Approved' in result or '✅' in result:
							approved += 1
							bot.send_message(call.from_user.id, f"✅ Approved | {name_map[gw]}\n📇 {cc}\n💬 {result}\n\n{dato(cc[:6])}")
						else:
							declined += 1
						
						time.sleep(10)
					except:
						declined += 1
						time.sleep(10)
			
			bot.edit_message_text(f"✅ Completed! ✅{approved} ❌{declined} Total:{total}", call.message.chat.id, msg.message_id)
		except Exception as e:
			bot.edit_message_text(f"❌ Error: {e}", call.message.chat.id, msg.message_id)
		finally:
			if os.path.exists(filename):
				os.remove(filename)
			if session_id in stopuser:
				del stopuser[session_id]
	
	threading.Thread(target=run).start()
	del user_file[user]
	bot.answer_callback_query(call.id)

# ==================== رفع ملف ====================
@bot.message_handler(content_types=['document'])
def handle_doc(m):
	user = str(m.from_user.id)
	try:
		info = bot.get_file(m.document.file_id)
		down = bot.download_file(info.file_path)
		filename = f"combo_{user}_{int(time.time())}.txt"
		with open(filename, "wb") as f:
			f.write(down)
		user_file[user] = filename
		bot.reply_to(m, "📁 Select gateway type:", reply_markup=combo_type_menu())
	except Exception as e:
		bot.reply_to(m, f"❌ Error: {e}")

# ==================== الفحص اليدوي ====================
def check_card(message, check_func, gateway_name, cmd_prefix):
	idt = message.from_user.id
	try:
		command_usage[idt]['last_time']
	except:
		command_usage[idt] = {'last_time': datetime.now()}
	
	if command_usage[idt]['last_time'] is not None:
		current_time = datetime.now()
		time_diff = (current_time - command_usage[idt]['last_time']).seconds
		if time_diff < 10:
			bot.reply_to(message, f"<b>Try again after {10-time_diff} seconds.</b>", parse_mode="HTML")
			return
	
	ko = bot.reply_to(message, "- Wait checking your card ...").message_id
	
	try:
		cc = message.reply_to_message.text
	except:
		cc = message.text
	
	cc = str(reg(cc))
	if cc == 'None' or cc is None:
		bot.edit_message_text('<b>🚫 Invalid format: XXXXXXXXXXXXXXXX|MM|YYYY|CVV</b>', message.chat.id, ko, parse_mode="HTML")
		return
	
	start_time = time.time()
	try:
		command_usage[idt]['last_time'] = datetime.now()
		last = str(check_func(cc))
	except Exception as e:
		last = f'Error: {str(e)}'
	
	end_time = time.time()
	execution_time = end_time - start_time
	status = 'Approved ✅' if 'Approved' in last else 'Declined ❌'
	
	msg = f'''<strong>#{gateway_name} 🔥
- - - - - - - - - - - - - - - - - - - - - - -
[ϟ] 𝐂𝐚𝐫𝐝: <code>{cc}</code>
[ϟ] 𝐒𝐭𝐚𝐭𝐮𝐬: <code>{status}</code>
[ϟ] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{last}</code>
- - - - - - - - - - - - - - - - - - - - - - -
{dato(cc[:6])}
- - - - - - - - - - - - - - - - - - - - - - -
[⌥] 𝐓𝐢𝐦𝐞: <code>{execution_time:.2f}'s</code>
[⌤] 𝐃𝐞𝐯: @s3s_a</strong>'''
	
	try:
		bot.edit_message_text(msg, message.chat.id, ko, parse_mode="HTML")
	except:
		pass

# ==================== الأوامر اليدوية ====================
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st1','.st1')))
def stripe1_cmd(m): check_card(m, Stripe1, "Stripe1", "st1")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st2','.st2')))
def stripe2_cmd(m): check_card(m, Stripe2, "Stripe2", "st2")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st3','.st3')))
def stripe3_cmd(m): check_card(m, Stripe3, "Stripe3", "st3")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st4','.st4')))
def stripe4_cmd(m): check_card(m, Stripe4, "Stripe4", "st4")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st5','.st5')))
def stripe5_cmd(m): check_card(m, Stripe5, "Stripe5", "st5")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st6','.st6')))
def stripe6_cmd(m): check_card(m, Stripe6, "Stripe6", "st6")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/donate','.donate')))
def donate_cmd(m): check_card(m, Donate, "Donate", "donate")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/br1','.br1')))
def br1_cmd(m): check_card(m, bra1, "Braintree1", "br1")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/br2','.br2')))
def br2_cmd(m): check_card(m, bra2, "Braintree2", "br2")
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/br3','.br3')))
def br3_cmd(m): check_card(m, BraC, "BraintreeCharge", "br3")

# ==================== معالج الرسائل ====================
@bot.message_handler(func=lambda m: True)
def handle_text(m):
	user = m.from_user.id
	text = m.text.strip()
	
	if text.isdigit() and 6 <= len(text) <= 8:
		bot.reply_to(m, check_bin_advanced(text[:6]), parse_mode="HTML")
		return
	
	if text.lower() in ["usa","uk","canada","germany","france","italy","netherlands","india","pakistan","china","russia","switzerland","south korea","japan"]:
		bot.reply_to(m, get_fake_info(text.capitalize()), parse_mode="HTML")
		return
	
	if '|' in text and 'x' in text.lower():
		try:
			parts = text.split()
			if len(parts) == 2 and parts[1].isdigit():
				pattern = parts[0]
				count = min(int(parts[1]), 100)
			else:
				pattern = text
				count = 10
			cards = generate_card_from_input(pattern, count)
			if cards:
				if count <= 10:
					for card in cards:
						bot.send_message(m.chat.id, f"<code>{card}</code>", parse_mode="HTML")
				else:
					fn = f"gen_{user}.txt"
					with open(fn, 'w') as f:
						f.write('\n'.join(cards))
					with open(fn, 'rb') as f:
						bot.send_document(m.chat.id, f)
					os.remove(fn)
			else:
				bot.reply_to(m, "❌ Invalid pattern")
		except Exception as e:
			bot.reply_to(m, f"❌ Error: {e}")
		return
	
	if str(user) in pending_gateway:
		gw = pending_gateway.pop(str(user))
		gw_map = {"st1":Stripe1,"st2":Stripe2,"st3":Stripe3,"st4":Stripe4,"st5":Stripe5,"st6":Stripe6,"donate":Donate,"br1":bra1,"br2":bra2,"chk1":BraC}
		name_map = {"st1":"Stripe1","st2":"Stripe2","st3":"Stripe3","st4":"Stripe4","st5":"Stripe5","st6":"Stripe6","donate":"Donate","br1":"Braintree1","br2":"Braintree2","chk1":"BraintreeCharge"}
		if gw in gw_map:
			check_card(m, gw_map[gw], name_map[gw], gw)

# ==================== تشغيل البوت ====================
print('- Auth Bot was run ..')

def generate_cards_advanced(user_input, count=10):
    """
    توليد بطاقات بصيغ متعددة:
    - 528445
    - 528445,400519,518928 (BINs متعددة)
    - 410621xxxx|12|29|xxx
    - 410621746xxxx|12|29|xxx
    """
    cards = []
    
    # صيغة BINs متعددة (مفصولة بفواصل)
    if ',' in user_input and '|' not in user_input:
        bins = [b.strip() for b in user_input.split(',') if b.strip()]
        for _ in range(count):
            bin_choice = random.choice(bins)
            remaining_len = 16 - len(bin_choice)
            if bin_choice.startswith('3'):
                remaining_len = 15 - len(bin_choice)
            if remaining_len > 0:
                random_digits = ''.join(random.choices(string.digits, k=remaining_len))
                card_num = bin_choice + random_digits
            else:
                card_num = bin_choice[:16]
            # حساب Luhn
            card_num = card_num[:-1] + str(luhn_checksum(card_num[:-1]))
            month = str(random.randint(1, 12)).zfill(2)
            year = str(random.randint(2026, 2031))
            cvv = ''.join(random.choices(string.digits, k=3))
            cards.append(f"{card_num}|{month}|{year}|{cvv}")
        return cards
    
    # صيغة BIN واحد
    if user_input.isdigit() and len(user_input) >= 6 and '|' not in user_input:
        bin_choice = user_input[:6]
        for _ in range(count):
            remaining_len = 16 - len(bin_choice)
            if bin_choice.startswith('3'):
                remaining_len = 15 - len(bin_choice)
            random_digits = ''.join(random.choices(string.digits, k=remaining_len))
            card_num = bin_choice + random_digits
            card_num = card_num[:-1] + str(luhn_checksum(card_num[:-1]))
            month = str(random.randint(1, 12)).zfill(2)
            year = str(random.randint(2026, 2031))
            cvv = ''.join(random.choices(string.digits, k=3))
            cards.append(f"{card_num}|{month}|{year}|{cvv}")
        return cards
    
    # صيغة بنمط x (مثل 410621xxxx|12|29|xxx)
    if '|' in user_input and ('x' in user_input.lower() or 'X' in user_input):
        parts = user_input.split('|')
        if len(parts) >= 4:
            card_pattern = parts[0]
            month = parts[1]
            year = parts[2]
            cvv_pattern = parts[3]
            
            # تحديد عدد الأرقام المطلوبة للبطاقة
            if card_pattern.startswith('3'):
                total_len = 15
            else:
                total_len = 16
            
            for _ in range(count):
                # معالجة رقم البطاقة
                if 'x' in card_pattern.lower():
                    x_count = card_pattern.lower().count('x')
                    needed = total_len - (len(card_pattern) - x_count)
                    random_digits = ''.join(random.choices(string.digits, k=needed))
                    card_num = card_pattern.lower().replace('x' * x_count, random_digits)
                else:
                    card_num = card_pattern
                
                # حساب Luhn
                card_num = card_num[:-1] + str(luhn_checksum(card_num[:-1]))
                
                # معالجة CVV
                if 'x' in cvv_pattern.lower():
                    x_count = cvv_pattern.lower().count('x')
                    cvv = ''.join(random.choices(string.digits, k=x_count)).zfill(x_count)
                else:
                    cvv = cvv_pattern
                
                cards.append(f"{card_num}|{month}|{year}|{cvv}")
            return cards
    
    return None

# ==================== استخراج بطاقات من رسالة ====================
def extract_cards_from_message(text):
    """استخراج جميع البطاقات من رسالة واحدة"""
    cards = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        # البحث عن بطاقات بصيغة رقم|شهر|سنة|CVV
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

# ==================== أوامر الميزات الجديدة ====================

# توليد بطاقات
@bot.message_handler(commands=['gen'])
def generate_cards_command(message):
    """/gen 528445 20  - توليد 20 بطاقة من BIN 528445
       /gen 410621xxxx|12|29|xxx 15 - توليد 15 بطاقة بنمط معين"""
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ استخدم: /gen <BIN/pattern> <count>\nمثال:\n/gen 528445 20\n/gen 410621xxxx|12|29|xxx 10")
            return
        
        pattern = parts[1]
        count = int(parts[2]) if len(parts) > 2 else 10
        if count > 100:
            bot.reply_to(message, "⚠️ الحد الأقصى 100 بطاقة في المرة")
            return
        
        cards = generate_cards_advanced(pattern, count)
        if not cards:
            bot.reply_to(message, "❌ صيغة غير صحيحة")
            return
        
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("📤 إرسال في الشات", callback_data=f"send_chat_{message.from_user.id}"),
            types.InlineKeyboardButton("💾 حفظ في ملف", callback_data=f"save_file_{message.from_user.id}")
        )
        
        # تخزين البطاقات مؤقتاً
        pending_cards[message.from_user.id] = cards
        bot.reply_to(message, f"🎴 تم توليد {len(cards)} بطاقة\nاختر طريقة الإرسال:", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

# قاموس مؤقت للبطاقات المولدة
pending_cards = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith('send_chat_') or call.data.startswith('save_file_'))
def handle_generated_cards(call):
    user_id = call.from_user.id
    if user_id not in pending_cards:
        bot.answer_callback_query(call.id, "❌ لا توجد بطاقات")
        return
    
    cards = pending_cards[user_id]
    
    if call.data.startswith('send_chat_'):
        # إرسال في الشات
        msg = "🎴 **البطاقات المولدة**\n━━━━━━━━━━━━━━━━\n"
        for card in cards:
            msg += f"<code>{card}</code>\n"
        if len(msg) > 4000:
            # إذا كان طويلاً، أرسل كملف
            filename = f"generated_{user_id}.txt"
            with open(filename, 'w') as f:
                f.write('\n'.join(cards))
            with open(filename, 'rb') as f:
                bot.send_document(call.message.chat.id, f, caption=f"🎴 {len(cards)} بطاقة مولدة")
            os.remove(filename)
        else:
            bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
        bot.answer_callback_query(call.id, "✅ تم الإرسال")
        
    elif call.data.startswith('save_file_'):
        filename = f"cards_{user_id}_{int(time.time())}.txt"
        with open(filename, 'w') as f:
            f.write('\n'.join(cards))
        with open(filename, 'rb') as f:
            bot.send_document(call.message.chat.id, f, caption=f"🎴 {len(cards)} بطاقة مولدة")
        os.remove(filename)
        bot.answer_callback_query(call.id, "✅ تم الحفظ")
    
    # حذف البطاقات المؤقتة
    del pending_cards[user_id]
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

# ==================== فحص رد على رسالة (Mass Check) ====================
@bot.message_handler(commands=['mass'])
def mass_check_command(message):
    """/mass - يفحص البطاقات في الرد على رسالة"""
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ قم بالرد على رسالة تحتوي على بطاقات\nمثال: /mass (مع الرد على رسالة البطاقات)")
        return
    
    # استخراج البطاقات من الرسالة المقتبسة
    cards = extract_cards_from_message(message.reply_to_message.text)
    if not cards:
        # حاول استخراج من الكابتشن
        if message.reply_to_message.caption:
            cards = extract_cards_from_message(message.reply_to_message.caption)
    
    if not cards:
        bot.reply_to(message, "❌ لم يتم العثور على بطاقات في الرسالة")
        return
    
    # تخزين البطاقات مؤقتاً
    pending_mass_cards[message.from_user.id] = cards
    
    # عرض بوابات الفحص
    markup = types.InlineKeyboardMarkup(row_width=2)
    gateways = [
        ("Stripe1", "mass_st1"), ("Stripe2", "mass_st2"), ("Stripe3", "mass_st3"),
        ("Stripe4", "mass_st4"), ("Stripe5", "mass_st5"), ("Stripe6", "mass_st6"),
        ("Braintree1", "mass_br1"), ("Braintree2", "mass_br2"), ("BraintreeCharge", "mass_chk1")
    ]
    for name, code in gateways:
        markup.add(types.InlineKeyboardButton(name, callback_data=code))
    markup.add(types.InlineKeyboardButton("🔙 إلغاء", callback_data="mass_cancel"))
    
    bot.reply_to(message, f"📊 تم العثور على {len(cards)} بطاقة\nاختر بوابة الفحص:", reply_markup=markup)

# قاموس مؤقت للبطاقات في الفحص الجماعي
pending_mass_cards = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith('mass_'))
def handle_mass_check(call):
    user_id = call.from_user.id
    gw_code = call.data.replace('mass_', '')
    
    if gw_code == 'cancel':
        if user_id in pending_mass_cards:
            del pending_mass_cards[user_id]
        bot.edit_message_text("❌ تم الإلغاء", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if user_id not in pending_mass_cards:
        bot.answer_callback_query(call.id, "❌ لا توجد بطاقات")
        return
    
    cards = pending_mass_cards[user_id]
    
    # خريطة البوابات
    gw_map = {
        "st1": Stripe1, "st2": Stripe2, "st3": Stripe3, "st4": Stripe4, "st5": Stripe5, "st6": Stripe6,
        "br1": bra1, "br2": bra2, "chk1": BraC
    }
    name_map = {
        "st1": "Stripe1", "st2": "Stripe2", "st3": "Stripe3", "st4": "Stripe4", "st5": "Stripe5", "st6": "Stripe6",
        "br1": "Braintree1", "br2": "Braintree2", "chk1": "BraintreeCharge"
    }
    
    if gw_code not in gw_map:
        bot.answer_callback_query(call.id, "بوابة غير صالحة")
        return
    
    bot.edit_message_text(f"🚀 بدء فحص {len(cards)} بطاقة على {name_map[gw_code]}...", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    
    # بدء الفحص
    def run_mass_check():
        approved = 0
        session_id = f"mass_{user_id}_{int(time.time())}"
        stopuser[session_id] = {'status': 'start'}
        
        for i, card in enumerate(cards, 1):
            if stopuser.get(session_id, {}).get('status') == 'stop':
                bot.send_message(user_id, f"⏹️ تم الإيقاف عند {i-1}/{len(cards)}")
                break
            
            try:
                start = time.time()
                result = str(gw_map[gw_code](card))
                exec_time = time.time() - start
                
                if 'Approved' in result or '✅' in result:
                    approved += 1
                    bot.send_message(user_id, f"✅ **Approved** | {name_map[gw_code]}\n📇 `{card}`\n💬 {result}\n\n{dato(card[:6])}", parse_mode="HTML")
                
                bot.send_message(user_id, f"📊 تقدم: {i}/{len(cards)} | ✅ {approved}")
                time.sleep(7)
                
            except Exception as e:
                bot.send_message(user_id, f"❌ خطأ في {card[:20]}...: {e}")
                time.sleep(5)
        
        bot.send_message(user_id, f"✅ **اكتمل الفحص**\n✅ Approved: {approved}\n❌ Declined: {len(cards)-approved}\n📊 الإجمالي: {len(cards)}")
        del pending_mass_cards[user_id]
    
    threading.Thread(target=run_mass_check).start()

# ==================== فحص بطاقات من رسالة واحدة (رداً على أمر) ====================
def check_cards_from_reply(message, check_func, gateway_name):
    """فحص جميع البطاقات في الرسالة المقتبسة"""
    if not message.reply_to_message:
        bot.reply_to(message, f"⚠️ قم بالرد على رسالة تحتوي على بطاقات\nمثال: {message.text} (مع الرد)")
        return
    
    cards = extract_cards_from_message(message.reply_to_message.text)
    if not cards and message.reply_to_message.caption:
        cards = extract_cards_from_message(message.reply_to_message.caption)
    
    if not cards:
        bot.reply_to(message, "❌ لم يتم العثور على بطاقات في الرسالة")
        return
    
    # إرسال نتيجة الفحص لكل بطاقة
    status_msg = bot.reply_to(message, f"🚀 جاري فحص {len(cards)} بطاقة...")
    
    def run():
        approved = 0
        results = []
        for card in cards:
            try:
                start = time.time()
                result = str(check_func(card))
                exec_time = time.time() - start
                
                if 'Approved' in result or '✅' in result:
                    approved += 1
                    msg = f"✅ **Approved** | {gateway_name}\n📇 `{card}`\n💬 {result}\n{dato(card[:6])}\n⏱️ {exec_time:.2f}s"
                else:
                    msg = f"❌ **Declined** | {gateway_name}\n📇 `{card}`\n💬 {result}\n{dato(card[:6])}"
                
                bot.send_message(message.chat.id, msg, parse_mode="HTML")
                results.append(msg)
                time.sleep(5)
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ خطأ في {card}: {e}")
        
        bot.edit_message_text(f"✅ اكتمل الفحص\n✅ Approved: {approved}\n❌ Declined: {len(cards)-approved}", message.chat.id, status_msg.message_id)
    
    threading.Thread(target=run).start()

# ==================== إضافة أوامر الرد على الرسائل ====================
# تعديل الأوامر الحالية لدعم الرد على رسائل متعددة
# حفظ الدوال الأصلية مؤقتاً
_original_handlers = {}

# إضافة أوامر جديدة للفحص الجماعي
@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st1','.st1')) and m.reply_to_message)
def stripe1_mass(m): check_cards_from_reply(m, Stripe1, "Stripe1")

@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st2','.st2')) and m.reply_to_message)
def stripe2_mass(m): check_cards_from_reply(m, Stripe2, "Stripe2")

@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st3','.st3')) and m.reply_to_message)
def stripe3_mass(m): check_cards_from_reply(m, Stripe3, "Stripe3")

@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st4','.st4')) and m.reply_to_message)
def stripe4_mass(m): check_cards_from_reply(m, Stripe4, "Stripe4")

@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st5','.st5')) and m.reply_to_message)
def stripe5_mass(m): check_cards_from_reply(m, Stripe5, "Stripe5")

@bot.message_handler(func=lambda m: m.text.lower().startswith(('/st6','.st6')) and m.reply_to_message)
def stripe6_mass(m): check_cards_from_reply(m, Stripe6, "Stripe6")

@bot.message_handler(func=lambda m: m.text.lower().startswith(('/br1','.br1')) and m.reply_to_message)
def br1_mass(m): check_cards_from_reply(m, bra1, "Braintree1")

@bot.message_handler(func=lambda m: m.text.lower().startswith(('/br2','.br2')) and m.reply_to_message)
def br2_mass(m): check_cards_from_reply(m, bra2, "Braintree2")

@bot.message_handler(func=lambda m: (m.text.lower().startswith(('/br3','.br3')) or m.text.lower().startswith('/chk1')) and m.reply_to_message)
def br3_mass(m): check_cards_from_reply(m, BraC, "BraintreeCharge")

@bot.message_handler(func=lambda m: m.text.lower().startswith(('/donate','.donate')) and m.reply_to_message)
def donate_mass(m): check_cards_from_reply(m, Donate, "Donate")

print("- New features added successfully!")

while True:
	try:
		bot.infinity_polling(timeout=60)
	except Exception as e:
		print(f'- Was error : {e}')
		time.sleep(20)