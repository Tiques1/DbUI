import sys
import pyodbc
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QTableView, QLabel, QMessageBox, QDialog, QPushButton, QLineEdit,
                             QFormLayout, QAbstractItemView)
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt6.QtGui import QFont
import os

class DatabaseTableModel(QAbstractTableModel):
    """
    Модель для отображения данных из базы данных в QTableView.
    """
    def __init__(self, data=None, column_names=None, parent=None, table_name=None, con_string=None):  # Добавлено table_name и con_string
        super().__init__(parent)
        self._data = data or []
        self._column_names = column_names or []
        self.table_name = table_name
        self.con_string = con_string

    def set_data(self, data, column_names, table_name):  # Добавлено table_name
        """
        Устанавливает данные для модели.
        """
        self.beginResetModel()
        self._data = data
        self._column_names = column_names
        self.table_name = table_name
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        # +1 для столбца с кнопкой удаления
        return len(self._column_names) + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        # Столбец с кнопкой удаления
        if index.column() == len(self._column_names):
            if role == Qt.ItemDataRole.DisplayRole:
                return ""  # Пустой текст для кнопки
            elif role == Qt.ItemDataRole.DecorationRole:
                return None   #QIcon("path/to/trash_icon.png") - если хотите иконку
            elif role == Qt.ItemDataRole.ToolTipRole:
                return "Удалить запись"
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal:
            if section == len(self._column_names):
                if role == Qt.ItemDataRole.DisplayRole:
                    return ""  # Заголовок для столбца с кнопкой
            elif role == Qt.ItemDataRole.DisplayRole:
                return self._column_names[section]
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        if index.column() == len(self._column_names):
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled  # Кнопка интерактивна

        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def delete_row(self, row):  # Функция для удаления строки
        if self.table_name is None or self.con_string is None:
             QMessageBox.critical(None, "Ошибка", "Не выбрана таблица или не установлена строка подключения.")
             return
        if 0 <= row < len(self._data):
            record_to_delete = self._data[row]
            # Подтверждение удаления
            reply = QMessageBox.question(None, 'Подтверждение удаления',
                f'Вы уверены, что хотите удалить запись?\n{record_to_delete}',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    conn = pyodbc.connect(self.con_string)
                    cursor = conn.cursor()

                    # Создание строки WHERE на основе столбцов и значений записи
                    where_clause = " AND ".join([f"[{self._column_names[i]}] = ?" for i in range(len(self._column_names))])

                    # Создание SQL-запроса для удаления записи
                    sql = f"DELETE FROM [{self.table_name}] WHERE {where_clause}"

                    # Выполнение запроса
                    cursor.execute(sql, record_to_delete)
                    conn.commit()
                    conn.close()

                    QMessageBox.information(None, "Успех", "Запись успешно удалена!")

                    # Обновление данных в модели
                    self.beginRemoveRows(QModelIndex(), row, row)
                    del self._data[row]
                    self.endRemoveRows()
                    self.layoutChanged.emit()

                except pyodbc.Error as e:
                    QMessageBox.critical(None, "Ошибка", f"Ошибка удаления записи: {e}")

from PyQt6.QtCore import QSortFilterProxyModel

class ClickableTableView(QTableView):
    """QTableView с возможностью обработки кликов по ячейкам."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self.handle_click)  # Подключаем сигнал clicked

    def handle_click(self, index):
        """Обрабатывает клик по ячейке."""
        model = index.model()
        # Проверяем, был ли клик по столбцу с кнопкой удаления
        if index.column() == model.columnCount() - 1:
            # Получаем номер строки, по которой кликнули
            row = index.row()
            # Вызываем функцию удаления строки из модели
            model.delete_row(row)  #delete_row определен в DatabaseTableModel

class EditDialog(QDialog):
    """
    Диалоговое окно для редактирования записи.
    """
    def __init__(self, con_string, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать запись")
        self.con_string = con_string
        self.table_name = None
        self.column_names = []
        self.line_edits = {}
        self.form_layout = QFormLayout()
        self.main_layout = QVBoxLayout()
        self.button_box = QHBoxLayout()

        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")
        self.button_box.addWidget(self.save_button)
        self.button_box.addWidget(self.cancel_button)

        self.save_button.clicked.connect(self.save_data)
        self.cancel_button.clicked.connect(self.reject)

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.button_box)
        self.setLayout(self.main_layout)

    def set_table_info(self, table_name, column_names):
        """Устанавливает имя таблицы и имена столбцов."""
        self.table_name = table_name
        self.column_names = column_names
        self.update_form_layout()

    def update_form_layout(self):
        """Обновляет форму с полями ввода для текущей таблицы."""
        # Очистить текущий макет
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.line_edits = {} # Очистить словарь полей ввода

        # Создать новые поля ввода для столбцов
        for column_name in self.column_names:
            line_edit = QLineEdit()
            self.form_layout.addRow(column_name, line_edit)
            self.line_edits[column_name] = line_edit

    def save_data(self):
        """Сохраняет данные в базу данных."""
        if not self.table_name or not self.column_names:
            QMessageBox.warning(self, "Внимание", "Не выбрана таблица.")
            return

        values = []
        for column_name in self.column_names:
            line_edit = self.line_edits[column_name]
            values.append(line_edit.text())

        try:
            conn = pyodbc.connect(self.con_string)
            cursor = conn.cursor()

            placeholders = ', '.join('?' * len(self.column_names))

            sql = f"INSERT INTO [{self.table_name}] ({', '.join(self.column_names)}) VALUES ({placeholders})"

            cursor.execute(sql, values)
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
            self.accept()

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления записи: {e}")


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
        self.table_combo.setFont(QFont("Arial", 12))
        self.table_combo.currentIndexChanged.connect(self.load_table_data)

        self.table_model = DatabaseTableModel()

        # Использовать ClickableTableView вместо QTableView
        self.table_view = ClickableTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Запретить редактирование ячеек

        self.header_label = QLabel("Выберите таблицу:")
        self.header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        hbox = QHBoxLayout()
        hbox.addWidget(self.header_label)

        edit_button = QPushButton("Добавить элемент", parent=self)
        edit_button.clicked.connect(self.edit)
        hbox.addWidget(edit_button)

        hbox.addWidget(self.table_combo)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.table_view)

        self.setLayout(vbox)

        self.load_table_names()
        self.edit_dialog = EditDialog(self.con_string, self) # Создание один раз

    def load_table_names(self):
        """Загружает список таблиц."""
        try:
            conn = pyodbc.connect(self.con_string)
            cursor = conn.cursor()
            tables = [x[2] for x in cursor.tables().fetchall() if x[3] == 'TABLE']
            self.table_combo.addItems(tables[1:])
            conn.close()

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")

    def load_table_data(self, index):
        """Загружает данные из выбранной таблицы."""
        table_name = self.table_combo.currentText()
        try:
            conn = pyodbc.connect(self.con_string)
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM [{table_name}]")
            data = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]

            # Передаем table_name и con_string в модель
            self.table_model.set_data(data, column_names, table_name)
            self.table_model.con_string = self.con_string # Update connection string too
            self.table_name = table_name
            self.column_names = column_names

            # После загрузки данных, подгоняем размеры столбцов под содержимое
            self.table_view.resizeColumnsToContents()

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")

    def edit(self):
        """Открывает диалог редактирования."""
        if self.table_name and self.column_names:
             self.edit_dialog.set_table_info(self.table_name, self.column_names)
             self.edit_dialog.show()
        else:
             QMessageBox.warning(self, "Внимание", "Выберите таблицу сначала")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    abs_path = os.getcwd() + '\\BookStore.mdb'
    con_string = rf'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={abs_path}'

    window = MainWindow(con_string)
    window.show()

    sys.exit(app.exec())