from flask import Flask, request, render_template, redirect, url_for, flash
from pymongo import MongoClient
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient("mongodb+srv://joepayyappilly2002:pHNghGp3wwZEviKu@cluster0.plorf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['movie_db']
movies = db['movies']

@app.route('/')
def movie_list():
    movie_list = list(movies.find({}, {'_id': 0}))

    for movie in movie_list:
        try:
            response = requests.get(f'http://review-service:5001/reviews/{movie["title"]}')  # Updated to use Docker service name
            if response.status_code == 200: 
                movie['reviews'] = response.json().get('reviews', [])
            else:
                movie['reviews'] = []
        except Exception as e:
            movie['reviews'] = []
            flash(f'Error fetching reviews: {str(e)}')

    return render_template('movies.html', movies=movie_list)

@app.route('/add_movie', methods=['POST'])
def add_movie():
    title = request.form.get('title')
    if title:
        movies.insert_one({'title': title})
        flash('Movie added successfully!')
    return redirect(url_for('movie_list'))

@app.route('/edit_movie/<title>', methods=['GET', 'POST'])
def edit_movie(title):
    if request.method == 'POST':
        new_title = request.form.get('title')
        movies.update_one({'title': title}, {'$set': {'title': new_title}})
        flash('Movie updated successfully!')
        return redirect(url_for('movie_list'))
    return render_template('edit_movie.html', title=title)

@app.route('/delete_movie/<title>', methods=['POST'])
def delete_movie(title):
    movies.delete_one({'title': title})
    flash('Movie deleted successfully!')
    return redirect(url_for('movie_list'))

@app.route('/add_review_ui/<title>')
def add_review_ui(title):
    return redirect(f'http://localhost:5001/?movie_title={title}')  # Updated to use Docker service name

@app.route('/movie/<title>/reviews')
def movie_reviews(title):
    try:
        response = requests.get(f'http://review-service:5001/reviews/{title}')  # Updated to use Docker service name
        if response.status_code == 200:
            reviews = response.json().get('reviews', [])
        else:
            reviews = []
    except requests.RequestException as e:
        reviews = []
        flash(f'Error fetching reviews: {str(e)}')

    return render_template('reviews.html', title=title, reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Use 0.0.0.0 to bind to all network interfaces
