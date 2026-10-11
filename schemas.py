from typing import List, Literal
from pydantic import BaseModel, Field


class Topics(BaseModel):
	topics: List[str] = Field(description="3 to 6 short topic names, 2-5 words each")


class Summary(BaseModel):
	summary: str = Field(description="A 3 to 5 sentence summary of the meeting")


class ActionItem(BaseModel):
	task: str = Field(description="What must be done, starting with a verb")
	owner: str = Field(default="Not specified", description="Person responsible, or 'Not specified'")


class ActionItems(BaseModel):
	items: List[ActionItem] = Field(default_factory=list)


class Priority(BaseModel):
	level: Literal["High Priority", "Medium Priority", "Low Priority"]
	reason: str = Field(description="One sentence naming the phrase or fact that decided the level")
