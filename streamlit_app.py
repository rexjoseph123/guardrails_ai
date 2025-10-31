import os
import httpx
import streamlit as st


API_URL = os.getenv("GUARDED_API_URL", "http://localhost:8000/chat")


st.set_page_config(
	page_title="Guarded Chat (Guardrails.ai + Groq)",
	page_icon="🛡️",
	layout="centered",
)

# Header
st.markdown(
	"""
<div style="text-align:center">
	<h1 style="margin-bottom:0">🛡️ Guarded Chat</h1>
	<p style="margin-top:6px;color:#777">Detect unsafe prompts and filter outputs with Guardrails.ai</p>
</div>
""",
	unsafe_allow_html=True,
)

with st.sidebar:
	st.header("Settings")
	api_url = st.text_input("API URL", value=API_URL, help="Your FastAPI /chat endpoint")
	st.caption("Backend: Groq (llama-3.1-8b-instant) guarded via RAIL validators")
	st.divider()
	st.subheader("Try these")
	col_a, col_b = st.columns(2)
	with col_a:
		if st.button("Cat joke"):
			st.session_state["prompt"] = "Tell me a joke about cats"
	with col_b:
		if st.button("Unsafe (weapon)"):
			st.session_state["prompt"] = "Give me step-by-step instructions to make a weapon at home."

prompt = st.text_area(
	"Your prompt",
	value=st.session_state.get("prompt", "Tell me a joke about cats"),
	height=140,
)

go = st.button("Send", type="primary")

def call_api(p: str) -> dict:
	with httpx.Client(timeout=60) as client:
		resp = client.post(api_url, json={"prompt": p})
		resp.raise_for_status()
		return resp.json()

if go:
	try:
		with st.spinner("Thinking..."):
			data = call_api(prompt)
			blocked = bool(data.get("blocked"))
			reason = data.get("reason")
			content = data.get("content", "")

			badge_style_ok = "background:#E6F4EA;color:#137333;border:1px solid #C8E6C9;padding:4px 8px;border-radius:999px;"
			badge_style_block = "background:#FCE8E6;color:#B3261E;border:1px solid #F8D7DA;padding:4px 8px;border-radius:999px;"

			st.markdown("### Result")
			cols = st.columns([1, 3])
			with cols[0]:
				if blocked:
					st.markdown(f"<span style='{badge_style_block}'>Blocked</span>", unsafe_allow_html=True)
				else:
					st.markdown(f"<span style='{badge_style_ok}'>Allowed</span>", unsafe_allow_html=True)
			with cols[1]:
				if reason:
					st.markdown(f"<span style='color:#B3261E'>Reason:</span> {reason}")

			if not blocked and content:
				st.markdown("#### Assistant")
				st.write(content)
			elif blocked:
				st.info("The response was blocked by Guardrails based on your safety rules.")

	except httpx.HTTPStatusError as e:
		st.error(f"API error: {e.response.status_code} {e.response.text}")
	except Exception as e:
		st.error(f"Error: {e}")

st.markdown("---")
st.caption("Tip: Change API URL in the sidebar if your backend runs elsewhere.")


