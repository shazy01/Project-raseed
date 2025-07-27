import streamlit as st
import requests
import json

# Sidebar for navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["📄 Receipt Upload", "🧠 Query Assistant", "📊 Spending Analysis"])

# ----------------------------
# 📄 Receipt Upload Page
# ----------------------------
if page == "📄 Receipt Upload":
    st.title("📄 Receipt Uploader")
    st.markdown("Upload a receipt image and extract structured data using your Django + Gemini backend.")

    uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file and st.button("Upload and Extract"):
        with st.spinner("Uploading and analyzing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post("http://localhost:8000/api/receipts/upload/", files=files)

                if response.status_code == 201:
                    st.success("✅ Upload successful and data extracted!")
                    data = response.json()
                    st.subheader("🧾 Extracted Receipt Data")
                    st.json(data.get("extracted_data", {}))
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error("⚠️ An error occurred.")
                st.exception(e)

# ----------------------------
# 🧠 Query Assistant Page
# ----------------------------
elif page == "🧠 Query Assistant":
    st.title("🧠 Query Assistant")
    st.markdown("Enter a question to get an answer from the Django backend.")

    query_input = st.text_input("Enter your query:")

    if st.button("Ask"):
        if not query_input.strip():
            st.warning("Please enter a query.")
        else:
            try:
                with st.spinner("Thinking..."):
                    response = requests.post(
                        "http://localhost:8000/api/queries/ask/",
                        json={"query": query_input}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Response received:")
                        st.write(result.get("response", "No response found."))
                    else:
                        st.error(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error("⚠️ An error occurred.")
                st.exception(e)

# ----------------------------
# 📊 Spending Analysis Page
# ----------------------------
elif page == "📊 Spending Analysis":
    st.title("📊 Spending Analysis")
    st.markdown("Paste your JSON input below for analysis.")

    json_input = st.text_area("Input JSON", height=200)

    if st.button("Analyze Spending"):
        if not json_input.strip():
            st.warning("Please paste valid JSON.")
        else:
            try:
                parsed_input = json.loads(json_input)  # Validate JSON
                with st.spinner("Analyzing spending data..."):
                    response = requests.post(
                        "http://localhost:8000/api/spendinganalysis/analyze/",
                        json=parsed_input
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Analysis complete!")
                        st.subheader("🧾 Analysis Result")
                        st.json(result)
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.text(response.text)
            except json.JSONDecodeError:
                st.error("⚠️ Invalid JSON input.")
            except Exception as e:
                st.error("⚠️ An error occurred.")
                st.exception(e)
