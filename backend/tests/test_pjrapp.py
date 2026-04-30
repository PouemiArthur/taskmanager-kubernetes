from src.pjrapp import get_db_conn, init_db, get_tasks, create_task, update_task, delete_task, cache_stats

def test_get_db_conn():
    assert get_db_conn() == "get_db_conn test passed!"

def test_init_db():
    assert init_db() == "init_db test passed!"

def test_get_tasks():
    assert get_tasks() == "get_tasks test passed!"

def test_create_task():
    assert create_task() == "create_task test passed!"

def test_update_task():
    assert update_task() == "update_task test passed!"

def test_delete_task():
    assert delete_task() == "delete_task test passed!"

def test_cache_stats():
    assert cache_stats() == "cache_stats test passed!"


