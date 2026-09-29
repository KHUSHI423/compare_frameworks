from flask import Blueprint, request, jsonify
from sqlalchemy import func
from .auth import jwt_required
from ..extensions import db
from ..models import Board, Task, TaskStatus
from ..schemas import TaskSchema, PaginatedSchema

tasks_bp = Blueprint('tasks', __name__, url_prefix='/boards/<int:board_id>/tasks')
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
paginated_schema = PaginatedSchema()

@tasks_bp.route('', methods=['POST'])
@jwt_required
def create_task(board_id, current_user=None):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first()
    if not board:
        return jsonify({"error": "Board not found or not owned"}), 404
        
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
        
    task = Task(
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'todo'),
        due_date=data.get('due_date'),
        board_id=board_id
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task_schema.dump(task)), 201

@tasks_bp.route('', methods=['GET'])
@jwt_required
def list_tasks(board_id, current_user=None):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first()
    if not board:
        return jsonify({"error": "Board not found or not owned"}), 404
        
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    status_filter = request.args.get('status')
    
    query = Task.query.filter_by(board_id=board_id)
    if status_filter and status_filter in ['todo', 'in_progress', 'done']:
        query = query.filter_by(status=TaskStatus[status_filter])
        
    total = query.count()
    items = query.offset((page-1)*page_size).limit(page_size).all()
    
    return jsonify(paginated_schema.dump({
        "items": tasks_schema.dump(items),
        "total": total,
        "page": page,
        "page_size": page_size
    }))

@tasks_bp.route('/<int:task_id>', methods=['PATCH'])
@jwt_required
def update_task(board_id, task_id, current_user=None):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first()
    if not board:
        return jsonify({"error": "Board not found or not owned"}), 404
        
    task = Task.query.filter_by(id=task_id, board_id=board_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
        
    data = request.get_json()
    for key in ['title', 'description', 'status', 'due_date']:
        if key in data:
            setattr(task, key, data[key])
            
    db.session.commit()
    return jsonify(task_schema.dump(task))

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required
def delete_task(board_id, task_id, current_user=None):
    board = Board.query.filter_by(id=board_id, owner_id=current_user.id).first()
    if not board:
        return jsonify({"error": "Board not found or not owned"}), 404
        
    task = Task.query.filter_by(id=task_id, board_id=board_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
        
    db.session.delete(task)
    db.session.commit()
    return '', 204