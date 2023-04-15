from dataclasses import dataclass, asdict


@dataclass
class User:
    name: str
    age: str
    queries: list[str]
    food_item: list[str]
    
    dict = asdict