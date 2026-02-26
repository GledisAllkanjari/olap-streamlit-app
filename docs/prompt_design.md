# Prompt Design Document

## Overview
This document explains the prompt engineering strategy used in the
BedBath&Beyond OLAP Assistant.

## System Prompt Strategy

The system prompt in prompts.py is designed to do three things:
1. Tell Claude exactly what columns exist in the dataset
2. Define each OLAP operation with a concrete pandas code example
3. Force Claude to return a structured JSON response every time

## Why JSON Output?
The app needs to parse Claude's response programmatically to:
- Display the correct operation label
- Execute the generated pandas code
- Choose the right chart type automatically

By forcing JSON output, the app can reliably extract the code and
explanation without any text parsing.

## OLAP Operation Definitions

### SLICE
Filters the dataframe on a single column condition.
Example prompt: "Show only products that are on sale"
Claude generates: result = df[df['SALE_PRICE'].notna()]

### DICE
Filters on multiple columns simultaneously using & operator.
Example prompt: "Show out of stock products in Bath category"
Claude generates: result = df[(df['AVAILABILITY']=='Out of Stock') &
(df['CATEGORY'].str.contains('Bath'))]

### GROUP & SUMMARIZE
Uses pandas groupby to aggregate numeric measures by dimension.
Example prompt: "How many products per category?"
Claude generates: result = df.groupby('CATEGORY').size().reset_index(name='Count')

### DRILL-DOWN
Parses the category breadcrumb field by splitting on the > separator
to navigate from top-level to subcategory level.
Example prompt: "Break down the largest category by subcategory"
Claude generates: df['level1'] = df['CATEGORY'].str.split('>').str[0].str.strip()

### COMPARE
Aggregates multiple measures side by side grouped by a dimension.
Example prompt: "Compare top 10 brands by average price"
Claude generates: result = df.groupby('BRAND')['REG_PRICE'].mean()
.reset_index().sort_values('REG_PRICE', ascending=False).head(10)

## Problems Found During Testing

### Problem 1: Wrong column names
The dataset uses uppercase column names (REG_PRICE, SALE_PRICE) but
the initial prompt used lowercase. Fixed by updating all column
references in the system prompt to match the actual dataset.

### Problem 2: JSON parsing failures
Sometimes Claude returned text with backticks around the JSON.
Fixed by adding explicit instructions: "Return ONLY the JSON object,
no markdown, no backticks."

### Problem 3: Result variable not created
Some generated code forgot to assign output to result variable.
Fixed by adding the rule prominently: "ALWAYS assign final output
to a variable named result."

## What I Would Improve With More Time
- Add few-shot examples directly in the system prompt
- Add a feedback button so users can rate each answer
- Store conversation history to allow follow-up questions
- Add more chart types like scatter plots and heatmaps