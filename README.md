# ftree.py

Simple CLI tool to parse tree-structured CSV data and display it as an ASCII table, with an added `nodes` column showing the number of child branches for each node.

## 🔧 Usage

```bash
python ftree.py <csv_file> -d column1,column2,...
```

- `-d` specifies hierarchy columns (top to bottom).
- Only one of the hierarchy columns is filled per row.

## 📄 Example

**Input (data.csv):**
```csv
a,b,c
1,,i
,1.1,x
,1.2,y
```

**Command:**
```bash
python ftree.py data.csv -d a,b
```

**Output:**
```
a | b   | c  | nodes
1 |     | i  | 2
  | 1.1 | x  |
  | 1.2 | y  |
```

## ✅ Notes

- No external dependencies.
- `nodes` column must not exist in input.
