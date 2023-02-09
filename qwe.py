from flask import request, Flask
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    year = db.Column(db.Integer)
    author = db.Column(db.String(200))

class BookSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    year = fields.Int()
    author = fields.Str()

book_schema = BookSchema()
books_schema = BookSchema(many=True)

api = Api(app)
book_ns = api.namespace('')

b1 = Book(id=1, name='Book1', year=2001, author='Author1')
b2 = Book(id=2, name='Book2', year=2002, author='Author2')

with app.app_context():
    db.create_all()
    db.session.add_all([b1, b2])

@book_ns.route("/books")
class BooksView(Resource):
    def get(self):
        all_books = db.session.query(Book).all()
        return book_schema.dumps(all_books), 200

    def post(self):
        req_json = request.json
        new_book = Book(**req_json)

        with db.session.begin():
            db.session.add(new_book)

        return "", 201

@book_ns.route("/books/<int:bid>")
class BookView(Resource):
    def get(self, bid: int):
        try:
            book_query = db.session.query(Book).filter(Book.id == bid).one()
            return book_query, 200
        except Exception as e:
            return str(e), 404

    def put(self, bid: int):
        book = db.session.query(Book).filter(id=bid).one()
        req_json = request.json

        book.name = req_json.get('name')
        book.year = req_json.get('year')
        book.author = req_json.get('author')
        with db.session.add(book):
            db.session.commit()

        return "", 204
    #
    def putch(self, bid: int):
        book = db.session.query(Book).filter(id=bid).one()
        req_json = request.json

        if "name" in req_json:
            book.name = req_json.get('name')
        if "author" in req_json:
            book.author = req_json.get('author')
        if "year" in req_json:
            book.year = req_json.get('year')
        with app.app_context():
            db.session.add(book)
            db.session.commit()


    def delete(self, bid):
        db.session.query(Book).delete()
        return "", 204

if __name__ == '__main__':
    app.run(host='127.0.0.3', port=5000, debug=True)
