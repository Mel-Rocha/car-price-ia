from fastapi import HTTPException


class InvalidCategoryException(HTTPException):
    VALID_CATEGORIES = [
        "fuel",
        "gear"
    ]

    def __init__(self, category):
        self.category = category
        detail = f"category inválido: {category}. Indique um dos seguintes categorys: {', '.join(self.VALID_CATEGORIES)}"
        super().__init__(status_code=400, detail=detail)
