# Update this section in the CSS styles portion of main.py
st.markdown("""
<style>
/* Main container for requirements section */
.requirements-container {
    margin: 1rem 0;  /* Reduced top margin to move closer to header */
    padding: 0.5rem; /* Reduced padding */
}

/* Individual requirement row */
.requirement-row {
    display: flex;
    align-items: center;
    min-height: 40px;  /* Slightly reduced for better spacing */
    margin-bottom: 1rem; /* Reduced bottom margin */
    gap: 1rem;
}

/* Text container */
.requirement-text {
    flex: 1;
    margin: 0;
    line-height: 1.4;
    padding: 0.25rem 0;  /* Reduced padding */
    display: flex;
    align-items: center; /* Better vertical alignment */
}

/* Checkbox container */
.checkbox-container {
    display: flex;
    align-items: center;
    min-width: 24px;
    padding-top: 4px; /* Slight adjustment to move checkboxes down */
}

/* Custom checkbox styling */
.stCheckbox {
    margin: 0 !important;
    padding: 0 !important;
    vertical-align: middle !important;
    transform: translateY(2px) !important; /* Fine-tuned vertical alignment */
}
</style>
""", unsafe_allow_html=True)

# Update the requirements text in the main content section
# Replace the three requirements sections with:

# First Requirement
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.markdown("""
        <div class="requirement-text">
        I have worked as a management consultant within the past two years.
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.checkbox("", key="consultant_check", label_visibility="collapsed")

# Second Requirement
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.markdown("""
        <div class="requirement-text">
        I am actively or passively seeking new employment opportunities.
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.checkbox("", key="seeking_check", label_visibility="collapsed")

# Third Requirement
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.markdown("""
        <div class="requirement-text">
        I commit to providing detailed feedback and suggestions.
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.checkbox("", key="feedback_check", label_visibility="collapsed")