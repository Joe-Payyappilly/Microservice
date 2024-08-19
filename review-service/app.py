from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from pymongo import MongoClient
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb+srv://joepayyappilly2002:pHNghGp3wwZEviKu@cluster0.plorf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['review_db']
reviews = db['reviews']

MOVIE_SERVICE_URL = 'http://movie-service:5000'  # Updated to use Docker service name

@app.route('/')
def index():
    movie_title = request.args.get('movie_title')
    review_list = list(reviews.find({'title': movie_title}, {'_id': 0})) if movie_title else list(reviews.find({}, {'_id': 0}))
    return render_template('index.html', reviews=review_list, movie_title=movie_title)

@app.route('/add_review', methods=['POST'])
def add_review():
    title = request.form.get('title')
    review = request.form.get('review')
    
    if title and review:
        data = {'title': title, 'review': review}
        response = requests.get(f'{MOVIE_SERVICE_URL}/movie/{title}/reviews')

        if response.status_code == 200:
            reviews.insert_one(data)
            flash('Review added successfully!')
        else:
            flash('Movie not found, review not added.')
    return redirect(url_for('index'))

@app.route('/update_review/<title>', methods=['POST'])
def update_review(title):
    new_review = request.form.get('review')
    
    if new_review:
        result = reviews.update_one({'title': title}, {'$set': {'review': new_review}})
        if result.matched_count:
            flash('Review updated successfully!')
        else:
            flash('Review not found.')
    return redirect(url_for('index'))

@app.route('/delete_review/<title>', methods=['POST'])
def delete_review(title):
    result = reviews.delete_one({'title': title})
    if result.deleted_count:
        flash('Review deleted successfully!')
    else:
        flash('Review not found.')
    return redirect(url_for('index'))

@app.route('/reviews/<title>')
def get_reviews(title):
    reviews_list = list(reviews.find({'title': title}, {'_id': 0}))
    return jsonify({'reviews': reviews_list})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Use 0.0.0.0 to bind to all network interfaces
