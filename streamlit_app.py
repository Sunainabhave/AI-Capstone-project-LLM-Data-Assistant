import streamlit as st
import requests

BACKEND_URL = "https://ai-capstone-project-llm-data-assistant.onrender.com"

st.set_page_config(page_title="LLM Data Assistant")
st.title("LLM Data Assistant (Dynamic Data Classification)")

file = st.file_uploader("Upload a file", type=["csv", "txt", "pdf", "pptx"])
query = st.text_input("Ask your question:")

if st.button("Submit") and file and query:
    with st.spinner("Thinking..."):
        try:
            files = {"file": (file.name, file.getvalue())}
            data = {"query": query}
            res = requests.post(f"{BACKEND_URL}/ask", data=data, files=files)

            try:
                out = res.json()
                st.subheader("📦 Raw Response")
                st.json(out)
            except Exception:
                st.error("❌ Couldn't parse response as JSON.")
                st.text(res.text)
                st.stop()

            if "error" in out:
                st.error(f"❌ Backend Error: {out['error']}")
            else:
                st.subheader("🔧 Tool Call")
                if "tool_call" in out:
                    st.json(out["tool_call"])
                else:
                    st.warning("⚠️ tool_call missing from backend response.")

                st.subheader("📋 Result")
                if "result" in out:
                    st.write(out["result"])
                else:
                    st.warning("⚠️ result missing from backend response.")

                st.subheader("🧠 Summary")
                if "summary" in out:
                    st.write(out["summary"])
                else:
                    st.warning("⚠️ summary missing from backend response.")

        except Exception as e:
            st.error(f"⚠️ Request failed: {str(e)}")
