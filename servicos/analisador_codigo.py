"""
Serviço de Análise de Código Python.

Implementa a lógica principal para análise e otimização de código Python,
identificando problemas de performance, legibilidade e boas práticas.
"""

import ast
import time
import re
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from modelos.schemas import Sugestao, TipoSugestao, NivelDetalhamento

logger = logging.getLogger(__name__)

class AnalisadorCodigo:
    """
    Analisador inteligente de código Python.
    
    Identifica problemas de performance, legibilidade, segurança
    e conformidade com boas práticas de programação.
    """
    
    def __init__(self):
        self.ultimo_tempo_analise = 0.0
        self.regras_analise = self._carregar_regras_analise()
        
    def _carregar_regras_analise(self) -> Dict[str, Any]:
        """Carrega as regras de análise de código."""
        return {
            'performance': {
                'loops_aninhados': {
                    'limite': 3,
                    'prioridade': 8,
                    'impacto': 'alto'
                },
                'concatenacao_strings': {
                    'padrao': r'\+.*str\(',
                    'prioridade': 6,
                    'impacto': 'médio'
                },
                'list_comprehension': {
                    'padrao': r'for.*in.*append\(',
                    'prioridade': 5,
                    'impacto': 'médio'
                }
            },
            'legibilidade': {
                'nomes_variaveis': {
                    'padrao': r'\b[a-z]\b|\b[a-z]{1,2}\b',
                    'prioridade': 4,
                    'impacto': 'baixo'
                },
                'linhas_muito_longas': {
                    'limite': 88,
                    'prioridade': 3,
                    'impacto': 'baixo'
                },
                'funcoes_muito_longas': {
                    'limite': 50,
                    'prioridade': 6,
                    'impacto': 'médio'
                }
            },
            'boas_praticas': {
                'imports_nao_utilizados': {
                    'prioridade': 4,
                    'impacto': 'baixo'
                },
                'docstrings_ausentes': {
                    'prioridade': 5,
                    'impacto': 'médio'
                },
                'excecoes_genericas': {
                    'padrao': r'except\s*:',
                    'prioridade': 7,
                    'impacto': 'alto'
                }
            },
            'seguranca': {
                'eval_exec': {
                    'padrao': r'\b(eval|exec)\s*\(',
                    'prioridade': 9,
                    'impacto': 'alto'
                },
                'sql_injection': {
                    'padrao': r'execute\s*\(\s*["\'].*%.*["\']',
                    'prioridade': 10,
                    'impacto': 'alto'
                }
            }
        }
    
    async def analisar_codigo(
        self,
        codigo: str,
        nivel_detalhamento: NivelDetalhamento = NivelDetalhamento.INTERMEDIARIO,
        focar_performance: bool = False
    ) -> List[Sugestao]:
        """
        Analisa o código Python e retorna sugestões de otimização.
        
        Args:
            codigo: Código Python a ser analisado
            nivel_detalhamento: Nível de detalhamento da análise
            focar_performance: Se deve focar em otimizações de performance
            
        Returns:
            Lista de sugestões de otimização
        """
        inicio_tempo = time.time()
        logger.info("Iniciando análise de código...")
        
        try:
            # Parse do código para AST
            arvore_ast = ast.parse(codigo)
            
            # Lista para armazenar todas as sugestões
            sugestoes = []
            
            # Análises específicas baseadas no nível de detalhamento
            if nivel_detalhamento in [NivelDetalhamento.BASICO, NivelDetalhamento.INTERMEDIARIO, NivelDetalhamento.AVANCADO]:
                sugestoes.extend(await self._analisar_performance(codigo, arvore_ast, focar_performance))
                sugestoes.extend(await self._analisar_legibilidade(codigo, arvore_ast))
                
            if nivel_detalhamento in [NivelDetalhamento.INTERMEDIARIO, NivelDetalhamento.AVANCADO]:
                sugestoes.extend(await self._analisar_boas_praticas(codigo, arvore_ast))
                
            if nivel_detalhamento == NivelDetalhamento.AVANCADO:
                sugestoes.extend(await self._analisar_seguranca(codigo, arvore_ast))
                sugestoes.extend(await self._analisar_complexidade(codigo, arvore_ast))
            
            # Ordena sugestões por prioridade (maior prioridade primeiro)
            sugestoes.sort(key=lambda x: x.prioridade, reverse=True)
            
            # Limita o número de sugestões baseado no nível
            limite_sugestoes = {
                NivelDetalhamento.BASICO: 5,
                NivelDetalhamento.INTERMEDIARIO: 10,
                NivelDetalhamento.AVANCADO: 20
            }
            
            sugestoes = sugestoes[:limite_sugestoes[nivel_detalhamento]]
            
            self.ultimo_tempo_analise = time.time() - inicio_tempo
            logger.info(f"Análise concluída em {self.ultimo_tempo_analise:.2f}s com {len(sugestoes)} sugestões")
            
            return sugestoes
            
        except Exception as e:
            logger.error(f"Erro durante análise: {e}")
            raise
    
    async def _analisar_performance(self, codigo: str, arvore_ast: ast.AST, focar_performance: bool) -> List[Sugestao]:
        """Analisa problemas de performance no código."""
        sugestoes = []
        linhas = codigo.split('\n')
        
        # Detecta loops aninhados
        for node in ast.walk(arvore_ast):
            if isinstance(node, (ast.For, ast.While)):
                nivel_aninhamento = self._contar_loops_aninhados(node)
                if nivel_aninhamento > self.regras_analise['performance']['loops_aninhados']['limite']:
                    sugestoes.append(Sugestao(
                        tipo=TipoSugestao.PERFORMANCE,
                        titulo="Loops muito aninhados detectados",
                        descricao=f"Encontrado {nivel_aninhamento} níveis de loops aninhados. "
                                 "Considere refatorar para melhorar a performance e legibilidade.",
                        linha_inicio=node.lineno,
                        impacto="alto",
                        prioridade=8,
                        codigo_sugerido="# Considere usar funções auxiliares ou algoritmos mais eficientes"
                    ))
        
        # Detecta concatenação ineficiente de strings
        for i, linha in enumerate(linhas, 1):
            if re.search(self.regras_analise['performance']['concatenacao_strings']['padrao'], linha):
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.PERFORMANCE,
                    titulo="Concatenação ineficiente de strings",
                    descricao="Use join() ou f-strings para concatenação mais eficiente de strings.",
                    linha_inicio=i,
                    codigo_original=linha.strip(),
                    codigo_sugerido="# Use: ''.join(lista_strings) ou f'{var1}{var2}'",
                    impacto="médio",
                    prioridade=6
                ))
        
        # Detecta oportunidades para list comprehension
        for i, linha in enumerate(linhas, 1):
            if re.search(self.regras_analise['performance']['list_comprehension']['padrao'], linha):
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.PERFORMANCE,
                    titulo="Oportunidade para list comprehension",
                    descricao="Substitua loops simples por list comprehensions para melhor performance.",
                    linha_inicio=i,
                    codigo_original=linha.strip(),
                    codigo_sugerido="# Use: [expressao for item in lista if condicao]",
                    impacto="médio",
                    prioridade=5
                ))
        
        return sugestoes
    
    async def _analisar_legibilidade(self, codigo: str, arvore_ast: ast.AST) -> List[Sugestao]:
        """Analisa problemas de legibilidade no código."""
        sugestoes = []
        linhas = codigo.split('\n')
        
        # Verifica linhas muito longas
        for i, linha in enumerate(linhas, 1):
            if len(linha) > self.regras_analise['legibilidade']['linhas_muito_longas']['limite']:
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.LEGIBILIDADE,
                    titulo="Linha muito longa",
                    descricao=f"Linha {i} tem {len(linha)} caracteres. "
                             "Considere quebrar em múltiplas linhas para melhor legibilidade.",
                    linha_inicio=i,
                    codigo_original=linha.strip(),
                    impacto="baixo",
                    prioridade=3
                ))
        
        # Verifica nomes de variáveis muito curtos
        for node in ast.walk(arvore_ast):
            if isinstance(node, ast.Name) and hasattr(node, 'id'):
                if re.match(self.regras_analise['legibilidade']['nomes_variaveis']['padrao'], node.id):
                    sugestoes.append(Sugestao(
                        tipo=TipoSugestao.LEGIBILIDADE,
                        titulo="Nome de variável pouco descritivo",
                        descricao=f"A variável '{node.id}' tem um nome muito curto. "
                                 "Use nomes mais descritivos para melhor legibilidade.",
                        linha_inicio=getattr(node, 'lineno', 1),
                        codigo_original=node.id,
                        impacto="baixo",
                        prioridade=4
                    ))
        
        # Verifica funções muito longas
        for node in ast.walk(arvore_ast):
            if isinstance(node, ast.FunctionDef):
                linhas_funcao = self._contar_linhas_funcao(node)
                if linhas_funcao > self.regras_analise['legibilidade']['funcoes_muito_longas']['limite']:
                    sugestoes.append(Sugestao(
                        tipo=TipoSugestao.LEGIBILIDADE,
                        titulo="Função muito longa",
                        descricao=f"A função '{node.name}' tem {linhas_funcao} linhas. "
                                 "Considere dividir em funções menores.",
                        linha_inicio=node.lineno,
                        impacto="médio",
                        prioridade=6
                    ))
        
        return sugestoes
    
    async def _analisar_boas_praticas(self, codigo: str, arvore_ast: ast.AST) -> List[Sugestao]:
        """Analisa conformidade com boas práticas."""
        sugestoes = []
        linhas = codigo.split('\n')
        
        # Verifica docstrings ausentes
        for node in ast.walk(arvore_ast):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    tipo_elemento = "função" if isinstance(node, ast.FunctionDef) else "classe"
                    sugestoes.append(Sugestao(
                        tipo=TipoSugestao.BOAS_PRATICAS,
                        titulo=f"Docstring ausente em {tipo_elemento}",
                        descricao=f"A {tipo_elemento} '{node.name}' não possui docstring. "
                                 "Adicione documentação para melhor manutenibilidade.",
                        linha_inicio=node.lineno,
                        codigo_sugerido=f'"""\n    Documentação da {tipo_elemento} {node.name}.\n    """',
                        impacto="médio",
                        prioridade=5
                    ))
        
        # Verifica exceções genéricas
        for i, linha in enumerate(linhas, 1):
            if re.search(self.regras_analise['boas_praticas']['excecoes_genericas']['padrao'], linha):
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.BOAS_PRATICAS,
                    titulo="Exceção genérica capturada",
                    descricao="Evite capturar exceções genéricas. Especifique o tipo de exceção.",
                    linha_inicio=i,
                    codigo_original=linha.strip(),
                    codigo_sugerido="except SpecificException as e:",
                    impacto="alto",
                    prioridade=7
                ))
        
        return sugestoes
    
    async def _analisar_seguranca(self, codigo: str, arvore_ast: ast.AST) -> List[Sugestao]:
        """Analisa problemas de segurança no código."""
        sugestoes = []
        linhas = codigo.split('\n')
        
        # Verifica uso de eval/exec
        for i, linha in enumerate(linhas, 1):
            if re.search(self.regras_analise['seguranca']['eval_exec']['padrao'], linha):
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.SEGURANCA,
                    titulo="Uso perigoso de eval/exec",
                    descricao="O uso de eval() ou exec() pode ser perigoso. "
                             "Considere alternativas mais seguras.",
                    linha_inicio=i,
                    codigo_original=linha.strip(),
                    impacto="alto",
                    prioridade=9
                ))
        
        # Verifica possível SQL injection
        for i, linha in enumerate(linhas, 1):
            if re.search(self.regras_analise['seguranca']['sql_injection']['padrao'], linha):
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.SEGURANCA,
                    titulo="Possível vulnerabilidade SQL injection",
                    descricao="Use parâmetros preparados em vez de concatenação de strings em SQL.",
                    linha_inicio=i,
                    codigo_original=linha.strip(),
                    codigo_sugerido="cursor.execute('SELECT * FROM table WHERE id = %s', (user_id,))",
                    impacto="alto",
                    prioridade=10
                ))
        
        return sugestoes
    
    async def _analisar_complexidade(self, codigo: str, arvore_ast: ast.AST) -> List[Sugestao]:
        """Analisa complexidade ciclomática do código."""
        sugestoes = []
        
        for node in ast.walk(arvore_ast):
            if isinstance(node, ast.FunctionDef):
                complexidade = self._calcular_complexidade_ciclomatica(node)
                if complexidade > 10:
                    sugestoes.append(Sugestao(
                        tipo=TipoSugestao.MANUTENCAO,
                        titulo="Alta complexidade ciclomática",
                        descricao=f"A função '{node.name}' tem complexidade {complexidade}. "
                                 "Considere refatorar para reduzir a complexidade.",
                        linha_inicio=node.lineno,
                        impacto="alto",
                        prioridade=8
                    ))
        
        return sugestoes
    
    def calcular_pontuacao_qualidade(self, codigo: str) -> float:
        """
        Calcula uma pontuação de qualidade para o código (0-100).
        
        Args:
            codigo: Código Python a ser avaliado
            
        Returns:
            Pontuação de qualidade (0-100)
        """
        try:
            pontuacao = 100.0
            linhas = codigo.split('\n')
            
            # Penalidades por problemas encontrados
            penalidades = {
                'linhas_longas': len([l for l in linhas if len(l) > 88]) * 2,
                'linhas_vazias_excessivas': max(0, (len([l for l in linhas if not l.strip()]) - len(linhas) * 0.1) * 1),
                'falta_espacos': len([l for l in linhas if '=' in l and ('=' not in l.replace('==', '').replace('!=', '').replace('<=', '').replace('>=', '') or ' = ' not in l)]) * 1,
            }
            
            # Aplica penalidades
            for tipo, valor in penalidades.items():
                pontuacao -= min(valor, 20)  # Máximo 20 pontos de penalidade por tipo
            
            # Bônus por boas práticas
            bonus = {
                'docstrings': len(re.findall(r'""".*?"""', codigo, re.DOTALL)) * 5,
                'comentarios': len([l for l in linhas if l.strip().startswith('#')]) * 1,
                'type_hints': len(re.findall(r':\s*\w+', codigo)) * 2,
            }
            
            # Aplica bônus
            for tipo, valor in bonus.items():
                pontuacao += min(valor, 10)  # Máximo 10 pontos de bônus por tipo
            
            return max(0, min(100, pontuacao))
            
        except Exception as e:
            logger.error(f"Erro ao calcular pontuação: {e}")
            return 50.0  # Pontuação padrão em caso de erro
    
    def _contar_loops_aninhados(self, node: ast.AST, nivel: int = 0) -> int:
        """Conta o nível de aninhamento de loops."""
        max_nivel = nivel
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                max_nivel = max(max_nivel, self._contar_loops_aninhados(child, nivel + 1))
        return max_nivel
    
    def _contar_linhas_funcao(self, node: ast.FunctionDef) -> int:
        """Conta o número de linhas de uma função."""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno - node.lineno + 1
        return 1
    
    def _calcular_complexidade_ciclomatica(self, node: ast.FunctionDef) -> int:
        """Calcula a complexidade ciclomática de uma função."""
        complexidade = 1  # Complexidade base
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexidade += 1
            elif isinstance(child, ast.BoolOp):
                complexidade += len(child.values) - 1
        
        return complexidade

