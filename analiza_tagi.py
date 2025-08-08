#!/usr/bin/env python3
"""
Analiza tagów technicznych w projektach AI/TAI
Ten skrypt analizuje projekty związane z przetwarzaniem języka naturalnego i analizą rozmów w kontekście bankowym.
"""

# Import bibliotek
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Ustawienia wyświetlania
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_colwidth', 100)

# Ustawienia dla wykresów
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
sns.set_style("whitegrid")

print("=" * 60)
print("ANALIZA TAGÓW TECHNICZNYCH W PROJEKTACH AI/TAI")
print("=" * 60)

# 1. Wczytanie danych
print("\n1. WCZYTANIE DANYCH")
print("-" * 40)

df_main = pd.read_csv('tagi_BC.csv')
df_legenda = pd.read_csv('legenda.csv')
df_pivot = pd.read_csv('pivot.csv')

print(f"Liczba projektów: {len(df_main)}")
print(f"Liczba tagów technicznych w legendzie: {len(df_legenda)}")
print(f"\nKolumny w głównym pliku:")
for col in df_main.columns:
    print(f"  - {col}")

# 2. Analiza zespołów i projektów
print("\n\n2. ANALIZA ZESPOŁÓW I PROJEKTÓW")
print("-" * 40)

zespoly = df_main['Zespół zgłaszający potrzebę'].value_counts()
print("\nStatystyki zespołów:")
for zespol, count in zespoly.items():
    print(f"  {zespol}: {count} projektów ({count/len(df_main)*100:.1f}%)")

# Wykres zespołów
plt.figure(figsize=(10, 6))
zespoly.plot(kind='bar')
plt.title('Liczba projektów według zespołów zgłaszających')
plt.xlabel('Zespół')
plt.ylabel('Liczba projektów')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('zespoly_projekty.png')
plt.close()
print("\nWykres zapisany jako: zespoly_projekty.png")

# 3. Analiza celów biznesowych
print("\n\n3. ANALIZA CELÓW BIZNESOWYCH")
print("-" * 40)

cele_biznesowe = df_main['Cel biznesowy'].value_counts().head(10)
print("\nTop 10 celów biznesowych:")
for i, (cel, count) in enumerate(cele_biznesowe.items(), 1):
    print(f"  {i}. {cel}: {count} projektów")

# 4. Analiza KPI
print("\n\n4. ANALIZA KPI")
print("-" * 40)

kpi_counts = df_main['KPI'].value_counts().head(10)
print("\nTop 10 KPI:")
for i, (kpi, count) in enumerate(kpi_counts.items(), 1):
    print(f"  {i}. {kpi}: {count} projektów")

# 5. Analiza tagów technicznych
print("\n\n5. ANALIZA TAGÓW TECHNICZNYCH")
print("-" * 40)

# Ekstrakcja wszystkich tagów
all_tags = []
for tags in df_main['TAI - tagi'].dropna():
    tag_list = [tag.strip() for tag in tags.split(',')]
    all_tags.extend(tag_list)

# Liczenie wystąpień tagów
tag_counts = Counter(all_tags)
print(f"\nLiczba unikalnych tagów: {len(tag_counts)}")
print(f"Łączna liczba użyć tagów: {sum(tag_counts.values())}")

# Top 20 tagów
print("\nTop 20 najczęściej używanych tagów:")
for i, (tag, count) in enumerate(tag_counts.most_common(20), 1):
    print(f"  {i:2d}. {tag:40s}: {count:3d} wystąpień")

# Wykres top tagów
top_tags = dict(tag_counts.most_common(15))
plt.figure(figsize=(12, 8))
plt.barh(list(top_tags.keys()), list(top_tags.values()))
plt.xlabel('Liczba wystąpień')
plt.title('Top 15 najczęściej używanych tagów')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('top_tagi.png')
plt.close()
print("\nWykres zapisany jako: top_tagi.png")

# 6. Analiza kategorii tagów
print("\n\n6. ANALIZA KATEGORII TAGÓW")
print("-" * 40)

tag_categories = {
    'Frazy': [tag for tag in tag_counts.keys() if 'frazy' in tag],
    'LLM': [tag for tag in tag_counts.keys() if 'llm' in tag],
    'Baza wektorowa': [tag for tag in tag_counts.keys() if 'baza-wektorowa' in tag],
    'Klasyfikacja': [tag for tag in tag_counts.keys() if 'klasyfikacja' in tag or 'classification' in tag],
    'Analiza': [tag for tag in tag_counts.keys() if 'analiza' in tag or 'analysis' in tag],
    'Detekcja': [tag for tag in tag_counts.keys() if 'detection' in tag or 'detekcja' in tag]
}

print("\nKategorie tagów:")
for cat, tags in tag_categories.items():
    if tags:
        total_usage = sum(tag_counts[tag] for tag in tags)
        print(f"\n{cat} ({len(tags)} tagów, {total_usage} użyć):")
        for tag in sorted(tags)[:5]:  # Pokaż max 5
            count = tag_counts[tag]
            print(f"  - {tag}: {count} wystąpień")
        if len(tags) > 5:
            print(f"  ... i {len(tags) - 5} więcej")

# 7. Analiza złożoności projektów
print("\n\n7. ANALIZA ZŁOŻONOŚCI PROJEKTÓW")
print("-" * 40)

# Liczba tagów per projekt
df_main['liczba_tagow'] = df_main['TAI - tagi'].apply(
    lambda x: len(x.split(',')) if pd.notna(x) else 0
)

print(f"Średnia liczba tagów na projekt: {df_main['liczba_tagow'].mean():.2f}")
print(f"Mediana liczby tagów: {df_main['liczba_tagow'].median():.0f}")
print(f"Minimalna liczba tagów: {df_main['liczba_tagow'].min()}")
print(f"Maksymalna liczba tagów: {df_main['liczba_tagow'].max()}")

# Najbardziej złożone projekty
print("\nNajbardziej złożone projekty (najwięcej tagów):")
complex_projects = df_main.nlargest(5, 'liczba_tagow')[['Projekt', 'liczba_tagow']]
for idx, row in complex_projects.iterrows():
    print(f"  - {row['Projekt'][:60]}... : {row['liczba_tagow']} tagów")

# 8. Analiza korelacji tagów (używając pivot)
print("\n\n8. ANALIZA KORELACJI TAGÓW")
print("-" * 40)

# Wybierz kolumny TAG_ z pivot
tag_columns = [col for col in df_pivot.columns if col.startswith('TAG_')]

# Oblicz sumę dla każdego tagu
tag_sums = df_pivot[tag_columns].sum().sort_values(ascending=False)

# Znajdź pary tagów często występujące razem
print("\nNajczęściej współwystępujące tagi:")
correlations = []
for i in range(min(10, len(tag_columns))):
    for j in range(i+1, min(10, len(tag_columns))):
        tag1 = tag_sums.index[i].replace('TAG_', '')
        tag2 = tag_sums.index[j].replace('TAG_', '')
        # Policz projekty gdzie oba tagi występują
        both = ((df_pivot[tag_sums.index[i]] == 1) & (df_pivot[tag_sums.index[j]] == 1)).sum()
        if both > 2:  # Minimum 3 wspólne projekty
            correlations.append((tag1, tag2, both))

correlations.sort(key=lambda x: x[2], reverse=True)
for tag1, tag2, count in correlations[:10]:
    print(f"  {tag1} + {tag2}: {count} projektów")

# 9. Analiza według typu zadania
print("\n\n9. ANALIZA WEDŁUG TYPU ZADANIA")
print("-" * 40)

# Ekstrakcja typu zadania z kolumny Dodatkowe
df_main['typ_zadania'] = df_main['Dodatkowe'].apply(
    lambda x: 'BIZNES' if 'BIZNES' in str(x) else 
              ('KONTROLA' if 'KONTROLA' in str(x) else 
               ('PROCES' if 'PROCES' in str(x) else 'NIEZNANY'))
)

typ_counts = df_main['typ_zadania'].value_counts()
print("\nRozkład projektów według typu:")
for typ, count in typ_counts.items():
    print(f"  {typ}: {count} projektów ({count/len(df_main)*100:.1f}%)")

# 10. Podsumowanie i rekomendacje
print("\n\n10. PODSUMOWANIE I REKOMENDACJE")
print("=" * 60)

print(f"\nKluczowe metryki:")
print(f"  - Liczba projektów: {len(df_main)}")
print(f"  - Liczba unikalnych tagów: {len(set(all_tags))}")
print(f"  - Średnia liczba tagów na projekt: {df_main['liczba_tagow'].mean():.2f}")
print(f"  - Dominujący zespół: {zespoly.index[0]} ({zespoly.iloc[0]} projektów)")
print(f"  - Najczęstszy cel biznesowy: {cele_biznesowe.index[0]}")
print(f"  - Najczęstszy tag: {tag_counts.most_common(1)[0][0]} ({tag_counts.most_common(1)[0][1]} wystąpień)")

# Rekomendacje
print("\nRekomendacje:")

# Analiza rzadkich tagów
rzadkie_tagi = [tag for tag, count in tag_counts.items() if count == 1]
if rzadkie_tagi:
    print(f"\n1. Optymalizacja tagów:")
    print(f"   - Znaleziono {len(rzadkie_tagi)} tagów używanych tylko raz")
    print(f"   - Rozważyć konsolidację lub eliminację rzadko używanych tagów")

# Analiza technologii
tech_usage = {
    'Klasyczne ML': sum(1 for tag in all_tags if any(kw in tag for kw in ['frazy-binary', 'klasyfikacja', 'clustering'])),
    'LLM/GenAI': sum(1 for tag in all_tags if 'llm' in tag),
    'Bazy wektorowe': sum(1 for tag in all_tags if 'baza-wektorowa' in tag or 'retrieval' in tag)
}

print(f"\n2. Adopcja technologii:")
for tech, count in tech_usage.items():
    percent = count / len(all_tags) * 100
    print(f"   - {tech}: {percent:.1f}% użyć")

# Złożoność projektów
wieloetapowe = df_main['TAI - uwagi'].apply(
    lambda x: 'wieloetapowe' in str(x).lower() if pd.notna(x) else False
).sum()

if wieloetapowe > len(df_main) * 0.3:
    print(f"\n3. Złożoność projektów:")
    print(f"   - {wieloetapowe} projektów wieloetapowych ({wieloetapowe/len(df_main)*100:.1f}%)")
    print(f"   - Rozważyć dekompozycję lub automatyzację złożonych procesów")

print("\n" + "=" * 60)
print("ANALIZA ZAKOŃCZONA")
print("=" * 60)

# Zapisz raport
raport_data = {
    'Metryka': [
        'Liczba projektów',
        'Liczba unikalnych tagów', 
        'Średnia liczba tagów na projekt',
        'Najczęstszy zespół',
        'Najczęstszy cel biznesowy',
        'Najczęstszy tag',
        'Projekty BIZNES',
        'Projekty KONTROLA',
        'Projekty PROCES'
    ],
    'Wartość': [
        len(df_main),
        len(set(all_tags)),
        f"{df_main['liczba_tagow'].mean():.2f}",
        f"{zespoly.index[0]} ({zespoly.iloc[0]})",
        cele_biznesowe.index[0],
        f"{tag_counts.most_common(1)[0][0]} ({tag_counts.most_common(1)[0][1]})",
        typ_counts.get('BIZNES', 0),
        typ_counts.get('KONTROLA', 0),
        typ_counts.get('PROCES', 0)
    ]
}

df_raport = pd.DataFrame(raport_data)
df_raport.to_csv('raport_analizy.csv', index=False)
print("\nRaport zapisany do pliku: raport_analizy.csv")