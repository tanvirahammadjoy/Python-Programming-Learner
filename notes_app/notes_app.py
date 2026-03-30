#!/usr/bin/env python3
"""
Simple Notes App - CLI Notes Manager
A command-line application to manage text notes with persistent storage
"""

import os
from datetime import datetime

# Constants
NOTES_FILE = "notes.txt"

def display_menu():
    """Display the main menu options"""
    print("\n=== NOTES APP ===")
    print("1. Add a note")
    print("2. View all notes")
    print("3. Delete a note")
    print("4. Exit")

def load_notes():
    """
    Load notes from the file.
    Returns a list of notes, where each note is a string.
    If file doesn't exist, returns empty list.
    """
    notes = []
    try:
        with open(NOTES_FILE, 'r', encoding='utf-8') as file:
            notes = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        # File doesn't exist yet - that's fine, just return empty list
        pass
    return notes

def save_notes(notes):
    """
    Save notes list to the file.
    Each note is written on a separate line.
    """
    with open(NOTES_FILE, 'w', encoding='utf-8') as file:
        for note in notes:
            file.write(note + '\n')

def add_note():
    """Add a new note with timestamp"""
    print("\n--- Add a New Note ---")
    note_content = input("Enter your note: ").strip()
    
    if not note_content:
        print("❌ Note cannot be empty!")
        return
    
    # Create timestamp in format: YYYY-MM-DD HH:MM:SS
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format: [timestamp] content
    formatted_note = f"[{timestamp}] {note_content}"
    
    # Append to file directly (more efficient than loading all notes)
    try:
        with open(NOTES_FILE, 'a', encoding='utf-8') as file:
            file.write(formatted_note + '\n')
        print("✅ Note added successfully!")
    except Exception as e:
        print(f"❌ Error adding note: {e}")

def display_notes(notes):
    """
    Display all notes with numbered entries.
    Returns the list of notes (for use in delete function)
    """
    print("\n--- Your Notes ---")
    
    if not notes:
        print("📭 No notes found. Add a note to get started!")
        return False
    
    for i, note in enumerate(notes, 1):
        # Split timestamp and content for better display
        if note.startswith('[') and ']' in note:
            # Extract timestamp (everything up to the first ']')
            timestamp_end = note.find(']')
            timestamp = note[1:timestamp_end]
            content = note[timestamp_end + 1:].strip()
            print(f"\n[{i}] {timestamp}")
            print(f"    {content}")
        else:
            # Fallback for notes without timestamp (backward compatibility)
            print(f"\n[{i}] {note}")
    
    return True

def delete_note():
    """Delete a note by its number"""
    notes = load_notes()
    
    if not notes:
        print("\n📭 No notes to delete.")
        return
    
    # Display notes with numbers
    print("\n--- Delete a Note ---")
    display_notes(notes)
    
    # Get user choice
    try:
        choice = int(input("\nEnter the note number to delete (or 0 to cancel): "))
        
        if choice == 0:
            print("❌ Deletion cancelled.")
            return
        
        if 1 <= choice <= len(notes):
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete note {choice}? (y/n): ").lower()
            if confirm == 'y':
                deleted_note = notes.pop(choice - 1)
                save_notes(notes)
                print(f"✅ Note deleted successfully!")
            else:
                print("❌ Deletion cancelled.")
        else:
            print(f"❌ Invalid note number. Please choose between 1 and {len(notes)}.")
    
    except ValueError:
        print("❌ Please enter a valid number.")

def main():
    """Main program loop"""
    print("=" * 30)
    print("   WELCOME TO NOTES APP")
    print("=" * 30)
    
    while True:
        display_menu()
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == '1':
            add_note()
        
        elif choice == '2':
            notes = load_notes()
            display_notes(notes)
        
        elif choice == '3':
            delete_note()
        
        elif choice == '4':
            print("\n👋 Goodbye! Your notes have been saved.")
            break
        
        else:
            print("❌ Invalid option. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()