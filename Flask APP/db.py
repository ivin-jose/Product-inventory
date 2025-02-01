from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid


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
