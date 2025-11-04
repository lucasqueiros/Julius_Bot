"""
Cliente Supabase para gerenciar transações financeiras
"""

from supabase import create_client, Client
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import os

class SupabaseClient:
    def __init__(self, url: str = None, key: str = None):
        """
        Inicializa o cliente Supabase
        
        Args:
            url: URL do projeto Supabase
            key: Service role key do Supabase
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios")
        
        self.client: Client = create_client(self.url, self.key)
        self.table_name = "transacoes"
    
    def inserir_transacao(self, tipo: str, valor: float, categoria: str, 
                         descricao: str) -> Optional[Dict]:
        """
        Insere uma nova transação no banco
        
        Args:
            tipo: 'gasto' ou 'receita'
            valor: Valor da transação
            categoria: Categoria da transação
            descricao: Descrição detalhada
            
        Returns:
            Dados da transação inserida ou None em caso de erro
        """
        try:
            dados = {
                "tipo": tipo.lower(),
                "valor": float(valor),
                "categoria": categoria.lower(),
                "descricao": descricao
            }
            
            response = self.client.table(self.table_name).insert(dados).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Erro ao inserir transação: {e}")
            return None
    
    def buscar_todas_transacoes(self, limite: int = 100) -> List[Dict]:
        """
        Busca todas as transações
        
        Args:
            limite: Número máximo de registros a retornar
            
        Returns:
            Lista de transações
        """
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .order("data", desc=True)\
                .limit(limite)\
                .execute()
            
            return response.data
        except Exception as e:
            print(f"Erro ao buscar transações: {e}")
            return []
    
    def buscar_ultimas_transacoes(self, quantidade: int = 5) -> List[Dict]:
        """
        Busca as últimas N transações
        
        Args:
            quantidade: Número de transações a retornar
            
        Returns:
            Lista das últimas transações
        """
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .order("data", desc=True)\
                .limit(quantidade)\
                .execute()
            
            return response.data
        except Exception as e:
            print(f"Erro ao buscar últimas transações: {e}")
            return []
    
    def buscar_por_tipo(self, tipo: str) -> List[Dict]:
        """
        Busca transações por tipo (gasto ou receita)
        
        Args:
            tipo: 'gasto' ou 'receita'
            
        Returns:
            Lista de transações do tipo especificado
        """
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("tipo", tipo.lower())\
                .order("data", desc=True)\
                .execute()
            
            return response.data
        except Exception as e:
            print(f"Erro ao buscar por tipo: {e}")
            return []
    
    def buscar_por_categoria(self, categoria: str) -> List[Dict]:
        """
        Busca transações por categoria
        
        Args:
            categoria: Nome da categoria
            
        Returns:
            Lista de transações da categoria
        """
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("categoria", categoria.lower())\
                .order("data", desc=True)\
                .execute()
            
            return response.data
        except Exception as e:
            print(f"Erro ao buscar por categoria: {e}")
            return []
    
    def buscar_por_periodo(self, data_inicio: datetime, data_fim: datetime) -> List[Dict]:
        """
        Busca transações em um período específico
        
        Args:
            data_inicio: Data inicial do período
            data_fim: Data final do período
            
        Returns:
            Lista de transações no período
        """
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .gte("data", data_inicio.isoformat())\
                .lte("data", data_fim.isoformat())\
                .order("data", desc=True)\
                .execute()
            
            return response.data
        except Exception as e:
            print(f"Erro ao buscar por período: {e}")
            return []
    
    def calcular_saldo_mes_atual(self) -> Dict[str, float]:
        """
        Calcula receitas, gastos e saldo do mês atual
        
        Returns:
            Dict com total_receitas, total_gastos e saldo
        """
        try:
            hoje = datetime.now()
            inicio_mes = datetime(hoje.year, hoje.month, 1)
            
            # Buscar todas as transações do mês
            response = self.client.table(self.table_name)\
                .select("*")\
                .gte("data", inicio_mes.isoformat())\
                .lte("data", hoje.isoformat())\
                .execute()
            
            transacoes = response.data
            
            # Calcular totais
            total_receitas = sum(float(t['valor']) for t in transacoes if t['tipo'] == 'receita')
            total_gastos = sum(float(t['valor']) for t in transacoes if t['tipo'] == 'gasto')
            saldo = total_receitas - total_gastos
            
            return {
                "total_receitas": total_receitas,
                "total_gastos": total_gastos,
                "saldo": saldo
            }
        except Exception as e:
            print(f"Erro ao calcular saldo: {e}")
            return {"total_receitas": 0, "total_gastos": 0, "saldo": 0}
    
    def gastos_por_categoria_mes_atual(self) -> Dict[str, float]:
        """
        Calcula total de gastos por categoria no mês atual
        
        Returns:
            Dict com categorias e valores totais
        """
        try:
            hoje = datetime.now()
            inicio_mes = datetime(hoje.year, hoje.month, 1)
            
            gastos = self.client.table(self.table_name)\
                .select("categoria, valor")\
                .eq("tipo", "gasto")\
                .gte("data", inicio_mes.isoformat())\
                .lte("data", hoje.isoformat())\
                .execute()
            
            categorias = {}
            for gasto in gastos.data:
                cat = gasto['categoria']
                categorias[cat] = categorias.get(cat, 0) + float(gasto['valor'])
            
            return categorias
        except Exception as e:
            print(f"Erro ao calcular gastos por categoria: {e}")
            return {}
    
    def deletar_transacao(self, transaction_id: str) -> bool:
        """
        Deleta uma transação pelo ID
        
        Args:
            transaction_id: UUID da transação
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            self.client.table(self.table_name)\
                .delete()\
                .eq("id", transaction_id)\
                .execute()
            
            return True
        except Exception as e:
            print(f"Erro ao deletar transação: {e}")
            return False


# Exemplo de uso
if __name__ == "__main__":
    # Teste básico
    cliente = SupabaseClient()
    
    # Inserir transação de teste
    transacao = cliente.inserir_transacao(
        tipo="gasto",
        valor=50.0,
        categoria="alimentação",
        descricao="Jantar no restaurante"
    )
    
    print("Transação inserida:", transacao)
    
    # Buscar saldo do mês
    saldo = cliente.calcular_saldo_mes_atual()
    print("\nSaldo do mês:", saldo)
    
    # Gastos por categoria
    gastos = cliente.gastos_por_categoria_mes_atual()
    print("\nGastos por categoria:", gastos)