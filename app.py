import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Dashboard de Vendas BI", layout="wide")

st.title("📊 Dashboard Inteligente de Vendas")

def gerar_template():
    df_template = pd.DataFrame({
        "Data": [],
        "Nº Pedido": [],
        "Cliente": [],
        "Produto/Serviço": [],
        "Quantidade": [],
        "Valor Unitário": [],
        "Total da Venda": [],
        "Custo Unitário": [],
        "Custo Total": [],
        "Lucro": [],
        "Forma de Pagamento": [],
        "Status do Pagamento": [],
        "Observações": []
    })

    output = BytesIO()
    df_template.to_excel(output, index=False)
    output.seek(0)
    return output

st.download_button(
    label="📥 Baixar Template do Arquivo",
    data=gerar_template(),
    file_name="Template_Controle_Vendas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()


arquivo = st.file_uploader("📂 Faça upload do arquivo preenchido", type=["xlsx"])

if arquivo:

    df = pd.read_excel(arquivo)

    colunas_obrigatorias = [
        "Data", "Produto/Serviço", "Total da Venda", "Lucro"
    ]

    colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]

    if colunas_faltando:
        st.error(f"O arquivo não possui as colunas obrigatórias: {colunas_faltando}")
        st.stop()


    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Data"])

    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce")
    df["Valor Unitário"] = pd.to_numeric(df["Valor Unitário"], errors="coerce")
    df["Custo Unitário"] = pd.to_numeric(df["Custo Unitário"], errors="coerce")

    df = df.dropna(subset=["Quantidade", "Valor Unitário", "Custo Unitário"])

    df["Total da Venda"] = df["Quantidade"] * df["Valor Unitário"]
    df["Custo Total"] = df["Quantidade"] * df["Custo Unitário"]
    df["Lucro"] = df["Total da Venda"] - df["Custo Total"]

    if df.empty:
        st.error("O arquivo não possui dados suficientes para análise.")
        st.stop()

    df["Mes"] = df["Data"].dt.to_period("M").astype(str)


    total_vendas = df["Total da Venda"].sum()
    total_lucro = df["Lucro"].sum()
    ticket_medio = df["Total da Venda"].mean() if total_vendas > 0 else 0
    margem = (total_lucro / total_vendas) * 100 if total_vendas > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Faturamento Total", f"R$ {total_vendas:,.2f}")
    col2.metric("📈 Lucro Total", f"R$ {total_lucro:,.2f}")
    col3.metric("🧾 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    col4.metric("📊 Margem (%)", f"{margem:.2f}%")

    st.divider()


    col1, col2 = st.columns(2)

    vendas_mes = df.groupby("Mes")["Total da Venda"].sum().reset_index()
    fig1 = px.line(
        vendas_mes,
        x="Mes",
        y="Total da Venda",
        markers=True,
        title="Evolução do Faturamento Mensal"
    )
    col1.plotly_chart(fig1, use_container_width=True)

    vendas_prod = df.groupby("Produto/Serviço")["Total da Venda"].sum().reset_index()
    fig2 = px.bar(
        vendas_prod.sort_values("Total da Venda", ascending=False),
        x="Produto/Serviço",
        y="Total da Venda",
        title="Faturamento por Produto"
    )
    col2.plotly_chart(fig2, use_container_width=True)

    if "Forma de Pagamento" in df.columns:
        fig3 = px.pie(
            df,
            names="Forma de Pagamento",
            values="Total da Venda",
            title="Distribuição por Forma de Pagamento"
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🧠 Insights Automáticos")

    produto_top = vendas_prod.sort_values("Total da Venda", ascending=False).iloc[0]["Produto/Serviço"]
    produto_bottom = vendas_prod.sort_values("Total da Venda").iloc[0]["Produto/Serviço"]
    mes_top = vendas_mes.sort_values("Total da Venda", ascending=False).iloc[0]["Mes"]

    st.success(f"""
    🔥 Produto campeão de vendas: **{produto_top}**
    📉 Produto com menor desempenho: **{produto_bottom}**
    🚀 Mês com maior faturamento: **{mes_top}**
    💡 Margem média do negócio: **{margem:.2f}%**
    """)

    st.subheader("📖 Storytelling Executivo")

    if margem > 30:
        narrativa = "O negócio apresenta excelente rentabilidade, com margem saudável e boa eficiência operacional."
    elif margem > 15:
        narrativa = "A empresa apresenta rentabilidade moderada, com oportunidades claras de otimização de custos."
    else:
        narrativa = "A margem está baixa, indicando necessidade de revisão de precificação ou redução de custos."

    st.info(f"""
    No período analisado, o faturamento total foi de **R$ {total_vendas:,.2f}**, 
    gerando um lucro de **R$ {total_lucro:,.2f}**.

    O principal motor de receita foi o produto **{produto_top}**, 
    enquanto **{produto_bottom}** apresenta menor contribuição no resultado.

    {narrativa}
    """)
