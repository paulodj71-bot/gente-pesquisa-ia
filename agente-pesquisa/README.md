# 🔍 Super Agente de Pesquisa Multi-Modelos

Este é um MVP (Mínimo Produto Viável) de um agente autônomo de pesquisa de mercado e inteligência. Ele combina o poder de busca em tempo real do Google com o processamento analítico das três maiores inteligências artificiais do mercado.

## 🚀 Como Funciona o Fluxo de Inteligência
1. **Coleta de Fatos:** O agente faz uma varredura em tempo real no Google Custom Search API.
2. **Análise Técnica:** O **ChatGPT (GPT-4o)** extrai os dados frios, estatísticas e pontos técnicos.
3. **Mapeamento de Tendências:** O **Gemini 1.5 Pro** projeta os impactos futuros e traz insights criativos.
4. **Editor-Chefe:** O **Claude 3.5 Sonnet** atua como revisor crítico, cruza as respostas, elimina alucinações das outras IAs e redige o relatório final unificado.

## 🛠️ Tecnologias Utilizadas
- **Interface:** Streamlit (Python)
- **Modelos de Linguagem:** OpenAI API, Anthropic API, Google Generative AI API
- **Busca:** Google Programmable Search Engine API

## 🔒 Configuração de Variáveis de Ambiente (Para Deploy)
Para rodar de forma segura em produção (SaaS), o app busca as seguintes chaves nas Secrets do servidor:
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_SEARCH_KEY`
- `GOOGLE_CX`
