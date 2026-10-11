from langgraph.graph import StateGraph, START, END
from state import MeetingState
from nodes import make_nodes


def route_after_actions(state: MeetingState) -> str:
	"""Conditional edge: only classify priority when there is something to prioritise."""
	return "priority" if state.get("action_items") else "final_report"


def build_graph(llm):
	input_node, topic_node, summary_node, action_node, priority_node, final_node = make_nodes(llm)
	g = StateGraph(MeetingState)
	g.add_node("input", input_node)
	g.add_node("topics", topic_node)
	g.add_node("summary", summary_node)
	g.add_node("actions", action_node)
	g.add_node("priority", priority_node)
	g.add_node("final_report", final_node)

	g.add_edge(START, "input")
	g.add_edge("input", "topics")
	g.add_edge("topics", "summary")
	g.add_edge("summary", "actions")
	g.add_conditional_edges("actions", route_after_actions, {"priority": "priority", "final_report": "final_report"})
	g.add_edge("priority", "final_report")
	g.add_edge("final_report", END)
	return g.compile()
