import streamlit as st
import sys
import time

sys.path.insert(0, "/Users/I578397/Desktop/OSS/flowmcp/python")

from flowmcp import RAG, Pipeline
from flowmcp.llm.base import LLMBase
from flowmcp.rag.chunker import chunk_text

# ── Smart Demo LLM — builds a real answer from retrieved chunks ─
class DemoLLM(LLMBase):
    def complete(self, prompt: str) -> str:
        # Parse question and context chunks out of the prompt
        question = ""
        chunks = []
        in_context = False

        for line in prompt.strip().split("\n"):
            if line.startswith("Question:"):
                question = line.replace("Question:", "").strip()
                in_context = False
            elif "Context from documents:" in line:
                in_context = True
            elif in_context and line.strip():
                chunks.append(line.strip())

        if not chunks:
            return (
                f"I could not find any relevant information in the knowledge base "
                f"to answer: **{question}**\n\n"
                f"Try adding more documents in the sidebar, or rephrase your question."
            )

        q_lower = question.lower()

        # Find the single most specific chunk by avoiding the generic intro
        def score(chunk):
            c = chunk.lower()
            score = 0
            for word in q_lower.split():
                if len(word) > 3 and word in c:
                    score += 2
            if "flowmcp is a simple" in c:   # penalise the generic opener
                score -= 3
            return score

        ranked = sorted(chunks, key=score, reverse=True)
        best = ranked[0]

        # Build a direct, question-aware answer
        if any(w in q_lower for w in ["what is", "what are", "explain", "define", "mean"]):
            answer = f"{best}"
        elif any(w in q_lower for w in ["how", "install", "run", "use", "load", "set up"]):
            answer = f"Here is how: {best}"
        elif any(w in q_lower for w in ["does", "can", "support", "work", "available"]):
            answer = f"Yes — {best}"
        elif any(w in q_lower for w in ["who", "which", "where"]):
            answer = f"{best}"
        else:
            answer = f"{best}"

        # Append additional context if there are more chunks
        extra = [c for c in ranked[1:] if c != best]
        additional = ""
        if extra:
            additional = "\n\n**Additional context:**\n" + "\n".join(f"- {c}" for c in extra[:2])

        return (
            f"**{answer}**"
            f"{additional}\n\n"
            f"---\n"
            f"*🔍 RAG retrieved {len(chunks)} chunk(s) from the knowledge base and passed them to the LLM. "
            f"In production replace DemoLLM with `openai/gpt-4` or `ollama/llama3` for real AI answers.*"
        )

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="flowmcp Demo",
    page_icon="⚡",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────
st.title("⚡ flowmcp")
st.markdown("**Simple RAG + MCP + LLM pipeline framework** — a clean alternative to LangChain")
st.markdown("---")

# ── Sidebar — configuration ───────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("LLM Provider")
    provider = st.selectbox(
        "Select provider",
        ["Demo (no API key needed)", "openai/gpt-4", "anthropic/claude-3-5-sonnet", "ollama/llama3"],
    )

    st.subheader("Knowledge Base")
    st.markdown("Add documents for RAG to search through:")
    default_docs = [
        "flowmcp supports four LLM providers: OpenAI (gpt-4, gpt-3.5), Anthropic (claude-3-5-sonnet), Ollama (llama3, mistral, phi3), and Gemini (gemini-pro).",
        "RAG stands for Retrieval-Augmented Generation. It splits documents into chunks, indexes them, and retrieves the most relevant chunks before sending to the LLM.",
        "MCP stands for Model Context Protocol — Anthropic's open standard for connecting AI models to external tools like filesystems, GitHub, databases, and APIs.",
        "flowmcp works in both Python and Java. The Python SDK uses pip install flowmcp. The Java SDK uses Maven with groupId io.flowmcp.",
        "To load documents: pass a folder path, a file path, or a plain text string to the RAG class. Supported formats are .txt, .md, and .pdf.",
        "To install flowmcp with OpenAI support run: pip install flowmcp[openai]. For Anthropic: pip install flowmcp[anthropic]. For Gemini: pip install flowmcp[gemini].",
        "Ollama runs LLMs locally on your machine for free with no API key needed. Install from ollama.com, pull a model with ollama pull llama3, then use llm=ollama/llama3.",
        "The Pipeline class is the main entry point in flowmcp. Initialise it with llm, docs, and tools parameters to configure your providers.",
        "Pipeline.ask() runs in three steps: first RAG retrieves relevant document chunks, then MCP executes any connected tools, then the LLM generates a final answer from the combined context.",
    ]
    doc_text = st.text_area(
        "Documents (one per line)",
        value="\n".join(default_docs),
        height=220,
    )

    st.markdown("---")
    st.markdown("**Links**")
    st.markdown("[GitHub Repo](https://github.com/SreejaPasula/flowmcp)")
    st.markdown("[Open Issues](https://github.com/SreejaPasula/flowmcp/issues)")
    st.markdown("[Contributing Guide](https://github.com/SreejaPasula/flowmcp/blob/main/CONTRIBUTING.md)")

# ── Build pipeline from sidebar config ────────────────────────
docs = [d.strip() for d in doc_text.strip().split("\n") if d.strip()]

@st.cache_resource(show_spinner=False)
def build_rag(doc_hash):
    return RAG(docs)

rag = build_rag(hash(doc_text))

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask a Question", "🔍 RAG Explorer", "🏗️ How It Works", "📋 Open Issues"])

# ── Tab 1: Ask a question ─────────────────────────────────────
with tab1:
    st.subheader("Ask anything about your documents")

    examples = [
        "What LLM providers does flowmcp support?",
        "What is RAG and how does it work?",
        "Does flowmcp work in Java?",
        "How do I load documents?",
        "What is MCP?",
    ]
    selected = st.selectbox("Try an example question:", ["— pick one —"] + examples)

    user_q = st.text_input(
        "Or type your own question:",
        value=selected if selected != "— pick one —" else "",
        placeholder="e.g. What is flowmcp?",
    )

    if st.button("Ask ⚡", type="primary") and user_q:
        with st.spinner("Retrieving relevant chunks and generating answer..."):
            time.sleep(0.4)

            # Show retrieved chunks
            chunks = rag.retrieve(user_q, top_k=3)
            st.markdown("**RAG — Retrieved chunks:**")
            for i, chunk in enumerate(chunks, 1):
                st.info(f"**Chunk {i}:** {chunk}")

            # Generate answer
            pipeline = Pipeline(llm=DemoLLM(), docs=docs)
            answer = pipeline.ask(user_q)

            st.markdown("**Answer:**")
            st.success(answer)

# ── Tab 2: RAG Explorer ───────────────────────────────────────
with tab2:
    st.subheader("See what RAG retrieves for any query")
    st.markdown("Type a query below and see which document chunks RAG scores as most relevant.")

    rag_q = st.text_input("Query:", placeholder="e.g. how to load documents")
    top_k = st.slider("Number of chunks to retrieve (top-K):", 1, 5, 3)

    if rag_q:
        results = rag.retrieve(rag_q, top_k=top_k)
        st.markdown(f"**Top {len(results)} chunk(s) retrieved for:** `{rag_q}`")
        for i, chunk in enumerate(results, 1):
            st.markdown(f"**{i}.** {chunk}")

    st.markdown("---")
    st.subheader("Document Chunks in the Knowledge Base")
    st.markdown(f"Total documents loaded: **{len(docs)}**")
    for i, doc in enumerate(docs, 1):
        st.markdown(f"**{i}.** {doc}")

# ── Tab 3: How it works ───────────────────────────────────────
with tab3:
    st.subheader("flowmcp Architecture")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Python — 5 lines")
        st.code("""
from flowmcp import Pipeline

pipeline = Pipeline(
    llm="openai/gpt-4",
    docs="./my-docs",
    tools=["filesystem"]
)
answer = pipeline.ask("What is our refund policy?")
print(answer)
        """, language="python")

        st.markdown("### How pipeline.ask() works")
        st.markdown("""
1. **RAG** searches your documents for the most relevant chunks
2. **MCP** runs any connected tools (filesystem, GitHub, etc.)
3. **Prompt** is built from the question + retrieved chunks + tool results
4. **LLM** receives the prompt and generates the answer
        """)

    with col2:
        st.markdown("### Supported LLM Providers")
        providers_data = {
            "Provider": ["OpenAI", "Anthropic", "Ollama", "Gemini"],
            "Example model": ["gpt-4", "claude-3-5-sonnet", "llama3", "gemini-pro"],
            "API key needed": ["Yes", "Yes", "No (local)", "Yes"],
        }
        st.table(providers_data)

        st.markdown("### Install")
        st.code("""
pip install flowmcp
pip install flowmcp[openai]     # OpenAI
pip install flowmcp[anthropic]  # Anthropic
pip install flowmcp[gemini]     # Gemini
        """, language="bash")

# ── Tab 4: Open Issues ────────────────────────────────────────
with tab4:
    st.subheader("Open Issues — Contribute to flowmcp")
    st.markdown("These are real open issues on the GitHub repo. Pick one and send a PR!")

    issues = [
        {"#": 1,  "Type": "🟢 Good First Issue", "Title": "Add Gemini provider for Python",                    "Skill": "Python"},
        {"#": 2,  "Type": "🟢 Good First Issue", "Title": "Implement OpenAI client for Java",                  "Skill": "Java"},
        {"#": 3,  "Type": "🟢 Good First Issue", "Title": "Implement Anthropic client for Java",               "Skill": "Java"},
        {"#": 4,  "Type": "🟢 Good First Issue", "Title": "Add PDF support to RAG loader",                     "Skill": "Python"},
        {"#": 5,  "Type": "🟢 Good First Issue", "Title": "Add embedding-based retrieval",                     "Skill": "Python"},
        {"#": 6,  "Type": "🟢 Good First Issue", "Title": "Add streaming support to Python Pipeline",          "Skill": "Python"},
        {"#": 7,  "Type": "🔴 Bug",              "Title": "Retriever fails silently on punctuation",           "Skill": "Python"},
        {"#": 8,  "Type": "🔴 Bug",              "Title": "OllamaClient JSON parsing breaks on complex output","Skill": "Java"},
        {"#": 9,  "Type": "🔴 Bug",              "Title": "No error when docs path does not exist",            "Skill": "Python"},
        {"#": 10, "Type": "🔵 Enhancement",      "Title": "Add multi-turn conversation / chat history",        "Skill": "Python"},
        {"#": 11, "Type": "🔵 Enhancement",      "Title": "Load documents from a URL",                        "Skill": "Python"},
        {"#": 12, "Type": "🔵 Enhancement",      "Title": "Add async support to Python Pipeline",             "Skill": "Python"},
        {"#": 13, "Type": "🔵 Enhancement",      "Title": "Add CLI — run flowmcp from the terminal",          "Skill": "Python"},
    ]

    filter_type = st.selectbox("Filter by type:", ["All", "🟢 Good First Issue", "🔴 Bug", "🔵 Enhancement"])
    filter_skill = st.selectbox("Filter by skill:", ["All", "Python", "Java"])

    filtered = issues
    if filter_type != "All":
        filtered = [i for i in filtered if i["Type"] == filter_type]
    if filter_skill != "All":
        filtered = [i for i in filtered if i["Skill"] == filter_skill]

    st.markdown(f"**Showing {len(filtered)} issue(s)**")
    for issue in filtered:
        col_num, col_type, col_title, col_skill = st.columns([1, 3, 7, 2])
        col_num.markdown(f"**#{issue['#']}**")
        col_type.markdown(issue["Type"])
        col_title.markdown(f"[{issue['Title']}](https://github.com/SreejaPasula/flowmcp/issues/{issue['#']})")
        col_skill.markdown(f"`{issue['Skill']}`")

    st.markdown("---")
    st.markdown("**How to contribute:**")
    st.code("""
# 1. Fork the repo
git clone https://github.com/SreejaPasula/flowmcp

# 2. Create a branch
git checkout -b fix/issue-7-punctuation

# 3. Make your change, add tests, then commit with sign-off
git commit -s -m "fix: handle punctuation in RAG retriever"

# 4. Open a PR — the review bot runs automatically
    """, language="bash")
