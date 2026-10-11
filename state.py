from typing import TypedDict, List, Dict


class MeetingState(TypedDict, total=False):
	transcript: str
	topics: List[str]
	summary: str
	action_items: List[Dict[str, str]]
	priority: str
	priority_reason: str
	final_report: str
