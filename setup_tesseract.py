"""
Configuration de Tesseract OCR pour Windows
"""
import os
import pytesseract
import platform


def configurer_tesseract():
    """Configure le chemin de Tesseract pour Windows."""
    
    if platform.system() != 'Windows':
        print("Ce script est pour Windows uniquement.")
        return
    
    # Chemins courants d'installation de Tesseract sur Windows
    chemins_possibles = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.environ.get('USERNAME', '')),
        r'C:\tesseract\tesseract.exe'
    ]
    
    # Vérifier si Tesseract est déjà accessible
    try:
        pytesseract.get_tesseract_version()
        print("✓ Tesseract est déjà configuré et accessible!")
        return True
    except:
        print("Tesseract n'est pas accessible. Recherche en cours...")
    
    # Chercher Tesseract dans les chemins courants
    for chemin in chemins_possibles:
        if os.path.exists(chemin):
            print(f"✓ Tesseract trouvé à: {chemin}")
            pytesseract.pytesseract.tesseract_cmd = chemin
            
            # Créer un fichier de configuration
            with open('tesseract_config.py', 'w') as f:
                f.write(f'# Configuration Tesseract pour Windows\n')
                f.write(f'TESSERACT_PATH = r"{chemin}"\n')
            
            print("✓ Configuration sauvegardée dans tesseract_config.py")
            return True
    
    print("\n❌ Tesseract OCR n'a pas été trouvé!")
    print("\nPour installer Tesseract:")
    print("1. Téléchargez depuis: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Installez en notant le chemin d'installation")
    print("3. Relancez ce script ou ajoutez manuellement le chemin")
    
    # Demander le chemin manuellement
    print("\nVous pouvez entrer le chemin manuellement (ou appuyez sur Entrée pour ignorer):")
    chemin_manuel = input("Chemin vers tesseract.exe: ").strip()
    
    if chemin_manuel and os.path.exists(chemin_manuel):
        pytesseract.pytesseract.tesseract_cmd = chemin_manuel
        with open('tesseract_config.py', 'w') as f:
            f.write(f'# Configuration Tesseract pour Windows\n')
            f.write(f'TESSERACT_PATH = r"{chemin_manuel}"\n')
        print("✓ Configuration sauvegardée!")
        return True
    
    return False


if __name__ == "__main__":
    configurer_tesseract()