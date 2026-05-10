import requests
import re

def check_bin(bin_code):
    """
    فحص BIN من 3 مصادر مختلفة
    bin_code: أول 6 أرقام من البطاقة (أو أقل)
    """
    bin_code = str(bin_code)[:6]
    
    # المصدر 1: antipublic (الأساسي)
    try:
        url = f"https://bins.antipublic.cc/bins/{bin_code}"
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            return format_bin_result(data, "antipublic")
    except:
        pass
    
    # المصدر 2: binlist.net (احتياطي)
    try:
        url = f"https://binlist.net/json/{bin_code}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return format_bin_result_alt(data, "binlist")
    except:
        pass
    
    # المصدر 3: neavr.com (احتياطي أخير)
    try:
        url = f"https://neavr.com/api/bins/?bin={bin_code}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return format_bin_result_alt2(data, "neavr")
    except:
        pass
    
    return "⚠️ لا يمكن فحص هذا BIN حالياً"

def format_bin_result(data, source):
    brand = data.get("brand", "Unknown")
    card_type = data.get("type", "Unknown")
    level = data.get("level", "Unknown")
    bank = data.get("bank", "Unknown")
    country_name = data.get("country_name", "Unknown")
    country_flag = data.get("country_flag", "🏳️")
    
    # تحديد إذا كان debit/credit/prepaid
    if "debit" in str(card_type).lower():
        type_icon = "💳 DEBIT"
    elif "credit" in str(card_type).lower():
        type_icon = "💎 CREDIT"
    elif "prepaid" in str(card_type).lower():
        type_icon = "🎫 PREPAID"
    else:
        type_icon = card_type.upper()
    
    result = f"""🔍 **BIN CHECK** | {source}
━━━━━━━━━━━━━━━━
💳 **BIN:** `{data.get('bin', 'N/A')}`
🏷️ **Brand:** {brand}
📌 **Type:** {type_icon}
⭐ **Level:** {level}
🏦 **Bank:** {bank}
🌍 **Country:** {country_name} {country_flag}
━━━━━━━━━━━━━━━━"""
    return result

def format_bin_result_alt(data, source):
    # binlist.net format
    try:
        scheme = data.get("scheme", "Unknown")
        type_ = data.get("type", "Unknown")
        brand = data.get("brand", "Unknown")
        bank_name = data.get("bank", {}).get("name", "Unknown")
        country_name = data.get("country", {}).get("name", "Unknown")
        country_code = data.get("country", {}).get("alpha2", "")
        
        flags = {"US": "🇺🇸", "GB": "🇬🇧", "CA": "🇨🇦", "DE": "🇩🇪", "FR": "🇫🇷", "IT": "🇮🇹", "NL": "🇳🇱", "IN": "🇮🇳", "PK": "🇵🇰", "CN": "🇨🇳", "RU": "🇷🇺", "CH": "🇨🇭", "KR": "🇰🇷", "JP": "🇯🇵", "KP": "🇰🇵"}
        flag = flags.get(country_code, "🏳️")
        
        result = f"""🔍 **BIN CHECK** | {source}
━━━━━━━━━━━━━━━━
💳 **BIN:** `{data.get('number', {}).get('length', 'N/A') and bin_code or 'N/A'}`
🏷️ **Brand:** {scheme}
📌 **Type:** {type_.upper()}
🏦 **Bank:** {bank_name}
🌍 **Country:** {country_name} {flag}
━━━━━━━━━━━━━━━━"""
        return result
    except:
        return format_bin_result_alt2(data, source)

def format_bin_result_alt2(data, source):
    try:
        brand = data.get("brand", "Unknown")
        type_ = data.get("type", "Unknown")
        bank = data.get("bank", "Unknown")
        country = data.get("country", "Unknown")
        
        result = f"""🔍 **BIN CHECK** | {source}
━━━━━━━━━━━━━━━━
🏷️ **Brand:** {brand}
📌 **Type:** {type_.upper()}
🏦 **Bank:** {bank}
🌍 **Country:** {country}
━━━━━━━━━━━━━━━━"""
        return result
    except:
        return "⚠️ فشل في قراءة بيانات BIN"