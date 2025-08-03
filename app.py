from flask import Flask, request, send_from_directory
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

def plot_data(df_pivot, initial_stock):

                    # Create the figure
                    fig = go.Figure()

                    # Add Purchase bars
                    fig.add_trace(go.Bar(
                        x=df_pivot['Time'],
                        y=df_pivot.get('Purchase', [0]*len(df_pivot)),
                        name='Purchase',
                        marker_color='green'
                    ))

                    # Add Sale bars
                    fig.add_trace(go.Bar(
                        x=df_pivot['Time'],
                        y=df_pivot.get('Sale', [0]*len(df_pivot)),
                        name='Sale',
                        marker_color='red'
                    ))

                    # Update layout
                    fig.update_layout(
                        title=f"Bar Chart",
                        xaxis_title='Time',
                        yaxis_title='QTY',
                        barmode='group',  # 'group' for side-by-side bars, 'stack' to stack them
                        xaxis=dict(type='category')  # Optional: you can remove this if 'Time' is datetime
                    )
                
                    print("reorder point ", reorder_point)
                    if initial_stock:
                        print("reorder point detected")
                        fig.add_hline(y=initial_stock, line_dash="dot", line_color="blue", annotation_text="Initial Stock",name="initial_stock")

                    return fig

fig = go.Figure()
reorder_point = None

app = Flask(__name__)

@app.route('/images/<path:filename>')
def serve_image(filename):
   return send_from_directory('images', filename)

@app.route('/', methods=['GET', 'POST'])


def index():
    global fig, reorder_point
    preview_html = ''
    chart_html = ''


    if request.method == 'POST':

        #file = request.files['file']
        file = request.files.get('file')
        initial_stock = request.form.get('initial_stock', type=float)  # <-- this line
       
        if file:

            df = pd.read_excel(file)

            
            # Table preview
            preview_html = df.head().to_html(classes='table table-striped', index=False)

            # Plot first numeric column
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
                df_in.rename(columns={'Time_in':'Time', 'In': 'Quantity'}, inplace=True)

                df_out = df[[date_col_out, col_out]].copy()
                df_out['Type'] = 'Sale'
                df_out.rename(columns={'Time_out':'Time', 'Out':'Quantity'}, inplace=True)

                if df_out['Quantity'].sum() > 0:
                    df_out['Quantity'] = df_out['Quantity']*(-1)

                df_combined = pd.concat([df_in, df_out])

            
                df_combined['Time'] = pd.to_datetime(df_combined['Time']).dt.date
                df_combined = df_combined.sort_values(by = 'Time' )
                df_combined.dropna(inplace=True)


                #df_combined['Time'] = pd.to_datetime(df_combined['Time'])
                # Purchases (green)
                #df_purchases = df_combined[df_combined['Type'] == 'Purchase']
                df_pivot = df_combined.pivot_table(
                    index='Time',
                    columns='Type',
                    values='Quantity',
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()

                # Sort by time
                df_pivot = df_pivot.sort_values('Time')

                fig = plot_data(df_pivot = df_pivot, initial_stock = initial_stock)

            if initial_stock:
                    
                    # Clean up previous Reorder Point lines/shapes if any
                # Remove existing reorder_point line if it exists
                if 'shapes' in fig.layout:
                    fig.layout.shapes = tuple(
                        shape for shape in fig.layout.shapes
                        if getattr(shape, 'name', None) != 'initial_stock'
                    )

                if 'annotations' in fig.layout:
                    fig.layout.annotations = tuple(
                        ann for ann in fig.layout.annotations
                        if getattr(ann, 'text', None) != 'Initial Stock'
                    )
                    
                fig.add_hline(y=initial_stock, line_dash="dot", line_color="blue", annotation_text="Initial Stock",name="initial_stock")
                    
        chart_html = fig.to_html()


    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Excel Uploader</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

        <script src="/static/main.js"></script>
        
        



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
            table {{
                text-align: right;
            }}
        </style>
    </head>

    <body class="bg-light py-5">
        <div class="container" style="max-width: 800px;">
            <h1 class="mb-4">Welcome to Soltar Reorder Point Optimizer</h1>

            {'<div class="section-title">Upload Purchase Orders and Consumption</div><div class="title-line"></div>'}
            
            <div class="mb-4">
                <p>
                    Please upload your Excel file containing both <strong>Purchase Orders</strong> and <strong>Consumption Data</strong> in the following format. 
                   
                </p>
                <img src="/images/excel_image.PNG"  class="img-fluid rounded shadow-sm" style="max-width: 70%; height: auto;">
            </div>

            <div class="row">
                <div class="col-md-6">
                    <form id = "upload-form" method="POST" enctype="multipart/form-data" class="card p-4 shadow-sm mb-4">
                        <input type="file" name="file" class="form-control mb-3" required>
                        <button type="submit" class="btn btn-primary">Upload</button>
                    </form>
                </div>
                <div class="col-md-6">
                    <form id = "initial-form" method="POST" class="card p-4 shadow-sm mb-4">
                        <label for="initial_stock" class="form-label">Enter Initial Stock</label>
                        <input type="number" name="initial_stock" class="form-control mb-3" placeholder="e.g., 150" required>
                        <button type="submit" class="btn btn-primary">Set Initial Stock</button>
                    </form>
                </div>
            </div>
            {'<div class="section-title">Preview</div><div class="title-line"></div>' + preview_html if preview_html else ''}
            {'<div class="section-title">Chart</div><div class="title-line"></div>' + chart_html if chart_html else ''}

        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
