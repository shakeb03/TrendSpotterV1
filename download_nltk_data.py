#!/usr/bin/env python3
"""
Download NLTK Data for Toronto Trendspotter

This script downloads the required NLTK data packages while bypassing SSL verification issues.
Run this script to set up the necessary NLTK resources before running the data preprocessing pipeline.
"""

import nltk
import ssl
import os
import sys

def download_nltk_data():
    """Download required NLTK data packages"""
    print("Downloading NLTK data packages...")
    
    # Try to create an unverified SSL context to bypass certificate issues
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Create a directory for NLTK data
    nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Download the required packages with progress indication
    packages = [
        'stopwords',        # Common stopwords
        'wordnet',          # For lemmatization
        'punkt',            # For tokenization
        'omw-1.4',          # Open Multilingual Wordnet
        'averaged_perceptron_tagger', # For POS tagging
        'maxent_ne_chunker',# For named entity recognition
        'words'             # Common English words
    ]
    
    for package in packages:
        print(f"Downloading {package}...")
        try:
            nltk.download(package, download_dir=nltk_data_dir)
            print(f"Successfully downloaded {package}")
        except Exception as e:
            print(f"Error downloading {package}: {e}")
    
    # Verify downloads
    print("\nVerifying downloads:")
    missing = []
    for package in packages:
        try:
            nltk.data.find(f"tokenizers/{package}" if package == 'punkt' else f"corpora/{package}")
            print(f"✓ {package} is installed")
        except LookupError:
            print(f"✗ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\nWARNING: The following packages are still missing: {', '.join(missing)}")
        print("Try downloading them manually or check your internet connection.")
    else:
        print(f"\nAll required NLTK data packages downloaded to: {nltk_data_dir}")
    
    print("\nNow you can run the data preprocessing pipeline.")

if __name__ == "__main__":
    download_nltk_data()