# -*- coding: utf-8 -*-
"""04_predict.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wGQywVFoWX_EMQaKOLCffQwD-igN69lh
"""

import pandas as pd
import re
from collections import Counter
from transformers import BertTokenizer, TFBertModel
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import scipy
import os

# Fungsi ringkas putusan
def ringkas_putusan(amar: str) -> str:
    """Meringkas putusan pengadilan menjadi poin-poin kunci"""
    if not isinstance(amar, str) or amar.strip() == "":
        return ""

    amar_lower = amar.lower()
    penjara = re.search(r'pidana penjara selama [^.,;\n]+', amar_lower)
    denda = re.search(r'pidana denda sejumlah [^.,;\n]+', amar_lower)
    subsider = re.search(r'diganti dengan pidana penjara selama [^.,;\n]+', amar_lower)

    hasil = []
    if penjara:
        kal = penjara.group()
        kal = re.sub(r'(\d+)\s*(tahun|bulan|hari)', r'\1 \2', kal)
        kal = re.sub(r'(\d+)\s+([a-z]+)\s*(?=\d|\.)', r'\1 ', kal)
        kal = kal.replace("pidana penjara selama ", "")
        hasil.append("Pidana penjara " + kal.strip().capitalize())
    if denda:
        kal = denda.group()
        kal = re.sub(r'pidana denda sejumlah ', '', kal)
        kal = kal.replace("rp", "Rp")
        hasil.append("Denda " + kal.strip().capitalize())
    if subsider:
        kal = subsider.group()
        kal = re.sub(r'diganti dengan pidana penjara selama ', '', kal)
        kal = re.sub(r'(\d+)\s*(tahun|bulan|hari)', r'\1 \2', kal)
        hasil.append("Subsider pidana penjara " + kal.strip().capitalize())

    return '. '.join(hasil).strip() + '.' if hasil else amar.strip()[:150] + "..."

# Fungsi prediksi BERT
def predict_outcome_with_majority_vote_bert(query: str, k: int = 5) -> dict:
    """Memprediksi kategori hukuman menggunakan majority vote (BERT)"""
    top_k_case_ids, top_k_similarities = retrieve_bert(query, k=k)

    if not top_k_case_ids:
        return {
            "predicted_category": "Tidak Diketahui",
            "predicted_sentence_range": "Tidak diketahui",
            "detailed_sentence": "Tidak ada kasus serupa ditemukan.",
            "confidence": 0.0,
            "top_k_case_ids": [],
            "most_similar_case_solution": "Tidak ada kasus serupa ditemukan.",
            "voting_distribution": {}
        }

    retrieved_categories = [case_categories.get(cid, 'Lainnya') for cid in top_k_case_ids]
    category_counts = Counter(retrieved_categories)

    if 'Lainnya' in category_counts and len(category_counts) > 1:
        del category_counts['Lainnya']

    predicted_category = category_counts.most_common(1)[0][0] if category_counts else "Tidak Diketahui"
    confidence = category_counts.most_common(1)[0][1] / len(top_k_case_ids) if category_counts else 0.0

    most_similar_case_id = top_k_case_ids[0]
    predicted_solution_text = case_solutions.get(most_similar_case_id, "Solusi tidak ditemukan.")
    detailed_sentence = ringkas_putusan(predicted_solution_text)

    sentence_ranges = {
        "Hukuman Ringan": "1-4 tahun atau hukuman ringan (misal: rehabilitasi, percobaan)",
        "Hukuman Sedang": "5-9 tahun penjara",
        "Hukuman Berat": "≥10 tahun penjara, seumur hidup, atau hukuman mati"
    }
    predicted_sentence_range = sentence_ranges.get(predicted_category, "Tidak diketahui")

    return {
        "predicted_category": predicted_category,
        "predicted_sentence_range": predicted_sentence_range,
        "detailed_sentence": detailed_sentence,
        "confidence": float(confidence),
        "top_k_case_ids": top_k_case_ids,
        "most_similar_case_solution": predicted_solution_text,
        "voting_distribution": dict(category_counts)
    }

# Fungsi prediksi TF-IDF + SVM
def predict_outcome_with_majority_vote_tfidf_svm(query: str, k: int = 5) -> dict:
    """Memprediksi kategori hukuman menggunakan majority vote (TF-IDF + SVM)"""
    top_k_case_ids, top_k_similarities = retrieve_tfidf_svm(query, k=k)

    if not top_k_case_ids:
        return {
            "predicted_category": "Tidak Diketahui",
            "predicted_sentence_range": "Tidak diketahui",
            "detailed_sentence": "Tidak ada kasus serupa ditemukan.",
            "confidence": 0.0,
            "top_k_case_ids": [],
            "most_similar_case_solution": "Tidak ada kasus serupa ditemukan.",
            "voting_distribution": {}
        }

    retrieved_categories = [case_categories.get(cid, 'Lainnya') for cid in top_k_case_ids]
    category_counts = Counter(retrieved_categories)

    if 'Lainnya' in category_counts and len(category_counts) > 1:
        del category_counts['Lainnya']

    predicted_category = category_counts.most_common(1)[0][0] if category_counts else "Tidak Diketahui"
    confidence = category_counts[predicted_category] / len(top_k_case_ids) if category_counts else 0.0

    most_similar_case_id = top_k_case_ids[0] if top_k_case_ids else None
    predicted_solution_text = case_solutions.get(most_similar_case_id, "Solusi tidak ditemukan.")

    sentence_ranges = {
        'Hukuman Ringan': "0 - <5 tahun",
        'Hukuman Sedang': "5 - 9 tahun",
        'Hukuman Berat': ">= 10 tahun"
    }
    predicted_sentence_range = sentence_ranges.get(predicted_category, "Tidak diketahui")

    return {
        "predicted_category": predicted_category,
        "predicted_sentence_range": predicted_sentence_range,
        "detailed_sentence": ringkas_putusan(predicted_solution_text),
        "confidence": confidence,
        "top_k_case_ids": top_k_case_ids,
        "most_similar_case_solution": predicted_solution_text,
        "voting_distribution": dict(category_counts)
    }

# Demo manual BERT
print("\n--- Demo Manual (BERT) ---")
predictions_list_majority_vote_bert = []
for index, row in df_uji.iterrows():
    query_text = row['text']
    query_id = row['query_id']
    prediction_results = predict_outcome_with_majority_vote_bert(query_text, k=5)

    predictions_list_majority_vote_bert.append({
        "query_id": query_id,
        "predicted_category": prediction_results['predicted_category'],
        "predicted_sentence_range": prediction_results['predicted_sentence_range'],
        "detailed_sentence": prediction_results['detailed_sentence'],
        "top_k_case_ids": prediction_results['top_k_case_ids'],
        "confidence": prediction_results['confidence'],
        "voting_distribution": prediction_results['voting_distribution']
    })

# Simpan prediksi BERT
df_predictions_majority_vote_bert = pd.DataFrame(predictions_list_majority_vote_bert)
predictions_csv_path_majority_vote_bert = f"{output_dir}/predictions_majority_vote_bert.csv"
df_predictions_majority_vote_bert.to_csv(predictions_csv_path_majority_vote_bert, index=False)
print(f"✅ File prediksi (Majority Vote BERT) saved to: {predictions_csv_path_majority_vote_bert}")

df_bert = pd.read_csv(predictions_csv_path_majority_vote_bert)
df_bert.head()

# Demo manual TF-IDF + SVM
print("\n--- Demo Manual (TF-IDF + SVM) ---")
predictions_list_majority_vote_tfidf_svm = []
for index, row in df_uji.iterrows():
    query_text = row['text']
    query_id = row['query_id']
    prediction_results = predict_outcome_with_majority_vote_tfidf_svm(query_text, k=5)

    predictions_list_majority_vote_tfidf_svm.append({
        "query_id": query_id,
        "predicted_category": prediction_results['predicted_category'],
        "predicted_sentence_range": prediction_results['predicted_sentence_range'],
        "detailed_sentence": prediction_results['detailed_sentence'],
        "top_k_case_ids": prediction_results['top_k_case_ids'],
        "confidence": prediction_results['confidence'],
        "voting_distribution": prediction_results['voting_distribution']
    })

# Simpan prediksi TF-IDF + SVM
df_predictions_majority_vote_tfidf_svm = pd.DataFrame(predictions_list_majority_vote_tfidf_svm)
predictions_csv_path_majority_vote_tfidf_svm = f"{output_dir}/predictions_majority_vote_tfidf_svm.csv"
df_predictions_majority_vote_tfidf_svm.to_csv(predictions_csv_path_majority_vote_tfidf_svm, index=False)
print(f"✅ File prediksi (Majority Vote TF-IDF + SVM) saved to: {predictions_csv_path_majority_vote_tfidf_svm}")

df_svm = pd.read_csv(predictions_csv_path_majority_vote_tfidf_svm)
df_svm.head()

df_uji = pd.DataFrame({
    'query_id': [1, 2, 3, 4, 5],
    'text': [
        "Terdakwa membawa 10 gram sabu dan ditangkap di jalan.",
        "Seorang pria ditangkap karena mengedarkan 5 kg kokain.",
        "Kasus kepemilikan 0.5 gram ganja untuk pribadi.",
        "Tersangka adalah bandar narkoba jaringan internasional.",
        "Pengguna ekstasi tertangkap di kelab malam."
    ]
})


print("\n--- Hasil Prediksi Menggunakan Majority Vote (BERT) ---")
for index, row in df_uji.iterrows():
    query_text = row['text']
    print(f"\nQuery: '{query_text}'")
    bert_prediction = predict_outcome_with_majority_vote_bert(query_text, k=5)
    print(f"   Kategori Prediksi: {bert_prediction['predicted_category']}")
    print(f"   Rentang Pidana: {bert_prediction['predicted_sentence_range']}")
    print(f"   Kepercayaan (Confidence): {bert_prediction['confidence']:.4f}")
    print(f"   Top {len(bert_prediction['top_k_case_ids'])} Case IDs Mirip: {bert_prediction['top_k_case_ids']}")
    print(f"   Distribusi Voting: {bert_prediction['voting_distribution']}")
    print(f"   Amar Putusan Kasus Paling Mirip: {bert_prediction['most_similar_case_solution']}")
    print(f"   Ringkasan Amar Putusan Mirip: {bert_prediction['detailed_sentence']}")

print("\n--- Hasil Prediksi Menggunakan TF-IDF + SVM (Direct Classification) ---")
for index, row in df_uji.iterrows():
    query_text = row['text']
    print(f"\nQuery: '{query_text}'")
    svm_direct_prediction = predict_outcome_with_majority_vote_tfidf_svm(query_text, k=5)
    print(f"   Kategori Prediksi: {svm_direct_prediction['predicted_category']}")
    print(f"   Rentang Pidana: {svm_direct_prediction['predicted_sentence_range']}")
    print(f"   Kepercayaan (Confidence): {svm_direct_prediction['confidence']:.4f}")
    print(f"   Distribusi Probabilitas (Voting): {svm_direct_prediction['voting_distribution']}")
    print(f"   Detail Prediksi: {svm_direct_prediction['detailed_sentence']}")