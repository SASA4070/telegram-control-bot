import json
import os
from datetime import datetime

# ===================================================================
# ========================== ملف المستخدمين ==========================
# ===================================================================
USERS_DB_FILE = "users_db.json"

def load_users():
    """تحميل بيانات المستخدمين من الملف"""
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """حفظ بيانات المستخدمين في الملف"""
    with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# ===================================================================
# ========================== إدارة المستخدمين ==========================
# ===================================================================

def get_user_plan(user_id):
    """الحصول على خطة المستخدم"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        # مستخدم جديد - خطة مجانية
        users[user_id_str] = {
            "plan": "Free - Not Subscribed",
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users)
        return "Free - Not Subscribed"
    
    return users[user_id_str].get("plan", "Free - Not Subscribed")

def set_user_plan(user_id, plan, expiry_date=None):
    """تعيين خطة للمستخدم"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    users[user_id_str]["plan"] = plan
    
    if expiry_date:
        users[user_id_str]["expiry"] = expiry_date
    elif "expiry" in users[user_id_str]:
        del users[user_id_str]["expiry"]
    
    save_users(users)
    return True

def add_points(user_id, points, reason=""):
    """إضافة نقاط للمستخدم"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {
            "plan": "Free - Not Subscribed",
            "points": 0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    current_points = users[user_id_str].get("points", 0)
    users[user_id_str]["points"] = current_points + points
    
    # تسجيل سبب الإضافة
    if "points_log" not in users[user_id_str]:
        users[user_id_str]["points_log"] = []
    users[user_id_str]["points_log"].append({
        "amount": points,
        "reason": reason,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    save_users(users)
    return users[user_id_str]["points"]

def get_points(user_id):
    """الحصول على رصيد النقاط"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        return 0
    
    return users[user_id_str].get("points", 0)

def check_user_status(user_id):
    """التحقق من حالة المستخدم (محظور أم لا)"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        return False
    
    return users[user_id_str].get("banned", False)

def ban_user(user_id, reason=""):
    """حظر مستخدم"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {
            "plan": "Free - Not Subscribed",
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    users[user_id_str]["banned"] = True
    users[user_id_str]["ban_reason"] = reason
    users[user_id_str]["banned_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    save_users(users)
    return True

def unban_user(user_id):
    """رفع الحظر عن مستخدم"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str in users:
        users[user_id_str]["banned"] = False
        if "ban_reason" in users[user_id_str]:
            del users[user_id_str]["ban_reason"]
        if "banned_at" in users[user_id_str]:
            del users[user_id_str]["banned_at"]
        save_users(users)
        return True
    
    return False

def is_vip(user_id):
    """التحقق إذا كان المستخدم VIP"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        return False
    
    plan = users[user_id_str].get("plan", "Free - Not Subscribed")
    
    # التحقق من صلاحية VIP
    if "VIP" in plan:
        expiry = users[user_id_str].get("expiry")
        if expiry:
            try:
                expiry_date = datetime.strptime(expiry, "%Y-%m-%d %H:%M")
                if datetime.now() > expiry_date:
                    # انتهت صلاحية VIP
                    users[user_id_str]["plan"] = "Free - Not Subscribed"
                    save_users(users)
                    return False
            except:
                pass
        return True
    
    return False

def get_all_users():
    """الحصول على جميع المستخدمين"""
    return load_users()

def get_user_info(user_id):
    """الحصول على معلومات مستخدم معين"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        return None
    
    return users[user_id_str]

def deduct_points(user_id, points, reason=""):
    """خصم نقاط من المستخدم"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {
            "plan": "Free - Not Subscribed",
            "points": 0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    current_points = users[user_id_str].get("points", 0)
    
    if current_points >= points:
        users[user_id_str]["points"] = current_points - points
        
        # تسجيل سبب الخصم
        if "points_log" not in users[user_id_str]:
            users[user_id_str]["points_log"] = []
        users[user_id_str]["points_log"].append({
            "amount": -points,
            "reason": reason,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        save_users(users)
        return True
    
    return False