import functools
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import jwt
from flask import Blueprint, Response, current_app, jsonify, make_response, request
from werkzeug.security import check_password_hash

bp = Blueprint('routes', __name__)


def get_mysql():
    return current_app.extensions['mysql']


def to_xml(data: Any, root: str = 'response') -> str:

    def render_node(key: str, value: Any) -> str:
        if isinstance(value, dict):
            children = ''.join(render_node(k, v) for k, v in value.items())
            return f'<{key}>{children}</{key}>'
        
        if isinstance(value, list):
            children = ''.join(render_node('item', item) for item in value)
            return f'<{key}>{children}</{key}>'
        
        return f'<{key}>{value}</{key}>'

    return f'<{root}>{render_node("data", data)}</{root}>'


def format_response(payload: Dict[str, Any], status: int = 200) -> Response:
    preferred = request.args.get('format', 'json').lower()
    if preferred == 'xml':
        xml_body = to_xml(payload)
        response = make_response(xml_body, status)
        response.headers['Content-Type'] = 'application/xml'
        return response
    return make_response(jsonify(payload), status)


def require_json(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return format_response({'error': 'Request body must be JSON'}, 415)
        return func(*args, **kwargs)

    return wrapper


def jwt_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return format_response({'error': 'Missing or invalid Authorization header'}, 401)
        token = header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return format_response({'error': 'Token expired'}, 401)
        except jwt.InvalidTokenError:
            return format_response({'error': 'Invalid token'}, 401)
        return func(*args, **kwargs)

    return wrapper


def validate_numeric(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def fetch_all(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    cur = get_mysql().connection.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    return rows


def fetch_one(query: str, params: Tuple = ()) -> Dict[str, Any]:
    cur = get_mysql().connection.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    cur.close()
    return row


def execute(query: str, params: Tuple = ()) -> int:
    cur = get_mysql().connection.cursor()
    cur.execute(query, params)
    get_mysql().connection.commit()
    last_id = getattr(cur, 'lastrowid', 0)
    cur.close()
    return last_id


@bp.route('/')
@bp.route('/index')
def index():
    return format_response({'message': 'Hello WWorld! Welcome to the Running Shoe API.'})


@bp.route('/auth/login', methods=['POST'])
@require_json
def login():
    payload = request.get_json()
    email = payload.get('email')
    password = payload.get('password')
    if not email or not password:
        return format_response({'error': 'Email and password are required'}, 400)

    user = fetch_one('SELECT * FROM users WHERE email = %s', (email,))
    if not user or not check_password_hash(user.get('password_hash'), password):
        return format_response({'error': 'Invalid credentials'}, 401)

    exp_minutes = current_app.config.get('JWT_EXPIRATION_DELTA', 60)
    expiry = datetime.utcnow() + timedelta(minutes=exp_minutes)
    token = jwt.encode({'sub': user['id'], 'email': user['email'], 'exp': expiry},
                       current_app.config['SECRET_KEY'], algorithm='HS256')
    return format_response({'token': token, 'expires_at': expiry.isoformat()})


# Shoes CRUD Endpoints
@bp.route('/shoes', methods=['GET'])
def get_shoes():
    brand = request.args.get('brand')
    color = request.args.get('color')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    size = request.args.get('size')

    filters: List[str] = []
    params: List[Any] = []
    if brand:
        filters.append('brand_id = %s')
        params.append(brand)
    if color:
        filters.append('color = %s')
        params.append(color)
    if size:
        filters.append('size = %s')
        params.append(size)
    if min_price and validate_numeric(min_price):
        filters.append('price >= %s')
        params.append(min_price)
    if max_price and validate_numeric(max_price):
        filters.append('price <= %s')
        params.append(max_price)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ''
    shoes = fetch_all(f'SELECT * FROM shoes {where_clause}', tuple(params))
    return format_response({'shoes': shoes})


@bp.route('/shoes/<int:shoe_id>', methods=['GET'])
def get_shoe(shoe_id):
    if shoe_id < 1:
        return format_response({'error': 'Invalid shoe ID'}, 400)
    shoe = fetch_one('SELECT * FROM shoes WHERE id = %s', (shoe_id,))
    if not shoe:
        return format_response({'error': 'Shoe not found'}, 404)
    return format_response({'shoe': shoe})


def validate_shoe_payload(data: Dict[str, Any], partial: bool = False) -> Tuple[bool, List[str]]:
    required = ['name', 'brand_id', 'size', 'color', 'price']
    errors: List[str] = []
    if not partial:
        missing = [field for field in required if field not in data]
        if missing:
            errors.append(f"Missing fields: {', '.join(missing)}")
    if 'price' in data and not validate_numeric(data['price']):
        errors.append('Price must be numeric')
    return len(errors) == 0, errors


@bp.route('/shoes', methods=['POST'])
@jwt_required
@require_json
def add_shoe():
    data = request.get_json()
    valid, errors = validate_shoe_payload(data)
    if not valid:
        return format_response({'error': errors}, 400)

    shoe_id = execute(
        'INSERT INTO shoes (name, brand_id, size, color, price) VALUES (%s, %s, %s, %s, %s)',
        (data['name'], data['brand_id'], data['size'], data['color'], data['price']),
    )
    return format_response({'message': 'Shoe added', 'id': shoe_id}, 201)


@bp.route('/shoes/<int:shoe_id>', methods=['PUT'])
@jwt_required
@require_json
def update_shoe(shoe_id):
    data = request.get_json()
    valid, errors = validate_shoe_payload(data, partial=True)
    if not valid:
        return format_response({'error': errors}, 400)
    if not data:
        return format_response({'error': 'No fields provided'}, 400)

    fields = ', '.join(f"{key} = %s" for key in data.keys())
    params = tuple(data.values()) + (shoe_id,)
    execute(f'UPDATE shoes SET {fields} WHERE id = %s', params)
    return format_response({'message': 'Shoe updated'})


@bp.route('/shoes/<int:shoe_id>', methods=['DELETE'])
@jwt_required
def delete_shoe(shoe_id):
    execute('DELETE FROM shoes WHERE id = %s', (shoe_id,))
    return format_response({'message': 'Shoe deleted'})


# Brands CRUD Endpoints
@bp.route('/brands', methods=['GET'])
def get_brands():
    brands = fetch_all('SELECT * FROM brands')
    return format_response({'brands': brands})


@bp.route('/brands/<int:brand_id>', methods=['GET'])
def get_brand(brand_id):
    if brand_id < 1:
        return format_response({'error': 'Invalid brand ID'}, 400)
    brand = fetch_one('SELECT * FROM brands WHERE id = %s', (brand_id,))
    if not brand:
        return format_response({'error': 'Brand not found'}, 404)
    return format_response({'brand': brand})


@bp.route('/brands', methods=['POST'])
@jwt_required
@require_json
def add_brand():
    data = request.get_json()
    if 'name' not in data:
        return format_response({'error': 'Name is required'}, 400)
    brand_id = execute('INSERT INTO brands (name) VALUES (%s)', (data['name'],))
    return format_response({'message': 'Brand added', 'id': brand_id}, 201)


@bp.route('/brands/<int:brand_id>', methods=['PUT'])
@jwt_required
@require_json
def update_brand(brand_id):
    data = request.get_json()
    if 'name' not in data:
        return format_response({'error': 'Name is required'}, 400)
    execute('UPDATE brands SET name = %s WHERE id = %s', (data['name'], brand_id))
    return format_response({'message': 'Brand updated'})


@bp.route('/brands/<int:brand_id>', methods=['DELETE'])
@jwt_required
def delete_brand(brand_id):
    execute('DELETE FROM brands WHERE id = %s', (brand_id,))
    return format_response({'message': 'Brand deleted'})


# Users CRUD Endpoints
@bp.route('/users', methods=['GET'])
@jwt_required
def get_users():
    users = fetch_all('SELECT id, username, email FROM users')
    return format_response({'users': users})


@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    if user_id < 1:
        return format_response({'error': 'Invalid user ID'}, 400)
    user = fetch_one('SELECT id, username, email FROM users WHERE id = %s', (user_id,))
    if not user:
        return format_response({'error': 'User not found'}, 404)
    return format_response({'user': user})


# Reviews CRUD Endpoints
@bp.route('/reviews', methods=['GET'])
def get_reviews():
    reviews = fetch_all('SELECT * FROM reviews')
    return format_response({'reviews': reviews})


@bp.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    if review_id < 1:
        return format_response({'error': 'Invalid review ID'}, 400)
    review = fetch_one('SELECT * FROM reviews WHERE id = %s', (review_id,))
    if not review:
        return format_response({'error': 'Review not found'}, 404)
    return format_response({'review': review})


@bp.route('/reviews', methods=['POST'])
@jwt_required
@require_json
def add_review():
    data = request.get_json()
    required = ['user_id', 'shoe_id', 'rating', 'comment']
    missing = [field for field in required if field not in data]
    if missing:
        return format_response({'error': f"Missing fields: {', '.join(missing)}"}, 400)
    if not validate_numeric(data['rating']):
        return format_response({'error': 'Rating must be numeric'}, 400)

    review_id = execute(
        'INSERT INTO reviews (user_id, shoe_id, rating, comment) VALUES (%s, %s, %s, %s)',
        (data['user_id'], data['shoe_id'], data['rating'], data['comment']),
    )
    return format_response({'message': 'Review added', 'id': review_id}, 201)


@bp.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required
@require_json
def update_review(review_id):
    data = request.get_json()
    if not data:
        return format_response({'error': 'No fields provided'}, 400)
    if 'rating' in data and not validate_numeric(data['rating']):
        return format_response({'error': 'Rating must be numeric'}, 400)
    fields = ', '.join(f"{key} = %s" for key in data.keys())
    params = tuple(data.values()) + (review_id,)
    execute(f'UPDATE reviews SET {fields} WHERE id = %s', params)
    return format_response({'message': 'Review updated'})


@bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required
def delete_review(review_id):
    execute('DELETE FROM reviews WHERE id = %s', (review_id,))
    return format_response({'message': 'Review deleted'})


# Search endpoint (across shoes and brands)
@bp.route('/search', methods=['GET'])
def search():
    term = request.args.get('q', '')
    if not term:
        return format_response({'error': 'Query parameter q is required'}, 400)
    like_term = f"%{term}%"
    shoes = fetch_all('SELECT * FROM shoes WHERE name LIKE %s OR color LIKE %s', (like_term, like_term))
    brands = fetch_all('SELECT * FROM brands WHERE name LIKE %s', (like_term,))
    return format_response({'shoes': shoes, 'brands': brands})