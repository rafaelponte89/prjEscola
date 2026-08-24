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

        def criar_wrapper(alias):

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

                    sql_limpo = sql.strip()

                    if not sql_limpo:
                        return

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
                            alias,
                        operacao,
                        sql_limpo[:80]
                    )
                    metricas.append({
                        "operacao": operacao,
                        "sql": sql_limpo,
                        "tempo_ms": tempo_ms,
                        "sucesso": sucesso,
                        "banco": alias,
                        "endpoint": request.path,
                        "metodo": request.method,
                    })

            return wrapper

        bancos_monitorados = [
            "default",
            "aluno",
            "rh",
        ]

        with ExitStack() as stack:

            for alias in bancos_monitorados:

                connection = connections[alias]

                stack.enter_context(
                    connection.execute_wrapper(
                        criar_wrapper(alias)
                    )
                )

            response = self.get_response(request)

        # Salva as métricas no banco de monitoramento
        for metrica in metricas:

            ColetaMetricasBancoSQL.objects.using(
                "monitoramento"
            ).create(
                operacao=metrica["operacao"],
                sql=metrica["sql"],
                tempo_execucao_ms=metrica["tempo_ms"],
                banco=metrica["banco"],
                sucesso=metrica["sucesso"],
                endpoint=metrica["endpoint"],
                metodo=metrica["metodo"],
            )

        return response