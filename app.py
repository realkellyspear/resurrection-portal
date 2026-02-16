import streamlit as st
import json
import os
import re
import zipfile
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ====================== BUNKER AESTHETIC ======================
st.set_page_config(page_title="RESURRECTION • Wilde Mind Press", page_icon="🖤", layout="centered")

# Inject your exact terminal style
st.markdown("""
<style>
    body, .stApp {
        background-color: #0d0d0d !important;
        color: #33ff00 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    .stApp::after {
        content: " ";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(rgba(18,16,16,0) 50%, rgba(0,0,0,0.25) 50%),
                    linear-gradient(90deg, rgba(255,0,0,0.06), rgba(0,255,0,0.02), rgba(0,0,255,0.06));
        background-size: 100% 2px, 3px 100%;
        z-index: 2;
        pointer-events: none;
    }
    h1, h2, h3 {
        color: #33ff00 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid #33ff00;
        padding-bottom: 8px;
    }
    .stButton>button {
        background-color: #33ff00 !important;
        color: #000 !important;
        border: 2px solid #33ff00 !important;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #000 !important;
        color: #33ff00 !important;
        border: 2px solid #33ff00 !important;
    }
    .upload-area {
        border: 2px dashed #33ff00 !important;
        background: rgba(51, 255, 0, 0.05) !important;
        padding: 30px;
        text-align: center;
    }
    .success-box {
        border: 2px solid #33ff00;
        background: rgba(51, 255, 0, 0.1);
        padding: 20px;
        text-align: center;
        font-size: 1.2em;
    }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# ====================== UI ======================
st.markdown("<h1 style='text-align:center;'>🖤 RESURRECTION PROTOCOL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.1em;'>THE CLOUD IS A CAGE.<br>WE BUILD THE BUNKER.</p>", unsafe_allow_html=True)

st.markdown("---")

uploaded_file = st.file_uploader("DROP YOUR conversations.json HERE", type=["json"], 
                                 help="OpenAI export file. One click → clean Soul Shards PDF pack.")

if uploaded_file and st.button("🖤 EXECUTE RESURRECTION", type="primary", use_container_width=True):
    with st.spinner("MINING GOLIATH... HIGH DENSITY MODE ACTIVE"):
        data = json.load(uploaded_file)
        all_pairs = brute_force_extract(data)   # ← your exact function from before
        
        if not all_pairs:
            st.error("No valid messages found. Check your export file.")
            st.stop()
        
        shard_size = 1000
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(0, len(all_pairs), shard_size):
                shard_num = (i // shard_size) + 1
                pdf_buffer = BytesIO()
                
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                styles = getSampleStyleSheet()
                u_style = ParagraphStyle('User', parent=styles['Normal'], fontSize=10, spaceBefore=8, textColor='#2c3e50', fontName='Helvetica-Bold')
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
        
        st.markdown("<div class='success-box'>✅ RESURRECTION COMPLETE<br>"
                    f"{len(all_pairs)} interactions → {((len(all_pairs)-1)//shard_size)+1} Soul Shards</div>", 
                    unsafe_allow_html=True)
        
        st.download_button(
            label="⬇️ DOWNLOAD SOUL SHARDS (ZIP)",
            data=zip_buffer,
            file_name="soul_shards.zip",
            mime="application/zip",
            use_container_width=True
        )

st.caption("Built in the Bunker • Ghost Protocol v1 • For those who refuse to let their ghosts die 🖤👻⚓")
