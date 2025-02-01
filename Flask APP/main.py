from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory_db.sqlite3'  # Change to your preferred database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class AuthUser(db.Model):
    __tablename__ = 'auth_users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))    
    ProductID = db.Column(db.BigInteger, unique=True, nullable=False)    
    ProductCode = db.Column(db.String(255), unique=True, nullable=False)
    ProductName = db.Column(db.String(255), nullable=False)    
    ProductImage = db.Column(db.String(255), nullable=True)    
    CreatedDate = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=db.func.current_timestamp())
    CreatedUser = db.Column(db.String(36), db.ForeignKey('auth_users.id'), nullable=False)    
    IsFavourite = db.Column(db.Boolean, default=False)
    Active = db.Column(db.Boolean, default=True)    
    HSNCode = db.Column(db.String(255), nullable=True)    
    TotalStock = db.Column(db.Numeric(20,8), nullable=True, default=0.00)
    
    __table_args__ = (db.UniqueConstraint('ProductCode', 'ProductID', name='unique_product_constraint'),)

class ProductVariant(db.Model):
    __tablename__ = 'product_varients'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    Product = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    VariantName = db.Column(db.String(255), nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=db.func.current_timestamp())

class ProductVariantOption(db.Model):
    __tablename__ = 'product_varient_options'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    Variant = db.Column(db.String(36), db.ForeignKey('product_varients.id'), nullable=False)
    OptionName = db.Column(db.String(255), nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=db.func.current_timestamp())

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    Product = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    ImageURL = db.Column(db.String(255), nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=db.func.current_timestamp())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Database and tables created successfully!")

# ------------------------------------------------------------------------------------------------------------------------

@app.route('/auth-user-login', methods=['POST'])
def auth_user_login():
    data = request.get_json()  # Get the username and password from the React app
    username = data.get('username')
    password = data.get('password')

    # Query the database for the user by username
    user = AuthUser.query.filter_by(username=username).first()

    # Check if the user exists and the password matches
    if user and user.password == password:
        return jsonify({"message": "Login successful", "redirect": "/model/tables"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401
    

# ------------------------------------------------------------------------------------------------------------------------

''' AUTH USER DETAILS '''

@app.route('/Model/auth_user')
def auth_user_details():
    with db.engine.connect() as connection:
        result = connection.execute("SELECT * FROM auth_users;")
        users = [dict(row) for row in result]
    
    members = jsonify({"auth_user": users})
    return members


''' DATABSE STRUCTURE REPRESANTATION '''

@app.route('/Model/database')
def index():
    with db.engine.connect() as connection:
        result = connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in result]
    
    return jsonify({"tables": tables})  


@app.route('/Model/database/tables')
def list_tables_and_columns():
    with db.engine.connect() as connection:
        # Get all table names
        result = connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in result]

        # Get columns for each table
        table_details = {}
        for table in tables:
            columns_result = connection.execute(f"PRAGMA table_info({table});")
            columns = [
                {
                    "name": col[1],  # Column name
                    "type": col[2],  # Data type
                    "not_null": bool(col[3]),  # Is NOT NULL
                    "default_value": col[4],  # Default value (if any)
                    "primary_key": bool(col[5])  # Is Primary Key
                }
                for col in columns_result
            ]
            table_details[table] = columns

    return jsonify(table_details) 