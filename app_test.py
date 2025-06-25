from flask import Flask, request, send_from_directory, jsonify
import os
import pandas as pd
import plotly.graph_objects as go

fig = go.Figure()
reorder_point = None

app = Flask(__name__)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route('/', methods=['GET', 'POST'])  # ✅ This must go directly above index()
def index():
    global fig, reorder_point

    preview_html = ''
    chart_html = ''

    if request.method == 'POST':
        file = request.files.get('file')
        reorder_point = request.form.get('reorder_point', type=float)

        if file:
            df = pd.read_excel(file)

            # Generate preview
            preview_html = df.head().to_html(classes='table table-striped', index=False)

            # Plot
            numeric_cols = df.select_dtypes(include='number').columns
            date_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns

            if not numeric_cols.any():
                chart_html = "<p>No numeric columns to plot.</p>"
            else:
                date_col_in = date_cols[0]
                date_col_out = date_cols[1]

                col_in = numeric_cols[0]
                col_out = numeric_cols[1]

                df_in = df[[date_col_in, col_in]].copy()
                df_in['Type'] = 'Purchase'
                df_in.rename(columns={date_col_in: 'Time', col_in: 'Quantity'}, inplace=True)

                df_out = df[[date_col_out, col_out]].copy()
                df_out['Type'] = 'Sale'
                df_out.rename(columns={date_col_out: 'Time', col_out: 'Quantity'}, inplace=True)

                if df_out['Quantity'].sum() > 0:
                    df_out['Quantity'] = -df_out['Quantity']

                df_combined = pd.concat([df_in, df_out])
                df_combined['Time'] = pd.to_datetime(df_combined['Time']).dt.date
                df_combined = df_combined.sort_values('Time')
                df_combined.dropna(inplace=True)

                df_pivot = df_combined.pivot_table(
                    index='Time',
                    columns='Type',
                    values='Quantity',
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_pivot['Time'],
                    y=df_pivot.get('Purchase', [0]*len(df_pivot)),
                    name='Purchase',
                    marker_color='green'
                ))
                fig.add_trace(go.Bar(
                    x=df_pivot['Time'],
                    y=df_pivot.get('Sale', [0]*len(df_pivot)),
                    name='Sale',
                    marker_color='red'
                ))

                fig.update_layout(
                    title=f"Bar Chart of '{col_in}'",
                    xaxis_title='Time',
                    yaxis_title='QTY',
                    barmode='group',
                    xaxis=dict(type='category')
                )

                if reorder_point:
                    fig.add_hline(y=reorder_point, line_dash="dot", line_color="blue", annotation_text="Reorder Point", name="reorder_point")

        if reorder_point:
            # Clean up previous Reorder Point lines/shapes
            if 'shapes' in fig.layout:
                fig.layout.shapes = tuple(
                    shape for shape in fig.layout.shapes
                    if getattr(shape, 'name', None) != 'reorder_point'
                )
            if 'annotations' in fig.layout:
                fig.layout.annotations = tuple(
                    ann for ann in fig.layout.annotations
                    if getattr(ann, 'text', None) != 'Reorder Point'
                )
            fig.add_hline(y=reorder_point, line_dash="dot", line_color="blue", annotation_text="Reorder Point", name="reorder_point")

        chart_html = fig.to_html(full_html=False)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'preview_html': preview_html,
                'chart_html': chart_html
            })

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Excel Uploader</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="/static/main.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light py-5">
        <div class="container" style="max-width: 800px;">
            <h1 class="mb-4">Welcome to Soltar Reorder Point Optimizer</h1>
            <!-- Static content stays here -->
    <h1 class="mb-4">Welcome to Soltar Reorder Point Optimizer</h1>

    <div class="section-title">Upload Purchase Orders and Consumption</div>
    <div class="title-line"></div>

    <div class="mb-4">
        <p>Please upload your Excel file containing both <strong>Purchase Orders</strong> and <strong>Consumption Data</strong> in the following format.</p>
        <img src="/images/excel_image.PNG" class="img-fluid rounded shadow-sm" style="max-width: 70%; height: auto;">
    </div>

    <!-- Forms stay -->
    ...

    <!-- Only these update dynamically -->
    <div id="preview-section">
        {'<div class="section-title">Preview</div><div class="title-line"></div>' + preview_html if preview_html else ''}
    </div>
    <div id="chart-section">
        {'<div class="section-title">Chart</div><div class="title-line"></div>' + chart_html if chart_html else ''}
    </div>


            <div class="row">
                <div class="col-md-6">
                    <form id="upload-form" method="POST" enctype="multipart/form-data" class="card p-4 shadow-sm mb-4">
                        <input type="file" name="file" class="form-control mb-3" required>
                        <button type="submit" class="btn btn-primary">Upload</button>
                    </form>
                </div>
                <div class="col-md-6">
                    <form id="reorder-form" method="POST" class="card p-4 shadow-sm mb-4">
                        <label for="reorder_point" class="form-label">Enter Reorder Point</label>
                        <input type="number" name="reorder_point" class="form-control mb-3" placeholder="e.g., 150" required>
                        <button type="submit" class="btn btn-primary">Set Reorder Point</button>
                    </form>
                </div>
            </div>

            <div id="preview-section">
                {'<div class="section-title">Preview</div><div class="title-line"></div>' + preview_html if preview_html else ''}
            </div>
            <div id="chart-section">
                {'<div class="section-title">Chart</div><div class="title-line"></div>' + chart_html if chart_html else ''}
            </div>
        </div>
    </body>
    </html>
    '''

# ✅ You still need this to run the server:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
