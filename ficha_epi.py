import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
import os
from PIL import Image

st.set_page_config(page_title="Ficha de EPI Digital", layout="wide")

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."
ARQUIVO_MEMORIA = os.path.join(DIRETORIO_ATUAL, "historico_epis.csv")

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
            return df[df["Nome"].str.lower() == nome.strip().lower()]
    return pd.DataFrame(columns=["Nome", "Empresa", "Setor", "Funcao", "CTPS", "DataAdm", "Calcado", "Calca", "TamCalca", "Camisa", "TamCamisa", "Data", "EPI", "CA"])

def gerar_pdf(dados, historico_df, imagem_assinatura=None):
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=False)
    
    # --- PÁGINA 1 (FRENTE DA FICHA) ---
    pdf.add_page()
    img_frente = os.path.join(DIRETORIO_ATUAL, "31442.png")
    if os.path.exists(img_frente):
        pdf.image(img_frente, x=0, y=0, w=210, h=297)
    
    pdf.set_font("Arial", "", 10)
    
    # Cabeçalho - Posições exatas na ficha
    pdf.text(20, 21.5, str(dados.get('Empresa', '')))
    pdf.text(142, 21.5, str(dados.get('Calcado', '')))
    
    pdf.text(16, 29.5, str(dados.get('Setor', '')))
    pdf.text(142, 29.5, str(dados.get('Calca', '')))
    pdf.text(182, 29.5, str(dados.get('TamCalca', '')))
    
    pdf.text(22, 37.5, str(dados.get('Funcao', '')))
    pdf.text(142, 37.5, str(dados.get('Camisa', '')))
    pdf.text(182, 37.5, str(dados.get('TamCamisa', '')))
    
    pdf.text(35, 45.5, str(dados.get('Nome', '')))
    pdf.text(160, 45.5, str(dados.get('DataAdm', '')))
    
    pdf.text(45, 53.5, str(dados.get('CTPS', '')))
    
    # Insere a assinatura desenhada na frente
    if imagem_assinatura is not None:
        caminho_ass = "temp_assinatura.png"
        imagem_assinatura.save(caminho_ass)
        pdf.image(caminho_ass, x=75, y=110, w=60, h=18)
        if os.path.exists(caminho_ass):
            os.remove(caminho_ass)

    # Tabela de Histórico da Frente
    y_inicial = 145
    passo_y = 7.3
    
    for index, row in historico_df.iterrows():
        if index < 14:
            y_atual = y_inicial + (index * passo_y)
            pdf.text(12, y_atual, str(row['Data']))
            pdf.text(30, y_atual, str(row['EPI']))
            pdf.text(98, y_atual, str(row['CA']))
            pdf.text(138, y_atual, "Entregue")
            
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
                pdf.text(30, y_atual, str(row['EPI']))
                pdf.text(98, y_atual, str(row['CA']))
                pdf.text(138, y_atual, "Entregue")
        
    nome_arquivo_pdf = f"Ficha_{dados['Nome'].replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo_pdf)
    return nome_arquivo_pdf

# ================= INTERFACE DO SITE =================

st.title("🛡️ Sistema de Ficha de EPI")

# Gerencia o estado dos campos para preenchimento automático
if "empresa" not in st.session_state:
    st.session_state.empresa = ""
    st.session_state.setor = ""
    st.session_state.funcao = ""
    st.session_state.ctps = ""
    st.session_state.data_adm = ""
    st.session_state.calcado = ""
    st.session_state.calca = ""
    st.session_state.tam_calca = ""
    st.session_state.camisa = ""
    st.session_state.tam_camisa = ""

col_b1, col_b2 = st.columns([3, 1])
with col_b1:
    input_nome = st.text_input("Digite o Nome do Funcionário:")
with col_b2:
    st.write("") # Espaçamento para alinhar o botão
    btn_buscar = st.button("🔍 Buscar", use_container_width=True)

if btn_buscar and input_nome:
    hist = carregar_historico(input_nome)
    if not hist.empty:
        st.success(f"✅ Histórico encontrado! ({len(hist)} EPIs registrados).")
        ultima = hist.iloc[-1]
        st.session_state.empresa = str(ultima.get('Empresa', ''))
        st.session_state.setor = str(ultima.get('Setor', ''))
        st.session_state.funcao = str(ultima.get('Funcao', ''))
        st.session_state.ctps = str(ultima.get('CTPS', ''))
        st.session_state.data_adm = str(ultima.get('DataAdm', ''))
        st.session_state.calcado = str(ultima.get('Calcado', ''))
        st.session_state.calca = str(ultima.get('Calca', ''))
        st.session_state.tam_calca = str(ultima.get('TamCalca', ''))
        st.session_state.camisa = str(ultima.get('Camisa', ''))
        st.session_state.tam_camisa = str(ultima.get('TamCamisa', ''))
    else:
        st.warning("⚠️ Nenhum histórico anterior encontrado para este nome. Preencha os dados abaixo.")

with st.expander("📝 Preencher / Atualizar Dados do Funcionário", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input("Empresa", value=st.session_state.empresa)
        setor = st.text_input("Setor", value=st.session_state.setor)
        funcao = st.text_input("Função", value=st.session_state.funcao)
        ctps = st.text_input("Carteira de Trabalho", value=st.session_state.ctps)
        data_adm = st.text_input("Data de Admissão", value=st.session_state.data_adm)
    with col2:
        calcado = st.text_input("Calçado Nº", value=st.session_state.calcado)
        calca = st.text_input("Calça Nº", value=st.session_state.calca)
        tam_calca = st.text_input("Tam. Calça", value=st.session_state.tam_calca)
        camisa = st.text_input("Camisa Nº", value=st.session_state.camisa)
        tam_camisa = st.text_input("Tam. Camisa", value=st.session_state.tam_camisa)

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
    if not input_nome or not epi_nome:
        st.error("Preencha o Nome do funcionário e o Material Entregue.")
    else:
        img_assinatura = None
        if canvas_result.image_data is not None:
            input_array = canvas_result.image_data
            img_assinatura = Image.fromarray(input_array.astype('uint8'), mode="RGBA")

        novo_registro = pd.DataFrame([{
            "Nome": input_nome, "Empresa": empresa, "Setor": setor, "Funcao": funcao,
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
        
        hist_atualizado = carregar_historico(input_nome)
        dados_colab = {
            "Nome": input_nome, "Empresa": empresa, "Setor": setor, "Funcao": funcao,
            "CTPS": ctps, "DataAdm": data_adm, "Calcado": calcado, "Calca": calca,
            "TamCalca": tam_calca, "Camisa": camisa, "TamCamisa": tam_camisa
        }
        
        arquivo_pdf = gerar_pdf(dados_colab, hist_atualizado, img_assinatura)
        st.success("Ficha oficial gerada e salva com sucesso!")
        
        with open(arquivo_pdf, "rb") as f:
            st.download_button("📥 Baixar Ficha PDF Oficial", f, file_name=arquivo_pdf, mime="application/pdf", type="primary")
            
