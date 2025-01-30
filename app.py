from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import pickle
import re

# Initialize Flask app
app = Flask(__name__)

# Load preprocessed movie dataset
final_data = pd.read_csv('movie_data.csv')

# Load precomputed cosine similarity matrix for recommendations
cosine_sim = np.load('cosine_sim_matrix.npy')

# Load trained TF-IDF vectorizer used for feature extraction
with open('tfidf_vectorizer.pkl', 'rb') as f:
    tfid = pickle.load(f)

class FlixHub:
    def __init__(self, df, cosine_sim):
        """
        Initializes the recommendation system.

        :param df: Pandas DataFrame containing movie and TV show data
        :param cosine_sim: Precomputed cosine similarity matrix for recommendations
        """        
        self.df = df
        self.cosine_sim = cosine_sim
    
    def recommendation(self, title, total_result=5, threshold=0.5):
        """
        Provides movie and TV show recommendations based on a given title.

        :param title: The title of the movie or TV show to find similar content
        :param total_result: Number of recommendations to return (default: 5)
        :return: Lists of similar movies and TV shows
        """        
        idx = self.find_id(title)
        if idx == -1:
            return [], []
        
        self.df['similarity'] = self.cosine_sim[idx]
        sort_df = self.df.sort_values(by='similarity', ascending=False)[1:total_result+1]
        
        movies = sort_df['title'][sort_df['type'] == 'Movie']
        tv_shows = sort_df['title'][sort_df['type'] == 'TV Show']
        
        similar_movies = [f'{i+1}. {movie}' for i, movie in enumerate(movies)]
        similar_tv_shows = [f'{i+1}. {tv_show}' for i, tv_show in enumerate(tv_shows)]
        
        return similar_movies, similar_tv_shows

    def find_id(self, name):
        """
        Finds the index of a title in the dataset.

        :param name: Movie or TV show title to search for
        :return: Index of the title in the dataset, or -1 if not found
        """        
        for index, string in enumerate(self.df['title']):
            if re.search(name, string, re.IGNORECASE):
                return index
        return -1

flix_hub = FlixHub(final_data, cosine_sim)

# Define the home route to serve the web interface
@app.route('/')
def home():
    return render_template('index.html')

# Define API endpoint for getting recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Handles requests to fetch movie/TV show recommendations.

    :return: JSON response with recommended movies and TV shows
    """
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    title = data.get('title', '')
    movies, tv_shows = flix_hub.recommendation(title, total_result=10)


    return jsonify({'movies': movies, 'tv_shows': tv_shows})


# Run the Flask app in debug mode
if __name__ == '__main__':
    app.run(debug=True)