from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


# database created
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# https://developer.themoviedb.org/reference/intro/getting-started
API_ACCESS_TOKEN = "GET_YOUR_ACCESS_TOKEN_USING_UPPER_URL"


# table created


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250),  nullable=True)
    year = db.Column(db.Integer,  nullable=True)
    description = db.Column(db.String(250),  nullable=True)
    rating = db.Column(db.Integer,  nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250),  nullable=True)
    img_url = db.Column(db.String(250), nullable=True)


# give entry to the table
with app.app_context():
    db.create_all()
    


# wt form creation
class ChangeRevRate(FlaskForm):
    rating = FloatField('Your Rating out of 10 e.g 7.5',
                        validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddMovie(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    add_movie = SubmitField('Add Movie')


# routes


@app.route("/")
def home():
    # all movies from Movie table
    # all_movies = Movie.query.all()

    # rank movie
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    id_no = request.args.get("id_no")
    movie = Movie.query.get(id_no)
    form = ChangeRevRate()
    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=movie)


# delete
@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id_no")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    movie_form = AddMovie()
    if movie_form.validate_on_submit():
        movie_name = movie_form.title.data
        url = f"https://api.themoviedb.org/3/search/movie?query={movie_name}&include_adult=false&language=en-US&page=1"

        api_access_token = API_ACCESS_TOKEN
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_access_token}"
        }
        response = requests.get(url, headers=headers)
        all_movies = response.json()['results']
        return render_template('select.html', movie_lst=all_movies)

    return render_template('add.html', movie_form=movie_form)


@app.route('/find')
def find_movie():
    movie_id = request.args.get('api_movie_id')
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization":  f"Bearer {api_access_token}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    new_movie = Movie(
        title=data['title'],
        img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
        year=data['release_date'].split("-")[0],
        description=data['overview']

    )
    db.session.add(new_movie)
    db.session.commit()
    id_no = new_movie.id
    return redirect(url_for('edit', id_no=id_no))


if __name__ == '__main__':
    app.run(debug=True)
