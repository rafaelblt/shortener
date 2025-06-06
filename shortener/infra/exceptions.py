class MissingEnvironmentVariableError(Exception):
    def __init__(self, var_name: str):
        self.var_name = var_name
        super().__init__(f"Missing required environment variable: {var_name}")
