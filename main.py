from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar & add tool bar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar & add status bar elements
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Detect if a cell is selected
        self.table.clicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        insert_dialog = InsertDialog()
        insert_dialog.exec()

    def search(self):
        search_dialog = SearchDialog()
        search_dialog.exec()

    def edit(self):
        edit_dialog = EditDialog()
        edit_dialog.exec()

    def delete(self):
        delete_dialog = DeleteDialog()
        delete_dialog.exec()

    def about(self):
        about_dialog = AboutDialog()
        about_dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.setFixedWidth(50)
        content = "This app was created during the course 'The Python Mega Course'. " \
                  "Feel free to modify and reuse this app."
        self.setText(content)


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        # Get the id of the row selected in the table
        # the student_id will be used to identify which row to delete in the database
        row = main_window.table.currentRow()
        self.student_id = main_window.table.item(row, 0).text()

        # Create widgets
        label = QLabel("Are you sure want to delete this record?")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        yes_button = QPushButton("Yes")
        yes_button.clicked.connect(self.delete_student)
        no_button = QPushButton("No")
        no_button.clicked.connect(self.close)

        # Add widgets to the layout
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0, 1, 1)
        layout.addWidget(no_button, 1, 1, 1, 1)

        self.setLayout(layout)

    def delete_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id=?", (self.student_id,))
        connection.commit()
        cursor.close()
        connection.commit()

        # Update main table
        main_window.load_data()
        # Close delete dialog
        self.close()
        # Create & display a confirmation message prompt
        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Success")
        confirmation_message.setText("Record is deleted successfully!")
        confirmation_message.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        row = main_window.table.currentRow()
        # Get the id of the selected row in the table
        self.id = main_window.table.item(row, 0).text()

        # Create Widgets
        student_name = main_window.table.item(row, 1).text()
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")

        course = main_window.table.item(row, 2).text()
        self.courses_combobox = QComboBox()
        courses_list = ["Biology", "Math", "Astronomy", "Physics"]
        self.courses_combobox.addItems(courses_list)
        self.courses_combobox.setCurrentText(course)

        phone = main_window.table.item(row, 3).text()
        self.phone = QLineEdit(phone)
        self.phone.setPlaceholderText("Phone")

        submit_button = QPushButton("Update")
        submit_button.clicked.connect(self.update_student)

        # Add widgets in layout
        layout.addWidget(self.student_name)
        layout.addWidget(self.courses_combobox)
        layout.addWidget(self.phone)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def update_student(self):
        name = self.student_name.text()
        course = self.courses_combobox.currentText()
        phone = self.phone.text()
        print(self.id, name, course, phone)
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (name, course, phone, self.id))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table
        main_window.load_data()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Create Widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")

        self.courses_combobox = QComboBox()
        courses_list = ["Biology", "Math", "Astronomy", "Physics"]
        self.courses_combobox.addItems(courses_list)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone")

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.add_student)
        submit_button.clicked.connect(self.reset_fields)

        # Add widgets in layout
        layout.addWidget(self.student_name)
        layout.addWidget(self.courses_combobox)
        layout.addWidget(self.phone)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.courses_combobox.currentText()
        mobile = self.phone.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()

    def reset_fields(self):
        self.student_name.setText("")
        self.courses_combobox.setCurrentIndex(0)
        self.phone.setText("")


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        # Create Widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)

        # Add widgets to the layout
        layout.addWidget(self.student_name)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()
        self.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())