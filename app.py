import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from io import StringIO

# ========== CONFIG ==========
st.set_page_config(page_title="Gerador de Cards Superbid", layout="centered")

UTM_PARAMS = {
    "utm_source": "email",
    "utm_medium": "disparo",
    "utm_campaign": "eventos_semanal"
}

HTML_HEADER = """
<table width="100%" style="background-color: #f4f4f4; padding: 20px;">
  <tr>
    <td align="center">
      <img src="https://superbid.net/logo.png" alt="Superbid Logo" width="120" />
      <h2 style="margin-top: 10px;">Confira os eventos em destaque da semana</h2>
    </td>
  </tr>
</table>
"""

HTML_FOOTER = """
<table width="100%" style="background-color: #f4f4f4; padding: 20px; text-align: center; font-size: 12px;">
  <tr>
    <td>
      <p>Você está recebendo este e-mail porque se inscreveu em nossos eventos.</p>
      <p>
        <a href="https://superbid.net">superbid.net</a> |
        <a href="https://instagram.com/superbid">Instagram</a> |
        <a href="https://linkedin.com/company/superbid">LinkedIn</a>
      </p>
      <p>© 2025 Superbid. Todos os direitos reservados.</p>
    </td>
  </tr>
</table>
"""

def extrair_info(url):
    try:
        r = requests.get(url, timeout=10)
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
    <table width="100%" style="padding: 20px;">
      <tr>
        <td style="border: 1px solid #ccc; padding: 15px; border-radius: 10px;">
          <img src="{info['imagem']}" alt="{info['titulo']}" width="100%" style="border-radius: 10px;" />
          <h3>{info['titulo']}</h3>
          <p>{info['descricao']}</p>
          <a href="{link_param}"
            style="display:inline-block; padding:10px 20px; background:#007bff; color:#fff; text-decoration:none; border-radius:5px;">
            Ver Evento
          </a>
        </td>
      </tr>
    </table>
    """

def gerar_html_final(cards):
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Eventos</title></head>
<body style="font-family: Arial, sans-serif;">
  {HTML_HEADER}
  {cards}
  {HTML_FOOTER}
</body>
</html>"""

st.image("https://superbid.net/logo.png", width=120)
st.title("Gerador de Cards para E-mail - Superbid")
st.markdown("Cole abaixo os **links dos eventos** (um por linha) e clique em **Gerar Cards**.")

links_input = st.text_area("Links dos eventos", height=200, placeholder="https://superbid.net/evento/123\nhttps://superbid.net/evento/456")

if st.button("🚀 Gerar Cards"):
    links = [l.strip() for l in links_input.splitlines() if l.strip()]
    cards_html = ""
    for link in links:
        info = extrair_info(link)
        if info:
            cards_html += gerar_card(info)
    
    html_final = gerar_html_final(cards_html)
    st.success("HTML gerado com sucesso!")

    with st.expander("📄 Visualizar HTML"):
        st.code(html_final, language='html')

    st.download_button(
        label="📥 Baixar HTML",
        data=StringIO(html_final),
        file_name="email.html",
        mime="text/html"
    )
