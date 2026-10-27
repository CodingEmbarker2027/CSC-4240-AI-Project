import streamlit as st


def main():
    pages = [
        st.Page("pages/resume_matcher.py", title="Resume Matcher"),
        st.Page("pages/ai_analytics.py", title="AI/NLP Analytics"),
        st.Page("pages/model_evaluation.py", title="Model Evaluations"),
    ]

    st.navigation(pages).run()


if __name__ == "__main__":
    main()