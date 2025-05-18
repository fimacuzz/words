from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.audio import SoundLoader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.relativelayout import RelativeLayout
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.uix.textfield import MDTextField
import random
import json
import Levenshtein
from kivy.uix.textinput import TextInput



MAX_WORDS = 227
MIN_WORDS = 10
LabelBase.register(name="ARCO", fn_regular="ofont.ru_Arco.ttf")


class SplashScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = Image(
            source="1e38af17-d5f2-4b31-8612-66fec8849ea7.png",
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.image)
        Clock.schedule_once(self.goto_home, 2.5)

    def goto_home(self, dt):
        self.manager.current = "home"


class HomeScreen(MDScreen):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager

        root = RelativeLayout()
        self.add_widget(root)

        # Фон
        bg = Image(source="fon.png", allow_stretch=True, keep_ratio=False)
        root.add_widget(bg)

        # Главный вертикальный контейнер
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=[dp(40), dp(40), dp(40), dp(40)]
        )

        # === Заголовки в отдельной секции ===
        header_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(140),
            spacing=dp(5),
            padding=[0, dp(10), 0, 0]
        )

        vocabulary_label = Label(
            text="СЛОВАРНЫЙ",
            halign="center",
            valign="middle",
            font_name="ARCO",
            font_size="40sp",
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(60)
        )

        dictation_label = Label(
            text="ДИКТАНТ",
            halign="center",
            valign="middle",
            font_name="ARCO",
            font_size="40sp",
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(60)
        )

        header_layout.add_widget(vocabulary_label)
        header_layout.add_widget(dictation_label)

        # === Ввод и кнопка ===
        input_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint=(0.8, None),
            height=dp(150),
            pos_hint={"center_x": 0.5}
        )
        self.word_count_input = MDTextField(
            hint_text="ВВЕДИ КОЛ-ВО СЛОВ (МАКС 227)",
            font_name="ARCO",
            font_size="24sp",
            mode="rectangle",
            line_color_normal=(1, 1, 1, 1),
            line_color_focus=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(60)
        )
        self.word_count_input = TextInput(
            hint_text="ВВЕДИ КОЛ-ВО СЛОВ (МАКС 227)",
            font_name="ARCO",
            font_size="24sp",
            foreground_color=(1, 1, 1, 1),  # ← Цвет текста
            background_color=(0, 0, 0, 0),  # ← Прозрачный фон
            cursor_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(60)
        )
        # Устанавливаем цвет текста после создания поля
        self.word_count_input.text_color = (1, 1, 1, 1)

        self.start_button = MDRaisedButton(
            text="НАЧАТЬ",
            font_name="ARCO",
            font_size="30sp",
            md_bg_color=(0.2, 0.6, 0.86, 1),
            text_color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(70),
            on_release=self.start_test
        )


        input_container.add_widget(self.word_count_input)
        input_container.add_widget(self.start_button)

        # Добавление в основной layout
        main_layout.add_widget(header_layout)
        main_layout.add_widget(Widget())  # Пустое пространство между заголовком и центром
        main_layout.add_widget(input_container)
        main_layout.add_widget(Widget())  # Пустое пространство внизу

        root.add_widget(main_layout)

    def start_test(self, instance):
        count_str = self.word_count_input.text.strip()
        if not count_str.isdigit():
            self.show_dialog("Введите число")
            return
        count = int(count_str)
        if count < MIN_WORDS or count > MAX_WORDS:
            self.show_dialog(f"Введите от {MIN_WORDS} до {MAX_WORDS} слов")
        else:
            self.screen_manager.get_screen("dictation").init_test(count)
            self.screen_manager.current = "dictation"

    def show_dialog(self, text):
        dialog = MDDialog(title="Ошибка", text=text, size_hint=(0.8, 0.3))
        dialog.open()



class DictationScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.word_list = []
        self.user_answers = []
        self.current_index = 0

        root = RelativeLayout()

        bg = Image(source="fon.png", allow_stretch=True, keep_ratio=False)
        root.add_widget(bg)

        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=30,
            padding=[dp(40), dp(40), dp(40), dp(40)],
            size_hint=(None, None),
            width=dp(600),
            pos_hint={"center_x": 0.5, "top": 1}
        )

        main_layout.bind(minimum_height=main_layout.setter('height'))

        header = Label(
            text="СЛУШАТЬ СЛОВО",
            halign="center",
            font_name="ARCO",
            font_size="45sp",
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(100)
        )

        self.play_button = MDRaisedButton(
            text="СЛУШАТЬ",
            font_name="ARCO",
            font_size="35sp",
            md_bg_color=(0.2, 0.6, 0.86, 1),
            size_hint=(0.8, None),
            height=dp(80),
            on_release=self.play_word
        )

        self.text_input = MDTextField(
            font_name="ARCO",
            font_size="30sp",

            mode="rectangle",
            line_color_normal=(1, 1, 1, 1),
            size_hint=(0.9, None),
            height=dp(80)

        )

        self.next_button = MDRaisedButton(
            text="ДАЛЕЕ",
            font_name="ARCO",
            font_size="30sp",
            md_bg_color=(0.3, 0.7, 0.9, 1),
            size_hint=(0.6, None),
            height=dp(70),
            on_release=self.next_word
        )

        main_layout.add_widget(header)
        main_layout.add_widget(self.play_button)
        main_layout.add_widget(self.text_input)
        main_layout.add_widget(self.next_button)
        main_layout.add_widget(self.create_keyboard())

        scroll = ScrollView()
        scroll.add_widget(main_layout)
        root.add_widget(scroll)
        self.add_widget(root)

    def init_test(self, count):
        with open("wordlist.json", "r", encoding="utf-8") as f:
            full_list = list(json.load(f).items())
        self.word_list = random.sample(full_list, count)
        self.user_answers = []
        self.current_index = 0
        self.text_input.text = ""

    def play_word(self, *args):
        if self.current_index < len(self.word_list):
            key, _ = self.word_list[self.current_index]
            sound = SoundLoader.load(f"words/{key}.mp3")
            if sound:
                sound.play()

    def next_word(self, *args):
        user_word = self.text_input.text.strip().lower()
        self.user_answers.append(user_word)
        self.text_input.text = ""
        self.current_index += 1

        if self.current_index >= len(self.word_list):
            self.finish_test()
        else:
            # Автоматически проигрываем следующее слово
            self.play_word()

    def finish_test(self):
        result_text = []
        correct_count = 0
        for i, (key, correct_word) in enumerate(self.word_list):
            user_word = self.user_answers[i]
            correct_word_lower = correct_word.lower()
            if user_word == correct_word_lower:
                correct_count += 1
                result_text.append(f"[color=00ff00]{i + 1}. ✓ {correct_word}[/color]")
            else:
                dist = Levenshtein.distance(user_word, correct_word_lower)
                result_text.append(f"[color=ff0000]{i + 1}. ✗ {user_word} → {correct_word} (Ошибок: {dist})[/color]")

        result_summary = (
            f"[b][size=20]ПРАВИЛЬНЫХ ОТВЕТОВ: {correct_count} ИЗ {len(self.word_list)}[/size][/b]\n"
            + "\n".join(result_text)
        )

        result_screen = self.manager.get_screen('results')
        result_screen.show_results(result_summary)
        self.manager.current = 'results'



    def create_keyboard(self):
        russian_keys = [
            list("ЙЦУКЕНГШЩЗХ"),
            list("ФЫВАПРОЛДЖЭ"),
            list("ЯЧСМИТЬБЮ")
        ]

        keyboard_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint=(None, None),
            width=dp(500),  # или подбери нужную ширину
            pos_hint={"center_x": 0.5},
            padding=[10, 10]
        )

        keyboard_layout.bind(minimum_height=keyboard_layout.setter('height'))

        for row in russian_keys:
            row_layout = GridLayout(
                cols=len(row),
                spacing=8,
                size_hint_y=None,
                height=50
            )
            for char in row:
                btn = MDRaisedButton(
                    text=char,
                    font_name="ARCO",
                    font_size="20sp",
                    on_release=self.insert_char,
                    md_bg_color=(0.3, 0.3, 0.3, 1),  # Темнее цвет кнопок
                    text_color=(1, 1, 1, 1),
                    size_hint=(None, None),
                    size=("40dp", "40dp"),
                    elevation=2
                )
                row_layout.add_widget(btn)
            keyboard_layout.add_widget(row_layout)

        control_row = GridLayout(
            cols=2,
            spacing=8,
            size_hint_y=None,
            height=50
        )
        space_btn = MDRaisedButton(
            text="Пробел",
            font_name="ARCO",
            font_size="18sp",
            on_release=lambda x: self.insert_text(" "),
            md_bg_color=(0.3, 0.3, 0.3, 1),
            text_color=(1, 1, 1, 1),
            size_hint=(0.7, None),
            height=40,
            elevation=2
        )
        backspace_btn = MDRaisedButton(
            text="СТЕРЕТЬ",
            font_name="ARCO",
            font_size="18sp",
            on_release=self.backspace,
            md_bg_color=(0.3, 0.3, 0.3, 1),
            text_color=(1, 1, 1, 1),
            size_hint=(0.3, None),
            height=40,
            elevation=2
        )
        control_row.add_widget(space_btn)
        control_row.add_widget(backspace_btn)
        keyboard_layout.add_widget(control_row)

        return keyboard_layout

    def insert_char(self, instance):
        self.text_input.text += instance.text

    def insert_text(self, text):
        self.text_input.text += text

    def backspace(self, instance):
        self.text_input.text = self.text_input.text[:-1]


class ResultScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical')
        self.root = RelativeLayout()
        self.bg = Image(source="fon.png", allow_stretch=True, keep_ratio=False)
        self.root.add_widget(self.bg)

        self.scroll = ScrollView()
        self.content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=20,
            padding=20
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)

        self.back_btn = MDRaisedButton(
            text="НА ГЛАВНУЮ",
            size_hint=(0.6, None),
            height=dp(60),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.2, 0.6, 0.86, 1),
            text_color=(1, 1, 1, 1),
            on_release=self.return_home
        )

        self.layout.add_widget(self.scroll)
        self.layout.add_widget(self.back_btn)
        self.root.add_widget(self.layout)
        self.add_widget(self.root)

    def show_results(self, results):
        self.content.clear_widgets()
        title = Label(
            text="РЕЗУЛЬТАТЫ ТЕСТА",
            font_name="ARCO",
            font_size=dp(24),
            halign='center',
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        result_label = Label(
            text=results,
            markup=True,
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(None, None),
            color=(0, 0, 0, 1)
        )
        result_label.bind(texture_size=lambda instance, size: setattr(result_label, 'size', size))
        self.content.add_widget(title)
        self.content.add_widget(result_label)

    def return_home(self, *args):
        self.manager.current = "home"


class DictationApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        sm = MDScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HomeScreen(sm, name="home"))
        sm.add_widget(DictationScreen(name="dictation"))
        sm.add_widget(ResultScreen(name="results"))
        sm.current = "splash"
        return sm


if __name__ == "__main__":
    DictationApp().run()