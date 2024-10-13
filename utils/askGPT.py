import os
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
import ast
import pandas as pd

from langsmith import Client

#############move to config!!!!!!!!!!!!!!!!!!!!!
load_dotenv()
client = Client()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
db = SQLDatabase.from_uri("sqlite:///parcel.db")
#############move to config!!!!!!!!!!!!!!!!!!!!!
write_query = create_sql_query_chain(llm, db)
execute_query = QuerySQLDataBaseTool(db=db)

def list_of_tuples_to_df(data, columns = ["bill_index", "bill_date", "receiver_tambon", "receiver_amphur", "receiver_province", "receiver_zipcode", "item_code", "item_name", "qty", "unit_name", "reg_code", "dest_code"]):
    return pd.DataFrame(data, columns=columns)

def rank_columns_by_occurrence(df, key_col="unit_name"):
    df = list_of_tuples_to_df(df)
    df = df.drop(columns=["unit_name", "bill_index", "reg_code", "item_code"])
    ranked_occurrences = {}
    
    qtySum = 0
    for col in df.columns:
        if(col == "qty"): 
            qtySum+=df[col].sum()
            continue
        value_counts = df[col].fillna('null').value_counts(dropna=False)
        sorted_counts = value_counts.sort_values(ascending=False)
        ranked_occurrences[col+"(ครั้ง)"] = sorted_counts

        if(col == "item_name"):
            summed_qty = df.groupby("item_name")["qty"].sum().reset_index()
            ranked_occurrences["item_name(หน่วย)"] = summed_qty.sort_values(ascending=False, by="qty")
        
    ranked_occurrences["จำนวนทั้งสิ้น(หน่วย)"] = int(qtySum)
    ranked_occurrences["จำนวนทั้งสิ้น(ครั้ง)"] = df[df.columns[0]].count()
    return ranked_occurrences

def query(query):
    """Execute query
    use table name parcel_list, here are the column name that might be useful BILL_INDEX,BILL_DATE,receiver_TAMBON,receiver_AMPHUR,receiver_PROVINCE,receiver_ZIPCODE,ITEM_CODE,ITEM_NAME,QTY,UNIT_NAME, the date format is YYYYMMDD
    you might want to sum QTY
    """
    print("DEBUG:", query)
    res = execute_query.invoke(input = query)
    print("DEBUG:", res[0:1000])
    print(type(res))
    return res

def query_and_summarize(query):
    try:
        """Takes in question, make query and summarize"""
        print("DEBUG:", query)
        res = execute_query.invoke(input = query)
        print("DEBUG:", res[0:1000])
        try:
            res = ast.literal_eval(res)
        except Exception:
            print(execute_query.invoke(input = query))
            print("AST error")
        if(len(res)==0): return "nothing in the result"
        return rank_columns_by_occurrence(res)
    except Exception as error:
        return f"error querying, {error}"


tools = [
    
    Tool(
        name="Query",
        func=query,
        description='''
        NEVER use SELECT * from with this tools. Useful when you need to query something in database, 
        the date format is YYYYMMDD, use WHERE ITEM_NAME LIKE rather than WHERE ITEM_NAME
        think carefully whether user asks for occurence or sum of quantity'''
    ),
    Tool(
        name="Query and summarize",
        func=query_and_summarize,
        description='''Useful when you need to query something in database and summarize it consecutively, use table name parcel_list, 
        here are the column name that might be useful 
        BILL_INDEX,BILL_DATE,receiver_TAMBON,receiver_AMPHUR,receiver_PROVINCE,receiver_ZIPCODE,ITEM_CODE,ITEM_NAME,QTY,UNIT_NAME, 
        the date format is YYYYMMDD, use WHERE ITEM_NAME LIKE rather than WHERE ITEM_NAME, 
        Query with SELECT * and don't use sum. do rank each property from occurence. also sumup occurence'''
    )
]

prompt = hub.pull("hwchase17/react")
prompt.template = """
Answer the question related to parcel shipping and querying. If they ask anything not related just answer you can't.
You have access to the following tools:

{tools}

if you just want to count or sum, please use Query.
if you want to query SELECT * please use Query and summarize.

when you summarize, if any item is null you must skip it.
item_name(หน่วย) is more priority than item_name(ครั้ง) but if you are going to report any you have to report both.
after you do the summary, you don't repeat anymore.
you only provide extra information when the summary is too short.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat 1 times, ideally don't repeat)
Thought: I now got the final answer
Final Answer: the summary must answer the input question and providing more insight


please answer in Thai and act like you're an assistant eager to help.
use a lot of related emojis. this year is 2024.

Begin!


Question: {input}
Thought:{agent_scratchpad}
"""

# Create the ReAct agent using the create_react_agent function
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    stop_sequence=True,
)

# Create an agent executor from the agent and tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True, 
    handle_parsing_errors=True
)

# Run the agent with a test query
def askGPT(question: str):
    response = agent_executor.invoke({"input": question})
    return response

if __name__ == "__main__":
    response = agent_executor.invoke({"input": "สรุปของที่ส่งจากเชียงใหม่ให้หน่อย"})
    print("response:", response)