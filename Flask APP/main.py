from flask import Flask, jsonify, request, render_template, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError


UPLOAD_FOLDER = 'static/uploads'  # Define where images will be stored
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}  # Allowed image types



app = Flask(__name__)
app.config['SECRET_KEY'] = "is my secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DATABASE and TABLES
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
    quantity = db.Column(db.String(36), db.ForeignKey('product_varients.id'), nullable=False)
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
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

# login page

@app.route('/login', methods=['POST', 'GET'])
def login():
    user_login_error = None  # Store error message

    if request.method == 'POST':
        username = request.form.get('user_name')
        userpassword = request.form.get('user_password')

        # Query user from the database
        user = AuthUser.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, userpassword):
            session['loggedin'] = True
            session['id'] = user.id
            session['username'] = user.username
            session['email'] = user.email

            return redirect('/')  
        else:
            user_login_error = 'Invalid username or password'

    return render_template('login.html', user_login_error=user_login_error)

# ------------------------------------------------------------------------------------------------------------------------
from flask import redirect, url_for, session

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    # Clear all session data
    session.clear()

    # Redirect to the login page
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------------------------------

# home
@app.route('/')
def home():
    if 'loggedin' in session:
        # Fetch all products
        products = Product.query.all()

        product_data = []
        for product in products:
            # Fetch variants related to the product
            variants = ProductVariant.query.filter_by(Product=product.id).all()
            variant_data = []

            for variant in variants:
                # Fetch variant options related to the variant
                options = ProductVariantOption.query.filter_by(Variant=variant.id).all()
                option_data = []

                for option in options:
                    # Get option name and stock quantity
                    option_data.append({
                        "option_name": option.OptionName,
                        "quantity": option.quantity  # Fetch the quantity field
                    })

                variant_data.append({
                    "variant_name": variant.VariantName,
                    "options": option_data
                })

            # Fetch product images
            product_images = ProductImage.query.filter_by(Product=product.id).all()
            image_urls = [img.ImageURL for img in product_images]

            # Fetch created user and created date from the product (if applicable)
            created_user = product.CreatedUser  # Assuming 'CreatedUser' stores the user ID of the product creator
            created_date = product.CreatedDate.strftime('%Y-%m-%d %H:%M:%S') if product.CreatedDate else None

            product_data.append({
                "id":product.id,
                "product_id": product.ProductID,
                "product_code": product.ProductCode,
                "product_name": product.ProductName,
                "product_image": image_urls,
                "variants": variant_data,
                "created_user": created_user,  # Add this field to display the creator's user ID
                "created_date": created_date  # Add this field to display the creation date
            })

        return render_template('home.html', products=product_data)
    else:
        return render_template('login.html')


# ---------------------------------------------------------------------------------------------------

# adding stock

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if the uploaded file is an allowed image format"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add-stock', methods=['POST', 'GET'])
def add_stock():
    if 'loggedin' in session:  # Ensure user is logged in
        if request.method == 'POST':
            product_id = request.form.get('product_id')
            product_code = request.form.get('product_code')
            product_name = request.form.get('product_name')
            product_image = request.files.get('product_image')

            variant_names = request.form.getlist('variant_name[]')

            # Collect variant options and stock quantities dynamically
            variant_options = []
            variant_stocks = []
            for i in range(len(variant_names)):
                options = request.form.getlist(f'variant_option_{i}[]')
                stocks = request.form.getlist(f'variant_stock_{i}[]')  # Collect stock quantities
                variant_options.append(options)
                variant_stocks.append(stocks)

            # Save the image if it exists
            image_filename = None
            if product_image and allowed_file(product_image.filename):
                filename = secure_filename(product_image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                product_image.save(image_path)
                image_filename = filename  # Store only the filename in DB

            if product_code:
                try:
                    # **CHECK IF PRODUCT CODE ALREADY EXISTS**
                    existing_product = Product.query.filter_by(ProductCode=product_code).first()
                    if existing_product:
                        database_error = f"❌ Product with code '{product_code}' already exists."
                        return render_template('add_stock.html', database_error=database_error)

                    # Step 1: Insert Product
                    new_product = Product(
                        id=str(uuid.uuid4()),
                        ProductID=product_id,
                        ProductCode=product_code,
                        ProductName=product_name,
                        ProductImage=image_filename,
                        CreatedUser=session.get('username'),
                        CreatedDate=datetime.now()
                    )
                    db.session.add(new_product)
                    db.session.commit()  # Commit to get product ID

                    # Step 2: Insert Variants
                    for index, variant_name in enumerate(variant_names):
                        variant = ProductVariant(
                            id=str(uuid.uuid4()),
                            Product=new_product.id,  # Foreign Key
                            VariantName=variant_name
                        )
                        db.session.add(variant)
                        db.session.commit()  # Commit to get variant ID

                        # Step 3: Insert Variant Options and their Stock Quantities
                        for option, stock in zip(variant_options[index], variant_stocks[index]):
                            variant_option = ProductVariantOption(
                                id=str(uuid.uuid4()),
                                Variant=variant.id,  # Foreign Key
                                OptionName=option,
                                quantity=int(stock) if stock.isdigit() else 0  # Convert stock to int
                            )
                            db.session.add(variant_option)
                            db.session.commit()  # Commit to get variant option ID

                    # Step 4: Insert Product Image (if available)
                    if image_filename:
                        product_image_entry = ProductImage(
                            id=str(uuid.uuid4()),
                            Product=new_product.id,
                            ImageURL=image_filename
                        )
                        db.session.add(product_image_entry)
                        db.session.commit()

                    message = "✅ Successfully Added Product!"
                    return render_template('add_stock.html', message=message)

                except IntegrityError:
                    db.session.rollback()  # **Rollback to avoid partial insertions**
                    database_error = f"❌ Product with code '{product_code}' already exists. Try a different code."
                    return render_template('add_stock.html', database_error=database_error)

                except Exception as e:
                    db.session.rollback()  # Ensure rollback in case of any other failure
                    database_error = f"❌ Adding Failed: {str(e)}"
                    return render_template('add_stock.html', database_error=database_error)

        return render_template('add_stock.html')  # Render form on GET request
    else:
        return render_template('login.html')  # Redirect to login if not logged in



# ---------------------------------------------------------------------------------------------------


# stock details

@app.route('/product-details/<product_id>')
def product_details(product_id):
    if 'loggedin' in session:
        try:
            # Fetch the product based on UUID (id)
            product = Product.query.filter_by(id=product_id).first()  # Query to get the Product object by its UUID (id)

            if not product:
                return f"Product with ID {product_id} not found", 404  # Return a 404 error if the product is not found

            # Fetch all details of the product, including its columns
            product_details = {
                "Product ID": product.id,
                "Product Code": product.ProductCode,
                "Product Name": product.ProductName,
                "Product Image": product.ProductImage,
                "Created Date": product.CreatedDate,
                "Updated Date": product.UpdatedDate,
                "Created User": product.CreatedUser,
                "Is Favourite": product.IsFavourite,
                "Active": product.Active,
                "HSN Code": product.HSNCode,
                "Total Stock": product.TotalStock
            }

            # Initialize a variable to track the total quantity
            total_quantity = 0

            # Fetch variants related to the product
            variants = ProductVariant.query.filter_by(Product=product.id).all()
            variant_data = []
            for variant in variants:
                # For each variant, fetch the options and their stock quantities
                options = ProductVariantOption.query.filter_by(Variant=variant.id).all()
                option_data = []
                for option in options:
                    # Ensure quantity is an integer before adding
                    option_quantity = int(option.quantity) if option.quantity else 0  # Convert quantity to int if it's not empty
                    option_data.append({
                        "option_name": option.OptionName,
                        "quantity": option_quantity  # Option quantity
                    })
                    total_quantity += option_quantity  # Accumulate the total quantity

                # Append variant with options and their quantities
                variant_data.append({
                    "variant_name": variant.VariantName,
                    "options": option_data,
                    "Variant ID": variant.id
                })

            # Fetch product images (if any)
            product_images = ProductImage.query.filter_by(Product=product.id).all()
            image_urls = [img.ImageURL for img in product_images]

            # Add total quantity to the product details
            product_details["Total Quantity"] = total_quantity

            # Render the template and pass all the fetched data
            return render_template('product_details.html', 
                                   product=product_details, 
                                   variants=variant_data, 
                                   images=image_urls)

        except Exception as e:
            print(f"Error: {e}")
            return f"Error retrieving product details: {e}", 500  # Return error if something goes wrong
    
    else:
        return redirect('/login')  # Redirect to login page if not logged in
    

# ---------------------------------------------------------------------------------------------------

# sell product
@app.route('/sell-product/<string:product_id>', methods=['GET', 'POST'])
def sell_product(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return "Product not found", 404
    
    variants = ProductVariant.query.filter_by(Product=product_id).all()
    
    if request.method == 'POST':
        variant_id = request.form.get('variant_id')
        option_id = request.form.get('option_id')
        quantity_sold = float(request.form.get('quantity'))
        
        # Update the quantity for the selected option
        option = ProductVariantOption.query.get(option_id)
        
        if option and quantity_sold <= float(option.quantity):
            option.quantity = float(option.quantity) - quantity_sold
            db.session.commit()
            flash("Successfully Sold", "success")
            return redirect(url_for('sell_product', product_id=product_id))
        else:
            flash("Not enough stock", "danger")
            return redirect(url_for('sell_product', product_id=product_id))
    
    return render_template('sell_product.html', product=product, variants=variants)

@app.route('/get-options/<string:variant_id>')
def get_variant_options(variant_id):
    options = ProductVariantOption.query.filter_by(Variant=variant_id).all()
    options_data = [
        {
            'id': option.id,
            'OptionName': option.OptionName,
            'quantity': option.quantity
        } for option in options
    ]
    return jsonify(options_data)

# buy product



@app.route('/buy-product/<string:product_id>', methods=['GET', 'POST'])
def buy_product(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return "Product not found", 404
    
    variants = ProductVariant.query.filter_by(Product=product_id).all()
    
    if request.method == 'POST':
        variant_id = request.form.get('variant_id')
        option_id = request.form.get('option_id')
        quantity_bought = float(request.form.get('quantity'))
        
        # Get the selected option
        option = ProductVariantOption.query.get(option_id)
        
        if option:
            option.quantity = float(option.quantity) + quantity_bought  # Increase the quantity
            db.session.commit()
            flash("Successfully Bought", "success")
            return redirect(url_for('buy_product', product_id=product_id))
        else:
            flash("Option not found", "danger")
            return redirect(url_for('buy_product', product_id=product_id))
    
    return render_template('buy_product.html', product=product, variants=variants)




# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------


# view stock 
@app.route('/view-stock')
def view_stock():
    if 'loggedin' in session:
        # Fetch all products
        products = Product.query.all()

        product_data = []
        for product in products:
            # Fetch variants related to the product
            variants = ProductVariant.query.filter_by(Product=product.id).all()
            variant_data = []

            for variant in variants:
                # Fetch variant options related to the variant
                options = ProductVariantOption.query.filter_by(Variant=variant.id).all()
                option_data = []

                for option in options:
                    # Get option name and stock quantity
                    option_data.append({
                        "option_name": option.OptionName,
                        "quantity": option.quantity  # Fetch the quantity field
                    })

                variant_data.append({
                    "variant_name": variant.VariantName,
                    "options": option_data
                })

            # Fetch product images
            product_images = ProductImage.query.filter_by(Product=product.id).all()
            image_urls = [img.ImageURL for img in product_images]

            # Fetch created user and created date from the product (if applicable)
            created_user = product.CreatedUser  # Assuming 'CreatedUser' stores the user ID of the product creator
            created_date = product.CreatedDate.strftime('%Y-%m-%d %H:%M:%S') if product.CreatedDate else None

            product_data.append({
                "id":product.id,
                "product_id": product.ProductID,
                "product_code": product.ProductCode,
                "product_name": product.ProductName,
                "product_image": image_urls,
                "variants": variant_data,
                "created_user": created_user,  # Add this field to display the creator's user ID
                "created_date": created_date  # Add this field to display the creation date
            })

        return render_template('view_stock.html', products=product_data)
    else:
        return render_template('login.html')


    

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