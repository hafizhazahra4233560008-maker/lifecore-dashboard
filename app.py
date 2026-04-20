import streamlit as st
import pandas as pd
import altair as alt

# ===== CONFIG =====
st.set_page_config(page_title="LIFECORE", layout="wide")

# ===== STYLE (FIX BACKGROUND + CARD) =====
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}

.card {
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
}

.blue {background: linear-gradient(135deg, #4facfe, #00f2fe);}
.green {background: linear-gradient(135deg, #43e97b, #38f9d7);}
.red {background: linear-gradient(135deg, #fa709a, #fee140);}

/* 🔥 TAMBAHAN BARU */
.model-card {
    padding: 25px;
    border-radius: 20px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    text-align: center;
    margin-bottom: 20px;
}

.predict-box {
    padding: 20px;
    border-radius: 15px;
    background: linear-gradient(135deg, #ff9a9e, #fad0c4);
}
</style>
""", unsafe_allow_html=True)

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    return pd.read_csv("cardio_train.csv", sep=';')

# ===== HEADER =====
st.title("🫀 LIFECORE - Dashboard Kesehatan")

st.markdown("""
Dashboard ini menampilkan data kesehatan terkait **penyakit jantung**.  
Digunakan untuk melihat hubungan antara umur, BMI (Body Mass Index), tekanan darah, dan risiko penyakit.
""")

# ===== INPUT =====
file = st.file_uploader("📂 Upload data tambahan (opsional)", type=["csv"])

if file:
    df = pd.read_csv(file, sep=';')
else:
    df = load_data()

# ===== PREPROCESS =====
df.columns = df.columns.str.strip()
df["age_year"] = df["age"]
df["BMI"] = df["weight"] / ((df["height"]/100) ** 2)

# ===== RINGKASAN =====
st.subheader("📌 Ringkasan")

avg_age = df["age_year"].mean()
avg_bmi = df["BMI"].mean()
risk = df["cardio"].mean() * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<div class="card blue"><h4>🧑 Umur rata-rata</h4><h2>{avg_age:.1f} tahun</h2></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="card green"><h4>⚖️ BMI rata-rata</h4><h2>{avg_bmi:.1f}</h2></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="card red"><h4>❤️ Risiko penyakit</h4><h2>{risk:.1f}%</h2></div>', unsafe_allow_html=True)

# ===== KATEGORI =====
if avg_bmi < 18.5:
    bmi_status = "di bawah normal"
elif avg_bmi < 25:
    bmi_status = "normal"
elif avg_bmi < 30:
    bmi_status = "kelebihan berat badan"
else:
    bmi_status = "obesitas"

if risk < 30:
    risk_status = "rendah"
elif risk < 60:
    risk_status = "sedang"
else:
    risk_status = "tinggi"

st.caption(f"""
BMI rata-rata berada pada kategori **{bmi_status}**,  
dengan tingkat risiko penyakit tergolong **{risk_status}**.
""")

st.markdown("---")

# ===== SAMPLE (FIX BIAR TIDAK BERUBAH) =====
df_sample = df.sample(min(3000, len(df)), random_state=42)  # 🔥 UPDATE

# =====================================================
# 📊 DISTRIBUSI BMI
# =====================================================
st.subheader("📊 Distribusi BMI")
st.caption("Sumbu X = BMI | Sumbu Y = jumlah responden")

bmi_dist = df_sample["BMI"].round().value_counts().sort_index().reset_index()
bmi_dist.columns = ["BMI", "Jumlah"]

chart_bmi = alt.Chart(bmi_dist).mark_bar(color="#43e97b").encode(
    x="BMI:O",
    y="Jumlah:Q",
    tooltip=["BMI", "Jumlah"]
)
st.altair_chart(chart_bmi, use_container_width=True)

bmi_most = bmi_dist.loc[bmi_dist["Jumlah"].idxmax(), "BMI"]

st.write(f"Sebagian besar responden memiliki BMI di sekitar nilai {bmi_most}.")

st.caption("""
BMI (Body Mass Index) adalah ukuran sederhana untuk menilai apakah berat badan seseorang sudah sesuai dengan tinggi badannya.  

Secara umum:
- BMI < 18.5 → terlalu kurus  
- 18.5 – 24.9 → normal  
- 25 – 29.9 → kelebihan berat badan  
- ≥ 30 → obesitas  

Grafik ini menunjukkan bagaimana kondisi berat badan responden tersebar dalam data.
""")

# =====================================================
# 📊 RISIKO BERDASARKAN UMUR
# =====================================================
st.subheader("📊 Risiko Berdasarkan Umur")
st.caption("Sumbu X = kelompok umur | Sumbu Y = risiko")

df_sample["age_group"] = pd.cut(df_sample["age_year"], bins=5).astype(str)
age_risk = df_sample.groupby("age_group")["cardio"].mean().reset_index()

chart_age = alt.Chart(age_risk).mark_bar(color="#4facfe").encode(
    x="age_group:O",
    y="cardio:Q"
)
st.altair_chart(chart_age, use_container_width=True)

max_risk_group = age_risk.loc[age_risk["cardio"].idxmax(), "age_group"]

st.write(f"Kelompok umur dengan risiko tertinggi berada pada rentang {max_risk_group}.")

st.caption("""
Grafik ini membandingkan kelompok umur dengan kemungkinan terkena penyakit jantung.  

Semakin tinggi nilai pada grafik, semakin banyak responden dalam kelompok tersebut yang memiliki penyakit.  

Secara umum, risiko penyakit jantung cenderung meningkat seiring bertambahnya usia.
""")

# =====================================================
# ❤️ KONDISI KESEHATAN
# =====================================================
st.subheader("❤️ Kondisi Kesehatan")
st.caption("0 = tidak sakit | 1 = sakit")

health = df["cardio"].value_counts().reset_index()
health.columns = ["Status", "Jumlah"]

chart_health = alt.Chart(health).mark_bar(color="#fa709a").encode(
    x="Status:O",
    y="Jumlah:Q"
)
st.altair_chart(chart_health, use_container_width=True)

sehat = health.loc[health["Status"] == 0, "Jumlah"].values[0]
sakit = health.loc[health["Status"] == 1, "Jumlah"].values[0]

if sakit > sehat:
    st.write("Jumlah responden dengan penyakit lebih banyak dibanding yang sehat.")
else:
    st.write("Sebagian besar responden berada dalam kondisi sehat.")

st.caption("""
Grafik ini menunjukkan perbandingan jumlah responden yang sehat dan yang memiliki penyakit jantung.  

- Nilai 0 → tidak memiliki penyakit  
- Nilai 1 → memiliki penyakit  

Ini membantu melihat seberapa besar proporsi kondisi kesehatan dalam data.
""")

# =====================================================
# 🩺 BMI vs TEKANAN DARAH
# =====================================================
st.subheader("🩺 BMI dan Tekanan Darah")
st.caption("X = BMI | Y = tekanan darah atas")

chart_scatter = alt.Chart(df_sample).mark_circle(size=60, color="#ff9a9e").encode(
    x="BMI",
    y="ap_hi"
)
st.altair_chart(chart_scatter, use_container_width=True)

corr = df_sample["BMI"].corr(df_sample["ap_hi"])

if corr > 0.3:
    st.write("Terdapat kecenderungan bahwa semakin tinggi BMI, tekanan darah juga meningkat.")
else:
    st.write("Hubungan antara BMI dan tekanan darah tidak terlalu kuat pada data ini.")

st.caption("""
Grafik ini menunjukkan hubungan antara berat badan (BMI) dan tekanan darah.  

Setiap titik mewakili satu orang.  
Jika titik-titik cenderung naik ke atas, berarti semakin tinggi BMI, tekanan darah juga meningkat.  

Hal ini penting karena tekanan darah tinggi merupakan salah satu faktor risiko penyakit jantung.
""")

# =====================================================
# 📉 TEKANAN DARAH
# =====================================================
st.subheader("📉 Tekanan Darah")

line_data = df_sample[["ap_hi", "ap_lo"]].reset_index().melt(id_vars=["index"])

chart_line = alt.Chart(line_data).mark_line().encode(
    x="index",
    y="value",
    color="variable"
)
st.altair_chart(chart_line, use_container_width=True)

avg_hi = df_sample["ap_hi"].mean()
avg_lo = df_sample["ap_lo"].mean()

st.write(f"Rata-rata tekanan darah atas sekitar {avg_hi:.0f}, sedangkan bawah sekitar {avg_lo:.0f}.")

st.caption("""
Tekanan darah terdiri dari dua nilai:
- Tekanan atas (sistolik) → saat jantung memompa darah  
- Tekanan bawah (diastolik) → saat jantung beristirahat  

Perbedaan kedua nilai ini membantu memahami kondisi tekanan darah seseorang.
""")

# ===== RINGKASAN =====
st.subheader("🧾 Ringkasan 🧾")

# insight tambahan dari data
bmi_most = bmi_dist.loc[bmi_dist["Jumlah"].idxmax(), "BMI"]
max_risk_group = age_risk.loc[age_risk["cardio"].idxmax(), "age_group"]

# hubungan BMI & tekanan darah
corr = df_sample["BMI"].corr(df_sample["ap_hi"])

if corr > 0.3:
    hubungan = "terlihat adanya kecenderungan hubungan antara BMI dan tekanan darah"
else:
    hubungan = "tidak terlihat hubungan yang kuat antara BMI dan tekanan darah"

# kondisi kesehatan
sehat = health.loc[health["Status"] == 0, "Jumlah"].values[0]
sakit = health.loc[health["Status"] == 1, "Jumlah"].values[0]

if sakit > sehat:
    kondisi = "jumlah responden dengan penyakit lebih banyak dibandingkan yang sehat"
else:
    kondisi = "sebagian besar responden berada dalam kondisi sehat"

# tampilkan ringkasan
st.write(f"""
Berdasarkan data yang dianalisis, rata-rata umur responden berada di sekitar {avg_age:.1f} tahun 
dengan nilai BMI rata-rata {avg_bmi:.1f}. Sebagian besar responden memiliki BMI di sekitar {bmi_most}.

Kelompok umur dengan tingkat risiko tertinggi berada pada rentang {max_risk_group}. 
Selain itu, {hubungan}.

Secara umum, {kondisi}, dengan tingkat risiko penyakit jantung sebesar {risk:.1f}% dalam dataset ini.
""")

# =====================================================
# 🤖 MODEL PREDIKSI (LOGISTIC REGRESSION)
# =====================================================
st.subheader("🤖 Model Prediksi Penyakit Jantung")

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# fitur yang digunakan
features = ["age_year", "BMI", "ap_hi", "ap_lo"]

# pastikan tidak ada missing value
df_model = df[features + ["cardio"]].dropna()

X = df_model[features]
y = df_model["cardio"]

# split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# prediksi
y_pred = model.predict(X_test)

# akurasi
acc = accuracy_score(y_test, y_pred)

st.markdown(f"""
<div class="model-card">
    <h3>🤖 Akurasi Model</h3>
    <h1>{acc*100:.2f}%</h1>
</div>
""", unsafe_allow_html=True)

# contoh prediksi
st.markdown('</div>', unsafe_allow_html=True)
st.subheader("🔍 Coba Prediksi")

col1, col2 = st.columns(2)

with col1:
    input_age = st.number_input("Umur", value=40)
    input_bmi = st.number_input("BMI", value=25.0)

with col2:
    input_hi = st.number_input("Tekanan Darah Atas", value=120)
    input_lo = st.number_input("Tekanan Darah Bawah", value=80)

# prediksi user
if st.button("Prediksi"):
    input_data = [[input_age, input_bmi, input_hi, input_lo]]
    hasil = model.predict(input_data)[0]

    if hasil == 1:
        st.markdown("""
        <div style="background:#ff4b5c;padding:15px;border-radius:10px;color:white;text-align:center;">
            ❤️ Berisiko Tinggi Penyakit Jantung
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#00c853;padding:15px;border-radius:10px;color:white;text-align:center;">
            💚 Risiko Rendah Penyakit Jantung
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# 🤖 INSIGHT OTOMATIS
# =====================================================
st.subheader("🤖 Insight 🤖")

# Korelasi BMI dan tekanan darah
corr_full = df["BMI"].corr(df["ap_hi"])

if corr_full > 0.3:
    st.write("Terdapat kecenderungan bahwa semakin tinggi BMI, tekanan darah juga meningkat.")
else:
    st.write("Tidak terlihat hubungan yang kuat antara BMI dan tekanan darah pada data ini.")

# Risiko keseluruhan
if risk > 60:
    st.write("Secara umum, tingkat risiko penyakit jantung dalam data ini tergolong tinggi.")
elif risk > 30:
    st.write("Risiko penyakit jantung berada pada tingkat sedang.")
else:
    st.write("Risiko penyakit jantung tergolong rendah.")

# BMI kategori umum
if avg_bmi < 18.5:
    st.write("Rata-rata responden cenderung memiliki berat badan di bawah normal.")
elif avg_bmi < 25:
    st.write("Sebagian besar responden memiliki berat badan yang normal.")
else:
    st.write("Terdapat kecenderungan kelebihan berat badan pada responden.")

# Kelompok umur risiko tertinggi
st.write(f"Kelompok umur dengan risiko tertinggi berada pada rentang {max_risk_group}.")