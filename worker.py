from rq import Worker
from app.config import get_worker_queue

if __name__ == "__main__":
    q = get_worker_queue()
    w = Worker(q)
    w.work()
