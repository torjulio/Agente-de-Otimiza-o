"""
Monitor do Sistema.

Implementa monitoramento abrangente do agente de otimização,
incluindo métricas de performance, saúde dos serviços e alertas.
"""

import asyncio
import logging
import psutil
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class MetricasSistema:
    """Métricas do sistema em um momento específico."""
    timestamp: datetime
    cpu_percent: float
    memoria_percent: float
    memoria_disponivel_mb: float
    disco_percent: float
    disco_disponivel_gb: float
    processos_ativos: int
    conexoes_rede: int

@dataclass
class MetricasAplicacao:
    """Métricas específicas da aplicação."""
    timestamp: datetime
    total_analises: int
    analises_por_minuto: float
    tempo_medio_analise: float
    cache_hit_rate: float
    workflows_ativos: int
    erros_por_minuto: float
    memoria_aplicacao_mb: float

@dataclass
class AlertaMonitoramento:
    """Representa um alerta do sistema de monitoramento."""
    id: str
    tipo: str
    severidade: str  # baixa, media, alta, critica
    titulo: str
    descricao: str
    timestamp: datetime
    resolvido: bool = False
    dados_contexto: Optional[Dict[str, Any]] = None

class MonitorSistema:
    """
    Monitor principal do sistema de otimização.
    
    Coleta métricas, detecta problemas e gera alertas para
    garantir a operação saudável do sistema.
    """
    
    def __init__(self):
        self.metricas_sistema_historico = []
        self.metricas_aplicacao_historico = []
        self.alertas_ativos = {}
        self.alertas_historico = []
        self.configuracao_alertas = self._carregar_configuracao_alertas()
        self.inicio_monitoramento = datetime.now()
        self.ultima_coleta = None
        
        # Contadores para métricas da aplicação
        self.contador_analises = 0
        self.contador_erros = 0
        self.tempos_analise = []
        
    def _carregar_configuracao_alertas(self) -> Dict[str, Any]:
        """Carrega configuração dos alertas."""
        return {
            'cpu_critico': 90.0,
            'cpu_alto': 75.0,
            'memoria_critica': 90.0,
            'memoria_alta': 80.0,
            'disco_critico': 95.0,
            'disco_alto': 85.0,
            'tempo_analise_lento': 30.0,  # segundos
            'cache_hit_rate_baixo': 50.0,  # percentual
            'erros_por_minuto_alto': 10,
            'max_historico_metricas': 1440,  # 24 horas (1 por minuto)
            'intervalo_coleta_segundos': 60
        }
    
    async def iniciar_monitoramento(self):
        """Inicia o loop de monitoramento contínuo."""
        logger.info("Iniciando monitoramento do sistema...")
        
        while True:
            try:
                await self._coletar_metricas()
                await self._verificar_alertas()
                await self._limpar_dados_antigos()
                
                # Aguarda próxima coleta
                await asyncio.sleep(self.configuracao_alertas['intervalo_coleta_segundos'])
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(30)  # Aguarda antes de tentar novamente
    
    async def _coletar_metricas(self):
        """Coleta métricas do sistema e da aplicação."""
        agora = datetime.now()
        
        # Métricas do sistema
        try:
            metricas_sistema = MetricasSistema(
                timestamp=agora,
                cpu_percent=psutil.cpu_percent(interval=1),
                memoria_percent=psutil.virtual_memory().percent,
                memoria_disponivel_mb=psutil.virtual_memory().available / (1024 * 1024),
                disco_percent=psutil.disk_usage('/').percent,
                disco_disponivel_gb=psutil.disk_usage('/').free / (1024 * 1024 * 1024),
                processos_ativos=len(psutil.pids()),
                conexoes_rede=len(psutil.net_connections())
            )
            
            self.metricas_sistema_historico.append(metricas_sistema)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
        
        # Métricas da aplicação
        try:
            metricas_app = await self._coletar_metricas_aplicacao(agora)
            self.metricas_aplicacao_historico.append(metricas_app)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas da aplicação: {e}")
        
        self.ultima_coleta = agora
    
    async def _coletar_metricas_aplicacao(self, timestamp: datetime) -> MetricasAplicacao:
        """Coleta métricas específicas da aplicação."""
        
        # Calcula análises por minuto
        analises_por_minuto = 0.0
        if self.ultima_coleta:
            intervalo_minutos = (timestamp - self.ultima_coleta).total_seconds() / 60
            if intervalo_minutos > 0:
                analises_por_minuto = self.contador_analises / intervalo_minutos
        
        # Calcula tempo médio de análise
        tempo_medio = 0.0
        if self.tempos_analise:
            tempo_medio = sum(self.tempos_analise) / len(self.tempos_analise)
        
        # Calcula erros por minuto
        erros_por_minuto = 0.0
        if self.ultima_coleta:
            intervalo_minutos = (timestamp - self.ultima_coleta).total_seconds() / 60
            if intervalo_minutos > 0:
                erros_por_minuto = self.contador_erros / intervalo_minutos
        
        # Obtém uso de memória do processo atual
        processo_atual = psutil.Process()
        memoria_app = processo_atual.memory_info().rss / (1024 * 1024)  # MB
        
        metricas = MetricasAplicacao(
            timestamp=timestamp,
            total_analises=self.contador_analises,
            analises_por_minuto=analises_por_minuto,
            tempo_medio_analise=tempo_medio,
            cache_hit_rate=await self._obter_cache_hit_rate(),
            workflows_ativos=await self._obter_workflows_ativos(),
            erros_por_minuto=erros_por_minuto,
            memoria_aplicacao_mb=memoria_app
        )
        
        # Reset dos contadores
        self.contador_analises = 0
        self.contador_erros = 0
        self.tempos_analise = []
        
        return metricas
    
    async def _obter_cache_hit_rate(self) -> float:
        """Obtém taxa de acerto do cache."""
        try:
            from servicos.gerenciador_cache import gerenciador_cache
            info_cache = await gerenciador_cache.obter_info_cache()
            return info_cache.get('taxa_acerto', 0.0)
        except Exception:
            return 0.0
    
    async def _obter_workflows_ativos(self) -> int:
        """Obtém número de workflows ativos."""
        try:
            # Aqui você integraria com o orquestrador para obter workflows ativos
            return 0  # Placeholder
        except Exception:
            return 0
    
    async def _verificar_alertas(self):
        """Verifica condições de alerta baseadas nas métricas coletadas."""
        if not self.metricas_sistema_historico or not self.metricas_aplicacao_historico:
            return
        
        ultima_metrica_sistema = self.metricas_sistema_historico[-1]
        ultima_metrica_app = self.metricas_aplicacao_historico[-1]
        
        # Verifica alertas de sistema
        await self._verificar_alerta_cpu(ultima_metrica_sistema)
        await self._verificar_alerta_memoria(ultima_metrica_sistema)
        await self._verificar_alerta_disco(ultima_metrica_sistema)
        
        # Verifica alertas de aplicação
        await self._verificar_alerta_performance(ultima_metrica_app)
        await self._verificar_alerta_cache(ultima_metrica_app)
        await self._verificar_alerta_erros(ultima_metrica_app)
    
    async def _verificar_alerta_cpu(self, metricas: MetricasSistema):
        """Verifica alertas relacionados ao uso de CPU."""
        cpu_percent = metricas.cpu_percent
        
        if cpu_percent >= self.configuracao_alertas['cpu_critico']:
            await self._criar_alerta(
                'cpu_critico',
                'critica',
                'CPU em uso crítico',
                f'Uso de CPU em {cpu_percent:.1f}% (crítico: ≥{self.configuracao_alertas["cpu_critico"]}%)',
                {'cpu_percent': cpu_percent}
            )
        elif cpu_percent >= self.configuracao_alertas['cpu_alto']:
            await self._criar_alerta(
                'cpu_alto',
                'alta',
                'CPU em uso elevado',
                f'Uso de CPU em {cpu_percent:.1f}% (alto: ≥{self.configuracao_alertas["cpu_alto"]}%)',
                {'cpu_percent': cpu_percent}
            )
        else:
            await self._resolver_alerta('cpu_critico')
            await self._resolver_alerta('cpu_alto')
    
    async def _verificar_alerta_memoria(self, metricas: MetricasSistema):
        """Verifica alertas relacionados ao uso de memória."""
        memoria_percent = metricas.memoria_percent
        
        if memoria_percent >= self.configuracao_alertas['memoria_critica']:
            await self._criar_alerta(
                'memoria_critica',
                'critica',
                'Memória em uso crítico',
                f'Uso de memória em {memoria_percent:.1f}% (crítico: ≥{self.configuracao_alertas["memoria_critica"]}%)',
                {'memoria_percent': memoria_percent, 'memoria_disponivel_mb': metricas.memoria_disponivel_mb}
            )
        elif memoria_percent >= self.configuracao_alertas['memoria_alta']:
            await self._criar_alerta(
                'memoria_alta',
                'alta',
                'Memória em uso elevado',
                f'Uso de memória em {memoria_percent:.1f}% (alto: ≥{self.configuracao_alertas["memoria_alta"]}%)',
                {'memoria_percent': memoria_percent, 'memoria_disponivel_mb': metricas.memoria_disponivel_mb}
            )
        else:
            await self._resolver_alerta('memoria_critica')
            await self._resolver_alerta('memoria_alta')
    
    async def _verificar_alerta_disco(self, metricas: MetricasSistema):
        """Verifica alertas relacionados ao uso de disco."""
        disco_percent = metricas.disco_percent
        
        if disco_percent >= self.configuracao_alertas['disco_critico']:
            await self._criar_alerta(
                'disco_critico',
                'critica',
                'Disco em uso crítico',
                f'Uso de disco em {disco_percent:.1f}% (crítico: ≥{self.configuracao_alertas["disco_critico"]}%)',
                {'disco_percent': disco_percent, 'disco_disponivel_gb': metricas.disco_disponivel_gb}
            )
        elif disco_percent >= self.configuracao_alertas['disco_alto']:
            await self._criar_alerta(
                'disco_alto',
                'alta',
                'Disco em uso elevado',
                f'Uso de disco em {disco_percent:.1f}% (alto: ≥{self.configuracao_alertas["disco_alto"]}%)',
                {'disco_percent': disco_percent, 'disco_disponivel_gb': metricas.disco_disponivel_gb}
            )
        else:
            await self._resolver_alerta('disco_critico')
            await self._resolver_alerta('disco_alto')
    
    async def _verificar_alerta_performance(self, metricas: MetricasAplicacao):
        """Verifica alertas relacionados à performance da aplicação."""
        tempo_medio = metricas.tempo_medio_analise
        
        if tempo_medio >= self.configuracao_alertas['tempo_analise_lento']:
            await self._criar_alerta(
                'performance_lenta',
                'media',
                'Performance de análise degradada',
                f'Tempo médio de análise em {tempo_medio:.2f}s (limite: {self.configuracao_alertas["tempo_analise_lento"]}s)',
                {'tempo_medio_analise': tempo_medio}
            )
        else:
            await self._resolver_alerta('performance_lenta')
    
    async def _verificar_alerta_cache(self, metricas: MetricasAplicacao):
        """Verifica alertas relacionados ao cache."""
        hit_rate = metricas.cache_hit_rate
        
        if hit_rate < self.configuracao_alertas['cache_hit_rate_baixo']:
            await self._criar_alerta(
                'cache_hit_baixo',
                'media',
                'Taxa de acerto do cache baixa',
                f'Taxa de acerto do cache em {hit_rate:.1f}% (mínimo: {self.configuracao_alertas["cache_hit_rate_baixo"]}%)',
                {'cache_hit_rate': hit_rate}
            )
        else:
            await self._resolver_alerta('cache_hit_baixo')
    
    async def _verificar_alerta_erros(self, metricas: MetricasAplicacao):
        """Verifica alertas relacionados a erros."""
        erros_por_minuto = metricas.erros_por_minuto
        
        if erros_por_minuto >= self.configuracao_alertas['erros_por_minuto_alto']:
            await self._criar_alerta(
                'erros_elevados',
                'alta',
                'Taxa de erros elevada',
                f'Erros por minuto: {erros_por_minuto:.1f} (limite: {self.configuracao_alertas["erros_por_minuto_alto"]})',
                {'erros_por_minuto': erros_por_minuto}
            )
        else:
            await self._resolver_alerta('erros_elevados')
    
    async def _criar_alerta(
        self,
        tipo: str,
        severidade: str,
        titulo: str,
        descricao: str,
        dados_contexto: Dict[str, Any]
    ):
        """Cria um novo alerta se não existir um ativo do mesmo tipo."""
        if tipo not in self.alertas_ativos:
            alerta = AlertaMonitoramento(
                id=f"{tipo}_{int(time.time())}",
                tipo=tipo,
                severidade=severidade,
                titulo=titulo,
                descricao=descricao,
                timestamp=datetime.now(),
                dados_contexto=dados_contexto
            )
            
            self.alertas_ativos[tipo] = alerta
            self.alertas_historico.append(alerta)
            
            logger.warning(f"ALERTA {severidade.upper()}: {titulo} - {descricao}")
    
    async def _resolver_alerta(self, tipo: str):
        """Resolve um alerta ativo."""
        if tipo in self.alertas_ativos:
            alerta = self.alertas_ativos[tipo]
            alerta.resolvido = True
            del self.alertas_ativos[tipo]
            
            logger.info(f"Alerta resolvido: {alerta.titulo}")
    
    async def _limpar_dados_antigos(self):
        """Remove dados antigos do histórico para economizar memória."""
        max_historico = self.configuracao_alertas['max_historico_metricas']
        
        if len(self.metricas_sistema_historico) > max_historico:
            self.metricas_sistema_historico = self.metricas_sistema_historico[-max_historico:]
        
        if len(self.metricas_aplicacao_historico) > max_historico:
            self.metricas_aplicacao_historico = self.metricas_aplicacao_historico[-max_historico:]
        
        # Remove alertas do histórico mais antigos que 7 dias
        limite_tempo = datetime.now() - timedelta(days=7)
        self.alertas_historico = [
            a for a in self.alertas_historico
            if a.timestamp > limite_tempo
        ]
    
    def registrar_analise(self, tempo_execucao: float):
        """Registra uma análise realizada."""
        self.contador_analises += 1
        self.tempos_analise.append(tempo_execucao)
    
    def registrar_erro(self):
        """Registra um erro ocorrido."""
        self.contador_erros += 1
    
    def obter_status_saude(self) -> Dict[str, Any]:
        """Obtém status geral de saúde do sistema."""
        if not self.metricas_sistema_historico or not self.metricas_aplicacao_historico:
            return {'status': 'inicializando', 'detalhes': 'Coletando métricas iniciais...'}
        
        ultima_sistema = self.metricas_sistema_historico[-1]
        ultima_app = self.metricas_aplicacao_historico[-1]
        
        # Determina status geral baseado nos alertas
        alertas_criticos = [a for a in self.alertas_ativos.values() if a.severidade == 'critica']
        alertas_altos = [a for a in self.alertas_ativos.values() if a.severidade == 'alta']
        
        if alertas_criticos:
            status = 'critico'
        elif alertas_altos:
            status = 'degradado'
        elif self.alertas_ativos:
            status = 'atencao'
        else:
            status = 'saudavel'
        
        return {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'uptime_segundos': (datetime.now() - self.inicio_monitoramento).total_seconds(),
            'alertas_ativos': len(self.alertas_ativos),
            'metricas_sistema': asdict(ultima_sistema),
            'metricas_aplicacao': asdict(ultima_app),
            'alertas_detalhes': [asdict(a) for a in self.alertas_ativos.values()]
        }
    
    def obter_metricas_historico(
        self,
        horas: int = 1,
        tipo: str = 'ambos'
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtém histórico de métricas.
        
        Args:
            horas: Número de horas de histórico
            tipo: 'sistema', 'aplicacao' ou 'ambos'
            
        Returns:
            Dicionário com histórico de métricas
        """
        limite_tempo = datetime.now() - timedelta(hours=horas)
        
        resultado = {}
        
        if tipo in ['sistema', 'ambos']:
            metricas_filtradas = [
                asdict(m) for m in self.metricas_sistema_historico
                if m.timestamp > limite_tempo
            ]
            resultado['sistema'] = metricas_filtradas
        
        if tipo in ['aplicacao', 'ambos']:
            metricas_filtradas = [
                asdict(m) for m in self.metricas_aplicacao_historico
                if m.timestamp > limite_tempo
            ]
            resultado['aplicacao'] = metricas_filtradas
        
        return resultado
    
    def obter_alertas_historico(self, dias: int = 7) -> List[Dict[str, Any]]:
        """Obtém histórico de alertas."""
        limite_tempo = datetime.now() - timedelta(days=dias)
        
        alertas_filtrados = [
            asdict(a) for a in self.alertas_historico
            if a.timestamp > limite_tempo
        ]
        
        return sorted(alertas_filtrados, key=lambda x: x['timestamp'], reverse=True)

# Instância global do monitor
monitor_sistema = MonitorSistema()

