import streamlit as st
import spacy
from spacy.matcher import PhraseMatcher

# Configuração da página Streamlit (Clean e Instrutivo)
st.set_page_config(
    page_title="Classificador de Solicitações | Banco Digital",
    page_icon="🏦",
    layout="centered"
)

# Carrega o modelo de linguagem em português do spaCy
# Usamos o st.cache_resource para não carregar o modelo toda vez que a tela atualizar
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("pt_core_news_sm")
    except OSError:
        st.error("Modelo do spaCy não encontrado. Execute: python -m spacy download pt_core_news_sm")
        st.stop()

nlp = load_spacy_model()

# Dicionário de intenções e suas palavras-chave associadas
INTENTS = {
    "Bloqueio de Cartão": ["bloquear cartão", "perdi meu cartão", "roubaram meu cartão", "cancelar cartão", "bloqueio"],
    "Segunda Via de Boleto": ["segunda via", "2 via", "2ª via", "novo boleto", "fatura atrasada", "segunda via de boleto"],
    "Empréstimo": ["simular empréstimo", "pedir empréstimo", "crédito pessoal", "taxa de juros"],
    "Acesso à Conta": ["esqueci a senha", "app não abre", "recuperar acesso", "senha bloqueada"]
}

# Configurando o PhraseMatcher do spaCy
matcher = PhraseMatcher(nlp.vocab, attr="LOWER") # attr="LOWER" ignora letras maiúsculas/minúsculas

for intent, keywords in INTENTS.items():
    patterns = [nlp.make_doc(text) for text in keywords]
    matcher.add(intent, patterns)

def classify_request(text):
    """Função que processa o texto e retorna a intenção baseada no matcher."""
    doc = nlp(text)
    matches = matcher(doc)
    
    found_intents = set()
    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id] # Pega o nome da intenção (ex: "Bloqueio de Cartão")
        found_intents.add(rule_id)
        
    return list(found_intents)

# ==========================================
# INTERFACE COM STREAMLIT
# ==========================================

st.title("🏦 Portal de Triagem de Clientes")
st.markdown("""
Bem-vindo ao sistema de análise de solicitações. 
Cole a mensagem do cliente abaixo para classificar automaticamente a intenção e agilizar o atendimento.
""")

st.divider()

# Área de input do usuário
user_input = st.text_area(
    "Mensagem do Cliente:", 
    placeholder="Ex: Olá, perdi minha carteira hoje cedo e preciso bloquear cartão urgente!!",
    height=150
)

# Botão de ação
if st.button("Analisar Solicitação", type="primary"):
    if not user_input.strip():
        st.warning("⚠️ Por favor, insira uma mensagem para análise.")
    else:
        with st.spinner("Analisando a mensagem..."):
            intents = classify_request(user_input)
            
            st.subheader("Resultado da Análise")
            
            if intents:
                for intent in intents:
                    # Cores dinâmicas para alertas críticos
                    if intent == "Bloqueio de Cartão":
                        st.error(f"🚨 **ALERTA CRÍTICO:** {intent} (Encaminhar para fila prioritária)")
                    else:
                        st.success(f"✅ **Intenção identificada:** {intent}")
            else:
                st.info("🤷 **Nenhuma intenção clara identificada.** Encaminhar para transbordo humano (Atendimento Geral).")
                
            # Exibe como o spaCy processou as palavras para fins educativos da equipe
            with st.expander("Ver detalhes do processamento (Logs)"):
                st.write("**Tokens analisados na frase:**")
                doc = nlp(user_input)
                tokens = [token.text for token in doc if not token.is_punct]
                st.write(tokens)