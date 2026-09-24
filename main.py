import requests, time, threading
from flask import Flask

TOKEN = "8968618487:AAGYfCqn3mSG7HldpkwhNuoHsPCAxQqdKkY"
API_FOOT = "1ee00ea16adc17777975c935c11a5fcf"

app = Flask(__name__)
headers_foot = {"x-apisports-key": API_FOOT}

def get_pronos():
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?date={today}&timezone=Africa/Abidjan"
    try:
        data = requests.get(url, headers=headers_foot, timeout=15).json()
        fixtures = data['response'][:5]
        if not fixtures: return "Pas de matchs aujourd'hui"
        msg = f"TOP 5 SCORES DU JOUR - {today}\n\n"
        for m in fixtures:
            fid = m['fixture']['id']
            home = m['teams']['home']['name']
            away = m['teams']['away']['name']
            p_url = f"https://v3.football.api-sports.io/predictions?fixture={fid}"
            pred = requests.get(p_url, headers=headers_foot, timeout=15).json()
            if pred['response']:
                r = pred['response'][0]['predictions']
                msg += f"{home} - {away}\nScore: {r['goals']['home']}-{r['goals']['away']}\n{r['advice']}\n\n"
            time.sleep(1)
        return msg
    except Exception as e:
        return f"Erreur: {e}"

def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": chat_id, "text": text})

def bot_loop():
    last = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last+1}&timeout=20"
            res = requests.get(url, timeout=25).json()
            for u in res.get('result', []):
                last = u['update_id']
                chat = u['message']['chat']['id']
                txt = u['message'].get('text','')
                if txt == "/start":
                    send(chat, "Bienvenue! /prono pour les scores")
                elif "/prono" in txt:
                    send(chat, "Calcul...")
                    send(chat, get_pronos())
        except: time.sleep(3)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home(): return "Bot actif"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
