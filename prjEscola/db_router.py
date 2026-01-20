class DB2Router:
    """
    Roteador de banco de dados para direcionar alguns modelos ao banco 'pessoas'.
    """

    def db_for_read(self, model, **hints):
        """Lê do banco correto."""
        if model._meta.app_label == 'rh':  # Troque pelo seu app
            return 'colaboradores'
      
        return 'default'

    def db_for_write(self, model, **hints):
        """Escreve no banco correto."""
        if model._meta.app_label == 'rh':  # Troque pelo seu app
            return 'colaboradores'

        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
       """Permite relações entre bancos diferentes?"""
       return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Decide se deve aplicar migração para o banco certo."""
        if app_label == 'rh':  # Apenas migra esse app para colaboradores
            return db == 'colaboradores'
        
        
        return db == 'default'
    
    
    
