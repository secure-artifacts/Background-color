import customtkinter as ctk
from .image_card import ImageCard

class ImageGrid(ctk.CTkScrollableFrame):
    def __init__(self, master, data_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.data_manager = data_manager
        self.pool = []
        self.active_cards = 0
        self.no_data_lbl = None
        
        self.columns = max(1, self.winfo_width() // 160) # 140 card + 20 padding
        if self.columns == 0: self.columns = 4
        
        self.bind("<Configure>", self.on_resize, add="+")
        self.current_data = {}
        self.showing_favorites = False
        
        # Grid weight config so that it centers
        for i in range(15):
            self.grid_columnconfigure(i, weight=1)

    def render_data(self, image_data, showing_favorites=False):
        """Renders the grid of images."""
        self.current_data = image_data
        self.showing_favorites = showing_favorites
        self.refresh_grid()

    def refresh_grid(self):
        # Reset scroll to top
        try:
            self._parent_canvas.yview_moveto(0)
        except Exception:
            pass
            
        # Hide currently active cards without destroying them
        for card in self.pool[:self.active_cards]:
            card.grid_forget()
            
        if self.no_data_lbl and self.no_data_lbl.winfo_exists():
            self.no_data_lbl.grid_forget()
        
        # If no data
        if not self.current_data:
            if not self.no_data_lbl or not self.no_data_lbl.winfo_exists():
                self.no_data_lbl = ctk.CTkLabel(self, text="这里没有找到任何图片哦~", font=ctk.CTkFont(size=14))
            self.no_data_lbl.grid(row=0, column=0, columnspan=self.columns, pady=50)
            self.active_cards = 0
            return

        self.active_cards = len(self.current_data)
        
        # Ensure our object pool has enough cards
        while len(self.pool) < self.active_cards:
            card = ImageCard(
                self, "", "", False, 
                self.data_manager, self.on_card_favorite_toggled
            )
            self.pool.append(card)

        # Repopulate map with new data
        row = 0
        col = 0
        for i, (img_id, desc) in enumerate(self.current_data.items()):
            is_fav = self.data_manager.is_favorite(img_id)
            card = self.pool[i]
            # Update existing widget data instead of recreating
            card.update_data(img_id, desc, is_fav)
            card.grid(row=row, column=col, padx=10, pady=10)
            
            col += 1
            if col >= self.columns:
                col = 0
                row += 1

    def on_card_favorite_toggled(self, img_id, is_fav):
        """Callback when an image's favorite status is toggled."""
        if self.showing_favorites and not is_fav:
            # If removing from favorites while viewing favorites, remove the card visually
            self.refresh_grid()

    def on_resize(self, event):
        """Responsive grid calculation."""
        # 140 widget width + 20 padding
        new_cols = max(1, event.width // 160)
        if new_cols != self.columns and new_cols > 0:
            self.columns = new_cols
            self.repack_cards()

    def repack_cards(self):
        """Regrid cards when resizing."""
        row = 0
        col = 0
        for i in range(self.active_cards):
            card = self.pool[i]
            card.grid_forget()
            card.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col >= self.columns:
                col = 0
                row += 1
