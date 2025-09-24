from pydantic import BaseModel, validator


class GenrePredictionRequest(BaseModel):
    customer_id: int
    
    @validator("customer_id")
    def validate_customer_id(cls, customer_id):
        if customer_id <= 0:
            raise ValueError("customer_id must be a positive integer")
        return customer_id


class GenrePredictionResponse(BaseModel):
    Genre: str