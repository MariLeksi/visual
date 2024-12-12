import json
import tkinter as tk
from tkinter import messagebox, ttk #всплывающее окна, разные элементы интерфейса

# Загружаем базу данных машин
def load_data():
    #Загружает данные о машинах из файла
    try:
        with open("carsbase.json", "r") as cars:
            return json.load(cars)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Создаем пустой словарь, если файл не найден или содержит ошибку

def save_data(d):
    """Сохраняет данные о машинах в файл."""
    with open("carsbase.json", "w") as cars:
        json.dump(d, cars, indent=2)

class CarManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Машинки")

        self.d = load_data()  # Загружаем данные при инициализации

        self.tree = ttk.Treeview(root, columns=('Номер', 'Марка', 'Цвет', 'Модель двигателя', 'Двери открыты?', 'Фары включены?', 'Место на парковке'), show='headings')
        self.tree.heading('Номер', text='Номер машины')
        self.tree.heading('Марка', text='Марка машины')
        self.tree.heading('Цвет', text='Цвет')
        self.tree.heading('Модель двигателя', text='Модель двигателя')
        self.tree.heading('Двери открыты?', text='Двери открыты?')
        self.tree.heading('Фары включены?', text='Фары включены?')
        self.tree.heading('Место на парковке', text='Место на парковке')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Поле для поиска
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(root, textvariable=self.search_var)
        self.search_entry.pack(padx=5, pady=5)

        # Кнопки поиска и сброса
        search_frame = tk.Frame(root)
        search_frame.pack(pady=5)

        ttk.Button(search_frame, text="Поиск", command=self.search_cars).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Сбросить поиск", command=self.reset_search).pack(side=tk.LEFT, padx=5)

        self.load_cars()

        # Контейнер для кнопок управления автомобилями
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, anchor='sw', padx=10, pady=10)

        # Кнопки управления автомобилями
        ttk.Button(button_frame, text="Добавить машину", command=self.add_car).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Изменить", command=self.edit_car).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Удалить машину", command=self.delete_car).grid(row=0, column=2, padx=5, pady=5)

        # Установка стилей для кнопок
        for btn in button_frame.winfo_children():
            btn.config(width=20)  # Устанавливаем одинаковую ширину для всех кнопок

    def load_cars(self):
        """Загружает данные о машинах в таблицу."""
        self.tree.delete(*self.tree.get_children())  # Очищаем таблицу перед загрузкой
        for index, (key, values) in enumerate(sorted(self.d.items(), key=lambda item: int(item[0]))):
            # Вставляем номер, который будет единым и не изменится при добавлении/удалении
            self.tree.insert('', 'end', values=(index + 1, *values))

    def add_car(self):
        """Добавляет новую машину."""
        self.open_car_dialog("Добавить машину", None)

    def edit_car(self):
        """Редактирует характеристики выбранной машины."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите машину для редактирования.")
            return

        item_id = selected_item[0]  # Получаем идентификатор выбранного элемента
        index = self.tree.index(item_id)  # Номер элемента для базы данных
        item_values = self.d[str(index)]  # Получаем данные для редактирования
        self.open_car_dialog("Изменить характеристики", item_values, index)

    def open_car_dialog(self, title, values, index=None):
        """Открывает диалог для ввода информации о машине."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)

        labels = ["Марка машины", "Цвет", "Модель двигателя", "Двери открыты? (Yes/No)", "Фары включены? (Yes/No)", "Место на парковке"]
        entries = []

        for label in labels:
            frame = tk.Frame(dialog)
            frame.pack(padx=10, pady=5)

            lbl = tk.Label(frame, text=label)
            lbl.pack(side=tk.LEFT)

            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT)
            entries.append(entry)

            if values:  # Если переданы значения, устанавливаем их в поля
                entry.insert(0, values[len(entries)-1])

        def save_changes():
            if any(entry.get() == "" for entry in entries):
                messagebox.showwarning("Ошибка", "Все поля должны быть заполнены.")
                return
            
            new_values = [entry.get() for entry in entries]

            if index is not None:  # Если индекс передан, обновляем существующую запись
                self.d[str(index)] = new_values
                self.tree.item(self.tree.selection()[0], values=(index + 1, *new_values))
            else:  # Иначе добавляем новую запись
                new_key = str(len(self.d))
                self.d[new_key] = new_values
                self.tree.insert('', 'end', values=(len(self.d), *new_values))

            save_data(self.d)
            dialog.destroy()

        save_button = ttk.Button(dialog, text="Сохранить", command=save_changes)
        save_button.pack(pady=10)

    def delete_car(self):
        """Удаляет выбранную машину."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите машину для удаления.")
            return
            
        item_id = selected_item[0]  # Получаем идентификатор выбранного элемента
        index = self.tree.index(item_id)  # Номер для базы данных
        del self.d[str(index)]  # Удаляем из базы данных
        self.tree.delete(item_id)

        # Обновляем ключи в словаре
        updated_d = {}
        for new_index, key in enumerate(sorted(self.d.keys(), key=int)):
            updated_d[str(new_index)] = self.d[key]
        self.d.clear()
        self.d.update(updated_d)
        
        save_data(self.d)

        # Перезагружаем номера машин
        self.load_cars()

    def search_cars(self):
        """Ищет автомобили по определенным характеристикам."""
        search_term = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())  # Очистить текущее содержимое таблицы

        for index, (key, car_values) in enumerate(sorted(self.d.items(), key=lambda item: int(item[0]))):
            if any(search_term in str(value).lower() for value in car_values):
                self.tree.insert('', 'end', values=(index + 1, *car_values))

    def reset_search(self):
        """Сбрасывает результаты поиска и показывает все машины."""
        self.load_cars()
        self.search_var.set('')  # Очищаем строку поиска

if __name__ == "__main__":
    root = tk.Tk()
    app = CarManagementApp(root)
    root.mainloop()