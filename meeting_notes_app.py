import streamlit as st
from llm import get_llm
from graph import build_graph

st.set_page_config(page_title="AI Meeting Notes Analyzer", layout="wide")
st.title("AI Meeting Notes Analyzer")
st.caption("Upload a transcript or paste its text to generate structured meeting notes.")

SAMPLE = """John: We need to improve the website performance.
Sarah: Yes, page load time is too slow.
David: I will optimize the database queries this week.
Sarah: I will redesign the homepage layout.
John: Let's try to finish these tasks before Friday."""


@st.cache_resource
def load_graph():
	return build_graph(get_llm())  # built once, reused on every click


input_method = st.radio("Transcript source", ["Paste text", "Upload .txt file"], horizontal=True)

if input_method == "Paste text":
	transcript = st.text_area("Meeting transcript", value=SAMPLE, height=260)
else:
	uploaded_file = st.file_uploader("Choose a transcript file", type=["txt"])
	transcript = ""
	if uploaded_file is not None:
		try:
			transcript = uploaded_file.getvalue().decode("utf-8-sig")
		except UnicodeDecodeError:
			st.error("The transcript file must be encoded as UTF-8.")

if st.button("Analyze meeting", type="primary"):
	if not transcript.strip():
		st.warning("Please paste a transcript first.")
	else:
		with st.spinner("Agents are working..."):
			result = load_graph().invoke({"transcript": transcript})

		st.subheader("Meeting Summary")
		st.write(result["summary"])

		st.subheader("Key Topics")
		for n, topic in enumerate(result["topics"], 1):
			st.write(f"{n}. {topic}")

		st.subheader("Action Items and Owners")
		if result["action_items"]:
			st.table(result["action_items"])
			level = result["priority"]
			st.subheader("Priority Level")
			{"High Priority": st.error, "Medium Priority": st.warning, "Low Priority": st.success}[level](level)
			st.caption(result["priority_reason"])
		else:
			st.info("No action items identified in this meeting.")

		st.subheader("Full Meeting Report")
		st.markdown(result["final_report"])
