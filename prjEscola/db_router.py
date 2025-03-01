class DB2Router:
    """
    Roteador de banco de dados para direcionar alguns modelos ao banco 'pessoas'.
    """

    def db_for_read(self, model, **hints):
        """Lê do banco correto."""
        if model._meta.app_label == 'app_cargo':  # Troque pelo seu app
            return 'colaboradores'
        elif model._meta.app_label == 'app_falta':
            return 'colaboradores'
        elif model._meta.app_label == 'app_pessoa':
            return 'colaboradores'
        elif model._meta.app_label == 'app_ficha_cem':
            return 'colaboradores'
        return 'default'

    def db_for_write(self, model, **hints):
        """Escreve no banco correto."""
        if model._meta.app_label == 'app_cargo':  # Troque pelo seu app
            return 'colaboradores'
        elif model._meta.app_label == 'app_falta':
            return 'colaboradores'
        elif model._meta.app_label == 'app_pessoa':
            return 'colaboradores'
        elif model._meta.app_label == 'app_ficha_cem':
            return 'colaboradores'


        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Permite relações entre bancos diferentes?"""
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Decide se deve aplicar migração para o banco certo."""
        if app_label == 'app_cargo':  # Apenas migra esse app para colaboradores
            return db == 'colaboradores'
        elif app_label == 'app_falta':  
            return db == 'colaboradores'
        elif app_label == 'app_pessoa':  
            return db == 'colaboradores'
        elif app_label == 'app_ficha_cem':  
            return db == 'colaboradores'
        
        return db == 'default'
