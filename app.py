
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from io import BytesIO

# ========== CONFIGURAÇÕES ==========

st.set_page_config(page_title="Gerador de Cards Superbid", layout="centered")

UTM_PARAMS = {
    "utm_source": "email",
    "utm_medium": "disparo",
    "utm_campaign": "eventos_semanal"
}

HTML_HEADER = """
<div style="max-width: 900px; margin: auto; text-align: center; background-color: #f7f7f7; padding: 30px 20px;">
  <img src="https://cdn.superbid.net/assets/logo-superbid.png" alt="Superbid Exchange" width="180">
  <h2 style="font-family: Arial, sans-serif; color: #333; margin-top: 10px;">Confira os eventos em destaque da semana</h2>
</div>
"""

HTML_FOOTER = """
<div style="max-width: 900px; margin: auto; padding: 20px; text-align: center; font-size: 12px; color: #888;">
  <p>Você está recebendo este e-mail porque se inscreveu em nossos eventos.</p>
  <p>
    <a href="https://superbid.net" style="color: #555;">superbid.net</a> |
    <a href="https://instagram.com/superbid" style="color: #555;">Instagram</a> |
    <a href="https://linkedin.com/company/superbid" style="color: #555;">LinkedIn</a>
  </p>
  <p>© 2025 Superbid. Todos os direitos reservados.</p>
</div>
"""

# ========== FUNÇÕES ==========

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
    <td style="width: 30%; padding: 15px; vertical-align: top;">
      <div style="border: 1px solid #ddd; border-radius: 10px; overflow: hidden; background: #fff; font-family: Arial, sans-serif;">
        <img src="{info['imagem']}" alt="{info['titulo']}" style="width: 100%; height: auto; border-bottom: 1px solid #eee;">
        <div style="padding: 15px;">
          <h3 style="font-size: 16px; color: #333;">{info['titulo']}</h3>
          <p style="font-size: 14px; color: #555;">{info['descricao']}</p>
          <a href="{link_param}" style="display: inline-block; margin-top: 10px; background-color: #007bff; color: white; padding: 10px 16px; text-decoration: none; border-radius: 5px; font-weight: bold;">Ver Evento</a>
        </div>
      </div>
    </td>
    """

def gerar_html_final(cards_list):
    linhas = ""
    for i in range(0, len(cards_list), 3):
        grupo = cards_list[i:i+3]
        linha = "<tr>" + "".join(grupo) + "</tr>"
        linhas += linha

    grid = f"""
    <table width="100%" style="max-width: 900px; margin: auto;">
      {linhas}
    </table>
    """

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Eventos</title></head>
<body style="font-family: Arial, sans-serif; background-color: #f0f0f0; margin:0; padding:0;">
  {HTML_HEADER}
  {grid}
  {HTML_FOOTER}
</body>
</html>"""

# ========== INTERFACE ==========

st.image("https://superbid.net/logo.png", width=120)
st.title("Gerador de Cards para E-mail - Superbid")
st.markdown("Cole abaixo os **links dos eventos** (um por linha) e clique em **Gerar Cards**.")

links_input = st.text_area("Links dos eventos", height=200, placeholder="https://superbid.net/evento/123")
https://superbid.net/evento/456")

if st.button("🚀 Gerar Cards"):
    links = [l.strip() for l in links_input.splitlines() if l.strip()]
    cards_html = []
    for link in links:
        info = extrair_info(link)
        if info:
            cards_html.append(gerar_card(info))

    html_final = gerar_html_final(cards_html)
    st.success("✅ HTML gerado com sucesso!")

    with st.expander("📄 Visualizar HTML"):
        st.components.v1.html(html_final, height=1200, scrolling=True)

    st.download_button(
        label="📥 Baixar HTML",
        data=BytesIO(html_final.encode("utf-8")),
        file_name="email.html",
        mime="text/html"
    )
