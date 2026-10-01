import streamlit as st
import llm
from reader import load_repo

st.set_page_config(page_title="ProjectDefender", page_icon="🛡️", layout="wide")

st.title("🛡️ ProjectDefender")
st.caption("Defend your codebase before an interviewer interrogates you on it.")

if "repo_data" not in st.session_state:
    st.session_state.repo_data = None
if "questions" not in st.session_state:
    st.session_state.questions = []
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = {}


def parse_and_validate_questions(raw_text, valid_paths):
    valid_questions = []
    for line in raw_text.splitlines():
        line = line.strip()
        if "FILE:" in line and "| QUESTION:" in line:
            try:
                parts = line.split("| QUESTION:")
                file_part = parts[0].replace("FILE:", "").strip().strip("`*")
                question_part = parts[1].strip()
                if file_part in valid_paths and question_part:
                    valid_questions.append({"file": file_part, "question": question_part})
            except Exception:
                continue
    return valid_questions


def generate_questions(repo_name, readme, files):
    valid_paths = {path for path, _ in files}

    files_summary = "\n\n".join(
        [f"--- Path: {path} ---\n{content[:2500]}" for path, content in files]
    )
    user_prompt = (
        f"Repository: {repo_name}\n\n"
        f"README:\n{readme[:2000]}\n\n"
        f"Available Files:\n{files_summary}\n\n"
        "Generate exactly 5 hard technical interview questions about design choices, trade-offs, "
        "scalability bottlenecks, edge cases, bugs, or 'what if X breaks'.\n"
        "Format strict requirement: Each question must be on its own line exactly formatted as:\n"
        "FILE: <exact_relative_path> | QUESTION: <question text>\n"
        "Only cite files that exist in the list above."
    )
    system_prompt = (
        "You are a rigorous technical interviewer interrogating a placement candidate about their own codebase. "
        "Strictly adhere to the requested output format."
    )

    raw_response = llm.ask(system_prompt, user_prompt)
    questions = parse_and_validate_questions(raw_response, valid_paths)

    if len(questions) < 3:
        retry_prompt = (
            user_prompt
            + "\n\nCRITICAL: Ensure the FILE matches the exact file paths provided above."
        )
        raw_response = llm.ask(system_prompt, retry_prompt)
        questions = parse_and_validate_questions(raw_response, valid_paths)

    return questions


repo_url = st.text_input("Enter GitHub Repository URL:", placeholder="https://github.com/owner/repo")
if st.button("Analyze repo", type="primary"):
    if not repo_url.strip():
        st.warning("Please enter a valid GitHub repository URL.")
    else:
        with st.spinner("Cloning and parsing repository..."):
            try:
                repo_data = load_repo(repo_url.strip())
                st.session_state.repo_data = repo_data
                st.session_state.feedbacks = {}
            except Exception as e:
                st.error(f"Failed to load repository: {e}")
                st.session_state.repo_data = None

        if st.session_state.repo_data:
            with st.spinner("Generating targeted interview questions..."):
                questions = generate_questions(
                    st.session_state.repo_data["name"],
                    st.session_state.repo_data.get("readme", ""),
                    st.session_state.repo_data.get("files", []),
                )
                st.session_state.questions = questions
                if not questions:
                    st.error("No valid questions generated. Check your API key and model settings, then try again.")

if st.session_state.repo_data:
    repo = st.session_state.repo_data
    with st.expander(f"📁 Loaded Files ({len(repo.get('files', []))} total)", expanded=False):
        for path, _ in repo.get("files", []):
            st.code(path, language="text")

if st.session_state.questions:
    st.subheader(f"Interview Questions ({len(st.session_state.questions)})")
    file_map = dict(st.session_state.repo_data.get("files", []))

    for idx, item in enumerate(st.session_state.questions):
        file_path = item["file"]
        question_text = item["question"]

        with st.container(border=True):
            st.markdown(f"**Q{idx + 1}:** {question_text}")
            st.caption(f"Target file: `{file_path}`")

            answer = st.text_area(
                "Your Answer:",
                key=f"ans_{idx}",
                placeholder="Explain the reasoning, trade-offs, or error handling...",
            )

            if st.button("Get feedback", key=f"btn_{idx}"):
                if not answer.strip():
                    st.warning("Please provide an answer before asking for feedback.")
                else:
                    file_content = file_map.get(file_path, "")
                    system_eval = (
                        "You are a technical interviewer reviewing a student's answer about their project. "
                        "Evaluate their response based on the provided code snippet. "
                        "Format your evaluation into three distinct sections:\n"
                        "(a) What the answer got right\n"
                        "(b) What was missed\n"
                        "(c) One follow-up question\n"
                        "Do not include any numeric score or grade."
                    )
                    user_eval = (
                        f"File Context ({file_path}):\n{file_content[:3000]}\n\n"
                        f"Question Asked: {question_text}\n\n"
                        f"Candidate's Answer:\n{answer}\n"
                    )

                    with st.spinner("Evaluating response..."):
                        feedback = llm.ask(system_eval, user_eval)
                        st.session_state.feedbacks[idx] = feedback

            if idx in st.session_state.feedbacks:
                st.info(st.session_state.feedbacks[idx])