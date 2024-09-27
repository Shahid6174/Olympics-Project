import streamlit as st
import pandas as pd
import preprocessor, helper
import seaborn as sns
import matplotlib.pyplot as plt 
import plotly.express as px
import plotly.figure_factory as ff

# Set page configuration before any other Streamlit functions
st.set_page_config(layout="wide", page_title="Olympics Analysis", page_icon="🏅")

page_bg_img = '''
<style>
[data-testid="stAppViewContainer"]{
    background-image: url("https://img.freepik.com/free-vector/abstract-gradient-blue-orange-panorama-horizontal-vector-sunset-nature-background_105738-1801.jpg");
    background-size: cover;
}

[data-testid="stSidebar"] {
    background-image: url("https://cdn.prod.website-files.com/5a9ee6416e90d20001b20038/64f5c4b7cb1f1c2f3220ad73_Rectangle%20(24).svg");
    background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

df = preprocessor.preprocess(df,region_df)

st.sidebar.title("Olympics Analysis")
st.sidebar.image('https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/1280px-Olympic_rings_without_rims.svg.png', width=180)
user_menu = st.sidebar.radio(
    'Select an option',
    ('Medal Tally', 'Overall Analysis', 'Country-Wise Analysis', 'Athlete-Wise Analysis')
)

if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df) 
    
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)
    
    medal_tally = helper.fetch_medal_tally(df,selected_year,selected_country)
    if selected_country == "Overall" and selected_year == "Overall":
        st.title("Overall Tally")
    elif selected_country != "Overall" and selected_year != "Overall":
        st.title(f"{selected_country}'s performance in {selected_year} olympics")
    elif selected_country != "Overall":
        st.title(f"{selected_country}'s overall performance")
    else:
        st.title(f"Medal tally in {selected_year} olympics")
    st.table(medal_tally)
    
if user_menu == 'Overall Analysis':
    editions = df['Year'].unique().shape[0] - 1  #1906 is not considered
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]
    
    st.title("Overall Stats")
    
    col1,col2,col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Cities")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)
        
    nations_over_time = helper.data_over_time(df,'region')
    st.title("Participating Nations over the years")
    fig = px.line(nations_over_time, x='Year', y='region')
    st.plotly_chart(fig)
    
    events_over_time = helper.data_over_time(df,'Event')
    st.title("Events over the years")
    fig = px.line(events_over_time, x='Year', y='Event')
    st.plotly_chart(fig)
    
    athletes_over_time = helper.data_over_time(df,'Name')
    st.title("Athletes over the years")
    fig = px.line(athletes_over_time, x='Year', y='Name')
    st.plotly_chart(fig)
    
    st.title("No of events over time [Every Sport]")
    fig,ax = plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(['Year','Sport','Event'])
    ax = sns.heatmap(x.pivot_table(index = 'Sport', columns = 'Year', values = 'Event', aggfunc='count').fillna(0).astype('int'),annot=True,cmap="Blues",vmin=0, vmax=0.5)
    st.pyplot(fig)
    
    st.title("Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')
    
    selected_sport = st.selectbox('Select a sport', sport_list)
    x = helper.most_successful(df,selected_sport)
    st.table(x)
    
if user_menu == 'Country-Wise Analysis':
    
    st.sidebar.title("Country-Wise Analysis")
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    default_country_index = country_list.index('India') if 'India' in country_list else 0
    selected_country = st.sidebar.selectbox('Select a country', country_list, index=default_country_index)

    # Analysis and visualizations
    country_df = helper.yrwise_medal_tally(df, selected_country)
    st.title(f"{selected_country} Medal tally over the years")
    fig = px.line(country_df, x='Year', y='Medal')
    st.plotly_chart(fig)

    # Heatmap for country sports performance
    pt = helper.country_event_hmap(df, selected_country)
    st.title(f"{selected_country} shines in the following sports")
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(pt, annot=True)
    st.pyplot(fig)
    
    st.title(f"Top 10 Athletes of {selected_country}")
    top_ten_df = helper.most_successful_country_based(df, selected_country)
    st.table(top_ten_df)
    
if user_menu == 'Athlete-Wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],show_hist=False, show_rug=False)
    fig.update_layout(autosize=False,width=1000,height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                     'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports(Gold Medalist)")
    st.plotly_chart(fig, use_container_width=True)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    st.title('Height Vs Weight')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df,selected_sport)
    fig,ax = plt.subplots()
    ax = sns.scatterplot(data=temp_df, x='Weight', y='Height', hue='Medal', style='Sex', s=60, ax=ax)
    st.pyplot(fig)

    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

