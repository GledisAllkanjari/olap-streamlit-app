# app.py
# Main Streamlit OLAP Assistant Application

import streamlit as st
import time
import plotly.express as px
from data_utils import load_data, execute_olap_code, get_dataset_summary

try:
    from prompts import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = ""

# --- PAGE CONFIG ---
st.set_page_config(
    page_title='BedBath&Beyond OLAP Assistant',
    page_icon='🛁',
    layout='wide'
)

# --- TITLE ---
st.title('🛁 BedBath&Beyond OLAP Assistant')
st.caption('Ask questions about product pricing, availability, and categories')

# --- LOAD DATA ---
df = load_data()

# --- SIDEBAR: Dataset Overview ---
with st.sidebar:
    st.header('Dataset Overview')
    stats = get_dataset_summary(df)
    st.metric('Total Products', f"{stats['total_products']:,}")
    st.metric('Brands', stats['brands'])
    st.metric('Categories', stats['categories'])
    st.metric('In Stock', f"{stats['in_stock']:,}")
    st.metric('On Sale', f"{stats['on_sale']:,}")
    st.metric('Avg Price', f"${stats['avg_price']}")
    st.divider()
    st.subheader('Try These Questions')
    examples = [
        'How many products per top-level category?',
        'Which brand has the highest average price?',
        'Show out-of-stock products in Bath category',
        'Drill down into the largest category',
        'Compare in-stock vs out-of-stock count by category'
    ]
    for ex in examples:
        st.caption(f'• {ex}')

# --- CHAT HISTORY ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.write(msg['content'])
        if 'dataframe' in msg:
            st.dataframe(msg['dataframe'], use_container_width=True)
        if 'chart' in msg:
            st.plotly_chart(msg['chart'], use_container_width=True)

# --- CHAT INPUT ---
user_question = st.chat_input('Ask an OLAP question about the product data...')

if user_question:
    # Show user message
    with st.chat_message('user'):
        st.write(user_question)
    st.session_state.messages.append({'role': 'user', 'content': user_question})

    with st.chat_message('assistant'):
        with st.spinner('Analyzing...'):
            time.sleep(1.5)  # simulate thinking

            # --- MOCK RESPONSES based on keyword detection ---
            q = user_question.lower()

            if any(w in q for w in ['out of stock', 'outofstock', 'unavailable', 'not available']):
                mock = {
                    "operation": "slice",
                    "explanation": "Filtering products where availability is 'OUT OF STOCK'.",
                    "code": "result = df[df['AVAILABILITY'] == 'OUT OF STOCK'][['VARIANT_NAME','BRAND','CATEGORY','REG_PRICE']].head(15)",
                    "chart_type": "none"
                }
            elif any(w in q for w in ['in stock', 'available']) and any(w in q for w in ['bath', 'bed', 'kitchen', 'category']):
                mock = {
                    "operation": "dice",
                    "explanation": "Filtering on both availability and category simultaneously.",
                    "code": "result = df[(df['AVAILABILITY'] == 'IN STOCK') & (df['CATEGORY'].str.contains('Bath', case=False, na=False))][['VARIANT_NAME','BRAND','REG_PRICE']].head(15)",
                    "chart_type": "none"
                }
            elif any(w in q for w in ['drill', 'subcategory', 'sub-category', 'break down', 'breakdown', 'hierarchy']):
                mock = {
                    "operation": "drilldown",
                    "explanation": "Drilling down into category hierarchy to show subcategory counts.",
                    "code": """df['level1'] = df['CATEGORY'].str.split('>').str[0].str.strip()
df['level2'] = df['CATEGORY'].str.split('>').str[1].str.strip()
result = df.groupby(['level1','level2']).size().reset_index(name='Count').sort_values('Count', ascending=False).head(15)""",
                    "chart_type": "bar"
                }
            elif any(w in q for w in ['compare', 'vs', 'versus', 'side by side', 'comparison']):
                mock = {
                    "operation": "compare",
                    "explanation": "Comparing top brands by product count, average price, and items on sale.",
                    "code": """result = df.groupby('BRAND').agg(
    Count=('VARIANT_NAME','count'),
    Avg_Price=('REG_PRICE','mean'),
    On_Sale=('SALE_PRICE', lambda x: x.notna().sum())
).reset_index().sort_values('Count', ascending=False).head(10)
result['Avg_Price'] = result['Avg_Price'].round(2)
result.columns = ['Brand', 'Count', 'Avg Price', 'On Sale']""",
                    "chart_type": "bar"
                }
            elif any(w in q for w in ['highest', 'most expensive', 'top price', 'highest price', 'highest average']):
                mock = {
                    "operation": "group",
                    "explanation": "Finding brands with the highest average regular price.",
                    "code": """result = df.groupby('BRAND')['REG_PRICE'].mean().reset_index()
result.columns = ['Brand', 'Average Price']
result['Average Price'] = result['Average Price'].round(2)
result = result.sort_values('Average Price', ascending=False).head(10)""",
                    "chart_type": "bar"
                }
            elif any(w in q for w in ['sale', 'discount', 'on sale', 'discounted']):
                mock = {
                    "operation": "slice",
                    "explanation": "Filtering products that are currently on sale (have a sale price).",
                    "code": """result = df[df['SALE_PRICE'].notna()][['VARIANT_NAME','BRAND','REG_PRICE','SALE_PRICE']].head(15)
result['REG_PRICE'] = result['REG_PRICE'].round(2)
result['SALE_PRICE'] = result['SALE_PRICE'].round(2)
result.columns = ['Product', 'Brand', 'Regular Price', 'Sale Price']""",
                    "chart_type": "none"
                }
            elif any(w in q for w in ['stock', 'in-stock', 'availability']):
                mock = {
                    "operation": "compare",
                    "explanation": "Comparing in-stock vs out-of-stock product counts by top-level category.",
                    "code": """df['level1'] = df['CATEGORY'].str.split('>').str[0].str.strip()
result = df.groupby(['level1','AVAILABILITY']).size().reset_index(name='Count').sort_values('Count', ascending=False).head(15)
result.columns = ['Category', 'Availability', 'Count']""",
                    "chart_type": "bar"
                }
            else:
                # default: group by top-level category
                mock = {
                    "operation": "group",
                    "explanation": "Grouping products by top-level category and counting each.",
                    "code": """df['level1'] = df['CATEGORY'].str.split('>').str[0].str.strip()
result = df.groupby('level1').size().reset_index(name='Count').sort_values('Count', ascending=False).head(15)
result.columns = ['Category', 'Count']""",
                    "chart_type": "bar"
                }

            operation = mock['operation']
            explanation = mock['explanation']
            code = mock['code']
            chart_type = mock['chart_type']

            # Show operation badge and explanation
            st.badge(f'OLAP: {operation.upper()}')
            st.write(explanation)

            # Execute the generated pandas code
            result_df, error = execute_olap_code(df, code)

            if error:
                st.error(f'Analysis error: {error}')
                st.code(code, language='python')
            else:
                st.dataframe(result_df, use_container_width=True)

                # Generate chart if requested
                fig = None
                if chart_type == 'bar' and len(result_df.columns) >= 2:
                    fig = px.bar(result_df, x=result_df.columns[0], y=result_df.columns[1])
                elif chart_type == 'pie' and len(result_df.columns) >= 2:
                    fig = px.pie(result_df, names=result_df.columns[0], values=result_df.columns[1])
                elif chart_type == 'line' and len(result_df.columns) >= 2:
                    fig = px.line(result_df, x=result_df.columns[0], y=result_df.columns[1])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                # Save to history
                msg = {
                    'role': 'assistant',
                    'content': f'[{operation.upper()}] {explanation}',
                    'dataframe': result_df
                }
                if fig:
                    msg['chart'] = fig
                st.session_state.messages.append(msg)