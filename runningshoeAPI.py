from flask import jsonify, request, Flask

from app import app, mysql

# Sample data
books = [
    {"id": 1, "title": "Concept of Physics", "author": "H.C Verma"},
    {"id": 2, "title": "Gunahon ka Devta", "author": "Dharamvir Bharti"},
    {"id": 3, "title": "Problems in General Physsics", "author": "I.E Irodov"},
    {"id": 4, "title": "Problems in General Physsics", "author": "I.E Irodov"}
]

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)
# end sample

# Shoes CRUD Endpoints
@app.route('/shoes', methods=['GET'])
def get_shoes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shoes")
    data = cur.fetchall()
    cur.close()
    #still need to format data into a list of dictionaries
    
    return jsonify({'shoes': data})

@app.route('/shoes/<int:shoe_id>', methods=['GET'])
def get_shoe(shoe_id):
    if(shoe_id < 1):
        return jsonify({'error': 'Invalid shoe ID'}), 400
    
    cur = mysql.connection.cursor()
    cur.execute("select * from shoes where id = ?", (shoe_id,))
    data = cur.fetchone()
    cur.close()

    return jsonify({'shoe': data})

@app.route('/shoes', methods=['POST'])
def add_shoe():

    


# Brands CRUD Endpoints ==========
@app.route('/brands', methods=['GET'])
def get_brands():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM brands")
    data = cur.fechall()
    cur.close()

    return jsonify({'brands': data})

@app.route('/brands/<int:brand_id>', methods=['GET'])
def get_brand(brand_id):
    if(brand_id < 1):
        return jsonify({'error': 'Invalid brand ID'}), 400
    
    cur = mysql.connection.cursor()
    cur.execute("select * from brands where id = ?", (brand_id,))
    data = cur.fetchone()
    cur.close()

    return jsonify({'brand': data})

# ========== Users CRUDEndpoints ==========
@app.route('/users', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    cur.close()

    return jsonify({'users': data})

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if(user_id < 1):
        return jsonify({'error': 'Invalid user ID'}), 400
    
    cur = mysql.connection.cursor()
    cur.execute("select * from users where id = ?", (user_id,))
    data = cur.fetchone()
    cur.close()

    return jsonify({'user': data})

# ========== Reviews CRUD Endpoints ==========
@app.route('/reviews', methods=['GET'])
def get_reviews():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reviews")
    data = cur.fetchall()
    cur.close()
    
    return jsonify({'reviews': data})

@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    if(review_id < 1):
        return jsonify({'error': 'Invalid review ID'}), 400
    
    cur = mysql.connection.cursor()
    cur.execute("select * from reviews where id = ?", (review_id,))
    data = cur.fetchone()
    cur.close()

    return jsonify({'review': data})



    
    

