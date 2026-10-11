from langchain_core.runnables import RunnableLambda
from schemas import Topics, Summary, ActionItem, ActionItems, Priority
from graph import build_graph


class FakeLLM:
	"""Stands in for a real model: returns canned answers, no API key needed."""

	def __init__(self, items):
		self.items = items

	def with_structured_output(self, schema):
		answers = {
			Topics: Topics(topics=["Website performance"]),
			Summary: Summary(summary="The team discussed website speed."),
			ActionItems: ActionItems(items=self.items),
			Priority: Priority(level="High Priority", reason="'this week' was mentioned"),
		}
		return RunnableLambda(lambda _: answers[schema])


def test_priority_runs_when_actions_exist():
	app = build_graph(FakeLLM([ActionItem(task="Optimize queries", owner="David")]))
	result = app.invoke({"transcript": "David: I will optimize queries this week."})
	assert result["priority"] == "High Priority"
	assert "David" in result["final_report"]


def test_priority_skipped_when_no_actions():
	app = build_graph(FakeLLM([]))
	result = app.invoke({"transcript": "We chatted about lunch."})
	assert "priority" not in result
	assert "No action items identified in this meeting." in result["final_report"]
