#working as of 05/12
import os
import openai
import pyodbc
from dotenv import load_dotenv
import pandas as pd
from tabulate import tabulate
import json
import re

def load_api_key():
    """Load the OpenAI API key from an environment variable."""
    load_dotenv(encoding="ISO-8859-1")  # Load environment variables from a .env file (optional)
    return os.getenv("OPENAI_API_KEY")  # Make sure the key is set in your environment

def get_schema_info():
    """Introspect SQL Server schema via INFORMATION_SCHEMA."""
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=;"
        "DATABASE=;"
        "Trusted_Connection=;"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Build a schema description string
    schema = {}
    for table, column, dtype in rows:
        schema.setdefault(table, []).append((column, dtype))
    lines = []
    for table, cols in schema.items():
        lines.append(f"Table: {table}:")
        for col, dtype in cols:
            lines.append(f"    [{col}] {dtype},")
    return "\n".join(lines)

def get_user_query():
    """Prompt the user or read from input."""
    return input("What do you want to query? E.g., 'Show me the total sales by region.'\n")

def generate_sql_query(natural_language_query, schema_info=""):
    """
    Send the user query (and schema info) to the OpenAI API
    and return the generated SQL query.
    """
    system_prompt = f"""
    You are an expert SQL assistant. Only write the SELECT queries for SQL Server.
    Given the database schema:
    {schema_info}

    Convert the following natural language request into a SQL query:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_language_query}
        ],
        max_tokens=150,
        temperature=0.0,
    )

    content: str = response.choices[0].message.content

    # 1️⃣  Prefer a fenced ```sql … ``` code block if one exists
    block = re.search(r"```(?:sql)?\s*(.*?)\s*```", content, re.I | re.S)
    if block:
        sql = block.group(1).strip()
    else:
        # 2️⃣  Fallback: grab everything from the first SELECT (or WITH) onward
        start = re.search(r"\b(SELECT|WITH)\b", content, re.I)
        sql = content[start.start():].strip() if start else None

    # 3️⃣  Final polish: ensure a trailing semicolon, collapse extra blank lines
    if sql:
        sql = sql.rstrip(";") + ";"
        sql = re.sub(r"\n{3,}", "\n\n", sql)

    return sql
    
def execute_query(sql_query):
    """Execute the generated SQL query on SQL Server."""
    try:
        conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=;"
            "DATABASE=;"
            "Trusted_Connection=;"
        )
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except Exception as e:
        print("Error executing query:", e)
        return pd.DataFrame()

    

def display_results(df, max_rows=20):
    """
    Display up to `max_rows` of the DataFrame in a table for speed.
    """
    if df is None or df.empty:
        print("No results to display.")
        return

    total = len(df)
    subset = df.head(max_rows)
    
    print("\nQuery Results:")
    print(tabulate(subset, headers=subset.columns, tablefmt="grid", showindex=False))

    if total > max_rows:
        print(f"\nShowing first {max_rows} of {total} rows. "
              "Refine your query to see more results.")

import json
import openai
import matplotlib.pyplot as plt

def auto_visualize(df, max_charts=1):
    """
    1) Summarize schema & sample
    2) Ask the LLM to write Python plotting code
    3) Extract & exec that code to render the chart(s)
    """
    if df is None or df.empty:
        print("No data to visualize.")
        return

    # 1. Build prompt
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    sample = df.head(5).to_dict(orient="list")
    system_prompt = f"""
You are a data visualization expert. Given a pandas DataFrame `df` with schema:
{json.dumps(schema, indent=2)}

And these first 5 rows:
{json.dumps(sample, indent=2)}

Generate up to {max_charts} Python code snippets (using matplotlib or pandas) 
that plot the most insightful charts ,graphs etc. Return ONLY the Python code blocks, wrapped in 
triple backticks (```), with no extra commentary.
"""

    # 2. Ask the model
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt}],
        temperature=0.0,
        max_tokens=300
    )
    content = resp.choices[0].message["content"]

    # 3. Extract code between ``` blocks
    import re
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", content, flags=re.S)
    if not code_blocks:
        print("LLM did not return any code. Skipping auto‑visualization.")
        return

    # 4. Execute each snippet in a safe namespace
    ns = {"df": df, "plt": plt, "pd": __import__("pandas")}
    for i, snippet in enumerate(code_blocks[:max_charts], start=1):
        print(f"\nExecuting chart #{i}:\n")
        try:
            exec(snippet, ns)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Failed to execute snippet #{i}: {e}")


def main():
    # 1. Load API key
    openai_api_key = load_api_key()
    if not openai_api_key:
        print("Error: OpenAI API key not found.")
        return
    openai.api_key = openai_api_key

    # 2. Fetch and format schema automatically
    print("Fetching database schema...")
    schema_info = get_schema_info()

    # 3. Get user input
    user_query = get_user_query()

    # 4. Generate and execute SQL
    print("Generating SQL from natural language...")
    sql_query = generate_sql_query(user_query, schema_info)
    print(f"Generated SQL query:\n{sql_query}\n")

    print("Executing query...")
    result_df = execute_query(sql_query)

    # 5. Display results
    display_results(result_df)

    # 6. Visualize
    auto_visualize(result_df)

if __name__ == "__main__":
    main()

