"""
Dashboard Streamlit - Assistente Financeiro
Visualização completa de receitas, gastos e análises
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import SupabaseClient

# Configuração da página
st.set_page_config(
    page_title="Assistente Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_database():
    """Inicializa conexão com Supabase (cached)"""
    try:
        return SupabaseClient()
    except Exception as e:
        st.error(f"❌ Erro ao conectar com banco de dados: {e}")
        return None


def formatar_moeda(valor):
    """Formata valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pagina_principal():
    """Página principal com resumo geral"""
    
    st.title("💰 Assistente Financeiro")
    st.markdown("### Dashboard de Controle Financeiro")
    
    db = get_database()
    if not db:
        return
    
    # Buscar dados
    saldo_mes = db.calcular_saldo_mes_atual()
    transacoes = db.buscar_todas_transacoes(100)
    
    # Cards de resumo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💵 Receitas do Mês",
            value=formatar_moeda(saldo_mes['total_receitas']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 Gastos do Mês",
            value=formatar_moeda(saldo_mes['total_gastos']),
            delta=None
        )
    
    with col3:
        saldo = saldo_mes['saldo']
        st.metric(
            label="📊 Saldo do Mês",
            value=formatar_moeda(saldo),
            delta=formatar_moeda(saldo) if saldo >= 0 else f"-{formatar_moeda(abs(saldo))}"
        )
    
    st.divider()
    
    # Verificar se há transações
    if not transacoes:
        st.info("📭 Nenhuma transação registrada ainda. Use o bot do Telegram para adicionar!")
        return
    
    # Preparar dados para gráficos
    df = pd.DataFrame(transacoes)
    df['data'] = pd.to_datetime(df['data'])
    df['valor'] = df['valor'].astype(float)
    
    # Filtro de período
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📈 Análise Temporal")
    
    with col2:
        periodo = st.selectbox(
            "Período",
            ["Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias", "Todo período"],
            index=2
        )
    
    # Aplicar filtro de período
    hoje = datetime.now()
    if periodo == "Últimos 7 dias":
        df_filtrado = df[df['data'] >= hoje - timedelta(days=7)]
    elif periodo == "Últimos 15 dias":
        df_filtrado = df[df['data'] >= hoje - timedelta(days=15)]
    elif periodo == "Últimos 30 dias":
        df_filtrado = df[df['data'] >= hoje - timedelta(days=30)]
    else:
        df_filtrado = df
    
    # Gráfico de linha - Evolução temporal
    df_temp = df_filtrado.copy()
    df_temp['data_formatada'] = df_temp['data'].dt.date
    df_temp['valor_assinado'] = df_temp.apply(
        lambda x: x['valor'] if x['tipo'] == 'receita' else -x['valor'], 
        axis=1
    )
    
    df_agrupado = df_temp.groupby(['data_formatada', 'tipo'])['valor'].sum().reset_index()
    
    fig_linha = px.line(
        df_agrupado,
        x='data_formatada',
        y='valor',
        color='tipo',
        title='Evolução de Receitas e Gastos',
        labels={'data_formatada': 'Data', 'valor': 'Valor (R$)', 'tipo': 'Tipo'},
        color_discrete_map={'receita': '#00CC96', 'gasto': '#EF553B'}
    )
    
    fig_linha.update_layout(
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig_linha, use_container_width=True)
    
    # Duas colunas para gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥧 Gastos por Categoria")
        
        # Gráfico de pizza - Gastos por categoria
        gastos_df = df_filtrado[df_filtrado['tipo'] == 'gasto']
        
        if not gastos_df.empty:
            gastos_categoria = gastos_df.groupby('categoria')['valor'].sum().reset_index()
            gastos_categoria = gastos_categoria.sort_values('valor', ascending=False)
            
            fig_pizza = px.pie(
                gastos_categoria,
                values='valor',
                names='categoria',
                title='Distribuição de Gastos',
                hole=0.4
            )
            
            fig_pizza.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>R$ %{value:.2f}<br>%{percent}<extra></extra>'
            )
            
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.info("Nenhum gasto no período selecionado")
    
    with col2:
        st.markdown("### 📊 Top 5 Categorias")
        
        # Gráfico de barras - Top categorias
        if not gastos_df.empty:
            top_categorias = gastos_df.groupby('categoria')['valor'].sum().reset_index()
            top_categorias = top_categorias.sort_values('valor', ascending=False).head(5)
            
            fig_barras = px.bar(
                top_categorias,
                x='valor',
                y='categoria',
                orientation='h',
                title='Maiores Gastos por Categoria',
                labels={'valor': 'Valor (R$)', 'categoria': 'Categoria'},
                color='valor',
                color_continuous_scale='Reds'
            )
            
            fig_barras.update_layout(showlegend=False)
            st.plotly_chart(fig_barras, use_container_width=True)
        else:
            st.info("Nenhum gasto no período selecionado")


def pagina_transacoes():
    """Página de listagem de transações"""
    
    st.title("📝 Transações")
    
    db = get_database()
    if not db:
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tipo_filtro = st.selectbox(
            "Tipo",
            ["Todos", "Gastos", "Receitas"]
        )
    
    with col2:
        categorias = ["Todas", "alimentação", "transporte", "moradia", "saúde", 
                     "educação", "lazer", "vestuário", "tecnologia", "contas",
                     "investimentos", "salário", "freelance", "vendas", "outros"]
        categoria_filtro = st.selectbox("Categoria", categorias)
    
    with col3:
        limite = st.number_input("Quantidade", min_value=10, max_value=500, value=50)
    
    # Buscar transações
    if tipo_filtro == "Gastos":
        transacoes = db.buscar_por_tipo("gasto")
    elif tipo_filtro == "Receitas":
        transacoes = db.buscar_por_tipo("receita")
    else:
        transacoes = db.buscar_todas_transacoes(limite)
    
    # Filtrar por categoria
    if categoria_filtro != "Todas":
        transacoes = [t for t in transacoes if t['categoria'] == categoria_filtro]
    
    # Limitar quantidade
    transacoes = transacoes[:limite]
    
    if not transacoes:
        st.info("📭 Nenhuma transação encontrada com os filtros selecionados")
        return
    
    # Exibir resumo
    st.markdown(f"### Encontradas {len(transacoes)} transações")
    
    total = sum(float(t['valor']) for t in transacoes)
    st.metric("Total", formatar_moeda(total))
    
    st.divider()
    
    # Converter para DataFrame
    df = pd.DataFrame(transacoes)
    df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y %H:%M')
    df['valor'] = df['valor'].astype(float)
    df['valor_formatado'] = df['valor'].apply(formatar_moeda)
    
    # Reorganizar colunas
    df_exibir = df[['data', 'tipo', 'categoria', 'descricao', 'valor_formatado']]
    df_exibir.columns = ['Data', 'Tipo', 'Categoria', 'Descrição', 'Valor']
    
    # Estilizar por tipo
    def destacar_tipo(row):
        if row['Tipo'] == 'gasto':
            return ['background-color: #ffebee'] * len(row)
        else:
            return ['background-color: #e8f5e9'] * len(row)
    
    st.dataframe(
        df_exibir.style.apply(destacar_tipo, axis=1),
        use_container_width=True,
        height=600
    )


def pagina_analises():
    """Página de análises e insights"""
    
    st.title("📊 Análises Detalhadas")
    
    db = get_database()
    if not db:
        return
    
    # Buscar dados
    hoje = datetime.now()
    inicio_mes = datetime(hoje.year, hoje.month, 1)
    
    transacoes_mes = db.buscar_por_periodo(inicio_mes, hoje)
    
    if not transacoes_mes:
        st.info("📭 Nenhuma transação neste mês para análise")
        return
    
    df = pd.DataFrame(transacoes_mes)
    df['valor'] = df['valor'].astype(float)
    
    # Análise por categoria
    st.markdown("### 📂 Análise por Categoria")
    
    gastos = df[df['tipo'] == 'gasto']
    
    if not gastos.empty:
        categoria_stats = gastos.groupby('categoria').agg({
            'valor': ['sum', 'mean', 'count']
        }).round(2)
        
        categoria_stats.columns = ['Total', 'Média', 'Quantidade']
        categoria_stats = categoria_stats.sort_values('Total', ascending=False)
        categoria_stats['Total'] = categoria_stats['Total'].apply(formatar_moeda)
        categoria_stats['Média'] = categoria_stats['Média'].apply(formatar_moeda)
        
        st.dataframe(categoria_stats, use_container_width=True)
        
        # Insights
        st.markdown("### 💡 Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            categoria_mais_gasta = gastos.groupby('categoria')['valor'].sum().idxmax()
            valor_mais_gasto = gastos.groupby('categoria')['valor'].sum().max()
            
            st.info(f"🔝 **Categoria com mais gastos:** {categoria_mais_gasta.capitalize()} - {formatar_moeda(valor_mais_gasto)}")
            
            gasto_medio = gastos['valor'].mean()
            st.info(f"📊 **Gasto médio por transação:** {formatar_moeda(gasto_medio)}")
        
        with col2:
            total_transacoes = len(gastos)
            st.info(f"🔢 **Total de transações de gasto:** {total_transacoes}")
            
            dias_mes = (hoje - inicio_mes).days + 1
            media_dia = gastos['valor'].sum() / dias_mes
            st.info(f"📅 **Média de gasto por dia:** {formatar_moeda(media_dia)}")
        
        # Comparação com mês anterior
        st.markdown("### 📈 Comparação com Mês Anterior")
        
        # Buscar mês anterior
        if hoje.month == 1:
            inicio_mes_anterior = datetime(hoje.year - 1, 12, 1)
            fim_mes_anterior = datetime(hoje.year, 1, 1) - timedelta(days=1)
        else:
            inicio_mes_anterior = datetime(hoje.year, hoje.month - 1, 1)
            fim_mes_anterior = inicio_mes - timedelta(days=1)
        
        transacoes_mes_anterior = db.buscar_por_periodo(inicio_mes_anterior, fim_mes_anterior)
        
        if transacoes_mes_anterior:
            df_anterior = pd.DataFrame(transacoes_mes_anterior)
            df_anterior['valor'] = df_anterior['valor'].astype(float)
            
            gastos_anterior = df_anterior[df_anterior['tipo'] == 'gasto']['valor'].sum()
            gastos_atual = gastos['valor'].sum()
            
            diferenca = gastos_atual - gastos_anterior
            percentual = (diferenca / gastos_anterior * 100) if gastos_anterior > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Mês Anterior", formatar_moeda(gastos_anterior))
            
            with col2:
                st.metric("Mês Atual", formatar_moeda(gastos_atual))
            
            with col3:
                st.metric(
                    "Variação",
                    formatar_moeda(abs(diferenca)),
                    f"{percentual:+.1f}%"
                )
        else:
            st.info("Sem dados do mês anterior para comparação")
    else:
        st.info("Nenhum gasto registrado neste mês")


def main():
    """Função principal do dashboard"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/money-bag.png", width=100)
        st.title("Navegação")
        
        pagina = st.radio(
            "Escolha a página:",
            ["🏠 Principal", "📝 Transações", "📊 Análises"]
        )
        
        st.divider()
        
        st.markdown("### ℹ️ Sobre")
        st.info(
            "Dashboard do Assistente Financeiro\n\n"
            "Use o bot do Telegram para registrar suas transações!"
        )
        
        # Botão de atualizar
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    
    # Renderizar página selecionada
    if pagina == "🏠 Principal":
        pagina_principal()
    elif pagina == "📝 Transações":
        pagina_transacoes()
    elif pagina == "📊 Análises":
        pagina_analises()


if __name__ == "__main__":
    main()