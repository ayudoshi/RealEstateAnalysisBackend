from django.shortcuts import render

# Create your views here.

import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os

# Excel file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'Sample_data.xlsx')

@api_view(['POST'])
def analyze_query(request):
    query = request.data.get('query', '').lower()

    try:
        df = pd.read_excel(DATA_PATH)
    except Exception as e:
        return Response({"error": f"Failed to read Excel file: {str(e)}"}, status=500)

    # Normalize columns (remove leading/trailing whitespaces)
    df.columns = df.columns.str.strip()

    if "analyze" in query:
        # Extract location name
        area = query.replace("analyze", "").strip().title()

        # Match against 'final location' column
        filtered_df = df[df['final location'].str.strip().str.title() == area]

        if filtered_df.empty:
            return Response({"summary": f"No data found for {area}"})

        # Mock Summary Example
        avg_price = filtered_df['flat - weighted average rate'].mean()
        total_sales = filtered_df['total_sales - igr'].sum()
        total_units = filtered_df['total units'].sum()
        summary = f"{area} has a total of {int(total_units)} units sold with ₹{avg_price:,.0f} as avg flat price and {int(total_sales)} in total IGR sales."

        # Chart: Year vs. avg flat rate
        chart_df = (
            filtered_df.groupby('year')['flat - weighted average rate']
            .mean()
            .reset_index()
            .rename(columns={'flat - weighted average rate': 'avg_flat_rate'})
        )

        # Prepare table data
        table_data = filtered_df.to_dict(orient='records')

        return Response({
            "summary": summary,
            "chartData": chart_df.to_dict(orient='records'),
            "tableData": table_data
        })

    return Response({"summary": "Sorry, I could not understand your query."})

