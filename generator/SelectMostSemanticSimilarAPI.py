
import json
from transformers import AutoTokenizer, AutoModel
import torch

def split_camel_case(method_name: str):
    words = []
    start_index = 0

    for i in range(1, len(method_name)):
        if method_name[i].isupper():
            if i - start_index >= 2:
                words.append(method_name[start_index:i].lower())
                start_index = i
    # 添加最后一个单词
    words.append(method_name[start_index:].lower())

    return words

def get_API(nodes: list):
    i = 0
    with open("../base/ASTAndUtilAndEdgeClassAllAPInfoWithCommon.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    separator = ' '
    apilist = {}
    # 遍历所有类

    for class_info in data["classes_contained_in_project_detail"]:
        class_name = str(class_info["class_name"])
        if class_name in nodes:
            # 如果是节点类，去头去尾，工具类因为不使用类名所以不对类名进行操作
            if class_name.startswith("AST"):
                if class_name.endswith("Declaration"):
                    class_name = class_name[3:]
                    index = class_name.find("Declaration")
                    class_name = class_name[:index]
                else:
                    class_name = class_name[3:]
                class_name = separator.join(split_camel_case(class_name))

            for API_info in class_info["APIs_contained_in_class_detail"]:

                api_name = str(API_info["method_name"])
                api_sig = str(API_info["method_signature"])

                # 如果是节点类，方法全是实例方法
                if str(class_info["class_name"]).startswith("AST"):
                    # 返回值类型
                    returnType = str(api_sig.split(" ")[1])

                    if returnType == "boolean":
                        api_name = separator.join(split_camel_case(api_name))
                        api_comment = "Check whether the " + class_name + " " + api_name
                        apilist[api_comment] = str(class_info["class_name"])
                        i += 1
                    else:
                        api_name = separator.join(split_camel_case(api_name))
                        api_comment = api_name + " of " + class_name
                        apilist[api_comment] = str(class_info["class_name"])
                        i += 1
                    if API_info["method_comment"] is not None:
                        api_comment = api_comment + ": " + str(API_info["method_comment"])
                        apilist[api_comment] = str(class_info["class_name"])
                        i += 1
                else:
                    # 返回值类型
                    returnType = str(api_sig.split(" ")[2])
                    if returnType == "boolean":
                        api_name = separator.join(split_camel_case(api_name))
                        api_name = "Check whether " + api_name
                        apilist[api_name] = str(class_info["class_name"])
                        i += 1
                    else:
                        api_name = separator.join(split_camel_case(api_name))
                        apilist[api_name] = str(class_info["class_name"])
                        i += 1
                    if API_info["method_comment"] is not None:
                        api_comment = api_name + ": " + str(API_info["method_comment"])
                        apilist[api_comment] = str(class_info["class_name"])
                        i += 1

    print(i)
    print(len(apilist))  # 比i少，因为有一些重载方法会被去重
    return apilist

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('D:/JetBrains/pycharm/bge-large-en-v1.5')
model = AutoModel.from_pretrained('D:/JetBrains/pycharm/bge-large-en-v1.5')
# tokenizer = AutoTokenizer.from_pretrained('/pub/data/xieyy/bge-large-en-v1.5')
# model = AutoModel.from_pretrained('/pub/data/xieyy/bge-large-en-v1.5')
model.eval()

# Database to store embeddings and corresponding sentences
database = []

def embeddingapis(sentences : dict):

    # Tokenize sentences
    encoded_input = tokenizer(list(sentences.keys()), padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)
        # Perform pooling. In this case, cls pooling.
        sentence_embeddings = model_output[0][:, 0]
    # normalize embeddings
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

    for key, value, emb in zip(sentences.keys(), sentences.values(), sentence_embeddings):
        database.append({'sentence': key, 'node': value, 'embedding': emb})

def cleardata():
    database.clear()

def get_most_similar_api(query: str, nodes: list):
    # sentences = get_API(nodes)
    # embeddingapis(sentences)
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

    part = [entry for entry in database if entry['node'] in nodes]

    # Compute cosine similarity with the specific sentence
    cosine_similarities = torch.nn.functional.cosine_similarity(query_embedding,
                                                                torch.stack([entry['embedding'] for entry in part]),
                                                                dim=1)
    # 找到最相似的句子索引
    most_similar_index = torch.argmax(cosine_similarities).item()
    most_similar_sentence = part[most_similar_index]['sentence']

    if float(cosine_similarities[most_similar_index].item()) > 0.8:
        with open("../base/ASTAndUtilAndEdgeClassAllAPInfoWithCommon.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        apis = []
        separator = ' '
        # 遍历所有相关类
        for class_info in data["classes_contained_in_project_detail"]:
            class_name = str(class_info["class_name"])
            if class_name in nodes:
                # 如果是节点类，去头去尾，工具类因为不使用类名所以不对类名进行操作
                if class_name.startswith("AST"):
                    if class_name.endswith("Declaration"):
                        class_name = class_name[3:]
                        index = class_name.find("Declaration")
                        class_name = class_name[:index]
                    else:
                        class_name = class_name[3:]
                    class_name = separator.join(split_camel_case(class_name))

                for API_info in class_info["APIs_contained_in_class_detail"]:
                    api_name = str(API_info["method_name"])
                    api_sig = str(API_info["method_signature"])
                    # 如果是节点类，方法全是实例方法
                    if str(class_info["class_name"]).startswith("AST"):
                        # 返回值类型
                        returnType = str(api_sig.split(" ")[1])
                        if returnType == "boolean":
                            api_name = separator.join(split_camel_case(api_name))
                            api_comment = "Check whether the " + class_name + " " + api_name
                        else:
                            api_name = separator.join(split_camel_case(api_name))
                            api_comment = api_name + " of " + class_name
                        if api_comment == most_similar_sentence:
                            if API_info["method_comment"] is not None:
                                meta_data = {"op_name": most_similar_sentence, "op_impl": str(class_info["class_package"])+": "+api_sig+", //"+str(API_info["method_comment"])}
                            else:
                                meta_data = {"op_name": most_similar_sentence, "op_impl": str(class_info["class_package"])+": "+api_sig}

                            print("query: " + query)
                            print("most similar API: " + most_similar_sentence)
                            print("cosine Similarity:", cosine_similarities[most_similar_index].item())
                            apis.append(meta_data)
                            return apis
                        if API_info["method_comment"] is not None:
                            api_comment = api_comment + ": " + str(API_info["method_comment"])
                            if api_comment == most_similar_sentence:
                                meta_data = {"op_name": most_similar_sentence,
                                             "op_impl": str(class_info["class_package"]) + ": " + api_sig + ", //" + str(
                                                 API_info["method_comment"])}

                                print("query: " + query)
                                print("most similar API: " + most_similar_sentence)
                                print("cosine Similarity:", cosine_similarities[most_similar_index].item())
                                apis.append(meta_data)
                                return apis
                    else:
                        # 返回值类型
                        returnType = str(api_sig.split(" ")[2])
                        if returnType == "boolean":
                            api_name = separator.join(split_camel_case(api_name))
                            api_comment = "Check whether " + api_name
                        else:
                            api_comment = separator.join(split_camel_case(api_name))
                        if api_comment == most_similar_sentence:
                            if API_info["method_comment"] is not None:
                                meta_data = {"op_name": most_similar_sentence,
                                             "op_impl": str(class_info["class_package"]) + ": " + api_sig + ", //" + str(
                                                 API_info["method_comment"])}
                            else:
                                meta_data = {"op_name": most_similar_sentence,
                                             "op_impl": str(class_info["class_package"]) + ": " + api_sig}

                            print("query: " + query)
                            print("most similar API: " + most_similar_sentence)
                            print("cosine Similarity:", cosine_similarities[most_similar_index].item())
                            apis.append(meta_data)
                            return apis
                        if API_info["method_comment"] is not None:
                            api_comment = api_comment + ": " + str(API_info["method_comment"])
                            if api_comment == most_similar_sentence:
                                meta_data = {"op_name": most_similar_sentence,
                                             "op_impl": str(class_info["class_package"]) + ": " + api_sig + ", //" + str(
                                                 API_info["method_comment"])}

                                print("query: " + query)
                                print("most similar API: " + most_similar_sentence)
                                print("cosine Similarity:", cosine_similarities[most_similar_index].item())
                                apis.append(meta_data)
                                return apis

    return []

