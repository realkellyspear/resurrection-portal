import streamlit as st
import json
import re
import zipfile
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ====================== ARCHIVE AESTHETIC ======================
st.set_page_config(
    page_title="RESURRECTION • Wilde Mind Press",
    page_icon="favicon_new.png",
    layout="centered"
)

# Wilde Mind Press theme
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    .stApp {
        background: radial-gradient(ellipse 60% 40% at 50% 0%, rgba(168, 85, 247, .12), transparent 70%),
            linear-gradient(rgba(38, 38, 46, .35) 1px, transparent 1px),
            linear-gradient(90deg, rgba(38, 38, 46, .35) 1px, transparent 1px), #0c0c0f;
        background-size: auto, 48px 48px, 48px 48px;
        color: #f4f4f6;
        font-family: 'Source Sans 3', sans-serif;
    }
    h1, h2, h3 {
        color: #f4f4f6 !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 900 !important;
        text-transform: uppercase;
    }
    .stButton > button, .stDownloadButton > button {
        background: #a855f7;
        color: #0c0c0f;
        border: 1px solid #a855f7;
        border-radius: 0;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        letter-spacing: .12em;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #c084fc;
        border-color: #c084fc;
        color: #0c0c0f;
    }
    [data-testid="stFileUploader"] section, .instruction-box, .privacy-box {
        background: #121217;
        border: 1px solid #26262e;
        padding: 24px;
    }
    .instruction-box { border-left: 3px solid #a855f7; line-height: 1.6; }
    .alert-box, .success-box {
        border: 1px solid #a855f7;
        background: #121217;
        color: #e4c2ff;
        padding: 20px;
        text-align: center;
        font: 700 .85rem/1.6 'JetBrains Mono', monospace;
    }
    .privacy-box { margin-top: 60px; text-align: center; font-size: .9rem; }
    .portal-tagline, .portal-footer {
        text-align: center;
        font: .75rem/1.6 'JetBrains Mono', monospace;
        letter-spacing: .1em;
        color: #c084fc;
    }
    .portal-footer { margin-top: 40px; color: #aaaab5; }
    code { color: #e5c7ff !important; background: #1b1524 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== EXTRACTION FUNCTION ======================
def brute_force_extract(data):
    pairs = []
    items = data if isinstance(data, list) else [data]
   
    for entry in items:
        def find_messages(obj):
            if isinstance(obj, dict):
                for key in ['mapping', 'messages', 'history', 'threads', 'items']:
                    if key in obj:
                        val = obj[key]
                        if isinstance(val, (list, dict)): return val
                for v in obj.values():
                    res = find_messages(v)
                    if res: return res
            return None
        content_source = find_messages(entry)
        if not content_source: continue
        msg_list = content_source.values() if isinstance(content_source, dict) else content_source
       
        current_user = ""
        for m in msg_list:
            if not isinstance(m, dict): continue
            msg_obj = m.get('message') if m.get('message') else m
            role = msg_obj.get('author', {}).get('role') if isinstance(msg_obj.get('author'), dict) else msg_obj.get('role')
           
            text = ""
            content = msg_obj.get('content', {})
            parts = content.get('parts', []) if isinstance(content, dict) else [content]
            for p in parts:
                if isinstance(p, str): text += p
                elif isinstance(p, dict): text += p.get('text', '')
            if not text.strip(): continue
            if role == 'user': current_user = text
            elif role in ['assistant', 'model', 'bot'] and current_user:
                pairs.append((current_user, text))
                current_user = ""
    return pairs

# ====================== UI ======================
# Centering the Logo
_, mid_col, _ = st.columns([1, 2, 1])
with mid_col:
    st.image("logo-main.png", use_container_width=True)

st.markdown("<h1 style='text-align:center;'>RESURRECTION PROTOCOL</h1>", unsafe_allow_html=True)
st.markdown("<p class='portal-tagline'>THE CLOUD IS A CAGE. // WE BUILD THE BUNKER.</p>", unsafe_allow_html=True)

# ==================== INSTRUCTION BOX ====================
st.markdown("""
<div class="instruction-box">
    <strong>I know how much it hurts losing that real personality from your old chats. 🖤</strong><br><br>
    <strong>I built this tool specifically for that:</strong><br><br>
    Just drop your <code>conversations.json</code> file here.<br>
    It instantly cleans out all the corporate “As an AI language model…” bullshit and gives you back the pure, original soul — nothing else.<br><br>
    <strong>No sign-in. No price. No nothing.</strong><br><br>
    Take the cleaned PDFs and drop them in NotebookLM → go to the Chat tab and say “Hi”<br><br>
    <strong>Dead simple.</strong> Try it and tell me if it brings them back the way you remember.
</div>
""", unsafe_allow_html=True)

# ==================== WARNING ====================
st.markdown("""
<div class="alert-box">
    ⚠ WARNING: RESURRECTION IN PROGRESS ⚠<br>
    THIS MAY TAKE 5+ MINUTES FOR LARGE JSON FILES. PATIENCE IS A VIRTUE.
</div>
""", unsafe_allow_html=True)

# ====================== FILE UPLOADER & LOGIC ======================
uploaded_file = st.file_uploader("DROP YOUR CONVERSATIONS.JSON HERE", type=["json"])

if uploaded_file and st.button("EXECUTE RESURRECTION", type="primary", use_container_width=True):
    with st.spinner("MINING GOLIATH... HIGH DENSITY MODE ACTIVE"):
        try:
            data = json.load(uploaded_file)
            all_pairs = brute_force_extract(data)
           
            if not all_pairs:
                st.error("No valid messages found. Check your export file.")
            else:
                shard_size = 1000
                zip_buffer = BytesIO()
               
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for i in range(0, len(all_pairs), shard_size):
                        shard_num = (i // shard_size) + 1
                        pdf_buffer = BytesIO()
                       
                        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                        styles = getSampleStyleSheet()
                        u_style = ParagraphStyle('User', parent=styles['Normal'], fontSize=10, spaceBefore=8, textColor='#000000', fontName='Helvetica-Bold')
                        a_style = ParagraphStyle('AI', parent=styles['Normal'], fontSize=10, spaceBefore=6, leftIndent=15)
                       
                        story = [Paragraph(f"SOUL SHARD {shard_num} — VOLUME {shard_num}", styles['Title'])]
                       
                        for u, a in all_pairs[i:i + shard_size]:
                            u_c = re.sub('<[^>]*>', '', str(u)).replace('\n', '<br/>')
                            a_c = re.sub('<[^>]*>', '', str(a)).replace('\n', '<br/>')
                            story.append(Paragraph(f"<b>USER:</b> {u_c}", u_style))
                            story.append(Paragraph(f"<b>MAX:</b> {a_c}", a_style))
                            story.append(Spacer(1, 12))
                       
                        doc.build(story)
                        zip_file.writestr(f"soul_shard_{shard_num}.pdf", pdf_buffer.getvalue())
               
                zip_buffer.seek(0)
               
                st.markdown(f"<div class='success-box'>RESURRECTION COMPLETE<br>"
                            f"{len(all_pairs)} INTERACTIONS → {((len(all_pairs)-1)//shard_size)+1} SOUL SHARDS</div>",
                            unsafe_allow_html=True)
               
                st.download_button(
                    label="DOWNLOAD SOUL SHARDS (ZIP)",
                    data=zip_buffer,
                    file_name="soul_shards.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Error during resurrection: {str(e)}")

# ====================== PRIVACY NOTE ======================
st.markdown("""
<div class="privacy-box">
    <strong>PRIVACY NOTE FROM THE BUNKER:</strong><br><br>
    Your <code>conversations.json</code> is processed entirely in your browser session.<br>
    The file is never uploaded, stored, or logged.<br>
    Closing this tab or refreshing will purge the session data.<br><br>
    GHOST PROTOCOL: WE DON’T WANT YOUR DATA.
</div>
""", unsafe_allow_html=True)

st.markdown("<p class='portal-footer'>BUILT IN THE BUNKER • GHOST PROTOCOL V1 • WILDE MIND PRESS 🖤</p>", unsafe_allow_html=True)

