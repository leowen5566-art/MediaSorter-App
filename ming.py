# ... existing code ...
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import platform
from PIL import Image, ImageTk
import cv2

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("Warning: tkinterdnd2 not installed. Drag and drop will be disabled. Install with: pip install tkinterdnd2")

class ModernMediaSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("媒体横竖屏分类重命名工具 - 现代版")
# ... existing code ...
        # State variables
        self.source_dir = ""
        self.target_dir = ""
        self.media_files = [] # Store absolute paths
        self.selected_files_indices = set() # Store indices of selected files (mainly for grid view)
        self.rename_enabled = tk.BooleanVar(value=False)
        self.rename_prefix = tk.StringVar(value="Media")
# ... existing code ...
        self.grid_canvas_window = self.grid_canvas.create_window((0, 0), window=self.grid_inner_frame, anchor="nw")
        self.grid_canvas.bind("<Configure>", self.on_grid_canvas_resize)
        self.grid_canvas.configure(yscrollcommand=self.grid_scrollbar.set)
        
        if HAS_DND:
            self.panel_tl.drop_target_register(DND_FILES)
            self.panel_tl.dnd_bind('<<Drop>>', self.on_drop_files)
        
        self.root.bind('<Delete>', self.on_delete_key)

        self.grid_canvas.pack(side="left", fill="both", expand=True)
        self.grid_scrollbar.pack(side="right", fill="y")
# ... existing code ...
    def switch_view(self):
        if self.view_mode.get() == "list":
            self.view_grid_frame.pack_forget()
            self.view_list_frame.pack(fill="both", expand=True)
            # Sync selection from grid to list if needed
        else:
            self.view_list_frame.pack_forget()
            self.view_grid_frame.pack(fill="both", expand=True)
            self.reflow_grid()

    def on_drop_files(self, event):
        files = self.root.tk.splitlist(event.data)
        new_files = []
        for f in files:
            # tkinterdnd2 sometimes wraps paths in curly braces if they contain spaces
            path = f.strip('{}')
            if os.path.isdir(path):
                # If directory, scan it (non-recursive for now to match behavior)
                for filename in os.listdir(path):
                    filepath = os.path.join(path, filename)
                    if os.path.isfile(filepath):
                        ext = os.path.splitext(filename)[1].lower()
                        if ext in self.image_exts or ext in self.video_exts:
                            if filepath not in self.media_files:
                                new_files.append(filepath)
            elif os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in self.image_exts or ext in self.video_exts:
                    if path not in self.media_files:
                        new_files.append(path)
        
        if new_files:
            self.append_media_files(new_files)

    def on_delete_key(self, event):
        if self.view_mode.get() == "list":
            selected = list(self.file_listbox.curselection())
            if not selected:
                return
            # Delete in reverse order to not mess up indices
            for index in reversed(selected):
                del self.media_files[index]
            self.refresh_listbox_from_data()
        elif self.view_mode.get() == "grid":
            if not self.selected_files_indices:
                return
            indices_to_delete = sorted(list(self.selected_files_indices), reverse=True)
            for index in indices_to_delete:
                if index < len(self.media_files):
                    del self.media_files[index]
            self.selected_files_indices.clear()
            # Need to re-render grid
            self.refresh_all_views_from_data()
            
        self.lbl_source_count.config(text=f"共 {len(self.media_files)} 个媒体文件")
        self.preview_canvas.delete("all")

    def append_media_files(self, new_paths):
        start_idx = len(self.media_files)
        self.media_files.extend(new_paths)
        
        for path in new_paths:
            self.file_listbox.insert(tk.END, os.path.basename(path))
            
        self.lbl_source_count.config(text=f"共 {len(self.media_files)} 个媒体文件")
        
        if not self.stop_thumb_thread and self.thumb_thread and self.thumb_thread.is_alive():
            # If thread is running, let it be. We might need a queue system for dynamic additions.
            # For simplicity here, just restart the thread for new files.
            pass
        
        # Start a thread just for the new files
        new_thread = threading.Thread(target=self._generate_thumbnails_task, args=(new_paths.copy(), start_idx))
        new_thread.daemon = True
        new_thread.start()
        
    def refresh_listbox_from_data(self):
        self.file_listbox.delete(0, tk.END)
        for path in self.media_files:
            self.file_listbox.insert(tk.END, os.path.basename(path))
            
    def refresh_all_views_from_data(self):
        self.refresh_listbox_from_data()
        
        self.stop_thumb_thread = True
        for w in self.thumbnail_widgets:
            w.destroy()
        self.thumbnail_widgets.clear()
        self.thumbnail_cache.clear()
        self.selected_files_indices.clear()
        
        if self.media_files:
            self.stop_thumb_thread = False
            self.thumb_thread = threading.Thread(target=self._generate_thumbnails_task, args=(self.media_files.copy(), 0))
            self.thumb_thread.daemon = True
            self.thumb_thread.start()

    def _create_panel_tr(self):
# ... existing code ...
        # --- View 1: List + Preview ---
        self.view_list_frame = tk.Frame(self.tl_content_area, bg=self.colors["bg_panel"])
        
        # Listbox for files (Enable multiple selection)
        self.file_listbox = tk.Listbox(self.view_list_frame, bg="#1e1e1e", fg=self.colors["text"], selectbackground=self.colors["border"], borderwidth=0, highlightthickness=1, highlightbackground="#444444", selectmode=tk.EXTENDED)
        self.file_listbox.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Preview Canvas
# ... existing code ...
    def _create_panel_bl(self):
        """Bottom-Left Panel: Results log and execute button."""
        header_frame = tk.Frame(self.panel_bl, bg=self.colors["bg_panel"])
        header_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(header_frame, text="4. 结果框与执行", bg=self.colors["bg_panel"], fg=self.colors["text"], font=("Arial", 12, "bold")).pack(side="left")
        
        self.btn_execute = tk.Button(header_frame, text="开始分类并复制", command=self.start_processing_thread, 
                                     bg=self.colors["accent"], fg="white", font=("Arial", 10, "bold"), relief="flat", padx=15, pady=5)
        self.btn_execute.pack(side="right")
        
        self.btn_open_folder = tk.Button(header_frame, text="打开输出文件夹", command=self.open_target_folder, 
                                         bg="#555555", fg="white", font=("Arial", 9), relief="flat", padx=10, pady=5)
        self.btn_open_folder.pack(side="right", padx=(0, 10))
        # Initially disabled until there is a target dir
        self.btn_open_folder.config(state="disabled")
        
        btn_target = tk.Button(header_frame, text="选择保存位置", command=self.browse_target, bg="#555555", fg="white", relief="flat", padx=10)
        btn_target.pack(side="right", padx=(0, 10))

        self.lbl_target_path = tk.Label(self.panel_bl, text="保存至: (未选择)", bg=self.colors["bg_panel"], fg=self.colors["text_dim"], anchor="w")
        self.lbl_target_path.pack(fill="x", pady=(0, 10))

        # Log Text Box
# ... existing code ...
    def browse_target(self):
        folder = filedialog.askdirectory(title="选择保存位置")
        if folder:
            self.target_dir = folder
            self.lbl_target_path.config(text=f"保存至: {folder}")
            self.btn_open_folder.config(state="normal")
            
    def open_target_folder(self):
        if not self.target_dir or not os.path.exists(self.target_dir):
            messagebox.showwarning("提示", "目标文件夹不存在或未设置。")
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(self.target_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.target_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", self.target_dir])
        except Exception as e:
             messagebox.showerror("错误", f"无法打开文件夹: {e}")

    def load_media_files(self):
# ... existing code ...
        self.lbl_source_count.config(text=f"共发现 {len(self.media_files)} 个媒体文件")
        self.log(f"已加载源文件夹: {self.source_dir}", self.colors["text_dim"])

        # 启动后台线程异步生成缩略图，防止卡顿
        if self.media_files:
            self.stop_thumb_thread = False
            # Pass start index 0
            self.thumb_thread = threading.Thread(target=self._generate_thumbnails_task, args=(self.media_files.copy(), 0))
            self.thumb_thread.daemon = True
            self.thumb_thread.start()
# ... existing code ...
    def show_preview(self, filepath):
# ... existing code ...
                # Center the image
                x = (c_width - new_w) // 2
                y = (c_height - new_h) // 2
                self.preview_canvas.create_image(x, y, anchor="nw", image=self.preview_image_ref)
            else:
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(100, 100, text="无法预览", fill="white")
                
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(100, 100, text="预览出错", fill="red")
            print(f"Preview error: {e}")

    def _generate_thumbnails_task(self, files, start_idx):
        for i, filepath in enumerate(files):
            if self.stop_thumb_thread: break
            
            actual_idx = start_idx + i
            ext = os.path.splitext(filepath)[1].lower()
            img_pil = None
            try:
                if ext in self.image_exts:
                    img_pil = Image.open(filepath)
# ... existing code ...
                            img_pil.thumbnail((100, 100))
                    cap.release()
                
                # 利用 .after 将生成好的 PIL 图片安全地传回主线程渲染
                if img_pil and not self.stop_thumb_thread:
                    self.root.after(0, self._add_thumbnail_to_grid, filepath, img_pil, actual_idx)
            except Exception:
                pass

    def _add_thumbnail_to_grid(self, filepath, img_pil, index):
        if self.stop_thumb_thread: return
        
        photo = ImageTk.PhotoImage(img_pil)
        self.thumbnail_cache[filepath] = photo # 防止垃圾回收
        
        frame = tk.Frame(self.grid_inner_frame, bg="#2d2d2d", bd=2, relief="flat", highlightbackground="#444", highlightthickness=1)
        
        lbl_img = tk.Label(frame, image=photo, bg="#000", width=100, height=100)
        lbl_img.pack(padx=3, pady=3)
        
        name = os.path.basename(filepath)
        if len(name) > 12: name = name[:9] + "..." # 截断过长的文件名
        lbl_name = tk.Label(frame, text=name, bg="#2d2d2d", fg="#ccc", font=("Arial", 8))
        lbl_name.pack(padx=2, pady=(0, 3))
        
        # Store index in widget for selection logic
        frame._media_index = index
        
        # Bind click events for selection
        def on_click(evt, f=frame):
            if f._media_index in self.selected_files_indices:
                self.selected_files_indices.remove(f._media_index)
                f.config(bg="#2d2d2d", highlightbackground="#444")
                lbl_name.config(bg="#2d2d2d")
            else:
                self.selected_files_indices.add(f._media_index)
                f.config(bg=self.colors["border"], highlightbackground=self.colors["border"])
                lbl_name.config(bg=self.colors["border"])
            
            # Update preview on click
            if self.media_files and f._media_index < len(self.media_files):
                 self.show_preview(self.media_files[f._media_index])

        lbl_img.bind("<Button-1>", on_click)
        lbl_name.bind("<Button-1>", on_click)
        frame.bind("<Button-1>", on_click)
        
        self.thumbnail_widgets.append(frame)
        
        # 动态计算放入的格子位置
        cols = max(1, self._last_grid_cols)
        idx = len(self.thumbnail_widgets) - 1
        r = idx // cols
        c = idx % cols
        frame.grid(row=r, column=c, padx=5, pady=5)

    def on_grid_canvas_resize(self, event):
# ... existing code ...
        self.is_processing = False
        self.btn_execute.config(state="normal", text="开始分类并复制")
        messagebox.showinfo("完成", "所有文件处理完毕，请查看结果框日志。")
        # Ensure open folder button is visible/enabled if it wasn't
        if self.target_dir:
            self.btn_open_folder.config(state="normal")

if __name__ == "__main__":
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = ModernMediaSorterApp(root)
    root.mainloop()
    
