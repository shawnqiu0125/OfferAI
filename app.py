import streamlit as st
import time
import pandas as pd
from llm import process_resume_request, clean_workspace, save_resume_to_pdf
import requests
import json
import os
import toml
from io import StringIO
import docx2txt
import PyPDF2

def job_list_page():
    # back button
    col1, col2 = st.columns([9, 1])
    with col1:
        if st.button("← Back", key="back_button"):
            st.session_state.current_page = 'welcome'
            st.rerun()

    st.markdown("""
    <style>
    .job-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .job-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }
    .job-title {
        font-size: 22px;
        font-weight: bold;
        color: #333;
        margin-bottom: 8px;
    }
    .job-company {
        color: #666;
        font-size: 16px;
        margin-bottom: 10px;
    }
    .job-details {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .job-location, .job-salary {
        font-size: 15px;
        margin-right: 15px;
    }
    .job-location {
        color: #666;
    }
    .job-salary {
        font-weight: bold;
        color: #007bff;
    }
    .job-deadline {
        color: #888;
        font-size: 14px;
    }
    .job-description {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
    }
    .apply-button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .apply-button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Job Listings")

    # 读取Excel文件
    df = pd.read_excel("软工数据库.xlsx", sheet_name='工作表1')

    # 确保正确的列
    columns_to_show = ['Job Title', 'Company Name', 'Work City', 'Salary', 'Application Deadline', 'Job Description']
    df.columns = columns_to_show if len(columns_to_show) == len(df.columns) else df.columns

    # 搜索和过滤
    search_term = st.text_input("Search Jobs", placeholder="Enter job title or company")
    city_filter = st.selectbox("Filter by City", ["All"] + list(df['Work City'].unique()))

    # 应用过滤
    df_filtered = df[
        (df['Job Title'].str.contains(search_term, case=False) |
         df['Company Name'].str.contains(search_term, case=False)) &
        ((df['Work City'] == city_filter) | (city_filter == "All"))
    ]

    # 分页
    items_per_page = 5
    total_pages = (len(df_filtered) - 1) // items_per_page + 1
    page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)

    start_idx = (page_number - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # 显示职位列表
    for _, job in df_filtered.iloc[start_idx:end_idx].iterrows():
        st.markdown(f"""
        <div class="job-card">
            <div class="job-title">{job['Job Title']}</div>
            <div class="job-company">{job['Company Name']}</div>
            <div class="job-details">
                <div class="job-location">📍 {job['Work City']}</div>
                <div class="job-salary">💰 {job['Salary']}</div>
            </div>
            <div class="job-deadline">🕒 Application Deadline: {job['Application Deadline']}</div>
            <div class="job-description">
                <strong>Job Description:</strong><br>
                {job['Job Description']}
            </div>
            <div style="text-align: right; margin-top: 15px;">
                <button class="apply-button">Apply Now</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 分页信息
    st.write(f"Page {page_number} of {total_pages} | Total Jobs: {len(df_filtered)}")

# Welcome Page Function
def welcome_page():
    # 自定义CSS样式
    st.markdown("""
        <style>
        .welcome-header {
            font-size: 3.2rem;
            background: linear-gradient(45deg, #009EDB, #00395D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 2rem 0;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 800;
        }
        .welcome-subtitle {
            font-size: 1.5rem;
            color: #666;
            text-align: center;
            margin-bottom: 3rem;
            font-weight: 300;
        }
        .feature-box {
            background: linear-gradient(135deg, #009EDB, #0056b3);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            min-height: 220px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .feature-box:hover {
            transform: translateY(-5px);
        }
        .feature-box h3 {
            color: white;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
        }
        .welcome-content {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border: 1px solid #eee;
        }
        .welcome-content h3 {
            color: #333;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
        }
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .feature-item {
            display: flex;
            align-items: center;
            margin: 1rem 0;
            color: white;
            font-size: 1.1rem;
            padding: 0.5rem;
        }
        .feature-icon {
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
        }
        .steps-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .step-item {
            display: flex;
            align-items: center;
            margin: 1rem 0;
            padding: 0.5rem;
            border-radius: 8px;
            color: #333;
            font-size: 1.1rem;
        }
        .step-number {
            background: #009EDB;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-weight: bold;
        }
        .stats-container {
            display: flex;
            justify-content: space-between;
            margin-top: 2rem;
        }
        .stat-box {
            text-align: center;
            padding: 1.5rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-number {
            color: #009EDB;
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
        }
        .stat-label {
            color: #666;
            margin: 0;
            font-size: 1rem;
        }
        .stButton>button {
            background: linear-gradient(45deg, #009EDB, #0056b3);
            color: white;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            border-radius: 30px;
            border: none;
            width: 100%;
            margin-top: 2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,158,219,0.3);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,158,219,0.4);
        }
        </style>
    """, unsafe_allow_html=True)

    # 页面标题和副标题
    st.markdown('<h1 class="welcome-header">Welcome to Campus Offer AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-subtitle">Your Intelligent Career Partner</p>', unsafe_allow_html=True)

    # 主要内容区域
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>🚀 Accelerate Your Career Growth</h3>
            <div class="feature-list">
                <div class="feature-item">
                    <div class="feature-icon">📝</div>
                    <span>AI-powered resume builder tailored to your industry</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🎯</div>
                    <span>Personalized job matching based on your profile</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🤖</div>
                    <span>Interview preparation with AI coaching</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">📊</div>
                    <span>Real-time application tracking and analytics</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="welcome-content">
            <h3>🎯 Quick Start Guide</h3>
            <div class="steps-list">
                <div class="step-item">
                    <div class="step-number">1</div>
                    <span>Create your professional profile</span>
                </div>
                <div class="step-item">
                    <div class="step-number">2</div>
                    <span>Select target positions</span>
                </div>
                <div class="step-item">
                    <div class="step-number">3</div>
                    <span>Generate AI-optimized resume</span>
                </div>
                <div class="step-item">
                    <div class="step-number">4</div>
                    <span>Start applying and tracking</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # 统计数据部分
    st.markdown("""
    <div class="stats-container">
        <div class="stat-box">
            <p class="stat-number">10k+</p>
            <p class="stat-label">Success Stories</p>
        </div>
        <div class="stat-box">
            <p class="stat-number">95%</p>
            <p class="stat-label">Interview Rate</p>
        </div>
        <div class="stat-box">
            <p class="stat-number">500+</p>
            <p class="stat-label">Partner Companies</p>
        </div>
        <div class="stat-box">
            <p class="stat-number">24/7</p>
            <p class="stat-label">AI Support</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Your Journey Now", key="start_button"):
        st.session_state.current_page = 'personal_info'
        st.rerun()

def personal_info_page():
    # back button
    col1, col2 = st.columns([9, 1])
    with col1:
        if st.button("← Back", key="back_button"):
            st.session_state.current_page = 'welcome'
            st.rerun()

    st.title("Personal Information")

    # Basic Information 部分
    st.header("Basic Information")
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Name*", placeholder="please input")

    with col2:
        sex = st.selectbox(
            "Sex*",
            options=["", "Male", "Female", "Other"],
            placeholder="please choose"
        )

    with col3:
        phone = st.text_input("Phone*", placeholder="please input")

    col4, col5 = st.columns(2)

    with col4:
        email = st.text_input("E-mail*", placeholder="please input")

    with col5:
        city = st.selectbox(
            "City*",
            options=["", "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Other"],
            placeholder="please choose"
        )

    # Job Information 部分
    st.header("Job Information")

    col6, col7, col8 = st.columns(3)

    with col6:
        university = st.selectbox(
            "University*",
            options=["", "The University of Hong Kong", "The Chinese University of Hong Kong",
                     " The Hong Kong University of Science and Technology", "The Hong Kong Polytechnic University","City University of Hong Kong"],
            placeholder="please choose"
        )

    with col7:
        degree = st.selectbox(
            "Degree*",
            options=["", "Bachelor", "Master", "PhD", "Other"],
            placeholder="please choose"
        )

    with col8:
        target_position = st.selectbox(
            "Target position*",
            options=["", "Product Manager", "Data Analyst", "Project Manager", "UI designer", "Software Developer","Tester"],
            placeholder="please choose"
        )

    # Work/Internship experiences
    work_experience = st.text_area(
        "Work/internship experiences*",
        placeholder="If you do not have these experiences, please enter 'null'",
        height=150
    )

    # Project experiences
    project_experience = st.text_area(
        "Project experiences*",
        placeholder="If you do not have these experiences, please enter 'null'",
        height=150
    )

    # Major courses
    major_courses = st.text_area(
        "Major courses*",
        placeholder="If you do not have these experiences, please enter 'null'",
        height=150
    )

    honors_won = st.text_area(
        "Honors won*",
        placeholder="If you do not have these experiences, please enter 'null'",
        height=150
    )

    # Generate button
    if st.button("Generate Resume"):
        user_data = {
            "name": name,
            "sex": sex,
            "phone": phone,
            "email": email,
            "city": city,
            "university": university,
            "degree": degree,
            "target_position": target_position,
            "work_experience": work_experience,
            "project_experience": project_experience,
            "major_courses": major_courses,
            "honors_won": honors_won
        }

        with st.spinner("Generating your resume..."):
            result = process_resume_request(user_data)

            if result["status"] == "success":
                st.markdown("### Generated Resume")
                st.markdown(result["content"])

                # PDF file download
                pdf_filename = f"resume_{int(time.time())}.pdf"
                if save_resume_to_pdf(result["content"], pdf_filename, name):
                    with open(pdf_filename, 'rb') as f:
                        st.download_button(
                            label="Download as PDF",
                            data=f.read(),
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
            else:
                st.error(result["message"])


def main():
    st.set_page_config(
        page_title="Offer AI",
        page_icon="👋",
        layout="wide"
    )

    # 添加侧边栏
    with st.sidebar:
        st.title("Offer AI")
        st.markdown("---")
        # 根据当前页面显示不同的导航选项
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'welcome'

        if st.session_state.current_page == 'welcome':
            menu = ["Welcome"]
        else:
            menu = ["Resume Generation","Job List"]  # Changed to only show Resume Generation

        choice = st.radio("Navigation", menu)

        # Handle page navigation
        if choice == "Welcome" and st.session_state.current_page != 'welcome':
            st.session_state.current_page = 'welcome'
            st.rerun()

        if choice == "Job List" and st.session_state.current_page != 'job_list':
            st.session_state.current_page = 'job_list'
            st.rerun()

        if choice == "Resume Generation" and st.session_state.current_page != 'personal_info':
            st.session_state.current_page = 'personal_info'
            st.rerun()

    # Render the current page
    if st.session_state.current_page == 'welcome':
        welcome_page()
    elif st.session_state.current_page == 'personal_info':
        personal_info_page()
    elif st.session_state.current_page == 'job_list':
        job_list_page()

    # Clean temporary files
    clean_workspace()

if __name__ == "__main__":
    main()