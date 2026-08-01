import time
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.interview_evaluator import evaluate_interview
from utils.evaluate import evaluate_answer
from utils.interview import generate_interview_questions
from utils.tables import create_comparison_table
from utils.charts import ats_pie_chart, ats_bar_chart
from utils.jd_match import match_resume_with_jd
from utils.jd_loader import load_jd_from_pdf
from utils.extract_score import extract_score
from utils.resume_compare import compare_resumes
from utils.resume_tools import analyze_uploaded_resumes
from utils.ats import analyze_resume
from utils.embeddings import create_embeddings
from utils.vector_store import VectorStore
from utils.chunking import create_chunks
from utils.pdf_loader import load_pdf
from utils.rag_pipeline import ask_question
from database.database import init_db, save_chat, get_history

import io

@st.cache_resource
def build_vector_store(pdf_bytes, document_name):

    # Convert bytes back into a file-like object
    pdf_file = io.BytesIO(pdf_bytes)

    # Load PDF
    pages = load_pdf(pdf_file)

    # Create chunks
    chunks = create_chunks(pages)
    for chunk in chunks:
        chunk["document"] = document_name

    print("Pages:", len(pages))
    print("Chunks:", len(chunks))

    if len(chunks) == 0:
        raise ValueError("No chunks were created from the PDF.")

    print("Total chunks:", len(chunks))

    if len(chunks) == 0:
        st.error("No chunks created.")
        st.stop()

    # Create embeddings
    embeddings = create_embeddings(chunks)
    print("Embeddings:", type(embeddings))

    if embeddings is None:
        st.error("Embeddings are None")
        st.stop()

    print("Embedding shape:", embeddings.shape)
    # Build vector store
    store = VectorStore()
    store.build_index(embeddings, chunks)

init_db()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ats_reports" not in st.session_state:
    st.session_state.ats_reports = {}

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

if "jd_reports" not in st.session_state:
    st.session_state.jd_reports = {}

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "final_feedback" not in st.session_state:
    st.session_state.final_feedback = ""

if "interview_completed" not in st.session_state:
    st.session_state.interview_completed = False

st.set_page_config(
    page_title="AI Recruitment Assistant",
    page_icon="🤖",
    layout="wide"
)

with st.sidebar:

    st.title("📚 Research Agent")

    st.markdown("---")

    st.write("### Model")
    st.info("Llama 3.3 70B (Groq)")

    st.write("### Embedding")
    st.info("all-MiniLM-L6-v2")

    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []
        st.session_state.ats_reports = {}

        st.session_state.uploader_key += 1

        st.cache_resource.clear()

        st.session_state.messages = []

        st.rerun()

st.title("🤖 AI Recruitment Assistant")

st.markdown("""
Ask questions about your uploaded PDF using **Retrieval-Augmented Generation (RAG)**.

### Features
- 📄 Multi Resume Upload
- 📊 ATS Resume Analysis
- 📈 Resume Comparison
- 🎯 Job Description Match
- 💬 AI Resume Chat
- 🤖 Groq Llama 3.3
- 🔍 Semantic Search
""")

uploaded_files = st.file_uploader(
    "Choose PDF(s)",
    type=["pdf"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

if not uploaded_files:
    st.info("📄 Please upload PDF(s).")
    st.stop()

from utils.pdf_processor import process_documents

store, chunks = process_documents(uploaded_files)

embeddings = create_embeddings(chunks)

store = VectorStore()
store.build_index(embeddings, chunks)

resume_files = uploaded_files

if resume_files:
    suggested_questions = [
        "Summarize my resume",
        "Generate interview questions",
        "What are my strengths?",
        "What skills are mentioned?",
        "Suggest projects to practice"
    ]
else:
    suggested_questions = [
        "Summarize this document",
        "Explain the key concepts",
        "List the important points",
        "Generate quiz questions",
        "What is the conclusion?"
    ]

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Suggested Questions")

for q in suggested_questions:
    st.sidebar.write(f"• {q}")

st.sidebar.markdown("---")
st.sidebar.write("### Document Statistics")

st.sidebar.metric("Documents", len(uploaded_files))
st.sidebar.metric("Chunks", len(chunks))
st.sidebar.metric(
    "Pages",
    len(set(chunk["page"] for chunk in chunks))
)

st.success(
    f"✅ PDF processed successfully! "
    f"{len(chunks)} chunks created and indexed."
)

if resume_files:

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Resume Tools")

    if st.sidebar.button("📊 ATS Resume Analysis"):

        with st.spinner("Analyzing Resume(s)..."):
            st.session_state.ats_reports = analyze_uploaded_resumes(
                resume_files
            )
            scores = []

            for name, report in st.session_state.ats_reports.items():

                score = extract_score(report)

                scores.append({
                    "Resume": name,
                    "Score": score
                })

            st.subheader("📋 Resume Comparison Table")

            df = pd.DataFrame(scores)

            st.dataframe(
                df.sort_values(
                    by="Score",
                    ascending=False
                ),
                use_container_width=True
            )

            fig = px.pie(
                df,
                names="Resume",
                values="Score",
                title="ATS Score Comparison"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            fig = px.bar(
                df.sort_values("Score"),
                x="Resume",
                y="Score",
                text="Score",
                title="ATS Score Comparison"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            best_resume = df.loc[df["Score"].idxmax()]

            st.success(
                f"🏆 Best Resume: {best_resume['Resume']}\n\n"
                f"ATS Score: {best_resume['Score']}/100"
            )

            st.info(
                f"📈 Average ATS Score: {df['Score'].mean():.1f}/100"
            )

            st.subheader("🥇 Resume Ranking")

            ranking = df.sort_values(
                by="Score",
                ascending=False
            )

            for i, row in ranking.iterrows():

                st.write(
                    f"{len(ranking[ranking['Score'] >= row['Score']])}. "
                    f"{row['Resume']} — {row['Score']}/100"
                )
    st.sidebar.markdown("---")
    st.sidebar.subheader("💼 Job Description")
    
    jd_option = st.sidebar.radio(
        "Choose Input Method",
        ["Upload PDF", "Paste Text"]
    )
    
    jd_description = ""
    
    if jd_option == "Upload PDF":
    
        jd_pdf = st.sidebar.file_uploader(
            "Upload JD PDF",
            type=["pdf"],
            key="jd_pdf"
        )
    
        if jd_pdf:
    
            pdf = io.BytesIO(jd_pdf.getvalue())
    
            pages = load_pdf(pdf)
    
            jd_description = "\n\n".join(
                page["content"]
                for page in pages
            )
    
    else:
    
        jd_description = st.sidebar.text_area(
            "Paste Job Description",
            height=250,
            placeholder="Paste Job Description here..."
        )
    
    if jd_description:
    
        st.session_state.jd_text = jd_description
    
        st.sidebar.success("✅ Job Description Loaded")
    
        if st.sidebar.button("🎯 Match Resume with JD"):
    
            if not st.session_state.jd_text:
    
                st.warning("Please upload or paste a Job Description.")
    
            else:
    
                st.session_state.jd_reports = {}
    
                for resume in resume_files:
    
                    pdf = io.BytesIO(resume.getvalue())
    
                    pages = load_pdf(pdf)
    
                    chunks = create_chunks(pages)
    
                    resume_text = "\n\n".join(
                        chunk["content"]
                        for chunk in chunks
                    )
    
                    with st.spinner(f"Matching {resume.name}..."):
    
                        report = match_resume_with_jd(
                            resume_text,
                            st.session_state.jd_text
                        )
    
                    st.session_state.jd_reports[
                        resume.name
                    ] = report

st.sidebar.markdown("---")
st.sidebar.subheader("📋 AI Mock Interview")

candidate_name = st.sidebar.text_input(
    "👤 Candidate Name"
)

st.session_state.candidate_name = candidate_name

if len(resume_files) == 0:
    st.error("Please upload a resume first.")
    st.stop()

job_role = st.sidebar.selectbox(
    "💼 Select Job Role",
    [
        "Python AI Engineer",
        "Python Developer",
        "Machine Learning Engineer",
        "Data Scientist",
        "AI Engineer"
    ]
)

st.session_state.job_role = job_role

if st.sidebar.button("📝 Start Mock Interview"):

    if not st.session_state.candidate_name.strip():
        st.sidebar.error("Please enter your name.")
        st.stop()

    pdf = io.BytesIO(resume_files[0].getvalue())
    pages = load_pdf(pdf)
    chunks = create_chunks(pages)

    resume_text = "\n\n".join(
        chunk["content"]
        for chunk in chunks
    )

    with st.spinner("Generating Interview Questions..."):

        questions = generate_interview_questions(
            resume_text,
            10
        )

    question_list = [
        q.strip()
        for q in questions.split("\n")
        if q.strip()
    ]

    st.session_state.questions = question_list
    st.session_state.answers = [""] * len(questions)
    st.session_state.current_question = 0
    st.session_state.show_instructions = True
    st.session_state.start_time = time.time()
    st.session_state.interview_duration = 15 * 60 


    st.rerun()  
# Show interview completion page
if st.session_state.interview_completed:

    st.success("🎉 Interview Completed Successfully!")

    st.title("✅ Interview Completed")

    st.balloons()

    st.markdown("### 📊 Final Interview Evaluation")

    st.divider()

    st.markdown(st.session_state.final_feedback)

    feedback = st.session_state.final_feedback.upper()

    st.divider()

    if "HIRING RECOMMENDATION: HIRE" in feedback:

        st.success("""
    ## ✅ HIRING RECOMMENDATION

    ### HIRE

    The candidate has demonstrated strong technical knowledge,
    good communication, and problem-solving ability.
    """)

    elif "HIRING RECOMMENDATION: CONSIDER" in feedback:

        st.warning("""
    ## 🟡 HIRING RECOMMENDATION

    ### CONSIDER

    The candidate shows potential but needs improvement in
    some technical areas.
    """)

    elif "HIRING RECOMMENDATION: REJECT" in feedback:

        st.error("""
    ## ❌ HIRING RECOMMENDATION

    ### REJECT

    The candidate currently does not meet the required
    technical expectations for this role.
    """)

    if st.button("🔄 Start New Interview"):
        st.session_state.interview_completed = False
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.current_question = 0
        st.session_state.final_feedback = ""

        if "start_time" in st.session_state:
            del st.session_state.start_time

        if "interview_duration" in st.session_state:
            del st.session_state.interview_duration

        st.rerun()

    st.stop()

if (
    "questions" in st.session_state
    and len(st.session_state.questions) > 0
):

    if (
        "start_time" in st.session_state
        and not st.session_state.interview_completed
    ):

        current = st.session_state.current_question
        total = len(st.session_state.questions)

    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Candidate Dashboard")

    st.sidebar.info(
        f"""
    **👤 Candidate:** {st.session_state.candidate_name}

    **💼 Position:** {st.session_state.job_role}

    **📄 Questions:** {total}
    """
    )

    remaining = (
        st.session_state.interview_duration
        - (time.time() - st.session_state.start_time)
    )

    remaining = max(0, int(remaining))

    mins = remaining // 60
    secs = remaining % 60

    st.sidebar.metric(
        "⏳ Time Remaining",
        f"{mins:02d}:{secs:02d}"
    )
    answered = len(
        [a for a in st.session_state.answers if a.strip()]
    )

    st.sidebar.metric("✅ Answered", answered)

    st.sidebar.metric(
        "📝 Remaining",
        total - answered
    )
    if remaining <= 0:

        interview_text = ""

        for q, a in zip(
            st.session_state.questions,
            st.session_state.answers
        ):

            interview_text += f"""
Question:
{q}

Answer:
{a}

"""

        with st.spinner("⏳ Time's Up! Submitting Interview..."):
            st.session_state.final_feedback = evaluate_interview(interview_text)

        st.session_state.interview_completed = True
        st.rerun()

    if current < total:

        st.progress((current + 1) / total)

        st.info(
            f"""
    ### 💬 Interview Question {current + 1} of {total}

    {st.session_state.questions[current]}
    """
        )

        answer = st.text_area(
            "✍️ Your Answer",
            value=(
                st.session_state.answers[current]
                if current < len(st.session_state.answers)
                else ""
            ),
            height=180,
            placeholder="Type your answer here...",
            key=f"answer_{current}"
        )

        st.session_state.answers[current] = answer

        col1, col2 = st.columns(2)

        with col1:

            if current > 0:

                if st.button("⬅ Previous", key=f"prev_{current}"):

                    st.session_state.current_question -= 1
                    st.rerun()

        with col2:

            if current < total - 1:

                if st.button("Next ➡", key=f"next_{current}"):

                    st.session_state.current_question += 1
                    st.rerun()

        if st.session_state.current_question == len(st.session_state.questions) - 1:

            st.divider()

            if st.button("✅ Finish Interview"):

                interview_text = ""

                for q, a in zip(
                    st.session_state.questions,
                    st.session_state.answers
                ):

                    interview_text += f"""
            Question:
            {q}

            Answer:
            {a}

            """

                with st.spinner("Evaluating Interview..."):
                    st.session_state.final_feedback = evaluate_interview(interview_text)

                st.session_state.interview_completed = True

                st.rerun()

    else:

        st.success("🎉 Interview Completed!")
                

if st.sidebar.button("📈 Compare Resumes"):

    with st.spinner("Comparing resumes..."):

        comparison = compare_resumes(resume_files)

    st.divider()
    st.subheader("📈 Resume Comparison")

    for item in comparison:

        with st.expander(f"📄 {item['Resume']}", expanded=False):

            st.markdown(item["Report"])

if st.session_state.jd_reports:
                
    st.divider()
    
    st.header("🎯 Job Description Match")
    
    for name, report in st.session_state.jd_reports.items():
    
        with st.expander(name, expanded=True):
    
            st.markdown(report)

if st.session_state.jd_text:

    st.subheader("📄 Job Description Preview")

    st.text_area(
        "",
        st.session_state.jd_text,
        height=250,
        disabled=True
    )

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a question about the document...")

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.spinner("Searching document..."):

        start_time = time.time()

        try:
            answer, pages, results = ask_question(
                 question,
                store
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.stop()

        end_time = time.time()

    total_time = end_time - start_time

    st.subheader("📖 Sources")

    st.subheader("📖 Retrieved Context")
    st.info(f"Retrieved {len(results)} relevant document chunks.")

    for i, item in enumerate(results, start=1):

        with st.expander(
            f"Source {i} | {item['document']} | Page {item['page']}"
        ):

            st.write(item["content"])

    documents = sorted(
        set(item["document"] for item in results)
    )

    document_names = ", ".join(documents)

    st.subheader("📖 Sources")

    for item in results:

        with st.expander(f"Page {item['page']}"):

            st.write(item["content"])

    citation = ", ".join(map(str, pages))

    save_chat(question, answer, citation)

    sources = []

    for item in results:
        source = f"{item['document']} (Page {item['page']})"
        if source not in sources:
            sources.append(source)

    assistant_response = f"""{answer}

    📄 **Documents**
    {document_names}

    📖 **Sources**
    """ + "\n".join(
            f"• {s}" for s in sources
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_response
        }
    )

    with st.chat_message("assistant"):
        st.markdown(assistant_response)
        st.divider()

        st.subheader("⚡ Performance")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Response Time", f"{total_time:.2f} sec")

        with col2:
            st.metric("Chunks Retrieved", len(results))
            st.metric("Source Pages", len(set(pages)))

        st.download_button(
            label="📥 Download Answer",
            data=assistant_response,
            file_name="research_answer.txt",
            mime="text/plain"
        )

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#808080; font-size:14px; padding:15px;">
        <h4>🤖 AI Recruitment Assistant</h4>
        <p>Powered by <b>Streamlit • Groq • Llama 3.3 • FAISS • Sentence Transformers</b></p>
        <p>© 2026 All Rights Reserved</p>
    </div>
    """,
    unsafe_allow_html=True
)