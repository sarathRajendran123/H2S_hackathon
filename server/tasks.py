# tasks.py
import multiprocessing
from multiprocessing import Manager
import time
from datetime import datetime, timedelta
import uuid
import threading

_manager = Manager()
TASKS = _manager.dict() 
_lock = threading.Lock()


def generate_task_id():
    return str(uuid.uuid4())


def start_task(request_data, session_id=None):
    from app import detect_text_logic

    task_id = generate_task_id()

    if session_id:
        for tid in get_session_tasks(session_id):
            cancel_task(tid)

    def task_wrapper(task_id, request_data):
        """Runs inside child process"""
        try:
            result = detect_text_logic(request_data)

            with _lock:
                if task_id in TASKS:
                    TASKS[task_id]["result"] = result

        except Exception as e:
            with _lock:
                if task_id in TASKS:
                    TASKS[task_id]["result"] = {"error": str(e)}
    p = multiprocessing.Process(target=task_wrapper, args=(task_id, request_data))

    p.start()

    with _lock:
        TASKS[task_id] = {
            "process": p,
            "result": None,
            "start_time": datetime.utcnow(),
            "session_id": session_id
        }

    return task_id


def task_running(task_id):
    with _lock:
        task = TASKS.get(task_id)
        return bool(task and task["process"].is_alive())


def get_task_result(task_id):
    with _lock:
        task = TASKS.get(task_id)
        if task:
            return task["result"]
        return None


def cancel_task(task_id):
    with _lock:
        task = TASKS.get(task_id)

        if not task:
            return False

        p = task["process"]
        if p.is_alive():
            p.terminate()
            p.join(timeout=2)

        task["result"] = {"status": "cancelled"}
        return True


def cancel_session_tasks(session_id):
    cancelled = []

    with _lock:
        for tid, task in list(TASKS.items()):
            if task.get("session_id") == session_id:
                p = task["process"]

                if p.is_alive():
                    p.terminate()
                    p.join(timeout=2)

                task["result"] = {"status": "cancelled", "reason": "user_exit"}
                cancelled.append(tid)

    return {"cancelled": len(cancelled), "task_ids": cancelled}


def cleanup_expired_tasks(max_age_minutes=30):
    now = datetime.utcnow()
    removed = []

    with _lock:
        for tid, task in list(TASKS.items()):
            if now - task["start_time"] > timedelta(minutes=max_age_minutes):
                p = task["process"]
                if p.is_alive():
                    p.terminate()
                    p.join()

                TASKS.pop(tid, None)
                removed.append(tid)

    return removed


def get_session_tasks(session_id):
    active = []

    with _lock:
        for tid, task in list(TASKS.items()):
            p = task["process"]

            if p.is_alive() and task.get("session_id") == session_id:
                active.append(tid)
            else:
                TASKS.pop(tid, None)

    return active
