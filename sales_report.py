import os
import glob
import pandas as pd

REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

def get_latest_report_file():
    files = glob.glob(os.path.join(REPORTS_DIR, "*.xlsx"))

    if not files:
        raise FileNotFoundError(f"В папке {REPORTS_DIR} нет Excel-отчётов.")

    return max(files, key=os.path.getmtime)

def load_sales_report():
    file_path = get_latest_report_file()

    df = pd.read_excel(file_path, header=None)

    header_row = None
    for i, row in df.iterrows():
        values = row.astype(str).str.lower().tolist()
        if "элемент номенклатуры" in values and "количество" in values:
            header_row = i
            break

    if header_row is None:
        raise ValueError("Не найдена строка заголовков в отчёте.")

    df = pd.read_excel(file_path, header=header_row)

    df = df.dropna(how="all")

    return df

def get_column(df, name_part):
    for col in df.columns:
        if name_part.lower() in str(col).lower():
            return col
    raise ValueError(f"Колонка с текстом '{name_part}' не найдена.")

def report_summary():
    df = load_sales_report()

    name_col = get_column(df, "элемент")
    qty_col = get_column(df, "количество")
    revenue_col = get_column(df, "выручка, р")

    df = df[df[name_col].notna()]
    df = df[pd.to_numeric(df[qty_col], errors="coerce").notna()]

    total_revenue = pd.to_numeric(df[revenue_col], errors="coerce").sum()
    total_qty = pd.to_numeric(df[qty_col], errors="coerce").sum()

    return (
        f"Отчёт по продажам:\n\n"
        f"Выручка: {total_revenue:,.0f} ₽\n"
        f"Продано позиций: {total_qty:,.1f}\n"
        f"Позиций в отчёте: {len(df)}"
    ).replace(",", " ")

def top_sales(limit=10):
    df = load_sales_report()

    name_col = get_column(df, "элемент")
    qty_col = get_column(df, "количество")
    revenue_col = get_column(df, "выручка, р")

    df = df[df[name_col].notna()]
    df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce")
    df[revenue_col] = pd.to_numeric(df[revenue_col], errors="coerce")
    df = df.dropna(subset=[qty_col])

    df = df.sort_values(qty_col, ascending=False).head(limit)

    text = "ТОП продаж по количеству:\n\n"

    for i, row in enumerate(df.itertuples(), start=1):
        name = getattr(row, name_col.replace(" ", "_"), None)
        qty = row[df.columns.get_loc(qty_col) + 1]
        revenue = row[df.columns.get_loc(revenue_col) + 1]
        text += f"{i}. {row[df.columns.get_loc(name_col) + 1]} — {qty:g} шт. / {revenue:,.0f} ₽\n"

    return text.replace(",", " ")

def profit_sales(limit=10):
    df = load_sales_report()

    name_col = get_column(df, "элемент")
    profit_col = get_column(df, "валовая прибыль")

    df = df[df[name_col].notna()]
    df[profit_col] = pd.to_numeric(df[profit_col], errors="coerce")
    df = df.dropna(subset=[profit_col])

    df = df.sort_values(profit_col, ascending=False).head(limit)

    text = "Самые прибыльные позиции:\n\n"

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        text += f"{i}. {row[name_col]} — {row[profit_col]:,.0f} ₽\n"

    return text.replace(",", " ")

def worst_sales(limit=10):
    df = load_sales_report()

    name_col = get_column(df, "элемент")
    qty_col = get_column(df, "количество")
    revenue_col = get_column(df, "выручка, р")

    df = df[df[name_col].notna()]
    df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce")
    df[revenue_col] = pd.to_numeric(df[revenue_col], errors="coerce")
    df = df.dropna(subset=[qty_col])

    df = df.sort_values(qty_col, ascending=True).head(limit)

    text = "Слабые продажи:\n\n"

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        text += f"{i}. {row[name_col]} — {row[qty_col]:g} шт. / {row[revenue_col]:,.0f} ₽\n"

    return text.replace(",", " ")

def sales_analysis():
    return (
        report_summary()
        + "\n\n"
        + top_sales(5)
        + "\n"
        + profit_sales(5)
        + "\n"
        + worst_sales(5)
    )




