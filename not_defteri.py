import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font
import os
import json

CONFIG_FILE = "ayarlar.json"

class NotDefteri:
    def __init__(self, root):
        self.root = root
        self.root.title("Not Defteri")
        self.root.geometry("800x600")

        self.current_theme = "light"
        self.current_file = None
        self.autosave_interval = 5000  # 5 saniye
        self.font_family = "Arial"
        self.font_size = 12

        self.load_config()

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=1)

        self.line_numbers = tk.Text(self.main_frame, width=4, padx=4, takefocus=0, border=0, background="#f0f0f0", state='disabled')
        self.line_numbers.pack(side="left", fill="y")

        self.text_area = tk.Text(self.main_frame, wrap="word", undo=True, font=(self.font_family, self.font_size))
        self.text_area.pack(fill="both", expand=1, side="left")

        self.scrollbar = tk.Scrollbar(self.text_area)
        self.scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_area.yview)

        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<MouseWheel>", self.update_line_numbers)

        self.create_menu()
        self.apply_theme()
        self.update_line_numbers()
        self.auto_save()

        if self.current_file:
            self.open_file(self.current_file)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        # Dosya Menüsü
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Yeni", command=self.new_file)
        file_menu.add_command(label="Aç", command=self.open_file_dialog)
        file_menu.add_command(label="Kaydet", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Çık", command=self.root.quit)
        menu_bar.add_cascade(label="Dosya", menu=file_menu)

        # Tema Menüsü
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Aydınlık Tema", command=lambda: self.set_theme("light"))
        theme_menu.add_command(label="Karanlık Tema", command=lambda: self.set_theme("dark"))
        menu_bar.add_cascade(label="Tema", menu=theme_menu)

        # Yazı Tipi Menüsü
        font_menu = tk.Menu(menu_bar, tearoff=0)
        font_menu.add_command(label="Yazı Tipini Değiştir", command=self.change_font)
        menu_bar.add_cascade(label="Yazı Tipi", menu=font_menu)

        # Düzen Menüsü
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Bul ve Değiştir", command=self.find_and_replace)
        menu_bar.add_cascade(label="Düzenle", menu=edit_menu)

        self.root.config(menu=menu_bar)

    def new_file(self):
        if messagebox.askyesno("Yeni Dosya", "Kaydedilmemiş değişiklikler kaybolacak. Emin misin?"):
            self.text_area.delete(1.0, tk.END)
            self.current_file = None

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")])
        if file_path:
            self.open_file(file_path)

    def open_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                self.current_file = file_path
                self.save_config()
                self.update_line_numbers()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def save_file(self):
        if self.current_file:
            file_path = self.current_file
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")])
            if not file_path:
                return
            self.current_file = file_path

        with open(file_path, "w", encoding="utf-8") as file:
            content = self.text_area.get(1.0, tk.END)
            file.write(content)
            messagebox.showinfo("Kaydedildi", "Dosya başarıyla kaydedildi.")
            self.save_config()

    def set_theme(self, theme):
        self.current_theme = theme
        self.apply_theme()
        self.save_config()

    def apply_theme(self):
        if self.current_theme == "dark":
            bg = "#1e1e1e"
            fg = "#ffffff"
            lineno_bg = "#2e2e2e"
        else:
            bg = "#ffffff"
            fg = "#000000"
            lineno_bg = "#f0f0f0"

        self.text_area.config(bg=bg, fg=fg, insertbackground=fg)
        self.line_numbers.config(bg=lineno_bg, fg=fg)

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        line_count = self.text_area.index('end-1c').split('.')[0]
        self.line_numbers.insert(1.0, "\n".join(str(i) for i in range(1, int(line_count))))
        self.line_numbers.config(state='disabled')

    def change_font(self):
        new_font = simpledialog.askstring("Yazı Tipi", "Yazı tipi (örn: Arial):", initialvalue=self.font_family)
        new_size = simpledialog.askinteger("Yazı Boyutu", "Boyut (örn: 12):", initialvalue=self.font_size)
        if new_font and new_size:
            self.font_family = new_font
            self.font_size = new_size
            self.text_area.config(font=(self.font_family, self.font_size))
            self.save_config()

    def find_and_replace(self):
        find = simpledialog.askstring("Bul", "Bulunacak metin:")
        replace = simpledialog.askstring("Değiştir", "Yerine geçecek metin:")
        if find and replace is not None:
            content = self.text_area.get(1.0, tk.END)
            new_content = content.replace(find, replace)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, new_content)

    def auto_save(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as file:
                    content = self.text_area.get(1.0, tk.END)
                    file.write(content)
            except:
                pass
        self.root.after(self.autosave_interval, self.auto_save)

    def save_config(self):
        config = {
            "last_file": self.current_file,
            "theme": self.current_theme,
            "font_family": self.font_family,
            "font_size": self.font_size
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(config, file)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                config = json.load(file)
                self.current_file = config.get("last_file")
                self.current_theme = config.get("theme", "light")
                self.font_family = config.get("font_family", "Arial")
                self.font_size = config.get("font_size", 12)

if __name__ == "__main__":
    root = tk.Tk()
    app = NotDefteri(root)
    root.mainloop()
