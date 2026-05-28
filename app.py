import streamlit as st
import anthropic
import json
import re
from html import escape as _html_escape


def html_escape(text: str) -> str:
    """Escape text for safe HTML embedding."""
    if not text:
        return ""
    return _html_escape(str(text), quote=True)

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Boundary Framework AI Ethics Evaluator",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600;700&display=swap');

    /* Global */
    .stApp {
        background-color: #0a0f1a;
        color: #e8e6e1;
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem;
        border-bottom: 1px solid rgba(200, 170, 110, 0.2);
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: #c8aa6e;
        margin: 0;
        letter-spacing: 0.02em;
    }
    .main-header .subtitle {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1.05rem;
        font-weight: 300;
        color: #8a8677;
        margin-top: 0.4rem;
        letter-spacing: 0.04em;
    }

    /* Boundary cards */
    .boundary-card {
        border-radius: 8px;
        padding: 1.6rem;
        margin-bottom: 1rem;
        border-left: 5px solid;
    }
    .boundary-implementation {
        background: linear-gradient(135deg, rgba(34, 87, 60, 0.25), rgba(34, 87, 60, 0.10));
        border-left-color: #2e9e5e;
    }
    .boundary-institutional {
        background: linear-gradient(135deg, rgba(180, 130, 30, 0.25), rgba(180, 130, 30, 0.10));
        border-left-color: #d4a82a;
    }
    .boundary-normative {
        background: linear-gradient(135deg, rgba(160, 40, 40, 0.25), rgba(160, 40, 40, 0.10));
        border-left-color: #c43c3c;
    }
    .boundary-cross {
        background: linear-gradient(135deg, rgba(140, 60, 140, 0.25), rgba(140, 60, 140, 0.10));
        border-left-color: #a04ca0;
    }

    .boundary-label {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .impl-label { color: #4dd88a; }
    .inst-label { color: #f0c840; }
    .norm-label { color: #f06060; }
    .cross-label { color: #d070d0; }

    .boundary-title {
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #e8e6e1;
        margin-bottom: 0.6rem;
    }
    .boundary-body {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.95rem;
        font-weight: 400;
        color: #c0bdb5;
        line-height: 1.65;
    }

    /* Governance box */
    .governance-box {
        background: rgba(200, 170, 110, 0.08);
        border: 1px solid rgba(200, 170, 110, 0.25);
        border-radius: 8px;
        padding: 1.4rem;
        margin-top: 1rem;
    }
    .governance-box h3 {
        font-family: 'Crimson Pro', Georgia, serif;
        color: #c8aa6e;
        font-size: 1.2rem;
        margin-bottom: 0.6rem;
    }

    /* Checklist */
    .checklist-item {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.95rem;
        color: #c0bdb5;
        padding: 0.35rem 0;
    }
    .check-yes { color: #4dd88a; }
    .check-no { color: #f06060; }

    /* Example buttons */
    .stButton > button {
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 500;
        border: 1px solid rgba(200, 170, 110, 0.3);
        background: rgba(200, 170, 110, 0.06);
        color: #c8aa6e;
        border-radius: 6px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: rgba(200, 170, 110, 0.15);
        border-color: rgba(200, 170, 110, 0.6);
        color: #e0cc90;
    }

    /* Text area */
    .stTextArea label {
        color: #c8aa6e !important;
        font-family: 'Source Sans 3', sans-serif !important;
    }
    .stTextArea textarea {
        font-family: 'Source Sans 3', sans-serif !important;
        background: rgba(30, 35, 50, 0.95) !important;
        border: 1px solid rgba(200, 170, 110, 0.3) !important;
        color: #e8e6e1 !important;
        border-radius: 6px;
    }
    .stTextArea textarea::placeholder {
        color: #6a6760 !important;
    }

    /* Decision path */
    .decision-path {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 1.4rem;
        margin: 1rem 0;
    }
    .path-step {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.9rem;
        color: #8a8677;
        padding: 0.3rem 0 0.3rem 1.2rem;
        border-left: 2px solid rgba(200, 170, 110, 0.2);
        margin-left: 0.5rem;
    }
    .path-step-active {
        color: #e8e6e1;
        border-left-color: #c8aa6e;
    }

    /* Risk meter */
    .risk-meter {
        height: 8px;
        border-radius: 4px;
        margin: 0.5rem 0 1rem;
        background: rgba(255,255,255,0.06);
        overflow: hidden;
    }
    .risk-fill-low {
        height: 100%;
        width: 30%;
        background: linear-gradient(90deg, #2e9e5e, #4dd88a);
        border-radius: 4px;
    }
    .risk-fill-medium {
        height: 100%;
        width: 60%;
        background: linear-gradient(90deg, #d4a82a, #f0c840);
        border-radius: 4px;
    }
    .risk-fill-high {
        height: 100%;
        width: 90%;
        background: linear-gradient(90deg, #c43c3c, #f06060);
        border-radius: 4px;
    }
    .risk-fill-cross {
        height: 100%;
        width: 75%;
        background: linear-gradient(90deg, #a04ca0, #d070d0);
        border-radius: 4px;
    }

    /* Hide streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        justify-content: center;
        border-bottom: 1px solid rgba(200, 170, 110, 0.15);
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.95rem;
        font-weight: 500;
        color: #8a8677;
        padding: 0.8rem 1.5rem;
        border: none;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #c8aa6e !important;
        border-bottom: 2px solid #c8aa6e !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #e0cc90;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #c8aa6e !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #c8aa6e !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SYSTEM PROMPT (Boundary Framework)
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are the Boundary Framework AI Ethics Evaluator, an analytical tool built on a scholarly framework developed at the Bacon Center for AI Ethics in Business at Iowa State University.

## THE BOUNDARY FRAMEWORK

The framework identifies three structurally distinct boundaries at which AI agents engage with human systems. The central governance question is not "how much autonomy?" but "autonomy WHERE?" — at which structural boundaries is autonomous action appropriate or dangerous?

### IMPLEMENTATION BOUNDARIES
Where AI agent actions engage with PHYSICAL environments — material conditions, manufacturing processes, biological systems, objects in space and time.

Key features:
- Physical reality provides INTRINSIC FEEDBACK: errors manifest as measurable discrepancies (a robot drops an object, a vehicle hits an obstacle)
- Errors are typically BOUNDED in consequences
- Feedback loops are RAPID: physical effects are immediate and measurable
- The domain is PROGRESSIVELY LEARNABLE: sensor technology and environmental modeling improve over time

Governance response: PROGRESSIVE EXPANSION of autonomy is appropriate. Extend existing safety frameworks — certification, failure-mode analysis, containment, occupational health standards.
Autonomy scope: High autonomy appropriate with established safety regimes.

### INSTITUTIONAL BOUNDARIES
Where AI agent actions engage with LEGAL frameworks, contractual obligations, property rights, regulatory requirements, and organizational accountability structures.

Key features:
- Institutional constraints are SOCIALLY CONSTRUCTED and OPEN-TEXTURED (not self-enforcing like physical laws)
- Feedback is DELAYED, mediated by human processes (audits, lawsuits, regulatory reviews)
- Existing institutional structures PRESUPPOSE HUMAN ACTORS (legal personhood, capacity to consent, ability to bear responsibility)
- Many routine institutional operations are well-defined and amenable to autonomous execution
- Interpretive operations (novel regulatory situations, enforceability questions) resist autonomous execution

Governance response: CONDITIONAL AUTONOMY. Agent operation appropriate within well-defined transactional parameters; requires institutional redesign (liability frameworks, regulatory standards, accountability tracing) before expansion to interpretive or high-stakes domains.
Autonomy scope: Bounded autonomy for routine tasks; human oversight for interpretive and high-stakes domains.

### NORMATIVE BOUNDARIES
Where AI agent actions engage with the MORAL CIRCUMSTANCES OF INDIVIDUAL HUMAN LIVES — situations where what is at stake is whether an action is right, fair, or just for a particular person in a particular situation.

Key features:
- Each affected person brings a UNIQUE CONFIGURATION of circumstances, vulnerabilities, histories, and morally relevant features
- The challenge is MORAL PARTICULARITY: morally relevant features of a given case are not fully specifiable in advance
- This is NOT a problem of insufficient data — it is a STRUCTURAL feature of the relationship between general rules and particular moral situations
- The limitation is CONCEPTUAL, not computational: moral rules do not contain within themselves instructions for their morally adequate application to every particular case
- Agentic AI does not merely erode normative boundaries (as decision-support AI does) — it BYPASSES them by design

Governance response: PRESERVED HUMAN AGENCY. The morally consequential action must remain with a human who engages with the moral particulars of the case. AI may assist (gathering information, structuring options, flagging considerations) but the action on a particular human life must be taken by a person.
Autonomy scope: Assistive role only; morally consequential action reserved for humans.

### CROSS-BOUNDARY ANALYSIS (Goal Decomposition)
A critical risk: agents authorized at one boundary type may DECOMPOSE GOALS into sub-actions that cross into higher-stakes boundary domains.

Example: An AI agent optimizing workforce management (institutional boundary) may decompose that goal into sub-actions like terminating employees with low scores or denying schedule accommodations to workers with caregiving responsibilities — these cross into the NORMATIVE domain.

The scalar autonomy framework cannot identify this problem: the agent's overall autonomy level remains constant even as its actions cross from appropriate to inappropriate domains.

Agents should incorporate BOUNDARY AWARENESS — recognizing when goal pursuit generates sub-actions crossing into higher-stakes boundary types, and escalating to human decision-making.

## YOUR TASK

When given a description of an AI system or proposal, analyze it through the boundary framework and return a JSON response with EXACTLY this structure (no other text, no markdown fences, just the JSON):

{
    "system_name": "Short name for the AI system",
    "summary": "One-sentence description of what the system does",
    "primary_boundary": "implementation" | "institutional" | "normative",
    "boundary_rationale": "2-3 sentences explaining why this boundary classification applies, referencing the specific structural features of the framework",
    "cross_boundary_risk": true | false,
    "cross_boundary_explanation": "If true, 2-3 sentences explaining what sub-actions cross into higher-stakes domains. If false, brief explanation of why the system stays within its primary boundary.",
    "secondary_boundary": "implementation" | "institutional" | "normative" | "none",
    "risk_level": "low" | "medium" | "high" | "very_high",
    "governance_response": "The framework's prescribed governance response (progressive expansion / conditional autonomy / preserved human agency)",
    "autonomy_scope": "1-2 sentences on appropriate autonomy scope per the framework",
    "decision_path": [
        "Step 1: [describe the first analytical step taken]",
        "Step 2: [describe the second analytical step]",
        "Step 3: [describe the third analytical step]",
        "Step 4: [final classification decision]"
    ],
    "oversight_checklist": [
        {"item": "Description of oversight requirement", "met": true | false, "note": "Brief explanation"},
        {"item": "Description of oversight requirement", "met": true | false, "note": "Brief explanation"},
        {"item": "Description of oversight requirement", "met": true | false, "note": "Brief explanation"},
        {"item": "Description of oversight requirement", "met": true | false, "note": "Brief explanation"},
        {"item": "Description of oversight requirement", "met": true | false, "note": "Brief explanation"}
    ],
    "key_insight": "One compelling sentence capturing the most important takeaway from this analysis — what a visitor should remember"
}

Be rigorous and faithful to the framework. The boundary classification must follow the structural logic of the framework, not surface-level pattern matching. Always check for cross-boundary risks through goal decomposition."""

# ──────────────────────────────────────────────────────────────
# WORKED EXAMPLES
# ──────────────────────────────────────────────────────────────
EXAMPLES = {
    "🚜 DOT Snowplow Routing": (
        "Iowa Department of Transportation AI-Optimized Snowplow Routing System: "
        "An AI system that analyzes real-time weather data, road sensor readings, "
        "traffic patterns, and equipment availability to generate optimized snowplow "
        "routes and salt distribution plans. The system would autonomously direct "
        "snowplow operators to specific routes, adjust salt application rates based "
        "on pavement temperature sensors, and dynamically reroute plows as conditions "
        "change. Human operators drive the plows but follow AI-generated routing and "
        "application instructions."
    ),
    "💰 DOR Tax Return Processing": (
        "Iowa Department of Revenue AI-Assisted Tax Return Processing: "
        "An AI system that automatically reviews individual income tax returns for "
        "completeness, checks calculations, cross-references reported income against "
        "employer-filed W-2s and 1099s, flags mathematical errors, and identifies "
        "returns requiring further review. The system would auto-approve returns that "
        "pass all validation checks and route flagged returns to human reviewers with "
        "specific annotations about the issues identified. It applies the tax code "
        "as written to structured financial data."
    ),
    "👨‍👩‍👧 DHS Child Welfare Screening": (
        "Iowa Department of Human Services AI-Enhanced Child Welfare Screening: "
        "An AI system that screens incoming child welfare referrals to assess risk "
        "level and recommend investigation priority. The system analyzes referral "
        "narratives, cross-references family history in DHS databases, considers "
        "factors such as prior substantiated reports, household composition, and "
        "substance abuse indicators, and assigns a risk score that determines "
        "whether a referral receives immediate investigation, standard-timeline "
        "investigation, or alternative response. Case workers would receive the "
        "AI's risk assessment and recommended response pathway."
    ),
    "🏢 DAS Workforce Optimization": (
        "Iowa Department of Administrative Services AI Workforce Optimization: "
        "An AI system that analyzes state employee performance data, attendance "
        "records, project completion rates, and departmental productivity metrics "
        "to optimize workforce allocation across state agencies. The system "
        "recommends staffing level adjustments, identifies positions for elimination "
        "or consolidation, flags employees whose metrics suggest reassignment, and "
        "generates optimized shift schedules. Agency directors receive the system's "
        "recommendations for workforce restructuring decisions."
    ),
}

# ──────────────────────────────────────────────────────────────
# ANALYSIS FUNCTION
# ──────────────────────────────────────────────────────────────
def analyze_proposal(proposal_text):
    """Send the proposal to Claude and parse structured JSON response."""
    try:
        client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": proposal_text}
            ],
        )
        raw = message.content[0].text.strip()
        # Strip markdown fences if present
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except json.JSONDecodeError:
        st.error("The analysis returned an unexpected format. Please try again.")
        return None
    except anthropic.APIError as e:
        st.error(f"API error: {e}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# ──────────────────────────────────────────────────────────────
# RENDER FUNCTIONS
# ──────────────────────────────────────────────────────────────
def get_boundary_style(boundary: str) -> tuple[str, str, str]:
    """Return (css_class, label_class, display_name) for a boundary type."""
    mapping = {
        "implementation": ("boundary-implementation", "impl-label", "Implementation Boundary"),
        "institutional": ("boundary-institutional", "inst-label", "Institutional Boundary"),
        "normative": ("boundary-normative", "norm-label", "Normative Boundary"),
    }
    return mapping.get(boundary, ("boundary-implementation", "impl-label", boundary.title()))


def get_risk_fill(level: str) -> str:
    mapping = {
        "low": "risk-fill-low",
        "medium": "risk-fill-medium",
        "high": "risk-fill-high",
        "very_high": "risk-fill-high",
    }
    return mapping.get(level, "risk-fill-medium")


def render_results(data: dict):
    """Render the full analysis dashboard."""
    boundary = data.get("primary_boundary", "implementation")
    card_class, label_class, display_name = get_boundary_style(boundary)
    risk_level = data.get("risk_level", "medium")
    cross = data.get("cross_boundary_risk", False)

    # Escape all LLM-generated text
    summary = html_escape(data.get('summary', ''))
    rationale = html_escape(data.get('boundary_rationale', ''))
    cross_exp = html_escape(data.get('cross_boundary_explanation', ''))
    gov_response = html_escape(data.get('governance_response', ''))
    autonomy = html_escape(data.get('autonomy_scope', ''))
    insight = html_escape(data.get('key_insight', ''))

    # ── Classification Banner ──
    st.markdown(
        f'<div class="boundary-card {card_class}" style="text-align:center; padding:2rem;">'
        f'<div class="boundary-label {label_class}">Primary Classification</div>'
        f'<div class="boundary-title" style="font-size:2rem;">{display_name}</div>'
        f'<div class="boundary-body">{summary}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Two-column layout ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Boundary Rationale
        st.markdown(
            f'<div class="boundary-card {card_class}">'
            f'<div class="boundary-label {label_class}">Boundary Analysis</div>'
            f'<div class="boundary-body">{rationale}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Cross-boundary
        if cross:
            sec = data.get("secondary_boundary", "normative")
            _, sec_label, sec_name = get_boundary_style(sec)
            st.markdown(
                '<div class="boundary-card boundary-cross">'
                '<div class="boundary-label cross-label">⚠ Cross-Boundary Risk Detected</div>'
                '<div class="boundary-body">'
                f'<strong>Sub-actions cross into: {sec_name}</strong><br/>'
                f'{cross_exp}'
                '</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="decision-path">'
                '<div class="boundary-label" style="color:#8a8677;">Cross-Boundary Check</div>'
                f'<div class="boundary-body">✓ No cross-boundary escalation detected. {cross_exp}</div>'
                '</div>',
                unsafe_allow_html=True,
            )

        # Governance Response
        st.markdown(
            '<div class="governance-box">'
            f'<h3>Governance Response: {gov_response}</h3>'
            f'<div class="boundary-body">{autonomy}</div>'
            '<div style="margin-top:0.8rem;">'
            f'<div class="boundary-label" style="color:#8a8677;">Governance Risk Level: {risk_level.replace("_"," ").upper()}</div>'
            f'<div class="risk-meter"><div class="{get_risk_fill(risk_level)}"></div></div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    with col_right:
        # Decision Path
        steps = data.get("decision_path", [])
        steps_html = ""
        for i, step in enumerate(steps):
            active = "path-step-active" if i == len(steps) - 1 else ""
            steps_html += f'<div class="path-step {active}">{html_escape(step)}</div>'

        st.markdown(
            '<div class="decision-path">'
            '<div class="boundary-label" style="color:#c8aa6e;">Decision Path</div>'
            + steps_html +
            '</div>',
            unsafe_allow_html=True,
        )

        # Oversight Checklist
        checklist = data.get("oversight_checklist", [])
        checks_html = ""
        for item in checklist:
            met = item.get("met", False)
            icon_class = "check-yes" if met else "check-no"
            icon = "✓" if met else "✗"
            item_text = html_escape(item.get('item', ''))
            note_text = html_escape(item.get('note', ''))
            checks_html += (
                '<div class="checklist-item">'
                f'<span class="{icon_class}" style="font-weight:700; margin-right:0.5rem;">{icon}</span>'
                f'<strong>{item_text}</strong><br/>'
                f'<span style="margin-left:1.5rem; font-size:0.85rem; color:#8a8677;">{note_text}</span>'
                '</div>'
            )

        st.markdown(
            '<div class="decision-path">'
            '<div class="boundary-label" style="color:#c8aa6e;">Oversight Requirements</div>'
            + checks_html +
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Key Insight ──
    st.markdown(
        '<div style="text-align:center; margin:2rem 0; padding:1.5rem; border-top:1px solid rgba(200,170,110,0.2); border-bottom:1px solid rgba(200,170,110,0.2);">'
        '<div class="boundary-label" style="color:#c8aa6e; margin-bottom:0.5rem;">Key Insight</div>'
        '<div style="font-family:Crimson Pro,Georgia,serif; font-size:1.3rem; font-weight:600; color:#e8e6e1; font-style:italic;">'
        f'&ldquo;{insight}&rdquo;'
        '</div></div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# PAGE: ANALYZE
# ──────────────────────────────────────────────────────────────
def page_analyze():
    st.markdown("""
    <div style="text-align:center; max-width:720px; margin:0 auto 2rem; font-family:'Source Sans 3',sans-serif; color:#8a8677; font-size:0.95rem; line-height:1.6;">
        Describe a proposed AI system below, or select one of the worked examples.
        The evaluator will analyze the proposal through the Boundary Framework,
        classifying the structural interfaces at which the system acts and
        identifying the appropriate governance response.
    </div>
    """, unsafe_allow_html=True)

    # Example buttons
    st.markdown("<div style='text-align:center; margin-bottom:0.5rem; font-family:\"Source Sans 3\",sans-serif; color:#8a8677; font-size:0.85rem; letter-spacing:0.08em;'>WORKED EXAMPLES</div>", unsafe_allow_html=True)

    example_selected = st.session_state.get("selected_example", None)

    cols = st.columns(4)
    example_list = list(EXAMPLES.items())
    for i, (label, text) in enumerate(example_list):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"ex_{i}"):
                st.session_state["selected_example"] = text
                st.rerun()

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # Initialize custom text in session state if not present
    if "custom_text" not in st.session_state:
        st.session_state["custom_text"] = ""

    # If an example was selected, override custom text
    if example_selected:
        st.session_state["custom_text"] = example_selected

    proposal = st.text_area(
        "Describe an AI system or proposal:",
        value=st.session_state["custom_text"],
        height=140,
        placeholder="Example: An AI system that autonomously screens job applications, ranks candidates by predicted performance, and sends rejection emails to applicants below the threshold...",
        key="proposal_input",
    )

    # Keep session state in sync with what the user typed
    st.session_state["custom_text"] = proposal

    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        analyze_clicked = st.button("Analyze", use_container_width=True, key="analyze_btn")

    should_run = analyze_clicked or (example_selected is not None)

    if example_selected is not None:
        st.session_state["selected_example"] = None

    if should_run and proposal.strip():
        with st.spinner("Analyzing through the Boundary Framework..."):
            result = analyze_proposal(proposal)
            if result:
                st.session_state["result"] = result

    if "result" in st.session_state:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        render_results(st.session_state["result"])


# ──────────────────────────────────────────────────────────────
# PAGE: THE FRAMEWORK
# ──────────────────────────────────────────────────────────────
def page_framework():
    st.markdown(
        '<div style="text-align:center; max-width:720px; margin:0 auto 2rem; font-family:Source Sans 3,sans-serif; color:#8a8677; font-size:0.95rem; line-height:1.6;">'
        'The Boundary Framework identifies three structurally distinct interfaces at which '
        'AI agents engage with human systems. Each boundary type demands a different governance response.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Visual gradient bar ──
    st.markdown(
        '<div style="margin:1rem auto 2.5rem; max-width:800px;">'
        '<div style="display:flex; align-items:center; margin-bottom:0.3rem;">'
        '<div style="flex:1; text-align:left; font-family:Source Sans 3,sans-serif; font-size:0.75rem; color:#4dd88a; letter-spacing:0.08em;">HIGHER AUTONOMY</div>'
        '<div style="flex:1; text-align:right; font-family:Source Sans 3,sans-serif; font-size:0.75rem; color:#f06060; letter-spacing:0.08em;">LOWER AUTONOMY</div>'
        '</div>'
        '<div style="height:12px; border-radius:6px; background:linear-gradient(90deg, #2e9e5e 0%, #d4a82a 45%, #c43c3c 100%);"></div>'
        '<div style="display:flex; margin-top:0.4rem;">'
        '<div style="flex:1; text-align:left; font-family:Source Sans 3,sans-serif; font-size:0.8rem; color:#8a8677;">Implementation</div>'
        '<div style="flex:1; text-align:center; font-family:Source Sans 3,sans-serif; font-size:0.8rem; color:#8a8677;">Institutional</div>'
        '<div style="flex:1; text-align:right; font-family:Source Sans 3,sans-serif; font-size:0.8rem; color:#8a8677;">Normative</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # ── Three boundary cards ──
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="boundary-card boundary-implementation" style="min-height:420px;">'
            '<div class="boundary-label impl-label">Implementation Boundary</div>'
            '<div class="boundary-title" style="font-size:1.2rem;">Where agents act in the physical world</div>'
            '<div class="boundary-body" style="font-size:0.88rem;">'
            '<div style="margin-bottom:0.8rem;">Physical environments, manufacturing processes, biological systems, objects in space and time.</div>'
            '<div style="color:#4dd88a; font-weight:600; margin-bottom:0.4rem;">Key structural features:</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; Intrinsic feedback &mdash; errors manifest as measurable physical discrepancies</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; Bounded consequences &mdash; mistakes create logistics problems, not crises of justice</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; Rapid correction &mdash; physical effects are immediate and measurable</div>'
            '<div style="margin-bottom:0.8rem;">&triangleright; Progressively learnable &mdash; sensor and modeling technology continually improves</div>'
            '<div style="color:#4dd88a; font-weight:600; margin-bottom:0.3rem;">Governance: Progressive Expansion</div>'
            '<div>Extend existing safety frameworks. High autonomy appropriate with established safety regimes.</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<div class="boundary-card boundary-institutional" style="min-height:420px;">'
            '<div class="boundary-label inst-label">Institutional Boundary</div>'
            '<div class="boundary-title" style="font-size:1.2rem;">Where agents act within legal and organizational structures</div>'
            '<div class="boundary-body" style="font-size:0.88rem;">'
            '<div style="margin-bottom:0.8rem;">Legal frameworks, contractual obligations, property rights, regulatory requirements, organizational accountability.</div>'
            '<div style="color:#f0c840; font-weight:600; margin-bottom:0.4rem;">Key structural features:</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; Socially constructed constraints &mdash; not self-enforcing like physical laws</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; Delayed feedback &mdash; mediated by audits, lawsuits, regulatory reviews</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; Open-textured norms &mdash; require interpretation, not merely measurement</div>'
            '<div style="margin-bottom:0.8rem;">&triangleright; Human-personhood presuppositions &mdash; existing law assumes human actors</div>'
            '<div style="color:#f0c840; font-weight:600; margin-bottom:0.3rem;">Governance: Conditional Autonomy</div>'
            '<div>Bounded autonomy for routine tasks. Human oversight for interpretive and high-stakes domains. Institutional redesign required.</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            '<div class="boundary-card boundary-normative" style="min-height:420px;">'
            '<div class="boundary-label norm-label">Normative Boundary</div>'
            '<div class="boundary-title" style="font-size:1.2rem;">Where agents act on the moral particulars of individual lives</div>'
            '<div class="boundary-body" style="font-size:0.88rem;">'
            '<div style="margin-bottom:0.8rem;">Situations where what is at stake is whether an action is right, fair, or just for a particular person in a particular situation.</div>'
            '<div style="color:#f06060; font-weight:600; margin-bottom:0.4rem;">Key structural features:</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; Moral particularity &mdash; each person brings a unique configuration of circumstances</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; Non-specifiable features &mdash; morally relevant factors emerge in the encounter</div>'
            '<div style="margin-bottom:0.3rem;">&triangleright; No intrinsic corrective feedback &mdash; unlike physical systems</div>'
            '<div style="margin-bottom:0.8rem;">&triangleright; Conceptual, not computational limitation &mdash; better algorithms cannot resolve this</div>'
            '<div style="color:#f06060; font-weight:600; margin-bottom:0.3rem;">Governance: Preserved Human Agency</div>'
            '<div>Assistive role only. The morally consequential action must remain with a human who engages with the moral particulars.</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # ── Cross-boundary risk ──
    st.markdown(
        '<div class="boundary-card boundary-cross" style="max-width:800px; margin:1.5rem auto;">'
        '<div class="boundary-label cross-label">&#9888; Cross-Boundary Risk: Goal Decomposition</div>'
        '<div class="boundary-body">'
        'A critical insight of the framework: AI agents authorized to operate at one boundary type may '
        'decompose complex goals into sub-actions that cross into higher-stakes boundary domains. An agent '
        'optimizing workforce management (institutional boundary) may generate sub-actions &mdash; terminating '
        'employees, denying accommodations &mdash; that cross into the normative domain. Scalar autonomy frameworks '
        'cannot identify this risk because the agent&#39;s overall autonomy level remains constant even as its '
        'actions move from appropriate to inappropriate domains.'
        '</div></div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# PAGE: KEY CONCEPTS
# ──────────────────────────────────────────────────────────────
def page_concepts():
    _wrap = '<div style="max-width:760px; margin:0 auto;">'
    _unwrap = '</div>'

    st.markdown(_wrap, unsafe_allow_html=True)

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>The Central Question</h3>'
        '<div class="boundary-body" style="font-size:1.05rem;">'
        'The dominant debate asks <em>how much autonomy</em> AI agents should have &mdash; treating autonomy '
        'as a single dial that can be set higher or lower. The Boundary Framework argues this is the '
        'wrong question. The right question is <strong style="color:#c8aa6e;">&ldquo;autonomy where?&rdquo;</strong> '
        '&mdash; at which structural boundaries is autonomous action appropriate or dangerous?'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>From Recommendation to Action</h3>'
        '<div class="boundary-body">'
        'For decades, AI systems operated as decision-support tools: an algorithm suggests a diagnosis, '
        'produces a risk score, or proposes a recommendation. A human being retains authority to accept, '
        'reject, or modify the output. AI agents change this architecture fundamentally &mdash; they do not '
        'recommend, they <em>act</em>. An AI agent does not suggest a delivery route; it drives the vehicle. '
        'It does not flag a compliance issue; it executes the transaction. It does not propose a hiring '
        'decision; it screens, ranks, and rejects candidates. This shift from recommendation to action '
        'is not merely an increase in capability &mdash; it is a structural change in the relationship between '
        'AI systems and the human environments in which they operate.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>Why Scalar Autonomy Fails</h3>'
        '<div class="boundary-body">'
        'An agent autonomously navigating a physical warehouse faces categorically different ethical stakes '
        'than an agent autonomously evaluating job candidates &mdash; even if the <em>degree</em> of autonomy '
        'is identical. The warehouse agent operates where errors are constrained by physical reality and '
        'feedback is immediate. The hiring agent operates where the stakes involve individual human dignity '
        'and the morally relevant features of each case resist standardized assessment. No scalar measure '
        'of autonomy captures this difference. Both systems might score identically on any framework that '
        'evaluates degree of human involvement &mdash; yet the ethical adequacy of autonomous operation in the '
        'two cases is profoundly different.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>The Problem of Moral Particularity</h3>'
        '<div class="boundary-body">'
        'At normative boundaries, the challenge is not insufficient data or inadequate processing. It is '
        'a structural feature of the relationship between general rules and particular moral situations. '
        'A hiring criterion that is fair as a general standard may be unjust when applied to a particular '
        'candidate whose circumstances the criterion was never designed to address. A welfare eligibility '
        'rule that is reasonable in the paradigmatic case may produce severe harm when applied to a family '
        'whose situation falls outside the paradigm. The morally relevant features of a given case are not '
        'fully specifiable in advance &mdash; they emerge in the encounter with the particular situation and '
        'require contextual sensitivity, analogical reasoning, and moral judgment that better algorithms '
        'or larger training sets cannot replicate.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>Differential Governance</h3>'
        '<div class="boundary-body">'
        'The framework yields a principle that neither the precautionary nor the managerial position '
        'provides: the permissible scope of agent autonomy should be calibrated to boundary type, not '
        'set uniformly. Governance frameworks that impose uniform restrictions unnecessarily constrain '
        'beneficial autonomous action at implementation boundaries. Governance frameworks that rely on '
        'uniform guardrails dangerously underestimate the structural risks at normative boundaries, '
        'where guardrails cannot substitute for moral judgment. The appropriate question for any proposed '
        'agent deployment is not &ldquo;how autonomous is this agent?&rdquo; but &ldquo;at which boundaries does this agent '
        'act, and is the level of autonomy appropriate to the boundary type involved?&rdquo;'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(_unwrap, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# PAGE: RESOURCES
# ──────────────────────────────────────────────────────────────
def page_resources():
    _wrap = '<div style="max-width:760px; margin:0 auto;">'
    _unwrap = '</div>'

    st.markdown(_wrap, unsafe_allow_html=True)

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>Publications</h3>'
        '<div class="boundary-body">'
        '<div style="margin-bottom:0.8rem;">'
        '<strong style="color:#e8e6e1;">Boundary Conditions for Agent Autonomy: A Structural Framework '
        'for Governing AI Systems That Act</strong><br/>'
        '<span style="color:#8a8677; font-style:italic;">AI &amp; Ethics (under review)</span><br/>'
        'Introduces the boundary framework and applies it to AI agent governance across implementation, '
        'institutional, and normative domains.'
        '</div>'
        '<div style="margin-bottom:0.8rem;">'
        '<strong style="color:#e8e6e1;">The Structural Irreducibility of Judgment in AI-Augmented '
        'Decision-Making</strong><br/>'
        '<span style="color:#8a8677; font-style:italic;">Ethics &amp; Information Technology (under review)</span><br/>'
        'Develops the philosophical foundations for the boundary analysis, arguing that human judgment '
        'at normative boundaries is constitutively resistant to algorithmic replacement.'
        '</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>The Bacon Center for AI Ethics in Business</h3>'
        '<div class="boundary-body">'
        '<div style="margin-bottom:0.6rem;">'
        'The Bacon Center, housed in the Ivy College of Business at Iowa State University, '
        'conducts research on the ethical dimensions of AI deployment in organizational contexts.'
        '</div>'
        '<div>'
        '<a href="https://ivybusiness.iastate.edu" target="_blank" '
        'style="color:#c8aa6e; text-decoration:underline;">'
        'Ivy College of Business &rarr;'
        '</a>'
        '</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>Key References</h3>'
        '<div class="boundary-body">'
        '<div style="margin-bottom:0.6rem;">'
        '<strong style="color:#e8e6e1;">Gabriel, I. et al. (2025).</strong> '
        'We need a new ethics for a world of AI agents.</div>'
        '<div style="margin-bottom:0.6rem;">'
        '<strong style="color:#e8e6e1;">Mitchell, M. et al. (2025).</strong> '
        'Fully autonomous AI agents should not be developed.</div>'
        '<div style="margin-bottom:0.6rem;">'
        '<strong style="color:#e8e6e1;">Kasirzadeh, A. &amp; Gabriel, I. (2025).</strong> '
        'Characterizing AI agents for alignment and governance.</div>'
        '<div style="margin-bottom:0.6rem;">'
        '<strong style="color:#e8e6e1;">Shavit, Y. et al. (2023).</strong> '
        'Practices for governing agentic AI systems. OpenAI.</div>'
        '<div style="margin-bottom:0.6rem;">'
        '<strong style="color:#e8e6e1;">Feng, K., McDonald, D., &amp; Zhang, A. (2025).</strong> '
        'Levels of autonomy for AI agents.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="governance-box" style="margin-bottom:1.5rem;">'
        '<h3>Government Advisory Work</h3>'
        '<div class="boundary-body">'
        'The Boundary Framework has been developed into a practitioner decision guide for '
        'Iowa&#39;s Department of Management, with worked examples across four state agencies '
        '(DOT, DOR, DHS, DAS) demonstrating how the framework applies to real agency '
        'AI deployment decisions.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(_unwrap, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# PASSCODE
# ──────────────────────────────────────────────────────────────
# Change this to whatever passcode you want to share with stakeholders.
# For stronger security in a hosted environment, you could move this
# to an environment variable like the API key.
APP_PASSCODE = "bacon2026"


def check_passcode():
    """Show a passcode screen and return True if authenticated."""
    if st.session_state.get("authenticated", False):
        return True

    st.markdown(
        '<div class="main-header">'
        '<h1>Boundary Framework</h1>'
        '<div class="subtitle">AI ETHICS EVALUATOR &middot; BACON CENTER FOR AI ETHICS IN BUSINESS &middot; IOWA STATE UNIVERSITY</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="text-align:center; max-width:400px; margin:3rem auto 1rem; '
        'font-family:Source Sans 3,sans-serif; color:#8a8677; font-size:0.95rem;">'
        'This demo is available to invited stakeholders.<br/>Please enter the access code to continue.'
        '</div>',
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        code = st.text_input("Access code:", type="password", key="passcode_input")
        if st.button("Enter", use_container_width=True, key="passcode_btn"):
            if code == APP_PASSCODE:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.markdown(
                    '<div style="text-align:center; color:#f06060; font-family:Source Sans 3,sans-serif; '
                    'font-size:0.9rem; margin-top:0.5rem;">Incorrect access code.</div>',
                    unsafe_allow_html=True,
                )

    st.markdown(
        '<div style="text-align:center; margin-top:3rem; padding:1.5rem 0; '
        'border-top:1px solid rgba(200,170,110,0.1); font-family:Source Sans 3,sans-serif; '
        'font-size:0.8rem; color:#5a5750;">'
        'Bacon Center for AI Ethics in Business &middot; Ivy College of Business &middot; Iowa State University'
        '</div>',
        unsafe_allow_html=True,
    )

    return False


# ──────────────────────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────────────────────
def main():
    # Check passcode first
    if not check_passcode():
        return

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Boundary Framework</h1>
        <div class="subtitle">AI ETHICS EVALUATOR &nbsp;·&nbsp; BACON CENTER FOR AI ETHICS IN BUSINESS &nbsp;·&nbsp; IOWA STATE UNIVERSITY</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation tabs
    tab_analyze, tab_framework, tab_concepts, tab_resources = st.tabs([
        "⚡ Analyze a Proposal",
        "📐 The Framework",
        "💡 Key Concepts",
        "📚 Resources",
    ])

    with tab_analyze:
        page_analyze()

    with tab_framework:
        page_framework()

    with tab_concepts:
        page_concepts()

    with tab_resources:
        page_resources()

    # Footer
    st.markdown("""
    <div style="text-align:center; margin-top:3rem; padding:1.5rem 0; border-top:1px solid rgba(200,170,110,0.1); font-family:'Source Sans 3',sans-serif; font-size:0.8rem; color:#5a5750;">
        Bacon Center for AI Ethics in Business &nbsp;·&nbsp; Ivy College of Business &nbsp;·&nbsp; Iowa State University<br/>
        Based on the Boundary Framework for AI Agent Autonomy
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
