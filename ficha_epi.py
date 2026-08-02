import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
import os

st.set_page_config(page_title="Ficha de EPI", layout="wide")

ARQUIVO_MEMORIA = "historico_epis.csv"

# Cria o arquivo de memória com as colunas novas
if not os.path.exists(ARQUIVO_MEMORIA):
    df_vazio = pd.DataFrame(columns=[
        "Nome", "Empresa", "Setor", "Funcao", "CTPS", "DataAdm",
        "Calcado", "Calca", "Camisa", "Data", "EPI", "CA"
    ])
    df_vazio.to_csv(ARQUIVO_MEMORIA, index=False)

def carregar_historico(nome):
    df = pd.read_csv(ARQUIVO_MEMORIA)
    return df[df["Nome"].str.lower() == nome.lower()]

def gerar_pdf(dados, historico_df):
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=False)
    
    # --- PÁGINA 1 (FRENTE) ---
    pdf.add_page()
    # Usa a imagem da frente como fundo (A4 = 210x297mm)
    pdf.image("31442.png", x=0, y=0, w=210, h=297)
    
    pdf.set_font("Arial", "B", 10)
    
    # Carimbando os dados do Cabeçalho (Coordenadas X, Y aproximadas)
    pdf.text(35, 23, str(dados.get('Empresa', '')))
    pdf.text(165, 23, str(dados.get('Calcado', '')))
    
    pdf.text(25, 36, str(dados.get('Setor', '')))
    pdf.text(160, 36, str(dados.get('Calca', '')))
    
    pdf.text(28, 48, str(dados.get('Funcao', '')))
    pdf.text(160, 48, str(dados.get('Camisa', '')))
    
    pdf.text(45, 60, str(dados.get('Nome', '')))
    pdf.text(160, 60, str(dados.get('DataAdm', '')))
    
    pdf.text(50, 72, str(dados.get('CTPS', '')))
    
    # Carimbando o Histórico na Tabela
    y_inicial = 188  # Altura da primeira linha da tabela
    passo_y = 8      # Distância entre as linhas
    
    pdf.set_font("Arial", "", 9)
    for index, row in historico_df.iterrows():
        if index < 12: # Cabem cerca de 12 linhas na frente
            y_atual = y_inicial + (index * passo_y)
            pdf.text(12, y_atual, str(row['Data']))
            pdf.text(40, y_atual, str(row['EPI']))
            pdf.text(110, y_atual, str(row['CA']))
            pdf.text(145, y_atual, "Assinado Digitalmente")
    
    # --- PÁGINA 2 (VERSO) - Se tiver muitos itens ---
    if len(historico_df) > 12:
        pdf.add_page()
        pdf.image("31443.png", x=0, y=0, w=210, h=297)
        y_inicial_verso = 25
        
        for index, row in historico_df.iterrows():
            if index >= 12:
                linha_verso = index - 12
                y_atual = y_inicial_verso + (linha_verso * passo_y)
                pdf.text(12, y_atual, str(row['Data']))
                pdf.text(40, y_atual, str(row['EPI']))
                pdf.text(110, y_atual, str(row['CA']))
                pdf.text(145, y_atual, "Assinado Digitalmente")
        
    nome_arquivo_pdf = f"Ficha_{dados['Nome'].replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo_pdf)
    return nome_arquivo_pdf

# ================= INTERFACE DO SITE =================

st.title("🛡️ Emissão de Ficha de EPI")

busca_nome = st.text_input("Nome Completo do Colaborador:")

# Valores padrão
empresa, setor, funcao, ctps, data_adm = "", "", "", "", ""
calcado, calca, camisa = "", "", ""

if busca_nome:
    hist = carregar_historico(busca_nome)
    if not hist.empty:
        st.success(f"✅ Colaborador encontrado! ({len(hist)} EPIs já retirados).")
        ultima = hist.iloc[-1]
        empresa, setor, funcao = ultima['Empresa'], ultima['Setor'], ultima['Funcao']
        ctps, data_adm = ultima['CTPS'], ultima['DataAdm']
        calcado, calca, camisa = ultima['Calcado'], ultima['Calca'], ultima['Camisa']

with st.expander("📝 Dados do Cabeçalho (Preencha ou Atualize)"):
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input("Empresa", value=empresa)
        setor = st.text_input("Setor", value=setor)
        funcao = st.text_input("Função", value=funcao)
        ctps = st.text_input("Carteira de Trabalho", value=ctps)
        data_adm = st.text_input("Data de Admissão", value=data_adm)
    with col2:
        calcado = st.text_input("Calçado Nº", value=calcado)
        calca = st.text_input("Calça Nº/Tam", value=calca)
        camisa = st.text_input("Camisa Nº/Tam", value=camisa)

st.markdown("### Entrega de Hoje")
col_epi1, col_epi2 = st.columns(2)
with col_epi1:
    epi_nome = st.text_input("Material Entregue")
    data_entrega = st.date_input("Data").strftime("%d/%m/%Y")
with col_epi2:
    ca_epi = st.text_input("C.A.")

st.info("Assinatura do Colaborador:")
canvas_result = st_canvas(stroke_width=2, height=100, width=350, drawing_mode="freedraw")

if st.button("💾 Salvar e Gerar Ficha PDF Oficial", type="primary"):
    if not busca_nome or not epi_nome:
        st.error("Preencha o Nome e o Material Entregue.")
    else:
        novo_registro = pd.DataFrame([{
            "Nome": busca_nome, "Empresa": empresa, "Setor": setor, "Funcao": funcao,
            "CTPS": ctps, "DataAdm": data_adm, "Calcado": calcado, "Calca": calca, "Camisa": camisa,
            "Data": data_entrega, "EPI": epi_nome, "CA": ca_epi
        }])
        
        df_completo = pd.read_csv(ARQUIVO_MEMORIA)
        df_completo = pd.concat([df_completo, novo_registro], ignore_index=True)
        df_completo.to_csv(ARQUIVO_MEMORIA, index=False)
        
        hist_atualizado = carregar_historico(busca_nome)
        dados_colab = {"Nome": busca_nome, "Empresa": empresa, "Setor": setor, "Funcao": funcao, "CTPS": ctps, "DataAdm": data_adm, "Calcado": calcado, "Calca": calca, "Camisa": camisa}
        
        arquivo_pdf = gerar_pdf(dados_colab, hist_atualizado)
        st.success("Ficha gerada com sucesso!")
        
        with open(arquivo_pdf, "rb") as f:
            st.download_button("📥 Baixar PDF Idêntico ao Original", f, file_name=arquivo_pdf, mime="application/pdf", type="primary")
            
