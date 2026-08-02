import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
import os

# Configuração da página
st.set_page_config(page_title="Ficha de EPI Digital", layout="wide")

# Arquivo de memória oculta
ARQUIVO_MEMORIA = "historico_epis.csv"

# Cria o arquivo de memória se ele não existir
if not os.path.exists(ARQUIVO_MEMORIA):
    df_vazio = pd.DataFrame(columns=["Nome", "Funcao", "Setor", "Data", "EPI", "CA"])
    df_vazio.to_csv(ARQUIVO_MEMORIA, index=False)

# Função para carregar histórico do funcionário
def carregar_historico(nome_funcionario):
    df = pd.read_csv(ARQUIVO_MEMORIA)
    return df[df["Nome"].str.lower() == nome_funcionario.lower()]

# Função para gerar o PDF
def gerar_pdf(nome, funcao, setor, historico_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    
    # Cabeçalho
    pdf.cell(200, 10, txt="FICHA DE CONTROLE DE EPI", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Nome: {nome}", ln=True)
    pdf.cell(200, 10, txt=f"Função: {funcao} | Setor: {setor}", ln=True)
    pdf.line(10, 40, 200, 40)
    
    # Termo de compromisso
    pdf.set_font("Arial", "I", 10)
    termo = "Declaro ter recebido os equipamentos de protecao abaixo relacionados, assumindo o compromisso de usa-los e conserva-los."
    pdf.multi_cell(0, 10, txt=termo)
    pdf.line(10, 60, 200, 60)
    
    # Tabela de Histórico
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "DATA", border=1)
    pdf.cell(90, 10, "MATERIAL ENTREGUE", border=1)
    pdf.cell(60, 10, "C.A.", border=1)
    pdf.ln()
    
    pdf.set_font("Arial", "", 10)
    for index, row in historico_df.iterrows():
        pdf.cell(40, 10, str(row["Data"]), border=1)
        pdf.cell(90, 10, str(row["EPI"]), border=1)
        pdf.cell(60, 10, str(row["CA"]), border=1)
        pdf.ln()
        
    nome_arquivo_pdf = f"Ficha_EPI_{nome.replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo_pdf)
    return nome_arquivo_pdf

# ================= INTERFACE =================

st.title("🛡️ Sistema de Entrega de EPI")
st.markdown("Busque o funcionário, registre a entrega e gere a ficha PDF atualizada.")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Dados do Funcionário e Entrega")
    busca_nome = st.text_input("Nome do Colaborador (Digite para buscar ou criar novo):")
    
    funcao_padrao = ""
    setor_padrao = ""
    if busca_nome:
        historico_existente = carregar_historico(busca_nome)
        if not historico_existente.empty:
            funcao_padrao = str(historico_existente.iloc[0]["Funcao"])
            setor_padrao = str(historico_existente.iloc[0]["Setor"])
            st.success(f"✅ Histórico encontrado! ({len(historico_existente)} itens já retirados).")
    
    funcao = st.text_input("Função", value=funcao_padrao)
    setor = st.text_input("Setor", value=setor_padrao)
    
    st.markdown("#### O que está sendo entregue hoje?")
    epi_nome = st.text_input("Material Entregue (Ex: Bota de Segurança)")
    ca_epi = st.text_input("Número do C.A.")
    data_entrega = st.date_input("Data da Entrega", value=datetime.now()).strftime("%d/%m/%Y")

with col2:
    st.subheader("2. Assinatura do Funcionário")
    st.info("Assine abaixo com o dedo ou mouse:")
    
    canvas_result = st_canvas(
        stroke_width=3, stroke_color="#000000", background_color="#FFFFFF",
        height=150, width=400, drawing_mode="freedraw", key="assinatura"
    )

st.markdown("---")

if st.button("💾 Salvar Entrega e Gerar PDF", type="primary", use_container_width=True):
    if not busca_nome or not epi_nome:
        st.error("Preencha o Nome do funcionário e o EPI entregue.")
    else:
        novo_registro = pd.DataFrame([{
            "Nome": busca_nome, "Funcao": funcao, "Setor": setor,
            "Data": data_entrega, "EPI": epi_nome, "CA": ca_epi
        }])
        
        df_completo = pd.read_csv(ARQUIVO_MEMORIA)
        df_completo = pd.concat([df_completo, novo_registro], ignore_index=True)
        df_completo.to_csv(ARQUIVO_MEMORIA, index=False)
        
        historico_atualizado = carregar_historico(busca_nome)
        arquivo_pdf = gerar_pdf(busca_nome, funcao, setor, historico_atualizado)
        
        st.success(f"Entrega registrada com sucesso! A ficha PDF de {busca_nome} foi atualizada.")
        
        with open(arquivo_pdf, "rb") as pdf_file:
            st.download_button(
                label="📥 Clique aqui para Baixar a Ficha em PDF",
                data=pdf_file,
                file_name=arquivo_pdf,
                mime="application/pdf",
                type="primary"
  )
          
