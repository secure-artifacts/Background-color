import customtkinter as ctk
import threading
from data_manager import DataManager
from ui.sidebar import Sidebar
from ui.image_grid import ImageGrid

# Set system appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("彩色背景提取工具 (Background Color Viewer)")
        self.geometry("1100x750")
        
        # Setting icon if needed (can be a standard .ico file later)
        # self.iconbitmap("app_icon.ico")
        
        # Configure grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # Initialize Data Manager
        self.data_manager = DataManager()
        
        # Build Sidebar
        self.sidebar = Sidebar(self, self.data_manager, self.on_category_select)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Build Main Frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Build Image Grid
        self.grid_frame = ImageGrid(self.main_frame, self.data_manager)
        self.grid_frame.grid(row=0, column=0, sticky="nsew")
        
        # Loading State Indicator
        self.loading_label = ctk.CTkLabel(self.main_frame, text="正在拉取并同步最新数据...", font=ctk.CTkFont(size=18))
        self.loading_label.grid(row=0, column=0)
        
        # Start data fetch
        threading.Thread(target=self.init_data, daemon=True).start()

    def init_data(self):
        """Fetches data from website in background and updates UI"""
        success = self.data_manager.fetch_latest_data()
        self.after(0, self.on_data_ready, success)

    def on_data_ready(self, success):
        # Remove loading label
        if self.loading_label.winfo_exists():
            self.loading_label.destroy()
            
        if not success and not self.data_manager.data:
            error_lbl = ctk.CTkLabel(self.main_frame, text="初始化失败: 无法连接网络，且没有本地缓存数据。", text_color=("red", "#ff4444"), font=ctk.CTkFont(size=16))
            error_lbl.grid(row=0, column=0)
            return
            
        # Initialize Sidebar with categories
        categories = list(self.data_manager.data.keys())
        first_cat = categories[0] if categories else None
        self.sidebar.render_categories(categories, current_category=first_cat)
        
        # Default load the first category
        if first_cat:
            self.on_category_select(first_cat)

    def on_category_select(self, category):
        """Callback to handle category selection from sidebar"""
        if category == "favorites":
            # Collect favorites from all categories by iterating through existing data
            fav_data = {}
            for cat, items in self.data_manager.data.items():
                for img_id, desc in items.items():
                    if self.data_manager.is_favorite(img_id):
                        fav_data[img_id] = desc
            self.grid_frame.render_data(fav_data, showing_favorites=True)
            self.title(f"彩色背景提取工具 - 我的收藏 ({len(fav_data)}张)")
        else:
            cat_data = self.data_manager.data.get(category, {})
            self.grid_frame.render_data(cat_data, showing_favorites=False)
            cat_name = self.data_manager.get_category_name(category)
            self.title(f"彩色背景提取工具 - {cat_name} ({len(cat_data)}张)")

if __name__ == "__main__":
    app = App()
    app.mainloop()
