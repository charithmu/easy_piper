#!/usr/bin/env python3
"""
Simple script to login to Hugging Face
Run this first before uploading
"""

from huggingface_hub import login

print("=" * 60)
print("HUGGING FACE LOGIN")
print("=" * 60)
print("\nGet your token from: https://huggingface.co/settings/tokens")
print("(Create a new token with 'write' permission if needed)\n")

try:
    login()
    print("\n✓ Login successful!")
    print("You can now run: python3 scripts/upload_to_huggingface.py")
except Exception as e:
    print(f"\n✗ Login failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you have a valid token from https://huggingface.co/settings/tokens")
    print("2. Token must have 'write' permission")
