from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

SECRET_API_KEY = 'SECRET_API_KEY'


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(10), nullable=False)
    autopilot = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# This was only needed to create the database
# db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


# This route returns all cars from the database.
@app.route('/all')
def get_all_cars():
    all_cars = Car.query.all()
    return jsonify(cars=[car.to_dict() for car in all_cars]), 200


# This route searches through the database and returns all cars that match the queried make of car
@app.route('/search_make')
def search_make():
    make = request.args.get('car_make')
    cars = Car.query.filter_by(make=make)
    if cars.count() > 0:
        return jsonify([car.to_dict() for car in cars]), 200
    else:
        return jsonify(error={'not found': f'There are no cars model {make}.'}), 400


# This route searches through the database and returns all cars that match the queried color of car
@app.route('/search_color')
def search_color():
    color = request.args.get('car_color')
    cars = Car.query.filter_by(color=color)
    if cars.count() > 0:
        return jsonify(cars=[car.to_dict() for car in cars]), 200
    else:
        return jsonify(error={'not found': f'There are no cars of color {color}.'}), 400


# Add new car entry to the database
@app.route('/add_car', methods=['POST'])
def add_car():
    if request.method == 'POST':
        if request.args.get('api_key') == SECRET_API_KEY:
            new_car = Car(
                make=request.form.get('make'),
                model=request.form.get('model'),
                year=request.form.get('year'),
                color=request.form.get('color'),
                autopilot=bool(request.form.get('autopilot')),
                price=request.form.get('price')
            )
            db.session.add(new_car)
            db.session.commit()
            return jsonify(success={'successful': 'New car successfully added to the database.'}), 200
        else:
            return jsonify(error={'invalid': 'Invalid api_key.'}), 400


# Update the price of a car in the database by car 'id'
@app.route('/update_price/<car_id>', methods=['PATCH'])
def update_price(car_id):
    new_price = request.args.get('new_price')
    car = Car.query.get(car_id)
    if car:
        car.price = new_price
        db.session.commit()
        return jsonify(success={'success': f'Car price successfully update. New car price is ${car.price}'}), 200
    else:
        return jsonify(error={'invalid': f'No car with id "{car_id}" was found in the database.'}), 400


# Remove car entry from database.
@app.route('/delete_car/<car_id>', methods=['DELETE'])
def delete_car(car_id):
    car = Car.query.get(car_id)
    if car:
        if request.args.get('api_key') == SECRET_API_KEY:
            db.session.delete(car)
            db.session.commit()
            return jsonify(success={'successful': 'Car successfully removed from the database.'}), 200
        else:
            return jsonify(error={'invalid': 'Invalid api_key.'}), 400
    else:
        return jsonify(error={'invalid': f'No car with id {car_id} was found in the database.'}), 400


if __name__ == '__main__':
    app.run(debug=True)

