from flask import Flask, jsonify, request
import time
import base64
import io
import os
from factorial import linear_search, bubble_sort, nested_loops, binary_search
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from minio import Minio
import uuid

#matplotlib initilization stuff 
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

#getting minio cred
load_dotenv()
minio_user=os.getenv("minio_user")
minio_password=os.getenv("minio_password")

#setting up minio so we can upload the images
from minio import Minio

client = Minio(
    "34.207.164.36:9000",
    access_key=f"{minio_user}",
    secret_key=f"{minio_password}",
    secure=False
)


app = Flask(__name__)

#creating the db 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///algorithms.db"
db=SQLAlchemy(app)

class algorithm_info(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    algo_name=db.Column(db.String(50),nullable = False)
    items=db.Column(db.Integer,nullable = False)
    steps=db.Column(db.Integer,nullable = False)
    start_time=db.Column(db.Float,nullable = False)
    end_time=db.Column(db.Float,nullable = False)
    total_time_ms=db.Column(db.Float,nullable = False)
    time_complexity = db.Column(db.String(50),nullable = False)
    path_to_graph=db.Column(db.String(50),nullable = False)
  

with app.app_context():
    db.create_all()


def analyze_algo(algo_name,n,steps):
    overall_start = time.perf_counter()

    algo_name = request.args.get("algo")
    n = request.args.get("n")
    steps = request.args.get("steps")

    n = int(n)
    steps = int(steps)

    step_sizes = [int((i + 1) * n / steps) for i in range(steps)]

    results = []
    times = []

    #the algorithms available
    algorithms = {
        "linear_search": linear_search,
        "bubble_sort": bubble_sort,
        "binary_search": binary_search,
        "nested_loops": nested_loops
    }

    algo_func = algorithms[algo_name]

    for size in step_sizes:
        start = time.perf_counter()
        algo_func(size)
        end = time.perf_counter()
        # to get the total time the function run for 
        runtime = end - start
        results.append({
            "n": size,
            "time_seconds": runtime
        })
        times.append(runtime)

    #getting the graph
    plt.figure()
    plt.plot(step_sizes, times, marker="o")
    plt.title(f"Time Complexity Analysis: {algo_name}")
    plt.xlabel("Input Size (n)")
    plt.ylabel("Execution Time (seconds)")

    # Convert plot into Base64
    # buf = io.BytesIO()
    #where to save the image
    IMAGES_DIR = os.path.join(app.root_path, 'images')
    STATIC_DIR = os.path.join(IMAGES_DIR, 'static')
    

    file_name = f"{algo_name}{uuid.uuid4()}.png"

    #create full path by joining the image dir with the name 
    full_path=os.path.join(IMAGES_DIR,file_name)


    plt.savefig(full_path, format="png")
    
    # buf.seek(0)

    # graph_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    #saving the image to minio
    bucket_name = "public-images"

    # Ensure bucket exists
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    # Upload file
    client.fput_object(
        bucket_name,
        file_name,
        full_path,
        content_type="image/png"
    )

    # MinIO public URL (if bucket is public)
    path_to_graph = f"http://34.207.164.36:9000/{bucket_name}/{file_name}"

    overall_end = time.perf_counter()

    if algo_name == "linear_search" :
        time_complexity = "O(n)"
    elif algo_name == "bubble_sort" :
        time_complexity = "O(n2)"
    elif algo_name == "binary_search" :
        time_complexity = "O(log n)"
    elif algo_name == "nested_loops" :
        time_complexity = "O(n2)"             

    response = {
        "algorithm": algo_name,
        "items": n,
        "time_complexity": time_complexity,
        "steps": steps,
        "start_time":start,
        "end_time":end,
        "total_analysis_time_seconds": overall_end - overall_start,
        # "results": results,
        # "graph_base64": graph_base64
        "path_to_graph":path_to_graph
    }
    return response
@app.route("/")
def home():
    return "Complexity Analyzer Running"



@app.route("/analyze", methods=["GET"])
def analyze():

    algo_name = request.args.get("algo")
    n = int(request.args.get("n"))
    steps = int(request.args.get("steps"))
    
    data = analyze_algo(algo_name, n, steps)
    return jsonify(data)

    

@app.route("/save_analysis", methods=["POST"])
def save_analysis():
    # Get from request JSON body instead of query params
    data = request.get_json()
    
    try:
        new_record = algorithm_info(
            algo_name=data["algorithm"],
            items=data["items"],
            steps=data["steps"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            total_time_ms=data["total_time_ms"],
            time_complexity=data["time_complexity"],
            path_to_graph=data["path_to_graph"]
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        return jsonify({"message": "saved!", "id": new_record.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/retrieve_analysis/<id>", methods=["GET"])
def retrieve_analysis(id):
    data = algorithm_info.query.filter_by(id=id).first()
    
    if not data:
        return jsonify({"error": "Not found"}), 404
    
    return jsonify({
        "id": data.id,
        "algo_name": data.algo_name,
        "items": data.items,
        "steps": data.steps,
        "start_time":data.start_time,
        "end_time":data.end_time,
        "time_complexity": data.time_complexity,
        "path_to_graph": data.path_to_graph
    })

if __name__ == "__main__":
    app.run(debug=True, port=3000)
