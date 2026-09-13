import sys, traceback
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMessageBox
from app.gui.main_window import MainWindow

app = QApplication(sys.argv)
win = MainWindow()

try:
    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No) as mock_q:
        win._on_load_folder("/tmp/errfolder")
    print("dialog shown (false positive GPS confirm):", mock_q.called)
    ds = win._data_manager.dataset
    print("rows:", len(ds))
    print("columns:", ds.column_names())
    print("is_gps:", ds.is_gps())

    # try selecting each column to see if plotting crashes
    for col in ds.column_names():
        win._on_column_selected(col)
        print(f"selected {col} OK, sample:", ds.columns[col][:3])
except Exception:
    traceback.print_exc()
