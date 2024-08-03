import re
import tkinter as tk

class MarkdownRenderer:
    @staticmethod
    def render(text_widget, markdown_text):
        lines = markdown_text.split('\n')
        in_code_block = False
        code_block = []

        for line in lines:
            if line.startswith('```'):
                if in_code_block:
                    MarkdownRenderer._insert_code_block(text_widget, code_block)
                    code_block = []
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                code_block.append(line)
            else:
                MarkdownRenderer._render_line(text_widget, line)

        if code_block:
            MarkdownRenderer._insert_code_block(text_widget, code_block)

    @staticmethod
    def _render_line(text_widget, line):
        # Headings
        if line.startswith('#'):
            level = len(line.split()[0])  # Count the number of '#' symbols
            text = line.lstrip('#').strip()
            text_widget.insert(tk.END, text + '\n', "heading")
            return

        # Bold
        line = re.sub(r'\*\*(.*?)\*\*', lambda m: text_widget.insert(tk.END, m.group(1), "bold") or '', line)
        
        # Italic
        line = re.sub(r'\*(.*?)\*', lambda m: text_widget.insert(tk.END, m.group(1), "italic") or '', line)
        
        # Inline code
        line = re.sub(r'`(.*?)`', lambda m: text_widget.insert(tk.END, m.group(1), "code") or '', line)

        # Remaining text
        if line:
            text_widget.insert(tk.END, line + '\n')

    @staticmethod
    def _insert_code_block(text_widget, code_block):
        text_widget.insert(tk.END, '\n')
        for line in code_block:
            text_widget.insert(tk.END, line + '\n', "code")
        text_widget.insert(tk.END, '\n')