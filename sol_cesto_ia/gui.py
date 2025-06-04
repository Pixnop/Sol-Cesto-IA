import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from PIL import Image, ImageTk
import os
from .analyzer_v2 import GameAnalyzerV2 as GameAnalyzer
from .recommender import MoveRecommender


class SolCestoGUI:
    """Interface graphique pour l'IA Sol Cesto."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sol Cesto IA - Assistant de jeu")
        self.root.geometry("800x600")
        
        self.analyzer = GameAnalyzer()
        self.recommender = MoveRecommender()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        style = ttk.Style()
        style.theme_use('default')
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        ttk.Label(main_frame, text="Sol Cesto IA", 
                 font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)
        
        ttk.Button(main_frame, text="Charger capture d'écran", 
                  command=self.charger_image).grid(row=1, column=0, pady=5)
        
        self.label_fichier = ttk.Label(main_frame, text="Aucun fichier chargé")
        self.label_fichier.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        ttk.Button(main_frame, text="Analyser", 
                  command=self.analyser_image).grid(row=1, column=2, pady=5)
        
        self.canvas_frame = ttk.Frame(main_frame)
        self.canvas_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='gray', width=400, height=300)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        result_frame = ttk.LabelFrame(main_frame, text="Résultats", padding="10")
        result_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.text_result = tk.Text(result_frame, height=10, width=70, wrap=tk.WORD)
        self.text_result.pack(fill=tk.BOTH, expand=True)
        
        self.text_result.tag_configure("titre", font=('Arial', 12, 'bold'))
        self.text_result.tag_configure("recommandation", foreground="green", 
                                      font=('Arial', 11, 'bold'))
        self.text_result.tag_configure("danger", foreground="red")
        self.text_result.tag_configure("info", foreground="blue")
        
        self.current_image_path = None
        
    def charger_image(self):
        """Charge une image depuis le système de fichiers."""
        filename = filedialog.askopenfilename(
            title="Sélectionner une capture d'écran",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp"), 
                      ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            self.current_image_path = filename
            self.label_fichier.config(text=os.path.basename(filename))
            self.afficher_image(filename)
            
    def afficher_image(self, filepath):
        """Affiche l'image dans le canvas."""
        try:
            image = Image.open(filepath)
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width <= 1:
                canvas_width = 400
            if canvas_height <= 1:
                canvas_height = 300
                
            image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(image)
            
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                    image=self.photo, anchor=tk.CENTER)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image: {str(e)}")
            
    def analyser_image(self):
        """Lance l'analyse de l'image dans un thread séparé."""
        if not self.current_image_path:
            messagebox.showwarning("Attention", "Veuillez d'abord charger une image")
            return
            
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, "Analyse en cours...\n", "info")
        
        thread = threading.Thread(target=self._analyser_thread)
        thread.daemon = True
        thread.start()
        
    def _analyser_thread(self):
        """Thread d'analyse pour ne pas bloquer l'interface."""
        try:
            etat_jeu = self.analyzer.analyser_capture(self.current_image_path)
            
            resultat = self.recommender.recommander_coup(
                grille=etat_jeu['grille'],
                stats=etat_jeu['stats_joueur'],
                modificateurs=etat_jeu['dents_actives']
            )
            
            self.root.after(0, self._afficher_resultats, etat_jeu, resultat)
            
        except Exception as e:
            self.root.after(0, self._afficher_erreur, str(e))
            
    def _afficher_resultats(self, etat_jeu, resultat):
        """Affiche les résultats de l'analyse."""
        self.text_result.delete(1.0, tk.END)
        
        self.text_result.insert(tk.END, "ÉTAT DU JEU DÉTECTÉ\n", "titre")
        self.text_result.insert(tk.END, f"PV: {etat_jeu['stats_joueur']['pv']} | ")
        self.text_result.insert(tk.END, f"Force: {etat_jeu['stats_joueur']['force']} | ")
        self.text_result.insert(tk.END, f"Magie: {etat_jeu['stats_joueur']['magie']}\n\n")
        
        self.text_result.insert(tk.END, "RECOMMANDATION\n", "titre")
        self.text_result.insert(tk.END, 
                               f"➤ Choisir rangée {resultat['rangee_optimale']}\n", 
                               "recommandation")
        self.text_result.insert(tk.END, f"Raison: {resultat['justification']}\n\n")
        
        self.text_result.insert(tk.END, "ANALYSE DÉTAILLÉE\n", "titre")
        self.text_result.insert(tk.END, f"Gains espérés: {resultat['esperance_gains']:.2f}\n")
        
        if resultat['risque_degats'] > 0:
            self.text_result.insert(tk.END, f"Risque de dégâts: {resultat['risque_degats']:.2f}\n", "danger")
        else:
            self.text_result.insert(tk.END, "Risque de dégâts: 0\n", "info")
            
        self.text_result.insert(tk.END, 
                               f"Probabilité de survie: {resultat['probabilite_survie']:.1%}\n\n")
        
        if 'details_toutes_rangees' in resultat:
            self.text_result.insert(tk.END, "COMPARAISON DES RANGÉES\n", "titre")
            for detail in resultat['details_toutes_rangees']:
                if detail['rangee'] == resultat['rangee_optimale']:
                    self.text_result.insert(tk.END, f"• Rangée {detail['rangee']}: ", "recommandation")
                else:
                    self.text_result.insert(tk.END, f"• Rangée {detail['rangee']}: ")
                self.text_result.insert(tk.END, 
                                       f"Score {detail['score']:.1f}, "
                                       f"Gains {detail['esperance_gains']:.1f}, "
                                       f"Dégâts {detail['esperance_degats']:.1f}\n")
                                       
    def _afficher_erreur(self, message):
        """Affiche un message d'erreur."""
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, "ERREUR\n", "titre")
        self.text_result.insert(tk.END, message, "danger")
        
    def run(self):
        """Lance l'interface graphique."""
        self.root.mainloop()


def main():
    """Point d'entrée pour l'interface graphique."""
    app = SolCestoGUI()
    app.run()


if __name__ == "__main__":
    main()