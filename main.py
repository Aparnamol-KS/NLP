import re
import sys
import random
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QClipboard, QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QCheckBox, QStatusBar
)

def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', ' ', text)
    # Remove email addresses
    text = re.sub(r'\S+@\S+', ' ', text)
    # Remove variable/script-like patterns
    text = re.sub(r'\bvar\b\s*\w*\s*=?\s*\d*;', ' ', text)
    # Remove HTML entities
    text = re.sub(r'&\w+;', ' ', text)
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', ' ', text)
    # Remove repeated punctuation
    text = re.sub(r'([!?.#\-])\1{1,}', ' ', text)
    # Remove special characters except allowed ones
    text = re.sub(r'[^a-zA-Z0-9\s,.!?\'"-]', ' ', text)
    # Replace multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

FAKE_JARGON = [
    lambda: "→ Reading input...",
    lambda: "→ Removing HTML tags...",
    lambda: "→ Stripping URLs and emails...",
    lambda: "→ Detecting and removing scripts...",
    lambda: "→ Resolving HTML entities...",
    lambda: "→ Cleaning phone numbers...",
    lambda: "→ Removing repeated punctuation...",
    lambda: "→ Removing special characters...",
    lambda: "→ Normalizing spaces...",
    lambda: "→ Finalizing cleaned output..."
]

def random_jargon_line():
    return random.choice(FAKE_JARGON)()

class ElegantTextCleaner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NLP Text Cleaner")
        self.setMinimumSize(1000, 700)
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("NLP Text Cleaner")
        title.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Remove HTML, URLs, emails, special characters, and more with regex")
        subtitle.setFont(QFont("Consolas", 11))
        layout.addWidget(subtitle)

        content_layout = QHBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste messy text here...")
        sample = '''<section>
                        <h1>Welcome to My Portfolio</h1>
                        <p>Hello! Contact me at test@example.com or visit https://mysite.com</p>
                        <p>Call me: 123-456-7890 or var myVar = 10;</p>
                        <footer>&copy; 2025 My Inc.</footer>
                    </section>
                '''
        self.input_text.setText(sample)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Clean text will appear here...")

        content_layout.addWidget(self.input_text)
        content_layout.addWidget(self.output_text)
        layout.addLayout(content_layout)

        button_layout = QHBoxLayout()
        self.remove_btn = QPushButton("Clean Text")
        self.remove_btn.clicked.connect(self.start_processing)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_text)

        self.copy_btn = QPushButton("Copy Output")
        self.copy_btn.clicked.connect(self.copy_output)

        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.copy_btn)
        layout.addLayout(button_layout)

        self.live_preview = QCheckBox("Live Preview")
        self.live_preview.stateChanged.connect(self.toggle_live_preview)
        layout.addWidget(self.live_preview)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        self.console.setStyleSheet("background-color: black; color: lime;")
        layout.addWidget(self.console)

        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        self.preview_timer = QTimer()
        self.preview_timer.setInterval(500)
        self.preview_timer.timeout.connect(lambda: self.process_text(log_steps=False))

    def start_processing(self):
        raw_text = self.input_text.toPlainText().strip()
        if not raw_text:
            self.status_bar.showMessage("No input provided.")
            return

        self.cleaned_pending = clean_text(raw_text)

        self.log_queue = [
            "Starting text cleaning...",
            random_jargon_line(),
            random_jargon_line(),
            f"→ Input length: {len(raw_text)} characters.",
            random_jargon_line(),
            f"→ Output length: {len(self.cleaned_pending)} characters.",
            random_jargon_line(),
            "Processing complete."
        ]

        self.console.clear()
        self.current_log_index = 0

        self.log_timer = QTimer()
        self.log_timer.setInterval(500)
        self.log_timer.timeout.connect(self.show_next_log)
        self.log_timer.start()

    def show_next_log(self):
        if self.current_log_index < len(self.log_queue):
            self.log_console(self.log_queue[self.current_log_index])
            self.current_log_index += 1
        else:
            self.output_text.setPlainText(self.cleaned_pending)
            self.status_bar.showMessage("Processing complete.")
            self.log_timer.stop()

    def log_console(self, message):
        self.console.append(message)
        self.console.moveCursor(QTextCursor.MoveOperation.End)

    def process_text(self, log_steps=True):
        raw_text = self.input_text.toPlainText().strip()
        if not raw_text:
            return
        cleaned = clean_text(raw_text)
        self.output_text.setPlainText(cleaned)

    def clear_text(self):
        self.input_text.clear()
        self.output_text.clear()
        self.console.clear()
        self.status_bar.clearMessage()

    def copy_output(self):
        clipboard: QClipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        self.status_bar.showMessage("Output copied to clipboard")

    def toggle_live_preview(self, state):
        if state == Qt.CheckState.Checked.value:
            self.input_text.textChanged.connect(self.preview_timer.start)
        else:
            self.input_text.textChanged.disconnect(self.preview_timer.start)
            self.preview_timer.stop()

def main():
    app = QApplication(sys.argv)
    win = ElegantTextCleaner()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
