import sys
import pyodbc
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QTableView, QLabel, QMessageBox)
from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtGui import QFont
import os

class DatabaseTableModel(QAbstractTableModel):
    """
    Модель для отображения данных из базы данных в QTableView.
    """
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data or []
        self._column_names = []

    def set_data(self, data, column_names):
        """
        Устанавливает данные для модели.
        """
        self.beginResetModel()
        self._data = data
        self._column_names = column_names
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._column_names)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._column_names[section]
        return None

class MainWindow(QWidget):
    """
    Основное окно приложения.
    """
    def __init__(self, con_string):
        super().__init__()
        self.con_string = con_string
        self.setWindowTitle("Database Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.table_combo = QComboBox()
        self.table_combo.setFont(QFont("Arial", 12))  # Set font for the combo box
        self.table_combo.currentIndexChanged.connect(self.load_table_data)

        self.table_model = DatabaseTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)

        # Заголовок
        self.header_label = QLabel("Выберите таблицу:")
        self.header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))  # Устанавливаем шрифт

        # Разметка
        hbox = QHBoxLayout()
        hbox.addWidget(self.header_label)
        hbox.addWidget(self.table_combo)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.table_view)

        self.setLayout(vbox)

        self.load_table_names()

    def load_table_names(self):
        """
        Загружает список таблиц из базы данных и заполняет QComboBox.
        """
        try:
            conn = pyodbc.connect(self.con_string)
            cursor = conn.cursor()

            # SQL запрос для получения списка таблиц (для MS Access)
            tables = [x[2] for x in cursor.tables().fetchall() if x[3] == 'TABLE']

            self.table_combo.addItems(tables)
            conn.close()

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения или получения списка таблиц: {e}")

    def load_table_data(self, index):
        """
        Загружает данные из выбранной таблицы и отображает их в QTableView.
        """
        table_name = self.table_combo.currentText()
        try:
            conn = pyodbc.connect(self.con_string)
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM [{table_name}]")
            data = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]  # Получаем имена столбцов

            self.table_model.set_data(data, column_names) # Устанавливаем данные и имена столбцов

            conn.close()

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных из таблицы '{table_name}': {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    abs_path = os.getcwd() + '\\BookStore.accdb'

    con_string = rf'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={abs_path};CHARSET=UTF8'

    window = MainWindow(con_string)
    window.show()

    sys.exit(app.exec())