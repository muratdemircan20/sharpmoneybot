import requests

# --- 1. AYARLAR ---
API_KEY = "b73ced4f1e88bb5b105b17625384e834"  # The Odds API anahtarını buraya yapıştır
TELEGRAM_TOKEN = "8826592187:AAEIVu7gi6ISPTBRj0ONRK4JwsK62asp4Ro"
CHAT_ID = "7460333970"

# Colab'dan aldığımız aktif futbol liglerinin TAMAMI
LEAGUES = [
    "soccer_argentina_primera_division",
    "soccer_australia_aleague",
    "soccer_austria_bundesliga",
    "soccer_belgium_first_div",
    "soccer_brazil_campeonato",
    "soccer_brazil_serie_b",
    "soccer_chile_campeonato",
    "soccer_conmebol_copa_libertadores",
    "soccer_conmebol_copa_sudamericana",
    "soccer_denmark_superliga",
    "soccer_efl_champ",
    "soccer_england_efl_cup",
    "soccer_england_league1",
    "soccer_england_league2",
    "soccer_epl",
    "soccer_finland_veikkausliiga",
    "soccer_france_ligue_one",
    "soccer_france_ligue_two",
    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",
    "soccer_germany_dfb_pokal",
    "soccer_germany_liga3",
    "soccer_greece_super_league",
    "soccer_italy_serie_a",
    "soccer_italy_serie_b",
    "soccer_japan_j_league",
    "soccer_league_of_ireland",
    "soccer_mexico_ligamx",
    "soccer_netherlands_eredivisie",
    "soccer_norway_eliteserien",
    "soccer_poland_ekstraklasa",
    "soccer_portugal_primeira_liga",
    "soccer_russia_premier_league",
    "soccer_saudi_arabia_pro_league",
    "soccer_spain_la_liga",
    "soccer_spain_segunda_division",
    "soccer_spl",
    "soccer_sweden_allsvenskan",
    "soccer_sweden_superettan",
    "soccer_switzerland_superleague",
    "soccer_turkey_super_league",
    "soccer_uefa_champs_league",
    "soccer_uefa_champs_league_women",
    "soccer_uefa_europa_league",
    "soccer_uefa_nations_league",
    "soccer_usa_mls"
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram mesajı başarıyla gönderildi.")
        else:
            print(f"Telegram mesajı gönderilemedi: {response.text}")
    except Exception as e:
        print(f"Hata oluştu: {e}")

def check_odds():
    signal_found_total = False
    
    for league in LEAGUES:
        print(f"Taranıyor: {league}...")
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal"
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            
            data = response.json()
            if not data:
                continue

            for match in data:
                home_team = match.get('home_team')
                away_team = match.get('away_team')
                bookmakers = match.get('bookmakers', [])
                
                pinnacle_odds = None
                other_odds = []

                for bookmaker in bookmakers:
                    if bookmaker.get('key') == 'pinnacle':
                        markets = bookmaker.get('markets', [])
                        for m in markets:
                            if m.get('key') == 'h2h':
                                pinnacle_odds = {outcome['name']: outcome['price'] for outcome in m.get('outcomes', [])}
                    else:
                        markets = bookmaker.get('markets', [])
                        for m in markets:
                            if m.get('key') == 'h2h':
                                prices = {outcome['name']: outcome['price'] for outcome in m.get('outcomes', [])}
                                other_odds.append(prices)

                if pinnacle_odds and other_odds:
                    for outcome, pin_price in pinnacle_odds.items():
                        # 1.30 - 1.80 oran aralığı filtresi
                        if 1.30 <= pin_price <= 1.80:
                            matching_prices = [book[outcome] for book in other_odds if outcome in book]
                            if matching_prices:
                                avg_price = sum(matching_prices) / len(matching_prices)
                                # %2.5 ve üzeri piyasa sapması kontrolü
                                deviation = ((avg_price - pin_price) / pin_price) * 100
                                if (deviation) >= 2.5:
                                    msg = (
                                        f"🚨 *Sharp Money Sinyali!* 🚨\n\n"
                                        f"🏆 *Lig:* {league}\n"
                                        f"⚽ *Maç:* {home_team} vs {away_team}\n"
                                        f"🎯 *Seçim:* {outcome}\n"
                                        f"📌 *Pinnacle Oranı:* {pin_price}\n"
                                        f"📊 *Piyasa Ortalaması:* {avg_price:.2f}\n"
                                        f"📈 *Sapma:* %{deviation:.2f}"
                                    )
                                    send_telegram_message(msg)
                                    signal_found_total = True

        except Exception as e:
            print(f"Lig taranırken hata ({league}): {e}")

    if not signal_found_total:
        print("Tüm ligler tarandı: Kriterlere uyan değer bulunamadı.")

if __name__ == "__main__":
    check_odds()

