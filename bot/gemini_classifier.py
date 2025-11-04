"""
Classificador de transações financeiras usando Google Gemini
"""

import google.generativeai as genai
import json
import os
from typing import Optional, Dict
import re
from dotenv import load_dotenv

load_dotenv()


class GeminiClassifier:
    def __init__(self, api_key: str = None):
        """
        Inicializa o classificador Gemini
        
        Args:
            api_key: Chave da API do Google Gemini
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY é obrigatória")
        
        # Configurar Gemini
        genai.configure(api_key=self.api_key)
        
        # Usar modelo Gemini Pro
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Categorias disponíveis
        self.categorias = [
            "alimentação",
            "transporte",
            "moradia",
            "saúde",
            "educação",
            "lazer",
            "vestuário",
            "tecnologia",
            "contas",
            "investimentos",
            "salário",
            "freelance",
            "vendas",
            "outros"
        ]
        
        # Prompt do sistema
        self.system_prompt = self._criar_prompt_sistema()
    
    def _criar_prompt_sistema(self) -> str:
        """Cria o prompt do sistema com instruções detalhadas"""
        
        categorias_str = ", ".join(self.categorias)
        
        prompt = f"""Você é um assistente especializado em classificar transações financeiras.

Sua tarefa é analisar mensagens de usuários sobre gastos e receitas e extrair informações estruturadas.

REGRAS IMPORTANTES:
1. Identifique se é um GASTO ou RECEITA
2. Extraia o VALOR numérico (aceite formatos: 50, 50.00, 50,00, R$ 50, etc)
3. Classifique em uma das categorias: {categorias_str}
4. Crie uma DESCRIÇÃO clara e concisa
5. SEMPRE retorne um JSON válido, mesmo se a mensagem for ambígua

CATEGORIAS E EXEMPLOS:
- alimentação: restaurante, mercado, lanche, comida, café, padaria
- transporte: uber, ônibus, gasolina, combustível, taxi, metrô
- moradia: aluguel, condomínio, energia, água, gás, internet
- saúde: médico, farmácia, remédio, consulta, exame
- educação: curso, livro, faculdade, escola, aula
- lazer: cinema, teatro, viagem, passeio, diversão
- vestuário: roupa, sapato, calça, camisa, acessório
- tecnologia: celular, computador, software, app, eletrônico
- contas: telefone, streaming, assinatura, serviços
- investimentos: ações, fundos, poupança, aplicação
- salário: pagamento mensal, remuneração, ordenado
- freelance: trabalho extra, bico, serviço prestado
- vendas: venda de produto, item vendido
- outros: qualquer coisa que não se encaixe acima

FORMATO DE SAÍDA (JSON):
{{
  "tipo": "gasto" ou "receita",
  "valor": número decimal,
  "categoria": "uma das categorias listadas",
  "descricao": "descrição clara e objetiva",
  "confianca": número de 0 a 1 indicando sua certeza
}}

EXEMPLOS:

Mensagem: "Gastei 45 reais no almoço"
Resposta:
{{
  "tipo": "gasto",
  "valor": 45.0,
  "categoria": "alimentação",
  "descricao": "Almoço",
  "confianca": 0.95
}}

Mensagem: "Uber pra casa 23,50"
Resposta:
{{
  "tipo": "gasto",
  "valor": 23.5,
  "categoria": "transporte",
  "descricao": "Uber para casa",
  "confianca": 0.9
}}

Mensagem: "Recebi 3000 de salário"
Resposta:
{{
  "tipo": "receita",
  "valor": 3000.0,
  "categoria": "salário",
  "descricao": "Salário mensal",
  "confianca": 0.95
}}

Mensagem: "paguei a conta de luz 150"
Resposta:
{{
  "tipo": "gasto",
  "valor": 150.0,
  "categoria": "moradia",
  "descricao": "Conta de luz",
  "confianca": 0.9
}}

IMPORTANTE:
- Se não conseguir identificar o valor, coloque 0 e confianca baixa
- Se a categoria for ambígua, escolha a mais provável
- Mantenha descrições curtas (máximo 50 caracteres)
- NUNCA retorne texto fora do JSON
- Retorne APENAS o JSON, sem markdown ou explicações
"""
        return prompt
    
    def _extrair_json(self, texto: str) -> Optional[Dict]:
        """
        Extrai JSON da resposta do Gemini
        
        Args:
            texto: Resposta do Gemini
            
        Returns:
            Dict com dados extraídos ou None
        """
        try:
            # Tentar encontrar JSON no texto
            # Remove markdown code blocks se existirem
            texto = texto.strip()
            texto = re.sub(r'^```json\s*', '', texto)
            texto = re.sub(r'^```\s*', '', texto)
            texto = re.sub(r'\s*```$', '', texto)
            
            # Tentar parsear JSON
            dados = json.loads(texto)
            
            # Validar campos obrigatórios
            campos_obrigatorios = ['tipo', 'valor', 'categoria', 'descricao']
            if not all(campo in dados for campo in campos_obrigatorios):
                return None
            
            # Validar tipo
            if dados['tipo'] not in ['gasto', 'receita']:
                return None
            
            # Validar valor
            try:
                dados['valor'] = float(dados['valor'])
            except (ValueError, TypeError):
                dados['valor'] = 0.0
            
            # Garantir que categoria está na lista
            if dados['categoria'] not in self.categorias:
                dados['categoria'] = 'outros'
            
            # Adicionar confianca se não existir
            if 'confianca' not in dados:
                dados['confianca'] = 0.7
            
            return dados
            
        except json.JSONDecodeError:
            # Se falhar, tentar extrair manualmente com regex
            return self._extrair_manual(texto)
        except Exception as e:
            print(f"Erro ao extrair JSON: {e}")
            return None
    
    def _extrair_manual(self, texto: str) -> Optional[Dict]:
        """
        Extração manual como fallback quando JSON falha
        
        Args:
            texto: Texto para extrair informações
            
        Returns:
            Dict com dados extraídos ou None
        """
        try:
            # Buscar padrões no texto
            tipo_match = re.search(r'"tipo"\s*:\s*"(gasto|receita)"', texto)
            valor_match = re.search(r'"valor"\s*:\s*(\d+\.?\d*)', texto)
            categoria_match = re.search(r'"categoria"\s*:\s*"([^"]+)"', texto)
            descricao_match = re.search(r'"descricao"\s*:\s*"([^"]+)"', texto)
            
            if tipo_match and valor_match:
                return {
                    'tipo': tipo_match.group(1),
                    'valor': float(valor_match.group(1)),
                    'categoria': categoria_match.group(1) if categoria_match else 'outros',
                    'descricao': descricao_match.group(1) if descricao_match else 'Transação',
                    'confianca': 0.5
                }
        except Exception as e:
            print(f"Erro na extração manual: {e}")
        
        return None
    
    def classificar(self, mensagem: str) -> Optional[Dict]:
        """
        Classifica uma mensagem de transação
        
        Args:
            mensagem: Mensagem do usuário sobre gasto/receita
            
        Returns:
            Dict com informações da transação ou None em caso de erro
        """
        try:
            # Criar prompt completo
            prompt_completo = f"{self.system_prompt}\n\nMensagem do usuário: \"{mensagem}\"\n\nRetorne APENAS o JSON:"
            
            # Fazer requisição ao Gemini
            response = self.model.generate_content(prompt_completo)
            
            # Extrair texto da resposta
            texto_resposta = response.text
            
            # Extrair e validar JSON
            dados = self._extrair_json(texto_resposta)
            
            if dados:
                print(f"✅ Classificação bem-sucedida (confiança: {dados['confianca']:.0%})")
                return dados
            else:
                print("❌ Não foi possível extrair dados válidos")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao classificar mensagem: {e}")
            return None
    
    def classificar_com_contexto(self, mensagem: str, historico: list = None) -> Optional[Dict]:
        """
        Classifica mensagem considerando histórico de conversas
        
        Args:
            mensagem: Mensagem atual
            historico: Lista de mensagens anteriores
            
        Returns:
            Dict com informações da transação
        """
        # TODO: Implementar classificação com contexto se necessário
        # Por enquanto, usa classificação simples
        return self.classificar(mensagem)


# Função de teste
def testar_classificador():
    """Testa o classificador com várias mensagens"""
    
    print("=" * 70)
    print("🧪 TESTANDO CLASSIFICADOR GEMINI")
    print("=" * 70 + "\n")
    
    # Criar classificador
    try:
        classificador = GeminiClassifier()
    except ValueError as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Configure a variável de ambiente GEMINI_API_KEY")
        return
    
    # Mensagens de teste
    mensagens_teste = [
        "Gastei 45 reais no almoço hoje",
        "Uber pro trabalho 23,50",
        "Recebi 3000 de salário",
        "Comprei um livro de Python por R$ 89,90",
        "paguei 150 de luz",
        "Netflix 29.90",
        "Vendi uns itens usados por 200 reais",
        "consulta médica 250",
        "cerveja com os amigos 80 reais",
        "fiz um freela, ganhei 500"
    ]
    
    resultados = []
    
    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"\n📝 Teste {i}: \"{mensagem}\"")
        print("-" * 70)
        
        resultado = classificador.classificar(mensagem)
        
        if resultado:
            resultados.append(resultado)
            print(f"  Tipo: {resultado['tipo'].upper()}")
            print(f"  Valor: R$ {resultado['valor']:.2f}")
            print(f"  Categoria: {resultado['categoria']}")
            print(f"  Descrição: {resultado['descricao']}")
            print(f"  Confiança: {resultado['confianca']:.0%}")
        else:
            print("  ❌ Falha na classificação")
        
        # Pausa para não sobrecarregar API
        import time
        time.sleep(1)
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Total de testes: {len(mensagens_teste)}")
    print(f"Sucessos: {len(resultados)}")
    print(f"Falhas: {len(mensagens_teste) - len(resultados)}")
    print(f"Taxa de sucesso: {len(resultados)/len(mensagens_teste)*100:.1f}%")
    
    if resultados:
        confianca_media = sum(r['confianca'] for r in resultados) / len(resultados)
        print(f"Confiança média: {confianca_media:.0%}")


if __name__ == "__main__":
    testar_classificador()