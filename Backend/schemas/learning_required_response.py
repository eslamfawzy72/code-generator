from schemas.response_schema import BaseResponse


class LearningRequiredResponse(BaseResponse):
    needs_learning: bool = True
    message: str