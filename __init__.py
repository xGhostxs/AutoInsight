"""
AutoInsight - Core Modül Paketi
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AutoInsight Team"

from .loader import DataLoader
from .cleaner import DataCleaner
from .analyzer import DataAnalyzer
from .visualizer import DataVisualizer
from .reporter import ReportGenerator

__all__ = [
    'DataLoader',
    'DataCleaner',
    'DataAnalyzer',
    'DataVisualizer',
    'ReportGenerator'
]

PACKAGE_INFO = {
    'free': {
        'limit_mb': 1,
        'pdf_support': False,
        'multi_file': False,
        'price': 'Free'
    },
    'pro': {
        'limit_mb': 25,
        'pdf_support': True,
        'multi_file': False,
        'price': '$9/month'
    },
    'business': {
        'limit_mb': 200,
        'pdf_support': True,
        'multi_file': True,
        'price': '$29/month'
    }
}

def get_package_info(package_name: str) -> dict:
    """Paket bilgilerini döndürür."""
    return PACKAGE_INFO.get(package_name.lower(), PACKAGE_INFO['free'])

def print_version():
    """Versiyon bilgisini yazdırır."""
    print(f"AutoInsight v{__version__}")
    print(f"Author: {__author__}")