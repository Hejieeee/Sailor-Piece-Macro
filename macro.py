import tkinter as tk
import threading
import time
import keyboard
import pydirectinput as pyautogui

class AFKMacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AFK Macro")
        self.root.geometry("350x300")
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)

        # Variables
        self.is_running = False
        self.runtime_seconds = 0
        self.current_hotkey = "f1"
        self.auto_clicker_var = tk.BooleanVar(value=True)

        self.setup_ui()
        self.setup_hotkey()

    def setup_ui(self):
        # Styling configuration
        bg_color = "#2b2b2b"
        fg_color = "white"
        entry_bg = "#3c3f41"
        font_main = ("Arial", 10)

        # Main Frame
        main_frame = tk.Frame(self.root, bg=bg_color, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Row 0: Labels
        tk.Label(main_frame, text="Target Keys (Max 5):", bg=bg_color, fg=fg_color, font=font_main).grid(row=0, column=0, sticky="w", pady=(0, 5))
        tk.Label(main_frame, text="Key Delay (ms):", bg=bg_color, fg=fg_color, font=font_main).grid(row=0, column=1, sticky="w", pady=(0, 5), padx=(10, 0))

        # Row 1: Entries
        self.keys_entry = tk.Entry(main_frame, bg=entry_bg, fg=fg_color, insertbackground="white", relief="flat")
        self.keys_entry.grid(row=1, column=0, sticky="we", ipady=3)
        
        self.key_delay_entry = tk.Entry(main_frame, bg=entry_bg, fg=fg_color, insertbackground="white", relief="flat")
        self.key_delay_entry.insert(0, "100")
        self.key_delay_entry.grid(row=1, column=1, sticky="we", padx=(10, 0), ipady=3)

        # Row 2: Checkbox & Label
        tk.Checkbutton(main_frame, text="Enable Auto Clicker", variable=self.auto_clicker_var, bg=bg_color, fg=fg_color, selectcolor="#2b2b2b", activebackground=bg_color, activeforeground=fg_color).grid(row=2, column=0, sticky="w", pady=(10, 5))
        tk.Label(main_frame, text="Click Delay (ms):", bg=bg_color, fg=fg_color, font=font_main).grid(row=2, column=1, sticky="w", pady=(10, 5), padx=(10, 0))

        # Row 3: Entry
        self.click_delay_entry = tk.Entry(main_frame, bg=entry_bg, fg=fg_color, insertbackground="white", relief="flat")
        self.click_delay_entry.insert(0, "100")
        self.click_delay_entry.grid(row=3, column=1, sticky="we", padx=(10, 0), ipady=3)

        # Row 4: Hotkey Label
        tk.Label(main_frame, text="Toggle Hotkey (Type to change):", bg=bg_color, fg=fg_color, font=font_main).grid(row=4, column=0, columnspan=2, sticky="w", pady=(15, 5))

        # Row 5: Hotkey Entry
        self.hotkey_entry = tk.Entry(main_frame, bg="white", fg="black", justify="center", font=("Arial", 10, "bold"), relief="flat")
        self.hotkey_entry.insert(0, "F1")
        self.hotkey_entry.grid(row=5, column=0, columnspan=2, sticky="we", ipady=5)

        # Row 6: Status & Runtime Frame
        status_frame = tk.Frame(main_frame, bg=bg_color)
        status_frame.grid(row=6, column=0, columnspan=2, sticky="we", pady=(20, 15))

        self.status_indicator = tk.Label(status_frame, bg="red", width=2, height=1)
        self.status_indicator.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(status_frame, text="Status: OFF", bg=bg_color, fg=fg_color, font=font_main)
        self.status_label.pack(side=tk.LEFT, padx=(5, 20))

        self.runtime_label = tk.Label(status_frame, text="Runtime: 0s", bg=bg_color, fg=fg_color, font=font_main)
        self.runtime_label.pack(side=tk.LEFT)

        # Row 7: Apply Settings Button
        apply_btn = tk.Button(main_frame, text="APPLY SETTINGS", bg="white", fg="black", font=("Arial", 10, "bold"), relief="flat", command=self.apply_settings)
        apply_btn.grid(row=7, column=0, columnspan=2, sticky="we", ipady=5)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def setup_hotkey(self):
        # Register the global hotkey
        keyboard.on_press_key(self.current_hotkey, self.toggle_macro, suppress=False)

    def apply_settings(self):
        # Unhook old hotkey and set new one
        new_hotkey = self.hotkey_entry.get().lower().strip()
        if new_hotkey != self.current_hotkey:
            try:
                keyboard.unhook_key(self.current_hotkey)
                self.current_hotkey = new_hotkey
                keyboard.on_press_key(self.current_hotkey, self.toggle_macro, suppress=False)
            except Exception as e:
                print(f"Error setting hotkey: {e}")

    def toggle_macro(self, event=None):
        self.is_running = not self.is_running
        
        if self.is_running:
            self.status_indicator.config(bg="green")
            self.status_label.config(text="Status: ON")
            self.runtime_seconds = 0
            self.update_timer()
            
            # Start macro thread
            self.macro_thread = threading.Thread(target=self.run_macro, daemon=True)
            self.macro_thread.start()
        else:
            self.status_indicator.config(bg="red")
            self.status_label.config(text="Status: OFF")

    def update_timer(self):
        if self.is_running:
            self.runtime_label.config(text=f"Runtime: {self.runtime_seconds}s")
            self.runtime_seconds += 1
            self.root.after(1000, self.update_timer)

    def run_macro(self):
        while self.is_running:
            try:
                # Get settings safely
                keys_to_press = list(self.keys_entry.get().strip())[:5] # Max 5 characters
                key_delay = max(1, int(self.key_delay_entry.get())) / 1000.0
                click_delay = max(1, int(self.click_delay_entry.get())) / 1000.0
                do_click = self.auto_clicker_var.get()

                # Execute Keys
                for key in keys_to_press:
                    if not self.is_running: break
                    keyboard.send(key)
                    time.sleep(key_delay)

                # Execute Click
                if do_click and self.is_running:
                    pyautogui.click()
                    time.sleep(click_delay)

            except ValueError:
                # Handle empty or invalid number entries
                time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = AFKMacroApp(root)
    root.mainloop()