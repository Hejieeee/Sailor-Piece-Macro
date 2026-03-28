import customtkinter as ctk
import threading
import time
import keyboard
from pynput.mouse import Controller, Button
from pynput.keyboard import Controller as KeyboardController, Key

# Configure CustomTkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MacroApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Sailor Piece AFK Macro")
        self.root.geometry("400x380")
        self.root.resizable(False, False)
        
        # Variables
        self.target_keys = []
        self.key_delay = 100
        self.click_delay = 100
        self.auto_clicker_enabled = True
        self.toggle_hotkey = "f1"
        self.is_running = False
        self.start_time = 0
        self.runtime_seconds = 0
        
        # Controllers
        self.mouse = Controller()
        self.keyboard_controller = KeyboardController()
        
        # Runtime update thread
        self.runtime_thread = None
        self.macro_thread = None
        
        self.create_ui()
        self.setup_hotkey()
        
    def create_ui(self):
        # Main frame with padding
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#1e1e1e")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title (clean - no branding)
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Sailor Piece AFK Macro",
            font=("Segoe UI", 16, "bold"),
            text_color="white"
        )
        self.title_label.pack(pady=(10, 20))
        
        # Settings frame
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="#2d2d2d")
        self.settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Row 1: Target Keys and Key Delay
        self.row1_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.row1_frame.pack(fill="x", padx=10, pady=5)
        
        # Target Keys
        self.keys_label = ctk.CTkLabel(
            self.row1_frame, 
            text="Target Keys (Max 5):",
            font=("Segoe UI", 11),
            text_color="white"
        )
        self.keys_label.pack(anchor="w")
        
        self.keys_entry = ctk.CTkEntry(
            self.row1_frame,
            width=150,
            height=28,
            font=("Segoe UI", 11),
            fg_color="#3d3d3d",
            text_color="white",
            border_color="#555555"
        )
        self.keys_entry.pack(side="left", pady=2)
        
        # Key Delay
        self.delay_frame = ctk.CTkFrame(self.row1_frame, fg_color="transparent")
        self.delay_frame.pack(side="right", padx=(20, 0))
        
        self.key_delay_label = ctk.CTkLabel(
            self.delay_frame,
            text="Key Delay (ms):",
            font=("Segoe UI", 11),
            text_color="white"
        )
        self.key_delay_label.pack(anchor="w")
        
        self.key_delay_entry = ctk.CTkEntry(
            self.delay_frame,
            width=80,
            height=28,
            font=("Segoe UI", 11),
            fg_color="#3d3d3d",
            text_color="white",
            border_color="#555555"
        )
        self.key_delay_entry.insert(0, "100")
        self.key_delay_entry.pack()
        
        # Row 2: Auto Clicker and Click Delay
        self.row2_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.row2_frame.pack(fill="x", padx=10, pady=5)
        
        # Auto Clicker Checkbox
        self.auto_clicker_var = ctk.BooleanVar(value=True)
        self.auto_clicker_check = ctk.CTkCheckBox(
            self.row2_frame,
            text="Enable Auto Clicker",
            variable=self.auto_clicker_var,
            font=("Segoe UI", 11),
            text_color="white",
            fg_color="#0078d7",
            hover_color="#005a9e",
            checkmark_color="white"
        )
        self.auto_clicker_check.pack(side="left", pady=10)
        
        # Click Delay
        self.click_delay_frame = ctk.CTkFrame(self.row2_frame, fg_color="transparent")
        self.click_delay_frame.pack(side="right", padx=(20, 0))
        
        self.click_delay_label = ctk.CTkLabel(
            self.click_delay_frame,
            text="Click Delay (ms):",
            font=("Segoe UI", 11),
            text_color="white"
        )
        self.click_delay_label.pack(anchor="w")
        
        self.click_delay_entry = ctk.CTkEntry(
            self.click_delay_frame,
            width=80,
            height=28,
            font=("Segoe UI", 11),
            fg_color="#3d3d3d",
            text_color="white",
            border_color="#555555"
        )
        self.click_delay_entry.insert(0, "100")
        self.click_delay_entry.pack()
        
        # Toggle Hotkey Section
        self.hotkey_frame = ctk.CTkFrame(self.main_frame, fg_color="#2d2d2d")
        self.hotkey_frame.pack(fill="x", padx=10, pady=5)
        
        self.hotkey_label = ctk.CTkLabel(
            self.hotkey_frame,
            text="Toggle Hotkey (Click to change):",
            font=("Segoe UI", 11),
            text_color="white"
        )
        self.hotkey_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.hotkey_entry = ctk.CTkEntry(
            self.hotkey_frame,
            width=150,
            height=28,
            font=("Segoe UI", 11),
            fg_color="#3d3d3d",
            text_color="white",
            border_color="#555555",
            state="readonly"
        )
        self.hotkey_entry.pack(anchor="w", padx=10, pady=5)
        self.hotkey_entry.insert(0, "F1")
        
        # Bind click to change hotkey
        self.hotkey_entry.bind("<Button-1>", self.change_hotkey)
        self.hotkey_label.bind("<Button-1>", self.change_hotkey)
        
        # Status Section
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="#2d2d2d")
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_inner_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.status_inner_frame.pack(fill="x", padx=10, pady=10)
        
        # Status indicator (colored square)
        self.status_indicator = ctk.CTkLabel(
            self.status_inner_frame,
            text="",
            width=15,
            height=15,
            fg_color="#ff4444",  # Red when off
            corner_radius=2
        )
        self.status_indicator.pack(side="left", padx=(0, 10))
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.status_inner_frame,
            text="Status:",
            font=("Segoe UI", 11),
            text_color="white"
        )
        self.status_label.pack(side="left")
        
        self.status_value = ctk.CTkLabel(
            self.status_inner_frame,
            text="OFF",
            font=("Segoe UI", 11, "bold"),
            text_color="#ff4444"
        )
        self.status_value.pack(side="left", padx=(5, 20))
        
        # Runtime
        self.runtime_label = ctk.CTkLabel(
            self.status_inner_frame,
            text="Runtime:",
            font=("Segoe UI", 11),
            text_color="#aaaaaa"
        )
        self.runtime_label.pack(side="left")
        
        self.runtime_value = ctk.CTkLabel(
            self.status_inner_frame,
            text="0s",
            font=("Segoe UI", 11),
            text_color="#aaaaaa"
        )
        self.runtime_value.pack(side="left", padx=5)
        
        # Apply Button
        self.apply_button = ctk.CTkButton(
            self.main_frame,
            text="APPLY SETTINGS",
            font=("Segoe UI", 12, "bold"),
            height=40,
            fg_color="#f0f0f0",
            text_color="#1e1e1e",
            hover_color="#e0e0e0",
            command=self.apply_settings
        )
        self.apply_button.pack(fill="x", padx=10, pady=15)
        
        # Status bar at bottom
        self.bottom_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Press {self.toggle_hotkey.upper()} to toggle macro",
            font=("Segoe UI", 9),
            text_color="#666666"
        )
        self.bottom_label.pack(pady=(0, 5))
        
    def setup_hotkey(self):
        """Setup the global hotkey for toggling"""
        keyboard.on_press_key(self.toggle_hotkey, lambda e: self.toggle_macro())
        
    def change_hotkey(self, event=None):
        """Change the toggle hotkey"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Change Hotkey")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        label = ctk.CTkLabel(
            dialog,
            text="Enter new hotkey (e.g., f2, insert, etc.):",
            font=("Segoe UI", 11)
        )
        label.pack(pady=20)
        
        entry = ctk.CTkEntry(
            dialog,
            width=200,
            font=("Segoe UI", 11)
        )
        entry.pack(pady=10)
        entry.focus()
        
        def save_hotkey():
            new_key = entry.get().lower().strip()
            if new_key:
                try:
                    # Remove old hotkey
                    keyboard.unhook_all()
                    
                    # Test if valid key
                    keyboard.parse_hotkey(new_key)
                    
                    # Set new hotkey
                    self.toggle_hotkey = new_key
                    self.hotkey_entry.configure(state="normal")
                    self.hotkey_entry.delete(0, "end")
                    self.hotkey_entry.insert(0, new_key.upper())
                    self.hotkey_entry.configure(state="readonly")
                    self.bottom_label.configure(text=f"Press {self.toggle_hotkey.upper()} to toggle macro")
                    
                    # Re-setup hotkey
                    self.setup_hotkey()
                    
                    dialog.destroy()
                except:
                    error_label = ctk.CTkLabel(
                        dialog,
                        text="Invalid key! Try f1-f12, insert, etc.",
                        font=("Segoe UI", 10),
                        text_color="#ff4444"
                    )
                    error_label.pack()
        
        save_btn = ctk.CTkButton(
            dialog,
            text="Save",
            command=save_hotkey
        )
        save_btn.pack(pady=10)
        
    def apply_settings(self):
        """Apply and validate settings"""
        try:
            # Parse target keys
            keys_text = self.keys_entry.get().strip()
            self.target_keys = []
            
            if keys_text:
                if "," in keys_text:
                    # Comma separated
                    keys = [k.strip() for k in keys_text.split(",") if k.strip()]
                elif " " in keys_text:
                    # Space separated
                    keys = keys_text.split()
                else:
                    # Individual characters
                    keys = list(keys_text)
                
                # Limit to 5 keys
                self.target_keys = keys[:5]
            
            # Get delays
            self.key_delay = int(self.key_delay_entry.get())
            self.click_delay = int(self.click_delay_entry.get())
            self.auto_clicker_enabled = self.auto_clicker_var.get()
            
            # Show confirmation
            self.show_tooltip(f"Settings Applied!\nKeys: {', '.join(self.target_keys) if self.target_keys else 'None'}\nAutoClick: {'ON' if self.auto_clicker_enabled else 'OFF'}")
            
        except ValueError:
            self.show_tooltip("Error: Invalid delay values!")
    
    def show_tooltip(self, message):
        """Show a temporary tooltip"""
        tooltip = ctk.CTkToplevel(self.root)
        tooltip.overrideredirect(True)
        tooltip.geometry(f"+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 150}")
        tooltip.attributes("-alpha", 0.9)
        
        label = ctk.CTkLabel(
            tooltip,
            text=message,
            font=("Segoe UI", 11),
            fg_color="#333333",
            text_color="white",
            corner_radius=5,
            padx=15,
            pady=10
        )
        label.pack()
        
        # Auto destroy after 2 seconds
        self.root.after(2000, tooltip.destroy)
    
    def toggle_macro(self):
        """Toggle macro on/off"""
        if not self.is_running:
            # Start macro
            if not self.target_keys:
                self.show_tooltip("Error: No target keys set!\nEnter keys and click Apply.")
                return
            
            self.is_running = True
            self.start_time = time.time()
            self.runtime_seconds = 0
            
            # Update UI
            self.status_indicator.configure(fg_color="#00ff00")  # Green
            self.status_value.configure(text="ON", text_color="#00ff00")
            
            # Start threads
            self.macro_thread = threading.Thread(target=self.macro_loop, daemon=True)
            self.macro_thread.start()
            
            self.runtime_thread = threading.Thread(target=self.update_runtime, daemon=True)
            self.runtime_thread.start()
            
        else:
            # Stop macro
            self.is_running = False
            
            # Update UI
            self.status_indicator.configure(fg_color="#ff4444")  # Red
            self.status_value.configure(text="OFF", text_color="#ff4444")
            self.runtime_value.configure(text="0s")
    
    def macro_loop(self):
        """Main macro execution loop"""
        while self.is_running:
            try:
                # Send target keys
                for key in self.target_keys:
                    if not self.is_running:
                        break
                    
                    # Handle special keys vs regular characters
                    try:
                        if len(key) == 1:
                            self.keyboard_controller.press(key)
                            self.keyboard_controller.release(key)
                        else:
                            # Try to parse as special key
                            special_key = getattr(Key, key.lower(), None)
                            if special_key:
                                self.keyboard_controller.press(special_key)
                                self.keyboard_controller.release(special_key)
                            else:
                                keyboard.send(key.lower())
                    except:
                        pass
                    
                    time.sleep(self.key_delay / 1000)
                
                # Auto clicker
                if self.auto_clicker_enabled and self.is_running:
                    self.mouse.click(Button.left)
                    time.sleep(self.click_delay / 1000)
                    
            except Exception as e:
                print(f"Macro error: {e}")
                time.sleep(0.1)
    
    def update_runtime(self):
        """Update runtime display"""
        while self.is_running:
            elapsed = int(time.time() - self.start_time)
            self.runtime_value.configure(text=f"{elapsed}s")
            time.sleep(1)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MacroApp()
    app.run()