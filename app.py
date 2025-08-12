
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from io import BytesIO

st.set_page_config(page_title="Gerador de Cards Superbid", layout="centered")

UTM_PARAMS = {
    "utm_source": "email",
    "utm_medium": "disparo",
    "utm_campaign": "eventos_semanal"
}

HTML_HEADER = """
<div style='text-align: center; padding: 40px 20px; background-color: #f3f3f3;'>
    <img src='https://image.leilao.portalsuperbid.net/lib/fe3b11727564047c701675/m/1/5b925e53-5b02-421a-b045-e327ab17e19c.png' alt='Superbid Logo' width='220' />
    <h2 style='font-family: "Plus Jakarta Sans", sans-serif; font-size: 24px; color: #313234; margin-top: 10px;'>Eventos em destaque da semana</h2>
</div>
"""

HTML_FOOTER = """
<div style='text-align: center; font-family: "Plus Jakarta Sans", sans-serif; font-size: 12px; color: #6e6d6d; padding: 30px 10px;'>
    <p>Você está recebendo este e-mail porque se inscreveu em nossos eventos.</p>
    <p><a href='https://superbid.net' style='color:#8800CB;'>superbid.net</a> | 
    <a href='https://instagram.com/superbid' style='color:#8800CB;'>Instagram</a> | 
    <a href='https://linkedin.com/company/superbid' style='color:#8800CB;'>LinkedIn</a></p>
    <p>© 2025 Superbid. Todos os direitos reservados.</p>
</div>
"""

def extrair_info(url):
    try:
        r = requests.get(url, timeout=10)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')

        titulo = soup.find("meta", property="og:title") or soup.title
        desc = soup.find("meta", property="og:description")
        img = soup.find("meta", property="og:image")

        return {
            "titulo": titulo["content"] if titulo else "Evento",
            "descricao": desc["content"] if desc else "",
            "imagem": img["content"] if img else "https://via.placeholder.com/600x300",
            "link": url
        }
    except Exception as e:
        st.error(f"Erro ao processar {url}: {e}")
        return None

def adicionar_parametros(url, params=UTM_PARAMS):
    parts = list(urlparse(url))
    query = parse_qs(parts[4])
    query.update(params)
    parts[4] = urlencode(query, doseq=True)
    return urlunparse(parts)

def gerar_card(info):
    link_param = adicionar_parametros(info["link"])
    return f"""
    <div style='flex: 1 1 300px; margin: 15px; background: #fff; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.05); overflow: hidden; max-width: 340px;'>
        <img src='{info["imagem"]}' alt='{info["titulo"]}' style='width: 100%; height: auto;'>
        <div style='padding: 16px; font-family: "Plus Jakarta Sans", sans-serif;'>
            <h3 style='font-size: 18px; color: #313234; margin: 0 0 10px;'>{info["titulo"]}</h3>
            <p style='font-size: 14px; color: #666;'>{info["descricao"]}</p>
            <a href='{link_param}' style='display: inline-block; margin-top: 15px; background: linear-gradient(45deg, #8800CB, #BE00FF); color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 6px;'>Aproveite</a>
        </div>
    </div>
    """

def gerar_html_final(cards_list):
    cards_html = "".join(cards_list)
    layout = f"""
    <div style='max-width: 1080px; margin: auto; padding: 30px;'>
        <div style='display: flex; flex-wrap: wrap; justify-content: center;'>
            {cards_html}
        </div>
    </div>
    """
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <title>Eventos</title>
    <link href='https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans&display=swap' rel='stylesheet'>
</head>
<body style='margin:0; padding:0; background-color: #f3f3f3;'>
    {HTML_HEADER}
    {layout}
    {HTML_FOOTER}
</body>
</html>"""
