import fitz  # PyMuPDF
import re
from flask import Flask, request, jsonify
from fuzzywuzzy import process  # Fuzzy matching için gerekli

app = Flask(__name__)

# PDF dosyasından metni al
def pdf_to_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Soru-Cevapları çıkart
def extract_qna(text):
    pattern = r"Q:(.*?)A:(.*?)(?=Q:|$)"
    matches = re.findall(pattern, text, re.DOTALL)
    return {q.strip(): a.strip() for q, a in matches}

# PDF'den veriyi çekelim
pdf_text = pdf_to_text("airbnb-faq.pdf")
qna_dict = extract_qna(pdf_text)
questions_list = list(qna_dict.keys())  # Tüm soruları bir listeye çeviriyoruz

# En uygun soruyu bul ve cevapla
def find_best_match(user_question):
    best_match, score = process.extractOne(user_question, questions_list)
    if score > 70:  # %70 eşleşme oranı yakalarsa
        return qna_dict[best_match]
    return "Üzgünüm, bu soruya cevap bulamadım."

# API: Kullanıcıdan gelen soruya uygun cevabı döndür
@app.route("/get_answer", methods=["POST"])
def get_answer():
    user_question = request.json.get("question", "").strip()
    answer = find_best_match(user_question)
    print(f"User Question: {user_question}")
    print(f"Answer: {answer}")
    return jsonify({"answer": answer})


# Flask server başlatma
if __name__ == "__main__":
    app.run(port=5000, debug=True)
