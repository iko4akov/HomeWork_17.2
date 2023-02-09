
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app. config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}

db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


api = Api(app)
movie_ns = api.namespace('movies')
with app.app_context():
    db.create_all()
    db.session.begin()
    db.session.commit()

@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        if request.args.get("director_id"):
            dir_id = request.args.get("director_id")
            movie_query = db.session.query(Movie).filter(Movie.director_id == dir_id).all()
            return movies_schema.dumps(movie_query, ensure_ascii=False), 200

        elif request.args.get("genre_id"):
            if request.args.get("genre_id"):
                gen_id = request.args.get("genre_id")
                movie_query = db.session.query(Movie).filter(Movie.genre_id == gen_id).all()
                return movies_schema.dumps(movie_query, ensure_ascii=False), 200

        else:
            all_movies = db.session.query(Movie).all()
            return movies_schema.dumps(all_movies, ensure_ascii=False), 200


@movie_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid: int):
        try:
            movie_query = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dumps(movie_query, ensure_ascii=False), 200
        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
