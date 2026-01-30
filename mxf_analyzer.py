"""
MXF文件分析器 - GUI主程序
使用tkinter实现的图形界面工具
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from mxf_parser import MXFParser


class MXFAnalyzerGUI:
    """MXF分析器GUI应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MXF文件分析器")
        self.root.geometry("1200x800")
        
        self.current_file = None
        self.parser = None
        self.parse_result = None
        
        self._create_widgets()
        self._setup_layout()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="打开MXF文件", command=self.open_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="刷新", command=self.refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="导出报告", command=self.export_report).pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(toolbar, text="未打开文件", foreground="gray")
        self.file_label.pack(side=tk.LEFT, padx=20)
        
        # 主容器 - 使用PanedWindow实现可调整大小的分割
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板 - 文件结构树
        left_frame = ttk.LabelFrame(main_paned, text="文件结构", padding=5)
        main_paned.add(left_frame, weight=1)
        
        # 树形视图
        tree_scroll = ttk.Scrollbar(left_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(left_frame, yscrollcommand=tree_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # 右侧面板 - 详细信息
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # 使用Notebook创建多标签页
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 标签页1: 基本信息
        info_frame = ttk.Frame(self.notebook)
        self.notebook.add(info_frame, text="基本信息")
        
        self.info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, font=("Courier", 10))
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 标签页2: 分区详情
        partition_frame = ttk.Frame(self.notebook)
        self.notebook.add(partition_frame, text="分区详情")
        
        self.partition_text = scrolledtext.ScrolledText(partition_frame, wrap=tk.WORD, font=("Courier", 10))
        self.partition_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 标签页3: 十六进制查看器
        hex_frame = ttk.Frame(self.notebook)
        self.notebook.add(hex_frame, text="十六进制查看")
        
        hex_control = ttk.Frame(hex_frame)
        hex_control.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(hex_control, text="偏移量(十六进制):").pack(side=tk.LEFT, padx=5)
        self.hex_offset_entry = ttk.Entry(hex_control, width=15)
        self.hex_offset_entry.pack(side=tk.LEFT, padx=5)
        self.hex_offset_entry.insert(0, "0")
        
        ttk.Label(hex_control, text="长度:").pack(side=tk.LEFT, padx=5)
        self.hex_length_entry = ttk.Entry(hex_control, width=10)
        self.hex_length_entry.pack(side=tk.LEFT, padx=5)
        self.hex_length_entry.insert(0, "256")
        
        ttk.Button(hex_control, text="查看", command=self.view_hex).pack(side=tk.LEFT, padx=5)
        
        self.hex_text = scrolledtext.ScrolledText(hex_frame, wrap=tk.NONE, font=("Courier", 9))
        self.hex_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 标签页4: 元数据
        metadata_frame = ttk.Frame(self.notebook)
        self.notebook.add(metadata_frame, text="元数据")
        
        self.metadata_text = scrolledtext.ScrolledText(metadata_frame, wrap=tk.WORD, font=("Courier", 10))
        self.metadata_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def _setup_layout(self):
        """设置布局"""
        pass
        
    def open_file(self):
        """打开MXF文件"""
        filepath = filedialog.askopenfilename(
            title="选择MXF文件",
            filetypes=[
                ("MXF文件", "*.mxf"),
                ("所有文件", "*.*")
            ]
        )
        
        if filepath:
            self.load_file(filepath)
            
    def load_file(self, filepath):
        """加载并解析文件"""
        try:
            self.status_bar.config(text=f"正在加载: {os.path.basename(filepath)}...")
            self.root.update()
            
            self.current_file = filepath
            self.parser = MXFParser(filepath)
            self.parse_result = self.parser.parse()
            
            if 'error' in self.parse_result:
                messagebox.showerror("错误", self.parse_result['error'])
                self.status_bar.config(text="加载失败")
                return
            
            # 更新界面
            self.file_label.config(text=os.path.basename(filepath), foreground="black")
            self.update_tree()
            self.update_info()
            self.update_partitions()
            self.update_metadata()
            
            self.status_bar.config(text=f"已加载: {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")
            self.status_bar.config(text="加载失败")
            
    def update_tree(self):
        """更新文件结构树"""
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.parse_result:
            return
        
        # 添加根节点
        root_text = f"MXF文件 ({self.parse_result['file_size_mb']} MB)"
        root_node = self.tree.insert('', 'end', text=root_text, open=True)
        
        # 添加分区节点
        for partition in self.parse_result['partitions']:
            partition_text = f"{partition['type']} @ {partition['offset_hex']}"
            self.tree.insert(root_node, 'end', text=partition_text, 
                           values=(partition['offset'], partition['length']))
        
    def update_info(self):
        """更新基本信息"""
        self.info_text.delete(1.0, tk.END)
        
        if not self.parse_result:
            return
        
        info = f"""文件路径: {self.parse_result['filepath']}
文件大小: {self.parse_result['file_size']:,} 字节 ({self.parse_result['file_size_mb']} MB)
分区数量: {len(self.parse_result['partitions'])}

文件结构:
"""
        
        for idx, partition in enumerate(self.parse_result['partitions'], 1):
            info += f"\n{idx}. {partition['type']}"
            info += f"\n   偏移: {partition['offset_hex']} ({partition['offset']} 字节)"
            info += f"\n   长度: {partition['length']} 字节"
        
        self.info_text.insert(1.0, info)
        
    def update_partitions(self):
        """更新分区详情"""
        self.partition_text.delete(1.0, tk.END)
        
        if not self.parse_result:
            return
        
        for idx, partition in enumerate(self.parse_result['partitions'], 1):
            detail = f"{'='*80}\n"
            detail += f"分区 {idx}: {partition['type']}\n"
            detail += f"{'='*80}\n\n"
            
            # 基本信息
            detail += f"【基本信息】\n"
            detail += f"  偏移量: {partition['offset_hex']} ({partition['offset']:,} 字节)\n"
            detail += f"  长度: {partition['length']:,} 字节\n"
            detail += f"  键值 (UL): {partition['key']}\n"
            
            # 分区包详细信息
            if 'version' in partition:
                detail += f"\n【分区包详细信息】\n"
                detail += f"  MXF版本: {partition['version']}\n"
                
                if 'kag_size' in partition:
                    detail += f"  KAG大小: {partition['kag_size']:,} 字节"
                    if partition.get('kag_size_kb', 0) > 0:
                        detail += f" ({partition['kag_size_kb']} KB)"
                    detail += "\n"
                
                if 'this_partition' in partition:
                    detail += f"  本分区偏移: {partition['this_partition_hex']} ({partition['this_partition']:,} 字节)\n"
                
                if 'previous_partition' in partition:
                    detail += f"  前一分区偏移: {partition['previous_partition_hex']}"
                    if partition['previous_partition'] > 0:
                        detail += f" ({partition['previous_partition']:,} 字节)"
                    detail += "\n"
                
                if 'footer_partition' in partition:
                    detail += f"  Footer分区偏移: {partition['footer_partition_hex']}"
                    if partition['footer_partition'] > 0:
                        detail += f" ({partition['footer_partition']:,} 字节)"
                    detail += "\n"
                
                if 'header_byte_count' in partition:
                    detail += f"  Header字节数: {partition['header_byte_count']:,} 字节\n"
                
                if 'index_byte_count' in partition:
                    detail += f"  Index字节数: {partition['index_byte_count']:,} 字节\n"
                
                if 'index_sid' in partition:
                    detail += f"  Index SID: {partition['index_sid']}\n"
                
                if 'body_offset' in partition:
                    detail += f"  Body偏移: {partition['body_offset_hex']} ({partition['body_offset']:,} 字节)\n"
                
                if 'body_sid' in partition:
                    detail += f"  Body SID: {partition['body_sid']}\n"
                
                # 操作模式
                if 'operational_pattern' in partition:
                    detail += f"\n【操作模式】\n"
                    detail += f"  模式: {partition.get('operational_pattern_name', 'Unknown')}\n"
                    detail += f"  UL: {partition['operational_pattern']}\n"
                
                # Essence Containers
                if 'essence_container_count' in partition:
                    detail += f"\n【Essence Containers】\n"
                    detail += f"  数量: {partition['essence_container_count']}\n"
                    
                    if 'essence_containers' in partition and partition['essence_containers']:
                        for ec_idx, ec in enumerate(partition['essence_containers'], 1):
                            detail += f"  {ec_idx}. {ec['name']}\n"
                            detail += f"     UL: {ec['ul']}\n"
            
            # 内容预览
            if 'content_preview' in partition:
                detail += f"\n【原始数据预览】(前64字节)\n"
                detail += f"{partition['content_preview']}\n"
            
            # 解析错误
            if 'parse_error' in partition:
                detail += f"\n【解析错误】\n"
                detail += f"{partition['parse_error']}\n"
            
            detail += "\n" + "="*80 + "\n\n"
            
            self.partition_text.insert(tk.END, detail)
        
    def update_metadata(self):
        """更新元数据"""
        self.metadata_text.delete(1.0, tk.END)
        
        if not self.parse_result or not self.parse_result['metadata']:
            self.metadata_text.insert(1.0, "暂无元数据信息")
            return
        
        metadata = self.parse_result['metadata']
        
        text = "元数据信息:\n\n"
        
        for key, value in metadata.items():
            if key == 'header_preview':
                text += f"{key}:\n{value}\n\n"
            else:
                text += f"{key}: {value}\n"
        
        self.metadata_text.insert(1.0, text)
        
    def on_tree_select(self, event):
        """树节点选择事件"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values:
                offset = int(values[0])
                self.hex_offset_entry.delete(0, tk.END)
                self.hex_offset_entry.insert(0, hex(offset))
                self.view_hex()
        
    def view_hex(self):
        """查看十六进制"""
        if not self.parser:
            return
        
        try:
            offset_str = self.hex_offset_entry.get()
            offset = int(offset_str, 16) if offset_str.startswith('0x') else int(offset_str)
            length = int(self.hex_length_entry.get())
            
            hex_dump = self.parser.get_hex_dump(offset, length)
            
            self.hex_text.delete(1.0, tk.END)
            self.hex_text.insert(1.0, hex_dump)
            
        except ValueError as e:
            messagebox.showerror("错误", "无效的偏移量或长度")
        except Exception as e:
            messagebox.showerror("错误", f"查看失败: {str(e)}")
        
    def refresh(self):
        """刷新当前文件"""
        if self.current_file:
            self.load_file(self.current_file)
        
    def export_report(self):
        """导出分析报告"""
        if not self.parse_result:
            messagebox.showwarning("警告", "请先打开一个MXF文件")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="保存报告",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("MXF文件分析报告\n")
                    f.write("="*60 + "\n\n")
                    f.write(self.info_text.get(1.0, tk.END))
                    f.write("\n\n" + "="*60 + "\n")
                    f.write("分区详情\n")
                    f.write("="*60 + "\n\n")
                    f.write(self.partition_text.get(1.0, tk.END))
                
                messagebox.showinfo("成功", f"报告已保存到: {filepath}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = MXFAnalyzerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
