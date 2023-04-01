from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my-top-movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.app_context().push()


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)
    img_url = db.Column(db.String, nullable=True)


class RateMovieForm(FlaskForm):
    rating = StringField(label='Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Set')


class AddMovieForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')

# db.create_all()
#
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    movie = Movie.query.get(id)
    edit = RateMovieForm()
    if edit.validate_on_submit():
        movie.rating = edit.rating.data
        movie.review = edit.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, edit=edit, id=id)


@app.route("/delete/<id>", methods=["GET", "POST"])
def delete(id):
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

api_key = "7c8dc1b75de85879171531c0f4b7f918"
# address = "https://api.themoviedb.org/3/search/movie?api_key=<<api_key>>&language=en-US&query=Whiplash&page=1&include_adult=false"

@app.route("/add", methods=["GET", "POST"])
def add():
    new_add = AddMovieForm()
    if new_add.validate_on_submit():
        print(new_add.title.data)
        response = requests.get(
            url=f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=en-US&query={new_add.title.data}&page=1&include_adult=false")
        response_json = response.json()
        # new_movie = Movie(title=new_add.title.data)
        # db.session.add(new_movie)
        # db.session.commit()
        return render_template("select.html", response=response_json)
    return render_template("add.html", form=new_add)

@app.route("/new_movie/<id1>", methods=["GET", "POST"])
def new_add(id1):
    response1 = requests.get(
        url=f"https://api.themoviedb.org/3/movie/{id1}?api_key=7c8dc1b75de85879171531c0f4b7f918&language=en-US")
    response1_json = response1.json()

    new_movie = Movie(
        title=response1_json["original_title"],
        year=(response1_json["release_date"]).split('-')[0],
        description=response1_json["overview"],
        img_url=f"https://image.tmdb.org/t/p/w500/{response1_json['backdrop_path']}"
    )

    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for('edit', id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
