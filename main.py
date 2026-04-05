import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import os
import sys
from pathlib import Path

class IconGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur d'icônes PWA - Luxious Beautyland")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Couleurs du thème
        self.colors = {
            'bg': '#f0f0f0',
            'primary': '#EC4899',
            'secondary': '#F472B6',
            'dark': '#1F2937',
            'light': '#F9FAFB'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Variables
        self.source_image = None
        self.output_dir = None
        
        # Tailles d'icônes requises pour la PWA
        self.icon_sizes = [
            (16, 16, "favicon-16x16.png"),
            (32, 32, "favicon-32x32.png"),
            (72, 72, "icon-72x72.png"),
            (96, 96, "icon-96x96.png"),
            (128, 128, "icon-128x128.png"),
            (144, 144, "icon-144x144.png"),
            (152, 152, "icon-152x152.png"),
            (180, 180, "apple-icon-180x180.png"),
            (192, 192, "icon-192x192.png"),
            (384, 384, "icon-384x384.png"),
            (512, 512, "icon-512x512.png"),
        ]
        
        # Tailles Apple Touch Icons
        self.apple_sizes = [
            (57, 57, "apple-icon-57x57.png"),
            (60, 60, "apple-icon-60x60.png"),
            (72, 72, "apple-icon-72x72.png"),
            (76, 76, "apple-icon-76x76.png"),
            (114, 114, "apple-icon-114x114.png"),
            (120, 120, "apple-icon-120x120.png"),
            (144, 144, "apple-icon-144x144.png"),
            (152, 152, "apple-icon-152x152.png"),
            (180, 180, "apple-icon-180x180.png"),
        ]
        
        # Autres icônes nécessaires
        self.other_icons = [
            (96, 96, "shortcut-product.png"),
            (96, 96, "shortcut-services.png"),
            (96, 96, "shortcut-contact.png"),
            (192, 192, "badge.png"),
            (1200, 630, "og-default.jpg"),
            (1280, 720, "screenshot-1.jpg"),
            (1280, 720, "screenshot-2.jpg"),
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # En-tête
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        header_frame.pack(fill='x')
        
        title_label = tk.Label(
            header_frame,
            text="🎨 Générateur d'icônes PWA",
            font=('Poppins', 18, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        )
        title_label.pack(expand=True, pady=10)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Section image source
        source_frame = tk.LabelFrame(
            main_frame,
            text="📁 Image source",
            font=('Poppins', 10, 'bold'),
            bg=self.colors['bg'],
            padx=10,
            pady=10
        )
        source_frame.pack(fill='x', pady=(0, 10))
        
        self.source_label = tk.Label(
            source_frame,
            text="Aucune image sélectionnée",
            font=('Poppins', 9),
            bg=self.colors['light'],
            relief='solid',
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.source_label.pack(fill='x', pady=(0, 10))
        
        select_btn = tk.Button(
            source_frame,
            text="📂 Choisir une image",
            font=('Poppins', 10),
            bg=self.colors['primary'],
            fg='white',
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.select_source_image
        )
        select_btn.pack()
        
        # Section dossier de sortie
        output_frame = tk.LabelFrame(
            main_frame,
            text="📂 Dossier de sortie",
            font=('Poppins', 10, 'bold'),
            bg=self.colors['bg'],
            padx=10,
            pady=10
        )
        output_frame.pack(fill='x', pady=(0, 10))
        
        self.output_label = tk.Label(
            output_frame,
            text="Aucun dossier sélectionné",
            font=('Poppins', 9),
            bg=self.colors['light'],
            relief='solid',
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.output_label.pack(fill='x', pady=(0, 10))
        
        output_btn = tk.Button(
            output_frame,
            text="📂 Choisir le dossier de sortie",
            font=('Poppins', 10),
            bg=self.colors['secondary'],
            fg='white',
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.select_output_dir
        )
        output_btn.pack()
        
        # Options
        options_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ Options",
            font=('Poppins', 10, 'bold'),
            bg=self.colors['bg'],
            padx=10,
            pady=10
        )
        options_frame.pack(fill='x', pady=(0, 10))
        
        self.generate_favicons_var = tk.BooleanVar(value=True)
        favicons_check = tk.Checkbutton(
            options_frame,
            text="Générer les favicons (16x16, 32x32)",
            variable=self.generate_favicons_var,
            font=('Poppins', 9),
            bg=self.colors['bg']
        )
        favicons_check.pack(anchor='w')
        
        self.generate_pwa_var = tk.BooleanVar(value=True)
        pwa_check = tk.Checkbutton(
            options_frame,
            text="Générer les icônes PWA (72x72 à 512x512)",
            variable=self.generate_pwa_var,
            font=('Poppins', 9),
            bg=self.colors['bg']
        )
        pwa_check.pack(anchor='w')
        
        self.generate_apple_var = tk.BooleanVar(value=True)
        apple_check = tk.Checkbutton(
            options_frame,
            text="Générer les Apple Touch Icons",
            variable=self.generate_apple_var,
            font=('Poppins', 9),
            bg=self.colors['bg']
        )
        apple_check.pack(anchor='w')
        
        self.generate_other_var = tk.BooleanVar(value=True)
        other_check = tk.Checkbutton(
            options_frame,
            text="Générer les autres icônes (shortcuts, badge, etc.)",
            variable=self.generate_other_var,
            font=('Poppins', 9),
            bg=self.colors['bg']
        )
        other_check.pack(anchor='w')
        
        self.optimize_var = tk.BooleanVar(value=True)
        optimize_check = tk.Checkbutton(
            options_frame,
            text="Optimiser les images (réduire la taille)",
            variable=self.optimize_var,
            font=('Poppins', 9),
            bg=self.colors['bg']
        )
        optimize_check.pack(anchor='w')
        
        # Barre de progression
        progress_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        progress_frame.pack(fill='x', pady=(0, 10))
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Prêt à générer",
            font=('Poppins', 9),
            bg=self.colors['bg']
        )
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=500
        )
        self.progress_bar.pack(fill='x', pady=(5, 0))
        
        # Bouton générer
        generate_btn = tk.Button(
            main_frame,
            text="🚀 Générer toutes les icônes",
            font=('Poppins', 12, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            padx=30,
            pady=12,
            relief='flat',
            cursor='hand2',
            command=self.generate_all_icons
        )
        generate_btn.pack(pady=(10, 0))
        
        # Message de statut
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=('Poppins', 9),
            bg=self.colors['bg'],
            fg=self.colors['primary'],
            wraplength=500
        )
        self.status_label.pack(pady=(10, 0))
        
    def select_source_image(self):
        filetypes = [
            ("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("Tous les fichiers", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Choisir une image source",
            filetypes=filetypes
        )
        
        if filename:
            self.source_image = filename
            basename = os.path.basename(filename)
            self.source_label.config(
                text=f"✓ {basename}",
                fg='green'
            )
            self.update_status(f"Image chargée : {basename}")
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(
            title="Choisir le dossier de sortie"
        )
        
        if directory:
            self.output_dir = directory
            self.output_label.config(
                text=f"📁 {directory}",
                fg='green'
            )
            
            # Créer le sous-dossier images
            images_dir = os.path.join(directory, 'images')
            os.makedirs(images_dir, exist_ok=True)
            self.output_dir = images_dir
            self.output_label.config(text=f"📁 {images_dir}")
    
    def generate_icon(self, img, size, filename):
        """Génère une icône à la taille spécifiée"""
        try:
            # Redimensionner l'image
            img_copy = img.copy()
            img_copy.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Créer une nouvelle image avec le fond transparent si nécessaire
            if img_copy.mode != 'RGBA':
                img_copy = img_copy.convert('RGBA')
            
            # Créer une image carrée
            square_img = Image.new('RGBA', size, (255, 255, 255, 0))
            
            # Calculer la position pour centrer
            x = (size[0] - img_copy.width) // 2
            y = (size[1] - img_copy.height) // 2
            
            # Coller l'image redimensionnée
            square_img.paste(img_copy, (x, y), img_copy if img_copy.mode == 'RGBA' else None)
            
            # Optimiser si demandé
            if self.optimize_var.get():
                square_img = square_img.quantize(colors=256)
            
            # Sauvegarder
            output_path = os.path.join(self.output_dir, filename)
            
            if filename.endswith('.jpg'):
                square_img = square_img.convert('RGB')
                square_img.save(output_path, 'JPEG', quality=85, optimize=True)
            else:
                square_img.save(output_path, 'PNG', optimize=True)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la génération de {filename}: {e}")
            return False
    
    def generate_all_icons(self):
        """Génère toutes les icônes"""
        
        # Vérifications
        if not self.source_image:
            messagebox.showerror(
                "Erreur",
                "Veuillez sélectionner une image source"
            )
            return
        
        if not self.output_dir:
            messagebox.showerror(
                "Erreur",
                "Veuillez sélectionner un dossier de sortie"
            )
            return
        
        try:
            # Charger l'image source
            img = Image.open(self.source_image)
            
            # Calculer le nombre total d'icônes à générer
            total_icons = 0
            if self.generate_favicons_var.get():
                total_icons += 2
            if self.generate_pwa_var.get():
                total_icons += len(self.icon_sizes)
            if self.generate_apple_var.get():
                total_icons += len(self.apple_sizes)
            if self.generate_other_var.get():
                total_icons += len(self.other_icons)
            
            self.progress_bar['maximum'] = total_icons
            self.progress_bar['value'] = 0
            generated = 0
            failed = []
            
            # Générer les favicons
            if self.generate_favicons_var.get():
                favicon_sizes = [
                    (16, 16, "favicon-16x16.png"),
                    (32, 32, "favicon-32x32.png"),
                    (96, 96, "favicon-96x96.png"),
                ]
                for size in favicon_sizes:
                    if self.generate_icon(img, (size[0], size[1]), size[2]):
                        generated += 1
                    else:
                        failed.append(size[2])
                    self.progress_bar['value'] = generated
                    self.progress_bar.update()
                    self.progress_label.config(
                        text=f"Génération: {size[2]} ({generated}/{total_icons})"
                    )
                    self.root.update()
            
            # Générer les icônes PWA
            if self.generate_pwa_var.get():
                for size in self.icon_sizes:
                    if self.generate_icon(img, (size[0], size[1]), size[2]):
                        generated += 1
                    else:
                        failed.append(size[2])
                    self.progress_bar['value'] = generated
                    self.progress_bar.update()
                    self.progress_label.config(
                        text=f"Génération: {size[2]} ({generated}/{total_icons})"
                    )
                    self.root.update()
            
            # Générer les Apple Touch Icons
            if self.generate_apple_var.get():
                for size in self.apple_sizes:
                    if self.generate_icon(img, (size[0], size[1]), size[2]):
                        generated += 1
                    else:
                        failed.append(size[2])
                    self.progress_bar['value'] = generated
                    self.progress_bar.update()
                    self.progress_label.config(
                        text=f"Génération: {size[2]} ({generated}/{total_icons})"
                    )
                    self.root.update()
            
            # Générer les autres icônes
            if self.generate_other_var.get():
                for size in self.other_icons:
                    if self.generate_icon(img, (size[0], size[1]), size[2]):
                        generated += 1
                    else:
                        failed.append(size[2])
                    self.progress_bar['value'] = generated
                    self.progress_bar.update()
                    self.progress_label.config(
                        text=f"Génération: {size[2]} ({generated}/{total_icons})"
                    )
                    self.root.update()
            
            # Message de fin
            self.progress_label.config(text="✅ Génération terminée!")
            
            if failed:
                messagebox.showwarning(
                    "Génération partielle",
                    f"{generated} icônes générées avec succès\n"
                    f"{len(failed)} échec(s):\n" + "\n".join(failed[:5])
                )
            else:
                messagebox.showinfo(
                    "Succès",
                    f"✅ {generated} icônes générées avec succès!\n"
                    f"Dossier: {self.output_dir}"
                )
            
            self.update_status(
                f"{generated} icônes générées dans {self.output_dir}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Erreur lors de la génération:\n{str(e)}"
            )
            self.update_status(f"Erreur: {str(e)}", error=True)
    
    def update_status(self, message, error=False):
        self.status_label.config(
            text=message,
            fg='red' if error else self.colors['primary']
        )
        self.root.update()

def main():
    # Vérifier si Pillow est installé
    try:
        from PIL import Image
    except ImportError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Module manquant",
            "Pillow n'est pas installé.\n\n"
            "Installez-le avec:\n"
            "pip install Pillow"
        )
        root.destroy()
        sys.exit(1)
    
    root = tk.Tk()
    app = IconGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()