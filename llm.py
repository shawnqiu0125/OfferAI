import requests
import json
import os
import toml
import streamlit as st
from fpdf import FPDF
import textwrap


def load_api_key():
    file_path = 'credential'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            secrets = toml.load(f)
    else:
        secrets = st.secrets
    return secrets['OPENROUTER']['OPENROUTER_API_KEY']


def generate_resume(user_data):
    """
    Generate AI resume
    :param user_data: User input information dictionary
    :return: Generated resume content
    """
    OPENROUTER_API_KEY = load_api_key()

    # Build system prompt
    system_prompt = """You are an expert resume writer with extensive experience in creating professional resumes. 
    Your task is to:
    1. Create a well-structured, professional resume
    2. Format the contact information in a single line at the top, separated by vertical bars (|)
    3. Highlight key achievements and experiences
    4. Tailor the content to match the target position
    5. Use professional language and formatting
    6. Ensure the resume is concise yet comprehensive
    7. Write the resume in English

    Please structure the resume with the following sections:
    - Contact Information (in a single line with | separators)
    - Education
    - Work Experience
    - Project Experience
    - Skills & Expertise
    - Honors & Awards

    Ensure each structure section header such as education, work experience and so on is formatted in bold using markdown syntax (**Section Name**)
    Other subheadings such as the title of the first paragraph of experience under work experience do not need to be bolded.
    """

    # Build user prompt
    user_prompt = f"""Based on the following information, please create a professional resume:

        {user_data.get('city', '')} | {user_data.get('email', '')} | {user_data.get('phone', '')}

        Education:
        {user_data.get('university', '')} | {user_data.get('degree', '')}

        Career Objective:
        - Target Position: {user_data.get('target_position', '')}

        Experience:
        - Work/Internship: {user_data.get('work_experience', '')}
        - Projects: {user_data.get('project_experience', '')}

        Academic:
        - Major Courses: {user_data.get('major_courses', '')}

        Please ensure all structure section headers such as education are in bold using markdown syntax (**Section Name**). 
        No name information is required on contact information.
        At the same time, please pay attention to the formatting. Each section of my resume should have one blank line and bold headings. 
        There is no need to provide me with any content outside of my resume in the document, such as suggestions and note.
        Other subheadings such as the title of the first paragraph of experience under work experience do not need to be bolded.
    """

    # Build message array
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        # Send API request
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            data=json.dumps({
                "messages": messages,
                "model": "openai/gpt-4o-mini-2024-07-18"
            })
        )

        # Check response status
        response.raise_for_status()

        # Parse response
        result = response.json()
        resume_content = result['choices'][0]['message']['content']

        return {
            "status": "success",
            "content": resume_content
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"API request failed: {str(e)}"
        }
    except KeyError as e:
        return {
            "status": "error",
            "message": f"Error parsing API response: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def format_resume(resume_content):
    """
    Format resume content
    :param resume_content: Raw content from AI-generated resume
    :return: Formatted resume content
    """
    if resume_content.startswith('```'):
        resume_content = resume_content[3:]
    if resume_content.endswith('```'):
        resume_content = resume_content[:-3]

    formatted_content = resume_content.replace('---', '\n')
    formatted_content = formatted_content.replace('###', '##')
    formatted_content = '\n\n'.join(line.strip() for line in formatted_content.splitlines() if line.strip())
    return formatted_content


def validate_user_input(user_data):
    """
    Validate user input
    :param user_data: User input data
    :return: (bool, str) - (Validation passed, error message)
    """
    required_fields = ['name', 'sex', 'phone', 'email', 'city',
                       'university', 'degree', 'target_position']

    missing_fields = []
    for field in required_fields:
        if not user_data.get(field):
            missing_fields.append(field)

    if missing_fields:
        return False, f"Please fill in all required fields: {', '.join(missing_fields)}"

    if '@' not in user_data['email']:
        return False, "Please enter a valid email address"

    if not user_data['phone'].isdigit():
        return False, "Please enter a valid phone number"

    return True, ""


def save_resume_to_file(content, filename):
    """
    Save resume content to file
    :param content: Resume content
    :param filename: File name
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False


def process_resume_request(user_data):
    """
    Main function to process resume generation request
    :param user_data: User input data
    :return: Processing result
    """
    is_valid, error_message = validate_user_input(user_data)
    if not is_valid:
        return {
            "status": "error",
            "message": error_message
        }

    result = generate_resume(user_data)
    if result["status"] == "success":
        formatted_resume = format_resume(result["content"])
        return {
            "status": "success",
            "content": formatted_resume
        }
    else:
        return result


def save_resume_to_pdf(content, filename, name):
    try:
        pdf = FPDF()
        pdf.add_page()

        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVuB', '', 'DejaVuSans-Bold.ttf', uni=True)

        pdf.set_font('DejaVuB', '', 16)
        pdf.cell(0, 10, f'{name}\'s Resume', 0, 1, 'C')
        # 添加联系方式并居中
        contact_info = content.splitlines()[0]  # 假设第一行是联系方式
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, contact_info, 0, 1, 'C')
        pdf.ln(2)

        lines = content.split('\n')[1:]
        for line in lines:
            if '**' in line:
                pdf.set_font('DejaVuB', '', 14)
                line = line.replace('**', '')
                pdf.cell(0, 10, line.strip(), 0, 1, 'L')
                pdf.set_font('DejaVu', '', 12)
            else:
                wrapped_lines = textwrap.wrap(line, width=85)
                for wrapped_line in wrapped_lines:
                    pdf.cell(0, 6, wrapped_line, 0, 1, 'L')

                if not line.strip():
                    pdf.ln(2)

        pdf.output(filename)
        return True

    except Exception as e:
        st.error(f"Error saving PDF: {str(e)}")
        return False


def clean_workspace():
    """
    Clean workspace by deleting temporary files
    """
    try:
        temp_files = [f for f in os.listdir() if f.endswith(('.txt', '.pdf'))]
        for file in temp_files:
            os.remove(file)
    except Exception as e:
        st.warning(f"Error cleaning workspace: {str(e)}")


if __name__ == "__main__":
    st.error("This file should be imported, not run directly!")