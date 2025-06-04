"""
Test simple pour vérifier que les modules fonctionnent
"""
try:
    import numpy as np
    print(f"✓ NumPy {np.__version__} installé")
except ImportError as e:
    print(f"✗ Erreur NumPy: {e}")

try:
    import cv2
    print(f"✓ OpenCV {cv2.__version__} installé")
except ImportError as e:
    print(f"✗ Erreur OpenCV: {e}")

try:
    import PIL
    print(f"✓ Pillow {PIL.__version__} installé")
except ImportError as e:
    print(f"✗ Erreur Pillow: {e}")

try:
    import pytesseract
    print("✓ pytesseract installé")
    # Charger la configuration Tesseract si elle existe
    try:
        from tesseract_config import TESSERACT_PATH
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    except:
        pass
    # Tester si Tesseract est accessible
    try:
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR accessible")
    except:
        print("✗ Tesseract OCR non trouvé - exécutez setup_tesseract.py")
except ImportError as e:
    print(f"✗ Erreur pytesseract: {e}")

print("\nSi tout est vert (✓), l'installation est réussie!")