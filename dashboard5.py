import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title('Science Mill Student Summer Camp Dashboard')

def get_camp_dates(file_path):
    data = pd.read_excel(file_path, sheet_name='Transfer')
    data.columns = data.columns.str.strip().str.lower()  # normalize column names
    return data['camp dates'].dropna().unique()

def read_csv(file_path):
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip().str.lower()

    # Normalize 'district' column
    if 'district' in data.columns:
        data['district'] = data['district'].str.lower().str.strip()

    # Remove empty rows and undesired districts
    data = data.dropna(subset=['district'])
    data = data[~data['district'].str.startswith(("-", "inactive"))]

    return data

def read_excel(file_path, camp_dates):
    data = pd.read_excel(file_path, sheet_name='Transfer')
    data.columns = data.columns.str.strip().str.lower()

    # Normalize 'district' and 'camp dates' columns
    if 'district' in data.columns:
        data['district'] = data['district'].str.lower().str.strip()
    if 'camp dates' in data.columns:
        data['camp dates'] = data['camp dates'].str.strip()

    # Remove empty rows and undesired districts
    data = data.dropna(subset=['district', 'camp dates'])
    data = data[data['camp dates'] == camp_dates]
    data = data[~data['district'].str.startswith(("-", "inactive"))]

    return data

def compare_surveys(pre_file_path, post_file_path, third_file_path, camp_dates):
    pre_data = read_csv(pre_file_path)
    post_data = read_csv(post_file_path)
    third_data = read_excel(third_file_path, camp_dates)

    pre_data = pre_data[['responder', 'district']]
    post_data = post_data[['responder', 'district']]
    third_data = third_data[['district', 'number of students', 'present']]

    # If there are null values in the "Present" column, return None
    if third_data['present'].isnull().values.any():
        return None

    pre_counts = pre_data['district'].value_counts().reset_index()
    post_counts = post_data['district'].value_counts().reset_index()

    pre_counts.columns = ['district', 'count_pre']
    post_counts.columns = ['district', 'count_post']

    merged_data = pd.merge(pre_counts, post_counts, on='district', how='outer')
    third_data.columns = ['district', 'count_enroll', 'count_present']
    merged_data = pd.merge(merged_data, third_data, on='district', how='outer')
    merged_data = merged_data.fillna(0)

    fig = go.Figure(data=[
        go.Bar(name='Pre', x=merged_data['district'], y=merged_data['count_pre']),
        go.Bar(name='Post', x=merged_data['district'], y=merged_data['count_post']),
        go.Bar(name='Enrollment', x=merged_data['district'], y=merged_data['count_enroll']),
        go.Bar(name='Present', x=merged_data['district'], y=merged_data['count_present'])
    ])

    fig.update_layout(barmode='group',
                      xaxis_title='District',
                      yaxis_title='Count',
                      title=f'Pre vs Post Survey Counts, Enrollment Numbers, and Presence for Camp Dates: {camp_dates}')

    return fig  # return the figure


# Sidebar selectbox for dashboard functionality
dashboard_function = st.sidebar.selectbox('Select a function:', ['Survey Analysis', 'Survey Completion'])

if dashboard_function == 'Survey Analysis':
    # Load the pre and post survey data
     # Raw GitHub link for your pre and post training data
    url_pre = 'https://raw.githubusercontent.com/henryco94/scienceMillDash/main/concatenated.csv'
    url_post = 'https://raw.githubusercontent.com/henryco94/scienceMillDash/main/june12_post.csv'

    # Load the pre and post survey data
    df_pre = pd.read_csv(url_pre)
    df_post = pd.read_csv(url_post)

    # Drop the specified columns
    columns_to_drop = ['#', 'Responder', 'Person', 'Teacher Number', 'Type', 'Approval Status', 'Date', 'Unnamed: 0',
                       'Student Number']
    df_pre = df_pre.drop(columns=columns_to_drop, errors='ignore')
    df_post = df_post.drop(columns=columns_to_drop, errors='ignore')

    # Get list of all districts
    districts = list(df_pre['District'].unique())
    districts.insert(0, 'All')

    # Mapping between pre and post survey questions

    # Mapping from full responses to broad career categories
    career_mapping = {
        'General Engineer - General engineers use principles of science and mathematics to solve technical problems in various sectors. They could work in several branches of engineering, such as mechanical, civil, chemical, or electrical, designing and building structures, machines, devices, systems, and processes.': 'General Engineer',
        'Healthcare Professional - This can encompass a wide variety of career paths, from becoming a physician or nurse, to more specialized roles like medical technologist or radiologist. These professionals use scientific principles to diagnose and treat illnesses, conduct medical research, or operate complex medical equipment.': 'Healthcare Professional',
        'Software Developer - Software developers design, build, and maintain computer software. They might create everything from operating systems and network controls to mobile apps and cloud-based services.': 'Software Developer',
        'Environmental Scientist - Environmental scientists use their knowledge of the natural sciences to protect the environment and human health. They may clean up polluted areas, advise policymakers, or work with industry to reduce waste and pollution.': 'Environmental Scientist',
        'Technical Vocational Professions - This can include a range of hands-on STEM professions that typically require a two-year degree, certification, or apprenticeship, rather than a traditional four-year college degree. This might include electricians, who work with electrical systems and networks; HVAC technicians, who install and repair heating and cooling systems; or automotive technicians, who service and repair vehicles.': 'Technical Vocational Professions'
    }

    # Replace the full responses with the broad career categories in the post-survey DataFrame
    df_post.replace(career_mapping, inplace=True)

    question_mapping = {
        'I try new things even if they look hard': 'After coming to this program, I try new things even if they look hard.',
        'I’m good at solving problems': 'After coming to this program, I’m a better problem solver.',
        'I believe I can be successful in a STEM (Science, Technology, Engineering or Math) career': 'I believe I can be successful in a STEM (Science, Technology, Engineering or Math) career.',
        'I think science, technology, engineering or math can be fun': 'I think science, technology, engineering or math can be fun.',
        'How much do I think I know about careers in STEM?': 'How much do I think I know about careers in STEM?',
        'When I grow up I would be interested in working in a STEM career or job': 'When I grow up I would be interested in working in a STEM career or job.',
    }

    # Dropdown to select a district
    selected_district = st.selectbox('Select a district:', districts)

    # Filter the data for the selected district
    if selected_district != 'All':
        df_pre = df_pre[df_pre['District'] == selected_district]
        df_post = df_post[df_post['District'] == selected_district]

    # Dropdown to select the survey type
    survey_type = st.selectbox('Select a survey type:', ['Pre only', 'Post only', 'Mapped'])

    # List of all questions in the pre and post survey data
    mapped_questions = list(question_mapping.keys()) + list(question_mapping.values())
    unmapped_questions_pre = [q for q in list(df_pre.columns) if q not in mapped_questions]
    unmapped_questions_post = [q for q in list(df_post.columns) if q not in mapped_questions]

    # Determine the list of questions to display based on the selected survey type
    if survey_type == 'Pre only':
        questions = unmapped_questions_pre
    elif survey_type == 'Post only':
        questions = unmapped_questions_post
    elif survey_type == 'Mapped':
        questions = mapped_questions

    # Dropdown to select a question
    selected_question = st.selectbox('Select a question:', questions)


    # Function to add percentage on the bars
    def add_percentage(ax):
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width() / 2.,
                    height + 0.01,
                    '{:1.1f}%'.format(height * 100),
                    ha="center")


    # If the selected question is a mapped question
    if selected_question in question_mapping.keys() or selected_question in question_mapping.values():
        fig, ax = plt.subplots()
        # Identify the pre and post question pair
        pre_question = [k for k, v in question_mapping.items() if v == selected_question][
            0] if selected_question in question_mapping.values() else selected_question
        post_question = question_mapping[pre_question]

        # Count the responses for the pre and post survey questions
        pre_counts = df_pre[pre_question].value_counts(normalize=True)
        post_counts = df_post[post_question].value_counts(normalize=True)

        # Create a DataFrame with the response counts for both surveys
        counts = pd.DataFrame({'Pre': pre_counts, 'Post': post_counts})

        # Plot a grouped bar chart with percentages
        counts.plot(kind='bar', color=['blue', 'green'], figsize=(10, 6), ax=ax)
        plt.title(f'Pre vs Post: {pre_question}')
        plt.ylabel('Proportion of Responses')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
        add_percentage(ax)
        plt.tight_layout()
        st.pyplot(fig)

    # If the selected question is in the pre survey data, plot a bar chart with percentages
    elif selected_question in df_pre.columns:
        fig, ax = plt.subplots()
        df_pre[selected_question].value_counts(normalize=True).plot(kind='bar', color='blue', figsize=(10, 6), ax=ax)
        plt.title(f'Pre: {selected_question}')
        plt.ylabel('Proportion of Responses')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
        add_percentage(ax)
        plt.tight_layout()
        st.pyplot(fig)

    # If the selected question is in the post survey data, plot a bar chart with percentages
    elif selected_question in df_post.columns:
        fig, ax = plt.subplots()
        df_post[selected_question].value_counts(normalize=True).plot(kind='bar', color='green', figsize=(10, 6), ax=ax)
        plt.title(f'Post: {selected_question}')
        plt.ylabel('Proportion of Responses')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
        add_percentage(ax)
        plt.tight_layout()
        st.pyplot(fig)
# Your existing dashboard functionality goes here...
elif dashboard_function == 'Survey Completion':
    
    url_pre = 'https://raw.githubusercontent.com/henryco94/scienceMillDash/main/concatenated.csv'
    url_post = 'https://raw.githubusercontent.com/henryco94/scienceMillDash/main/june12_post.csv'
    
    pre_file_path = pd.read_csv(url_pre)
    post_file_path = pd.read_csv(url_post)
    third_file_path = '2023 Summer Camp Enrollment Dashboard.xlsx'

    # Get the available camp dates
    available_camp_dates = get_camp_dates(third_file_path)

    # Sidebar for selecting camp dates
    selected_camp_date = st.sidebar.selectbox("Select camp dates:", options=available_camp_dates)

    if pd.isnull(selected_camp_date):
        st.write("Data coming soon...")
    else:
        fig = compare_surveys(pre_file_path, post_file_path, third_file_path, selected_camp_date)

        # If fig is None, display the message "Data Available Soon"
        if fig is None:
            st.write("Data Available Soon")
        else:
            st.plotly_chart(fig)  # use this line to display the figure
