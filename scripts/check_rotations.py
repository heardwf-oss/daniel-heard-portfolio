"""Check PDF page rotations to find upside-down documents."""
import os
import sys

PDF_DIR = r"C:\Users\heard\OneDrive\Documents\daniel-heard-engineering-portfolio\pdfs\source"
FIX_DIR = r"C:\Users\heard\OneDrive\Documents\daniel-heard-engineering-portfolio\pdfs\source"

def check_all():
    try:
        import fitz
        print("Using pymupdf (fitz)")
    except ImportError:
        print("pymupdf not available, trying pypdf")
        try:
            from pypdf import PdfReader
        except ImportError:
            print("Neither pymupdf nor pypdf available")
            sys.exit(1)
        check_with_pypdf()
        return
    
    results = {}
    for fname in sorted(os.listdir(PDF_DIR)):
        if not fname.endswith('.pdf'):
            continue
        fpath = os.path.join(PDF_DIR, fname)
        try:
            doc = fitz.open(fpath)
            rotations = [page.rotation for page in doc]
            if any(r != 0 for r in rotations):
                results[fname] = rotations
                print(f"ROTATED: {fname}")
                print(f"  Rotations: {rotations[:10]}{'...' if len(rotations) > 10 else ''}")
            else:
                print(f"ok: {fname}")
            doc.close()
        except Exception as e:
            print(f"ERROR: {fname}: {e}")
    
    return results

def check_with_pypdf():
    from pypdf import PdfReader
    for fname in sorted(os.listdir(PDF_DIR)):
        if not fname.endswith('.pdf'):
            continue
        fpath = os.path.join(PDF_DIR, fname)
        try:
            reader = PdfReader(fpath)
            rotations = []
            for page in reader.pages:
                rot = page.get('/Rotate', 0) or 0
                rotations.append(int(rot))
            if any(r != 0 for r in rotations):
                print(f"ROTATED: {fname}")
                print(f"  Rotations: {rotations[:10]}{'...' if len(rotations) > 10 else ''}")
            else:
                print(f"ok: {fname}")
        except Exception as e:
            print(f"ERROR {fname}: {e}")

if __name__ == "__main__":
    check_all()
