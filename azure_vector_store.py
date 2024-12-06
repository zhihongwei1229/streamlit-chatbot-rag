import requests
import os
from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()

TIME_STAMP_CHUNK_NAME = "update_check_point.md"
AZURE_API_KEY = os.getenv("AZURE_SEARCH_KEY")
DEFAULT_TIME_STAMP = "2022-01-01 00:00:00"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
# SEARCH_API_URL = "https://george-test-search-service.search.windows.net/indexes/product_index/docs/search"
# MODIFY_API_URL = "https://george-test-search-service.search.windows.net/indexes/product_index/docs/index"

SEARCH_API_URL = "https://george-test-search-service.search.windows.net/indexes/dsi_sharepoint_search_bdm_dev/docs/search"
MODIFY_API_URL = "https://george-test-search-service.search.windows.net/indexes/dsi_sharepoint_search_bdm_dev/docs/index"

def get_embedding_vector_from_content(content: str) -> list:
    aoai_client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"]
    )

    # generate a vector embedding of the user's question
    embedding = aoai_client.embeddings.create(input=content,
                                            model=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"])
    vector = embedding.data[0].embedding
    return vector
    
def get_chunk_info_by_file_name(file_names: list, ai_search_version: str, select_field = "id, document_name"):
    end_point = SEARCH_API_URL + "?api-version=" + ai_search_version
    filter_items = []
    for file_name in file_names:
        filter_items.append("document_name eq '" + file_name + "'")
    filter_conditions = " or ".join(filter_items)
    headers = {'content-type': 'application/json', 'api-key': AZURE_API_KEY}
    payload = {"filter": filter_conditions, "select": select_field}
    response = requests.post(end_point, json=payload, headers=headers)
    json_data = response.json()
    
    return json_data


def get_chunk_info_by_query(query: str, select_field = "id, document_name", num_doc=10):
    ai_search_version=os.environ["AZURE_OPENAI_API_VERSION"]
    end_point = SEARCH_API_URL + "?api-version=" + ai_search_version
    
    headers = {'content-type': 'application/json', 'api-key': AZURE_API_KEY}
    payload = {"search": query, 
               "queryType": "simple", 
            #    "searchMode": "all", 
               "searchFields": "content",
               "top": 10,
               "count": True,
               "select": select_field
               }
    response = requests.post(end_point, json=payload, headers=headers)
    json_data = response.json()
    
    return json_data
