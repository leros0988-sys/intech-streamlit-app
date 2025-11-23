import pandas as pd
import io

def generate_bill(bill_df, save_path="대금청구서.xlsx"):
    bill_df.to_excel(save_path, index=False)
    return save_path

def generate_document(doc_df, save_path="기안자료.xlsx"):
    doc_df.to_excel(save_path, index=False)
    return save_path

