import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
import os
from PIL import Image

st.set_page_config(page_title="Gestão Profissional de EPI", layout="wide", page_icon="🛡️")

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."
ARQUIVO_MEMORIA = os.path.join(DIRETORIO_ATUAL, "historico_epis.csv")

if not os.path.exists(ARQUIVO_MEMORIA):
    df_vazio = pd.DataFrame(columns=[
        "Nome", "Empresa", "Setor", "Funcao", "CTPS", "DataAdm",
        "Calcado", "Calca", "TamCalca", "Camisa", "TamCamisa", "DataEntrega", "EPI", "CA"
    ])
    df_vazio.to_csv(ARQUIVO_MEMORIA, index=False)

def carregar_dados():
    if os.path.exists(ARQUIVO_MEMORIA):
        return pd.read_csv(ARQUIVO_MEMORIA)
    return pd.DataFrame()

def safe_str(val):
    """Garante que acentos e caracteres especiais apareçam perfeitamente no PDF"""
    if pd.isna(val) or val is None:
        return ""
    return str(val).encode('latin-1', 'replace').decode('latin-1')

def gerar_pdf_comprovante(dados_colab, historico_funcionario, imagem_assinatura=None):
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Cabeçalho do Comprovante Profissional
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, safe_str("FICHA DE CONTROLE E ENTREGA DE EPI"), ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, safe_str("Em conformidade com a Norma Regulamentadora NR-06"), ln=True, align="C")
    pdf.ln(5)
    
    # Dados do Funcionário
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, safe_str("1. Dados do Colaborador"), ln=True)
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(95, 6, safe_str(f"Nome: {dados_colab.get('Nome', '')}"), border=1)
    pdf.cell(95, 6, safe_str(f"Empresa: {dados_colab.get('Empresa', '')}"), border=1, ln=True)
    
    pdf.cell(95, 6, safe_str(f"Setor: {dados_colab.get('Setor', '')}"), border=1)
    pdf.cell(95, 6, safe_str(f"Função: {dados_colab.get('Funcao', '')}"), border=1, ln=True)
    
    pdf.cell(95, 6, safe_str(f"CTPS: {dados_colab.get('CTPS', '')}"), border=1)
    pdf.cell(95, 6, safe_str(f"Admissão: {dados_colab.get('DataAdm', '')}"), border=1, ln=True)
    
    pdf.cell(63, 6, safe_str(f"Calçado: {dados_colab.get('Calcado', '')}"), border=1)
    pdf.cell(63, 6, safe_str(f"Calça: {dados_colab.get('Calca', '')} ({dados_colab.get('TamCalca', '')})"), border=1)
    pdf.cell(64, 6, safe_str(f"Camisa: {dados_colab.get('Camisa', '')} ({dados_colab.get('TamCamisa', '')})"), border=1, ln=True)
    pdf.ln(8)
    
    # Histórico de EPIs Entregues
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, safe_str("2. Histórico de Equipamentos Entregues"), ln=True)
    
    # Cabeçalho da Tabela
    pdf.set_font("Arial", "B", 9)
    pdf.cell(25, 7, safe_str("Data"), border=1, align="C")
    pdf.cell(125, 7, safe_str("Equipamento de Proteção Individual (EPI)"), border=1, align="C")
    pdf.cell(40, 7, safe_str("C.A. (Certificado)"), border=1, align="C", ln=True)
    
    pdf.set_font("Arial", "", 9)
    for _, row in historico_funcionario.iterrows():
        pdf.cell(25, 6, safe_str(row['DataEntrega']), border=1, align="C")
        pdf.cell(125, 6, safe_str(row['EPI']), border=1)
        pdf.cell(40, 6, safe_str(row['CA']), border=1, align="C", ln=True)
        
    pdf.ln(10)
    
    # Termo de Responsabilidade
    pdf.set_font("Arial", "B", 9)
    pdf.cell(190, 5, safe_str("TERMO DE RESPONSABILIDADE:"), ln=True)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(190, 4, safe_str("Declaro que recebi os EPIs acima relacionados em perfeito estado de conservação, compromete-me a usá-los estritamente para os fins a que se destinam, responsabilizando-me pela sua guarda, higienização e conservação, bem como comunicar à empresa qualquer irregularidade ou dano."))
    pdf.ln(15)
    
    # Assinatura
    if imagem_assinatura is not None:
        caminho_ass = "temp_assinatura.png"
        imagem_assinatura.save(caminho_ass)
        pdf.image(caminho_ass, x=65, y=pdf.get_y(), w=80, h=25)
        if os.path.exists(caminho_ass):
            os.remove(caminho_ass)
            
    pdf.ln(25)
    pdf.cell(190, 0, "", "T", ln=True)
    pdf.cell(190, 5, safe_str(f"Assinatura do Colaborador: {dados_colab.get('Nome', '')}"), ln=True, align="C")
    
    nome_arquivo = f"Comprovante_{dados_colab['Nome'].replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# ================= INTERFACE PRINCIPAL =================

st.title("🛡️ Sistema Profissional de Controle de EPIs")

aba1, aba2, aba3 = st.tabs(["➕ Registrar Entrega", "👥 Consultar Colaborador", "📊 Base Completa"])

df_geral = carregar_dados()

with aba1:
    st.subheader("Nova Entrega de EPI")
    
    col_n1, col_n2 = st.columns([3, 1])
    with col_n1:
        input_nome = st.text_input("Nome Completo do Funcionário:")
    with col_n2:
        st.write("")
        btn_autofill = st.button("🔍 Carregar Dados", use_container_width=True)
        
    empresa_val, setor_val, funcao_val, ctps_val, dataadm_val = "", "", "", "", ""
    calcado_val, calca_val, tamcalca_val, camisa_val, tamcamisa_val = "", "", "", "", ""
    
    if btn_autofill and input_nome:
        match = df_geral[df_geral["Nome"].str.lower() == input_nome.strip().lower()]
        if not match.empty:
            ultima = match.iloc[-1]
            empresa_val = str(ultima.get('Empresa', ''))
            setor_val = str(ultima.get('Setor', ''))
            funcao_val = str(ultima.get('Funcao', ''))
            ctps_val = str(ultima.get('CTPS', ''))
            dataadm_val = str(ultima.get('DataAdm', ''))
            calcado_val = str(ultima.get('Calcado', ''))
            calca_val = str(ultima.get('Calca', ''))
            tamcalca_val = str(ultima.get('TamCalca', ''))
            camisa_val = str(ultima.get('Camisa', ''))
            tamcamisa_val = str(ultima.get('TamCamisa', ''))
            st.success("Dados do funcionário carregados com sucesso!")
        else:
            st.info("Novo colaborador detectado. Preencha os dados abaixo.")

    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            empresa = st.text_input("Empresa", value=empresa_val)
            setor = st.text_input("Setor", value=setor_val)
            funcao = st.text_input("Função", value=funcao_val)
            ctps = st.text_input("CTPS", value=ctps_val)
            data_adm = st.text_input("Data de Admissão", value=dataadm_val)
        with c2:
            calcado = st.text_input("Calçado Nº", value=calcado_val)
            calca = st.text_input("Calça Nº", value=calca_val)
            tam_calca = st.text_input("Tam. Calça", value=tamcalca_val)
            camisa = st.text_input("Camisa Nº", value=camisa_val)
            tam_camisa = st.text_input("Tam. Camisa", value=tamcamisa_val)

    st.markdown("---")
    st.markdown("### 📦 Detalhes do Material Entregue")
    
    e1, e2, e3 = st.columns(3)
    with e1:
        epi_nome = st.text_input("Nome do EPI (Ex: Botina de Couro)")
    with e2:
        ca_epi = st.text_input("Número do C.A.")
    with e3:
        data_entrega = st.date_input("Data da Assinatura / Entrega", value=datetime.now()).strftime("%d/%m/%Y")
        
    st.info("✍️ Assinatura Digital do Funcionário:")
    canvas_result = st_canvas(
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=130,
        width=400,
        drawing_mode="freedraw",
        key="canvas_assinatura_principal"
    )
    
    if st.button("💾 Salvar Registro e Gerar Comprovante", type="primary", use_container_width=True):
        if not input_nome or not epi_nome:
            st.error("Por favor, preencha o Nome do Funcionário e o Material Entregue.")
        else:
            img_assinatura = None
            if canvas_result.image_data is not None:
                img_assinatura = Image.fromarray(canvas_result.image_data.astype('uint8'), mode="RGBA")
                
            novo_reg = pd.DataFrame([{
                "Nome": input_nome, "Empresa": empresa, "Setor": setor, "Funcao": funcao,
                "CTPS": ctps, "DataAdm": data_adm, "Calcado": calcado, "Calca": calca,
                "TamCalca": tam_calca, "Camisa": camisa, "TamCamisa": tam_camisa,
                "DataEntrega": data_entrega, "EPI": epi_nome, "CA": ca_epi
            }])
            
            df_atualizado = pd.concat([df_geral, novo_reg], ignore_index=True)
            df_atualizado.to_csv(ARQUIVO_MEMORIA, index=False)
            
            hist_func = df_atualizado[df_atualizado["Nome"].str.lower() == input_nome.strip().lower()]
            dados_colab = {
                "Nome": input_nome, "Empresa": empresa, "Setor": setor, "Funcao": funcao,
                "CTPS": ctps, "DataAdm": data_adm, "Calcado": calcado, "Calca": calca,
                "TamCalca": tam_calca, "Camisa": camisa, "TamCamisa": tam_camisa
            }
            
            pdf_path = gerar_pdf_comprovante(dados_colab, hist_func, img_assinatura)
            st.success("Entrega registrada e salva na base com sucesso!")
            
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Baixar Comprovante Oficial em PDF", f, file_name=pdf_path, mime="application/pdf", type="primary")

with aba2:
    st.subheader("Consultar Histórico por Funcionário")
    busca_nome = st.text_input("Digite o nome para consultar:")
    if busca_nome:
        resultado = df_geral[df_geral["Nome"].str.contains(busca_nome, case=False, na=False)]
        if not resultado.empty:
            st.write(f"Encontrados {len(resultado)} registros para '{busca_nome}':")
            st.dataframe(resultado, use_container_width=True)
        else:
            st.warning("Nenhum funcionário encontrado com esse nome.")

with aba3:
    st.subheader("Base Completa de Dados")
    if not df_geral.empty:
        st.dataframe(df_geral, use_container_width=True)
        
        csv_export = df_geral.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Base Completa em CSV (Backup)", csv_export, "base_epis_completa.csv", "text/csv")
    else:
        st.info("Nenhum registro cadastrado na base ainda.")
        
