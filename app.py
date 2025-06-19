from flask import Flask, request
import os
import pandas as pd
import plotly.express as px

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    preview_html = ''
    chart_html = ''

    if request.method == 'POST':
        file = request.files['file']
        df = pd.read_excel(file)

        # Table preview
        preview_html = df.head().to_html(classes='table table-striped', index=False)

        # Plot first numeric column
        numeric_cols = df.select_dtypes(include='number').columns
        if not numeric_cols.any():
            chart_html = "<p>No numeric columns to plot.</p>"
        else:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            fig = px.line(df, x = x_col, y=y_col, title=f"Line Chart of '{y_col}'")
            chart_html = fig.to_html(full_html=False)

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Excel Uploader</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .section-title {{
                font-size: 1.5rem;
                font-weight: 600;
                margin-top: 2rem;
            }}
            .title-line {{
                height: 1px;
                background-color: #ccc;
                margin-bottom: 1rem;
                max-width: 600px;
            }}
        </style>
    </head>
    <body class="bg-light py-5">
        <div class="container" style="max-width: 800px;">
            <h1 class="mb-4">Upload Your Excel File</h1>
            <form method="POST" enctype="multipart/form-data" class="card p-4 shadow-sm mb-4">
                <input type="file" name="file" class="form-control mb-3" required>
                <button type="submit" class="btn btn-primary">Upload</button>
            </form>

            {'<div class="section-title">Preview</div><div class="title-line"></div>' + preview_html if preview_html else ''}
            {'<div class="section-title">Chart</div><div class="title-line"></div>' + chart_html if chart_html else ''}
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
