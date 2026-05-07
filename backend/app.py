"""
图书馆管理系统 - Flask 后端
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'library-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://postgres:library123@localhost:5432/library'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-2026')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ==================== 数据库模型 ====================

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='librarian')  # admin/librarian
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }


class Book(db.Model):
    """图书表"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(20), unique=True)
    publisher = db.Column(db.String(100))  # 出版社
    published_date = db.Column(db.Date)     # 出版日期
    category = db.Column(db.String(50))     # 分类/类型
    price = db.Column(db.Float, default=0)  # 价格
    stock = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    cover = db.Column(db.String(500))       # 封面图URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    borrowings = db.relationship('Borrowing', backref='book', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'publisher': self.publisher,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'category': self.category,
            'price': self.price,
            'stock': self.stock,
            'description': self.description,
            'cover': self.cover,
            'available': self.stock - len([b for b in self.borrowings if b.status == 'borrowed'])
        }


class Reader(db.Model):
    """读者表"""
    __tablename__ = 'readers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    register_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    borrowings = db.relationship('Borrowing', backref='reader', lazy=True)
    
    @property
    def borrowed_count(self):
        return len([b for b in self.borrowings if b.status == 'borrowed'])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'register_date': self.register_date.isoformat() if self.register_date else None,
            'borrowed_count': self.borrowed_count
        }


class Borrowing(db.Model):
    """借阅记录表"""
    __tablename__ = 'borrowings'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    reader_id = db.Column(db.Integer, db.ForeignKey('readers.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')  # borrowed/returned/overdue
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'reader_id': self.reader_id,
            'book_title': self.book.title if self.book else None,
            'reader_name': self.reader.name if self.reader else None,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status
        }


# ==================== 认证 API ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    })


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify(user.to_dict())


# ==================== 图书 API ====================

@app.route('/api/books', methods=['GET'])
def get_books():
    """获取图书列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Book.query
    
    if search:
        query = query.filter(
            (Book.title.contains(search)) | 
            (Book.author.contains(search)) |
            (Book.isbn.contains(search))
        )
    
    if category:
        query = query.filter(Book.category == category)
    
    pagination = query.order_by(Book.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'books': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """获取图书详情"""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@app.route('/api/books', methods=['POST'])
@jwt_required()
def create_book():
    """添加图书"""
    data = request.get_json()
    
    book = Book(
        title=data.get('title'),
        author=data.get('author'),
        isbn=data.get('isbn'),
        category=data.get('category'),
        publish_date=datetime.strptime(data['publish_date'], '%Y-%m-%d').date() if data.get('publish_date') else None,
        stock=data.get('stock', 1),
        description=data.get('description')
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    """更新图书"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.isbn = data.get('isbn', book.isbn)
    book.category = data.get('category', book.category)
    book.stock = data.get('stock', book.stock)
    book.description = data.get('description', book.description)
    
    if data.get('publish_date'):
        book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
    
    db.session.commit()
    
    return jsonify(book.to_dict())


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    """删除图书"""
    book = Book.query.get_or_404(book_id)
    
    # 检查是否有未还的借阅
    active_borrowing = Borrowing.query.filter_by(
        book_id=book_id, status='borrowed'
    ).first()
    
    if active_borrowing:
        return jsonify({'error': '该图书有未还借阅，无法删除'}), 400
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': '删除成功'})


# ==================== 读者 API ====================

@app.route('/api/readers', methods=['GET'])
def get_readers():
    """获取读者列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Reader.query
    
    if search:
        query = query.filter(
            (Reader.name.contains(search)) | 
            (Reader.phone.contains(search))
        )
    
    pagination = query.order_by(Reader.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'readers': [reader.to_dict() for reader in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@app.route('/api/readers/<int:reader_id>', methods=['GET'])
def get_reader(reader_id):
    """获取读者详情"""
    reader = Reader.query.get_or_404(reader_id)
    return jsonify(reader.to_dict())


@app.route('/api/readers', methods=['POST'])
@jwt_required()
def create_reader():
    """添加读者"""
    data = request.get_json()
    
    reader = Reader(
        name=data.get('name'),
        gender=data.get('gender'),
        age=data.get('age'),
        phone=data.get('phone')
    )
    
    db.session.add(reader)
    db.session.commit()
    
    return jsonify(reader.to_dict()), 201


@app.route('/api/readers/<int:reader_id>', methods=['PUT'])
@jwt_required()
def update_reader(reader_id):
    """更新读者"""
    reader = Reader.query.get_or_404(reader_id)
    data = request.get_json()
    
    reader.name = data.get('name', reader.name)
    reader.gender = data.get('gender', reader.gender)
    reader.age = data.get('age', reader.age)
    reader.phone = data.get('phone', reader.phone)
    
    db.session.commit()
    
    return jsonify(reader.to_dict())


@app.route('/api/readers/<int:reader_id>', methods=['DELETE'])
@jwt_required()
def delete_reader(reader_id):
    """删除读者"""
    reader = Reader.query.get_or_404(reader_id)
    
    # 检查是否有未还的借阅
    active_borrowing = Borrowing.query.filter_by(
        reader_id=reader_id, status='borrowed'
    ).first()
    
    if active_borrowing:
        return jsonify({'error': '该读者有未还图书，无法删除'}), 400
    
    db.session.delete(reader)
    db.session.commit()
    
    return jsonify({'message': '删除成功'})


# ==================== 借阅 API ====================

@app.route('/api/borrowings', methods=['GET'])
def get_borrowings():
    """获取借阅记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    
    query = Borrowing.query
    
    if status:
        query = query.filter(Borrowing.status == status)
    
    pagination = query.order_by(Borrowing.borrow_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'borrowings': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@app.route('/api/borrowings', methods=['POST'])
@jwt_required()
def borrow_book():
    """借书"""
    data = request.get_json()
    book_id = data.get('book_id')
    reader_id = data.get('reader_id')
    days = data.get('days', 30)  # 默认借30天
    
    # 检查图书
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': '图书不存在'}), 404
    
    # 检查库存
    available = book.stock - Borrowing.query.filter_by(
        book_id=book_id, status='borrowed'
    ).count()
    
    if available <= 0:
        return jsonify({'error': '图书库存不足'}), 400
    
    # 检查读者
    reader = Reader.query.get(reader_id)
    if not reader:
        return jsonify({'error': '读者不存在'}), 404
    
    # 检查读者是否有逾期未还
    overdue = Borrowing.query.filter_by(
        reader_id=reader_id, status='overdue'
    ).first()
    
    if overdue:
        return jsonify({'error': '读者有逾期未还的图书'}), 400
    
    # 创建借阅记录
    borrowing = Borrowing(
        book_id=book_id,
        reader_id=reader_id,
        due_date=datetime.utcnow() + timedelta(days=days),
        status='borrowed'
    )
    
    db.session.add(borrowing)
    db.session.commit()
    
    return jsonify(borrowing.to_dict()), 201


@app.route('/api/borrowings/<int:borrowing_id>/return', methods=['PUT'])
@jwt_required()
def return_book(borrowing_id):
    """还书"""
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    
    if borrowing.status == 'returned':
        return jsonify({'error': '该图书已归还'}), 400
    
    borrowing.return_date = datetime.utcnow()
    borrowing.status = 'returned'
    
    db.session.commit()
    
    return jsonify(borrowing.to_dict())


# ==================== 统计 API ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    total_books = Book.query.count()
    total_readers = Reader.query.count()
    
    # 今日借阅
    today = datetime.utcnow().date()
    today_borrowings = Borrowing.query.filter(
        db.func.date(Borrowing.borrow_date) == today
    ).count()
    
    # 在借数量
    borrowed_count = Borrowing.query.filter_by(status='borrowed').count()
    
    # 逾期数量
    overdue_count = Borrowing.query.filter(
        Borrowing.status == 'borrowed',
        Borrowing.due_date < datetime.utcnow()
    ).count()
    
    # 更新逾期状态
    Borrowing.query.filter(
        Borrowing.status == 'borrowed',
        Borrowing.due_date < datetime.utcnow()
    ).update({'status': 'overdue'})
    db.session.commit()
    
    return jsonify({
        'total_books': total_books,
        'total_readers': total_readers,
        'today_borrowings': today_borrowings,
        'borrowed_count': borrowed_count,
        'overdue_count': overdue_count
    })


# ==================== 初始化数据 ====================

def init_db():
    """初始化数据库和默认数据"""
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
        
        # 创建默认图书管理员
        if not User.query.filter_by(username='librarian').first():
            librarian = User(username='librarian', role='librarian')
            librarian.set_password('librarian123')
            db.session.add(librarian)
        
        db.session.commit()
        print("数据库初始化完成！")
        print("默认账号: admin/admin123")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
