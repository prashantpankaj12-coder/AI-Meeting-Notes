from langchain_core.prompts import ChatPromptTemplate
from schemas import Topics, Summary, ActionItems, Priority
from state import MeetingState

NO_ACTIONS = "No action items identified in this meeting."


def _agent(llm, schema, system, human="Transcript:\n{transcript}"):
	"""Create a prompt-to-LLM chain that returns the requested schema."""
	prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
	return prompt | llm.with_structured_output(schema)


def make_nodes(llm):
	topic_agent = _agent(
		llm,
		Topics,
		"You are a meeting analyst. List the 3 to 6 main topics discussed in the transcript. "
		"Each topic is a short noun phrase (2-5 words). Do not invent topics that were not discussed.",
	)
	summary_agent = _agent(
		llm,
		Summary,
		"You write meeting summaries. Write 3 to 5 sentences covering what the meeting was about "
		"and any decisions made. Use only facts in the transcript.",
	)
	action_agent = _agent(
		llm,
		ActionItems,
		"You extract action items: tasks that someone commits to or is assigned. "
		"For each give the task (start with a verb) and the owner. Phrases like 'I will' mean the "
		"speaker is the owner. If no owner is stated, use 'Not specified'. "
		"Opinions, problems and general discussion are NOT action items. If there are none, return an empty list.",
	)
	priority_agent = _agent(
		llm,
		Priority,
		"You classify the overall urgency of the meeting's tasks as exactly one of: "
		"High Priority, Medium Priority, Low Priority.\n"
		"High: words like urgent, ASAP, immediately, today, by tomorrow, this week, before Friday, or a deadline within a few days.\n"
		"Medium: a deadline in the next few weeks, 'next week', 'soon'.\n"
		"Low: no deadline or 'when possible', 'someday'.\n"
		"Give a one-sentence reason quoting the deciding phrase.",
		human="Transcript:\n{transcript}\n\nAction items:\n{action_text}",
	)

	def input_node(state: MeetingState):
		text = " ".join(state.get("transcript", "").split())
		if not text:
			raise ValueError("Transcript is empty.")
		return {"transcript": text}

	def topic_node(state: MeetingState):
		return {"topics": topic_agent.invoke(state).topics}

	def summary_node(state: MeetingState):
		return {"summary": summary_agent.invoke(state).summary}

	def action_node(state: MeetingState):
		items = action_agent.invoke(state).items
		return {"action_items": [item.model_dump() for item in items]}

	def priority_node(state: MeetingState):
		action_text = "\n".join(
			f"- {item['task']} ({item['owner']})" for item in state["action_items"]
		)
		out = priority_agent.invoke(
			{"transcript": state["transcript"], "action_text": action_text}
		)
		return {"priority": out.level, "priority_reason": out.reason}

	def final_node(state: MeetingState):
		items = state.get("action_items", [])
		lines = ["# Meeting Report", "", "## Meeting Summary", state["summary"], "", "## Key Topics"]
		lines += [f"{number}. {topic}" for number, topic in enumerate(state["topics"], 1)]
		lines += ["", "## Action Items"]
		if items:
			lines += [f"{number}. {item['task']}" for number, item in enumerate(items, 1)]
			lines += ["", "## Task Owners"]
			lines += [f"- {item['task']}: {item['owner']}" for item in items]
			lines += ["", "## Priority Level", f"{state['priority']} - {state['priority_reason']}"]
		else:
			lines += [NO_ACTIONS]
		return {"final_report": "\n".join(lines)}

	return input_node, topic_node, summary_node, action_node, priority_node, final_node
