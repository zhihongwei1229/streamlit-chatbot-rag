from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import os

from promptflow.core import tool, Prompty
from rag_read import get_relevant_chunks


os.environ["OPENAI_API_VERSION"] = "2023-12-01-preview"
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")

def chatbot_response(query):
    path_to_prompty = f"prompty/sample.prompty"
    # load prompty as a flow
    rag_data_list, meta_info_list = get_relevant_chunks(query)
    rag_data = "\n".join(rag_data_list)
    meta_info = "\n".join(meta_info_list)

    if rag_data:
        rag_data = "Given the backgound information: \n" + rag_data
    else:
        rag_data = ""

    flow = Prompty.load(path_to_prompty)
    result = flow(rag_data=rag_data, query=query)
    
    result += "\n\n" + meta_info
    
    return result

if __name__ == "__main__":
    # query = "What is gemini?"
    query = "What is the meaning of the abbreviation HER2?"
    result = chatbot_response(query)
    print(result)