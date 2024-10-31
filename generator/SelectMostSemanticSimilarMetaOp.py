
# TODO 先读取元操作md的每一个元操作
# 嵌入，存储向量

# 将每一个检查逻辑跟这里的元操作比较相似度，如果大于0.9，则提取元操作实现
# 如果没匹配到，去嵌入、检索API，如果大于0.8，提取API实现
import json

from transformers import AutoTokenizer, AutoModel
import torch

from generator.SelectMostSemanticSimilarAPI import get_most_similar_api


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
tokenizer = AutoTokenizer.from_pretrained('xx/bge-large-en-v1.5')
model = AutoModel.from_pretrained('xx/bge-large-en-v1.5')
model.eval()

def embeddingsentences():
    database.clear()
    # Sentences we want sentence embeddings for
    sentences = get_data("../base/Meta_Op_DB.json")

    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)
        # Perform pooling. In this case, cls pooling.
        sentence_embeddings = model_output[0][:, 0]
    # normalize embeddings
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)


    # Populate database with sentence embeddings and corresponding sentences
    for sent, emb in zip(sentences, sentence_embeddings):
        database.append({'sentence': sent, 'embedding': emb})

def findopimpl(op_name: str):
    with open("../base/Meta_Op_DB.json", 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 遍历所有类
    for op_info in data:
        # 检查当前类是否是目标类
        if str(op_info["meta_op"]) == op_name:
            return str(op_info["meta_impl"])

def get_most_similar_meta_operation(query: str):
    # 特定句子
    query_sentence = query
    # Tokenize query sentence
    encoded_query = tokenizer(query_sentence, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings for the query sentence
    with torch.no_grad():
        query_model_output = model(**encoded_query)
        # Perform pooling. In this case, cls pooling.
        query_embedding = query_model_output[0][:, 0]
    # Normalize query embedding
    query_embedding = torch.nn.functional.normalize(query_embedding, p=2, dim=1)
    cosine_similarities = torch.nn.functional.cosine_similarity(query_embedding, torch.stack([entry['embedding'] for entry in database]), dim=1)

    # 找到最相似的句子索引
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
    # 找到了代码段
    if len(impl) >= 1:
        return impl
    else:
        impl = get_most_similar_api(query, nodes)
        # 找到了API
        if len(impl) >= 1:
            return impl
    return []