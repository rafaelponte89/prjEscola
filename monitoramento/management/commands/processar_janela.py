import sqlite3
import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Processa as métricas coletadas"

    def handle(self, *args, **options):

        # ==========================================
        # 1. CARREGAR DADOS
        # ==========================================

        db_path = settings.DATABASES["monitoramento"]["NAME"]

        self.stdout.write(
            f"Banco: {db_path}"
        )

        connection = sqlite3.connect(db_path)

        query = """
            SELECT
                data_hora,
                operacao,
                endpoint,
                metodo,
                sql,
                tempo_execucao_ms,
                banco,
                sucesso
            FROM monitoramento_coletametricasbancosql
        """

        df = pd.read_sql_query(
            query,
            connection
        )

        connection.close()

        # ==========================================
        # 2. CONVERTER DATA
        # ==========================================

        df["data_hora"] = pd.to_datetime(
            df["data_hora"]
        )

        # ==========================================
        # 3. CRIAR JANELA DE 1 HORA
        # ==========================================

        df["janela"] = (
            df["data_hora"].dt.floor("h")
        )

        # ==========================================
        # 4. INFORMAÇÕES
        # ==========================================

        self.stdout.write(
            f"Registros encontrados: {len(df)}"
        )

        print("\n=== TIPOS ===")
        print(df.dtypes)

        print("\n=== VALORES NULOS ===")
        print(df.isnull().sum())

        print("\n=== ESTATÍSTICAS ===")
        print(
            df["tempo_execucao_ms"].describe()
        )

        # ==========================================
        # 5. CRIAR FEATURES
        # ==========================================

        features = (
            df.groupby([
                "sql",
                "banco",
                "operacao",
                "endpoint",
                "metodo",
                "janela"
            ])
            .agg(

                qtd_execucoes=(
                    "tempo_execucao_ms",
                    "count"
                ),

                tempo_medio=(
                    "tempo_execucao_ms",
                    "mean"
                ),

                tempo_minimo=(
                    "tempo_execucao_ms",
                    "min"
                ),

                tempo_maximo=(
                    "tempo_execucao_ms",
                    "max"
                ),

                desvio_padrao=(
                    "tempo_execucao_ms",
                    "std"
                ),
                
                p95_tempo=(
                    "tempo_execucao_ms",
                    lambda x: x.quantile(0.95),
                ),

                taxa_sucesso=(
                    "sucesso",
                    "mean"
                )
            )
            .reset_index()
        )

        # ==========================================
        # 6. TRATAR DESVIO PADRÃO
        # ==========================================

        features["desvio_padrao"] = (
            features["desvio_padrao"]
            .fillna(0)
        )

        # ==========================================
        # 7. MOSTRAR RESULTADO
        # ==========================================

        print("\n=== FEATURES ===")

        print(
            features.head(20).to_string(
                index=False
            )
        )

        self.stdout.write(
            f"\nAmostras geradas: {len(features)}"
        )