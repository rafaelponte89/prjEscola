import time
from contextlib import ExitStack

from django.db import connections
from .models import ColetaMetricasBancoSQL


class MonitoramentoMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("NOVA REQUISIÇÃO:", request.method, request.path)
        from django.utils import timezone

        print("timezone.now():", timezone.now())
        print("TIME_ZONE:", timezone.get_current_timezone())
        
        metricas = []

        def criar_wrapper(banco):

            def wrapper(execute, sql, params, many, context):

                inicio = time.perf_counter()

                try:
                    resultado = execute(
                        sql,
                        params,
                        many,
                        context
                    )

                    sucesso = True

                    return resultado

                except Exception:
                    sucesso = False
                    raise

                finally:

                    fim = time.perf_counter()

                    tempo_ms = round(
                        (fim - inicio) * 1000,
                        3
                    )

                    # Retira quebra de linha e espaços em branco do início e do fim da query
                    sql_limpo = sql.strip()

                    # Ignora queries vazias
                    if not sql_limpo:
                        return

                    # Ignora queries de controle de transação
                    operacao = sql_limpo.split()[0].upper()

                    if operacao in {
                        "BEGIN",
                        "COMMIT",
                        "ROLLBACK",
                        "SAVEPOINT",
                        "RELEASE",
                    }:
                        return
                    print(
                        "CAPTURADO:",
                            banco,
                        operacao,
                        sql_limpo[:80]
                    )
                    metricas.append({
                        "operacao": operacao,
                        "sql": sql_limpo,
                        "tempo_execucao_ms": tempo_ms,
                        "banco": banco,
                        "endpoint": request.path,
                        "metodo": request.method,
                        "sucesso": sucesso,

                    })

            return wrapper

        ignore_bancos = {
            "monitoramento",
        }

        with ExitStack() as stack:

            for banco in connections.databases.keys():
                
                if banco in ignore_bancos:
                    continue

                connection = connections[banco]

                stack.enter_context(
                    connection.execute_wrapper(
                        criar_wrapper(banco)
                    )
                )

            response = self.get_response(request)
        
        # Salva as métricas no banco de monitoramento
        for metrica in metricas:
            
            ColetaMetricasBancoSQL.objects.using(
                "monitoramento"
            ).create(**metrica)
        

        return response