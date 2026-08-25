import sqlite3
import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Processa as métricas coletadas"

    def handle(self, *args, **options):

        # =====================================================
        # 1. CARREGAR DADOS BRUTOS
        # =====================================================

        db_path = settings.DATABASES["monitoramento"]["NAME"]

        self.stdout.write(
            f"Banco: {db_path}"
        )

        connection = sqlite3.connect(db_path)

        query = """
            SELECT
                data_hora,
                operacao,
                sql,
                tempo_execucao_ms,
                banco,
                endpoint,
                metodo,
                sucesso
            FROM monitoramento_coletametricasbancosql
        """

        df = pd.read_sql_query(
            query,
            connection
        )

        connection.close()

        # =====================================================
        # 2. CONVERTER TIPOS
        # =====================================================

        df["data_hora"] = pd.to_datetime(
            df["data_hora"]
        )

        # =====================================================
        # 3. INFORMAÇÕES BÁSICAS
        # =====================================================

        self.stdout.write(
            f"Registros encontrados: {len(df)}"
        )

        print("\n=== TIPOS ===")
        print(df.dtypes)

        print("\n=== VALORES NULOS ===")
        print(df.isnull().sum())

        print("\n=== OPERAÇÕES ===")
        print(df["operacao"].value_counts())

        print("\n=== BANCOS ===")
        print(df["banco"].value_counts())

        print("\n=== ESTATÍSTICAS DO TEMPO ===")
        print(df["tempo_execucao_ms"].describe())

        # =====================================================
        # 4. CRIAR FEATURES
        # =====================================================

        features = (
            df.groupby(
                ["sql", "banco", "operacao", "endpoint", "metodo"]
            )
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

        # =====================================================
        # 5. TRATAR DESVIO PADRÃO
        # =====================================================

        features["desvio_padrao"] = (
            features["desvio_padrao"]
            .fillna(0)
        )

        # =====================================================
        # 6. EXIBIR FEATURES
        # =====================================================

        print("\n=== FEATURES ===")

        print(
            features.head(20).to_string(
                index=False
            )
        )

        print(
            "\nQuantidade de consultas processadas:",
            len(features)
        )
        
        
        
        from sklearn.ensemble import IsolationForest
        colunas_features = [
        "qtd_execucoes",
        "tempo_medio",
        "p95_tempo",
        "desvio_padrao",
        "taxa_sucesso",
        ]

        X = features[colunas_features]

        modelo = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        features["anomalia"] = modelo.fit_predict(X)
        
        print("\n=== RESULTADO ===")

        print(
            features[
            [
               "qtd_execucoes",
               "tempo_medio",
               "p95_tempo",
               "desvio_padrao",
               "taxa_sucesso",
                "anomalia"
            ]
            ].to_string(index=False)
        )
        
        anomalias = features[
        features["anomalia"] == -1
        ]
        
        print("\n=== POSSÍVEIS ANOMALIAS ===")

        print(
            anomalias[
                [
                "sql",
                "banco",
                "operacao",
                "endpoint",
                "metodo",
                "qtd_execucoes",
                "tempo_medio",
                "tempo_minimo",
                "tempo_maximo",
                "desvio_padrao",
                "p95_tempo",
                "taxa_sucesso",
                "anomalia"
                ]
            ].to_string(index=False)
        )
        
        # Cria o modelo
        #import joblib
        #joblib.dump(
        #    modelo,
        #"modelo_isolation_forest.joblib"
        #)