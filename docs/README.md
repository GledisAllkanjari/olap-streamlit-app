# BedBath\&Beyond OLAP Assistant

## What This App Does

This is an AI-powered Business Intelligence web application that allows

business users to analyze the BedBath\&Beyond product catalog using natural

language questions. The app uses OLAP (Online Analytical Processing) techniques

to answer questions about pricing, availability, categories, and brands.

## Dataset

* Source: BedBath\&Beyond product catalog (scraped and cleaned)
* Records: 845,753 products
* Fields: BRAND, CATEGORY, AVAILABILITY, REG\_PRICE, SALE\_PRICE, LANG, VARIANT\_NAME

## How to Install

1. Make sure Python 3.10 or higher is installed
2. Open PowerShell in the project folder
3. Install required packages:

   pip install -r requirements.txt

   ## How to Configure the API Key

1. Go to console.anthropic.com and create an API key
2. Open the .streamlit/secrets.toml file
3. Add your key:

   ANTHROPIC\_API\_KEY = "sk-ant-api03-C9n8lncGN\_qygqLH7ixL3tGnp7oAeEmgXp4JiG-ByJjECX61a9sMZYNcFyzg71yLj84pVGUeURWH6FvYJhKKbQ-yR7W6QAA"

   ## How to Run

   streamlit run app.py

   Then open your browser at: http://localhost:8501

   ## OLAP Operations Supported

* SLICE: Filter on one dimension (e.g. "Show only products on sale")
* DICE: Filter on multiple dimensions (e.g. "Show out of stock Bath products")
* GROUP: Summarize by category (e.g. "Count products per category")
* DRILL-DOWN: Navigate hierarchy (e.g. "Break down largest category by subcategory")
* COMPARE: Side by side analysis (e.g. "Compare top 10 brands by average price")

  ## Technical Stack

* Frontend: Streamlit
* Data Processing: Pandas
* AI Integration: Anthropic Claude API
* Visualization: Plotly
