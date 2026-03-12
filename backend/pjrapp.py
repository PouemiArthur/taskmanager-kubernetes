from flask import Flask, request, jsonify
import psycopg2
import redis
import json
import os
import time
import psycopg2.pool
from contextlib import contextmanager
import math

app = Flask(__name__)

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=6379,
    decode_responses=True
)

db_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=20,
    host=os.getenv('DB_HOST', 'localhost'),
    database=os.getenv('DB_NAME', 'tasks'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'mypasswordpjr12')
)

@contextmanager
def get_db_conn():
    """Context manager to handle getting and returning connections to the pool."""
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        # Crucial: Always return the connection back to the pool
        db_pool.putconn(conn)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully!")

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/stress')
def stress():
      for i in range(1000000):
          math.sqrt(i)
      return jsonify({"message":"CPU usage increased!"})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    cached_tasks = redis_client.get('all_tasks')
    if cached_tasks:
        print("Cache HIT! Returning from Redis")
        return jsonify(json.loads(cached_tasks))
    
    print("Cache MISS! Fetching from database")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, title, description, completed, created_at, updated_at FROM tasks')
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    
    tasks_list = [{
        'id': task[0],
        'title': task[1],
        'description': task[2],
        'completed': task[3],
        'created_at': task[4].isoformat() if task[4] else None,
        'updated_at': task[5].isoformat() if task[5] else None
    } for task in tasks]
    
    redis_client.setex('all_tasks', 60, json.dumps(tasks_list))
    
    return jsonify(tasks_list)

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, title, description, completed FROM tasks WHERE id = %s', (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()
    
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({
        'id': task[0],
        'title': task[1],
        'description': task[2],
        'completed': task[3],
        'created_at': task[4].isoformat() if task[4] else None,
        'updated_at': task[5].isoformat() if task[5] else None
    })

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    
    # Using 'with' ensures the connection returns to the pool even if an error occurs
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING id',
            (title, description)
        )
        task_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    
    redis_client.delete('all_tasks')
    return jsonify({'id': task_id, 'title': title, 'completed': False}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    
    updates = []
    values = []
    
    if 'title' in data:
        updates.append('title = %s')
        values.append(data['title'])
    
    if 'description' in data:
        updates.append('description = %s')
        values.append(data['description'])
    
    if 'completed' in data:
        updates.append('completed = %s')
        values.append(data['completed'])
    

    updates.append('updated_at = CURRENT_TIMESTAMP')

    if len(updates) == 1:
        return jsonify({'error': 'No fields to update'}), 400
    
    values.append(task_id)
    
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s"
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, values)
    rows_affected = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Task not found'}), 404
    
    # Invalidate cache when task is updated
    redis_client.delete('all_tasks')
    
    return jsonify({'message': 'Task updated successfully'}), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    rows_affected = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Task not found'}), 404
    
    # Invalidate cache when task is deleted
    redis_client.delete('all_tasks')
    
    return jsonify({'message': 'Task deleted'}), 200

# New endpoint to check cache stats
@app.route('/cache/stats')
def cache_stats():
    info = redis_client.info('stats')
    return jsonify({
        'redis_connected': True,
        'total_commands_processed': info.get('total_commands_processed', 0),
        'keyspace_hits': info.get('keyspace_hits', 0),
        'keyspace_misses': info.get('keyspace_misses', 0)
    })

if __name__ == '__main__':
    print("Starting Flask application...")
    init_db()
    print("Flask app running on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
