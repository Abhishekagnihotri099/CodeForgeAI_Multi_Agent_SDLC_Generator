# Streamlit App 
import sys
from pathlib import Path

# Added parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from orchestrator.pipeline import run_pipeline
from core.logging_config import setup_logging
import re
import json
import zipfile
import io
from datetime import datetime
import time

st.set_page_config(
    page_title="CodeForge AI - Multi-Agent SDLC Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(120deg, #2563eb, #7c3aed);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(120deg, #1d4ed8, #6d28d9);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    .metric-card {
        background: #f9fafb;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
    }
    .success-box {
        background: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: #eff6ff;
        border: 1px solid #3b82f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar 
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.markdown("### ⚙️ Configuration")
    
    # Templates
    st.markdown("#### 📋 Quick Templates")
    template = st.selectbox(
        "Choose a template",
        ["Custom", "REST API", "Microservice", "CLI Tool", "Data Pipeline", "Web Scraper", "Authentication Service"]
    )
    
    template_descriptions = {
        "REST API": "Build a RESTful API with FastAPI, database integration, and authentication",
        "Microservice": "Create a microservice with Docker, message queue, and service discovery",
        "CLI Tool": "Develop a command-line tool with argument parsing and configuration management",
        "Data Pipeline": "Build an ETL pipeline with data validation and error handling",
        "Web Scraper": "Create a web scraping tool with rate limiting and data storage",
        "Authentication Service": "Build a JWT-based authentication service with user management"
    }
    
    st.markdown("#### 🎛️ Advanced Options")
    show_debug = st.checkbox("Show Debug Information", value=False)
    auto_download = st.checkbox("Auto-download ZIP on completion", value=True)
    show_tokens = st.checkbox("Show Token Usage", value=False)
    
    st.markdown("#### 📊 Session Stats")
    if 'total_projects' not in st.session_state:
        st.session_state.total_projects = 0
    if 'total_files' not in st.session_state:
        st.session_state.total_files = 0
    
    st.metric("Projects Generated", st.session_state.total_projects)
    st.metric("Total Files Created", st.session_state.total_files)
    
    st.markdown("---")
    st.markdown("#### ℹ️ About")
    st.markdown("""
    **Multi-Agent SDLC Generator**
    
    Version: 1.0  
    Powered by: Llama & Groq 
    Framework: AutoGen
    
    🔗 [Documentation](#)  
    🐛 [Report Issue](#)
    """)


st.markdown('<h1 class="main-header">🤖 CodeForge AI - Multi-Agent SDLC Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transform your ideas into production-ready code with intelligent multi-agent collaboration</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("### 📝")
    st.markdown("**Requirements**\nAutomated analysis")
with col2:
    st.markdown("### 🏗️")
    st.markdown("**Architecture**\nSmart design")
with col3:
    st.markdown("### 💻")
    st.markdown("**Code & Tests**\nProduction-ready")
with col4:
    st.markdown("### 🚀")
    st.markdown("**Deployment**\nDocker configs")

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    # Project name input
    project_name = st.text_input(
        "🏷️ Project Name", 
        value="my_awesome_project",
        help="Enter a unique name for your project",
        placeholder="e.g., jwt_auth_api"
    )

with col2:
    # Language/Framework selector
    language = st.selectbox(
        "🔧 Primary Language",
        ["Python", "JavaScript (Coming Soon)", "Java (Coming Soon)"],
        disabled=True,
        index=0
    )

if template != "Custom" and template in template_descriptions:
    default_desc = template_descriptions[template]
else:
    default_desc = ""

req = st.text_area(
    "📄 Project Description",
    height=180,
    placeholder="Describe your project in detail. Be specific about features, technologies, and requirements...",
    value=default_desc,
    help="The more detailed your description, the better the generated code will be"
)

if req:
    st.caption(f"✍️ Characters: {len(req)} | Words: {len(req.split())}")

sanitized_project_name = re.sub(r'[^a-zA-Z0-9_-]', '_', project_name)

col1, col2= st.columns([2, 1])
with col1:
    generate_button = st.button("🚀 Generate Full Project", type="primary", use_container_width=True)
with col2:
    if st.button("🔄 Reset", use_container_width=True):
        st.rerun()

# Main Logic
if generate_button:
    if not req.strip():
        st.error("⚠️ Please provide a project description")
        st.stop()
    
    if not sanitized_project_name.strip():
        st.error("⚠️ Please provide a valid project name")
        st.stop()
    
    start_time = time.time()
    
    # Initialize logging 
    log_file = setup_logging(sanitized_project_name)
    
    # Progress Container
    progress_container = st.container()
    with progress_container:
        st.markdown("### 🔄 Generation in Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Stage indicators
        stages = ["Requirements", "Architecture", "Code Generation", "Testing", "Documentation", "Deployment"]
        stage_cols = st.columns(6)
        stage_indicators = []
        for i, col in enumerate(stage_cols):
            with col:
                stage_indicators.append(st.empty())
                stage_indicators[i].markdown(f"⏳ {stages[i]}")
        
        # Simulate progress 
        def update_stage(stage_idx, status="done"):
            emoji = "✅" if status == "done" else "⏳" if status == "active" else "⚪"
            stage_indicators[stage_idx].markdown(f"{emoji} {stages[stage_idx]}")
            progress_bar.progress((stage_idx + 1) / len(stages))
        
        status_text.info(f"📝 Logging to: {Path(log_file).name}")
        
        # Run Pipeline
        try:
            with st.spinner("🤖 AI agents are collaborating on your project..."):
                for i in range(len(stages)):
                    update_stage(i, "active")
                    time.sleep(0.1)  
                    if i < len(stages) - 1:
                        update_stage(i, "done")
                
                out = run_pipeline(req, sanitized_project_name)
                update_stage(len(stages) - 1, "done")
            
            elapsed_time = time.time() - start_time
            
            if "error" in out:
                st.error(f"❌ Generation Failed: {out['error']}")
                with st.expander("🔍 View Error Details"):
                    st.code(out.get('_exception', 'No additional details available'))
                    st.info(f"💡 Check log file for more information: {log_file}")
                st.stop()
            
            st.session_state.total_projects += 1
            if "save_stats" in out:
                st.session_state.total_files += sum([
                    out["save_stats"]["code"]["saved_count"],
                    out["save_stats"]["tests"]["saved_count"],
                    out["save_stats"]["docs"]["saved_count"],
                    out["save_stats"]["deploy"]["saved_count"]
                ])
            
            st.balloons()
            st.success(f"✅ Project Generated Successfully in {elapsed_time:.2f}s!")
            
            st.markdown("### 📊 Generation Statistics")
            metric_cols = st.columns(5)
            
            with metric_cols[0]:
                total_files = sum([
                    out["save_stats"]["code"]["saved_count"],
                    out["save_stats"]["tests"]["saved_count"],
                    out["save_stats"]["docs"]["saved_count"],
                    out["save_stats"]["deploy"]["saved_count"]
                ])
                st.metric("Total Files", total_files, delta="Generated")
            
            with metric_cols[1]:
                st.metric("Code Files", out["save_stats"]["code"]["saved_count"])
            
            with metric_cols[2]:
                st.metric("Test Files", out["save_stats"]["tests"]["saved_count"])
            
            with metric_cols[3]:
                st.metric("Docs", out["save_stats"]["docs"]["saved_count"])
            
            with metric_cols[4]:
                st.metric("Deploy Configs", out["save_stats"]["deploy"]["saved_count"])
            
            # Project Location
            project_dir = out["save_stats"]["code"].get("target_directory", "").replace("\\src", "").replace("/src", "")
            st.info(f"📂 **Project Location:** `{project_dir}`")
            
            # Download Section
            st.markdown("### 💾 Download Options")
            dl_col1, dl_col2, dl_col3 = st.columns(3)
            
            with dl_col1:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add code files
                    for f in out["code"]["files"]:
                        zip_file.writestr(f"src/{f['path']}", f['content'])
                    # Add test files
                    for t in out["tests"]["tests"]:
                        zip_file.writestr(f"tests/{t['path']}", t['content'])
                    # Add docs
                    for d in out["docs"]["docs"]:
                        zip_file.writestr(f"docs/{d['path']}", d['content'])
                    # Add deploy files
                    for dep in out["deploy"]["deploy"]:
                        zip_file.writestr(f"deploy/{dep['path']}", dep['content'])
                
                st.download_button(
                    label="📦 Download Complete Project (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{sanitized_project_name}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            
            with dl_col2:
                # Download requirements as JSON
                requirements_json = json.dumps(out["requirements"], indent=2)
                st.download_button(
                    label="📋 Download Requirements (JSON)",
                    data=requirements_json,
                    file_name=f"{sanitized_project_name}_requirements.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with dl_col3:
                # Download architecture as JSON
                architecture_json = json.dumps(out["architecture"], indent=2)
                st.download_button(
                    label="🏗️ Download Architecture (JSON)",
                    data=architecture_json,
                    file_name=f"{sanitized_project_name}_architecture.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # View Log File
            if show_debug:
                with st.expander("🔍 View Log File"):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            log_content = f.read()
                        st.code(log_content, language='log')
                    except Exception as e:
                        st.error(f"Could not read log file: {e}")
            
            st.markdown("---")
            
            st.markdown("### 📄 Generated Artifacts")
            tabs = st.tabs([
                "📝 Requirements", 
                "🏗️ Architecture", 
                "💻 Source Code", 
                "🧪 Tests", 
                "📚 Documentation", 
                "🚀 Deployment"
            ])
            
            with tabs[0]:
                st.markdown("#### Functional Requirements")
                for idx, req_item in enumerate(out["requirements"].get("functional_requirements", []), 1):
                    st.markdown(f"{idx}. {req_item}")
                
                st.markdown("#### Non-Functional Requirements")
                for idx, req_item in enumerate(out["requirements"].get("non_functional_requirements", []), 1):
                    st.markdown(f"{idx}. {req_item}")
                
                st.markdown("#### Constraints")
                for idx, constraint in enumerate(out["requirements"].get("constraints", []), 1):
                    st.markdown(f"{idx}. {constraint}")
                
                with st.expander("📊 View Raw JSON"):
                    st.json(out["requirements"])
            
            with tabs[1]:
                st.markdown("#### System Components")
                components = out["architecture"].get("components", [])
                if components:
                    for idx, comp in enumerate(components, 1):
                        if isinstance(comp, dict):
                            with st.expander(f"Component {idx}: {comp.get('name', 'Unnamed')}"):
                                st.markdown(f"**Purpose:** {comp.get('purpose', 'N/A')}")
                                st.markdown(f"**Technology:** {comp.get('technology', 'N/A')}")
                                if comp.get('description'):
                                    st.markdown(f"**Description:** {comp.get('description')}")
                        else:
                            st.markdown(f"{idx}. {comp}")
                else:
                    st.info("No components defined")
                
                st.markdown("#### Data Models")
                data_models = out["architecture"].get("data_models", [])
                if data_models:
                    for idx, model in enumerate(data_models, 1):
                        if isinstance(model, dict):
                            model_name = model.get('name', f'Model {idx}')
                            with st.expander(f"📊 {model_name}"):
                                st.json(model)
                        else:
                            st.markdown(f"{idx}. {model}")
                else:
                    st.info("No data models defined")
                
                st.markdown("#### APIs")
                apis = out["architecture"].get("apis", [])
                if apis:
                    for idx, api in enumerate(apis, 1):
                        if isinstance(api, dict):
                            st.markdown(f"**{idx}. {api.get('endpoint', 'API')}**")
                            st.markdown(f"- Method: {api.get('method', 'N/A')}")
                            st.markdown(f"- Description: {api.get('description', 'N/A')}")
                        else:
                            st.markdown(f"{idx}. {api}")
                
                with st.expander("📊 View Complete Architecture"):
                    st.json(out["architecture"])
            
            with tabs[2]:
                st.markdown(f"#### Generated {len(out['code']['files'])} Source Files")
                for idx, f in enumerate(out["code"]["files"], 1):
                    with st.expander(f"📄 {f['path']} ({len(f['content'])} chars)"):
                        st.code(f["content"], language="python", line_numbers=True)
                        
                        # Download individual file
                        st.download_button(
                            label=f"💾 Download {f['path']}",
                            data=f['content'],
                            file_name=f['path'],
                            mime="text/plain",
                            key=f"download_code_{idx}"
                        )
            
            with tabs[3]:
                st.markdown(f"#### Generated {len(out['tests']['tests'])} Test Files")
                for idx, t in enumerate(out["tests"]["tests"], 1):
                    with st.expander(f"🧪 {t['path']} ({len(t['content'])} chars)"):
                        st.code(t["content"], language="python", line_numbers=True)
                        
                        st.download_button(
                            label=f"💾 Download {t['path']}",
                            data=t['content'],
                            file_name=t['path'],
                            mime="text/plain",
                            key=f"download_test_{idx}"
                        )
            
            with tabs[4]:
                st.markdown(f"#### Generated {len(out['docs']['docs'])} Documentation Files")
                for idx, d in enumerate(out["docs"]["docs"], 1):
                    st.markdown(f"### 📄 {d['path']}")
                    st.markdown(d["content"])
                    st.markdown("---")
                    
                    st.download_button(
                        label=f"💾 Download {d['path']}",
                        data=d['content'],
                        file_name=d['path'],
                        mime="text/markdown",
                        key=f"download_doc_{idx}"
                    )
            
            with tabs[5]:
                st.markdown(f"#### Generated {len(out['deploy']['deploy'])} Deployment Files")
                for idx, dep in enumerate(out["deploy"]["deploy"], 1):
                    with st.expander(f"🚀 {dep['path']}"):
                        st.code(dep["content"], language="dockerfile" if "Dockerfile" in dep['path'] else "yaml")
                        
                        st.download_button(
                            label=f"💾 Download {dep['path']}",
                            data=dep['content'],
                            file_name=dep['path'],
                            mime="text/plain",
                            key=f"download_deploy_{idx}"
                        )
        
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            with st.expander("🔍 View Full Error"):
                st.exception(e)
            st.info(f"💡 Check log file: {log_file}")

# Footer
st.markdown("---")
footer_cols = st.columns([2, 1, 1])
with footer_cols[0]:
    st.markdown("**Multi-Agent SDLC Generator** | Powered by AI")
with footer_cols[1]:
    st.markdown("🔗 [Documentation](https://github.com)")
with footer_cols[2]:
    st.markdown(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")

