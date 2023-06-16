import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title('Science Mill Student Summer Camp Dashboard')

# Raw GitHub link for your pre and post training data
url_pre = 'https://raw.githubusercontent.com/henryco94/scienceMillDash/main/june12_pre.csv'
url_post = 'https://github.com/henryco94/studentdash/blob/main/stu_post_jun16.csv'

# Load the pre and post survey data
df_pre = pd.read_csv(url_pre)
df_post = pd.read_csv(url_post)

# Drop the specified columns
columns_to_drop = ['#', 'Responder','Person', 'Teacher Number', 'Type', 'Approval Status', 'Date','Unnamed: 0', 'Student Number']
df_pre = df_pre.drop(columns=columns_to_drop, errors='ignore')
df_post = df_post.drop(columns=columns_to_drop, errors='ignore')

# Define a mapping from the full responses to the broad categories
career_mapping = {
    'General Engineer - General engineers use principles of science and mathematics to solve technical problems in various sectors. They could work in several branches of engineering, such as mechanical, civil, chemical, or electrical, designing and building structures, machines, devices, systems, and processes.': 'General Engineer',
    'Healthcare Professional - This can encompass a wide variety of career paths, from becoming a physician or nurse, to more specialized roles like medical technologist or radiologist. These professionals use scientific principles to diagnose and treat illnesses, conduct medical research, or operate complex medical equipment.': 'Healthcare Professional',
    'Software Developer - Software developers design, build, and maintain computer software. They might create everything from operating systems and network controls to mobile apps and cloud-based services.': 'Software Developer',
    'Environmental Scientist - Environmental scientists use their knowledge of the natural sciences to protect the environment and human health. They may clean up polluted areas, advise policymakers, or work with industry to reduce waste and pollution.': 'Environmental Scientist',
    'Technical Vocational Professions - This can include a range of hands-on STEM professions that typically require a two-year degree, certification, or apprenticeship, rather than a traditional four-year college degree. This might include electricians, who work with electrical systems and networks; HVAC technicians, who install and repair heating and cooling systems; or automotive technicians, who service and repair vehicles.': 'Technical Vocational Professions'
}

# Replace the full responses with the broad categories in the post-survey DataFrame
df_post.replace(career_mapping, inplace=True)

# Get list of all districts
districts = list(df_pre['District'].unique())
districts.insert(0, 'All')

# Mapping between pre and post survey questions
question_mapping = {
    'When I work in a group, or as part of a team I like ... Sharing my ideas, tasks and responsibilities with the group': 'After participating in this program, do you feel more comfortable sharing your ideas, tasks, and responsibilities when working in a group or as part of a team?',
    'I try new things even if they look hard': 'After coming to this program, I try new things even if they look hard.',
    'I’m good at solving problems': 'After coming to this program, I’m a better problem solver.',
    'I believe I can be successful in a STEM (Science, Technology, Engineering or Math) career': 'I believe I can be successful in a STEM (Science, Technology, Engineering or Math) career.',
    'I think science, technology, engineering or math can be fun': 'I think science, technology, engineering or math can be fun.',
    #'How much do I think I know about careers in STEM?': 'How much do I think I know about careers in STEM?',
    'When I grow up I would be interested in working in a STEM career or job': 'When I grow up I would be interested in working in a STEM career or job.',
    'I feel like I belong in STEM': 'I feel like I belong in STEM'
}
# Dropdown to select a district
selected_district = st.selectbox('Select a district:', districts)

# Filter the data for the selected district
if selected_district != 'All':
    df_pre = df_pre[df_pre['District'] == selected_district]
    df_post = df_post[df_post['District'] == selected_district]

# Dropdown to select the survey type
survey_type = st.selectbox('Select a survey type:', ['Pre only', 'Post only', 'Mapped'])

# Determine the list of questions to display based on the selected survey type
if survey_type == 'Pre only':
    questions = [q for q in list(df_pre.columns) if q not in question_mapping.keys()]
elif survey_type == 'Post only':
    questions = [q for q in list(df_post.columns) if q not in question_mapping.values()]
elif survey_type == 'Mapped':
    questions = list(question_mapping.keys())

# Dropdown to select a question
selected_question = st.selectbox('Select a question:', questions)

# Function to add percentage on the bars
def add_percentage(ax):
    for p in ax.patches:
        height = p.get_height()
        ax.text(p.get_x()+p.get_width()/2.,
                height + 0.01,
                '{:1.1f}%'.format(height*100),
                ha="center")

# If the selected question is a mapped question
if selected_question in question_mapping.keys():
    fig, ax = plt.subplots()
    post_question = question_mapping[selected_question]
    pre_counts = df_pre[selected_question].value_counts(normalize=True).reindex(['No', 'Mostly No', 'Mostly Yes', 'Yes'])
    post_counts = df_post[post_question].value_counts(normalize=True).reindex(['No', 'Mostly No', 'Mostly Yes', 'Yes'])
    counts = pd.DataFrame({'Pre': pre_counts, 'Post': post_counts})
    counts.plot(kind='bar', color=['blue', 'green'], figsize=(10, 6), ax=ax)
    plt.title(f'Pre vs Post: {selected_question}')
    plt.ylabel('Proportion of Responses')
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
    add_percentage(ax)
    plt.tight_layout()
    st.pyplot(fig)

elif selected_question in df_pre.columns:
    fig, ax = plt.subplots()
    counts = df_pre[selected_question].value_counts(normalize=True)
    if len(counts) > 0:
        counts.plot(kind='bar', color='blue', figsize=(10, 6), ax=ax)
        plt.title(f'Pre: {selected_question}')
        plt.ylabel('Proportion of Responses')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
        add_percentage(ax)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write("No responses for this question.")

elif selected_question in df_post.columns:
    fig, ax = plt.subplots()
    counts = df_post[selected_question].value_counts(normalize=True)
    if len(counts) > 0:
        counts.plot(kind='bar', color='green', figsize=(10, 6), ax=ax)
        plt.title(f'Post: {selected_question}')
        plt.ylabel('Proportion of Responses')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
        add_percentage(ax)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write("No responses for this question.")
