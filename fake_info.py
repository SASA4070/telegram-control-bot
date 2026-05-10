import random

def get_fake_info(country):
    """
    توليد بيانات وهمية حسب الدولة المختارة
    """
    countries_data = {
        "USA": {
            "first_names": ["John", "James", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"],
            "last_names": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"],
            "addresses": ["6200 Phyllis Dr", "123 Main St", "456 Oak Ave", "789 Pine Rd", "321 Elm St"],
            "cities": ["Cypress", "Los Angeles", "New York", "Miami", "Chicago", "Houston", "Phoenix"],
            "states": ["CA", "NY", "FL", "TX", "IL", "AZ", "PA"],
            "zip_codes": ["90630", "10001", "33101", "77001", "60601", "85001", "19101"],
            "phones": ["+15416450372", "+12125551234", "+13125551234", "+14155551234", "+16175551234"],
            "email_domains": ["gmail.com", "yahoo.com", "outlook.com"]
        },
        "UK": {
            "first_names": ["James", "David", "John", "Paul", "Mark", "Andrew", "Thomas", "Daniel", "Christopher", "Matthew"],
            "last_names": ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Robinson", "Wright"],
            "addresses": ["221 Baker St", "10 Downing St", "1 Kings Rd", "25 High St", "42 Abbey Rd"],
            "cities": ["London", "Manchester", "Birmingham", "Glasgow", "Liverpool", "Bristol", "Leeds"],
            "postcodes": ["NW1 6XE", "M1 1AE", "B1 1BB", "G1 1AA", "L1 1AA", "BS1 1AA", "LS1 1AA"],
            "phones": ["+442079460958", "+441612345678", "+441212345678", "+441412345678", "+441151234567"],
            "email_domains": ["gmail.com", "yahoo.co.uk", "outlook.com"]
        },
        "Canada": {
            "first_names": ["Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"],
            "last_names": ["Smith", "Brown", "Tremblay", "Martin", "Roy", "Gagnon", "Lee", "Wilson", "Johnson", "MacDonald"],
            "addresses": ["123 Queen St", "456 King St", "789 Yonge St", "321 Robson St", "555 Sainte-Catherine St"],
            "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Edmonton", "Ottawa", "Winnipeg"],
            "provinces": ["ON", "BC", "QC", "AB", "MB", "SK", "NS"],
            "postcodes": ["M5V 2T6", "V6B 1A1", "H2Y 1A1", "T2P 1A1", "T5J 1A1", "K1A 0A1", "R3B 1A1"],
            "phones": ["+14165551234", "+16045551234", "+15145551234", "+14035551234", "+17805551234"],
            "email_domains": ["gmail.com", "yahoo.ca", "outlook.com"]
        },
        "Germany": {
            "first_names": ["Max", "Alexander", "Paul", "Lukas", "Felix", "Leon", "Jonas", "David", "Julian", "Luca"],
            "last_names": ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann"],
            "addresses": ["Hauptstrasse 1", "Bahnhofstrasse 10", "Schillerstrasse 5", "Goethestrasse 8", "Karlstrasse 12"],
            "cities": ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf"],
            "postcodes": ["10115", "80331", "20095", "50667", "60311", "70173", "40213"],
            "phones": ["+49301234567", "+49891234567", "+49401234567", "+492211234567", "+49691234567"],
            "email_domains": ["gmail.com", "web.de", "gmx.de"]
        },
        "France": {
            "first_names": ["Lucas", "Louis", "Jules", "Gabriel", "Raphaël", "Arthur", "Léo", "Paul", "Nathan", "Hugo"],
            "last_names": ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau"],
            "addresses": ["10 Rue de la Paix", "25 Avenue des Champs-Élysées", "5 Boulevard Saint-Germain", "15 Rue de Rivoli", "8 Place de la Concorde"],
            "cities": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg"],
            "postcodes": ["75001", "13001", "69001", "31000", "06000", "44000", "67000"],
            "phones": ["+33123456789", "+33491234567", "+33472123456", "+33561123456", "+33493123456"],
            "email_domains": ["gmail.com", "yahoo.fr", "orange.fr"]
        },
        "Italy": {
            "first_names": ["Leonardo", "Francesco", "Alessandro", "Lorenzo", "Mattia", "Andrea", "Gabriele", "Riccardo", "Tommaso", "Edoardo"],
            "last_names": ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco"],
            "addresses": ["Via Roma 1", "Corso Vittorio Emanuele 10", "Piazza Duomo 5", "Via Garibaldi 8", "Viale dei Mille 12"],
            "cities": ["Rome", "Milan", "Naples", "Turin", "Florence", "Bologna", "Venice"],
            "postcodes": ["00100", "20100", "80100", "10100", "50100", "40100", "30100"],
            "phones": ["+39061234567", "+39021234567", "+39081234567", "+390111234567", "+390551234567"],
            "email_domains": ["gmail.com", "libero.it", "yahoo.it"]
        },
        "Netherlands": {
            "first_names": ["Daan", "Sem", "Lucas", "Milan", "Levi", "Luuk", "Finn", "Bram", "Jesse", "Thomas"],
            "last_names": ["de Jong", "Jansen", "de Vries", "Bakker", "Visser", "Smit", "Meijer", "de Boer", "Mulder", "Bos"],
            "addresses": ["Damrak 1", "Kalverstraat 10", "Leidsestraat 5", "Herengracht 8", "Prinsengracht 12"],
            "cities": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", "Groningen", "Tilburg"],
            "postcodes": ["1012AB", "3011AA", "2511AA", "3511AA", "5611AA", "9711AA", "5011AA"],
            "phones": ["+31201234567", "+31101234567", "+31701234567", "+31301234567", "+31401234567"],
            "email_domains": ["gmail.com", "hotmail.nl", "outlook.com"]
        },
        "India": {
            "first_names": ["Aarav", "Vihaan", "Vivaan", "Ananya", "Diya", "Aditya", "Kabir", "Sai", "Ishaan", "Myra"],
            "last_names": ["Kumar", "Sharma", "Singh", "Patel", "Verma", "Reddy", "Gupta", "Joshi", "Nair", "Malhotra"],
            "addresses": ["MG Road 1", "Connaught Place 10", "Banjara Hills 5", "Koramangala 8", "Salt Lake City 12"],
            "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune"],
            "postcodes": ["400001", "110001", "560001", "500001", "600001", "700001", "411001"],
            "phones": ["+91221234567", "+91111234567", "+91801234567", "+91401234567", "+91441234567"],
            "email_domains": ["gmail.com", "yahoo.co.in", "rediffmail.com"]
        },
        "Pakistan": {
            "first_names": ["Muhammad", "Ali", "Hamza", "Hassan", "Hussain", "Omar", "Usman", "Zain", "Ayesha", "Fatima"],
            "last_names": ["Khan", "Malik", "Butt", "Chaudhry", "Raja", "Mirza", "Bukhari", "Abbasi", "Shah", "Qureshi"],
            "addresses": ["Gulberg 1", "Defence Housing Authority 10", "Blue Area 5", "Gulshan-e-Iqbal 8", "Faisal Town 12"],
            "cities": ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar"],
            "postcodes": ["74000", "54000", "44000", "46000", "38000", "60000", "25000"],
            "phones": ["+92211234567", "+92421234567", "+92511234567", "+92511234567", "+92411234567"],
            "email_domains": ["gmail.com", "yahoo.com", "hotmail.com"]
        },
        "China": {
            "first_names": ["Wei", "Ming", "Li", "Juan", "Hui", "Qiang", "Fang", "Yong", "Na", "Tao"],
            "last_names": ["Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou"],
            "addresses": ["Chang'an Avenue 1", "Nanjing Road 10", "Huaihai Road 5", "Zhongshan Road 8", "Renmin Road 12"],
            "cities": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Tianjin", "Chongqing", "Wuhan"],
            "postcodes": ["100000", "200000", "510000", "518000", "300000", "400000", "430000"],
            "phones": ["+86101234567", "+86211234567", "+86201234567", "+867551234567", "+86221234567"],
            "email_domains": ["gmail.com", "qq.com", "163.com"]
        },
        "Russia": {
            "first_names": ["Alexander", "Dmitry", "Maxim", "Sergey", "Andrey", "Alexey", "Vladimir", "Ivan", "Mikhail", "Nikolay"],
            "last_names": ["Ivanov", "Smirnov", "Kuznetsov", "Popov", "Sokolov", "Lebedev", "Kozlov", "Novikov", "Morozov", "Petrov"],
            "addresses": ["Tverskaya Street 1", "Nevsky Prospect 10", "Lenin Street 5", "Pushkin Street 8", "Gorky Street 12"],
            "cities": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Nizhny Novgorod", "Kazan", "Chelyabinsk"],
            "postcodes": ["101000", "190000", "630000", "620000", "603000", "420000", "454000"],
            "phones": ["+74951234567", "+78121234567", "+73831234567", "+73431234567", "+78311234567"],
            "email_domains": ["gmail.com", "yandex.ru", "mail.ru"]
        },
        "Switzerland": {
            "first_names": ["Liam", "Noah", "Luca", "Elias", "Finn", "Leon", "Jan", "Simon", "Timo", "Nico"],
            "last_names": ["Meier", "Müller", "Schmid", "Keller", "Weber", "Steiner", "Frei", "Gerber", "Brunner", "Baumann"],
            "addresses": ["Bahnhofstrasse 1", "Rue de la Confédération 10", "Via Nassa 5", "Avenue de la Gare 8", "Limmatquai 12"],
            "cities": ["Zurich", "Geneva", "Bern", "Basel", "Lausanne", "Lucerne", "St. Gallen"],
            "postcodes": ["8000", "1200", "3000", "4000", "1000", "6000", "9000"],
            "phones": ["+41441234567", "+41221234567", "+41311234567", "+41611234567", "+41211234567"],
            "email_domains": ["gmail.com", "bluewin.ch", "outlook.com"]
        },
        "South Korea": {
            "first_names": ["Min-jun", "Seo-jun", "Ha-joon", "Ji-ho", "Eun-woo", "Si-woo", "Do-yoon", "Ye-jun", "Jae-won", "Hyun-woo"],
            "last_names": ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Cho", "Yoon", "Jang", "Lim"],
            "addresses": ["Gangnam-daero 1", "Myeongdong 10", "Hongdae 5", "Itaewon 8", "Jongno 12"],
            "cities": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju", "Ulsan"],
            "postcodes": ["04524", "48000", "22000", "41900", "34800", "61000", "44000"],
            "phones": ["+82212345678", "+825112345678", "+823212345678", "+825312345678", "+824212345678"],
            "email_domains": ["gmail.com", "naver.com", "daum.net"]
        },
        "North Korea": {
            "first_names": ["Myong", "Chol", "Yong", "Jin", "Song", "Hyok", "Sun", "Hui", "Ok", "Kyong"],
            "last_names": ["Kim", "Ri", "Pak", "Choe", "Jon", "An", "Kang", "Han", "Ryu", "So"],
            "addresses": ["Pyongyang Street 1", "Kim Il-sung Square 10", "Munsu Street 5", "Tongil Street 8", "Ryomyong Street 12"],
            "cities": ["Pyongyang", "Hamhung", "Chongjin", "Nampo", "Wonsan", "Sinuiju", "Hyesan"],
            "postcodes": ["99901", "99902", "99903", "99904", "99905", "99906", "99907"],
            "phones": ["+85021234567", "+85031234567", "+85041234567", "+85051234567", "+85061234567"],
            "email_domains": ["gmail.com", "yahoo.com"],
            "note": "⚠️ بيانات تمثيلية"
        },
        "Japan": {
            "first_names": ["Haruto", "Sota", "Yuto", "Riku", "Kaito", "Rin", "Hinata", "Sakura", "Yuna", "Aoi"],
            "last_names": ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato"],
            "addresses": ["Shibuya 1-1-1", "Shinjuku 2-2-2", "Ginza 3-3-3", "Roppongi 4-4-4", "Akihabara 5-5-5"],
            "cities": ["Tokyo", "Osaka", "Yokohama", "Nagoya", "Sapporo", "Fukuoka", "Kobe"],
            "postcodes": ["100-0001", "530-0001", "220-0001", "460-0001", "060-0001", "810-0001", "650-0001"],
            "phones": ["+81312345678", "+81612345678", "+814512345678", "+815212345678", "+811112345678"],
            "email_domains": ["gmail.com", "yahoo.co.jp", "docomo.ne.jp"]
        }
    }
    
    if country not in countries_data:
        country = "USA"
    
    data = countries_data[country]
    
    first = random.choice(data["first_names"])
    last = random.choice(data["last_names"])
    name = f"{first} {last}"
    
    address = random.choice(data["addresses"])
    city = random.choice(data["cities"])
    phone = random.choice(data["phones"])
    
    if "states" in data:
        state = random.choice(data["states"])
    elif "provinces" in data:
        state = random.choice(data["provinces"])
    elif "postcodes" in data:
        state = "N/A"
    else:
        state = "N/A"
    
    if "zip_codes" in data:
        postcode = random.choice(data["zip_codes"])
    elif "postcodes" in data:
        postcode = random.choice(data["postcodes"])
    else:
        postcode = "00000"
    
    email_domain = random.choice(data["email_domains"])
    email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{email_domain}"
    
    result = f"""🌍 **Fake Info - {country}**
━━━━━━━━━━━━━━━━
👤 **Name:** {name}
📧 **Email:** {email}
🏠 **Address:** {address}
🌆 **City:** {city}
📍 **State/Province:** {state}
📮 **Postal Code:** {postcode}
📞 **Phone:** {phone}
━━━━━━━━━━━━━━━━"""
    
    return result

def get_all_countries():
    return ["USA", "UK", "Canada", "Germany", "France", "Italy", "Netherlands", "India", "Pakistan", "China", "Russia", "Switzerland", "South Korea", "North Korea", "Japan"]