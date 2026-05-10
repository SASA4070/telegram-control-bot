import random
import re

def luhn_checksum(card_number):
    """حساب الرقم الأخير لخوارزمية Luhn"""
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return (checksum * 9) % 10

def generate_luhn_card(bin_prefix, length=16):
    """توليد رقم بطاقة كامل بخوارزمية Luhn"""
    if len(bin_prefix) >= length:
        return bin_prefix[:length]
    
    # توليد أرقام عشوائية للخانات المتبقية (ما عدا آخر خانة)
    remaining_length = length - len(bin_prefix) - 1
    random_part = ''.join(str(random.randint(0, 9)) for _ in range(remaining_length))
    partial_number = bin_prefix + random_part
    checksum = luhn_checksum(partial_number + '0')
    return partial_number + str(checksum)

def generate_card_from_input(user_input, count=1):
    """
    توليد بطاقات من مدخل مثل:
    410621000580xxxx|10|27|xxx
    أو
    540716000968xxxx|08|26|xxx
    """
    try:
        # تجزئة المدخل
        parts = user_input.split('|')
        if len(parts) != 4:
            return None
        
        card_pattern = parts[0].strip()
        month = parts[1].strip()
        year = parts[2].strip()
        cvv_pattern = parts[3].strip()
        
        # استخراج الـ BIN من النص (كل الأرقام قبل xxxx)
        match = re.match(r'^(\d+)(x+)$', card_pattern, re.IGNORECASE)
        if not match:
            # لو مفيش xxx، استخدم الرقم كله كـ BIN ثابت
            bin_part = card_pattern
            x_count = 0
        else:
            bin_part = match.group(1)
            x_count = len(match.group(2))
        
        # عدد الأرقام المطلوب توليدها عشوائياً
        total_length = 16 if not card_pattern.startswith('3') else 15
        fixed_length = len(bin_part)
        random_needed = total_length - fixed_length
        
        cards = []
        for _ in range(count):
            # توليد الرقم العشوائي المطلوب
            if random_needed > 0:
                random_digits = ''.join(str(random.randint(0, 9)) for _ in range(random_needed))
                full_number = bin_part + random_digits
            else:
                full_number = bin_part[:total_length]
            
            # تطبيق Luhn لتصحيح آخر رقم
            final_number = full_number[:-1] + str(luhn_checksum(full_number[:-1]))
            
            # توليد CVV عشوائي إذا كان مطلوب
            if cvv_pattern.lower() == 'xxx' or cvv_pattern == '***':
                final_cvv = str(random.randint(100, 999))
            else:
                final_cvv = cvv_pattern
            
            cards.append(f"{final_number}|{month}|{year}|{final_cvv}")
        
        return cards
    
    except Exception as e:
        print(f"Generation error: {e}")
        return None

def generate_multiple_bins(bins_input, count_per_bin=5):
    """توليد بطاقات من عدة BINs في نفس الوقت"""
    lines = bins_input.strip().split('\n')
    all_cards = []
    
    for line in lines:
        if line.strip():
            cards = generate_card_from_input(line.strip(), count_per_bin)
            if cards:
                all_cards.extend(cards)
    
    return all_cards