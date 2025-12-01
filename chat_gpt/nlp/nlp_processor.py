from transformers import BertTokenizer

def tokenize_data(dataset):
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    return dataset.map(lambda examples: tokenizer(examples['question'], padding='max_length', truncation=True), batched=True)
