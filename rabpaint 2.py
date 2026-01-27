import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageGrab, ImageDraw
import os
from datetime import datetime

root = tk.Tk()

root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
current_alpha = 1  # Начальная прозрачность
root.attributes('-alpha', current_alpha)

current_color = "black"
last_x, last_y = None, None
eraser_mode = False
eraser_width = 20

preset_colors = {
    '1': 'red',
    '2': 'green',
    '3': 'blue',
    '4': 'yellow',
    '5': 'black',
    '6': 'orange',
    '7': 'purple',
    '8': 'pink',
    '9': 'cyan',
    'q': 'brown',
    'w': 'gray',
    'e': 'gold',
    'r': 'silver',
    't': 'maroon',
    'y': 'olive',
    'u': 'navy',
    'i': 'teal',
    'o': 'lime',
    'p': 'magenta'
}

# ========== МОДУЛЬ УПРАВЛЕНИЯ ПРОЗРАЧНОСТЬЮ ==========

class TransparencyModule:
    """Класс для управления прозрачностью окна"""
    
    def __init__(self, root):
        self.root = root
        self.current_alpha = current_alpha
        self.transparency_window = None
        self.alpha_label = None
        
        # Создаем элементы управления прозрачностью
        self.create_transparency_controls()
    
    def create_transparency_controls(self):
        """Создает элементы для управления прозрачностью"""
        # Фрейм для управления прозрачностью
        self.transparency_frame = tk.Frame(
            root, 
            bg='lightgray', 
            relief='raised', 
            bd=2
        )
        self.transparency_frame.place(x=10, y=220, width=200, height=90)
        
        # Заголовок
        title_label = tk.Label(
            self.transparency_frame,
            text="Прозрачность окна:",
            bg='lightgray',
            font=('Arial', 9, 'bold')
        )
        title_label.pack(pady=(5, 0))
        
        # Слайдер для регулировки прозрачности
        self.alpha_slider = tk.Scale(
            self.transparency_frame,
            from_=1,  # 1% - почти не видно
            to=100,   # 100% - полностью непрозрачно
            orient='horizontal',
            length=180,
            showvalue=True,
            command=self.change_transparency_slider,
            bg='lightgray',
            troughcolor='lightblue',
            sliderrelief='raised',
            resolution=1
        )
        self.alpha_slider.set(int(self.current_alpha * 100))  # Устанавливаем начальное значение
        self.alpha_slider.pack(pady=5, padx=10)
        
        # Кнопка для быстрого сброса
        reset_btn = tk.Button(
            self.transparency_frame,
            text="Сброс (10%)",
            command=self.reset_transparency,
            bg='lightyellow',
            font=('Arial', 8)
        )
        reset_btn.pack(pady=(0, 5))
    
    def change_transparency_slider(self, value):
        """Изменяет прозрачность через слайдер"""
        alpha_value = int(value) / 100.0
        self.set_transparency(alpha_value)
    
    def set_transparency(self, alpha_value):
        """Устанавливает прозрачность окна"""
        # Ограничиваем значение от 0.01 до 1.0
        alpha_value = max(0.01, min(1.0, alpha_value))
        self.current_alpha = alpha_value
        self.root.attributes('-alpha', alpha_value)
        
        # Обновляем слайдер
        if hasattr(self, 'alpha_slider'):
            self.alpha_slider.set(int(alpha_value * 100))
        
        # Обновляем подсказку в информационной метке
        info_label.config(text=f"Прозрачность: {int(alpha_value*100)}% | F1 - справка | Esc - свернуть")
    
    def increase_transparency(self, step=0.05):
        """Увеличивает прозрачность (делает окно более видимым)"""
        new_alpha = min(1.0, self.current_alpha + step)
        self.set_transparency(new_alpha)
    
    def decrease_transparency(self, step=0.05):
        """Уменьшает прозрачность (делает окно более прозрачным)"""
        new_alpha = max(0.05, self.current_alpha - step)
        self.set_transparency(new_alpha)
    
    def reset_transparency(self):
        """Сбрасывает прозрачность к значению по умолчанию (10%)"""
        self.set_transparency(0.1)
    
    def toggle_transparency_mode(self):
        """Переключает между режимами прозрачности"""
        if self.current_alpha < 0.3:
            # Если окно почти прозрачное, делаем его видимым
            self.set_transparency(0.8)
        elif self.current_alpha > 0.7:
            # Если окно почти непрозрачное, делаем его едва видимым
            self.set_transparency(0.1)
    
    def show_transparency_info(self):
        """Показывает информацию о текущей прозрачности"""
        messagebox.showinfo(
            "Прозрачность окна",
            f"Текущая прозрачность: {int(self.current_alpha * 100)}%\n\n"
            "Горячие клавиши:\n"
            "[ или - : Уменьшить прозрачность\n"
            "] или + : Увеличить прозрачность\n"
            "0 : Сбросить к 10%\n"
            "T : Переключить режимы\n\n"
            "Совет: Используйте низкую прозрачность\n"
            "для рисования поверх других окон."
        )

# ========== МОДУЛЬ ПОДСКАЗОК ==========

class HelpModule:
    """Класс для управления подсказками и справкой"""
    
    def __init__(self, root):
        self.root = root
        self.help_window = None
        self.showing_tooltip = False
        self.tooltip_window = None
        
        # Создаем кнопку помощи
        self.create_help_button()
        
        # Создаем контекстные подсказки для элементов
        self.create_context_tooltips()
    
    def create_help_button(self):
        """Создает кнопку вызова справки"""
        self.help_btn = tk.Button(
            root, 
            text="❓ Помощь", 
            command=self.show_help_window,
            bg='lightblue',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=2
        )
        self.help_btn.place(x=10, y=320, width=100, height=30)
    
    def show_help_window(self):
        """Показывает окно справки"""
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.lift()
            return
        
        self.help_window = Toplevel(root)
        self.help_window.title("Справка - Графический редактор")
        self.help_window.geometry("600x550")
        self.help_window.resizable(True, True)
        self.help_window.configure(bg='white')
        
        # Делаем окно поверх других
        self.help_window.attributes('-topmost', True)
        
        # Создаем текстовое поле с прокруткой
        text_frame = tk.Frame(self.help_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        help_text = tk.Text(
            text_frame, 
            wrap='word', 
            yscrollcommand=scrollbar.set,
            font=('Arial', 10),
            bg='white',
            padx=10,
            pady=10
        )
        help_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=help_text.yview)
        
        # Вставляем текст справки
        help_content = self.generate_help_content()
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')  # Только для чтения
        
        # Кнопка закрытия
        close_btn = tk.Button(
            self.help_window,
            text="Закрыть справку",
            command=self.help_window.destroy,
            bg='lightgray',
            font=('Arial', 10)
        )
        close_btn.pack(pady=10)
    
    def generate_help_content(self):
        """Генерирует текст справки с информацией о прозрачности"""
        return f"""
╔══════════════════════════════════╗
║        ГРАФИЧЕСКИЙ РЕДАКТОР - СПРАВКА       ║            
╚══════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 ОСНОВНЫЕ ВОЗМОЖНОСТИ:
• Рисование мышью с различными цветами
• Режим ластика для удаления нарисованного
• Настройка прозрачности окна
• Сохранение рисунков в разных форматах
• Копирование в буфер обмена
• Работа поверх всех окон

Текущая прозрачность: {int(current_alpha * 100)}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖱️ УПРАВЛЕНИЕ МЫШЬЮ:
• ЛКМ и перетаскивание - рисование
• Используйте ластик для исправлений

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⌨️ ГОРЯЧИЕ КЛАВИШИ - ЦВЕТА:
1 - Красный         6 - Оранжевый
2 - Зеленый         7 - Фиолетовый
3 - Синий           8 - Розовый
4 - Желтый          9 - Голубой
5 - Черный          0 - Белый

Q - Коричневый      U - Темно-синий
W - Серый           I - Бирюзовый
E - Золотой         O - Лаймовый
R - Серебряный      P - Пурпурный
T - Бордовый
Y - Оливковый

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎛️ ГОРЯЧИЕ КЛАВИШИ - ПРОЗРАЧНОСТЬ:
[ или -   : Уменьшить прозрачность (сделать виднее)
] или +   : Увеличить прозрачность (сделать прозрачнее)
0         : Сбросить к 10%
T         : Переключить режимы (10% ↔ 80%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⌨️ ГОРЯЧИЕ КЛАВИШИ - ИНСТРУМЕНТЫ:
S - Включить ластик         Ctrl+S - Сохранить как...
D - Выключить ластик        Ctrl+Q - Быстрое сохранение
C - Очистить холст          Ctrl+C - Копировать в буфер
                            Ctrl+P - Сохранить как PDF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⌨️ СИСТЕМНЫЕ КЛАВИШИ:
Esc - Свернуть/развернуть окно
F1  - Показать эту справку
F2  - Информация о прозрачности

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 СОХРАНЕНИЕ:
• Все рисунки сохраняются в папку 'drawings'
• Автоматические имена содержат дату и время
• Поддерживаются форматы: PNG, JPEG, GIF, BMP, PDF
• Быстрое сохранение: Ctrl+Q

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 СОВЕТЫ ПО ПРОЗРАЧНОСТИ:
1. Низкая прозрачность (10-30%) - для рисования поверх окон
2. Средняя прозрачность (40-60%) - для выделения областей
3. Высокая прозрачность (70-100%) - для основного рисования
4. Используйте T для быстрого переключения режимов

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 ПОДДЕРЖКА:
Программа разработана для удобного рисования поверх любых окон.
Для закрытия программы используйте Alt+F4 или меню Файл → Выход.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def create_context_tooltips(self):
        """Создает контекстные подсказки для элементов интерфейса"""
        # Словарь с подсказками для элементов
        self.tooltips = {
            color_display: "Текущий цвет/инструмент\nS - ластик, D - кисть",
            control_frame: "Панель сохранения\nИспользуйте кнопки или горячие клавиши",
            canvas: "Область рисования\nЛКМ - рисовать, перетаскивать - линия",
            transparency_module.transparency_frame: "Управление прозрачностью\n[ ] - регулировать, T - переключить"
        }
        
        # Привязываем события наведения
        for widget, tip_text in self.tooltips.items():
            widget.bind('<Enter>', lambda e, text=tip_text: self.show_tooltip(e, text))
            widget.bind('<Leave>', self.hide_tooltip)
    
    def show_tooltip(self, event, text):
        """Показывает всплывающую подсказку"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
        
        self.tooltip_window = Toplevel(root)
        self.tooltip_window.wm_overrideredirect(True)  # Без рамки
        
        # Позиционируем подсказку рядом с курсором
        x = event.x_root + 20
        y = event.y_root + 10
        
        self.tooltip_window.geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window, 
            text=text,
            justify='left',
            background='lightyellow',
            relief='solid',
            borderwidth=1,
            font=('Arial', 9),
            padx=5,
            pady=2
        )
        label.pack()
        
        self.showing_tooltip = True
    
    def hide_tooltip(self, event=None):
        """Скрывает всплывающую подсказку"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            self.showing_tooltip = False

# ========== ОСТАЛЬНЫЕ ФУНКЦИИ ==========

def change_color(event):
    global current_color, eraser_mode
    key = event.keysym
    if key in preset_colors:
        current_color = preset_colors[key]
        eraser_mode = False
        update_color_display()

def toggle_minimize():
    if root.state() == 'iconic':
        root.deiconify()
    else:
        root.iconify()

# ... (функции сохранения остаются без изменений) ...

def save_canvas():
    if not os.path.exists("drawings"):
        os.makedirs("drawings")
    
    filetypes = [
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg;*.jpeg"),
        ("GIF files", "*.gif"),
        ("BMP files", "*.bmp"),
        ("All files", "*.*")
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"drawings/drawing_{timestamp}.png"
    
    filename = filedialog.asksaveasfilename(
        title="Сохранить рисунок",
        defaultextension=".png",
        initialfile=f"drawing_{timestamp}",
        initialdir="drawings",
        filetypes=filetypes
    )
    
    if filename:
        save_image(filename)

def quick_save():
    if not os.path.exists("drawings"):
        os.makedirs("drawings")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"drawings/drawing_{timestamp}.png"
    
    if save_image(filename):
        messagebox.showinfo("Сохранено", f"Рисунок сохранен как:\n{filename}")

def save_image(filename):
    try:
        x = root.winfo_rootx() + canvas.winfo_x()
        y = root.winfo_rooty() + canvas.winfo_y()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()
        
        screenshot = ImageGrab.grab(bbox=(x, y, x1, y1))
        screenshot.save(filename)
        return True
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
        return False

def copy_to_clipboard():
    try:
        x = root.winfo_rootx() + canvas.winfo_x()
        y = root.winfo_rooty() + canvas.winfo_y()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()
        
        screenshot = ImageGrab.grab(bbox=(x, y, x1, y1))
        
        import io
        import win32clipboard
        
        output = io.BytesIO()
        screenshot.convert('RGB').save(output, 'BMP')
        data = output.getvalue()[14:]
        output.close()
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        
        messagebox.showinfo("Скопировано", "Рисунок скопирован в буфер обмена!")
        
    except ImportError:
        messagebox.showwarning("Ошибка", "Для копирования в буфер обмена нужна библиотека pywin32")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось скопировать:\n{str(e)}")

def save_as_pdf():
    try:
        from PIL import Image
        
        if not os.path.exists("drawings"):
            os.makedirs("drawings")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"drawings/drawing_{timestamp}.pdf"
        
        x = root.winfo_rootx() + canvas.winfo_x()
        y = root.winfo_rooty() + canvas.winfo_y()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()
        
        screenshot = ImageGrab.grab(bbox=(x, y, x1, y1))
        rgb_screenshot = screenshot.convert('RGB')
        rgb_screenshot.save(filename, "PDF", resolution=100.0)
        
        messagebox.showinfo("Сохранено", f"PDF сохранен как:\n{filename}")
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить PDF:\n{str(e)}")

def on_key_press(event):
    global eraser_mode
    
    # Обработка клавиш прозрачности
    if event.keysym in ['bracketleft', 'minus']:  # [ или -
        transparency_module.decrease_transparency()
        return
    elif event.keysym in ['bracketright', 'plus']:  # ] или +
        transparency_module.increase_transparency()
        return
    elif event.keysym == '0':
        transparency_module.reset_transparency()
        return
    elif event.keysym.lower() == 'a':
        transparency_module.toggle_transparency_mode()
        return
    
    # Добавляем F2 для информации о прозрачности
    if event.keysym == 'F2':
        transparency_module.show_transparency_info()
        return
    
    # Добавляем F1 для вызова справки
    if event.keysym == 'F1':
        help_module.show_help_window()
        return
    
    if event.keysym == 'Escape':
        toggle_minimize()
    elif event.keysym in preset_colors:
        change_color(event)
    elif event.keysym.lower() == 's':
        if event.state & 0x0004:
            save_canvas()
        else:
            eraser_mode = True
            update_color_display()
    elif event.keysym.lower() == 'd':
        eraser_mode = False
        update_color_display()
    elif event.keysym.lower() == 'c':
        if event.state & 0x0004:
            copy_to_clipboard()
        else:
            canvas.delete("all")
            update_color_display()
    elif event.keysym.lower() == 'q':
        if event.state & 0x0004:
            quick_save()
    elif event.keysym.lower() == 'p':
        if event.state & 0x0004:
            save_as_pdf()

# ========== СОЗДАНИЕ ИНТЕРФЕЙСА ==========

canvas = tk.Canvas(root, bg='white', highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

color_display = tk.Label(root, text="      ", bg=current_color, relief='raised')
color_display.place(x=10, y=10)

def update_color_display():
    if eraser_mode:
        color_display.config(bg='white', text='СТИРКА', font=('Arial', 10, 'bold'))
    else:
        color_display.config(bg=current_color, text="      ", font=('Arial', 8))

control_frame = tk.Frame(root, bg='lightgray', relief='raised', bd=2)
control_frame.place(x=10, y=40, width=200, height=100)

save_btn = tk.Button(control_frame, text="Сохранить (Ctrl+S)", command=save_canvas, 
                     bg='lightblue', font=('Arial', 9))
save_btn.pack(fill='x', padx=5, pady=2)

quick_save_btn = tk.Button(control_frame, text="Быстрое сохранение", command=quick_save,
                          bg='lightgreen', font=('Arial', 9))
quick_save_btn.pack(fill='x', padx=5, pady=2)

copy_btn = tk.Button(control_frame, text="Копировать (Ctrl+C)", command=copy_to_clipboard,
                    bg='lightyellow', font=('Arial', 9))
copy_btn.pack(fill='x', padx=5, pady=2)

info_label = tk.Label(root, 
                     text=f"Прозрачность: {int(current_alpha*100)}% | F1 - справка | Esc - свернуть", 
                     bg='lightgray', font=('Arial', 8))
info_label.place(x=10, y=150)

# ========== ИНИЦИАЛИЗАЦИЯ МОДУЛЕЙ ==========

# Сначала создаем модуль прозрачности
transparency_module = TransparencyModule(root)

# Затем модуль помощи
help_module = HelpModule(root)

# ========== ПРИВЯЗКА СОБЫТИЙ ==========

def on_button_press(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def on_move_press(event):
    global last_x, last_y
    if last_x is not None and last_y is not None:
        line_width = eraser_width if eraser_mode else 3
        line_color = 'white' if eraser_mode else current_color
        canvas.create_line(last_x, last_y, event.x, event.y, fill=line_color, width=line_width)
        last_x, last_y = event.x, event.y

def on_button_release(event):
    global last_x, last_y
    last_x, last_y = None, None

canvas.bind('<ButtonPress-1>', on_button_press)
canvas.bind('<B1-Motion>', on_move_press)
canvas.bind('<ButtonRelease-1>', on_button_release)

root.bind_all('<Key>', on_key_press)

update_color_display()

# ========== МЕНЮ ==========

menubar = tk.Menu(root)

# Меню "Файл"
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Сохранить как...", command=save_canvas, accelerator="Ctrl+S")
filemenu.add_command(label="Быстрое сохранение", command=quick_save, accelerator="Ctrl+Q")
filemenu.add_command(label="Копировать в буфер", command=copy_to_clipboard, accelerator="Ctrl+C")
filemenu.add_command(label="Сохранить как PDF", command=save_as_pdf, accelerator="Ctrl+P")
filemenu.add_separator()
filemenu.add_command(label="Очистить холст", command=lambda: canvas.delete("all"))
filemenu.add_separator()
filemenu.add_command(label="Выход", command=root.quit)
menubar.add_cascade(label="Файл", menu=filemenu)

# Меню "Настройки"
settingsmenu = tk.Menu(menubar, tearoff=0)
settingsmenu.add_command(label="Управление прозрачностью", 
                         command=transparency_module.show_transparency_info,
                         accelerator="F2")
settingsmenu.add_separator()
settingsmenu.add_command(label="Увеличить прозрачность", 
                         command=lambda: transparency_module.increase_transparency(),
                         accelerator="]")
settingsmenu.add_command(label="Уменьшить прозрачность", 
                         command=lambda: transparency_module.decrease_transparency(),
                         accelerator="[")
settingsmenu.add_command(label="Сбросить прозрачность", 
                         command=transparency_module.reset_transparency,
                         accelerator="0")
settingsmenu.add_command(label="Переключить режим", 
                         command=transparency_module.toggle_transparency_mode,
                         accelerator="T")
menubar.add_cascade(label="Настройки", menu=settingsmenu)

# Меню "Справка"
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Открыть справку", command=help_module.show_help_window, accelerator="F1")
helpmenu.add_command(label="Информация о прозрачности", 
                     command=transparency_module.show_transparency_info,
                     accelerator="F2")
menubar.add_cascade(label="Справка", menu=helpmenu)

root.config(menu=menubar)

# ========== ЗАПУСК ПРОГРАММЫ ==========

root.mainloop()