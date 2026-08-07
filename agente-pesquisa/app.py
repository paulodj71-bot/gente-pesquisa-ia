import streamlit as st
import requests
from openai import OpenAI
import google.generativeai as gemini
from anthropic import Anthropic

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Super Agente de Pesquisa", 
    page_icon="🔍", 
    layout="wide"
)

# --- CONFIGURAÇÃO DAS CHAVES DE API ---
# Você pode colar aqui ou usar a barra lateral do Streamlit para preencher com segurança
OPENAI_API_KEY = st.sidebar.text_input("OpenAI API Key", type="password")
GEMINI_API_KEY = st.sidebar.text_input("Gemini API Key", type="password")
ANTHROPIC_API_KEY = st.sidebar.text_input("Claude API Key", type="password")
GOOGLE_SEARCH_KEY = st.sidebar.text_input("Google Search Key", type="password")
GOOGLE_CX = st.sidebar.text_input("Search Engine ID (CX)", type="password")

# --- FUNÇÕES DO AGENTE (LÓGICA) ---

def buscar_no_google(termo_pesquisa, api_key, cx):
    url = "https://googleapis.com"
    params = {"q": termo_pesquisa, "key": api_key, "cx": cx, "num": 4}
    try:
        response = requests.get(url, params=params).json()
        contexto = ""
        if "items" in response:
            for item in response["items"]:
                contexto += f"Título: {item['title']}\nLink: {item['link']}\nResumo: {item['snippet']}\n\n"
        return contexto if contexto else "Nenhum resultado recente encontrado."
    except Exception as e:
        return f"Erro na busca: {str(e)}"

def consultar_chatgpt(contexto_web, pergunta, api_key):
    client = OpenAI(api_key=api_key)
    prompt = f"Contexto da Web:\n{contexto_web}\n\nExtraia os fatos principais e dados técnicos sobre: {pergunta}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices.message.content

def consultar_gemini(contexto_web, pergunta, api_key):
    gemini.configure(api_key=api_key)
    prompt = f"Contexto da Web:\n{contexto_web}\n\nIdentifique tendências futuras e insights criativos sobre: {pergunta}"
    model = gemini.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

def consolidar_com_claude(pergunta, dados_web, resp_gpt, resp_gemini, api_key):
    client = Anthropic(api_key=api_key)
    prompt = f"""
    Você é um Agente Consolidador Sênior de Pesquisa. Crie o relatório definitivo sobre: "{pergunta}"
    
    FONTES BRUTAS DA WEB:
    {dados_web}
    
    ANÁLISE DO CHATGPT:
    {resp_gpt}
    
    INSIGHTS DO GEMINI:
    {resp_gemini}
    
    DIRETRIZES:
    1. Mescle a precisão do ChatGPT com a visão de futuro do Gemini.
    2. Valide as informações cruzando com as fontes da Web para evitar alucinações.
    3. Use formatação Markdown elegante com títulos, subtítulos e marcadores.
    4. Crie uma seção final listando os links das fontes utilizadas.
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# --- INTERFACE GRÁFICA (STREAMLIT) ---

st.title("🔍 Super Agente de Pesquisa Multi-Modelos")
st.caption("Google Search + ChatGPT + Gemini unificados e consolidados pela inteligência crítica do Claude.")

# Campo de entrada da pesquisa
pergunta_usuario = st.text_input(
    "O que você deseja pesquisar em profundidade?", 
    placeholder="Ex: Regulamentação de Inteligência Artificial na Europa e impactos no Brasil"
)

if st.button("Iniciar Pesquisa Avançada", type="primary"):
    # Validação rápida de chaves preenchidas
    if not all([OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_SEARCH_KEY, GOOGLE_CX]):
        st.error("⚠️ Por favor, preencha todas as chaves de API na barra lateral esquerda antes de começar.")
    elif not pergunta_usuario:
        st.warning("⚠️ Digite um tema para pesquisar.")
    else:
        # Criando a área de status para o usuário acompanhar o progresso
        with st.status("Executando agente de pesquisa...", expanded=True) as status:
            
            st.write("🌐 Consultando o Google em tempo real...")
            dados_web = buscar_no_google(pergunta_usuario, GOOGLE_SEARCH_KEY, GOOGLE_CX)
            
            st.write("🤖 ChatGPT extraindo dados técnicos...")
            resposta_gpt = consultar_chatgpt(dados_web, pergunta_usuario, OPENAI_API_KEY)
            
            st.write("♊ Gemini gerando insights e tendências...")
            resposta_gemini = consultar_gemini(dados_web, pergunta_usuario, GEMINI_API_KEY)
            
            st.write("🦉 Claude editando e consolidando o relatório final...")
            relatorio_final = consolidar_com_claude(pergunta_usuario, dados_web, resposta_gpt, resposta_gemini, ANTHROPIC_API_KEY)
            
            status.update(label="Pesquisa concluída com sucesso!", state="complete", expanded=False)
        
        # Exibição dos resultados organizados em abas
        aba_final, aba_bastidores = st.tabs(["📋 Relatório Consolidado", "⚙️ Análises Individuais (Bastidores)"])
        
        with aba_final:
            st.subheader("Relatório Final de Inteligência")
            st.markdown(relatorio_final)
            
            # Botão para baixar o relatório em Markdown
            st.download_button(
                label="📥 Baixar Relatório (.md)",
                data=relatorio_final,
                file_name=f"relatorio_pesquisa.md",
                mime="text/markdown"
            )
            
        with aba_bastidores:
            st.warning("Aqui estão as respostas brutas geradas por cada IA antes da revisão final do Claude:")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🤖 ChatGPT")
                st.write(resposta_gpt)
            with col2:
                st.subheader("♊ Gemini")
                st.write(resposta_gemini)
                
            st.subheader("🌐 Fontes do Google Encontradas")
            st.code(dados_web, language="text")
