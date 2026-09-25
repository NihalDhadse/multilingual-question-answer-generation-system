import streamlit as st
import tempfile
from pathlib import Path
import time

from src.document_reader import extract_text
from src.text_processor import (
    clean_text,
    chunk_text,
    remove_duplicate_questions
)
from src.qna_generator import generate_qna
from src.validator import validate_qna
from src.translator import translate_qna
from src.excel_generator import create_excel


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Multilingual QnA Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(99, 102, 241, 0.18),
                transparent 25%
            ),
            radial-gradient(
                circle at 90% 15%,
                rgba(168, 85, 247, 0.16),
                transparent 25%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(14, 165, 233, 0.12),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #070b18 0%,
                #0b1020 45%,
                #111827 100%
            );

        color: #f8fafc;
        min-height: 100vh;
    }


    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* ======================================================
       HERO
       ====================================================== */

    .hero {
        text-align: center;
        padding: 2.5rem 1rem 2rem 1rem;
        margin-bottom: 1.5rem;
    }

    .hero-badge {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 999px;

        background: rgba(99, 102, 241, 0.14);
        border: 1px solid rgba(129, 140, 248, 0.35);

        color: #c7d2fe;

        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;

        box-shadow:
            0 0 25px rgba(99, 102, 241, 0.15);
    }

    .hero-title {
        margin-top: 18px;

        font-size: clamp(2.2rem, 5vw, 4.8rem);
        line-height: 1.05;

        font-weight: 800;

        background:
            linear-gradient(
                90deg,
                #60a5fa,
                #a78bfa,
                #f472b6,
                #22d3ee,
                #60a5fa
            );

        background-size: 300% auto;

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        animation: gradientFlow 7s linear infinite;
    }

    @keyframes gradientFlow {
        0% {
            background-position: 0% center;
        }

        50% {
            background-position: 100% center;
        }

        100% {
            background-position: 0% center;
        }
    }

    .hero-subtitle {
        max-width: 780px;
        margin: 18px auto 0 auto;

        color: #a5b4fc;

        font-size: 1.05rem;
        line-height: 1.7;
    }


    /* ======================================================
       GLASS CARD
       ====================================================== */

    .glass-card {
        padding: 25px;

        border-radius: 22px;

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.075),
                rgba(255,255,255,0.025)
            );

        border: 1px solid rgba(255,255,255,0.09);

        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);

        box-shadow:
            0 20px 60px rgba(0,0,0,0.25);
    }


    /* ======================================================
       SECTION TITLES
       ====================================================== */

    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 6px;
    }

    .section-description {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-bottom: 18px;
        line-height: 1.6;
    }


    /* ======================================================
       FILE UPLOADER
       ====================================================== */

    [data-testid="stFileUploader"] {
        background:
            linear-gradient(
                135deg,
                rgba(59,130,246,0.08),
                rgba(139,92,246,0.08)
            );

        border: 2px dashed rgba(129,140,248,0.35);

        border-radius: 20px;

        padding: 10px;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        width: 100%;

        border: none;
        border-radius: 14px;

        padding: 0.75rem 1.2rem;

        font-weight: 700;
        color: white;

        background:
            linear-gradient(
                135deg,
                #4f46e5,
                #7c3aed,
                #9333ea
            );

        box-shadow:
            0 10px 30px rgba(99,102,241,0.28);

        transition: 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);

        box-shadow:
            0 15px 40px rgba(139,92,246,0.38);
    }


    /* ======================================================
       DOWNLOAD BUTTON
       ====================================================== */

    .stDownloadButton > button {
        width: 100%;

        border: 1px solid rgba(52,211,153,0.35);

        border-radius: 14px;

        padding: 0.8rem 1.2rem;

        font-weight: 750;

        color: #ecfdf5;

        background:
            linear-gradient(
                135deg,
                rgba(16,185,129,0.85),
                rgba(5,150,105,0.9)
            );

        box-shadow:
            0 10px 35px rgba(16,185,129,0.2);
    }


    /* ======================================================
       STAT CARDS
       ====================================================== */

    .stat-card {
        text-align: center;

        padding: 20px;

        border-radius: 18px;

        background:
            rgba(255,255,255,0.045);

        border:
            1px solid rgba(255,255,255,0.07);
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 800;

        background:
            linear-gradient(
                90deg,
                #60a5fa,
                #a78bfa
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stat-label {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: 4px;
    }


    /* ======================================================
       LANGUAGE CARDS
       ====================================================== */

    .language-card {
        position: relative;

        padding: 22px;

        min-height: 145px;

        border-radius: 20px;

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.07),
                rgba(255,255,255,0.025)
            );

        border:
            1px solid rgba(255,255,255,0.08);

        overflow: hidden;
    }

    .language-icon {
        font-size: 2rem;
        margin-bottom: 8px;
    }

    .language-name {
        font-weight: 750;
        font-size: 1.05rem;
    }

    .language-count {
        margin-top: 8px;
        color: #94a3b8;
        font-size: 0.9rem;
    }


    /* ======================================================
       PROCESSING CARD
       ====================================================== */

    .processing-card {
        padding: 22px;

        border-radius: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(59,130,246,0.08),
                rgba(139,92,246,0.08)
            );

        border:
            1px solid rgba(129,140,248,0.18);

        margin-top: 18px;
    }

    .processing-title {
        font-weight: 700;
        font-size: 1rem;
    }

    .processing-text {
        color: #94a3b8;
        margin-top: 5px;
    }


    /* ======================================================
       EXPANDER
       ====================================================== */

    [data-testid="stExpander"] {
        background:
            rgba(255,255,255,0.035);

        border:
            1px solid rgba(255,255,255,0.07);

        border-radius: 16px;
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {
        text-align: center;

        margin-top: 45px;

        padding-top: 25px;

        border-top:
            1px solid rgba(255,255,255,0.07);

        color: #64748b;

        font-size: 0.82rem;
    }

    .footer-highlight {
        color: #a78bfa;
        font-weight: 650;
    }


    /* ======================================================
       MOBILE
       ====================================================== */

    @media (max-width: 768px) {

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero {
            padding-top: 1.3rem;
        }

        .hero-title {
            font-size: 2.4rem;
        }

        .hero-subtitle {
            font-size: 0.95rem;
        }

        .glass-card {
            padding: 18px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HERO SECTION
# ============================================================

st.html(
    """
    <div class="hero">

        <div class="hero-badge">
            ✦ AI-POWERED EDUCATIONAL TOOL
        </div>

        <div class="hero-title">
            Multilingual QnA Generator
        </div>

        <div class="hero-subtitle">
            Transform your documents into accurate, contextual
            Question & Answer pairs in
            <b>English</b>, <b>हिन्दी</b> and <b>मराठी</b>.
        </div>

    </div>
    """
)


# ============================================================
# TOP STATS
# ============================================================

stat1, stat2, stat3, stat4 = st.columns(4)


with stat1:
    st.html(
        """
        <div class="stat-card">
            <div class="stat-number">3</div>
            <div class="stat-label">Output Languages</div>
        </div>
        """
    )


with stat2:
    st.html(
        """
        <div class="stat-card">
            <div class="stat-number">3</div>
            <div class="stat-label">Supported Formats</div>
        </div>
        """
    )


with stat3:
    st.html(
        """
        <div class="stat-card">
            <div class="stat-number">AI</div>
            <div class="stat-label">Question Generation</div>
        </div>
        """
    )


with stat4:
    st.html(
        """
        <div class="stat-card">
            <div class="stat-number">XLSX</div>
            <div class="stat-label">Final Output</div>
        </div>
        """
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# UPLOAD SECTION
# ============================================================

st.html(
    """
    <div class="glass-card">

        <div class="section-title">
            📄 Upload Your Document
        </div>

        <div class="section-description">
            Upload a PDF, DOCX or TXT file to generate
            multilingual Question & Answer pairs.
        </div>

    </div>
    """
)


uploaded_file = st.file_uploader(
    "Choose a document",
    type=["pdf", "docx", "txt"],
    label_visibility="collapsed"
)


# ============================================================
# WHEN FILE IS UPLOADED
# ============================================================

if uploaded_file:

    # ========================================================
    # FILE INFORMATION
    # ========================================================

    file_size_mb = uploaded_file.size / (1024 * 1024)

    col1, col2, col3 = st.columns(3)


    with col1:

        st.html(
            f"""
            <div class="stat-card">

                <div class="stat-number">
                    📄
                </div>

                <div class="stat-label">
                    {uploaded_file.name}
                </div>

            </div>
            """
        )


    with col2:

        st.html(
            f"""
            <div class="stat-card">

                <div class="stat-number">
                    {file_size_mb:.2f}
                </div>

                <div class="stat-label">
                    File Size (MB)
                </div>

            </div>
            """
        )


    with col3:

        st.html(
            f"""
            <div class="stat-card">

                <div class="stat-number">
                    {Path(uploaded_file.name).suffix.upper()}
                </div>

                <div class="stat-label">
                    File Format
                </div>

            </div>
            """
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # ========================================================
    # GENERATE BUTTON
    # ========================================================

    generate_button = st.button(
        "🚀 Generate Multilingual QnA",
        use_container_width=True
    )


    if generate_button:

        temp_path = None

        try:

            # =================================================
            # PROCESSING CARD
            # =================================================

            st.html(
                """
                <div class="processing-card">

                    <div class="processing-title">
                        ⚡ AI Processing Started
                    </div>

                    <div class="processing-text">
                        Your document is being analyzed and
                        transformed into multilingual
                        educational content.
                    </div>

                </div>
                """
            )


            progress_bar = st.progress(0)
            status = st.empty()


            # =================================================
            # SAVE TEMP FILE
            # =================================================

            suffix = Path(uploaded_file.name).suffix

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name


            # =================================================
            # STEP 1 - READ DOCUMENT
            # =================================================

            status.info("📖 Reading document...")

            progress_bar.progress(10)

            text = extract_text(temp_path)

            if not text or not text.strip():

                raise ValueError(
                    "The document does not contain readable text."
                )

            time.sleep(0.3)


            # =================================================
            # STEP 2 - CLEAN TEXT
            # =================================================

            status.info(
                "🧹 Cleaning and preparing document..."
            )

            progress_bar.progress(20)

            text = clean_text(text)

            time.sleep(0.3)


            # =================================================
            # STEP 3 - CHUNK TEXT
            # =================================================

            status.info(
                "✂️ Splitting document into intelligent sections..."
            )

            progress_bar.progress(30)

            chunks = chunk_text(
                text,
                max_words=1800
            )

            if not chunks:

                raise ValueError(
                    "Unable to create document chunks."
                )

            time.sleep(0.3)


            # =================================================
            # STEP 4 - GENERATE ENGLISH QNA
            # =================================================

            status.info(
                "🧠 Generating context-aware English QnAs..."
            )

            english_qna = []

            total_chunks = len(chunks)


            for index, chunk in enumerate(
                chunks,
                start=1
            ):

                qna = generate_qna(
                    chunk,
                    number_of_questions=5
                )

                qna = validate_qna(
                    chunk,
                    qna
                )

                english_qna.extend(qna)

                generation_progress = (
                    30
                    + int(
                        (index / total_chunks) * 30
                    )
                )

                progress_bar.progress(
                    min(
                        generation_progress,
                        60
                    )
                )


            english_qna = remove_duplicate_questions(
                english_qna
            )


            if not english_qna:

                raise RuntimeError(
                    "No valid QnAs were generated."
                )


            # =================================================
            # STEP 5 - HINDI TRANSLATION
            # =================================================

            status.info(
                "🇮🇳 Translating QnAs into Hindi..."
            )

            progress_bar.progress(70)

            hindi_qna = translate_qna(
                english_qna,
                "Hindi"
            )

            time.sleep(0.3)


            # =================================================
            # STEP 6 - MARATHI TRANSLATION
            # =================================================

            status.info(
                "🇮🇳 Translating QnAs into Marathi..."
            )

            progress_bar.progress(82)

            marathi_qna = translate_qna(
                english_qna,
                "Marathi"
            )

            time.sleep(0.3)


            # =================================================
            # STEP 7 - CREATE EXCEL
            # =================================================

            status.info(
                "📊 Creating multilingual Excel workbook..."
            )

            progress_bar.progress(92)

            output_dir = Path("output")

            output_dir.mkdir(
                exist_ok=True
            )

            output_file = (
                output_dir /
                "Multilingual_QnA.xlsx"
            )


            create_excel(
                english_qna,
                hindi_qna,
                marathi_qna,
                str(output_file)
            )


            progress_bar.progress(100)

            time.sleep(0.5)


            status.success(
                "✨ QnA generation completed successfully!"
            )


            # =================================================
            # SUCCESS CARD
            # =================================================

            st.html(
                """
                <div class="glass-card">

                    <div class="section-title">
                        🎉 Generation Complete
                    </div>

                    <div class="section-description">
                        Your multilingual Question & Answer
                        dataset is ready.
                    </div>

                </div>
                """
            )


            st.markdown("<br>", unsafe_allow_html=True)


            # =================================================
            # LANGUAGE RESULT CARDS
            # =================================================

            lang1, lang2, lang3 = st.columns(3)


            with lang1:

                st.html(
                    f"""
                    <div class="language-card">

                        <div class="language-icon">
                            🇬🇧
                        </div>

                        <div class="language-name">
                            English
                        </div>

                        <div class="language-count">
                            {len(english_qna)}
                            Question-Answer pairs
                        </div>

                    </div>
                    """
                )


            with lang2:

                st.html(
                    f"""
                    <div class="language-card">

                        <div class="language-icon">
                            🇮🇳
                        </div>

                        <div class="language-name">
                            हिन्दी
                        </div>

                        <div class="language-count">
                            {len(hindi_qna)}
                            Question-Answer pairs
                        </div>

                    </div>
                    """
                )


            with lang3:

                st.html(
                    f"""
                    <div class="language-card">

                        <div class="language-icon">
                            🇮🇳
                        </div>

                        <div class="language-name">
                            मराठी
                        </div>

                        <div class="language-count">
                            {len(marathi_qna)}
                            Question-Answer pairs
                        </div>

                    </div>
                    """
                )


            # =================================================
            # PREVIEW
            # =================================================

            st.markdown("<br>", unsafe_allow_html=True)


            st.html(
                """
                <div class="section-title">
                    👀 Preview Generated QnAs
                </div>

                <div class="section-description">
                    Review the generated questions and answers
                    before downloading the final Excel file.
                </div>
                """
            )


            tab1, tab2, tab3 = st.tabs(
                [
                    "🇬🇧 English",
                    "🇮🇳 हिन्दी",
                    "🇮🇳 मराठी"
                ]
            )


            # =================================================
            # ENGLISH
            # =================================================

            with tab1:

                st.dataframe(
                    english_qna,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "question": st.column_config.TextColumn(
                            "Questions",
                            width="large"
                        ),
                        "answer": st.column_config.TextColumn(
                            "Answers",
                            width="large"
                        )
                    }
                )


            # =================================================
            # HINDI
            # =================================================

            with tab2:

                st.dataframe(
                    hindi_qna,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "question": st.column_config.TextColumn(
                            "Questions",
                            width="large"
                        ),
                        "answer": st.column_config.TextColumn(
                            "Answers",
                            width="large"
                        )
                    }
                )


            # =================================================
            # MARATHI
            # =================================================

            with tab3:

                st.dataframe(
                    marathi_qna,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "question": st.column_config.TextColumn(
                            "Questions",
                            width="large"
                        ),
                        "answer": st.column_config.TextColumn(
                            "Answers",
                            width="large"
                        )
                    }
                )


            # =================================================
            # DOWNLOAD SECTION
            # =================================================

            st.markdown("<br>", unsafe_allow_html=True)


            st.html(
                """
                <div class="glass-card">

                    <div class="section-title">
                        📥 Download Your Dataset
                    </div>

                    <div class="section-description">
                        The workbook contains three sheets:
                        English, Hindi and Marathi.
                    </div>

                </div>
                """
            )


            with open(
                output_file,
                "rb"
            ) as file:

                st.download_button(
                    label="⬇️ Download Multilingual_QnA.xlsx",
                    data=file,
                    file_name="Multilingual_QnA.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True
                )


            # =================================================
            # PROCESSING DETAILS
            # =================================================

            with st.expander(
                "🔍 View Processing Details"
            ):

                detail1, detail2 = st.columns(2)


                with detail1:

                    st.write(
                        f"**Document:** {uploaded_file.name}"
                    )

                    st.write(
                        f"**Characters extracted:** "
                        f"{len(text):,}"
                    )

                    st.write(
                        f"**Document chunks:** "
                        f"{len(chunks)}"
                    )


                with detail2:

                    st.write(
                        f"**English QnAs:** "
                        f"{len(english_qna)}"
                    )

                    st.write(
                        f"**Hindi QnAs:** "
                        f"{len(hindi_qna)}"
                    )

                    st.write(
                        f"**Marathi QnAs:** "
                        f"{len(marathi_qna)}"
                    )


        # =====================================================
        # ERROR HANDLING
        # =====================================================

        except Exception as error:

            if "progress_bar" in locals():
                progress_bar.empty()

            if "status" in locals():
                status.error(
                    "❌ Something went wrong during processing."
                )

            st.error(
                f"Error: {error}"
            )


            with st.expander(
                "🛠️ Troubleshooting"
            ):

                st.markdown(
                    """
                    **Possible causes:**

                    - The document contains no readable text.
                    - The PDF may be scanned/image-only.
                    - The Gemini API key may be missing or invalid.
                    - The Gemini API free-tier limit may have been reached.
                    - The document may be too large.
                    - A temporary network/API error occurred.
                    - One of the required Python packages is missing.

                    Try a smaller text-based document first.
                    """
                )


        # =====================================================
        # CLEAN TEMP FILE
        # =====================================================

        finally:

            if temp_path:

                try:

                    Path(temp_path).unlink(
                        missing_ok=True
                    )

                except Exception:

                    pass


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.html(
        """
        <br>

        <div class="glass-card">

            <div style="text-align:center;">

                <div style="font-size:4rem;">
                    📚
                </div>

                <div class="section-title">
                    Ready to Generate Questions?
                </div>

                <div class="section-description">

                    Upload your study material above and let AI
                    automatically create meaningful Question &
                    Answer pairs.

                </div>

            </div>

        </div>

        <br>
        """
    )


    # ========================================================
    # FEATURES
    # ========================================================

    feature1, feature2, feature3 = st.columns(3)


    with feature1:

        st.html(
            """
            <div class="language-card">

                <div class="language-icon">
                    🧠
                </div>

                <div class="language-name">
                    Context-Aware AI
                </div>

                <div class="language-count">
                    Questions are generated directly
                    from your document content.
                </div>

            </div>
            """
        )


    with feature2:

        st.html(
            """
            <div class="language-card">

                <div class="language-icon">
                    🌐
                </div>

                <div class="language-name">
                    Multilingual
                </div>

                <div class="language-count">
                    Generate content in English,
                    Hindi and Marathi.
                </div>

            </div>
            """
        )


    with feature3:

        st.html(
            """
            <div class="language-card">

                <div class="language-icon">
                    📊
                </div>

                <div class="language-name">
                    Excel Ready
                </div>

                <div class="language-count">
                    Download all generated QnAs
                    in one organized workbook.
                </div>

            </div>
            """
        )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="footer">

        Built with
        <span class="footer-highlight">Python</span>
        +
        <span class="footer-highlight">Streamlit</span>
        +
        <span class="footer-highlight">Gemini AI</span>

        <br><br>

        Multilingual QnA Generation System •
        College Project

    </div>
    """
)