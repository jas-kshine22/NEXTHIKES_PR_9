import streamlit as st
from groq import Groq
from newsapi import NewsApiClient

# ---------------------------
# CONFIGURATION
# ---------------------------

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# ---------------------------
# FUNCTIONS
# ---------------------------

def get_news_articles(query):
    articles = newsapi.get_everything(
        q=query,
        language='en',
        sort_by='relevancy',
        page_size=5
    )
    return articles["articles"]

def summarize_articles(articles):
    summaries = []
    for article in articles:
        title = article["title"]
        description = article["description"]

        if description:
            summaries.append(f"Title: {title}\nSummary: {description}\n")

    return "\n".join(summaries)

def generate_report(query, combined_summaries, output_type):

    if output_type == "Detailed":
        style_instruction = "Write a detailed structured equity research report."
    else:
        style_instruction = "Write a concise structured summary."

    prompt = f"""
    You are an Equity Research Analyst.

    Based on the following news summaries:

    {combined_summaries}

    {style_instruction}

    Topic: {query}

    Structure output with:
    1. Key Highlights
    2. Revenue & Earnings
    3. Market Trends
    4. Risks
    5. Future Outlook
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

# ---------------------------
# UI DESIGN
# ---------------------------

st.set_page_config(page_title="AI Equity Research Dashboard", layout="wide")

st.title("📊 AI-Powered Equity Research Dashboard")
st.markdown("Generate structured research reports from live news data.")

col1, col2 = st.columns(2)

with col1:
    query = st.text_input("Enter Topic", placeholder="AI companies earnings")
    output_type = st.selectbox("Select Report Type", ["Summary", "Detailed"])

with col2:
    language = st.selectbox("Select Output Language", ["English", "Hindi", "French", "German"])

if st.button("Generate Report"):

    with st.spinner("Fetching news and generating report..."):

        articles = get_news_articles(query)
        combined_summaries = summarize_articles(articles)
        report = generate_report(query, combined_summaries, output_type)

        if language != "English":
            translate_prompt = f"Translate the following text into {language}:\n\n{report}"

            translation = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": translate_prompt}],
                temperature=0
            )

            report = translation.choices[0].message.content

    st.success("Report Generated Successfully!")

    st.markdown("### 📄 Generated Report")
    st.write(report)

    st.download_button(
        label="Download Report",
        data=report,
        file_name="equity_research_report.txt",
        mime="text/plain"
    )
