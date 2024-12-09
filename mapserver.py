from flask import Flask, jsonify, send_file, redirect, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def home():
    return redirect('/render')  # Redirect root to the render page

@app.route('/maps/<path:filename>')
def get_map_file(filename):
    map_folder = os.path.join(os.getcwd(), "maps")
    return send_from_directory(map_folder, filename)

@app.route('/render')
def render_view():
    return send_file("web_view/index.html")  # Serve the HTML viewer

@app.route('/<path:filename>')
def serve_static(filename):
    static_folder = os.path.join(os.getcwd(), "web_view")
    return send_from_directory(static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True)