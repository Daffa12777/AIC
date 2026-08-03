"""Custom exceptions untuk backend AlumiSight AI."""


class DatasetValidationError(Exception):
    def __init__(self, message: str, missing_columns: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.missing_columns = missing_columns or []


class ModelNotTrainedError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
