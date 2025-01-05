import streamlit as st
import os
import tempfile
from utils.resume_parser import ResumeParser

def render_personal_info():
    with st.form("personal_info_form"):
        st.subheader("Personal Information")

        # File upload section with better visual feedback
        st.markdown("### Resume Upload")
        uploaded_file = st.file_uploader(
            "Upload your existing resume (DOCX)",
            type=['docx'],
            key="resume_uploader",
            help="Upload your Word document and click 'Parse Resume' to automatically fill in your information"
        )

        if uploaded_file is not None:
            st.info(f"File selected: {uploaded_file.name}")
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
            if file_size > 10:  # 10MB limit
                st.warning(f"File size ({file_size:.1f}MB) exceeds 10MB limit")
            else:
                st.success(f"File size: {file_size:.1f}MB (Ready to parse)")

                if st.form_submit_button("Parse Resume"):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name

                            # Parse the resume
                            parser = ResumeParser()
                            parsed_content = parser.parse_docx(tmp_file_path)

                            # Update session state with parsed content
                            if parsed_content.get('contact'):
                                st.session_state.personal_info = parsed_content['contact']
                            if parsed_content.get('education'):
                                st.session_state.education = parsed_content['education']
                            if parsed_content.get('experience'):
                                st.session_state.experience = parsed_content['experience']
                            if parsed_content.get('skills'):
                                st.session_state.skills = [
                                    skill for category in parsed_content['skills'].values() 
                                    for skill in category if isinstance(skill, str)
                                ]

                            st.success("✅ Resume successfully parsed! Form fields have been updated.")

                            # Clean up temporary file
                            os.unlink(tmp_file_path)

                    except Exception as e:
                        st.error(f"Error parsing resume: {str(e)}")

        # Manual input fields as fallback
        name = st.text_input(
            "Full Name",
            value=st.session_state.personal_info.get('name', ''),
            key="name_input"
        )

        email = st.text_input(
            "Email",
            value=st.session_state.personal_info.get('email', ''),
            key="email_input"
        )

        phone = st.text_input(
            "Phone",
            value=st.session_state.personal_info.get('phone', ''),
            key="phone_input"
        )

        # Save button for manual edits
        if st.form_submit_button("Save Personal Info"):
            st.session_state.personal_info = {
                'name': name,
                'email': email,
                'phone': phone
            }
            st.success("✅ Personal information saved!")

def render_education():
    st.subheader("Education")
    
    if st.button("Add Education"):
        st.session_state.education.append({})

    for i, edu in enumerate(st.session_state.education):
        with st.form(f"education_form_{i}"):
            st.write(f"Education #{i+1}")
            
            institution = st.text_input(
                "Institution",
                value=edu.get('institution', ''),
                key=f"institution_{i}"
            )
            
            degree = st.text_input(
                "Degree",
                value=edu.get('degree', ''),
                key=f"degree_{i}"
            )
            
            graduation_year = st.text_input(
                "Graduation Year",
                value=edu.get('graduation_year', ''),
                key=f"grad_year_{i}"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.form_submit_button("Save"):
                    st.session_state.education[i] = {
                        'institution': institution,
                        'degree': degree,
                        'graduation_year': graduation_year
                    }
                    st.success(f"Education #{i+1} saved!")
            
            with col2:
                if st.form_submit_button("Remove"):
                    st.session_state.education.pop(i)
                    st.rerun()

def render_experience():
    st.subheader("Professional Experience")
    
    if st.button("Add Experience"):
        st.session_state.experience.append({})

    for i, exp in enumerate(st.session_state.experience):
        with st.form(f"experience_form_{i}"):
            st.write(f"Experience #{i+1}")
            
            company = st.text_input(
                "Company",
                value=exp.get('company', ''),
                key=f"company_{i}"
            )
            
            position = st.text_input(
                "Position",
                value=exp.get('position', ''),
                key=f"position_{i}"
            )
            
            duration = st.text_input(
                "Duration",
                value=exp.get('duration', ''),
                key=f"duration_{i}"
            )
            
            description = st.text_area(
                "Description",
                value=exp.get('description', ''),
                key=f"description_{i}"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.form_submit_button("Save"):
                    st.session_state.experience[i] = {
                        'company': company,
                        'position': position,
                        'duration': duration,
                        'description': description
                    }
                    st.success(f"Experience #{i+1} saved!")
            
            with col2:
                if st.form_submit_button("Remove"):
                    st.session_state.experience.pop(i)
                    st.rerun()

def render_skills():
    st.subheader("Skills")
    
    # Convert skills list to string for input
    current_skills = ", ".join(st.session_state.skills)
    
    with st.form("skills_form"):
        skills_input = st.text_area(
            "Enter your skills (comma-separated)",
            value=current_skills
        )
        
        if st.form_submit_button("Save Skills"):
            # Convert input string to list and clean up
            skills_list = [
                skill.strip()
                for skill in skills_input.split(",")
                if skill.strip()
            ]
            st.session_state.skills = skills_list
            st.success("Skills saved!")