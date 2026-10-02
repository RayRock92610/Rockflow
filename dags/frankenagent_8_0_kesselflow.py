#!/usr/bin/env python3
import os, sqlite3, logging, time, threading, subprocess, shlex
from datetime import datetime
import numpy as np
import requests
import json
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("⚠ youtube_transcript_api not installed. Run: pip install youtube_transcript_api")

# ---------------------------
# Logging setup
logging.basicConfig(filename="frankenagent_8.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------------------------
# Database setup
DB_PATH="agent_memory.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute("PRAGMA journal_mode=WAL;")
# Auto-patch columns
existing_cols=[row[1] for row in c.execute("PRAGMA table_info(tasks)")]
if "result" not in existing_cols:
    c.execute("ALTER TABLE tasks ADD COLUMN result TEXT")
c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    type TEXT,
    content TEXT,
    status TEXT,
    result TEXT
)
""")
conn.commit()
db_lock = threading.Lock()

def db_execute(query, params=()):
    with db_lock:
        c.execute(query, params)
        conn.commit()
        if query.strip().upper().startswith("SELECT"):
            return c.fetchall()
        return None

# ---------------------------
# Memory vectors
# 🛡️ Security note: Using JSON instead of numpy's allow_pickle=True to prevent arbitrary code execution (ACE) vulnerabilities during deserialization.
VECTOR_PATH="task_vectors.json"
EMBED_DIM=512
if os.path.exists(VECTOR_PATH):
    with open(VECTOR_PATH, "r") as f:
        vectors = {int(k): np.array(v, dtype="float32") for k, v in json.load(f).items()}
else:
    vectors={}

def embed_text(text):
    return np.random.rand(EMBED_DIM).astype("float32")

def update_vector(task_id, content):
    vectors[task_id] = embed_text(content)
    # 🛡️ Security note: Safely serializing vector data to JSON format to avoid relying on insecure pickle formats.
    with open(VECTOR_PATH, "w") as f:
        json.dump({str(k): v.tolist() for k, v in vectors.items()}, f)

# ---------------------------
# Rayrock Decree enforcement
ALLOWED_COMMANDS = {
    "git",
    "pytest",
    "python3",
    "ls",
    "echo",
}

def obey_rayrock_decree(content: str) -> list[str]:
    """
    Validates and tokenizes the command payload against a strict allowlist.
    Raises ValueError if the executable is unauthorized or tokens are malformed.
    """
    if not content or not content.strip():
        raise ValueError("Empty command payload rejected by decree.")

    tokens = shlex.split(content.strip())
    if not tokens:
        raise ValueError("Invalid command formatting.")

    # Extract base executable name (strip directory paths to avoid path traversal)
    executable = os.path.basename(tokens[0])

    if executable not in ALLOWED_COMMANDS:
        raise ValueError(f"Command '{executable}' is unauthorized by decree.")

    # Guard against interpreter abuse (e.g., python3 -c 'import os; os.system(...)')
    if executable == "python3" and any(arg in ("-c", "-m") for arg in tokens[1:]):
        raise ValueError("Arbitrary execution flags (-c, -m) forbidden for python3.")

    return tokens


# ---------------------------
# Task executor
def execute_task(task_id, task_type, content):
    try:
        if task_type=="content_creation":
            output=content
            update_vector(task_id, content)
        else:
            cmd_tokens = obey_rayrock_decree(content)
            output=subprocess.check_output(cmd_tokens, shell=False, text=True, timeout=30, stderr=subprocess.STDOUT)
        status="done"
    except Exception as e:
        logging.error("Task failed due to %s for task_id=%s", type(e).__name__, task_id)
        output=json.dumps({"status": "FAILED", "error_type": type(e).__name__})
        status="failed"
    db_execute("UPDATE tasks SET status=?, result=? WHERE id=?", (status, output, task_id))

def check_tasks():
    while True:
        pending=db_execute("SELECT id,type,content FROM tasks WHERE status='pending'")
        threads=[]
        for task in pending:
            t=threading.Thread(target=execute_task,args=(task[0],task[1],task[2]))
            t.start(); threads.append(t)
        for t in threads: t.join()
        time.sleep(1)

# ---------------------------
# Auto-ingestion
def fetch_reddit(subreddit="python", limit=5):
    try:
        url=f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
        headers={"User-Agent":"KesselFlowAgent/0.1"}
        r=requests.get(url, headers=headers, timeout=10)
        posts=r.json().get("data",{}).get("children",[])
        for p in posts:
            title=p["data"]["title"]
            db_execute("INSERT INTO tasks (timestamp,type,content,status,result) VALUES (?,?,?,?,?)",
                       (datetime.now().isoformat(),"content_creation",f"[Reddit {subreddit}] {title}","pending",None))
    except Exception as e:
        logging.error("Reddit fetch failed due to %s", type(e).__name__)

def fetch_youtube_transcripts(video_ids):
    for vid in video_ids:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([x['text'] for x in transcript])
            db_execute("INSERT INTO tasks (timestamp,type,content,status,result) VALUES (?,?,?,?,?)",
                       (datetime.now().isoformat(),"content_creation",f"[YouTube {vid}] {text[:500]}","pending",None))
        except Exception as e:
            logging.warning("YouTube transcript failed for %s due to %s", vid, type(e).__name__)

def auto_ingest_loop():
    while True:
        fetch_reddit("learnpython", limit=3)
        fetch_youtube_transcripts(["UC_x5XG1OV2P6uZZ5FSM9Ttw"])
        time.sleep(300)

# ---------------------------
# CLI
def show_memory():
    rows=db_execute("SELECT id,type,content,status FROM tasks ORDER BY id DESC LIMIT 10")
    print("=== Last 10 tasks ===")
    for r in rows: print(r)

def cli():
    while True:
        print("\nOptions: 1-Content | 2-Assistant | 3-Show Memory | 4-Search Memory | 5-Exit")
        choice=input("Choose: ").strip()
        if choice=="1":
            prompt=input("Enter content prompt: ").strip()
            db_execute("INSERT INTO tasks (timestamp,type,content,status,result) VALUES (?,?,?,?,?)",
                       (datetime.now().isoformat(),"content_creation",prompt,"pending",None))
        elif choice=="2":
            task=input("Enter assistant task: ").strip()
            db_execute("INSERT INTO tasks (timestamp,type,content,status,result) VALUES (?,?,?,?,?)",
                       (datetime.now().isoformat(),"personal_assistant",task,"pending",None))
        elif choice=="3": show_memory()
        elif choice=="4":
            keyword=input("Keyword: ").strip()
            rows=db_execute("SELECT id,type,content,status,result FROM tasks WHERE content LIKE ?", ('%'+keyword+'%',))
            for r in rows: print(r)
        elif choice=="5": break
        else: print("Invalid choice.")

if __name__=="__main__":
    threading.Thread(target=check_tasks, daemon=True).start()
    threading.Thread(target=auto_ingest_loop, daemon=True).start()
    print("=== FRANKENAGENT 8.0 KESSEL FLOW ACTIVE ===")
    print("Memory entries:", len(vectors))
    cli()
