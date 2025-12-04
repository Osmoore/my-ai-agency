import streamlit as st
from google import genai
from tavily import TavilyClient
import os

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Research Agency", page_icon="🕵️", layout="wide")

# 2. LOAD KEYS (Auto-detect from Secrets OR Sidebar)
# We check if the key exists in the Cloud Secrets first
if "GOOGLE_API_KEY" in st.secrets:
    google_api_key = st.secrets["GOOGLE_API_KEY"]
else:
    google_api_key = st.sidebar.text_input("Google API Key", type="password")

if "TAVILY_API_KEY" in st.secrets:
    tavily_api_key = st.secrets["TAVILY_API_KEY"]
else:
    tavily_api_key = st.sidebar.text_input("Tavily API Key", type="password")

# 3. DEFINE THE TOOLS
def search_web(topic, tavily_key):
    try:
        # Use the key passed to the function
        tavily = TavilyClient(api_key=tavily_key)
        response = tavily.search(query=topic, search_depth="advanced", max_results=5)
        
        context = []
        for result in response.get('results', []):
            context.append(f"Source: {result['title']}\nURL: {result['url']}\nContent: {result['content']}")
        
        return "\n\n".join(context)
    except Exception as e:
        return f"Search Error: {e}"

def generate_summary(query, raw_data, google_key):
    try:
        client = genai.Client(api_key=google_key)
        prompt = f"""
        You are a senior market research analyst. 
        Write a professional executive summary answering the user's question.
        Use strict factual data from the search results below.
        
        USER QUESTION: {query}
        
        SEARCH DATA:
        {raw_data}
        """
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

# 4. MAIN DASHBOARD UI
st.title("🕵️ GH-Automate: Commercial Intelligence")
st.markdown("### Enterprise-Grade Market Research")

# Hide the sidebar info if keys are already loaded
if "GOOGLE_API_KEY" not in st.secrets:
    st.sidebar.info("Enter keys to start.")

query = st.text_input("Research Topic", placeholder="e.g., Current price of 50kg Dangote Cement in Accra")

if st.button("🚀 Run Analysis", type="primary"):
    if not google_api_key or not tavily_api_key:
        st.error("⚠️ API Keys are missing! Please check settings or sidebar.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with st.status("🕵️ Agent is working...", expanded=True) as status:
            st.write("Connecting to Tavily API...")
            raw_data = search_web(query, tavily_api_key)
            st.write("Reading search results...")
            
            st.write("Synthesizing report with Gemini...")
            final_report = generate_summary(query, raw_data, google_api_key)
            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

        st.markdown("---")
        st.subheader("📄 Executive Summary")
        st.markdown(final_report)
        
        with st.expander("🔍 View Raw Data (Proof)"):
            st.text(raw_data)
