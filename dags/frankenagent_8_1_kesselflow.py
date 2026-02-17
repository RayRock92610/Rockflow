#!/usr/bin/env python3
import os, sqlite3, logging, time, threading, subprocess, json
from datetime import datetime
import numpy as np
import requests

# ---------------------------
# Logging setup
logging.basicConfig(filename="frankenagent_8_1.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------------------------
# DB + persistent memory
DB_PATH="agent_memory.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute("PRAGMA journal_mode=WAL;")
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

VECTOR_PATH="task_vectors.npy"
EMBED_DIM=512
if os.path.exists(VECTOR_PATH):
    vectors=np.load(VECTOR_PATH, allow_pickle=True).item()
else:
    vectors={}

def db_execute(query, params=()):
    with db_lock:
        c.execute(query, params)
        conn.commit()
        if query.strip().upper().startswith("SELECT"):
            return c.fetchall()
        return None

def embed_text(text):
    return np.random.rand(EMBED_DIM).astype("float32")

def update_vector(task_id, content):
    vectors[task_id] = embed_text(content)
    np.save(VECTOR_PATH, vectors)

# ---------------------------
# Rayrock Decree
def obey_rayrock_decree(task_type, content):
    forbidden=["rm -rf","sudo"]
    for f in forbidden:
        if f in content: return False, "Blocked by Rayrock Decree"
    return True, None

# ---------------------------
# Task execution
def execute_task(task_id, task_type, content):
    allowed,msg=obey_rayrock_decree(task_type, content)
    if not allowed:
        db_execute("UPDATE tasks SET status=?, result=? WHERE id=?", ("blocked", msg, task_id))
        return
    try:
        if task_type=="content_creation":
            output=content
            update_vector(task_id, content)
        else:
            output=subprocess.check_output(content, shell=True, stderr=subprocess.STDOUT).decode()
        status="done"
    except Exception as e:
        output=str(e)
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
        logging.error(f"Reddit fetch failed: {e}")

def fetch_youtube_transcripts(video_ids):
    for vid in video_ids:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([x['text'] for x in transcript])
            db_execute("INSERT INTO tasks (timestamp,type,content,status,result) VALUES (?,?,?,?,?)",
                       (datetime.now().isoformat(),"content_creation",f"[YouTube {vid}] {text[:500]}","pending",None))
        except Exception as e:
            logging.warning(f"YouTube transcript failed for {vid}: {e}")

def auto_ingest_loop():
    while True:
        fetch_reddit("learnpython", limit=3)
        fetch_youtube_transcripts(["UC_x5XG1OV2P6uZZ5FSM9Ttw"])
        time.sleep(300)

# ---------------------------
# Semantic search
def cosine_sim(v1,v2):
    return np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)+1e-10)

def semantic_search(query, top_k=5):
    q_vec=embed_text(query)
    scores=[(tid, cosine_sim(q_vec, vec)) for tid,vec in vectors.items()]
    scores.sort(key=lambda x:x[1], reverse=True)
    results=[]
    for tid,score in scores[:top_k]:
        row=db_execute("SELECT id,type,content,status,result FROM tasks WHERE id=?",(tid,))
        if row: results.append(row[0])
    return results

# ---------------------------
# CLI
def show_memory():
    rows=db_execute("SELECT id,type,content,status,result FROM tasks ORDER BY id DESC LIMIT 10")
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
            results=semantic_search(keyword)
            for r in results: print(r)
        elif choice=="5": break
        else: print("Invalid choice.")

if __name__=="__main__":
    threading.Thread(target=check_tasks, daemon=True).start()
    threading.Thread(target=auto_ingest_loop, daemon=True).start()
    print("=== FRANKENAGENT 8.1 KESSEL FLOW ACTIVE ===")
    print("Memory entries:", len(vectors))
    cli()
