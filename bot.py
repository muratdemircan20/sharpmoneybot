import requests

# --- 1. AYARLAR ---
API_KEY = "b73ced4f1e88bb5b105b17625384e834"  # The Odds API anahtarını buraya yapıştır
TELEGRAM_TOKEN = "8826592187:AAEIVu7gi6ISPTBRj0ONRK4JwsK62asp4Ro"
CHAT_ID = "7460333970"

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
    # Örnek olarak Süper Lig veya popüler ligler üzerinden tarama yapılır
    url = f"https://api.the-odds-api.com/v4/sports/soccer_turkey_super_lig/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"API Hatası: {response.text}")
            return
        
        data = response.json()
        if not data:
            print("Şu an aktif maç oranı bulunamadı.")
            return

        signal_found = False
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
                            if abs(deviation) >= 2.5:
                                msg = (
                                    f"🚨 *Sharp Money Sinyali!* 🚨\n\n"
                                    f"⚽ *Maç:* {home_team} vs {away_team}\n"
                                    f"🎯 *Seçim:* {outcome}\n"
                                    f"📌 *Pinnacle Oranı:* {pin_price}\n"
                                    f"📊 *Piyasa Ortalaması:* {avg_price:.2f}\n"
                                    f"📈 *Sapma:* %{deviation:.2f}"
                                )
                                send_telegram_message(msg)
                                signal_found = True

        if not signal_found:
            print("Tarama tamamlandı: Kriterlere uyan değer bulunamadı.")

    except Exception as e:
        print(f"Tarama sırasında hata: {e}")

if __name__ == "__main__":
    check_odds()
