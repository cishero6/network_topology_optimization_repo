from qgis.PyQt import QtWidgets

class BoundsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Set Capacity Bounds')
        layout = QtWidgets.QFormLayout(self)
        self.lower = QtWidgets.QDoubleSpinBox()
        self.lower.setDecimals(2)
        self.lower.setRange(0.0, 0.999)
        self.lower.setSingleStep(0.01)
        self.upper = QtWidgets.QDoubleSpinBox()
        self.upper.setDecimals(2)
        self.upper.setRange(1.001, 10.0)
        self.upper.setSingleStep(0.01)
        layout.addRow('Lower bound (<1):', self.lower)
        layout.addRow('Upper bound (>1):', self.upper)
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)