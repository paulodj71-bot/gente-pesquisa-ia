import streamlit as st
import requests
import os
import google.generativeai as gemini
from anthropic import Anthropic

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Super Agente de Pesquisa", 
    page_icon="🔍", 
    layout="wide"
)

# --- CARREGAMENTO SEGURO DAS CHAVES (VARIÁVEIS DE AMBIENTE / SECRETS) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GOOGLE_SEARCH_KEY = os.environ.get("GOOGLE_SEARCH_KEY")
GOOGLE_CX = os.environ.get("GOOGLE_CX")

# --- FUNÇÕES DO AGENTE DE INTELIGÊNCIA ---

def buscar_no_google(termo_pesquisa):
    url = "https://googleapis.com"
    params = {"q": termo_pesquisa, "key": GOOGLE_SEARCH_KEY, "cx": GOOGLE_CX, "num": 4}
    try:
        response = requests.get(url, params=params).json()
        contexto = ""
        if "items" in response:
            for item in response["items"]:
                contexto += f"Título: {item['title']}\nLink: {item['link']}\nResumo: {item['snippet']}\n\n"
        return contexto if contexto else "Nenhum resultado recente encontrado na web."
    except Exception as e:
        return f"Erro na busca web: {str(e)}"

def consultar_gemini(contexto_web, pergunta):
    gemini.configure(api_key=GEMINI_API_KEY)
    prompt = f"Contexto da Web:\n{contexto_web}\n\nIdentifique os fatos principais, dados numéricos, tendências futuras e insights práticos sobre: {pergunta}"
    # Atualizado para o modelo estável de nova geração
    model = gemini.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def consolidar_com_claude(pergunta, dados_web, resp_gemini):
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""
    Você é um Agente Consolidador Sênior de Pesquisa. Sua tarefa é analisar o material bruto da web e a perspectiva gerada por uma inteligência especialista para redigir o relatório definitivo de pesquisa sobre o tema: "{pergunta}"
    
    FONTES BRUTAS DA WEB:
    {dados_web}
    
    INSIGHTS E ANÁLISES (Gemini):
    {resp_gemini}
    
    DIRETRIZES DE REDAÇÃO DO RELATÓRIO:
    1. Fusão Inteligente: Combine os dados da Web com os insights do Gemini.
    2. Fact-Checking: Use os dados brutos da Web para validar informações e evitar alucinações.
    3. Sem Repetições: Elimine textos redundantes.
    4. Estrutura Profissional: Formate o texto usando Markdown elegante, títulos claros, bullet points e crie uma seção dedicada ao final listando de forma organizada os links das fontes web utilizadas.
    5. Tom: Executivo, analítico e imparcial. Tem que parecer um relatório feito por um analista humano sênior.
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content.text

# --- INTERFACE GRÁFICA DO APLICATIVO ---

st.title("🔍 Agente de Pesquisa de Mercado & Inteligência")
st.caption("Google Search + Gemini unificados e editados criticamente pelo Claude 3.5 Sonnet.")

# Campo de entrada da pesquisa do usuário
pergunta_usuario = st.text_input(
    "O que você deseja investigar em profundidade?", 
    placeholder="Ex: Regulamentação de Inteligência Artificial e seus impactos no ecossistema brasileiro"
)

if st.button("Iniciar Pesquisa Avançada", type="primary"):
    # Validação interna de segurança antes de disparar o agente
    if not all([GEMINI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_SEARCH_KEY, GOOGLE_CX]):
        st.error("⚠️ Erro de Configuração: As chaves de API necessárias não foram detectadas no ambiente do servidor.")
    elif not pergunta_usuario:
        st.warning("⚠️ Por favor, digite um tema ou pergunta antes de iniciar.")
    else:
        # Linha do tempo visual do progresso do agente
        with st.status("Agente operacional em execução...", expanded=True) as status:
            st.write("🌐 Realizando varredura em tempo real no Google...")
            dados_web = buscar_no_google(pergunta_usuario)
            
            st.write("♊ Gemini extraindo dados e mapeando tendências...")
            resposta_gemini = consultar_gemini(dados_web, pergunta_usuario)
            
            st.write("🦉 Claude assumindo a posição de Editor-Chefe para gerar o relatório final...")
            relatorio_final = consolidar_com_claude(pergunta_usuario, dados_web, resposta_gemini)
            
            status.update(label="Análise finalizada com sucesso!", state="complete", expanded=False)
        
        # Exibição do resultado final limpo em abas separadas
        aba_final, aba_bastidores = st.tabs(["📋 Relatório Consolidado", "⚙️ Dados de Inteligência Brutos"])
        
        with aba_final:
            st.subheader("Relatório de Inteligência Executiva")
            st.markdown(relatorio_final)
            
            # Recurso profissional: Baixar relatório gerado
            st.download_button(
                label="📥 Baixar Relatório Completo (.md)",
                data=relatorio_final,
                file_name="relatorio_inteligencia.md",
                mime="text/markdown"
            )
            
        with aba_bastidores:
            st.info("Abaixo estão as respostas originais do Gemini antes do tratamento e consolidação analítica do Claude.")
            
            st.subheader("♊ Gemini")
            st.write(resposta_gemini)
                
            st.subheader("🌐 Links e Textos Brutos Capturados na Web")
            st.code(dados_web, language="text")
