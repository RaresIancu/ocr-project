import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

tesseract_path = os.path.join(BASE_DIR, "tesseract", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = tesseract_path
os.environ['TESSDATA_PREFIX'] = os.path.join(BASE_DIR, "tesseract", "tessdata")

root = None
output_text = None
lang_var = None


def ocr_image(image_path, lang='ron'):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, lang=lang)


def ocr_folder(folder_path, lang='ron'):
    results = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            path = os.path.join(folder_path, filename)
            print(f"Procesare {filename}...")
            ocr_result = ocr_image(path, lang=lang)
            results[filename] = ocr_result
    return results


def ocr_pdf(pdf_path, lang='ron'):
    images = convert_from_path(pdf_path, dpi=300)
    full_text = ""
    for i, img in enumerate(images):
        print(f"Pagina {i+1}...")
        page_text = pytesseract.image_to_string(img, lang=lang)
        full_text += f"\n--- Pagina {i+1} ---\n{page_text}"
    return full_text


def select_file_gui():
    file_path = filedialog.askopenfilename(
        filetypes=[("Imagini sau PDF", "*.png *.jpg *.jpeg *.tiff *.pdf")]
    )
    if file_path:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Se procesează...\n")
        root.update()
        try:
            if file_path.lower().endswith('.pdf'):
                result = ocr_pdf(file_path)
            else:
                result = ocr_image(file_path)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o problemă:\n{e}")


def porneste_gui():
    global root, output_text, lang_var
    root = tk.Tk()
    root.title("OCR Interfață - Imagine & PDF")
    root.geometry("1000x800")

    lang_var = tk.StringVar(value='ron')

    btn = tk.Button(root, text="Selectează imagine sau PDF", command=select_file_gui, font=("Arial", 12))
    btn.pack(pady=10)

    output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11))
    output_text.pack(expand=True, fill='both', padx=10, pady=10)

    btn_salveaza = tk.Button(root, text="Salvează text OCR în fișier", command=salveaza_text_ocr, font=("Arial", 11))
    btn_salveaza.pack(pady=5)

    btn_folder = tk.Button(root, text="OCR pe un întreg folder", command=selecteaza_folder_gui, font=("Arial", 11))
    btn_folder.pack(pady=5)

    lang_var = tk.StringVar(value='ron')  # implicit română

    frame_lang = tk.Frame(root)
    frame_lang.pack(pady=5)

    tk.Label(frame_lang, text="Limba OCR:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
    lang_menu = tk.OptionMenu(frame_lang, lang_var, "ron", "eng", "deu", "fra", "ita", "spa")
    lang_menu.pack(side=tk.LEFT)

    root.mainloop()


def salveaza_text_ocr():
    content = output_text.get(1.0, tk.END).strip()
    if not content:
        messagebox.showwarning("Atenție", "Nu există text de salvat.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Fișiere text", "*.txt")],
        title="Salvează rezultatul OCR"
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Succes", f"Textul a fost salvat în:\n{file_path}")


def selecteaza_folder_gui():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Se procesează folderul...\n")
        root.update()
        try:
            lang = lang_var.get()
            results = ocr_folder(folder_path, lang=lang)
            output_text.delete(1.0, tk.END)
            for file_name, text_result in results.items():
                output_text.insert(tk.END, f"\n--- {file_name} ---\n{text_result}\n")
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o problemă:\n{e}")


if __name__ == "__main__":
    porneste_gui()
