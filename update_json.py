import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
from typing import Dict, List, Any
import webbrowser

class BookmarksManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Bookmarks Manager")
        self.root.geometry("1100x600")
        
        # Data storage
        self.bookmarks_data = {"categories": []}
        self.file_path = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # File operations frame
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="Load JSON", command=self.load_file).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(file_frame, text="Save JSON", command=self.save_file).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Save As...", command=self.save_as_file).grid(row=0, column=2, padx=5)
        
        self.file_label = ttk.Label(file_frame, text="No file loaded")
        self.file_label.grid(row=0, column=3, padx=(10, 0))
        
        # Categories frame
        categories_frame = ttk.LabelFrame(main_frame, text="Categories", padding="5")
        categories_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        categories_frame.columnconfigure(0, weight=1)
        categories_frame.rowconfigure(0, weight=1)
        
        # Categories listbox with scrollbar
        categories_list_frame = ttk.Frame(categories_frame)
        categories_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        categories_list_frame.columnconfigure(0, weight=1)
        categories_list_frame.rowconfigure(0, weight=1)
        
        self.categories_listbox = tk.Listbox(categories_list_frame)
        self.categories_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.categories_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        categories_scrollbar = ttk.Scrollbar(categories_list_frame, orient="vertical", command=self.categories_listbox.yview)
        categories_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.categories_listbox.configure(yscrollcommand=categories_scrollbar.set)
        
        # Category buttons
        cat_buttons_frame = ttk.Frame(categories_frame)
        cat_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(cat_buttons_frame, text="Add Category", command=self.add_category).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(cat_buttons_frame, text="Rename", command=self.rename_category).grid(row=0, column=1, padx=2)
        ttk.Button(cat_buttons_frame, text="Delete", command=self.delete_category).grid(row=0, column=2, padx=2)
        ttk.Button(cat_buttons_frame, text="Move Up", command=lambda: self.move_category(-1)).grid(row=0, column=3, padx=2)
        ttk.Button(cat_buttons_frame, text="Move Down", command=lambda: self.move_category(1)).grid(row=0, column=4, padx=(2, 0))
        
        # Links frame
        links_frame = ttk.LabelFrame(main_frame, text="Links", padding="5")
        links_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        links_frame.columnconfigure(0, weight=1)
        links_frame.rowconfigure(0, weight=1)
        
        # Links treeview with scrollbar
        links_tree_frame = ttk.Frame(links_frame)
        links_tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        links_tree_frame.columnconfigure(0, weight=1)
        links_tree_frame.rowconfigure(0, weight=1)
        
        self.links_tree = ttk.Treeview(links_tree_frame, columns=('name', 'url'), show='headings', height=15)
        self.links_tree.heading('name', text='Name')
        self.links_tree.heading('url', text='URL')
        self.links_tree.column('name', width=200)
        self.links_tree.column('url', width=300)
        self.links_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.links_tree.bind('<Double-1>', self.open_link)
        
        links_scrollbar = ttk.Scrollbar(links_tree_frame, orient="vertical", command=self.links_tree.yview)
        links_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.links_tree.configure(yscrollcommand=links_scrollbar.set)
        
        # Link buttons
        links_buttons_frame = ttk.Frame(links_frame)
        links_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(links_buttons_frame, text="Add Link", command=self.add_link).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(links_buttons_frame, text="Edit", command=self.edit_link).grid(row=0, column=1, padx=2)
        ttk.Button(links_buttons_frame, text="Delete", command=self.delete_link).grid(row=0, column=2, padx=2)
        ttk.Button(links_buttons_frame, text="Move Up", command=lambda: self.move_link(-1)).grid(row=0, column=3, padx=2)
        ttk.Button(links_buttons_frame, text="Move Down", command=lambda: self.move_link(1)).grid(row=0, column=4, padx=(2, 0))
        
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Load Bookmarks JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.bookmarks_data = json.load(f)
                
                self.file_path = file_path
                self.file_label.config(text=f"Loaded: {os.path.basename(file_path)}")
                self.refresh_categories()
                messagebox.showinfo("Success", "Bookmarks loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def save_file(self):
        if not self.file_path:
            self.save_as_file()
            return
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", "Bookmarks saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Bookmarks JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=f"File: {os.path.basename(file_path)}")
            self.save_file()
    
    def refresh_categories(self):
        self.categories_listbox.delete(0, tk.END)
        for category in self.bookmarks_data.get('categories', []):
            self.categories_listbox.insert(tk.END, category.get('title', ''))
        
        # Clear links view
        for item in self.links_tree.get_children():
            self.links_tree.delete(item)
    
    def refresh_links(self):
        # Clear current links
        for item in self.links_tree.get_children():
            self.links_tree.delete(item)
        
        # Get selected category
        selection = self.categories_listbox.curselection()
        if not selection:
            return
        
        category_index = selection[0]
        category = self.bookmarks_data['categories'][category_index]
        
        # Add links to tree
        for link in category.get('links', []):
            self.links_tree.insert('', tk.END, values=(link.get('name', ''), link.get('url', '')))
    
    def on_category_select(self, event):
        self.refresh_links()
    
    def add_category(self):
        title = simpledialog.askstring("Add Category", "Enter category title:")
        if title:
            new_category = {"title": title, "links": []}
            self.bookmarks_data['categories'].append(new_category)
            self.refresh_categories()
    
    def rename_category(self):
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to rename.")
            return
        
        category_index = selection[0]
        current_title = self.bookmarks_data['categories'][category_index]['title']
        
        new_title = simpledialog.askstring("Rename Category", "Enter new category title:", initialvalue=current_title)
        if new_title:
            self.bookmarks_data['categories'][category_index]['title'] = new_title
            self.refresh_categories()
            self.categories_listbox.selection_set(category_index)
    
    def delete_category(self):
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to delete.")
            return
        
        category_index = selection[0]
        category_title = self.bookmarks_data['categories'][category_index]['title']
        
        if messagebox.askyesno("Confirm Delete", f"Delete category '{category_title}' and all its links?"):
            del self.bookmarks_data['categories'][category_index]
            self.refresh_categories()
    
    def move_category(self, direction):
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to move.")
            return
        
        current_index = selection[0]
        new_index = current_index + direction
        
        if 0 <= new_index < len(self.bookmarks_data['categories']):
            # Swap categories
            categories = self.bookmarks_data['categories']
            categories[current_index], categories[new_index] = categories[new_index], categories[current_index]
            
            self.refresh_categories()
            self.categories_listbox.selection_set(new_index)
            self.refresh_links()
    
    def add_link(self):
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category first.")
            return
        
        link_dialog = LinkDialog(self.root, "Add Link")
        if link_dialog.result:
            category_index = selection[0]
            self.bookmarks_data['categories'][category_index]['links'].append(link_dialog.result)
            self.refresh_links()
    
    def edit_link(self):
        selection = self.categories_listbox.curselection()
        link_selection = self.links_tree.selection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a category first.")
            return
        
        if not link_selection:
            messagebox.showwarning("Warning", "Please select a link to edit.")
            return
        
        category_index = selection[0]
        link_index = self.links_tree.index(link_selection[0])
        current_link = self.bookmarks_data['categories'][category_index]['links'][link_index]
        
        link_dialog = LinkDialog(self.root, "Edit Link", current_link)
        if link_dialog.result:
            self.bookmarks_data['categories'][category_index]['links'][link_index] = link_dialog.result
            self.refresh_links()
    
    def delete_link(self):
        selection = self.categories_listbox.curselection()
        link_selection = self.links_tree.selection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a category first.")
            return
        
        if not link_selection:
            messagebox.showwarning("Warning", "Please select a link to delete.")
            return
        
        category_index = selection[0]
        link_index = self.links_tree.index(link_selection[0])
        link_name = self.bookmarks_data['categories'][category_index]['links'][link_index]['name']
        
        if messagebox.askyesno("Confirm Delete", f"Delete link '{link_name}'?"):
            del self.bookmarks_data['categories'][category_index]['links'][link_index]
            self.refresh_links()
    
    def move_link(self, direction):
        selection = self.categories_listbox.curselection()
        link_selection = self.links_tree.selection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a category first.")
            return
        
        if not link_selection:
            messagebox.showwarning("Warning", "Please select a link to move.")
            return
        
        category_index = selection[0]
        current_index = self.links_tree.index(link_selection[0])
        new_index = current_index + direction
        
        links = self.bookmarks_data['categories'][category_index]['links']
        if 0 <= new_index < len(links):
            # Swap links
            links[current_index], links[new_index] = links[new_index], links[current_index]
            
            self.refresh_links()
            # Select the moved item
            new_item = self.links_tree.get_children()[new_index]
            self.links_tree.selection_set(new_item)
    
    def open_link(self, event):
        link_selection = self.links_tree.selection()
        if link_selection:
            item = self.links_tree.item(link_selection[0])
            url = item['values'][1]
            webbrowser.open(url)

class LinkDialog:
    def __init__(self, parent, title, initial_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name field
        ttk.Label(main_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # URL field
        ttk.Label(main_frame, text="URL:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Set initial values if provided
        if initial_data:
            self.name_entry.insert(0, initial_data.get('name', ''))
            self.url_entry.insert(0, initial_data.get('url', ''))
        
        # Focus on name entry
        self.name_entry.focus()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def ok_clicked(self):
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Warning", "Please enter a name.")
            return
        
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL.")
            return
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.result = {"name": name, "url": url}
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()

def main():
    root = tk.Tk()
    app = BookmarksManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()