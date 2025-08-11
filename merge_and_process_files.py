import pandas as pd
import numpy as np
from collections import defaultdict
import re

# Wczytanie plików
print("Wczytywanie plików...")
df1 = pd.read_csv('TAI_EDIT_Voice2text_claude_gpt_human.csv')
df2 = pd.read_csv('TAGI_BC_ODZ.csv')

# Wyświetlenie informacji o plikach
print(f"\nPlik 1 - TAI_EDIT_Voice2text_claude_gpt_human.csv:")
print(f"Liczba wierszy: {len(df1)}")
print(f"Kolumny: {list(df1.columns)}")

print(f"\nPlik 2 - TAGI_BC_ODZ.csv:")
print(f"Liczba wierszy: {len(df2)}")
print(f"Kolumny: {list(df2.columns)}")

# Łączenie plików - używamy outer join aby zachować wszystkie rekordy
# Najpierw musimy znaleźć wspólne kolumny do łączenia
# Sprawdzamy, czy są jakieś wspólne kolumny
common_columns = set(df1.columns).intersection(set(df2.columns))
print(f"\nWspólne kolumny: {common_columns}")

# Jeśli nie ma wspólnych kolumn identyfikujących, łączymy po indeksie
# Dodajemy prefix do kolumn z drugiego pliku, które się powtarzają
df2_renamed = df2.copy()
for col in df2.columns:
    if col in df1.columns and col != 'TAI - tagi':  # Zachowujemy kolumnę TAI - tagi
        df2_renamed.rename(columns={col: f"{col}_BC"}, inplace=True)

# Łączenie dataframe'ów
# Zakładam, że pliki mają odpowiadające sobie wiersze w tej samej kolejności
if len(df1) == len(df2):
    print("\nPliki mają taką samą liczbę wierszy - łączę po indeksie")
    merged_df = pd.concat([df1, df2_renamed], axis=1)
else:
    print("\nPliki mają różną liczbę wierszy - łączę wszystkie dane")
    # Jeśli pliki mają różną liczbę wierszy, musimy je połączyć inaczej
    # Szukamy kolumn, które mogą służyć jako klucz
    # Sprawdzamy kolumnę 'Projekt' w df1 i 'NAZWA - PROJEKT' w df2
    if 'Projekt' in df1.columns and 'NAZWA - PROJEKT' in df2.columns:
        merged_df = pd.merge(df1, df2_renamed, 
                           left_on='Projekt', 
                           right_on='NAZWA - PROJEKT', 
                           how='outer')
    else:
        # Jeśli nie możemy znaleźć klucza, łączymy wszystkie dane
        merged_df = pd.concat([df1, df2_renamed], axis=0, ignore_index=True)

print(f"\nPołączony plik:")
print(f"Liczba wierszy: {len(merged_df)}")
print(f"Liczba kolumn: {len(merged_df.columns)}")

# Standaryzacja tagów
print("\n\nStandaryzacja tagów...")

# Funkcja do standaryzacji tagów
def standardize_tags(tags_str):
    if pd.isna(tags_str) or tags_str == '':
        return ''
    
    # Słownik mapowania różnych wersji tagów na standardową wersję
    tag_mapping = {
        # Clustering fraz
        'clusterowanie-fraz': 'frazy-clustering',
        'clustering-frazy': 'frazy-clustering',
        'frazy-clusterowanie': 'frazy-clustering',
        'frazy-klasteryzacja': 'frazy-clustering',
        
        # Ekstrakcja fraz
        'ekstrakcja-fraz': 'frazy-ekstrakcja',
        'frazy-extraction': 'frazy-ekstrakcja',
        
        # Binary frazy
        'binary-frazy': 'frazy-binary',
        'frazy-binarne': 'frazy-binary',
        
        # Kategoryzacja
        'kategoryzacja-rozmow': 'kategoryzacja-rozmów',
        'kategorizacja-rozmów': 'kategoryzacja-rozmów',
        
        # Ocena
        'llm-ocena-argumentow': 'llm-ocena-argumentów',
        'llm-ocena-pokrycia': 'llm-ocena-pokrycia',
        
        # Retrieval
        'retrieval-reranking': 'retrieval+reranking',
        'retrieval_reranking': 'retrieval+reranking',
        
        # Inne
        'frazy-binaryx2': 'frazy-binary-x2',
        'pair-classfication-client-agent': 'pair-classification-agent-client',
        'pair-classification-client-agent': 'pair-classification-agent-client',
    }
    
    # Rozdziel tagi
    tags = [tag.strip() for tag in str(tags_str).split(',')]
    
    # Standaryzuj każdy tag
    standardized_tags = []
    for tag in tags:
        tag_lower = tag.lower()
        # Sprawdź czy tag jest w mapowaniu
        standardized = tag_mapping.get(tag_lower, tag)
        standardized_tags.append(standardized)
    
    # Usuń duplikaty zachowując kolejność
    seen = set()
    unique_tags = []
    for tag in standardized_tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return ', '.join(unique_tags)

# Aplikuj standaryzację do kolumn z tagami
if 'TAI - tagi' in merged_df.columns:
    merged_df['TAI - tagi_standaryzowane'] = merged_df['TAI - tagi'].apply(standardize_tags)
    print("Utworzono kolumnę: TAI - tagi_standaryzowane")

if 'TAI-tagi' in merged_df.columns:
    merged_df['TAI-tagi_standaryzowane'] = merged_df['TAI-tagi'].apply(standardize_tags)
    print("Utworzono kolumnę: TAI-tagi_standaryzowane")

# Połącz tagi z obu źródeł jeśli istnieją
if 'TAI - tagi_standaryzowane' in merged_df.columns and 'TAI-tagi_standaryzowane' in merged_df.columns:
    def merge_tags(tag1, tag2):
        if pd.isna(tag1) or tag1 == '':
            return tag2 if not pd.isna(tag2) else ''
        if pd.isna(tag2) or tag2 == '':
            return tag1
        
        # Połącz i usuń duplikaty
        all_tags = tag1.split(', ') + tag2.split(', ')
        seen = set()
        unique = []
        for tag in all_tags:
            if tag and tag not in seen:
                seen.add(tag)
                unique.append(tag)
        return ', '.join(unique)
    
    merged_df['TAI_tagi_final'] = merged_df.apply(
        lambda row: merge_tags(
            row.get('TAI - tagi_standaryzowane', ''), 
            row.get('TAI-tagi_standaryzowane', '')
        ), axis=1
    )
elif 'TAI - tagi_standaryzowane' in merged_df.columns:
    merged_df['TAI_tagi_final'] = merged_df['TAI - tagi_standaryzowane']
elif 'TAI-tagi_standaryzowane' in merged_df.columns:
    merged_df['TAI_tagi_final'] = merged_df['TAI-tagi_standaryzowane']

# Tworzenie kolumn pipeline
print("\n\nTworzenie kolumn pipeline...")

# Zbierz wszystkie unikalne kombinacje tagów metodologicznych
methodological_tags = [
    'frazy-binary', 'frazy-ekstrakcja', 'frazy-clustering',
    'llm-ocena-argumentów', 'llm-ocena-pokrycia', 'llm-podsumowanie',
    'baza-wektorowa', 'retrieval+reranking', 'multi-label-klasyfikacja',
    'kategoryzacja-rozmów', 'scoring', 'thresholding',
    'human-in-the-loop', 'pair-classification-agent-client',
    'topic-modeling', 'sentyment', 'timeline-analiza'
]

# Funkcja do wyodrębnienia pipeline'ów
def extract_pipelines(tags_str):
    if pd.isna(tags_str) or tags_str == '':
        return []
    
    tags = [tag.strip() for tag in str(tags_str).split(',')]
    # Filtruj tylko tagi metodologiczne
    method_tags = [tag for tag in tags if any(
        method in tag for method in ['frazy', 'llm', 'baza-wektorowa', 
        'retrieval', 'klasyfikacja', 'kategoryzacja', 'scoring', 
        'clustering', 'sentyment', 'topic', 'pair-classification']
    )]
    
    return method_tags

# Znajdź wszystkie unikalne pipeline'y
all_pipelines = set()
for idx, row in merged_df.iterrows():
    if 'TAI_tagi_final' in merged_df.columns:
        pipeline = extract_pipelines(row['TAI_tagi_final'])
        if pipeline:
            # Sortuj tagi w pipeline dla spójności
            pipeline_str = ', '.join(sorted(pipeline))
            all_pipelines.add(pipeline_str)

print(f"\nZnalezione unikalne pipeline'y: {len(all_pipelines)}")
for i, pipeline in enumerate(sorted(all_pipelines), 1):
    print(f"{i}. {pipeline}")

# Twórz kolumny dla każdego pipeline'u
for pipeline in sorted(all_pipelines):
    if pipeline:  # Pomijamy puste pipeline'y
        col_name = f"pipeline_{pipeline.replace(', ', '_').replace('-', '_')}"
        # Ogranicz długość nazwy kolumny
        if len(col_name) > 100:
            col_name = col_name[:97] + "..."
        
        merged_df[col_name] = 0
        
        # Ustaw 1 dla wierszy, które mają ten pipeline
        for idx, row in merged_df.iterrows():
            if 'TAI_tagi_final' in merged_df.columns:
                row_pipeline = extract_pipelines(row['TAI_tagi_final'])
                if row_pipeline:
                    row_pipeline_str = ', '.join(sorted(row_pipeline))
                    if row_pipeline_str == pipeline:
                        merged_df.at[idx, col_name] = 1

# Podsumowanie
print(f"\n\nPodsumowanie:")
print(f"Liczba wierszy w połączonym pliku: {len(merged_df)}")
print(f"Liczba kolumn w połączonym pliku: {len(merged_df.columns)}")
print(f"Liczba utworzonych kolumn pipeline: {len([col for col in merged_df.columns if col.startswith('pipeline_')])}")

# Zapisz wynikowy plik
output_filename = 'merged_tai_bc_with_pipelines.csv'
merged_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
print(f"\n\nPlik zapisany jako: {output_filename}")

# Wyświetl przykładowe dane
print("\n\nPrzykładowe dane (pierwsze 3 wiersze):")
display_columns = ['Projekt', 'TAI_tagi_final'] + [col for col in merged_df.columns if col.startswith('pipeline_')][:3]
display_columns = [col for col in display_columns if col in merged_df.columns]
if display_columns:
    print(merged_df[display_columns].head(3))