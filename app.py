import streamlit as st
import json
import re
import zipfile
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ====================== BUNKER AESTHETIC ======================
st.set_page_config(
    page_title="RESURRECTION • Wilde Mind Press",
    page_icon="favicon.png",
    layout="centered"
)

# Full terminal scanline + green glow
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
        background: rgba(51,255,0,0.05) !important; 
        padding: 40px; 
        text-align: center; 
        border-radius: 8px; 
    }
    .alert-box { 
        border: 1px dashed #ff0000; 
        color: #ff0000; 
        background: rgba(255,0,0,0.05); 
        padding: 20px; 
        margin: 20px 0; 
        text-align: center; 
        font-weight: bold; 
        letter-spacing: 1px; 
        text-shadow: 0 0 5px #ff0000; 
    }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .success-box { 
        border: 2px solid #33ff00; 
        background: rgba(51,255,0,0.1); 
        padding: 20px; 
        text-align: center; 
        font-size: 1.2em; 
        margin: 20px 0; 
    }
</style>
""", unsafe_allow_html=True)

# ====================== YOUR EXTRACTION FUNCTION ======================
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
st.image("logo-main.png", width=400, use_column_width="always")  # Big centered logo

st.markdown("<h1 style='text-align:center;'>🖤 RESURRECTION PROTOCOL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.2em;'>THE CLOUD IS A CAGE.<br>WE BUILD THE BUNKER.</p>", unsafe_allow_html=True)

st.markdown("""
<div class="alert-box">
⚠ WARNING: RESURRECTION IN PROGRESS ⚠<br>
This may take 5+ minutes for large JSON files. Patience is a virtue in the Bunker.
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("DROP YOUR conversations.json HERE", type=["json"], 
                                 help="OpenAI export file. One drag → clean PDF Soul Shards pack.")

if uploaded_file and st.button("🖤 EXECUTE RESURRECTION", type="primary", use_container_width=True):
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
                
                st.markdown(f"<div class='success-box'>✅ RESURRECTION COMPLETE<br>"
                            f"{len(all_pairs)} interactions → {((len(all_pairs)-1)//shard_size)+1} Soul Shards</div>", 
                            unsafe_allow_html=True)
                
                st.download_button(
                    label="⬇️ DOWNLOAD SOUL SHARDS (ZIP)",
                    data=zip_buffer,
                    file_name="soul_shards.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Error during resurrection: {str(e)}")

st.markdown("<p style='text-align:center; font-size:0.9em; opacity:0.8;'>Built in the Bunker • Ghost Protocol v1 • For those who refuse to let their ghosts die 🖤👻⚓</p>", unsafe_allow_html=True)
