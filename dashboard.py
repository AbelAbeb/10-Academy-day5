import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from wordcloud import WordCloud
import plotly.express as px
from add_data import db_execute_fetch

st.set_page_config('Dashboard', layout="wide")
st.title("Topic Modeling and Sentimet Anlysis")
st.markdown("***")


class dashboard:
    def __init__(self):
        pass

    # loads the data fromm the db based on query
    def loadData(self, ):
        query = "select * from Tweet"
        df = db_execute_fetch(query, dbName="Tweetdb", rdf=True)
        #st.write(df)
        return df 

    def text_category(self, p):
        """
        A function  that takes a value p and returns, depending on the value of p, 
        a string 'positive', 'negative' or 'neutral'
        """
        if p > 0 : return 'positive'
        elif p == 0: return 'neutral'
        return 'negative'

    # display the db based on the polarity
    def display_df_polarity(self, p):
        df = self.loadData()
        df['score'] = df['polarity'].apply(self.text_category)
        if p == 'positive':
            st.write(df[df['score'] == 'positive'])
        elif p == 'negative':
            st.write(df[df['score'] == 'negative'])
        elif p == 'neutral':
            st.write(df[df['score'] == 'neutral'])
        else:
            st.write(df)
    

    # Count the number of positive, neutral, and negative
    def polarity_count(self):
        df = self.loadData()
        df['score'] = df['polarity'].apply(self.text_category) 
        sc = list(df['score'])
        return { 'positive': sc.count('positive'), 'neutral': sc.count('neutral'),
                                'negative': sc.count('negative')  } 

    # draws bar chart of the polarity
    def barChart(self):
        st.title('Bar')
        count = self.polarity_count()
        data = pd.DataFrame({
        'Sentiment': list(count.keys()),
        'label': [count[key] for key in count.keys()],
                    })
        bar_fig = px.bar(data, x='Sentiment', y='label')
        st.plotly_chart(bar_fig)

    # draws pie chart of the polarity
    def pieChart(self):
        st.title('Pie')
        count = self.polarity_count()
        pie_fig = px.pie(values=[count[key] for key in count.keys()], names=list(count.keys()))
        st.plotly_chart(pie_fig)
        
    # location of twittes
    def selectLocAndAuth(self):
        df = self.loadData()
        location = st.multiselect("choose Location of tweets", list(df['place_coordinate'].unique()))
        lang = st.multiselect("choose Language of tweets", list(df['language'].unique()))

        if location and not lang:
            df = df[np.isin(df, location).any(axis=1)]
            st.write(df)
        elif lang and not location:
            df = df[np.isin(df, lang).any(axis=1)]
            st.write(df)
        elif lang and location:
            location.extend(lang)
            df = df[np.isin(df, location).any(axis=1)]
            st.write(df)
        else:
            st.write(df)
        
    # topic modeling
    def wordCloud(self):
        df = self.loadData()
        # Convert to lowercase
        df['clean_text'] = df['clean_text'].map(lambda x: x.lower())
        # Join the different processed titles together.
        long_string = ','.join(list(df['clean_text'].values))

        # Create a WordCloud object
        wordcloud = WordCloud(background_color="white", width=650, height=450, \
                                min_font_size=5, contour_color='steelblue')
        # Generate a word cloud
        wordcloud.generate(long_string)
        st.title("Tweet Text Word Cloud")
        st.image(wordcloud.to_array())

st1 = dashboard()
st1.selectLocAndAuth()
polarity = st.sidebar.selectbox('choose polarity of tweets', ('All', 'positive', 'negative', 'neutral'))
st1.display_df_polarity(polarity)

st.success("")
st.title("Visualizations")
random_tweet = st.sidebar.selectbox('Visualizations', 
                ('Topic Modeling','Bar Chart','Pie Chart'))
if random_tweet == 'Topic Modeling': st1.wordCloud()
elif random_tweet == 'Bar Chart': st1.barChart()
elif random_tweet == 'Pie Chart': st1.pieChart()
