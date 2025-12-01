from nlp.model_trainer import train_model
from data import load_data  # agar faylni import qilish kerak bo'lsa

if __name__ == "__main__":
    data = load_data('data/knowledge_base.json')
    train_model(data)
