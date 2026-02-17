#!/usr/bin/env python3
import os, sqlite3, logging, subprocess, sys
from datetime import datetime
from threading import Thread, Lock
import importlib
import numpy as np

# --- Auto Module Installer ---
modules = ["numpy","faiss-cpu"]
for m in modules:
    try: importlib.import_module(m)
    except ImportError:
        print(f"[Kessel Flow] Installing missing module: {m}")
        subprocess.check_call([sys.executable,"-m","pip","install",m])

# --- LLaMA / Stub ---
try:
    from llama_cpp import Llama
    USE_STUB=False
except ImportError:
    USE_STUB=True

# --- Logging ---
logging.basicConfig(filename="agent.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- DB & Memory ---
DB_PATH="agent_memory.db"
conn=sqlite3.connect(DB_PATH,check_same_thread=False)
c=conn.cursor()
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

db_lock = Lock()  # Thread-safe SQLite

def db_execute(query, params=()):
    with db_lock:
        c.execute(query, params)
        conn.commit()
        if query.strip().upper().startswith("SELECT"):
            return c.fetchall()
        return None

# --- Vectors ---
EMBED_DIM=512
VECTOR_PATH="task_vectors.npy"
if os.path.exists(VECTOR_PATH):
    vectors=np.load(VECTOR_PATH,allow_pickle=True).item()
else:
    vectors={}

MODEL_PATH="/home/userland/very_rock_manifesto.bin"
class LlamaStub:
    def __init__(self,model_path=None): self.model_path=model_path
    def __call__(self,prompt,max_tokens=150):
        return {"choices":[{"text":f"[Stub Manifesto Brain] {prompt[:50]}..."}]}
llm = LlamaStub(MODEL_PATH) if USE_STUB else Llama(MODEL_PATH)

print("=== FRANKENAGENT 7.2 ACTIVE ===")
print("Brain:", "Stub" if USE_STUB else MODEL_PATH)
print("Kessel Flow ONLINE | Super Recall ON | Memory entries:", len(vectors))

# --- Functions ---
def embed_text(text): return np.random.rand(EMBED_DIM).astype("float32")
def generate_content(prompt,max_tokens=150,top_k=5):
    context=""
    if vectors:
        keys=list(vectors.keys())
        matrix=np.array([vectors[k] for k in keys])
        q=embed_text(prompt)
        sims=matrix@q
        top_indices=sims.argsort()[-top_k:][::-1]
        similar=[keys[i] for i in top_indices]
        for task_id in similar:
            r=db_execute("SELECT content,result FROM tasks WHERE id=?",(task_id,))
            if r and r[0][1]: context+=f"Prompt:{r[0][0]} | Result:{r[0][1]}\n"
    full_prompt=f"{context}New Prompt: {prompt}"
    logging.info(f"[Kessel Flow] Generating content: {prompt}")
    resp=llm(full_prompt,max_tokens=max_tokens)
    return resp.get("choices",[{}])[0].get("text","[No output]")

def execute_task(task_id,task_type,content):
    try:
        if task_type=="content_creation":
            output=generate_content(content)
            vectors[task_id]=embed_text(content)
            np.save(VECTOR_PATH,vectors)
        else:
            output=subprocess.check_output(content,shell=True,stderr=subprocess.STDOUT).decode()
        status="done"
    except Exception as e:
        output=str(e)
        status="failed"
    db_execute("UPDATE tasks SET status=?, result=? WHERE id=?", (status,output,task_id))

def check_tasks():
    while True:
        pending=db_execute("SELECT id,type,content FROM tasks WHERE status='pending'")
        threads=[]
        for task in pending:
            t=Thread(target=execute_task,args=(task[0],task[1],task[2]))
            t.start(); threads.append(t)
        for t in threads: t.join()

def show_memory():
    rows=db_execute("SELECT id,type,content,status FROM tasks ORDER BY id DESC LIMIT 10")
    print("=== Last 10 tasks ===")
    for r in rows: print(r)

def search_memory(keyword):
    rows=db_execute("SELECT id,type,content,status,result FROM tasks WHERE content LIKE ?", ('%'+keyword+'%',))
    print(f"=== Search: {keyword} ===")
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
            prompt=input("Enter assistant task: ").strip()
            db_execute("INSERT INTO tasks (timestamp,type,content,status,result) VALUES (?,?,?,?,?)",
                       (datetime.now().isoformat(),"personal_assistant",prompt,"pending",None))
        elif choice=="3": show_memory()
        elif choice=="4":
            keyword=input("Keyword: ").strip()
            search_memory(keyword)
        elif choice=="5":
            print("Exiting CLI. FRANKENAGENT keeps learning in background."); break
        else: print("Invalid choice.")

if __name__=="__main__":
    t=Thread(target=check_tasks,daemon=True); t.start()
    cli()
