
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
    words.append(method_name[start_index:].lower())
    return words

def get_API(nodes: list):
    i = 0
    with open("../PMD_FullAPI_DB.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    separator = ' '
    apilist = {}

    for class_info in data["classes_contained_in_project_detail"]:
        class_name = str(class_info["class_name"])
        if class_name in nodes:
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

                if str(class_info["class_name"]).startswith("AST"):

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
    print(len(apilist))
    return apilist

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('../bge-large-en-v1.5')
model = AutoModel.from_pretrained('../bge-large-en-v1.5')
model.eval()

# Database to store embeddings and corresponding sentences
database = []

def embeddingapis(sentences : dict):
    encoded_input = tokenizer(list(sentences.keys()), padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
        sentence_embeddings = model_output[0][:, 0]
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
    for key, value, emb in zip(sentences.keys(), sentences.values(), sentence_embeddings):
        database.append({'sentence': key, 'node': value, 'embedding': emb})

def cleardata():
    database.clear()

def get_most_similar_api(query: str, nodes: list):
    query_sentence = query
    encoded_query = tokenizer(query_sentence, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        query_model_output = model(**encoded_query)
        query_embedding = query_model_output[0][:, 0]
    query_embedding = torch.nn.functional.normalize(query_embedding, p=2, dim=1)
    part = [entry for entry in database if entry['node'] in nodes]
    cosine_similarities = torch.nn.functional.cosine_similarity(query_embedding,
                                                                torch.stack([entry['embedding'] for entry in part]),
                                                                dim=1)
    most_similar_index = torch.argmax(cosine_similarities).item()
    most_similar_sentence = part[most_similar_index]['sentence']
    if float(cosine_similarities[most_similar_index].item()) > 0.8:
        with open("../PMD_FullAPI_DB.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        apis = []
        separator = ' '
        for class_info in data["classes_contained_in_project_detail"]:
            class_name = str(class_info["class_name"])
            if class_name in nodes:
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
                    if str(class_info["class_name"]).startswith("AST"):
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

