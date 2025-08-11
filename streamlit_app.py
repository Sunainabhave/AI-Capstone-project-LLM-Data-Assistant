import streamlit as st
import requests

st.set_page_config(page_title="LLM Data Assistant")
st.title("LLM Data Assistant (Dynamic Data Classification)")

# ✅ File upload (supports CSV, TXT, PDF, PPTX)
file = st.file_uploader("Upload a file", type=["csv", "txt", "pdf", "pptx"])

# ✅ User question input
query = st.text_input("Ask your question:")

# ✅ Only trigger when both file and query are provided
if st.button("Submit") and file and query:
    with st.spinner("Thinking..."):
        try:
            # 📨 Prepare file and query to send to backend
            files = {"file": (file.name, file.getvalue())}
            data = {"query": query}
            res = requests.post("http://localhost:8000/ask", data=data, files=files)

            # ✅ Parse backend response
            try:
                out = res.json()
                st.subheader("📦 Raw Response")
                st.json(out)
            except Exception:
                st.error("❌ Couldn't parse response as JSON.")
                st.text(res.text)
                st.stop()

            # ❗ Check for top-level error key
            if "error" in out:
                st.error(f"❌ Backend Error: {out['error']}")
            else:
                # ✅ Display tool_call
                st.subheader("🔧 Tool Call")
                if "tool_call" in out:
                    st.json(out["tool_call"])
                else:
                    st.warning("⚠️ tool_call missing from backend response.")

                # ✅ Display result
                st.subheader("📋 Result")
                if "result" in out:
                    st.write(out["result"])
                else:
                    st.warning("⚠️ result missing from backend response.")

                # ✅ Display summary
                st.subheader("🧠 Summary")
                if "summary" in out:
                    st.write(out["summary"])
                else:
                    st.warning("⚠️ summary missing from backend response.")

        except Exception as e:
            st.error(f"⚠️ Request failed: {str(e)}")
