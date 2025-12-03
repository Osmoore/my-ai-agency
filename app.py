import streamlit as st
from google import genai
from tavily import TavilyClient

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Research Agency", page_icon="🕵️", layout="wide")

# 2. SIDEBAR - SECURE KEY INPUT
with st.sidebar:
    st.header("⚙️ Mission Control")
    google_api_key = st.text_input("Google API Key", type="password")
    tavily_api_key = st.text_input("Tavily API Key", type="password")
    
    st.info("Keys are never stored. They are used only for this session.")
    st.markdown("---")
    st.write("### 🤖 Agent Specs")
    st.write("• **Brain:** Gemini 2.0 Flash")
    st.write("• **Eyes:** Tavily Search API")

# 3. DEFINE THE TOOLS
def search_web(topic, tavily_key):
    """Runs the search using Tavily (Commercial Grade)"""
    try:
        tavily = TavilyClient(api_key=tavily_key)
        # 'search_depth="advanced"' gives deeper, better results for business topics
        response = tavily.search(query=topic, search_depth="advanced", max_results=5)
        
        # Format the results for the AI to read
        context = []
        for result in response['results']:
            context.append(f"Source: {result['title']}\nURL: {result['url']}\nContent: {result['content']}")
        
        return "\n\n".join(context)
    except Exception as e:
        return f"Search Error: {e}"

def generate_summary(query, raw_data, google_key):
    """The Brain (Gemini) reads the data and writes the report"""
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

query = st.text_input("Research Topic", placeholder="e.g., Current price of 50kg Dangote Cement in Accra")

if st.button("🚀 Run Analysis", type="primary"):
    if not google_api_key or not tavily_api_key:
        st.error("⚠️ Please enter BOTH API Keys in the sidebar!")
    else:
        # Create columns for layout
        col1, col2 = st.columns([1, 1])
        
        # STATUS: SEARCHING
        with st.status("🕵️ Agent is working...", expanded=True) as status:
            st.write("Connecting to Tavily API...")
            raw_data = search_web(query, tavily_api_key)
            st.write("Reading search results...")
            
            st.write("Synthesizing report with Gemini...")
            final_report = generate_summary(query, raw_data, google_api_key)
            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

        # OUTPUT
        st.markdown("---")
        st.subheader("📄 Executive Summary")
        st.markdown(final_report)
        
        with st.expander("🔍 View Raw Data (Proof)"):
            st.text(raw_data)