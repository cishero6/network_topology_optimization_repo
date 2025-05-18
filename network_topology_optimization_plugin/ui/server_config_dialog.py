from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton

class ServerConfigDialog(QDialog):
    def __init__(self, current_url="http://localhost:8000"):
        super().__init__()
        self.setWindowTitle("Server Configuration")
        self.layout = QVBoxLayout()

        self.input = QLineEdit()
        self.input.setText(current_url)
        self.layout.addWidget(self.input)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_btn)

        self.setLayout(self.layout)

    def get_url(self):
        return self.input.text().strip()