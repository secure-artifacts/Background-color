import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, data_manager, on_category_select, **kwargs):
        super().__init__(master, width=220, corner_radius=0, **kwargs)
        self.data_manager = data_manager
        self.on_category_select = on_category_select
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="分类目录", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Scrollable area for categories
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=0)
        
        # Buttons list
        self.buttons = []
        
    def render_categories(self, categories, current_category=None):
        """Renders category buttons based on data."""
        # Clear existing buttons
        for _, btn in self.buttons:
            btn.destroy()
        self.buttons.clear()
        
        # Add "Favorites" first
        fav_count = len(self.data_manager.favorites)
        fav_btn = ctk.CTkButton(
            self.scroll_frame, text=f"⭐ 我的收藏 ({fav_count})", anchor="w", 
            fg_color="transparent", text_color=("gray10", "gray90"), 
            hover_color=("gray75", "gray25"), 
            command=lambda: self.select("favorites")
        )
        fav_btn.pack(fill="x", padx=10, pady=2)
        self.buttons.append(('favorites', fav_btn))

        # Add other categories
        for cat_key in categories:
            cat_name = self.data_manager.get_category_name(cat_key)
            cat_count = len(self.data_manager.data.get(cat_key, {}))
            
            btn = ctk.CTkButton(
                self.scroll_frame, text=f"{cat_name} ({cat_count})", anchor="w", 
                fg_color="transparent", text_color=("gray10", "gray90"), 
                hover_color=("gray75", "gray25"), 
                command=lambda k=cat_key: self.select(k)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.buttons.append((cat_key, btn))
            
        if current_category:
            self.highlight_button(current_category)

    def select(self, category):
        self.highlight_button(category)
        self.on_category_select(category)

    def highlight_button(self, category):
        for key, btn in self.buttons:
            if key == category:
                # Highlight active category
                btn.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
                btn.configure(text_color=ctk.ThemeManager.theme["CTkButton"]["text_color"])
            else:
                # Reset others
                btn.configure(fg_color="transparent")
                btn.configure(text_color=("gray10", "gray90"))
