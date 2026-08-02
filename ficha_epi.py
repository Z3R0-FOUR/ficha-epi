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

COLUNAS_PADRAO = [
    "Nome", "Empresa", "Setor", "Funcao", "CTPS", "DataAdm",
    "Calcado", "Calca", "TamCalca", "Camisa", "TamCamisa", "DataEntrega", "EPI", "CA"
]

def carregar_dados():
    if os.path.exists(ARQUIVO_MEMORIA):
        df = pd.read_csv(ARQUIVO_MEMORIA)
        for col in COLUNAS_PADRAO:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=COLUNAS_PADRAO)

def safe_str(val):
    if pd.isna(val) or val is None:
        return ""
    return str(val).encode('latin-1', 'replace').decode('latin-1')

def gerar_pdf_comprovante(dados_colab, historico_funcionario, imagem_assinatura=None):
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, safe_str("FICHA DE CONTROLE E ENTREGA DE EPI"), ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, safe_str("Em conformidade com a Norma Regulamentadora NR-06"), ln=True, align="C")
    pdf.ln(5)
    
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
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, safe_str("2. Histórico de Equipamentos Entregues"), ln=True)
    
    pdf.set_font("Arial", "B", 9)
    pdf.cell(25, 7, safe_str("Data"), border=1, align="C")
    pdf.cell(125, 7, safe_str("Equipamento de Proteção Individual (EPI)"), border=1, align="C")
    pdf.cell(40, 7, safe_str("C.A. (Certificado)"), border=1, align="C", ln=True)
    
    pdf.set_font("Arial", "", 9)
    for _, row in historico_funcionario.iterrows():
        data_ent = safe_str(row.get('DataEntrega', ''))
        nome_epi = safe_str(row.get('EPI', ''))
        num_ca = safe_str(row.get('CA', ''))
        pdf.cell(25, 6, data_ent, border=1, align="C")
        pdf.cell(125, 6, nome_epi, border=1)
        pdf.cell(40, 6, num_ca, border=1, align="C", ln=True)
        
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 9)
    pdf.cell(190, 5, safe_str("TERMO DE RESPONSABILIDADE:"), ln=True)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(190, 4, safe_str("Declaro que recebi os EPIs acima relacionados em perfeito estado de conservação, compromete-me a usá-los estritamente para os fins a que se destinam, responsabilizando-me pela sua guarda, higienização e conservação, bem como comunicar à empresa qualquer irregularidade ou dano."))
    pdf.ln(15)
    
    if imagem_assinatura is not None:
        caminho_ass = "temp_assinatura.png"
        imagem_assinatura.save(caminho_ass)
        pdf.image(caminho_ass, x=65, y=pdf.get_y(), w=80, h=25)
        if os.path.exists(caminho_ass):
            os.remove(caminho_ass)
            
    pdf.ln(25)
    pdf.cell(190, 0, "", "T", ln=True)
    pdf.cell(190, 5, safe_str(f"Assinatura do Colaborador: {dados_colab.get('Nome', '')}"), ln=True, align="C")
    
    nome_arquivo = f"Comprovante_{str(dados_colab.get('Nome', 'Colaborador')).replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

st.title("🛡️ Sistema Profissional de Controle de EPIs")

aba1, aba2, aba3 = st.tabs(["➕ Registrar Entrega", "👥 Consultar Colaborador", "📊 Base Completa"])

df_geral = carregar_dados()

# Inicialização de estados
campos_sessao = {
    "nome": "", "empresa": "", "setor": "", "funcao": "", "ctps": "", 
    "data_adm": "", "calcado": "", "calca": "", "tam_calca": "", 
    "camisa": "", "tam_camisa": "", "epi_nome": "", "ca_epi": ""
}
for campo, valor_padrao in campos_sessao.items():
    if campo not in st.session_state:
        st.session_state[campo] = valor_padrao

with aba1:
    st.subheader("Nova Entrega de EPI")
    
    nomes_existentes = sorted(df_geral["Nome"].dropna().unique().tolist()) if not df_geral.empty else []
    
    colab_escolhido = st.selectbox("Carregar Colaborador Existente (Opcional):", ["-- Novo / Digitar Manualmente --"] + nomes_existentes)
    
    if colab_escolhido != "-- Novo / Digitar Manualmente --":
        if st.button("📥 Puxar Dados Deste Colaborador"):
            ultima = df_geral[df_geral["Nome"] == colab_escolhido].iloc[-1]
            st.session_state.nome = str(ultima.get('Nome', ''))
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
            st.success("Dados carregados com sucesso!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📝 Dados do Colaborador")
    
    st.text_input("Nome Completo do Funcionário:", key="nome")
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Empresa", key="empresa")
        st.text_input("Setor", key="setor")
        st.text_input("Função", key="funcao")
        st.text_input("CTPS", key="ctps")
        st.text_input("Data de Admissão", key="data_adm")
    with c2:
        st.text_input("Calçado Nº", key="calcado")
        st.text_input("Calça Nº", key="calca")
        st.text_input("Tam. Calça", key="tam_calca")
        st.text_input("Camisa Nº", key="camisa")
        st.text_input("Tam. Camisa", key="tam_camisa")

    st.markdown("---")
    st.markdown("### 📦 Detalhes do Material Entregue")
    
    e1, e2, e3 = st.columns(3)
    with e1:
        st.text_input("Nome do EPI (Ex: Botina de Couro)", key="epi_nome")
    with e2:
        st.text_input("Número do C.A.", key="ca_epi")
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
    
    st.write("")
    if st.button("💾 Salvar Registro e Gerar Comprovante", type="primary", use_container_width=True):
        nome_val = st.session_state.nome.strip()
        epi_val = st.session_state.epi_nome.strip()
        
        if not nome_val or not epi_val:
            st.error("Por favor, preencha o Nome do Funcionário e o Nome do EPI.")
        else:
            img_assinatura = None
            if canvas_result.image_data is not None:
                img_assinatura = Image.fromarray(canvas_result.image_data.astype('uint8'), mode="RGBA")
                
            novo_reg = pd.DataFrame([{
                "Nome": nome_val, 
                "Empresa": st.session_state.empresa, 
                "Setor": st.session_state.setor, 
                "Funcao": st.session_state.funcao,
                "CTPS": st.session_state.ctps, 
                "DataAdm": st.session_state.data_adm, 
                "Calcado": st.session_state.calcado, 
                "Calca": st.session_state.calca,
                "TamCalca": st.session_state.tam_calca, 
                "Camisa": st.session_state.camisa, 
                "TamCamisa": st.session_state.tam_camisa,
                "DataEntrega": data_entrega, 
                "EPI": epi_val, 
                "CA": st.session_state.ca_epi
            }])
            
            df_geral_atualizado = carregar_dados()
            df_atualizado = pd.concat([df_geral_atualizado, novo_reg], ignore_index=True)
            df_atualizado.to_csv(ARQUIVO_MEMORIA, index=False)
            
            # Filtro robusto para pegar todo o histórico do colaborador
            hist_func = df_atualizado[df_atualizado["Nome"].str.lower().str.strip() == nome_val.lower()]
            
            dados_colab = {
                "Nome": nome_val, 
                "Empresa": st.session_state.empresa, 
                "Setor": st.session_state.setor, 
                "Funcao": st.session_state.funcao,
                "CTPS": st.session_state.ctps, 
                "DataAdm": st.session_state.data_adm, 
                "Calcado": st.session_state.calcado, 
                "Calca": st.session_state.calca,
                "TamCalca": st.session_state.tam_calca, 
                "Camisa": st.session_state.camisa, 
                "TamCamisa": st.session_state.tam_camisa
            }
            
            pdf_path = gerar_pdf_comprovante(dados_colab, hist_func, img_assinatura)
            st.success("Entrega registrada e salva na base com sucesso!")
            
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Baixar Comprovante Oficial em PDF", f, file_name=pdf_path, mime="application/pdf", type="primary")

with aba2:
    st.subheader("Consultar Histórico por Funcionário")
    busca_nome = st.text_input("Digite o nome para consultar:", key="busca_aba2")
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
