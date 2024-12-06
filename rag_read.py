# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import TypedDict
import os
import json
from urllib.parse import quote
# set environment variables before importing any other code
from dotenv import load_dotenv
load_dotenv()

from promptflow.tracing import trace
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from azure_vector_store import get_chunk_info_by_file_name, get_embedding_vector_from_content, get_chunk_info_by_query

class ChatResponse(TypedDict):
    context: dict
    reply: str

THERSHOLD = 0.6
AZURE_AI_SEARCH_VERSION = '2023-07-01-preview'



def get_file_path(search_query: str, num_docs=3) -> dict:
    return_data = {}
    index_name = os.environ["AZUREAI_SEARCH_INDEX_NAME"]

    #  retrieve documents relevant to the user's question from Cognitive Search
    search_client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
        index_name=index_name)

    embedding_to_query = get_embedding_vector_from_content(search_query)

    context = ""
    # use the vector embedding to do a vector search on the index
    vector_query = VectorizedQuery(vector=embedding_to_query, k_nearest_neighbors=num_docs, fields="contentVector")
    results = trace(search_client.search)(
        search_text="",
        vector_queries=[vector_query],
        # select=["filepath"]
        )
    
    for result in results:
        if result['@search.score'] >= THERSHOLD:
            return_data['score'] = result['@search.score']
            return_data['title'] = result['title']
            return_data['filepath'] = result['document_name']
            # return_data['content'] = result['content']
        break
    
    return return_data

def get_query_relevant_chunk(query):
    select_field = "id, content, document_name, meta_json_string"
    json_data = get_chunk_info_by_query(query, select_field)
    chunks = {}
    for item in json_data['value']:
        print(item['id'])


def get_document_content(document_name: str, ai_search_version=AZURE_AI_SEARCH_VERSION):
    select_field = "id, document_name, content, meta_json_string"
    json_data = get_chunk_info_by_file_name([document_name], ai_search_version, select_field)
    chunks = {}
    for item in json_data['value']:
        if 'meta_json_string' in item and item['meta_json_string']:
            json_data = json.loads(item['meta_json_string'])
            if 'source' in json_data and 'chunk_id' in json_data['source']:
                id = json_data['source']['chunk_id']
                chunks[id] = item['content']
    
    ordered_chunks_id = list(chunks.keys())
    ordered_chunks_id.sort()
    document_content = ""
    count = 0
    for chunk_id in ordered_chunks_id:
        document_content += chunks[chunk_id]
        count += 1
        if count >= 5:
            break
    return document_content


def find_relevant_document(query: str):
    document_content = ""
    relevant_chunks = get_file_path(query, 1)
    if relevant_chunks:
        document_name = relevant_chunks['filepath']
        document_content = get_document_content(document_name)
    
    return document_content


def process_meta_data(content: str, json_string: str) -> str:
    meta_json = json.loads(json_string)
    meta_info = "\n --- \n"
    if meta_json['file_name']:
        if 'file_link' in meta_json and meta_json['file_link']:
            url = str(meta_json['file_link'])
            url = quote(url, safe=':/')
            # meta_info += "Reference: " + meta_json['file_name']
            meta_info += "Reference: [%s](%s)" % (meta_json['file_name'], url)
        else:
            meta_info += "Reference: " + meta_json['file_name']
    if meta_json['page'] is not None:
        meta_info += "\n\nPage: " +  str(meta_json['page'])
    # meta_info += "\ncontent: \n" + content
    return meta_info
    
    


def get_relevant_chunks(query: str, num_docs=3):
    return_data = []
    meta_info_list = []
    select_fields = "id, document_name, content, meta_json_string"
    results = get_chunk_info_by_query(query, select_fields)
    for result in results['value']:
        if result['@search.score'] >= THERSHOLD:
            return_data.append(result['content'])
            if result['meta_json_string']:
                meta_info = process_meta_data(result['content'], result['meta_json_string'])
                meta_info += " Score: {%s}" % str(result['@search.score'])
                meta_info_list.append(meta_info)
            else:
                meta_info_list.append("")
    
    if return_data:
        return return_data, meta_info_list
    else:
        return [], []




    # return_data = []
    # meta_info_list = []
    # index_name = os.environ["AZUREAI_SEARCH_INDEX_NAME"]
    # search_client = SearchClient(
    #     endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    #     credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
    #     index_name=index_name)
    # embedding_to_query = get_embedding_vector_from_content(query)
    # vector_query = VectorizedQuery(vector=embedding_to_query, k_nearest_neighbors=num_docs, fields="contentVector")
    # results = trace(search_client.search)(
    #     # search_text="tmp_george",
    #     # search_text="",
    #     # filter="document_name eq 'tmp_" + user_name + "'",
    #     vector_queries=[vector_query],
    #     # select=["id", "content", "@search.score"]
    #     )
    
    # # for result in results:
    # #     if result['@search.score'] >= THERSHOLD:
    # #         return_data.append(result['content'])
    # #         if result['meta_json_string']:
    # #             meta_info = process_meta_data(result['content'], result['meta_json_string'])
    # #             meta_info += " Score: {%s}" % str(result['@search.score'])
    # #             meta_info_list.append(meta_info)
    # #             # meta_info_list.append(result['meta_json_string'])
    # #         else:
    # #             meta_info_list.append("")
            
    
    # if return_data:
    #     return return_data, meta_info_list
    # else:
    #     return [], []

    

if __name__ == "__main__":
    # query = "Could you tell me the price about SkyView 2-Person Tent"
    # result = get_file_path(query)
    # if result:
    #     document_name = result['filepath']
    #     document_content = get_document_content(document_name)
    #     print(document_content)

    # query = "please give me some information about gemini."
    # query = """2023, with the 70B releasing on the January 29, 2024.
    # Starting with the foundation models from Llama 2, Meta AI would 
    # train an additional 500B tokens of code datasets,"""
    # query = """
    # What is the meaning of the abbreviation HER2?
    # """
    query = """
    what is risk based quality management in clinical trials
    """
    contents, meta_infos = get_relevant_chunks(query)
    for meta_info in meta_infos:
        print(meta_info)
        print("---------")
    # get_query_relevant_chunk(query)
    # contents, meta_infos = get_relevant_chunks(query)
    # print(contents)
    # print(meta_infos)
    # for meta_info in meta_infos:
    #     print(meta_info)
    #     print("---------")

