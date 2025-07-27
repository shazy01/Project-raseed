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
                response = requests.post("http://127.0.0.1:8000/api/receipts/upload/", files=files)

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
    st.markdown("Ask a question or give an action-based instruction.")

    query_input = st.text_input("Enter your query:")

    if st.button("Ask"):
        if not query_input.strip():
            st.warning("Please enter a query.")
        else:
            try:
                with st.spinner("Processing your request..."):
                    response = requests.post(
                        "http://localhost:8000/api/queries/ask/",
                        json={"query": query_input}
                    )
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            # Check if the response contains a wallet pass or structured JSON
                            if "answer" in result and isinstance(result["answer"], str):
                                st.success("✅ Response:")
                                st.write(result["answer"])
                            else:
                                st.success("✅ JSON Response:")
                                st.json(result)
                        except Exception as parse_error:
                            st.error("⚠️ Response received, but parsing failed.")
                            st.text(response.text)
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
    st.markdown("Get personalized insights from your receipt data.")

    user_query = st.text_input("Ask a financial question (e.g. How can I save more?)")

    if st.button("Analyze Spending"):
        if not user_query.strip():
            st.warning("Please enter a query.")
        else:
            try:
                with st.spinner("Analyzing your spending data..."):
                    response = requests.post(
                        "http://localhost:8000/api/spendinganalysis/analyze/",
                        json={"query": user_query}
                    )

                    if response.status_code == 200:
                        result = response.json()

                        # Display Gemini's analysis
                        analysis = result.get("analysis_text", "")
                        st.subheader("🧠 Gemini Analysis")
                        st.write(analysis)

                        # Display chart data if available
                        category_data = result.get("category_data", [])
                        if category_data:
                            import pandas as pd
                            import altair as alt
                            df = pd.DataFrame(category_data)
                            st.subheader("📊 Item Count by Category")
                            chart = alt.Chart(df).mark_bar().encode(
                                x='category:N',
                                y='item_count:Q',
                                tooltip=['category', 'item_count']
                            ).properties(width=600)
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.info("No categorized items to display.")

                    else:
                        st.error(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error("⚠️ An error occurred.")
                st.exception(e)
