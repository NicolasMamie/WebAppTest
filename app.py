from flask import Flask, request
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

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
        date_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns
        if not numeric_cols.any():
            chart_html = "<p>No numeric columns to plot.</p>"
        else:
            date_col_in = date_cols[0]
            date_col_out = date_cols[1]
            
            
           
            col_in = numeric_cols[0]
            col_out = numeric_cols[1]

            df_in = df[[date_col_in, col_in]]
            df_in['Type'] = 'Purchase'
            df_in.rename(columns={'Time_in':'Time', 'In': 'Quantity'}, inplace=True)

            df_out = df[[date_col_out, col_out]]
            df_out['Type'] = 'Sale'
            df_out.rename(columns={'Time_out':'Time', 'Out':'Quantity'}, inplace=True)

            if df_out['Quantity'].sum() > 0:
                df_out['Quantity'] = df_out['Quantity']*(-1)

            df_combined = pd.concat([df_in, df_out])

           
            df_combined['Time'] = pd.to_datetime(df_combined['Time']).dt.date
            df_combined = df_combined.sort_values(by = 'Time' )
            df_combined.dropna(inplace=True)

            print(df_combined)
          
         
            fig = go.Figure()

            '''
           
            fig.add_trace(go.Bar(
                    x=df_combined['Time'],
                    y=df_combined['Quantity'],
                    name=col_in,
                    marker_color='green',
                    width=0.05
                ))
            '''
            df_combined['Time'] = pd.to_datetime(df_combined['Time'])
            # Purchases (green)
            df_purchases = df_combined[df_combined['Type'] == 'Purchase']
            fig.add_trace(go.Bar(
                x=df_purchases['Time'],
                y=df_purchases['Quantity'],
                name='Purchase',
                marker_color='green',
                width=0.5
            ))

            # Sales (red)
            df_sales = df_combined[df_combined['Type'] == 'Sale']
            fig.add_trace(go.Bar(
                x=df_sales['Time'],
                y=df_sales['Quantity'],
                name='Sale',
                marker_color='red',
                width=0.5
            ))
            
            fig.update_layout(
                title=f"Bar Chart of '{col_in}'",
                xaxis_title='Time',
                yaxis_title='QTY',
                #xaxis=dict(type='category'),  # Use 'category' if x_col is datetime and not continuous
                xaxis=dict(
                    type='date',
                    tickformat='%Y-%m-%d'
                )
                
            )
            chart_html = fig.to_html(full_html=True)


    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Excel Uploader</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
            table {{
                text-align: right;
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
