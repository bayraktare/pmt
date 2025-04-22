import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import json
import io
import base64
import os
import uuid
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import calendar

# Set page configuration
st.set_page_config(
    page_title="TechSight Project Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f7ff;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f4ff;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: #4b5563;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    .card {
        border-radius: 5px;
        background-color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 20px;
        margin-bottom: 20px;
    }
    .metrics-card {
        text-align: center;
        padding: 15px;
    }
    .metrics-card h3 {
        margin-top: 0;
        color: #4b5563;
        font-size: 16px;
    }
    .metrics-card p {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    button.css-1cpxqw2 {
        background-color: #3b82f6;
        color: white;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
PARTNERS = [
    "Yildiz Technical University (YTU)",
    "THE NEW WAY",
    "Ss. Cyril and Methodius University in Skopje",
    "Politecnico da Guarda",
    "HOCHSCHULE MAGDEBURG-STENDAL",
    "Center for the Promotion of Science",
    "Daugavpils Universitate"
]

TASK_CATEGORIES = [
    "Project Management",
    "Research",
    "Development",
    "Implementation",
    "Dissemination",
    "Quality Assurance",
    "Reporting"
]

TASK_STATUS = ["Not Started", "In Progress", "Completed", "Delayed", "Cancelled"]

# Helper functions
def init_session_state():
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    if 'tasks' not in st.session_state:
        # Create sample data
        st.session_state.tasks = create_sample_tasks()
        
    if 'reports' not in st.session_state:
        st.session_state.reports = create_sample_reports()
    
    if 'users' not in st.session_state:
        st.session_state.users = create_sample_users()
        
    if 'notifications' not in st.session_state:
        st.session_state.notifications = create_sample_notifications()
    
    if 'documents' not in st.session_state:
        st.session_state.documents = create_sample_documents()

def create_sample_tasks():
    today = datetime.now().date()
    tasks = []
    
    # Create a set of tasks for each partner
    for i, partner in enumerate(PARTNERS):
        # Past tasks
        for j in range(3):
            start_date = today - timedelta(days=90-j*10)
            end_date = start_date + timedelta(days=15)
            tasks.append({
                "id": f"task_{len(tasks)+1}",
                "title": f"Past Task {j+1} for {partner}",
                "description": f"A completed task for {partner}",
                "assigned_to": partner,
                "assigned_by": "Yildiz Technical University (YTU)" if partner != "Yildiz Technical University (YTU)" else "THE NEW WAY",
                "category": TASK_CATEGORIES[j % len(TASK_CATEGORIES)],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "status": "Completed",
                "progress": 100,
                "priority": "High" if j == 0 else "Medium" if j == 1 else "Low",
                "comments": []
            })
        
        # Current tasks
        for j in range(2):
            start_date = today - timedelta(days=15-j*5)
            end_date = today + timedelta(days=15+j*5)
            tasks.append({
                "id": f"task_{len(tasks)+1}",
                "title": f"Current Task {j+1} for {partner}",
                "description": f"An ongoing task for {partner}",
                "assigned_to": partner,
                "assigned_by": "Yildiz Technical University (YTU)" if partner != "Yildiz Technical University (YTU)" else "THE NEW WAY",
                "category": TASK_CATEGORIES[(j+3) % len(TASK_CATEGORIES)],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "status": "In Progress",
                "progress": 50 + j*20,
                "priority": "High" if j == 0 else "Medium",
                "comments": []
            })
        
        # Future tasks
        for j in range(3):
            start_date = today + timedelta(days=30+j*15)
            end_date = start_date + timedelta(days=20)
            tasks.append({
                "id": f"task_{len(tasks)+1}",
                "title": f"Future Task {j+1} for {partner}",
                "description": f"A planned task for {partner}",
                "assigned_to": partner,
                "assigned_by": "Yildiz Technical University (YTU)" if partner != "Yildiz Technical University (YTU)" else "THE NEW WAY",
                "category": TASK_CATEGORIES[(j+5) % len(TASK_CATEGORIES)],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "status": "Not Started",
                "progress": 0,
                "priority": "Medium" if j == 0 else "Low",
                "comments": []
            })
    
    return tasks

def create_sample_reports():
    today = datetime.now().date()
    reports = []
    
    for i, partner in enumerate(PARTNERS):
        for j in range(6):
            report_date = today - timedelta(days=(6-j)*14)
            reports.append({
                "id": f"report_{len(reports)+1}",
                "title": f"Biweekly Report {j+1}",
                "partner": partner,
                "submission_date": report_date.strftime("%Y-%m-%d"),
                "period_start": (report_date - timedelta(days=14)).strftime("%Y-%m-%d"),
                "period_end": report_date.strftime("%Y-%m-%d"),
                "activities_completed": f"Completed activities for {partner} in period {j+1}",
                "activities_in_progress": f"Ongoing activities for {partner} in period {j+1}",
                "activities_planned": f"Planned activities for {partner} in period {j+1}",
                "issues": f"Issues encountered by {partner} in period {j+1}" if j % 3 == 0 else "",
                "status": "Submitted" if j < 5 else "Draft" if partner == "Yildiz Technical University (YTU)" else "Pending"
            })
    
    return reports

def create_sample_users():
    users = [
        {
            "username": "admin",
            "password": "admin123",  # In a real app, use hashed passwords!
            "role": "admin",
            "organization": "Yildiz Technical University (YTU)",
            "name": "Administrator",
            "email": "admin@ytu.edu.tr"
        }
    ]
    
    for partner in PARTNERS:
        partner_short = partner.split()[0].lower()
        users.append({
            "username": partner_short,
            "password": f"{partner_short}123",  # In a real app, use hashed passwords!
            "role": "partner",
            "organization": partner,
            "name": f"{partner} Representative",
            "email": f"contact@{partner_short}.edu"
        })
    
    return users

def create_sample_notifications():
    today = datetime.now().date()
    notifications = []
    
    # Task assignments
    for i, partner in enumerate(PARTNERS):
        notifications.append({
            "id": f"notif_{len(notifications)+1}",
            "user": partner,
            "message": f"New task assigned: Current Task 1",
            "date": (today - timedelta(days=15)).strftime("%Y-%m-%d"),
            "read": False,
            "type": "task_assignment"
        })
    
    # Report reminders
    for i, partner in enumerate(PARTNERS):
        notifications.append({
            "id": f"notif_{len(notifications)+1}",
            "user": partner,
            "message": "Reminder: Biweekly report due tomorrow",
            "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "read": False,
            "type": "report_reminder"
        })
    
    # Comment notifications
    for i, partner in enumerate(PARTNERS):
        if i > 0:  # Skip the first partner
            notifications.append({
                "id": f"notif_{len(notifications)+1}",
                "user": partner,
                "message": f"New comment from {PARTNERS[0]} on Current Task 1",
                "date": today.strftime("%Y-%m-%d"),
                "read": False,
                "type": "comment"
            })
    
    return notifications

def create_sample_documents():
    documents = []
    
    # Project documents
    documents.append({
        "id": "doc_1",
        "title": "TechSight Project Handbook",
        "category": "Project Management",
        "upload_date": "2024-01-15",
        "uploaded_by": "Yildiz Technical University (YTU)",
        "file_type": "PDF",
        "shared_with": "All Partners",
        "description": "Project handbook for the TechSight project"
    })
    
    documents.append({
        "id": "doc_2",
        "title": "Financial Guidelines",
        "category": "Project Management",
        "upload_date": "2024-01-20",
        "uploaded_by": "Yildiz Technical University (YTU)",
        "file_type": "PDF",
        "shared_with": "All Partners",
        "description": "Financial guidelines for the TechSight project"
    })
    
    # Partner-specific documents
    for i, partner in enumerate(PARTNERS):
        documents.append({
            "id": f"doc_{len(documents)+1}",
            "title": f"{partner} - Initial Plan",
            "category": "Planning",
            "upload_date": "2024-02-01",
            "uploaded_by": partner,
            "file_type": "PDF",
            "shared_with": ["Yildiz Technical University (YTU)", partner],
            "description": f"Initial plan for {partner}"
        })
    
    return documents

def get_user_tasks(username):
    user = next((u for u in st.session_state.users if u["username"] == username), None)
    if not user:
        return []
    
    organization = user["organization"]
    if user["role"] == "admin":
        return st.session_state.tasks
    else:
        return [task for task in st.session_state.tasks if task["assigned_to"] == organization]

def get_user_reports(username):
    user = next((u for u in st.session_state.users if u["username"] == username), None)
    if not user:
        return []
    
    organization = user["organization"]
    if user["role"] == "admin":
        return st.session_state.reports
    else:
        return [report for report in st.session_state.reports if report["partner"] == organization]

def get_user_notifications(username):
    user = next((u for u in st.session_state.users if u["username"] == username), None)
    if not user:
        return []
    
    organization = user["organization"]
    return [notif for notif in st.session_state.notifications if notif["user"] == organization]

def login_user(username, password):
    user = next((u for u in st.session_state.users if u["username"] == username and u["password"] == password), None)
    if user:
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.session_state.is_admin = user["role"] == "admin"
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.is_admin = False

def create_gantt_chart(tasks):
    if not tasks:
        return None
    
    # Prepare data for Gantt chart
    df = []
    for task in tasks:
        task_status = task["status"]
        color = ""
        if task_status == "Completed":
            color = "rgb(0, 128, 0)"  # Green
        elif task_status == "In Progress":
            color = "rgb(30, 144, 255)"  # Blue
        elif task_status == "Not Started":
            color = "rgb(192, 192, 192)"  # Gray
        elif task_status == "Delayed":
            color = "rgb(255, 165, 0)"  # Orange
        else:  # Cancelled
            color = "rgb(255, 0, 0)"  # Red
        
        df.append(dict(
            Task=task["title"],
            Start=task["start_date"],
            Finish=task["end_date"],
            Partner=task["assigned_to"],
            Status=task_status,
            Description=task["description"],
            Resource=task["category"],
            Progress=task["progress"],
            Priority=task["priority"],
            color=color
        ))
    
    if not df:
        return None
    
    fig = ff.create_gantt(
        df,
        colors={task["title"]: task["color"] for task in df},
        index_col='Partner',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        title="TechSight Project Gantt Chart"
    )
    
    # Update layout for better visibility
    fig.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, b=10, t=50),
        title_font=dict(size=24),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600
    )
    
    return fig

def task_progress_chart(tasks):
    if not tasks:
        return None
    
    task_status = pd.DataFrame([{"Status": task["status"], "Count": 1} for task in tasks])
    status_counts = task_status.groupby("Status").sum().reset_index()
    
    # Create pie chart
    fig = px.pie(
        status_counts,
        values="Count",
        names="Status",
        title="Task Status Distribution",
        color="Status",
        color_discrete_map={
            "Completed": "green",
            "In Progress": "blue",
            "Not Started": "gray",
            "Delayed": "orange",
            "Cancelled": "red"
        }
    )
    
    fig.update_layout(
        margin=dict(t=50, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    return fig

def partner_task_distribution(tasks):
    if not tasks:
        return None
    
    partner_data = []
    for partner in PARTNERS:
        partner_tasks = [task for task in tasks if task["assigned_to"] == partner]
        if partner_tasks:
            completed = len([t for t in partner_tasks if t["status"] == "Completed"])
            in_progress = len([t for t in partner_tasks if t["status"] == "In Progress"])
            not_started = len([t for t in partner_tasks if t["status"] == "Not Started"])
            delayed = len([t for t in partner_tasks if t["status"] == "Delayed"])
            cancelled = len([t for t in partner_tasks if t["status"] == "Cancelled"])
            
            partner_data.append({
                "Partner": partner,
                "Completed": completed,
                "In Progress": in_progress,
                "Not Started": not_started,
                "Delayed": delayed,
                "Cancelled": cancelled,
                "Total": len(partner_tasks)
            })
    
    partner_df = pd.DataFrame(partner_data)
    
    # Create stacked bar chart
    fig = px.bar(
        partner_df,
        x="Partner",
        y=["Completed", "In Progress", "Not Started", "Delayed", "Cancelled"],
        title="Task Distribution by Partner",
        color_discrete_map={
            "Completed": "green",
            "In Progress": "blue",
            "Not Started": "gray",
            "Delayed": "orange",
            "Cancelled": "red"
        },
        labels={"value": "Number of Tasks", "variable": "Status"},
        text_auto=True
    )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Number of Tasks",
        legend_title="Task Status",
        font=dict(size=12),
        xaxis={'categoryorder':'total descending'},
        margin=dict(t=50, b=150),
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def report_submission_chart(reports):
    if not reports:
        return None
    
    report_data = []
    for partner in PARTNERS:
        partner_reports = [r for r in reports if r["partner"] == partner]
        if partner_reports:
            submitted = len([r for r in partner_reports if r["status"] == "Submitted"])
            pending = len([r for r in partner_reports if r["status"] == "Pending"])
            draft = len([r for r in partner_reports if r["status"] == "Draft"])
            
            report_data.append({
                "Partner": partner,
                "Submitted": submitted,
                "Pending": pending,
                "Draft": draft,
                "Total": len(partner_reports),
                "Submission Rate": (submitted / len(partner_reports)) * 100 if len(partner_reports) > 0 else 0
            })
    
    report_df = pd.DataFrame(report_data)
    
    # Create bar chart
    fig = px.bar(
        report_df,
        x="Partner",
        y=["Submitted", "Pending", "Draft"],
        title="Report Submission Status by Partner",
        color_discrete_map={
            "Submitted": "green",
            "Pending": "orange",
            "Draft": "gray"
        },
        labels={"value": "Number of Reports", "variable": "Status"},
        text_auto=True
    )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Number of Reports",
        legend_title="Report Status",
        font=dict(size=12),
        margin=dict(t=50, b=150),
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def add_task(task_data):
    task_id = f"task_{len(st.session_state.tasks)+1}"
    new_task = {
        "id": task_id,
        **task_data,
        "comments": []
    }
    st.session_state.tasks.append(new_task)
    
    # Add notification
    new_notification = {
        "id": f"notif_{len(st.session_state.notifications)+1}",
        "user": task_data["assigned_to"],
        "message": f"New task assigned: {task_data['title']}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "read": False,
        "type": "task_assignment"
    }
    st.session_state.notifications.append(new_notification)
    
    return task_id

def edit_task(task_id, updated_data):
    for i, task in enumerate(st.session_state.tasks):
        if task["id"] == task_id:
            for key, value in updated_data.items():
                st.session_state.tasks[i][key] = value
            
            # Add notification if assigned to has changed
            if "assigned_to" in updated_data:
                new_notification = {
                    "id": f"notif_{len(st.session_state.notifications)+1}",
                    "user": updated_data["assigned_to"],
                    "message": f"Task reassigned to you: {st.session_state.tasks[i]['title']}",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "read": False,
                    "type": "task_assignment"
                }
                st.session_state.notifications.append(new_notification)
            
            return True
    return False

def delete_task(task_id):
    for i, task in enumerate(st.session_state.tasks):
        if task["id"] == task_id:
            st.session_state.tasks.pop(i)
            return True
    return False

def add_report(report_data):
    report_id = f"report_{len(st.session_state.reports)+1}"
    new_report = {
        "id": report_id,
        **report_data
    }
    st.session_state.reports.append(new_report)
    
    # Add notification for admin
    new_notification = {
        "id": f"notif_{len(st.session_state.notifications)+1}",
        "user": "Yildiz Technical University (YTU)",
        "message": f"New report submitted by {report_data['partner']}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "read": False,
        "type": "report_submission"
    }
    st.session_state.notifications.append(new_notification)
    
    return report_id

def edit_report(report_id, updated_data):
    for i, report in enumerate(st.session_state.reports):
        if report["id"] == report_id:
            for key, value in updated_data.items():
                st.session_state.reports[i][key] = value
            
            # Add notification if status changed to Submitted
            if "status" in updated_data and updated_data["status"] == "Submitted":
                new_notification = {
                    "id": f"notif_{len(st.session_state.notifications)+1}",
                    "user": "Yildiz Technical University (YTU)",
                    "message": f"Report {st.session_state.reports[i]['title']} submitted by {st.session_state.reports[i]['partner']}",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "read": False,
                    "type": "report_submission"
                }
                st.session_state.notifications.append(new_notification)
            
            return True
    return False

def delete_report(report_id):
    for i, report in enumerate(st.session_state.reports):
        if report["id"] == report_id:
            st.session_state.reports.pop(i)
            return True
    return False

def get_download_link(data, filename, text):
    """Generate a link to download data as a file"""
    json_str = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{filename}">{text}</a>'
    return href

def format_date(date_str):
    """Format date string to a more readable format"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d %b %Y")
    except:
        return date_str

def get_current_user_info():
    if not st.session_state.logged_in or not st.session_state.current_user:
        return None
    
    return next((u for u in st.session_state.users if u["username"] == st.session_state.current_user), None)

# Main App
def run_app():
    init_session_state()
    
    # Login screen
    if not st.session_state.logged_in:
        display_login()
        return
    
    # Main application after login
    user_info = get_current_user_info()
    organization = user_info["organization"]
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x100?text=TechSight", width=150)
        st.title("TechSight Project")
        
        st.markdown(f"**User:** {user_info['name']}")
        st.markdown(f"**Organization:** {organization}")
        st.markdown(f"**Role:** {user_info['role'].capitalize()}")
        
        menu_options = ["Dashboard", "Tasks", "Gantt Chart", "Reports", "Documents"]
        if st.session_state.is_admin:
            menu_options.append("Partner Management")
            menu_options.append("Settings")
        
        selected_menu = st.selectbox("Navigation", menu_options)
        
        notifications = get_user_notifications(st.session_state.current_user)
        unread_count = len([n for n in notifications if not n["read"]])
        
        if unread_count > 0:
            st.markdown(f"#### 📬 Notifications ({unread_count})")
            
            for notif in notifications:
                if not notif["read"]:
                    with st.container():
                        st.markdown(f"**{notif['message']}**")
                        st.caption(f"{notif['date']}")
                        st.markdown("---")
        
        if st.button("Logout"):
            logout_user()
            # st.experimental_rerun()
    
    # Main content
    if selected_menu == "Dashboard":
        display_dashboard(organization)
    elif selected_menu == "Tasks":
        display_tasks(organization)
    elif selected_menu == "Gantt Chart":
        display_gantt_chart(organization)
    elif selected_menu == "Reports":
        display_reports(organization)
    # elif selected_menu == "Documents":
    #     # display_documents(organization)
    # elif selected_menu == "Partner Management" and st.session_state.is_admin:
    #     # display_partner_management()
    # elif selected_menu == "Settings" and st.session_state.is_admin:
    #     # display_settings()

def display_login():
    st.title("TechSight Project Management Tool")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h2>Project Overview</h2>
            <p>TechSight is an EIT Higher Education Initiative project led by Yildiz Technical University (YTU) with multiple international partners.</p>
            <p>This tool helps manage project tasks, track progress, generate reports, and facilitate communication between partners.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>Project Partners</h3>
            <ul>
                <li>Yildiz Technical University (YTU) - Project Lead</li>
                <li>THE NEW WAY</li>
                <li>Ss. Cyril and Methodius University in Skopje</li>
                <li>Politecnico da Guarda</li>
                <li>HOCHSCHULE MAGDEBURG-STENDAL</li>
                <li>Center for the Promotion of Science</li>
                <li>Daugavpils Universitate</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", key="login_button"):
            if login_user(username, password):
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Default Login Credentials")
        st.markdown("**Admin:**")
        st.markdown("- Username: admin")
        st.markdown("- Password: admin123")
        
        st.markdown("**Partners:** (Example for YTU)")
        st.markdown("- Username: yildiz")
        st.markdown("- Password: yildiz123")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Note:** This is a demo version and real-world data may not be available.")
        st.markdown("---")
        st.markdown("**Contact:**")
        st.markdown("TechSight Team")
        st.markdown("Email: [techsight@example.com](mailto:techsight@example.com)")
        st.markdown("Phone: +1 123-456-7890")
        st.markdown("---")
        st.markdown("**License:**")
        st.markdown("This project is licensed under the MIT License.")
        st.markdown("---")
        st.markdown("**Disclaimer:**")
        st.markdown("This tool is provided as-is without any warranty or guarantee.")
        st.markdown("---")

def display_dashboard(organization):
    st.title("TechSight Project Dashboard")
    
    tasks = get_user_tasks(st.session_state.current_user)
    reports = get_user_reports(st.session_state.current_user)
    
    # Project Overview
    st.markdown("## Project Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Task metrics
    with col1:
        st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
        total_tasks = len(tasks)
        st.markdown("<h3>Total Tasks</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{total_tasks}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
        completed_tasks = len([t for t in tasks if t["status"] == "Completed"])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.markdown("<h3>Task Completion Rate</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{completion_rate:.1f}%</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
        in_progress = len([t for t in tasks if t["status"] == "In Progress"])
        st.markdown("<h3>Tasks In Progress</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{in_progress}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
        total_reports = len(reports)
        submitted_reports = len([r for r in reports if r["status"] == "Submitted"])
        report_rate = (submitted_reports / total_reports * 100) if total_reports > 0 else 0
        st.markdown("<h3>Report Submission Rate</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{report_rate:.1f}%</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts
    st.markdown("## Project Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = task_progress_chart(tasks)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if st.session_state.is_admin:
            fig = partner_task_distribution(tasks)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            # For partners, show their task categories distribution
            task_categories = {}
            for task in tasks:
                category = task["category"]
                if category not in task_categories:
                    task_categories[category] = 0
                task_categories[category] += 1
            
            df = pd.DataFrame({"Category": list(task_categories.keys()), "Count": list(task_categories.values())})
            if not df.empty:
                fig = px.bar(
                    df,
                    x="Category",
                    y="Count",
                    title=f"Tasks by Category for {organization}",
                    color="Category"
                )
                fig.update_layout(xaxis_title="", yaxis_title="Number of Tasks")
                st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activities
    st.markdown("## Recent Activities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Recent Tasks")
        recent_tasks = sorted(tasks, key=lambda x: x["start_date"], reverse=True)[:5]
        
        if recent_tasks:
            for task in recent_tasks:
                st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 10px; border-radius: 5px; background-color: {'#e6ffe6' if task['status'] == 'Completed' else '#fff3e6' if task['status'] == 'Delayed' else '#e6f7ff' if task['status'] == 'In Progress' else '#f2f2f2'};">
                    <strong>{task['title']}</strong><br>
                    Status: {task['status']}<br>
                    Progress: {task['progress']}%<br>
                    Due: {format_date(task['end_date'])}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent tasks found.")
    
    with col2:
        st.markdown("### Recent Reports")
        recent_reports = sorted(reports, key=lambda x: x["submission_date"], reverse=True)[:5]
        
        if recent_reports:
            for report in recent_reports:
                st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 10px; border-radius: 5px; background-color: {'#e6ffe6' if report['status'] == 'Submitted' else '#fff3e6' if report['status'] == 'Pending' else '#f2f2f2'};">
                    <strong>{report['title']}</strong><br>
                    Partner: {report['partner']}<br>
                    Status: {report['status']}<br>
                    Submission Date: {format_date(report['submission_date'])}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent reports found.")
    
    # Upcoming Deadlines
    st.markdown("## Upcoming Deadlines")
    today = datetime.now().date()
    upcoming_tasks = sorted(
        [t for t in tasks if t["status"] not in ["Completed", "Cancelled"] and datetime.strptime(t["end_date"], "%Y-%m-%d").date() >= today],
        key=lambda x: x["end_date"]
    )[:5]
    
    if upcoming_tasks:
        for task in upcoming_tasks:
            due_date = datetime.strptime(task["end_date"], "%Y-%m-%d").date()
            days_left = (due_date - today).days
            
            st.markdown(f"""
            <div style="padding: 10px; margin-bottom: 10px; border-radius: 5px; background-color: {'#ffe6e6' if days_left <= 3 else '#fff3e6' if days_left <= 7 else '#f9f9f9'};">
                <strong>{task['title']}</strong> - Due in {days_left} days<br>
                Assigned to: {task['assigned_to']}<br>
                Status: {task['status']}<br>
                Progress: {task['progress']}%
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No upcoming deadlines.")

def display_tasks(organization):
    st.title("Task Management")
    
    # Get tasks relevant to the current user
    tasks = get_user_tasks(st.session_state.current_user)
    
    # Task filtering options
    st.markdown("### Filter Tasks")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.multiselect("Status", TASK_STATUS, default=TASK_STATUS)
    
    with col2:
        filter_category = st.multiselect("Category", TASK_CATEGORIES, default=TASK_CATEGORIES)
    
    with col3:
        if st.session_state.is_admin:
            filter_partner = st.multiselect("Partner", PARTNERS, default=PARTNERS)
        else:
            filter_partner = [organization]
    
    # Apply filters
    filtered_tasks = [
        task for task in tasks 
        if task["status"] in filter_status 
        and task["category"] in filter_category
        and task["assigned_to"] in filter_partner
    ]
    
    # Sort options
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by",
            ["Start Date", "End Date", "Status", "Progress", "Priority"]
        )
    
    with sort_col2:
        sort_ascending = st.checkbox("Ascending order", value=True)
    
    # Apply sorting
    if sort_by == "Start Date":
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x["start_date"], reverse=not sort_ascending)
    elif sort_by == "End Date":
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x["end_date"], reverse=not sort_ascending)
    elif sort_by == "Status":
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x["status"], reverse=not sort_ascending)
    elif sort_by == "Progress":
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x["progress"], reverse=not sort_ascending)
    elif sort_by == "Priority":
        priority_map = {"High": 3, "Medium": 2, "Low": 1}
        filtered_tasks = sorted(filtered_tasks, key=lambda x: priority_map.get(x["priority"], 0), reverse=not sort_ascending)
    
    # Create new task
    st.markdown("### Task Management")
    
    if st.session_state.is_admin:
        if st.button("Add New Task"):
            st.session_state.show_task_form = True
    
    # Task creation form
    if st.session_state.is_admin and st.session_state.get("show_task_form", False):
        st.markdown("### Create New Task")
        with st.form(key="task_form"):
            task_title = st.text_input("Task Title")
            task_description = st.text_area("Task Description")
            
            col1, col2 = st.columns(2)
            with col1:
                task_assigned_to = st.selectbox("Assigned To", PARTNERS)
                task_category = st.selectbox("Category", TASK_CATEGORIES)
                task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            
            with col2:
                task_start_date = st.date_input("Start Date")
                task_end_date = st.date_input("End Date")
                task_status = st.selectbox("Status", TASK_STATUS)
            
            task_progress = st.slider("Progress (%)", 0, 100, 0)
            
            submit_button = st.form_submit_button("Create Task")
            
            if submit_button:
                if not task_title:
                    st.error("Task title is required.")
                elif task_end_date < task_start_date:
                    st.error("End date cannot be before start date.")
                else:
                    task_data = {
                        "title": task_title,
                        "description": task_description,
                        "assigned_to": task_assigned_to,
                        "assigned_by": get_current_user_info()["organization"],
                        "category": task_category,
                        "start_date": task_start_date.strftime("%Y-%m-%d"),
                        "end_date": task_end_date.strftime("%Y-%m-%d"),
                        "status": task_status,
                        "progress": task_progress,
                        "priority": task_priority
                    }
                    
                    add_task(task_data)
                    st.success("Task created successfully!")
                    st.session_state.show_task_form = False
                    # st.experimental_rerun()
        
        if st.button("Cancel"):
            st.session_state.show_task_form = False
            # st.experimental_rerun()
    
    # Task list
    st.markdown("### Task List")
    st.markdown(f"Showing {len(filtered_tasks)} tasks")
    
    if filtered_tasks:
        for task in filtered_tasks:
            with st.expander(f"{task['title']} ({task['status']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {task['description']}")
                    st.markdown(f"**Category:** {task['category']}")
                    st.markdown(f"**Assigned To:** {task['assigned_to']}")
                    st.markdown(f"**Assigned By:** {task['assigned_by']}")
                    st.markdown(f"**Priority:** {task['priority']}")
                
                with col2:
                    st.markdown(f"**Start Date:** {format_date(task['start_date'])}")
                    st.markdown(f"**End Date:** {format_date(task['end_date'])}")
                    st.markdown(f"**Status:** {task['status']}")
                    st.progress(task['progress'] / 100)
                    st.markdown(f"**Progress:** {task['progress']}%")
                
                # Task actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"Update Progress", key=f"update_{task['id']}"):
                        st.session_state.update_task_id = task["id"]
                        st.session_state.update_task_progress = True
                
                with col2:
                    if st.session_state.is_admin and st.button(f"Edit Task", key=f"edit_{task['id']}"):
                        st.session_state.edit_task_id = task["id"]
                        st.session_state.show_edit_form = True
                
                with col3:
                    if st.session_state.is_admin and st.button(f"Delete Task", key=f"delete_{task['id']}"):
                        if delete_task(task["id"]):
                            st.success("Task deleted successfully!")
                            # st.experimental_rerun()
                
                # Comments section
                st.markdown("#### Comments")
                
                for comment in task.get("comments", []):
                    st.markdown(f"""
                    <div style="padding: 10px; margin-bottom: 10px; border-radius: 5px; background-color: #f9f9f9;">
                        <strong>{comment['user']}</strong> - {comment['date']}<br>
                        {comment['text']}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add comment
                new_comment = st.text_area("Add a comment", key=f"comment_{task['id']}")
                if st.button("Post Comment", key=f"post_{task['id']}"):
                    for i, t in enumerate(st.session_state.tasks):
                        if t["id"] == task["id"]:
                            if "comments" not in st.session_state.tasks[i]:
                                st.session_state.tasks[i]["comments"] = []
                            
                            st.session_state.tasks[i]["comments"].append({
                                "user": get_current_user_info()["organization"],
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "text": new_comment
                            })
                            
                            # Notify task owner if not the commenter
                            if task["assigned_to"] != get_current_user_info()["organization"]:
                                new_notification = {
                                    "id": f"notif_{len(st.session_state.notifications)+1}",
                                    "user": task["assigned_to"],
                                    "message": f"New comment on task: {task['title']}",
                                    "date": datetime.now().strftime("%Y-%m-%d"),
                                    "read": False,
                                    "type": "comment"
                                }
                                st.session_state.notifications.append(new_notification)
                            
                            st.success("Comment added!")
                            # st.experimental_rerun()
                            break
    else:
        st.info("No tasks found with the selected filters.")
    
    # Task progress update form
    if hasattr(st.session_state, "update_task_progress") and st.session_state.update_task_progress:
        task_id = st.session_state.update_task_id
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if task:
            st.markdown("### Update Task Progress")
            
            with st.form(key="progress_form"):
                new_progress = st.slider("Progress (%)", 0, 100, int(task["progress"]))
                new_status = st.selectbox("Status", TASK_STATUS, TASK_STATUS.index(task["status"]))
                
                status_note = st.text_area("Status Note (Optional)")
                
                submit_button = st.form_submit_button("Update Task")
                
                if submit_button:
                    updated_data = {
                        "progress": new_progress,
                        "status": new_status
                    }
                    
                    if edit_task(task_id, updated_data):
                        # Add comment if there's a status note
                        if status_note:
                            for i, t in enumerate(st.session_state.tasks):
                                if t["id"] == task_id:
                                    if "comments" not in st.session_state.tasks[i]:
                                        st.session_state.tasks[i]["comments"] = []
                                    
                                    st.session_state.tasks[i]["comments"].append({
                                        "user": get_current_user_info()["organization"],
                                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                        "text": f"Status update: {status_note}"
                                    })
                                    break
                        
                        st.success("Task updated successfully!")
                        st.session_state.update_task_progress = False
                        # st.experimental_rerun()
            
            if st.button("Cancel Update"):
                st.session_state.update_task_progress = False
                # st.experimental_rerun()
    
    # Task edit form
    if st.session_state.is_admin and hasattr(st.session_state, "show_edit_form") and st.session_state.show_edit_form:
        task_id = st.session_state.edit_task_id
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if task:
            st.markdown("### Edit Task")
            
            with st.form(key="edit_task_form"):
                task_title = st.text_input("Task Title", value=task["title"])
                task_description = st.text_area("Task Description", value=task["description"])
                
                col1, col2 = st.columns(2)
                with col1:
                    task_assigned_to = st.selectbox("Assigned To", PARTNERS, PARTNERS.index(task["assigned_to"]))
                    task_category = st.selectbox("Category", TASK_CATEGORIES, TASK_CATEGORIES.index(task["category"]))
                    task_priority = st.selectbox("Priority", ["High", "Medium", "Low"], ["High", "Medium", "Low"].index(task["priority"]))
                
                with col2:
                    task_start_date = st.date_input("Start Date", datetime.strptime(task["start_date"], "%Y-%m-%d"))
                    task_end_date = st.date_input("End Date", datetime.strptime(task["end_date"], "%Y-%m-%d"))
                    task_status = st.selectbox("Status", TASK_STATUS, TASK_STATUS.index(task["status"]))
                
                task_progress = st.slider("Progress (%)", 0, 100, task["progress"])
                
                submit_button = st.form_submit_button("Update Task")
                
                if submit_button:
                    if not task_title:
                        st.error("Task title is required.")
                    elif task_end_date < task_start_date:
                        st.error("End date cannot be before start date.")
                    else:
                        updated_data = {
                            "title": task_title,
                            "description": task_description,
                            "assigned_to": task_assigned_to,
                            "category": task_category,
                            "start_date": task_start_date.strftime("%Y-%m-%d"),
                            "end_date": task_end_date.strftime("%Y-%m-%d"),
                            "status": task_status,
                            "progress": task_progress,
                            "priority": task_priority
                        }
                        
                        if edit_task(task_id, updated_data):
                            st.success("Task updated successfully!")
                            st.session_state.show_edit_form = False
                            # st.experimental_rerun()
            
            if st.button("Cancel Edit"):
                st.session_state.show_edit_form = False
                # st.experimental_rerun()

def display_gantt_chart(organization):
    st.title("Project Gantt Chart")
    
    # Get tasks relevant to the current user
    tasks = get_user_tasks(st.session_state.current_user)
    
    # Filtering options for Gantt chart
    st.markdown("### Filter Gantt Chart")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.multiselect("Status", TASK_STATUS, default=TASK_STATUS)
    
    with col2:
        filter_category = st.multiselect("Category", TASK_CATEGORIES, default=TASK_CATEGORIES)
    
    with col3:
        if st.session_state.is_admin:
            filter_partner = st.multiselect("Partner", PARTNERS, default=PARTNERS)
        else:
            filter_partner = [organization]
    
    # Apply filters
    filtered_tasks = [
        task for task in tasks 
        if task["status"] in filter_status 
        and task["category"] in filter_category
        and task["assigned_to"] in filter_partner
    ]
    
    # Create Gantt chart
    gantt_fig = create_gantt_chart(filtered_tasks)
    
    if gantt_fig:
        st.plotly_chart(gantt_fig, use_container_width=True)
    else:
        st.info("No tasks found to display in Gantt chart.")
    
    # Task statistics
    st.markdown("### Task Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Task category distribution
        categories = {}
        for task in filtered_tasks:
            category = task["category"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        if categories:
            df = pd.DataFrame({"Category": list(categories.keys()), "Count": list(categories.values())})
            fig = px.pie(
                df,
                values="Count",
                names="Category",
                title="Tasks by Category",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Task priority distribution
        priorities = {}
        for task in filtered_tasks:
            priority = task["priority"]
            if priority not in priorities:
                priorities[priority] = 0
            priorities[priority] += 1
        
        if priorities:
            df = pd.DataFrame({"Priority": list(priorities.keys()), "Count": list(priorities.values())})
            fig = px.bar(
                df,
                x="Priority",
                y="Count",
                title="Tasks by Priority",
                color="Priority",
                color_discrete_map={
                    "High": "red",
                    "Medium": "orange",
                    "Low": "blue"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Timeline view
    st.markdown("### Project Timeline")
    
    if filtered_tasks:
        # Sort tasks by start date
        sorted_tasks = sorted(filtered_tasks, key=lambda x: x["start_date"])
        
        # Get earliest and latest dates
        start_dates = [datetime.strptime(task["start_date"], "%Y-%m-%d") for task in sorted_tasks]
        end_dates = [datetime.strptime(task["end_date"], "%Y-%m-%d") for task in sorted_tasks]
        
        min_date = min(start_dates)
        max_date = max(end_dates)
        
        # Generate timeline data
        timeline_data = []
        for i, task in enumerate(sorted_tasks):
            start = datetime.strptime(task["start_date"], "%Y-%m-%d")
            end = datetime.strptime(task["end_date"], "%Y-%m-%d")
            
            timeline_data.append({
                "Task": task["title"],
                "Start": start,
                "End": end,
                "Partner": task["assigned_to"],
                "Status": task["status"]
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create timeline chart
        fig = px.timeline(
            timeline_df, 
            x_start="Start", 
            x_end="End", 
            y="Task",
            color="Status",
            color_discrete_map={
                "Completed": "green",
                "In Progress": "blue",
                "Not Started": "gray",
                "Delayed": "orange",
                "Cancelled": "red"
            },
            hover_data=["Partner"]
        )
        
        fig.update_layout(
            xaxis=dict(
                type='date',
                title="Date",
                tickformat="%d %b %Y",
                title_font=dict(size=14)
            ),
            yaxis=dict(
                title="",
                tickangle=0,
                automargin=True
            ),
            height=max(400, len(sorted_tasks) * 30),
            margin=dict(t=50, b=50, l=20, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tasks found to display in the timeline.")

def display_reports(organization):
    st.title("Reports Management")
    
    # Get reports relevant to the current user
    reports = get_user_reports(st.session_state.current_user)
    
    # Report filtering options
    st.markdown("### Filter Reports")
    col1, col2 = st.columns(2)
    
    with col1:
        filter_status = st.multiselect("Status", ["Submitted", "Pending", "Draft"], default=["Submitted", "Pending", "Draft"])
    
    with col2:
        if st.session_state.is_admin:
            filter_partner = st.multiselect("Partner", PARTNERS, default=PARTNERS)
        else:
            filter_partner = [organization]
    
    # Apply filters
    filtered_reports = [
        report for report in reports 
        if report["status"] in filter_status 
        and report["partner"] in filter_partner
    ]
    
    # Create new report
    st.markdown("### Report Management")
    
    if not st.session_state.is_admin:  # Only partners can create reports
        if st.button("Create New Report"):
            st.session_state.show_report_form = True
    
    # Report creation form
    if not st.session_state.is_admin and st.session_state.get("show_report_form", False):
        st.markdown("### Create New Report")
        with st.form(key="report_form"):
            today = datetime.now().date()
            two_weeks_ago = today - timedelta(days=14)
            
            report_title = st.text_input("Report Title", value=f"Biweekly Report {today.strftime('%d %b %Y')}")
            
            col1, col2 = st.columns(2)
            with col1:
                period_start = st.date_input("Period Start", value=two_weeks_ago)
            
            with col2:
                period_end = st.date_input("Period End", value=today)
            
            activities_completed = st.text_area("Completed Activities")
            activities_in_progress = st.text_area("Ongoing Activities")
            activities_planned = st.text_area("Planned Activities")
            issues = st.text_area("Issues Encountered (Optional)")
            
            report_status = st.selectbox("Status", ["Draft", "Pending", "Submitted"])
            
            submit_button = st.form_submit_button("Create Report")
            
            if submit_button:
                if not report_title:
                    st.error("Report title is required.")
                elif period_end < period_start:
                    st.error("Period end date cannot be before start date.")
                else:
                    report_data = {
                        "title": report_title,
                        "partner": organization,
                        "submission_date": today.strftime("%Y-%m-%d"),
                        "period_start": period_start.strftime("%Y-%m-%d"),
                        "period_end": period_end.strftime("%Y-%m-%d"),
                        "activities_completed": activities_completed,
                        "activities_in_progress": activities_in_progress,
                        "activities_planned": activities_planned,
                        "issues": issues,
                        "status": report_status
                    }
                    
                    add_report(report_data)
                    st.success("Report created successfully!")
                    st.session_state.show_report_form = False
                    # st.experimental_rerun()
        
        if st.button("Cancel"):
            st.session_state.show_report_form = False
            # st.experimental_rerun()
    
    # Report submission chart (for admin only)
    if st.session_state.is_admin:
        st.markdown("### Report Submission Status")
        submission_fig = report_submission_chart(reports)
        if submission_fig:
            st.plotly_chart(submission_fig, use_container_width=True)
    
    # Report list
    st.markdown("### Report List")
    st.markdown(f"Showing {len(filtered_reports)} reports")
    
    if filtered_reports:
        # Sort by submission date, newest first
        sorted_reports = sorted(filtered_reports, key=lambda x: x["submission_date"], reverse=True)
        
        for report in sorted_reports:
            with st.expander(f"{report['title']} - {report['partner']} ({report['status']})"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**Partner:** {report['partner']}")
                    st.markdown(f"**Submission Date:** {format_date(report['submission_date'])}")
                    st.markdown(f"**Status:** {report['status']}")
                
                with col2:
                    st.markdown(f"**Period:** {format_date(report['period_start'])} to {format_date(report['period_end'])}")
                
                st.markdown("#### Completed Activities")
                st.markdown(report['activities_completed'] or "None")
                st.markdown("#### Ongoing Activities")
                st.markdown(report['activities_in_progress'] or "None")
                st.markdown("#### Planned Activities")
                st.markdown(report['activities_planned'] or "None")
                st.markdown("#### Issues Encountered")
                st.markdown(report['issues'] or "None")
                st.markdown("")
                st.markdown("---")
