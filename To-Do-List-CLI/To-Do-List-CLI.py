import json
import os
from datetime import datetime
from typing import Dict, Optional, Union

class TodoApp:
    def __init__(self, filename="tasks.json"):
        """Initialize the To-Do app with a filename for persistence"""
        self.filename = filename
        self.tasks: Dict[int, Dict] = {}
        self.next_id = 1
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file on startup"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as file:
                    data = json.load(file)
                    self.tasks = {int(k): v for k, v in data.items()}
                    # Update next_id to be greater than any existing ID
                    if self.tasks:
                        self.next_id = max(self.tasks.keys()) + 1
                print(f"✅ Loaded {len(self.tasks)} tasks from {self.filename}")
            else:
                print(f"📁 No existing tasks file found. Starting fresh!")
        except Exception as e:
            print(f"⚠️ Error loading tasks: {e}")
            self.tasks = {}
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.filename, 'w') as file:
                json.dump(self.tasks, file, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving tasks: {e}")
            return False
    
    def add_task(self, description: str) -> Optional[int]:
        """Add a new task with the given description"""
        if not description.strip():
            print("❌ Task description cannot be empty!")
            return None
        
        task_id = self.next_id
        self.tasks[task_id] = {
            "description": description.strip(),
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.next_id += 1
        
        if self.save_tasks():
            print(f"✅ Task added successfully! (ID: {task_id})")
            return task_id
        else:
            # Remove task if save failed
            del self.tasks[task_id]
            return None
    
    def view_all_tasks(self):
        """Display all tasks with their details"""
        if not self.tasks:
            print("\n📋 No tasks found! Add some tasks to get started.")
            return
        
        print("\n" + "="*60)
        print("ALL TASKS")
        print("="*60)
        
        # Separate incomplete and completed tasks
        incomplete = {k: v for k, v in self.tasks.items() if not v["completed"]}
        completed = {k: v for k, v in self.tasks.items() if v["completed"]}
        
        if incomplete:
            print("\n📌 INCOMPLETE TASKS:")
            for task_id, task in incomplete.items():
                status = "[ ]"
                created = task.get("created_at", "").split("T")[0] if task.get("created_at") else "Unknown"
                print(f"  {status} {task_id:3d}. {task['description']:<40} (Created: {created})")
        
        if completed:
            print("\n✅ COMPLETED TASKS:")
            for task_id, task in completed.items():
                status = "[✓]"
                created = task.get("created_at", "").split("T")[0] if task.get("created_at") else "Unknown"
                completed_at = task.get("completed_at", "").split("T")[0] if task.get("completed_at") else "Unknown"
                print(f"  {status} {task_id:3d}. {task['description']:<40} (Completed: {completed_at})")
        
        print(f"\n📊 Summary: {len(incomplete)} pending, {len(completed)} completed")
        print("="*60)
    
    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as completed"""
        if task_id not in self.tasks:
            print(f"❌ Task with ID {task_id} not found!")
            return False
        
        if self.tasks[task_id]["completed"]:
            print(f"⚠️ Task '{self.tasks[task_id]['description']}' is already completed!")
            return False
        
        self.tasks[task_id]["completed"] = True
        self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
        
        if self.save_tasks():
            print(f"✅ Task '{self.tasks[task_id]['description']}' marked as complete!")
            return True
        else:
            # Revert changes if save failed
            self.tasks[task_id]["completed"] = False
            self.tasks[task_id]["completed_at"] = None
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID"""
        if task_id not in self.tasks:
            print(f"❌ Task with ID {task_id} not found!")
            return False
        
        description = self.tasks[task_id]["description"]
        del self.tasks[task_id]
        
        if self.save_tasks():
            print(f"✅ Task '{description}' (ID: {task_id}) deleted successfully!")
            return True
        else:
            # This is tricky to revert without keeping a backup
            print(f"❌ Failed to delete task '{description}'!")
            return False
    
    def clear_screen(self):
        """Clear the console screen (works on Windows, macOS, Linux)"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("     📝 TO-DO LIST APPLICATION")
        print("="*50)
        print("1. ➕ Add task")
        print("2. 👁️ View all tasks")
        print("3. ✅ Mark task complete")
        print("4. 🗑️ Delete task")
        print("5. 🚪 Exit")
        print("="*50)
    
    def get_valid_input(self, prompt: str, input_type: type = str) -> Optional[Union[str, int]]:
        """Get valid user input with error handling"""
        while True:
            try:
                user_input = input(prompt).strip()
                if input_type == int:
                    if user_input == "":
                        return None
                    return int(user_input)
                return user_input
            except ValueError:
                print("❌ Invalid input. Please enter a valid value.")
    
    def run(self):
        """Main application loop"""
        print("\n🎉 Welcome to the To-Do List Application!")
        print(f"📁 Data file: {self.filename}")
        
        while True:
            try:
                self.display_menu()
                choice = input("Choose an option (1-5): ").strip()
                
                if choice == "1":  # Add task
                    print("\n--- ADD NEW TASK ---")
                    description = self.get_valid_input("Enter task description: ")
                    if description:
                        self.add_task(description)
                    input("\nPress Enter to continue...")
                
                elif choice == "2":  # View tasks
                    self.view_all_tasks()
                    input("\nPress Enter to continue...")
                
                elif choice == "3":  # Mark complete
                    print("\n--- MARK TASK COMPLETE ---")
                    self.view_all_tasks()
                    task_id = self.get_valid_input("Enter task ID to mark complete (or 0 to cancel): ", int)
                    if task_id and task_id > 0:
                        self.mark_complete(task_id)
                    input("\nPress Enter to continue...")
                
                elif choice == "4":  # Delete task
                    print("\n--- DELETE TASK ---")
                    self.view_all_tasks()
                    task_id = self.get_valid_input("Enter task ID to delete (or 0 to cancel): ", int)
                    if task_id and task_id > 0:
                        # Confirm deletion
                        confirm = input(f"Are you sure you want to delete task {task_id}? (y/n): ").lower()
                        if confirm == 'y':
                            self.delete_task(task_id)
                        else:
                            print("Deletion cancelled.")
                    input("\nPress Enter to continue...")
                
                elif choice == "5":  # Exit
                    print("\n👋 Thank you for using the To-Do List Application!")
                    print(f"💾 Your tasks have been saved to {self.filename}")
                    break
                
                else:
                    print("❌ Invalid choice. Please enter a number between 1 and 5.")
                    input("Press Enter to continue...")
                
                # Clear screen for next iteration (optional - comment out if you prefer not to clear)
                # self.clear_screen()
                
            except KeyboardInterrupt:
                print("\n\n👋 Application interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}")
                input("Press Enter to continue...")

def main():
    """Entry point of the application"""
    app = TodoApp("my_tasks.json")
    app.run()

if __name__ == "__main__":
    main()