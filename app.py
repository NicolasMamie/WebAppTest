from flask import Flask, request, render_template
import os
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h2>Upload Excel File</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit">
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # You can process the file here
    return f"Received file: {file.filename}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
