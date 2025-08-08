## Najważniejsze informacje (na podstawie tagi_BC.csv)

- **Liczba rekordów**: 125
- **Cel biznesowy (top)**:
  - Wzrost sprzedaży: 43
  - Kontrola jakości: 33
  - NPS: 14
  - Poprawa wskaźników jakościowych FCR/NPS/Sat NET: 11
- **KPI (top)**:
  - Quality Score / Missed Information Rate: 34
  - SR / SV (sprzedaż): 33
  - (brak): 21, NPS: 14
- **Zespoły (top)**: ODZ (76), ZRKiWS (25), ZDKwKZ (13)
- **Najczęstsze tagi techniczne**: frazy-binary (92), frazy-ekstrakcja (53), frazy-clustering (44), oraz częściej pojawiające się retrieval/baza-wektorowa i LLM (podsumowania/oceny).

## Standardowe pipeline’y (modułowe, reużywalne)

Poniższe pipeline’y składają się z modułów, które można włączać/wyłączać i konfigurować per-zespół/projekt (konfiguracja jako dane, np. YAML), z kalibracją progów i definicji reguł.

- **A. Klasyfikacja binarna (frazy-binary)**
  - Wejście: transkrypcja, definicja zjawiska (słownik/etykiety), próbki referencyjne
  - Kroki: preprocessing → detekcja/słowniki/ML → kalibracja progów → raport
  - Wyjście: label (0/1), score, explain (trafienia)

- **B. Podwójna klasyfikacja binarna (frazy-binaryx2)**
  - Jak A, ale z dwoma niezależnymi etykietami (np. „sprawa rozwiązana?” i „ofertowanie?”)

- **C. Ekstrakcja + Klasteryzacja fraz (frazy-ekstrakcja, frazy-clustering)**
  - Wejście: transkrypcje; opcjonalnie zbiory słów kluczowych
  - Kroki: ekstrakcja fraz → embeddingi → klasteryzacja → etykietowanie klastrów → ranking przykładów
  - Wyjście: słownik fraz/tematów, przykłady, statystyki

- **D. Retrieval + Baza wektorowa (produkty, oświadczenia, skrypty, tematy)**
  - Wejście: indeks(y) wektorowe + BM25; definicje kolekcji
  - Kroki: embeddingi → wyszukiwanie + reranking → dopasowanie do wzorca → metryki (MRR/Recall@k)
  - Wyjście: dopasowania z uzasadnieniem (passages), trafienia do audytu

- **E. Pair-classification (klient ↔ doradca)**
  - Wejście: pary wypowiedzi (role), definicje relacji/reakcji
  - Kroki: przygotowanie par → model relacji → ocena → agregacja

- **F. LLM scoring/podsumowanie (llm-ocena, llm-podsumowanie)**
  - Wejście: transkrypt + kryteria oceny/opisu
  - Kroki: LLM w pętli HIL (walidacja) → agregacja → stresszczenia narracyjne

- **G. Checklisty/coverage (checklista, llm-ocena-pokrycia)**
  - Wejście: definicje checklist (oświadczenia/procedury)
  - Kroki: dopasowanie (retrieval/regex/LLM) → coverage score → braki

- **H. Audyt zgodności rozmowa ↔ system (system-rozmowa-alignment)**  
  - Wejście: parametry oferty z rozmowy vs logi systemów (prime/af)
  - Kroki: ekstrakcja parametrów → porównanie → raport niezgodności

- **I. Sentyment/emocje w czasie (sentyment-czasowy)**
  - Wejście: transkrypcja z segmentacją (klient/doradca)
  - Kroki: segmentacja → sentyment/emocje per segment → trend/heatmapa

- **J. Novelty/anomalie (novelty-detection)**
  - Wejście: resztowe przypadki po filtrze znanych wzorców
  - Kroki: wektorowe grupowanie → detekcja nowości → kolejka HIL

## Najistotniejsze kejsy (priorytetyzacja biznes + wykonalność)

- **Ofertowanie i CTA (kredyt gotówkowy, karta kredytowa)**  
  Pipeline: A + C + F (opcjonalnie scoring)  
  Wpływ na SR/SV, szybkie wdrożenie, dostępne definicje.

- **Service-to-Sales, cross-sell (np. KK do KG, Select)**  
  Pipeline: B + D (produkty) + E (reakcja doradcy)  
  Wzrost cross-sell, mierzalność per segment/kampania.

- **Obiekcje i retencja (zarządzanie odpowiedziami)**  
  Pipeline: A + C + E + F  
  Redukcja churn, lepsze skrypty i coaching.

- **Checklisty i obowiązki informacyjne (compliance/audyt)**  
  Pipeline: G + D (oświadczenia/skrypty)  
  Minimalizacja ryzyk regulacyjnych, szybkie zwycięstwa.

- **Asysta digital i finalizacja zdalna**  
  Pipeline: A + I (jeśli badamy tok), integracja z KPI procesowymi  
  Zwiększenie adopcji MA/Remote Sales.

- **Dashboardy doradców i narratywne raporty**  
  Pipeline: agregacja metryk + F (narracja)  
  Użyteczne w ciągłym doskonaleniu.

- **Fraudy – nowości i punkty styczne**  
  Pipeline: J + D (indykatory)  
  Wczesne ostrzeganie, materiał do polityk bezpieczeństwa.

## Architektura modułowa (klocki reużywalne)

- **Ingest + Preprocessing**: normalizacja, segmentacja roli, tokenizacja.
- **Detektory**: binary (A/B), pair-classification (E), sentyment/emocje (I).
- **Ekstraktory/Tematy**: frazy-ekstrakcja + clustering (C).
- **Wyszukiwarka/KB**: wektorowe kolekcje produktów, oświadczeń, skryptów, tematów (D).
- **Ocena LLM/Podsumowania**: moduł F ze standaryzowanymi promptami/kryteriami.
- **Checklisty/Audyt**: moduł G (coverage) i H (alignment z systemami).
- **Novelty**: moduł J z kolejką HIL i akceptacją do słownika.
- **Warstwa konfiguracyjna**: „config-as-data” (kolekcje, progi, słowniki) per-zespół.
- **Ocena i monitoring**: metryki jakości (precision/recall/F1, calibration), metryki biznesowe (SR/SV/NPS), drift.
- **Artefakty wyjściowe**: `tagi_BC.csv`, `legenda.csv`, `pivot.csv`, dashboardy.

## Roadmapa (3/6/12 miesięcy)

### 0–3 miesiące (MVP i fundamenty)
- Standaryzacja tagów i taksonomii (słownik tagów technicznych + mapowania).
- Budowa modułów bazowych: A (binary), C (ekstrakcja+clustering), D (wektorowe KB), F (LLM podsumowania – light), G (checklisty).
- POC-y na 2–3 kejsach o najwyższym wpływie (Ofertowanie/CTA, Compliance checklisty, Asysta digital).  
  Kalibracja progów, metryki bazowe, raporty w `pivot.csv` + prosty dashboard.
- Operacyjnie: repo na konfiguracje per-zespół (YAML), joby wsadowe, audyt śladów (explanations, trafienia).

### 3–6 miesięcy (skalowanie i adaptacja)
- Dodanie E (pair-classification), H (alignment rozmowa↔system), I (sentyment w czasie), J (novelty + HIL).
- Rozszerzenie KB (produkty, oświadczenia, skrypty, tematy) + metryki IR (Recall@k/MRR); wersjonowanie indeksów.
- Rolling rollout do zespołów ODZ, ZRKiWS, ZDKwKZ; szablony konfiguracji i playbook kalibracji.
- Automatyczne generowanie `legenda.csv` i raportów narracyjnych (F) do cyklicznego przeglądu.

### 6–12 miesięcy (produkcyjna skalowalność, self‑service)
- Warstwa self‑service: UI do konfiguracji/kontroli progów, selekcji kolekcji KB, podglądu trafień i audytu.
- MLOps: rejestr modeli/indeksów, CI/CD eksperymentów, monitoring jakości/driftu, A/B testy na kejsach sprzedażowych.
- Multi‑kanał: rozszerzenie na czat/e‑mail/video; integracje z CRM do oceny efektu (uplift, konwersje).
- Governance: polityki danych/retencji, RODO, wyjaśnialność (explainability) i rejestrowanie decyzji.

## Dodatkowe zalecenia wdrożeniowe

- Utrzymywać „konfigurację jako dane” (kolekcje, słowniki, reguły, progi), aby każdy zespół mógł adaptować i kalibrować moduły.
- W każdym kejsie zapewnić pakiet metryk: techniczne (P/R/F1, coverage), produktowe (czas do wartości), biznesowe (SR/SV/NPS/SL).
- Wprowadzić cykl HIL (Human‑in‑the‑Loop): kolejka kandydatów do przeglądu, szybkie poprawki słowników i progów.
- Dbać o spójność tagów: systematycznie aktualizować `legenda.csv` i mapowania – automatyzować normalizację.