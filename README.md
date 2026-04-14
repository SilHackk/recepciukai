# 🍳 Maisto receptų generatorius

Interaktyvus NLP projektas, kuris leidžia vartotojui įvesti turimus ingredientus (su kiekiais) ir automatiškai gauti receptus, kuriuos galima pagaminti.

Sistema taip pat nurodo:
- kurie ingredientai sutampa
- kurių ingredientų trūksta
- kaip pagaminti patiekalą

---

## 🚀 Funkcionalumas

- Ingredientų įvedimas (su kiekiais)
- Kiekio ir vienetų atpažinimas (Regex)
- Ingredientų normalizavimas (LT → EN)
- Receptų paieška pagal panašumą (TF-IDF)
- Fuzzy matching ingredientams
- Trūkstamų ingredientų nustatymas
- Interaktyvus UI su Streamlit

---

## 🧠 Naudoti NLP metodai

### 1. Regex (Reguliarūs išsireiškimai)
Naudojami kiekio ir vienetų ištraukimui iš teksto:
- `200 g`
- `250 ml`
- `2 kiaušiniai`

### 2. Tokenizacija ir normalizavimas
- Tekstas suskaidomas į žodžius
- Pašalinami nereikšminiai žodžiai
- Ingredientai suvienodinami (pvz. „pomidorai“ → „tomato“)

### 3. TF-IDF
- Ingredientų sąrašai paverčiami vektoriais
- Skaičiuojamas panašumas tarp vartotojo įvesties ir receptų

### 4. Fuzzy matching
- Leidžia atpažinti panašius žodžius:
  - `pomidorai` ≈ `tomato`
  - `svogūnas` ≈ `onion`

---

## 📊 Papildoma logika

- Receptai reitinguojami pagal:
  - ingredientų padengimą
  - TF-IDF panašumą
- Galima nustatyti maksimalų trūkstamų ingredientų skaičių
- Greitas atsakas (tinka demo)

---

## 📂 Naudojami duomenys

Naudojamas atviras receptų datasetas (~13k receptų).

Pirmo paleidimo metu automatiškai parsisiunčiamas CSV failas:
data/13k-recipes.csv


---

## ⚙️ Paleidimo instrukcija

### 1. Atsisiųsk projektą

git clone <TAVO_REPO_LINK>
cd <repo_pavadinimas>

### 2. Susikurk virtualią aplinką
python -m venv .venv

### 3. Aktyvuok virtualią aplinką
Windows:
.venv\Scripts\activate
Linux / Mac:
source .venv/bin/activate
### 4. Įdiek priklausomybes
pip install -r requirements.txt
### 5. Paleisk programą
streamlit run app.py
### 6. Atidaryk naršyklėje

Jei neatsidaro automatiškai:

http://localhost:8501
