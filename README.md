# opaceval
OPAC評価の実験


テストの実行
----

```bash
poetry install
poetry run python test.py
```

2021/3/27の実行結果
----
|        | Enju  | CALIL(ISBN) | CALIL(TSV) |
|--------|-------|-------------|------------|
| Recall | 0.880 | 1.000       | 1.000      |
| MRR    | 0.696 | 0.707       | 0.740      |