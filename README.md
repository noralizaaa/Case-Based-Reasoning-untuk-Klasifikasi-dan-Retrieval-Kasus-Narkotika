# Case-Based Reasoning untuk Klasifikasi dan Retrieval Kasus Narkotika
Deskripsi Proyek
Proyek ini mengimplementasikan sistem Case-Based Reasoning (CBR) untuk mengklasifikasikan dan melakukan retrieval kasus narkotika berdasarkan teks putusan pengadilan (amar_putusan).

**Sistem menggunakan dua pendekatan:**

BERT (IndoBERT): Model berbasis transformer untuk menghasilkan embedding teks dan klasifikasi kategori hukuman.

TF-IDF + SVM: Pendekatan berbasis TF-IDF untuk representasi teks dan SVM untuk klasifikasi.

**Fitur utama meliputi:**

Preprocessing teks untuk mengekstrak informasi hukuman (tahun, bulan, denda).

Klasifikasi hukuman ke dalam kategori: Hukuman Ringan, Hukuman Sedang, Hukuman Berat.

Retrieval kasus serupa menggunakan cosine similarity.

Prediksi kategori hukuman menggunakan majority voting berdasarkan kasus serupa.

Evaluasi performa retrieval dan prediksi menggunakan metrik seperti akurasi, presisi, recall, dan F1-score.



**Dependensi**

Proyek ini memerlukan library Python berikut:

pandas: Manipulasi dan analisis data.

numpy: Operasi numerik dan manipulasi array.

re: Regular expression untuk preprocessing teks.

transformers: Memuat model dan tokenizer IndoBERT.

tensorflow: Framework untuk model BERT.

scikit-learn: Klasifikasi (SVM), TF-IDF, dan metrik evaluasi.

matplotlib: Visualisasi bar chart.

seaborn: Visualisasi heatmap confusion matrix.

scipy: Menghitung cosine similarity.

collections: Majority voting dengan Counter.

os: Operasi sistem file.

json: Menyimpan data uji dalam format JSON.

**Instal dependensi dengan perintah:**

pip install pandas numpy transformers tensorflow scikit-learn matplotlib seaborn scipy

**Catatan:**

Pastikan versi transformers dan tensorflow kompatibel (contoh: transformers==4.30.2, tensorflow==2.12.0).

Koneksi internet diperlukan untuk mengunduh model IndoBERT saat pertama kali dijalankan.

**Cara Menjalankan**

Persiapan Data:

Siapkan file Kasus_narkotika3.csv di direktori /content/ dengan kolom case_id, amar_putusan, dan lainnya sesuai kebutuhan.

Pastikan data_uji didefinisikan sebagai list of dictionaries dengan query_id, text, dan ground_truth_case_ids.

Jalankan Kode:

Jika menggunakan Jupyter Notebook (.ipynb):

Buka file di Jupyter Notebook atau Google Colab.

Jalankan sel secara berurutan untuk preprocessing, pelatihan model, retrieval, prediksi, dan evaluasi.


Jika menggunakan skrip Python (.py):

Gabungkan semua bagian kode ke dalam satu file Python.

Jalankan dengan perintah:python script.py


Output:

File hasil disimpan di direktori /content/eval dan /content/results:

queries.json: Data uji dalam format JSON.

predictions_majority_vote_bert.csv: Hasil prediksi BERT.

predictions_majority_vote_tfidf_svm.csv: Hasil prediksi TF-IDF + SVM.

retrieval_metrics.csv: Metrik evaluasi retrieval.

prediction_metrics.csv: Metrik evaluasi prediksi.

retrieval_performance.png: Bar chart performa retrieval.

prediction_performance.png: Bar chart performa prediksi.

Visualisasi:

Heatmap confusion matrix dan bar chart akan ditampilkan saat kode dieksekusi.

File visualisasi disimpan sebagai PNG di direktori /content/eval.
