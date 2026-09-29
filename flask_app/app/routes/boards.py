from flask import Blueprint, request, jsonify
from sqlalchemy import func
from .auth import jwt_required
from ..extensions import db
from ..models import Board
from ..schemas import BoardSchema, PaginatedSchema

boards_bp = Blueprint('boards', __name__)
board_schema = BoardSchema()
boards_schema = BoardSchema(many=True)
paginated_schema = PaginatedSchema()
import os
import csv
import io
from flask import Blueprint, request, jsonify, send_file
from .auth import jwt_required
from ..extensions import db
from ..models import Board, Task, Attachment

UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ... [Previous Board Routes] ...

@boards_bp.route('/<int:board_id>/attachment', methods=['POST'])
@jwt_required
def upload_attachment(board_id, current_user=None):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first()
    if not board:
        return jsonify({"error": "Board not found or not owned"}), 404

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    safe_filename = f"{board_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    file.save(file_path)  # Sync save

    attachment = Attachment(
        board_id=board_id,
        file_path=file_path,
        original_filename=file.filename
    )
    db.session.add(attachment)
    db.session.commit()

    return jsonify({"url": f"/uploads/{safe_filename}", "filename": file.filename})

@boards_bp.route('/<int:board_id>/export', methods=['GET'])
@jwt_required
def export_tasks_csv(board_id, current_user=None):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first()
    if not board:
        return jsonify({"error": "Board not found or not owned"}), 404

    # Generate CSV in memory
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'title', 'status', 'due_date', 'created_at'])
    
    tasks = Task.query.filter_by(board_id=board_id).all()
    for task in tasks:
        writer.writerow([task.id, task.title, task.status.value, task.due_date, task.created_at])
    
    si.seek(0)
    return send_file(
        io.BytesIO(si.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'board_{board_id}_tasks.csv'
    )
@boards_bp.route('/boards', methods=['POST'])
@jwt_required
def create_board(current_user=None):
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
        
    board = Board(title=data['title'], owner_id=current_user.id)
    db.session.add(board)
    db.session.commit()
    return jsonify(board_schema.dump(board)), 201

@boards_bp.route('/boards', methods=['GET'])
@jwt_required
def list_boards(current_user=None):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    query = Board.query.filter_by(owner_id=current_user.id)
    total = query.count()
    items = query.offset((page-1)*page_size).limit(page_size).all()
    
    return jsonify(paginated_schema.dump({
        "items": boards_schema.dump(items),
        "total": total,
        "page": page,
        "page_size": page_size
    }))

@boards_bp.route('/boards/<int:board_id>', methods=['GET'])
@jwt_required
def get_board(board_id, current_user=None):
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    if board.owner_id != current_user.id:
        return jsonify({"error": "Not authorized"}), 403
    return jsonify(board_schema.dump(board))

@boards_bp.route('/boards/<int:board_id>', methods=['DELETE'])
@jwt_required
def delete_board(board_id, current_user=None):
    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404
    if board.owner_id != current_user.id:
        return jsonify({"error": "Not authorized"}), 403
        
    db.session.delete(board)
    db.session.commit()
    return '', 204