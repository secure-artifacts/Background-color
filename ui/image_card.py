import threading
import customtkinter as ctk
from PIL import Image
import pyperclip
import os
import time
from concurrent.futures import ThreadPoolExecutor

# Global thread pool to limit concurrent image processing and loading
_thread_pool = ThreadPoolExecutor(max_workers=8)

class HoverPreview:
    _instance = None
    _loading = False
    
    @classmethod
    def show(cls, widget, img_path, x_offset):
        if cls._loading: return
        cls._loading = True
        
        # Small delay to prevent flashing if mouse moves quickly over things
        def _show():
            if not cls._loading: return
            if cls._instance:
                cls.hide()
                
            try:
                # Need to use standard Toplevel as CTkToplevel has issues with overrideredirect in some OS
                import tkinter as tk
                cls._instance = tk.Toplevel(widget)
                cls._instance.overrideredirect(True)
                cls._instance.attributes("-topmost", True)
                
                # Load larger image (cache the PIL image or just load fast from SSD)
                pil_img = Image.open(img_path)
                pil_img.thumbnail((360, 360), Image.LANCZOS)
                
                # Size calculation
                w, h = pil_img.width, pil_img.height
                x = widget.winfo_rootx() + x_offset
                y = widget.winfo_rooty() - (h - widget.winfo_height()) // 2
                
                # Keep on screen bounds roughly
                screen_width = widget.winfo_screenwidth()
                screen_height = widget.winfo_screenheight()
                if x + w > screen_width:
                    x = widget.winfo_rootx() - w - 10
                if y + h > screen_height:
                    y = screen_height - h - 10
                if y < 0: y = 10
                
                cls._instance.geometry(f"{w}x{h}+{x}+{y}")
                
                ctk_img = ctk.CTkImage(light_image=pil_img, size=(w, h))
                cls._instance._ctk_img = ctk_img # Keep reference
                
                lbl = ctk.CTkLabel(cls._instance, image=ctk_img, text="", fg_color="transparent")
                lbl.pack(fill="both", expand=True)
            except Exception as e:
                print(f"Hover preview error: {e}")
                cls.hide()
            finally:
                cls._loading = False
                
        widget.after(300, _show)

    @classmethod
    def hide(cls):
        cls._loading = False
        if cls._instance:
            cls._instance.destroy()
            cls._instance = None


class ImageCard(ctk.CTkFrame):
    # Memory cache so re-rending same categories is instant
    _THUMBNAIL_CACHE = {}

    def __init__(self, master, img_id, desc, is_favorite, data_manager, on_favorite_toggle, **kwargs):
        super().__init__(master, fg_color=("gray90", "gray15"), corner_radius=8, cursor="hand2", **kwargs)
        self.img_id = img_id
        self.desc = desc
        self.is_favorite = is_favorite
        self.data_manager = data_manager
        self.on_favorite_toggle = on_favorite_toggle
        self.img_path = None
        
        # Compact design
        self.card_size = 140
        self.configure(width=self.card_size, height=self.card_size)
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        # Image placeholder
        self.image_label = ctk.CTkLabel(self, text="Loading...", width=self.card_size, height=self.card_size)
        self.image_label.pack(fill="both", expand=True)
        
        # Favorite Button overlay (top right)
        self.fav_btn_text = "❤️" if self.is_favorite else "🤍"
        self.fav_btn = ctk.CTkButton(
            self, text=self.fav_btn_text, width=28, height=28,
            hover_color=("gray80", "gray25"), fg_color="transparent", 
            text_color=("red", "pink"), corner_radius=14,
            command=self.toggle_fav
        )
        self.fav_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-4, y=4)
        
        # Success Toast overlay (center)
        self.toast_label = ctk.CTkLabel(
            self, text="  ID 已复制  ", fg_color=("white", "black"), 
            corner_radius=6, font=ctk.CTkFont(size=12, weight="bold")
        )
        
        # Bindings
        self.bind("<Button-1>", self.copy_id)
        self.image_label.bind("<Button-1>", self.copy_id)
        
        self.bind("<Enter>", self.on_hover_in)
        self.bind("<Leave>", self.on_hover_out)
        self.image_label.bind("<Enter>", self.on_hover_in)
        self.image_label.bind("<Leave>", self.on_hover_out)
        self.fav_btn.bind("<Enter>", lambda e: HoverPreview.hide()) # Don't hover preview on btn
        
        # Start loading image
        if self.img_id:
            if self.img_id in ImageCard._THUMBNAIL_CACHE:
                self.image_label.configure(image=ImageCard._THUMBNAIL_CACHE[self.img_id], text="")
                self.img_path = self.data_manager.get_image_path(self.img_id) # Should be fast cache hit
            else:
                _thread_pool.submit(self.load_image)
        else:
             self.image_label.configure(text="")
        
    def update_data(self, img_id, desc, is_favorite):
        self.img_id = img_id
        self.desc = desc
        self.is_favorite = is_favorite
        self.img_path = None
        
        # Reset UI to loading
        self.image_label.configure(image="", text="Loading...")
        
        self.fav_btn_text = "❤️" if self.is_favorite else "🤍"
        self.fav_btn.configure(text=self.fav_btn_text)
        
        # Start loading image
        if self.img_id:
            if self.img_id in ImageCard._THUMBNAIL_CACHE:
                self.image_label.configure(image=ImageCard._THUMBNAIL_CACHE[self.img_id], text="")
                self.img_path = self.data_manager.get_image_path(self.img_id) # Should be fast cache hit
            else:
                _thread_pool.submit(self.load_image)
        
    def load_image(self):
        """Loads image file or fetches from URL in background."""
        self.img_path = self.data_manager.get_image_path(self.img_id)
        if self.img_path and os.path.exists(self.img_path):
            try:
                pil_img = Image.open(self.img_path)
                # Resize image to fit square
                pil_img.thumbnail((self.card_size, self.card_size), Image.LANCZOS)
                
                # Create a square background image
                square_img = Image.new("RGBA", (self.card_size, self.card_size), (255, 255, 255, 0))
                offset = ((self.card_size - pil_img.width) // 2, (self.card_size - pil_img.height) // 2)
                square_img.paste(pil_img, offset)
                
                ctk_img = ctk.CTkImage(light_image=square_img, size=(self.card_size, self.card_size))
                ImageCard._THUMBNAIL_CACHE[self.img_id] = ctk_img
                
                if self.winfo_exists():
                    self.after(0, self.update_image, ctk_img)
            except Exception as e:
                print(f"Failed to process image {self.img_id}: {e}")
                if self.winfo_exists():
                    self.after(0, lambda: self.image_label.configure(text="Error"))
        else:
            if self.winfo_exists():
                self.after(0, lambda: self.image_label.configure(text="Error loading"))

    def update_image(self, ctk_img):
        """Updates the widget image main thread."""
        self.image_label.configure(image=ctk_img, text="")

    def copy_id(self, event=None):
        """Copies ID to clipboard with visual feedback."""
        pyperclip.copy(self.img_id)
        # Show toast
        self.toast_label.place(relx=0.5, rely=0.5, anchor="center")
        self.after(1000, self.toast_label.place_forget)

    def toggle_fav(self):
        """Toggles the favorite status."""
        HoverPreview.hide()
        self.is_favorite = self.data_manager.toggle_favorite(self.img_id)
        self.fav_btn_text = "❤️" if self.is_favorite else "🤍"
        self.fav_btn.configure(text=self.fav_btn_text)
        if self.on_favorite_toggle:
            self.on_favorite_toggle(self.img_id, self.is_favorite)

    def on_hover_in(self, event):
        if self.img_path and os.path.exists(self.img_path):
            HoverPreview.show(self, self.img_path, self.card_size + 10)

    def on_hover_out(self, event):
        HoverPreview.hide()
