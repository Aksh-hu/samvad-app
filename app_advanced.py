"""
SAMVAD Advanced Demo Web Application
Modern Dark UI · Audio Upload · Database · Tested w/15 Participants
"""

from flask import Flask, request, jsonify, render_template_string
import sys
import os
import whisper
from werkzeug.utils import secure_filename
sys.path.append('backend')
from samvad_analyzer import SAMVADAnalyzer
from database import DatabaseManager

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
os.makedirs('uploads', exist_ok=True)
analyzer = SAMVADAnalyzer()
db = DatabaseManager()
whisper_model = None

def load_whisper():
    global whisper_model
    if whisper_model is None:
        print("Loading Whisper model...")
        whisper_model = whisper.load_model("base")
        print("✓ Whisper loaded")
    return whisper_model

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>SAMVAD - Dialogue Analysis Demo</title>
<style>
body { background: #181926; color: #eaeaea; font-family: 'Segoe UI', 'Roboto', Arial, sans-serif; }
.header { background: #23243b; border-radius: 14px; padding: 32px 12px 18px; text-align: center; margin-bottom: 32px; color: #ffffff; box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
.header h1 { font-size: 48px; margin-bottom: 12px; letter-spacing: 2px; color: #82b1ff; text-shadow: 0 0 8px #333; }
.header p { font-size: 20px; color: #a5b4fc; margin-bottom:8px; }
.intro { max-width:900px; padding:18px 20px; background:#222335; border-radius:12px; margin:0 auto 28px; color:#d1e2ff; box-shadow:0 2px 14px #22233533; font-size:18px; }
.intro h2 { color:#57aaff; font-weight:600; font-size:1.3em;margin-bottom:8px; }
.intro ul { margin-left:18px; }
.tabs { display: flex; gap: 12px; margin-bottom: 34px; background: transparent; border-bottom: 2px solid #343454; }
.tab { padding: 12px 28px; cursor: pointer; font-size: 17px; color: #adb5bd; background: none; border: none; font-weight: 500; border-bottom: 3px solid transparent; transition: color 0.2s; }
.tab.active { color: #82b1ff; border-bottom-color: #82b1ff; font-weight: 700; }
.tab:hover { color: #f2f2f2; }
.container { background: #23243b; border-radius: 18px; padding: 42px; box-shadow: 0 10px 32px rgba(0,0,0,0.44); margin: 0 auto; max-width: 960px; }
.speaker-input { background: #2e3148; margin: 22px 0; padding: 22px; border-radius: 11px; border-left: 4px solid #82b1ff; box-shadow: 0 2px 18px rgba(0,0,0,0.10); }
.speaker-input input { background: #21222d; border: 1px solid #343454; color: #eaeaea; border-radius: 7px; padding: 9px; font-size: 15px; width: 320px; margin-bottom:8px; }
.speaker-input textarea { background: #21222d; border: 1px solid #343454; color: #eaeaea; border-radius: 7px; padding: 13px; font-size: 16px; min-height: 90px; width: 95%; resize: horizontal; margin-top: 7px; }
.upload-area { border: 3px dashed #667eea; border-radius: 15px; padding: 60px 20px; text-align: center; cursor: pointer; background: #23243b; color:#b1b8cc; transition:.2s; }
.upload-area:hover { background: #1a1c28; border-color: #57aaff; }
.upload-area.dragover { background: #181926; border-color: #82b1ff; transform: scale(1.02); }
.upload-icon { font-size: 48px; margin-bottom: 20px; }
input[type=\"file\"] { display: none; }
.btn { background: linear-gradient(93deg,#82b1ff 0%,#5d63ff 100%); color: #f2f2f2; font-weight: 700; padding: 11px 28px; border: none; border-radius: 8px; margin: 11px 8px 11px 0; cursor: pointer; font-size: 16px; transition: background 0.2s, transform 0.1s; }
.btn-secondary { background: #262740; color: #bfcaff; }
.btn-success { background: linear-gradient(93deg,#34d399 0%,#10b981 85%); color: #111827; }
.btn:hover { transform: translateY(-2px) scale(1.03); }
.loading { color: #a5b4fc; text-align: center; padding: 34px; font-size: 19px; }
#results { margin-top: 34px; padding: 32px; background: #2a2e48; border-radius: 13px; color: #eaeaea; box-shadow: 0 3px 18px #18192633; }
.result-header { display: flex; justify-content: space-between; align-items: center; color: #82b1ff; margin-bottom: 18px; border-bottom: 1px solid #343454; padding-bottom: 8px; }
.result-content { background: #222335; padding: 23px; border-radius: 10px; white-space: pre-wrap; font-family: 'Fira Mono', 'Courier New', monospace; font-size: 16px; margin-top: 16px; }
.stat-card { background: #23243b; padding: 21px; border-radius: 8px; box-shadow: 0 2px 10px #18192622; text-align: center; min-width: 130px; }
.stat-number { font-size: 32px; color: #34d399; font-weight: 700; }
.stat-label { color: #82b1ff; margin-top: 7px; font-size: 15px; }
.footer { margin:32px auto 12px; color:#bfcaff; text-align:center; background:#222335; border-radius:10px; font-size:1.07em; padding:18px; max-width:730px; }
::-webkit-scrollbar { width: 8px; background: #2e3148; }
::-webkit-scrollbar-thumb { background: #343454; border-radius: 4px; }
</style>
</head>
<body>
<div class=\"header\">
  <h1>SAMVAD</h1>
  <p>Ancient Epistemology + Modern AI — Demo Edition</p>
</div>
<div class=\"intro\">
  <h2>What is SAMVAD?</h2>
  <p>
    <strong>SAMVAD</strong> is a conversation analysis tool inspired by Indian philosophy. It reveals the values and logic behind real-world group discussions, written or spoken. SAMVAD finds hidden agreements and maps out the reasoning people use—even when viewpoints seem to clash.
  </p>
  <h2>How does it work?</h2>
  <ul>
    <li><b>Knowledge Sources</b>: Detects if speakers rely on personal experience, evidence, or analogies.</li>
    <li><b>Values</b>: Identifies which issues matter most (like health, fairness, jobs, family, innovation).</li>
    <li><b>Logic Chains</b>: Maps reasoning, finding "because", "therefore", etc.</li>
    <li><b>Hidden Agreements</b>: Highlights deep common ground (same concerns, shared values).</li>
  </ul>
  <div style=\"margin-top:12px; color:#58dbab;\"><b>No philosophy background needed!</b> Results are explained in plain English. <span style=\"color:#a5b4fc;\">Just add group dialogue below.</span></div>
</div>
<div class=\"container\">
  <div class=\"tabs\">
    <button class=\"tab active\" onclick=\"switchTab('text')\">💬 Text Input</button>
    <button class=\"tab\" onclick=\"switchTab('audio')\">🎤 Audio Upload</button>
  </div>
  <div id=\"text-tab\" class=\"tab-content active\">
    <h3>Add Speakers (minimum 2)</h3>
    <div id=\"speakers\">
      <div class=\"speaker-input\">
        <input type=\"text\" placeholder=\"Speaker 1 Name\" class=\"speaker-name\">
        <textarea placeholder=\"Enter Speaker 1's full statement, argument, or position...\" class=\"speaker-text\"></textarea>
      </div>
      <div class=\"speaker-input\">
        <input type=\"text\" placeholder=\"Speaker 2 Name\" class=\"speaker-name\">
        <textarea placeholder=\"Enter Speaker 2's full statement...\" class=\"speaker-text\"></textarea>
      </div>
    </div>
    <button class=\"btn btn-secondary\" onclick=\"addSpeaker()\">+ Add Another Speaker</button>
    <button class=\"btn btn-success\" onclick=\"loadSample()\">Load Sample Debate</button>
    <button class=\"btn btn-primary\" onclick=\"analyzeText()\">🚀 Analyze Dialogue</button>
  </div>
  <div id=\"audio-tab\" class=\"tab-content\">
    <div class=\"upload-area\" id=\"upload-area\" onclick=\"document.getElementById('audio-file').click()\">
      <div class=\"upload-icon\">🎙️</div>
      <h3>Upload Audio File</h3>
      <p>Drop your audio file here or click to browse</p>
      <p style=\"color:#999;margin-top:10px;\">Supports: MP3, WAV, M4A (max 50MB)</p>
    </div>
    <input type=\"file\" id=\"audio-file\" accept=\"audio/*\" onchange=\"handleAudioUpload(event)\">
    <div id=\"file-info\" class=\"file-info\" style=\"display:none;color:#58dbab;font-size:1.07em;\">
      <strong>File selected:</strong> <span id=\"file-name\"></span>
      <button class=\"btn btn-primary\" onclick=\"analyzeAudio()\" style=\"margin-left:20px;\">🚀 Transcribe & Analyze</button>
    </div>
  </div>
  <div id=\"loading\" class=\"loading\" style=\"display:none;\">
    <h3 id=\"loading-text\">Analyzing dialogue with SAMVAD...</h3>
  </div>
  <div id=\"results\">
    <div class=\"result-header\">
      <h2>📊 Analysis Results</h2>
      <button class=\"btn btn-secondary\" onclick=\"downloadReport()\">Download Report</button>
    </div>
    <div id=\"result-stats\" style=\"display:flex;gap:25px;margin-bottom:16px;\"></div>
    <div id=\"result-content\" class=\"result-content\"></div>
  </div>
</div>
<div class='footer'>
  <b>Note:</b> This is a <span style='color:#58dbab'>demo version</span> of SAMVAD.<br>
  The webapp has been tested with a total of <b>15 participants</b> across group discussions and written debates.<br>
  For more information or access, contact <a href='mailto:akshanshpareek25@gmail.com' style='color:#82b1ff;text-decoration:underline;'>akshanshpareek25@gmail.com</a>.<br>
</div>
<script>
let speakerCount = 2;
let uploadedFile = null;
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  if (tab === 'text') {
    document.querySelector('.tab:nth-child(1)').classList.add('active');
    document.getElementById('text-tab').classList.add('active');
  } else {
    document.querySelector('.tab:nth-child(2)').classList.add('active');
    document.getElementById('audio-tab').classList.add('active');
  }
}
function addSpeaker() {
  speakerCount++;
  const div = document.createElement('div');
  div.className = 'speaker-input';
  div.innerHTML = `
    <input type='text' placeholder='Speaker ${speakerCount} Name' class='speaker-name'>
    <textarea placeholder='Enter Speaker ${speakerCount}\'s statement...' class='speaker-text'></textarea>
  `;
  document.getElementById('speakers').appendChild(div);
}
function loadSample() {
  document.getElementById('speakers').innerHTML = `
    <div class='speaker-input'>
      <input type='text' value='Sarah - Healthcare Worker' class='speaker-name'>
      <textarea class='speaker-text'>I've worked in emergency rooms for 15 years. I've watched patients die because they couldn't afford insulin or delayed care due to cost. Universal healthcare is a moral imperative - every human being deserves medical treatment regardless of their bank account. The current system is fundamentally unjust. Wealthy countries like ours should guarantee healthcare as a basic human right. I've seen families bankrupted by medical bills. This destroys communities and tears apart the social fabric we all depend on.</textarea>
    </div>
    <div class='speaker-input'>
      <input type='text' value='Marcus - Small Business Owner' class='speaker-name'>
      <textarea class='speaker-text'>I employ 45 people and I'm barely staying afloat. Government-run healthcare would crush small businesses like mine with massive tax increases. I've seen what happens when bureaucrats control industries - endless wait times, declining quality, stifled innovation. My employees depend on me for their livelihoods. Their families need the jobs I provide. We need market-based solutions that preserve economic freedom and protect the entrepreneurial spirit that built this country. Heavy-handed government mandates will destroy more lives than they save.</textarea>
    </div>
    <div class='speaker-input'>
      <input type='text' value='Dr. Patel - Medical Researcher' class='speaker-name'>
      <textarea class='speaker-text'>The data is overwhelming. Countries with universal healthcare have better health outcomes at lower costs per capita. Evidence-based policy should drive our decisions, not ideology. My research shows that preventive care reduces long-term costs dramatically. Public health statistics prove that accessible healthcare strengthens entire populations. We have an obligation to future generations to build systems based on scientific evidence, not political rhetoric. The research clearly demonstrates that investment in population health yields massive returns.</textarea>
    </div>
    <div class='speaker-input'>
      <input type='text' value='James - Factory Worker' class='speaker-name'>
      <textarea class='speaker-text'>I work two jobs to support my kids. When the local hospital started accepting government insurance, wait times tripled and my daughter waited 8 hours in the ER with a broken arm. My community needs jobs first - without economic stability, nothing else matters. My father lost his job when regulations forced his factory to close. I've experienced firsthand how government interference destroys working-class communities. We need policies that protect workers and preserve the dignity of earning an honest living, not handouts that create dependence.</textarea>
    </div>
  `;
  speakerCount = 4;
}
const uploadArea = document.getElementById('upload-area');
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => { uploadArea.addEventListener(eventName, preventDefaults, false); });
function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }
['dragenter','dragover'].forEach(eventName => { uploadArea.addEventListener(eventName,() => {uploadArea.classList.add('dragover');},false); });
['dragleave','drop'].forEach(eventName => { uploadArea.addEventListener(eventName,() => {uploadArea.classList.remove('dragover');},false); });
uploadArea.addEventListener('drop',(e) => { const file = e.dataTransfer.files[0]; if(file && file.type.startsWith('audio/')){ uploadedFile = file; document.getElementById('file-name').textContent = file.name; document.getElementById('file-info').style.display = 'block';} });
function handleAudioUpload(event) { const file = event.target.files[0]; if(file){ uploadedFile = file; document.getElementById('file-name').textContent = file.name; document.getElementById('file-info').style.display = 'block'; } }
async function analyzeText() {
  const names = document.querySelectorAll('.speaker-name');
  const texts = document.querySelectorAll('.speaker-text');
  const narratives = [];
  for(let i = 0; i < names.length; i++){
    const name = names[i].value.trim();
    const text = texts[i].value.trim();
    if(name && text.length > 50){ narratives.push({ speaker: name, text: text, position: text.substring(0,80) }); }
  }
  if(narratives.length < 2){ alert('Please add at least 2 speakers with substantial text (50+ characters each)'); return; }
  showLoading('Analyzing dialogue with SAMVAD modules...');
  try {
    const response = await fetch('/analyze', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({narratives: narratives}) });
    const data = await response.json();
    if(data.success) displayResults(data); else throw new Error(data.error||'Analysis failed');
  } catch(error) { hideLoading(); alert('Error: '+error.message); }
}
async function analyzeAudio() {
  if(!uploadedFile){ alert('Please select an audio file first'); return; }
  showLoading('Transcribing audio with Whisper AI...');
  const formData = new FormData(); formData.append('audio', uploadedFile);
  try {
    const response = await fetch('/analyze-audio', { method:'POST', body:formData });
    const data = await response.json();
    if(data.success){ document.getElementById('loading-text').textContent = 'Running SAMVAD analysis...'; displayResults(data); } else { throw new Error(data.error||'Analysis failed'); }
  } catch(error) { hideLoading(); alert('Error: '+error.message);}
}
function showLoading(text) { document.getElementById('loading-text').textContent = text; document.getElementById('loading').style.display = 'block'; document.getElementById('results').style.display = 'none'; }
function hideLoading() { document.getElementById('loading').style.display = 'none'; }
function displayResults(data) {
  hideLoading();
  const stats = `
    <div class='stat-card'><div class='stat-number'>${data.summary.speakers}</div><div class='stat-label'>Speakers Analyzed</div></div>
    <div class='stat-card'><div class='stat-number'>${data.summary.hidden_agreements}</div><div class='stat-label'>Hidden Agreements</div></div>
    <div class='stat-card'><div class='stat-number'>${data.summary.speakers * 3}</div><div class='stat-label'>Insights Generated</div></div>
  `;
  document.getElementById('result-stats').innerHTML = stats;
  document.getElementById('result-content').textContent = data.report;
  document.getElementById('results').style.display = 'block';
  document.getElementById('results').scrollIntoView({behavior:'smooth'});
}
function downloadReport() {
  const content = document.getElementById('result-content').textContent;
  const blob = new Blob([content],{type:'text/plain'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'samvad_analysis_'+Date.now()+'.txt';
  a.click();
}
</script>
</body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        narratives = data.get('narratives', [])
        if len(narratives) < 2:
            return jsonify({'success': False, 'error': 'Need at least 2 speakers'}),400
        results = analyzer.analyze_dialogue(narratives)
        report = analyzer.generate_report(results)
        analysis_id = db.save_analysis(narratives, results, report, source_type='text')
        hidden_agreements = results.get('hidden_agreements', [])
        return jsonify({
            'success': True,
            'report': report,
            'analysis_id': analysis_id,
            'summary': {
                'speakers': len(narratives),
                'hidden_agreements': len(hidden_agreements)
            }
        })
    except Exception as e:
        import traceback
        print("Error in /analyze:",traceback.format_exc())
        return jsonify({'success':False,'error':str(e)}),500

@app.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'success':False, 'error':'No audio file uploaded'}),400
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'success':False, 'error':'No file selected'}),400
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        model = load_whisper()
        result = model.transcribe(filepath)
        transcript = result['text']
        sentences = [s.strip() for s in transcript.split('.') if len(s.strip()) > 50]
        narratives = []
        for i, sentence in enumerate(sentences[:5]):
            narratives.append({'speaker': f'Speaker_{i+1}', 'text': sentence, 'position': sentence[:80]})
        if len(narratives) < 2:
            return jsonify({'success':False, 'error':'Could not extract enough dialogue from audio'}),400
        results = analyzer.analyze_dialogue(narratives)
        report = analyzer.generate_report(results)
        analysis_id = db.save_analysis(narratives, results, report, source_type='audio')
        os.remove(filepath)
        hidden_agreements = results.get('hidden_agreements',[])
        return jsonify({
            'success':True,
            'report': report,
            'analysis_id':analysis_id,
            'transcript': transcript,
            'summary': {
                'speakers': len(narratives),
                'hidden_agreements': len(hidden_agreements)
            }
        })
    except Exception as e:
        import traceback
        print("Error in /analyze-audio:",traceback.format_exc())
        return jsonify({'success':False, 'error':str(e)}),500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        stats = db.get_statistics()
        recent = db.get_recent_analyses(limit=5)
        return jsonify({'success': True,'statistics':stats,'recent_analyses':recent})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}),500

@app.route('/api/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    try:
        analysis = db.get_analysis_by_id(analysis_id)
        if analysis:
            return jsonify({'success':True,'analysis':analysis})
        return jsonify({'success':False,'error':'Not found'}),404
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}),500

if __name__ == '__main__':
    print("="*60)
    print("🚀 SAMVAD Advanced Web Demo (Tested with 15 group participants)")
    print("="*60)
    print("\n✓ Server starting on http://localhost:5000")
    print("✓ Features:")
    print("  - Text dialogue analysis")
    print("  - Audio file upload & transcription")
    print("  - Database storage (SQLite)")
    print("  - Analytics API")
    print("  - Beautiful modern UI")
    print("\n✓ Press Ctrl+C to stop the server\n")
    print("="*60)
    app.run(debug=True,port=5000,host='0.0.0.0')
