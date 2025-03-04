from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/flappy_bird.html')
def serve_html():
    return send_from_directory(os.getcwd(), 'flappy_bird.html')

if __name__ == '__main__':
    app.run(port=5000)  # You can choose any available port