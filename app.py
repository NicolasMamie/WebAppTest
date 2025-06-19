from flask import Flask, request, render_template
import os
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
      <title>Excel Uploader</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light text-center py-5">
      <div class="container">
        <h1 class="mb-4">Upload Your Excel File</h1>
        <form method="POST" action="/upload" enctype="multipart/form-data" class="card p-4 mx-auto" style="max-width: 400px;">
          <input type="file" name="file" class="form-control mb-3" required>
          <button type="submit" class="btn btn-primary">Upload</button>
        </form>
      </div>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # You can process the file here
    return f"Received file: {file.filename}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
