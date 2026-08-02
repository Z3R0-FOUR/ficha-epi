import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
import os

st.set_page_config(page_title="Ficha de EPI Digital", layout="wide")

# Caminho seguro para a memória na nuvem
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."
ARQUIVO_MEMORIA = os.path.join(DIRETORIO_ATUAL, "historico_epis.csv")

# Garante a criação da tabela de dados caso não exista
if not os.path.exists(ARQUIVO_MEMORIA):
    df_vazio = pd.DataFrame(columns=[
        "Nome", "Empresa", "Setor", "Funcao", "CTPS", "DataAdm",
        "Calcado", "Calca", "TamCalca", "Camisa", "TamCamisa", "Data", "EPI", "CA"
    ])
    df_vazio.to_csv(ARQUIVO_MEMORIA, index=False)

def carregar_historico(nome):
    if os.path.exists(ARQUIVO_MEMORIA):
        df = pd.read_csv(ARQUIVO_MEMORIA)
        if not df.empty and "Nome" in df.columns:
            return df[df["Nome"].str.lower() == nome.lower()]
    return pd.DataFrame(columns=["Nome", "Empresa", "Setor", "Funcao", "CTPS", "DataAdm", "Calcado", "Calca", "TamCalca", "Camisa", "TamCamisa", "Data", "EPI", "CA"])

def gerar_pdf(dados, historico_df):
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=False)
    
    # --- PÁGINA 1 (FRENTE DA FICHA) ---
    pdf.add_page()
    img_frente = os.path.join(DIRETORIO_ATUAL, "31442.png")
    if os.path.exists(img_frente):
        pdf.image(img_frente, x=0, y=0, w=210, h=297)
    
    # Fonte legível e maior para o preenchimento automático
    pdf.set_font("Arial", "", 11)
    
    # Cabeçalho - Ajustado milimetricamente para a frente da ficha
    pdf.text(22, 23, str(dados.get('Empresa', '')))
    pdf.text(155, 23, str(dados.get('Calcado', '')))
    
    pdf.text(20, 31, str(dados.get('Setor', '')))
    pdf.text(145, 31, str(dados.get('Calca', '')))
    pdf.text(180, 31, str(dados.get('TamCalca', '')))
    
    pdf.text(20, 39, str(dados.get('Funcao', '')))
    pdf.text(145, 39, str(dados.get('Camisa', '')))
    pdf.text(180, 39, str(dados.get('TamCamisa', '')))
    
    pdf.text(35, 48, str(dados.get('Nome', '')))
    pdf.text(155, 48, str(dados.get('DataAdm', '')))
    
    pdf.text(35, 57, str(dados.get('CTPS', '')))
    
    # Tabela de Histórico da Frente
    y_inicial = 137
    passo_y = 7.5
    
    for index, row in historico_df.iterrows():
        if index < 14:
            y_atual = y_inicial + (index * passo_y)
            pdf.text(12, y_atual, str(row['Data']))
            pdf.text(35, y_atual, str(row['EPI']))
            pdf.text(105, y_atual, str(row['CA']))
            pdf.text(138, y_atual, "Assinado Digitalmente")
            
    # --- PÁGINA 2 (VERSO DA FICHA) ---
    if len(historico_df) > 14:
        pdf.add_page()
        img_verso = os.path.join(DIRETORIO_ATUAL, "31443.png")
        if os.path.exists(img_verso):
            pdf.image(img_verso, x=0, y=0, w=210, h=297)
            
        y_inicial_verso = 25
        for index, row in historico_df.iterrows():
            if index >= 14:
                linha_verso = index - 14
                y_atual = y_inicial_verso + (linha_verso * passo_y)
                pdf.text(12, y_atual, str(row['Data']))
                pdf.text(35, y_atual, str(row['EPI']))
                pdf.text(105, y_atual, str(row['CA']))
                pdf.text(138, y_atual, "Assinado Digitalmente")
        
    nome_arquivo_pdf = f"Ficha_{dados['Nome'].replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo_pdf)
    return nome_arquivo_pdf

# ================= INTERFACE DO SITE =================

st.title("🛡️ Sistema de Ficha de EPI")

busca_nome = st.text_input("Digite o Nome do Funcionário:")

empresa, setor, funcao, ctps, data_adm = "", "", "", "", ""
calcado, calca, tam_calca, camisa, tam_camisa = "", "", "", "", ""

if busca_nome:
    hist = carregar_historico(busca_nome)
    if not hist.empty:
        st.success(f"✅ Histórico encontrado! ({len(hist)} EPIs registrados).")
        ultima = hist.iloc[-1]
        empresa = str(ultima.get('Empresa', ''))
        setor = str(ultima.get('Setor', ''))
        funcao = str(ultima.get('Funcao', ''))
        ctps = str(ultima.get('CTPS', ''))
        data_adm = str(ultima.get('DataAdm', ''))
        calcado = str(ultima.get('Calcado', ''))
        calca = str(ultima.get('Calca', ''))
        tam_calca = str(ultima.get('TamCalca', ''))
        camisa = str(ultima.get('Camisa', ''))
        tam_camisa = str(ultima.get('TamCamisa', ''))

with st.expander("📝 Preencher / Atualizar Dados do Funcionário"):
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input("Empresa", value=empresa)
        setor = st.text_input("Setor", value=setor)
        funcao = st.text_input("Função", value=funcao)
        ctps = st.text_input("Carteira de Trabalho", value=ctps)
        data_adm = st.text_input("Data de Admissão", value=data_adm)
    with col2:
        calcado = st.text_input("Calçado Nº", value=calcado)
        calca = st.text_input("Calça Nº", value=calca)
        tam_calca = st.text_input("Tam. Calça", value=tam_calca)
        camisa = st.text_input("Camisa Nº", value=camisa)
        tam_camisa = st.text_input("Tam. Camisa", value=tam_camisa)

st.markdown("### 🛠️ Entrega Atual")
col_e1, col_e2 = st.columns(2)
with col_e1:
    epi_nome = st.text_input("Material Entregue (Ex: Bota de Segurança)")
    data_entrega = st.date_input("Data da Entrega", value=datetime.now()).strftime("%d/%m/%Y")
with col_e2:
    ca_epi = st.text_input("Número do C.A.")

st.info("Assinatura do Funcionário (Desenhe abaixo com o dedo):")
canvas_result = st_canvas(
    stroke_width=2,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=120,
    width=350,
    drawing_mode="freedraw",
    key="canvas_assinatura_principal"
)

if st.button("💾 Salvar e Gerar Ficha Oficial", type="primary", use_container_width=True):
    if not busca_nome or not epi_nome:
        st.error("Preencha o Nome do funcionário e o Material Entregue.")
    else:
        novo_registro = pd.DataFrame([{
            "Nome": busca_nome, "Empresa": empresa, "Setor": setor, "Funcao": funcao,
            "CTPS": ctps, "DataAdm": data_adm, "Calcado": calcado, "Calca": calca,
            "TamCalca": tam_calca, "Camisa": camisa, "TamCamisa": tam_camisa,
            "Data": data_entrega, "EPI": epi_nome, "CA": ca_epi
        }])
        
        if os.path.exists(ARQUIVO_MEMORIA):
            df_completo = pd.read_csv(ARQUIVO_MEMORIA)
            df_completo = pd.concat([df_completo, novo_registro], ignore_index=True)
        else:
            df_completo = novo_registro
            
        df_completo.to_csv(ARQUIVO_MEMORIA, index=False)
        
        hist_atualizado = carregar_historico(busca_nome)
        dados_colab = {
            "Nome": busca_nome, "Empresa": empresa, "Setor": setor, "Funcao": funcao,
            "CTPS": ctps, "DataAdm": data_adm, "Calcado": calcado, "Calca": calca,
            "TamCalca": tam_calca, "Camisa": camisa, "TamCamisa": tam_camisa
        }
        
        arquivo_pdf = gerar_pdf(dados_colab, hist_atualizado)
        st.success("Ficha oficial gerada e salva com sucesso!")
        
        with open(arquivo_pdf, "rb") as f:
            st.download_button("📥 Baixar Ficha PDF Oficial", f, file_name=arquivo_pdf, mime="application/pdf", type="primary")
            
