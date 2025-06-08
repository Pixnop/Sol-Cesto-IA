#!/usr/bin/env python3
"""
Script pour lancer tous les tests du projet Sol Cesto IA
"""

import sys
import os
import unittest
import time
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_all_tests():
    """Lance tous les tests unitaires"""
    print("=" * 70)
    print("🧪 SOL CESTO IA - LANCEMENT DES TESTS")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Découverte automatique des tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Compter les tests
    test_count = suite.countTestCases()
    print(f"📊 Nombre de tests trouvés: {test_count}")
    print()
    
    # Lancer les tests avec un runner détaillé
    runner = unittest.TextTestRunner(verbosity=2)
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Résumé des résultats
    print("\n" + "=" * 70)
    print("📈 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    print(f"⏱️  Temps d'exécution: {end_time - start_time:.2f} secondes")
    print(f"✅ Tests réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests échoués: {len(result.failures)}")
    print(f"💥 Erreurs: {len(result.errors)}")
    print(f"⏭️  Tests ignorés: {len(result.skipped)}")
    
    # Détails des échecs
    if result.failures:
        print("\n❌ DÉTAILS DES ÉCHECS:")
        for test, traceback in result.failures:
            print(f"\n- {test}")
            print(f"  {traceback}")
    
    # Détails des erreurs
    if result.errors:
        print("\n💥 DÉTAILS DES ERREURS:")
        for test, traceback in result.errors:
            print(f"\n- {test}")
            print(f"  {traceback}")
    
    # Code de sortie
    success = result.wasSuccessful()
    
    if success:
        print("\n✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS! 🎉")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ!")
    
    return 0 if success else 1


def run_specific_test_module(module_name):
    """Lance un module de test spécifique"""
    print(f"🧪 Lancement des tests du module: {module_name}")
    
    try:
        # Importer et lancer le module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(f'tests.unit.{module_name}')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement du module: {e}")
        return 1


def run_coverage_tests():
    """Lance les tests avec analyse de couverture (nécessite coverage)"""
    try:
        import coverage
        
        print("📊 Lancement des tests avec analyse de couverture...")
        
        # Configurer coverage
        cov = coverage.Coverage(source=['sol_cesto'])
        cov.start()
        
        # Lancer les tests
        loader = unittest.TestLoader()
        suite = loader.discover('tests', pattern='test_*.py')
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        # Arrêter et générer le rapport
        cov.stop()
        cov.save()
        
        print("\n📊 RAPPORT DE COUVERTURE:")
        cov.report()
        
        # Générer un rapport HTML
        cov.html_report(directory='htmlcov')
        print("\n📄 Rapport HTML généré dans: htmlcov/index.html")
        
        return 0 if result.wasSuccessful() else 1
        
    except ImportError:
        print("⚠️  Le module 'coverage' n'est pas installé.")
        print("   Installez-le avec: pip install coverage")
        return 1


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lancer les tests Sol Cesto IA')
    parser.add_argument('--module', '-m', help='Module de test spécifique à lancer')
    parser.add_argument('--coverage', '-c', action='store_true', 
                        help='Lancer avec analyse de couverture')
    
    args = parser.parse_args()
    
    if args.coverage:
        return run_coverage_tests()
    elif args.module:
        return run_specific_test_module(args.module)
    else:
        return run_all_tests()


if __name__ == '__main__':
    sys.exit(main())