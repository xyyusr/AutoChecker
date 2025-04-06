
import json
from transformers import AutoTokenizer, AutoModel
import torch
from tool.generator.SelectMostSemanticSimilarAPI import get_most_similar_api

def get_data(file_path: str):
    sentences = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for op_info in data:
        op_name = str(op_info["meta_op"])
        sentences.append(op_name)
    return sentences

# Database to store embeddings and corresponding sentences
database = []
# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('../bge-large-en-v1.5')
model = AutoModel.from_pretrained('../bge-large-en-v1.5')
model.eval()

def embeddingsentences():
    database.clear()
    sentences = get_data("../PMD_MetaAPI_DB.json")
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
        sentence_embeddings = model_output[0][:, 0]
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
    for sent, emb in zip(sentences, sentence_embeddings):
        database.append({'sentence': sent, 'embedding': emb})

def findopimpl(op_name: str):
    with open("../PMD_MetaAPI_DB.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    for op_info in data:
        if str(op_info["meta_op"]) == op_name:
            return str(op_info["meta_impl"])

def get_most_similar_meta_operation(query: str):
    query_sentence = query
    encoded_query = tokenizer(query_sentence, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        query_model_output = model(**encoded_query)
        query_embedding = query_model_output[0][:, 0]
    query_embedding = torch.nn.functional.normalize(query_embedding, p=2, dim=1)
    cosine_similarities = torch.nn.functional.cosine_similarity(query_embedding, torch.stack([entry['embedding'] for entry in database]), dim=1)
    most_similar_index = torch.argmax(cosine_similarities).item()
    most_similar_sentence = database[most_similar_index]['sentence']
    impl = []
    code = findopimpl(most_similar_sentence)
    meta_data = {"op_name": most_similar_sentence, "op_impl": code}
    if float(cosine_similarities[most_similar_index].item()) > 0.85:
        print("logic:", query)
        print("most similar meta operation:", most_similar_sentence)
        print("cosine Similarity:", cosine_similarities[most_similar_index].item())
        impl.append(meta_data)
    return impl

def get_impl(query: str, nodes: list):
    impl = get_most_similar_meta_operation(query)
    if len(impl) >= 1:
        return impl
    else:
        impl = get_most_similar_api(query, nodes)
        if len(impl) >= 1:
            return impl
    return []