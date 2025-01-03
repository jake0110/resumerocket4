import streamlit as st

def render_preview(template):
    st.markdown("""
        <style>
        .preview-container {
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
            background-color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="preview-container">', unsafe_allow_html=True)
        
        # Personal Information
        if st.session_state.personal_info:
            st.markdown(f"# {st.session_state.personal_info.get('name', '')}")
            st.markdown(f"📧 {st.session_state.personal_info.get('email', '')}")
            st.markdown(f"📱 {st.session_state.personal_info.get('phone', '')}")
            st.markdown("---")

        # Education Section
        if any(edu.get('institution') for edu in st.session_state.education):
            st.markdown("## Education")
            for edu in st.session_state.education:
                if edu.get('institution'):
                    st.markdown(f"**{edu.get('institution')}**")
                    st.markdown(f"{edu.get('degree')} - {edu.get('graduation_year')}")
            st.markdown("---")

        # Experience Section
        if any(exp.get('company') for exp in st.session_state.experience):
            st.markdown("## Professional Experience")
            for exp in st.session_state.experience:
                if exp.get('company'):
                    st.markdown(f"**{exp.get('company')}**")
                    st.markdown(f"*{exp.get('position')} ({exp.get('duration')})*")
                    st.markdown(exp.get('description', ''))
            st.markdown("---")

        # Skills Section
        if st.session_state.skills:
            st.markdown("## Skills")
            st.markdown(", ".join(st.session_state.skills))

        st.markdown('</div>', unsafe_allow_html=True)

