from pydantic import BaseModel
from typing import List
from llama_index.core.program import FunctionCallingProgram

class Metadata(BaseModel):
    """Data model for the metadata field."""
    column_names: List[str]
    column_types: List[str]
    row_count: int

class IndexRow(BaseModel):
    """Data model for each row in the result set."""
    ranking: int
    coin: str
    price_today: float
    optimized_relative_strength: float
    narrative: str

class IndexResult(BaseModel):
    """Data model for the result field."""
    rows: List[IndexRow]
    metadata: Metadata
    role : str = 'Function'
class NarrativeRow(BaseModel):
    """Data model for each row in the result set."""
    optimized_relative_strength: float
    price_growth: float
    relative_strategy: float
    relative_strength: float
    signal: str

class NarrativeResult(BaseModel):
    """Data model for the result field."""
    rows: List[NarrativeRow]
    metadata: Metadata
    role : str = 'Function'

def get_structured_response(response, output_cls):

    prompt_template_str = """ Generate structured output data using {response}  """

    program = FunctionCallingProgram.from_defaults(
        output_cls=output_cls,
        prompt_template_str=prompt_template_str,
        verbose=True,
    )
    output = program(response=response)
    return output.dict()
