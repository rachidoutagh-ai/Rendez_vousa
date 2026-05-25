import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date, datetime
import re

class ApplicationRendezVous:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Système de Gestion des Rendez-vous")
        self.fenetre.geometry("1100x700")
        self.fenetre.configure(bg="#f0f8ff")  
        self.fenetre.minsize(1000, 650)

       
        self.conn = sqlite3.connect("rendez_vous.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        
        self.nom_var = tk.StringVar()
        self.tel_var = tk.StringVar()
        self.jour_var = tk.StringVar(value=f"{date.today().day:02d}")
        self.mois_var = tk.StringVar(value=f"{date.today().month:02d}")
        self.annee_var = tk.StringVar(value=str(date.today().year))
        self.heure_var = tk.StringVar(value=self.get_next_half_hour())
        self.motif_var = tk.StringVar()
        self.selected_item = None

    
        self.create_header()
        self.create_form()
        self.create_buttons()
        self.create_table_view()
        self.afficher_rdv()

    def create_header(self):
        header = tk.Frame(self.fenetre, bg="#1e88e5", height=70)
        header.pack(fill="x", padx=10, pady=5)
        
        title = tk.Label(
            header, 
            text="Système de Gestion des Rendez-vous", 
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#1e88e5"
        )
        title.pack(pady=10)

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rendez_vous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            tel TEXT NOT NULL,
            date TEXT NOT NULL,
            heure TEXT NOT NULL,
            motif TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def get_next_half_hour(self):
        """Returns the next half-hour slot from current time"""
        now = datetime.now()
        minutes = now.minute
        if minutes < 30:
            next_time = now.replace(minute=30, second=0, microsecond=0)
        else:
            next_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
        
        
        if next_time.hour == 24:
            next_time = next_time.replace(hour=0)
            
        return next_time.strftime("%H:%M")

    def create_form(self):
        frame_form = tk.LabelFrame(
            self.fenetre, 
            text=" Détails du Rendez-vous ", 
            bg="#f0f8ff", 
            font=("Arial", 10, "bold"),
            padx=15, 
            pady=15,
            relief="groove",
            bd=2
        )
        frame_form.pack(pady=10, padx=20, fill="x")

        
        tk.Label(frame_form, text="Nom complet:", bg="#f0f8ff", font=("Arial", 9)).grid(
            row=0, column=0, sticky="e", padx=5, pady=8
        )
        nom_entry = tk.Entry(
            frame_form, 
            textvariable=self.nom_var, 
            width=35,
            font=("Arial", 10),
            relief="solid",
            bd=1
        )
        nom_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        nom_entry.focus_set()

        
        tk.Label(frame_form, text="Téléphone:", bg="#f0f8ff", font=("Arial", 9)).grid(
            row=0, column=2, sticky="e", padx=15, pady=8
        )

       
        tel_entry = tk.Entry(
            frame_form, 
            textvariable=self.tel_var, 
            width=20,
            font=("Arial", 10),
            relief="solid",
            bd=1
        )
        tel_entry.grid(row=0, column=3, padx=5, pady=8, sticky="w")

       
        tk.Label(frame_form, text="Date:", bg="#f0f8ff", font=("Arial", 9)).grid(
            row=1, column=0, sticky="e", padx=5, pady=8
        )
        
        date_frame = tk.Frame(frame_form, bg="#f0f8ff")
        date_frame.grid(row=1, column=1, sticky="w", pady=8)
        
        jours = [f"{i:02d}" for i in range(1, 32)]
        mois = [f"{i:02d}" for i in range(1, 13)]
        annees = [str(i) for i in range(date.today().year, date.today().year + 3)]
        
        jour_cb = ttk.Combobox(
            date_frame, 
            textvariable=self.jour_var, 
            values=jours, 
            width=4,
            state="readonly",
            font=("Arial", 10)
        )
        jour_cb.pack(side="left", padx=2)
        
        mois_cb = ttk.Combobox(
            date_frame, 
            textvariable=self.mois_var, 
            values=mois, 
            width=4,
            state="readonly",
            font=("Arial", 10)
        )
        mois_cb.pack(side="left", padx=2)
        
        annee_cb = ttk.Combobox(
            date_frame, 
            textvariable=self.annee_var, 
            values=annees, 
            width=6,
            state="readonly",
            font=("Arial", 10)
        )
        annee_cb.pack(side="left", padx=2)

        
        tk.Label(frame_form, text="Heure:", bg="#f0f8ff", font=("Arial", 9)).grid(
            row=1, column=2, sticky="e", padx=15, pady=8
        )
        
        heures_24h = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in (0, 30)]
        heure_cb = ttk.Combobox(
            frame_form, 
            textvariable=self.heure_var, 
            values=heures_24h, 
            width=10,
            state="readonly",
            font=("Arial", 10)
        )
        heure_cb.grid(row=1, column=3, sticky="w", pady=8)

     
        tk.Label(frame_form, text="Motif:", bg="#f0f8ff", font=("Arial", 9)).grid(
            row=2, column=0, sticky="e", padx=5, pady=8
        )
        
        self.liste_motifs = [
            "Médecin généraliste", "Spécialiste", "Urgence", 
            "Radiologie", "Contrôle de routine", "Vaccination", 
            "Bilan de santé", "Analyses de sang", "Radiographie"
        ]
        motif_cb = ttk.Combobox(
            frame_form, 
            textvariable=self.motif_var, 
            values=self.liste_motifs, 
            width=32,
            state="readonly",
            font=("Arial", 10)
        )
        motif_cb.grid(row=2, column=1, sticky="w", pady=8, columnspan=2)
        motif_cb.set("Sélectionnez un motif")

    def create_buttons(self):
        frame_btn = tk.Frame(self.fenetre, bg="#f0f8ff")
        frame_btn.pack(pady=12)
        
        button_style = {
            "font": ("Arial", 10, "bold"),
            "width": 11,
            "height": 1,
            "bd": 0,
            "relief": "flat"
        }
        
        buttons = [
            ("Nouveau", "#4caf50", self.clear_fields),
            ("Ajouter", "#2196f3", self.ajouter_rdv),
            ("Modifier", "#ff9800", self.modifier_rdv),
            ("Supprimer", "#f44336", self.supprimer_rdv),
            ("Actualiser", "#9c27b0", self.afficher_rdv),
            ("Quitter", "#757575", self.quit_app)
        ]
        
        for i, (text, color, cmd) in enumerate(buttons):
            btn = tk.Button(
                frame_btn, 
                text=text,
                bg=color,
                fg="white",
                command=cmd,
                **button_style
            )
            btn.grid(row=0, column=i, padx=8, pady=5)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self.darken_color(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

    def darken_color(self, hex_color):
        """Darken a hex color by 20%"""
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        darkened = [max(0, int(c * 0.8)) for c in rgb]
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def create_table_view(self):
        frame_table = tk.Frame(self.fenetre, bg="#f0f8ff")
        frame_table.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        
        scrollbar_y = ttk.Scrollbar(frame_table)
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = ttk.Scrollbar(frame_table, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e3f2fd")
        style.configure("Treeview", font=("Arial", 9), rowheight=25)
        
        self.tree = ttk.Treeview(
            frame_table,
            columns=("id", "nom", "tel", "date", "heure", "motif"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            selectmode="browse"
        )
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nom", text="Nom Complet")
        self.tree.heading("tel", text="Téléphone")
        self.tree.heading("date", text="Date (JJ/MM/AAAA)")
        self.tree.heading("heure", text="Heure")
        self.tree.heading("motif", text="Motif")
        
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nom", width=200, anchor="w")
        self.tree.column("tel", width=120, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("heure", width=80, anchor="center")
        self.tree.column("motif", width=300, anchor="w")
        
        self.tree.pack(fill="both", expand=True)
        
    
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self.modifier_rdv() if self.selected_item else None)

    def get_full_date(self):
        return f"{self.annee_var.get()}-{self.mois_var.get()}-{self.jour_var.get()}"

    def iso_to_display(self, iso_date):
        """Convert ISO date (YYYY-MM-DD) to DD/MM/YYYY format"""
        try:
            parts = iso_date.split('-')
            if len(parts) == 3:
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
        except:
            pass
        return iso_date

    def validate_phone(self, phone):
        """Validate French phone number format"""
        cleaned = re.sub(r'\D', '', phone)
        if len(cleaned) < 10:
            return False
        
        valid_prefixes = ['05', '06', '07', ]
        return cleaned[:2] in valid_prefixes

    def ajouter_rdv(self):
       
        if not self.nom_var.get().strip():
            messagebox.showerror("Erreur", "Le nom est obligatoire")
            return
            
        if not self.validate_phone(self.tel_var.get()):
            messagebox.showerror("Erreur", "Numéro de téléphone invalide")
            return
            
        if self.motif_var.get() == "Sélectionnez un motif" or not self.motif_var.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un motif")
            return
        
       
        full_date = self.get_full_date()
        self.cursor.execute("""
            SELECT COUNT(*) FROM rendez_vous 
            WHERE date = ? AND heure = ?
        """, (full_date, self.heure_var.get()))
        
        if self.cursor.fetchone()[0] > 0:
            if not messagebox.askyesno("Attention", 
                "Un rendez-vous existe déjà à cette date et heure.\nVoulez-vous le remplacer ?"):
                return
        
      
        self.cursor.execute("""
            INSERT INTO rendez_vous (nom, tel, date, heure, motif) 
            VALUES (?, ?, ?, ?, ?)
        """, (
            self.nom_var.get().strip(),
            self.tel_var.get().strip(),
            full_date,
            self.heure_var.get(),
            self.motif_var.get()
        ))
        self.conn.commit()
        
        messagebox.showinfo("Succès", "Rendez-vous ajouté avec succès !")
        self.afficher_rdv()
        self.clear_fields()
        self.tree.yview_moveto(1)  

    def afficher_rdv(self):
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
       
        self.cursor.execute("""
            SELECT * FROM rendez_vous 
            ORDER BY date DESC, heure DESC
        """)
        
        for row in self.cursor.fetchall():
            
            display_date = self.iso_to_display(row[3])
            self.tree.insert("", "end", values=(
                row[0],
                row[1],
                row[2],
                display_date,
                row[4],
                row[5]
            ))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            self.selected_item = None
            return
            
        self.selected_item = selected[0]
        values = self.tree.item(self.selected_item)["values"]
        
        if not values:
            return
            
        
        self.nom_var.set(values[1])
        self.tel_var.set(values[2])
        
        
        date_parts = values[3].split('/')
        if len(date_parts) == 3:
            self.jour_var.set(date_parts[0])
            self.mois_var.set(date_parts[1])
            self.annee_var.set(date_parts[2])
        
        self.heure_var.set(values[4])
        self.motif_var.set(values[5])

    def supprimer_rdv(self):
        if not self.selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous à supprimer")
            return
            
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce rendez-vous ?"):
            rdv_id = self.tree.item(self.selected_item)["values"][0]
            self.cursor.execute("DELETE FROM rendez_vous WHERE id=?", (rdv_id,))
            self.conn.commit()
            self.afficher_rdv()
            self.clear_fields()
            messagebox.showinfo("Succès", "Rendez-vous supprimé avec succès !")

    def modifier_rdv(self):
        if not self.selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous à modifier")
            return
        if not self.nom_var.get().strip():
            messagebox.showerror("Erreur", "Le nom est obligatoire")
            return
            
        if not self.validate_phone(self.tel_var.get()):
            messagebox.showerror("Erreur", "Numéro de téléphone invalide")
            return
            
        if self.motif_var.get() == "Sélectionnez un motif" or not self.motif_var.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un motif")
            return
        
       
        rdv_id = self.tree.item(self.selected_item)["values"][0]
        full_date = self.get_full_date()
        
       
        self.cursor.execute("""
            UPDATE rendez_vous 
            SET nom=?, tel=?, date=?, heure=?, motif=? 
            WHERE id=?
        """, (
            self.nom_var.get().strip(),
            self.tel_var.get().strip(),
            full_date,
            self.heure_var.get(),
            self.motif_var.get(),
            rdv_id
        ))
        self.conn.commit()
        
        messagebox.showinfo("Succès", "Rendez-vous mis à jour avec succès !")
        self.afficher_rdv()
        self.clear_fields()

    def clear_fields(self):
        self.nom_var.set("")
        self.tel_var.set("")
        self.motif_var.set("Sélectionnez un motif")
        self.jour_var.set(f"{date.today().day:02d}")
        self.mois_var.set(f"{date.today().month:02d}")
        self.annee_var.set(str(date.today().year))
        self.heure_var.set(self.get_next_half_hour())
        self.selected_item = None

    def quit_app(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment quitter l'application ?"):
            self.conn.close()
            self.fenetre.destroy()

if __name__ == "__main__":
    fenetre = tk.Tk()
    app = ApplicationRendezVous(fenetre)
    fenetre.mainloop()