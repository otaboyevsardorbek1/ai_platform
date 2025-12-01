from transformers import BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

def train_model(train_dataset):
    model = BertForSequenceClassification.from_pretrained("bert-base-multilingual-cased", num_labels=3)
    
    training_args = TrainingArguments(
        output_dir='./results',
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )
    
    trainer.train()
    model.save_pretrained("./models/trained_model")
