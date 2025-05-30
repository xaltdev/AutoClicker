import customtkinter as ctk
import tkinter as tk # Still needed for Toplevel in picker overlay
from pynput import mouse, keyboard
import threading
import time

# --- Configuration ---
DEFAULT_HOTKEY = keyboard.Key.f6
DEFAULT_HOTKEY_STR = "F6"

# --- Custom Colors for Modern Theme ---
COLORS = {
    "bg_primary": "#0a0a0a",
    "bg_secondary": "#1a1a1a",
    "bg_tertiary": "#2a2a2a",
    "bg_glass": "#1e1e1e",
    "accent_primary": "#6366f1",
    "accent_secondary": "#8b5cf6",
    "accent_success": "#10b981",
    "accent_success_hover": "#059669", # Added for consistency
    "accent_warning": "#f59e0b",
    "accent_warning_hover": "#d97706", # Added for consistency
    "accent_danger": "#ef4444",
    "accent_danger_hover": "#dc2626",  # Added for consistency
    "text_primary": "#ffffff",
    "text_secondary": "#a1a1aa",
    "border_glass": "#404040"
}

# --- Main Application Class ---
class CompactAutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Instance Variables for Clicker & State ---
        self.click_thread = None
        self.running = False
        self.stop_event = threading.Event()
        self.current_hotkey = DEFAULT_HOTKEY
        self.current_hotkey_str = DEFAULT_HOTKEY_STR

        # --- Mouse Control ---
        self.mouse_controller = mouse.Controller()
        # self.keyboard_controller = keyboard.Controller() # Was unused

        # --- Picker specific listeners ---
        self.picker_mouse_listener = None
        self.picker_keyboard_listener = None
        self.hotkey_listener_instance = None # For the main hotkey

        self.title("Auto Clicker")
        self.geometry("500x630") # Increased height for status label
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=COLORS["bg_primary"])

        self.build_compact_ui()
        self.setup_hotkey_listener()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def create_glass_frame(self, parent, **kwargs):
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_glass"],
            border_width=1,
            border_color=COLORS["border_glass"],
            corner_radius=12,
            **kwargs
        )
        return frame

    def create_gradient_button(self, parent, text, command=None, color_key="primary", height=32, **kwargs):
        button_colors_map = {
            "primary": (COLORS["accent_primary"], COLORS["accent_secondary"]),
            "success": (COLORS["accent_success"], COLORS["accent_success_hover"]),
            "danger": (COLORS["accent_danger"], COLORS["accent_danger_hover"]),
            "warning": (COLORS["accent_warning"], COLORS["accent_warning_hover"]),
        }
        fg_color, hover_color = button_colors_map.get(color_key, button_colors_map["primary"])

        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=height,
            **kwargs
        )
        return button

    def create_compact_entry(self, parent, default_value, placeholder="", width=60):
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border_glass"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_secondary"],
            corner_radius=6,
            height=28,
            width=width,
            font=ctk.CTkFont(size=11)
        )
        entry.insert(0, str(default_value))
        return entry

    def build_compact_ui(self):
        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Auto Clicker",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=15)

        # --- Click Interval Section ---
        interval_section = self.create_glass_frame(self)
        interval_section.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(interval_section, text="Interval", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(10, 5))
        time_frame = ctk.CTkFrame(interval_section, fg_color="transparent")
        time_frame.pack(padx=15, pady=(0, 10))
        self.hours_entry = self.create_compact_entry(time_frame, "0", "H", 50)
        self.hours_entry.pack(side="left", padx=2); ctk.CTkLabel(time_frame, text="h", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 8))
        self.mins_entry = self.create_compact_entry(time_frame, "0", "M", 50)
        self.mins_entry.pack(side="left", padx=2); ctk.CTkLabel(time_frame, text="m", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 8))
        self.secs_entry = self.create_compact_entry(time_frame, "0", "S", 50)
        self.secs_entry.pack(side="left", padx=2); ctk.CTkLabel(time_frame, text="s", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 8))
        self.ms_entry = self.create_compact_entry(time_frame, "100", "MS", 60)
        self.ms_entry.pack(side="left", padx=2); ctk.CTkLabel(time_frame, text="ms", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=10)).pack(side="left")

        # --- Click Options Section ---
        options_section = self.create_glass_frame(self)
        options_section.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(options_section, text="Options", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(10, 5))
        options_grid = ctk.CTkFrame(options_section, fg_color="transparent"); options_grid.pack(fill="x", padx=15, pady=(0, 10)); options_grid.grid_columnconfigure((0, 1), weight=1)
        
        self.mouse_button_var = ctk.StringVar(value="Left")
        self.mouse_button_combo = ctk.CTkComboBox(
            options_grid, 
            values=["Left", "Right", "Middle"], 
            variable=self.mouse_button_var, 
            fg_color=COLORS["bg_tertiary"], 
            border_color=COLORS["accent_primary"], 
            button_color=COLORS["accent_primary"], 
            button_hover_color=COLORS["accent_secondary"], 
            dropdown_fg_color=COLORS["bg_secondary"], 
            height=28, 
            font=ctk.CTkFont(size=11),
            state="readonly",
            command=lambda choice: None 
        )
        self.mouse_button_combo.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="ew")
        self.mouse_button_combo.bind("<Button-1>", 
            lambda event, cb=self.mouse_button_combo: cb._open_dropdown_menu())
        self.mouse_button_combo.configure(cursor="hand2")
        self.mouse_button_combo._entry.configure(cursor="hand2")
        
        self.click_type_var = ctk.StringVar(value="Single")
        self.click_type_combo = ctk.CTkComboBox(
            options_grid, 
            values=["Single", "Double"], 
            variable=self.click_type_var, 
            fg_color=COLORS["bg_tertiary"], 
            border_color=COLORS["accent_primary"], 
            button_color=COLORS["accent_primary"], 
            button_hover_color=COLORS["accent_secondary"], 
            dropdown_fg_color=COLORS["bg_secondary"], 
            height=28, 
            font=ctk.CTkFont(size=11),
            state="readonly",
            command=lambda choice: None
        )
        self.click_type_combo.grid(row=0, column=1, padx=(5, 0), pady=2, sticky="ew")
        self.click_type_combo.bind("<Button-1>", 
            lambda event, cb=self.click_type_combo: cb._open_dropdown_menu())
        self.click_type_combo.configure(cursor="hand2")
        self.click_type_combo._entry.configure(cursor="hand2")

        # --- Repeat Options Section ---
        repeat_section = self.create_glass_frame(self)
        repeat_section.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(repeat_section, text="Repeat", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(10, 5))
        repeat_frame = ctk.CTkFrame(repeat_section, fg_color="transparent"); repeat_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.repeat_mode_var = ctk.StringVar(value="until_stopped")
        repeat_top = ctk.CTkFrame(repeat_frame, fg_color="transparent"); repeat_top.pack(fill="x", pady=(0, 5))
        self.repeat_n_radio = ctk.CTkRadioButton(repeat_top, text="Repeat", variable=self.repeat_mode_var, value="n_times", command=self.toggle_repeat_entry, radiobutton_width=16, radiobutton_height=16, fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_secondary"], font=ctk.CTkFont(size=11))
        self.repeat_n_radio.pack(side="left", padx=(0, 8))
        self.repeat_times_entry = self.create_compact_entry(repeat_top, "1", "Times", 60); self.repeat_times_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(repeat_top, text="times", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=10)).pack(side="left")
        self.repeat_until_stopped_radio = ctk.CTkRadioButton(repeat_frame, text="Until stopped", variable=self.repeat_mode_var, value="until_stopped", command=self.toggle_repeat_entry, radiobutton_width=16, radiobutton_height=16, fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_secondary"], font=ctk.CTkFont(size=11))
        self.repeat_until_stopped_radio.pack(anchor="w"); self.repeat_until_stopped_radio.select(); self.toggle_repeat_entry()

        # --- Cursor Position Section ---
        cursor_section = self.create_glass_frame(self)
        cursor_section.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(cursor_section, text="Position", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(10, 5))
        cursor_frame = ctk.CTkFrame(cursor_section, fg_color="transparent"); cursor_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.cursor_pos_var = ctk.StringVar(value="current")
        cursor_top = ctk.CTkFrame(cursor_frame, fg_color="transparent"); cursor_top.pack(fill="x", pady=(0, 5))
        self.current_loc_radio = ctk.CTkRadioButton(cursor_top, text="Current", variable=self.cursor_pos_var, value="current", command=self.toggle_pick_location, radiobutton_width=16, radiobutton_height=16, fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_secondary"], font=ctk.CTkFont(size=11))
        self.current_loc_radio.pack(side="left", padx=(0, 15)); self.current_loc_radio.select()
        self.pick_loc_radio = ctk.CTkRadioButton(cursor_top, text="Pick", variable=self.cursor_pos_var, value="pick", command=self.toggle_pick_location, radiobutton_width=16, radiobutton_height=16, fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_secondary"], font=ctk.CTkFont(size=11))
        self.pick_loc_radio.pack(side="left", padx=(0, 10))
        self.pick_location_button = self.create_gradient_button(cursor_top, "📍", command=self.start_pick_location, color_key="primary", width=40, height=28) # Matched height to entries for alignment
        self.pick_location_button.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(cursor_top, text="X:", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 2))
        self.x_pos_entry = self.create_compact_entry(cursor_top, "0", "X", 50); self.x_pos_entry.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(cursor_top, text="Y:", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 2))
        self.y_pos_entry = self.create_compact_entry(cursor_top, "0", "Y", 50); self.y_pos_entry.pack(side="left")
        self.toggle_pick_location()

        # --- Control Section ---
        control_section = self.create_glass_frame(self)
        control_section.pack(fill="x", padx=15, pady=5)
        control_frame = ctk.CTkFrame(control_section, fg_color="transparent"); control_frame.pack(fill="x", padx=15, pady=15); control_frame.grid_columnconfigure((0, 1), weight=1)
        self.start_stop_button = self.create_gradient_button(control_frame, f"▶️ Start ({self.current_hotkey_str})", command=self.toggle_clicking, color_key="success", height=40)
        self.start_stop_button.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.hotkey_button = self.create_gradient_button(control_frame, "Change Hotkey", command=self.open_hotkey_dialog, color_key="primary", height=40)
        self.hotkey_button.grid(row=0, column=1, padx=(8, 0), sticky="ew")
        
        # --- Status Label ---
        self.status_label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"])
        self.status_label.pack(pady=(5, 10))

        self.configurable_elements = [
            self.hours_entry, self.mins_entry, self.secs_entry, self.ms_entry,
            self.mouse_button_combo, self.click_type_combo,
            self.repeat_n_radio, self.repeat_times_entry, self.repeat_until_stopped_radio,
            self.current_loc_radio, self.pick_loc_radio, self.pick_location_button,
            self.x_pos_entry, self.y_pos_entry, self.hotkey_button
        ]

    def toggle_repeat_entry(self):
        if self.repeat_mode_var.get() == "n_times":
            self.repeat_times_entry.configure(state="normal")
        else:
            self.repeat_times_entry.configure(state="disabled", text_color=COLORS["text_secondary"]) # Visually indicate disabled

    def toggle_pick_location(self):
        is_pick_mode = self.cursor_pos_var.get() == "pick"
        state = "normal" if is_pick_mode else "disabled"
        text_color = COLORS["text_primary"] if is_pick_mode else COLORS["text_secondary"] # Visually indicate disabled

        self.pick_location_button.configure(state=state)
        self.x_pos_entry.configure(state=state, text_color=text_color)
        self.y_pos_entry.configure(state=state, text_color=text_color)


    def _update_picker_overlay_text(self, text, color):
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
             self.status_label.configure(text=text, text_color=color)

    def _destroy_picker_overlay_and_reappear(self):
        if hasattr(self, 'picker_overlay') and self.picker_overlay.winfo_exists():
            self.picker_overlay.destroy()
            del self.picker_overlay # Clean up attribute
        self.deiconify() # Bring main window back

    def start_pick_location(self):
        self._update_picker_overlay_text("Click to pick location...", COLORS["accent_warning"])
        self.withdraw() # Hide main window

        self.picker_overlay = tk.Toplevel(self) # Using tk.Toplevel for minimal overlay
        self.picker_overlay.attributes("-topmost", True)
        self.picker_overlay.attributes("-alpha", 0.9) # Slight transparency
        self.picker_overlay.overrideredirect(True) # No window decorations

        screen_width = self.picker_overlay.winfo_screenwidth()
        screen_height = self.picker_overlay.winfo_screenheight()
        overlay_width, overlay_height = 350, 80
        x_pos = (screen_width // 2) - (overlay_width // 2)
        y_pos = (screen_height // 2) - (overlay_height // 2)
        self.picker_overlay.geometry(f"{overlay_width}x{overlay_height}+{x_pos}+{y_pos}")

        overlay_frame = tk.Frame(self.picker_overlay, bg=COLORS["bg_secondary"], relief="flat", bd=1)
        overlay_frame.pack(fill="both", expand=True, padx=1, pady=1) # Small border
        tk.Label(overlay_frame, text="Click anywhere to select position", bg=COLORS["bg_secondary"], fg=COLORS["text_primary"], font=("Segoe UI", 12, "bold")).pack(pady=(12, 3))
        tk.Label(overlay_frame, text="Press ESC to cancel", bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"], font=("Segoe UI", 9)).pack()

        self.stop_pick_location_listeners() # Ensure old ones are stopped
        self.picker_mouse_listener = mouse.Listener(on_click=self._on_pick_click_callback)
        self.picker_mouse_listener.start()
        self.picker_keyboard_listener = keyboard.Listener(on_press=self._on_pick_cancel_callback)
        self.picker_keyboard_listener.start()

    def _on_pick_click_callback(self, x, y, button, pressed):
        if pressed:
            self.after(0, self._process_pick_click, x, y)
            return False # Stop this listener

    def _process_pick_click(self, x, y):
        self.x_pos_entry.delete(0, ctk.END)
        self.x_pos_entry.insert(0, str(x))
        self.y_pos_entry.delete(0, ctk.END)
        self.y_pos_entry.insert(0, str(y))
        self._update_picker_overlay_text(f"Position: ({x}, {y})", COLORS["accent_success"])
        self.stop_pick_location_listeners()
        self._destroy_picker_overlay_and_reappear()


    def _on_pick_cancel_callback(self, key):
        if key == keyboard.Key.esc:
            self.after(0, self._process_pick_cancel)
            return False # Stop this listener

    def _process_pick_cancel(self):
        self._update_picker_overlay_text("Picking cancelled", COLORS["accent_warning"])
        self.stop_pick_location_listeners()
        self._destroy_picker_overlay_and_reappear()

    def stop_pick_location_listeners(self):
        if self.picker_mouse_listener:
            self.picker_mouse_listener.stop()
            self.picker_mouse_listener = None
        if self.picker_keyboard_listener:
            self.picker_keyboard_listener.stop()
            self.picker_keyboard_listener = None

    def get_click_settings(self):
        try:
            h = int(self.hours_entry.get() or 0)
            m = int(self.mins_entry.get() or 0)
            s = int(self.secs_entry.get() or 0)
            ms = int(self.ms_entry.get() or 0)
            interval = (h * 3600 + m * 60 + s) + (ms / 1000.0)
            interval = max(0.001, interval) # Ensure interval is at least 1ms

            button_str = self.mouse_button_var.get()
            click_button = {"Left": mouse.Button.left, "Right": mouse.Button.right, "Middle": mouse.Button.middle}[button_str]
            click_count = 2 if self.click_type_var.get() == "Double" else 1

            repeat_mode = self.repeat_mode_var.get()
            repeat_times = 0
            if repeat_mode == "n_times":
                repeat_times = int(self.repeat_times_entry.get() or 1)
                repeat_times = max(1, repeat_times)

            cursor_mode = self.cursor_pos_var.get()
            target_x, target_y = 0, 0
            if cursor_mode == "pick":
                target_x = int(self.x_pos_entry.get() or 0)
                target_y = int(self.y_pos_entry.get() or 0)

            return {"interval": interval, "button": click_button, "count": click_count,
                    "repeat_mode": repeat_mode, "repeat_times": repeat_times,
                    "cursor_mode": cursor_mode, "x": target_x, "y": target_y}
        except ValueError:
            self._update_picker_overlay_text("Invalid input in settings!", COLORS["accent_danger"])
            return None

    def toggle_clicking(self):
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def _set_controls_state(self, state="normal"):
        text_color = COLORS["text_primary"] if state == "normal" else COLORS["text_secondary"]
        for elem in self.configurable_elements:
            # Check if the element is one of the entries that needs text color change
            if isinstance(elem, ctk.CTkEntry) and elem not in [self.repeat_times_entry, self.x_pos_entry, self.y_pos_entry]:
                 elem.configure(state=state, text_color=text_color)
            else:
                 elem.configure(state=state)
        
        # Restore conditional states after blanket change
        self.toggle_repeat_entry()
        self.toggle_pick_location()


    def start_clicking(self):
        settings = self.get_click_settings()
        if not settings:
            return

        self.running = True
        self.stop_event.clear()
        danger_fg_color = COLORS["accent_danger"]
        danger_hover_color = COLORS["accent_danger_hover"]
        self.start_stop_button.configure(
            text=f"⏹️ Stop ({self.current_hotkey_str})",
            fg_color=danger_fg_color,
            hover_color=danger_hover_color
        )

        self._update_picker_overlay_text("Auto-clicking...", COLORS["accent_success"])
        
        self._set_controls_state("disabled")

        self.click_thread = threading.Thread(target=self._click_worker, args=(settings,), daemon=True)
        self.click_thread.start()

    def stop_clicking(self, from_worker_completion=False):
        if self.running or from_worker_completion:
            self.running = False
            self.stop_event.set()
            if self.click_thread and self.click_thread.is_alive():
                self.click_thread.join(timeout=0.2)
            self.click_thread = None

            success_fg_color = COLORS["accent_success"]
            success_hover_color = COLORS["accent_success_hover"]
            self.start_stop_button.configure(
                text=f"▶️ Start ({self.current_hotkey_str})",
                fg_color=success_fg_color,
                hover_color=success_hover_color
            )

            if not from_worker_completion:
                 self._update_picker_overlay_text("Stopped", COLORS["accent_warning"])
            
            self._set_controls_state("normal")


    def _click_worker(self, settings):
        clicks_done = 0
        try:
            while not self.stop_event.is_set():
                if settings["cursor_mode"] == "pick":
                    original_pos = self.mouse_controller.position
                    self.mouse_controller.position = (settings["x"], settings["y"])
                    time.sleep(0.01) # Brief pause for position update

                self.mouse_controller.click(settings["button"], settings["count"])

                if settings["cursor_mode"] == "pick": # Restore position if it was changed
                    self.mouse_controller.position = original_pos
                
                clicks_done += 1

                if settings["repeat_mode"] == "n_times" and clicks_done >= settings["repeat_times"]:
                    break

                # Interruptible sleep
                sleep_target = settings["interval"]
                while sleep_target > 0 and not self.stop_event.is_set():
                    sleep_chunk = min(sleep_target, 0.05) # Sleep in chunks of max 50ms
                    time.sleep(sleep_chunk)
                    sleep_target -= sleep_chunk
        finally:
            # Ensure UI update happens on main thread after worker finishes or is stopped
            self.after(0, self.stop_clicking_from_thread, clicks_done == settings.get("repeat_times", float('inf')))


    def stop_clicking_from_thread(self, completed_normally):
        # This method is called via self.after() from the _click_worker thread
        if completed_normally and self.repeat_mode_var.get() == "n_times":
            self._update_picker_overlay_text("Completed!", COLORS["accent_primary"])
        elif not self.running and not self.stop_event.is_set(): # If stop_clicking already ran
             pass # Already handled
        else:
            self._update_picker_overlay_text("Stopped", COLORS["accent_warning"])
        
        # Ensure stop_clicking logic runs to re-enable UI etc.
        # Pass True to indicate it's from worker completion, for state handling
        self.stop_clicking(from_worker_completion=True)


    def open_hotkey_dialog(self):
        if self.running:
            self._update_picker_overlay_text("Stop clicking before changing hotkey.", COLORS["accent_warning"])
            return
            
        dialog = CompactHotkeyDialog(self, current_hotkey_str=self.current_hotkey_str)
        # transient and grab_set are handled by CTkToplevel if parent is given
        self.wait_window(dialog) # Waits for dialog to close

        if dialog.new_hotkey: # Check if a new hotkey was set
            self.current_hotkey = dialog.new_hotkey
            self.current_hotkey_str = dialog.new_hotkey_str
            
            # Update button text based on current state (running or not)
            if self.running:
                self.start_stop_button.configure(text=f"⏹️ Stop ({self.current_hotkey_str})")
            else:
                self.start_stop_button.configure(text=f"▶️ Start ({self.current_hotkey_str})")

            self.stop_hotkey_listener() # Stop old listener
            self.setup_hotkey_listener() # Start new one
            self._update_picker_overlay_text(f"Hotkey set to: {self.current_hotkey_str}", COLORS["accent_primary"])
        elif dialog.cancelled:
            self._update_picker_overlay_text("Hotkey change cancelled.", COLORS["text_secondary"])


    def setup_hotkey_listener(self):
        # Listener runs in its own thread, managed by pynput
        if self.hotkey_listener_instance and self.hotkey_listener_instance.is_alive():
            self.hotkey_listener_instance.stop()

        self.hotkey_listener_instance = keyboard.Listener(on_press=self._on_hotkey_press_callback)
        self.hotkey_listener_instance.start()

    def _on_hotkey_press_callback(self, key):
        if self.running and key == self.current_hotkey: # Only toggle if matches current hotkey
            self.after(0, self.toggle_clicking)
        elif not self.running and key == self.current_hotkey:
             # If not running, and hotkey is pressed, try to start
            if hasattr(self, 'picker_overlay') and self.picker_overlay.winfo_exists():
                # Don't start if picker overlay is active
                return
            self.after(0, self.toggle_clicking)


    def stop_hotkey_listener(self):
        if self.hotkey_listener_instance and self.hotkey_listener_instance.is_alive():
            self.hotkey_listener_instance.stop()
            self.hotkey_listener_instance = None # Clear the instance

    def on_closing(self):
        self.stop_event.set() # Signal all threads that might be using it
        self.stop_clicking()
        self.stop_hotkey_listener()
        self.stop_pick_location_listeners()
        
        # Explicitly join threads if they were not daemons or if critical cleanup is needed
        # Since click_thread is daemon and pynput listeners manage their own threads,
        # setting stop_event and calling stop() on listeners is usually enough.
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=0.1)

        self.destroy()

# --- Compact Hotkey Dialog Class ---
class CompactHotkeyDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_hotkey_str):
        super().__init__(parent)
        self.parent = parent # Keep a reference if needed
        self.title("Set Hotkey")
        # Center on parent
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        width, height = 300, 150
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.lift() # Lift window on top
        self.attributes("-topmost", True) # Keep on top
        self.grab_set() # Modal behavior
        self.protocol("WM_DELETE_WINDOW", self._on_dialog_close) # Handle X button close

        self.configure(fg_color=COLORS["bg_primary"])

        self.new_hotkey = None
        self.new_hotkey_str = ""
        self.cancelled = False # Flag for cancellation

        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_glass"], border_width=1, border_color=COLORS["border_glass"], corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.info_label = ctk.CTkLabel(main_frame, text=f"Current: {current_hotkey_str}\nPress new key (ESC to cancel)", font=ctk.CTkFont(size=14), text_color=COLORS["text_primary"])
        self.info_label.pack(pady=20, padx=15)
        
        self.key_display_label = ctk.CTkLabel(main_frame, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["accent_success"])
        self.key_display_label.pack(pady=(0,20), padx=15)


        self.listener = keyboard.Listener(on_press=self._on_key_press_callback_dialog)
        self.listener.start()

    def _on_key_press_callback_dialog(self, key):
        self.listener.stop() # Stop listening immediately
        self.after(0, self._process_key_press_dialog, key) # Process in main thread

    def _process_key_press_dialog(self, key):
        if key == keyboard.Key.esc:
            self.new_hotkey = None
            self.new_hotkey_str = ""
            self.cancelled = True
            self.key_display_label.configure(text="Cancelled", text_color=COLORS["accent_warning"])
            self.after(1000, self._close_dialog)
        else:
            self.new_hotkey = key
            try:
                # For special keys like F6, .name is preferred. For chars, .char.
                if hasattr(key, 'char') and key.char is not None:
                    self.new_hotkey_str = key.char.upper()
                elif hasattr(key, 'name'):
                    self.new_hotkey_str = key.name.upper()
                else: # Fallback for less common key types
                    self.new_hotkey_str = str(key).upper()

                # Simplify display for keys like "Key.f6" to "F6"
                if self.new_hotkey_str.startswith("KEY."):
                    self.new_hotkey_str = self.new_hotkey_str.split('.')[1]
                    
            except AttributeError: # Should not happen if key is from pynput
                self.new_hotkey_str = str(key).upper()

            self.key_display_label.configure(text=f"New: {self.new_hotkey_str}", text_color=COLORS["accent_success"])
            self.info_label.configure(text="Hotkey set!") # Update info label
            self.after(1000, self._close_dialog)

    def _on_dialog_close(self): # Called when 'X' is pressed
        if self.listener and self.listener.is_alive():
            self.listener.stop()
        self.cancelled = True # Treat closing via 'X' as a cancel
        self.new_hotkey = None # Ensure no hotkey is passed back
        self.new_hotkey_str = ""
        self.grab_release()
        self.destroy()

    def _close_dialog(self):
        if self.listener and self.listener.is_alive(): # Should be stopped already but good check
            self.listener.stop()
        self.grab_release()
        self.destroy()


# --- Main Execution ---
if __name__ == "__main__":
    app = CompactAutoClickerApp()
    app.mainloop()