from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
import re
from functools import partial


class FloatInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join(
                re.sub(pat, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, from_undo=from_undo)


class SpinnerOptions(SpinnerOption):

    def __init__(self, **kwargs):
        super(SpinnerOptions, self).__init__(**kwargs)
        self.background_color = [0, 0.6, 1, 1]


class SpinnerWidget(Spinner):
    def __init__(self, **kwargs):
        super(SpinnerWidget, self).__init__(**kwargs)
        self.option_cls = SpinnerOptions


class CalculatorWiresApp(App):
    # Модальное окно справки
    def close(self, instance):
        self.gl_modal_about2.clear_widgets()
        self.modal_about.dismiss()

    def about(self, instance):
        self.modal_about = ModalView(size_hint=(.9, .55), auto_dismiss=False, background_color=[0, 0.6, 1, 1])
        gl_modal_about = GridLayout(cols=1, rows_minimum={0: Window.height * 0.25, 1: Window.height * 0.15,
                                                          2: Window.height * 0.1, 3: Window.height * 0.05},
                                    row_force_default=True)
        self.gl_modal_about2 = GridLayout(cols=2, cols_minimum={0: Window.width * 0.7, 1: Window.width * 0.15},
                                          col_force_default=True)
        lb = Label(
            text='При отсутствии круглого провода(ов) нужного диаметра можно применять несколько проводов с меньшим диаметром. Допустимо занижение сечения на 2—3% без уменьшения мощности двигателя. Увеличение сечения ограничивается возможностью размещения обмотки в пазу.',
            text_size=(Window.width * 0.85, None))
        lb4 = Label(text='Виктор Ульдинович\n2022г.', text_size=(Window.width * 0.85, None))
        btn_close = Button(text='Закрыть', size_hint=(.5, .25), on_press=self.close, background_color=[0, 0.6, 1, 1])

        lb2 = Label(text='Максимальное увеличение площади сечения в %', text_size=(Window.width * 0.65, None),
                    halign='center')
        lb3 = Label(text='Минимальное уменьшение площади сечения в %', text_size=(Window.width * 0.65, None),
                    halign='center')

        self.gl_modal_about2.add_widget(lb3)
        self.gl_modal_about2.add_widget(self.sp_min)
        self.gl_modal_about2.add_widget(lb2)
        self.gl_modal_about2.add_widget(self.sp_max)

        gl_modal_about.add_widget(lb)
        gl_modal_about.add_widget(self.gl_modal_about2)
        gl_modal_about.add_widget(lb4)
        gl_modal_about.add_widget(btn_close)
        self.modal_about.add_widget(gl_modal_about)

        return self.modal_about.open()

    # Метод для страницы выбора проводников
    def box_provod(self):
        with open("property.txt", "r") as f:
            temp = f.read()
            temp = temp.split('\n')
            self.n2 = dict(eval(temp[0]))
            self.cb_active = eval(temp[1])

        x = 0
        self.sort = []

        # Генератор вариантов проводников
        for key in self.n2:
            x += 1
            gl_list = GridLayout(cols=2, size_hint=(1, None), padding=[0, 0, 75, 0])
            globals()['self.cb' + str(x)] = CheckBox(size_hint=(.1, None), active=False)
            app_me = [globals()['self.cb' + str(x)], key, self.n2[key]]
            self.sort.append(app_me)
            lb = Label(text="Диаметр: " + key + "мм, площадь " + str(self.n2[key]) + 'мм[sup]2[/sup]',
                       text_size=(Window.width * 0.75, None), halign='left', markup=True)
            gl_list.add_widget(lb)
            gl_list.add_widget(globals()['self.cb' + str(x)])
            self.gl_page2.add_widget(gl_list)
        for a, i in zip(self.cb_active, self.sort):
            if a == 1:
                i[0].active = True

        return self.gl_page2

    # Метод удаления из словаря проводников
    def remove(self, widget, key, instance):
        self.n2.pop(key)
        self.gl_page_remove.remove_widget(widget)
        with open("property.txt", "w") as f:
            f.write(str(self.n2))
            f.write('\n')
            f.write(str(self.cb_active))
            f.write('\n')
            f.write(self.sp_min.text)
            f.write('\n')
            f.write(self.sp_max.text)
        self.sv.clear_widgets()
        self.gl_page2.clear_widgets()
        self.sv.add_widget(self.box_provod())

    # Мктод окна выбора проводников
    def provod(self, instance):
        self.gl_modal2 = GridLayout(cols=1)
        self.gl_page1.remove_widget(self.gl_modal2)
        self.gl_page1.remove_widget(self.sv_result)
        lb = Label(text="Виды проводников", text_size=(Window.width * 0.75, None), halign='center',
                   size=(Window.width, Window.height * 0.05), size_hint=(None, None))

        self.gl_page2 = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.gl_page2.bind(minimum_height=self.gl_page2.setter('height'))

        self.sv = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.48))
        self.sv.add_widget(self.box_provod())

        btn_add = Button(text='Добавить', size_hint=(None, None), size=(Window.width / 2, Window.height * 0.05),
                         on_press=self.modal_add.open, background_color=[0, 0.6, 1, 1])

        btn_remove = Button(text='Удалить', size_hint=(None, None), size=(Window.width / 2, Window.height * 0.05),
                            on_press=self.modal_remove.open, background_color=[0, 0.6, 1, 1])

        gl_modal21 = GridLayout(cols=2, size_hint=(None, None), size=(Window.width, Window.height * 0.05))

        gl_modal21.add_widget(btn_add)
        gl_modal21.add_widget(btn_remove)

        self.gl_modal2.add_widget(lb)
        self.gl_modal2.add_widget(self.sv)
        self.gl_modal2.add_widget(gl_modal21)

        self.gl_page1.add_widget(self.gl_modal2)

    # Метод добавления в словарь проводников
    def add(self, instance):
        if self.fi1.text != '' and self.fi2.text != '':
            self.n2[self.fi1.text] = float(self.fi2.text)
            self.n2 = sorted(self.n2.items())
            with open("property.txt", "w") as f:
                f.write(str(self.n2))
                f.write('\n')
                f.write(str(self.cb_active))
                f.write('\n')
                f.write(self.sp_min.text)
                f.write('\n')
                f.write(self.sp_max.text)
            self.sv.clear_widgets()
            self.gl_page2.clear_widgets()
            self.sv.add_widget(self.box_provod())

            self.gl_page_remove.clear_widgets()
            x = 0

            with open("property.txt", "r") as f:
                temp = f.read()
                temp = temp.split('\n')
                self.n2 = dict(eval(temp[0]))
                self.cb_active = eval(temp[1])

            self.sort = []
            for key in self.n2:
                x += 1
                globals()['self.gl_r' + str(x)] = GridLayout(cols=2, size_hint=(1, None))
                app_me = [globals()['self.gl_r' + str(x)], key]
                self.sort.append(app_me)
                globals()['self.btn_r' + str(x)] = Button(text='X', size_hint=(.1, None),
                                                          on_press=partial(self.remove, globals()['self.gl_r' + str(x)],
                                                                           key), background_colo=[0, 0.6, 1, 1])
                lb = Label(text="Диаметр: " + key + "мм, площадь " + str(self.n2[key]) + 'мм[sup]2[/sup]',
                           text_size=(Window.width * 0.75, None), halign='left', markup=True)
                globals()['self.gl_r' + str(x)].add_widget(lb)
                globals()['self.gl_r' + str(x)].add_widget(globals()['self.btn_r' + str(x)])
                self.gl_page_remove.add_widget(globals()['self.gl_r' + str(x)])

    # Метод ал=>ку
    def al_cu(self, instance):
        try:
            self.lbl.text = str(round((eval(self.lbl.text) / 1.63), 3))
        except:
            self.lbl.text = ''

    # Метод слайдера
    def slid(self, instance, value):
        self.lbl3.text = str(int(self.s.value))

    # Метод строки ввода
    def add_vvod(self, instance):
        self.vvod += str(instance.text)
        self.lbl.text = self.vvod

    # Очистка
    def clear(self, instance):
        self.vvod = ''
        self.lbl.text = ''

    # Подсчет результатов
    def result(self, instance):
        try:
            self.lbl.text = str(eval(self.lbl.text))
        except:
            self.lbl.text = ''
        self.vvod = ""

    def build(self):

        self.sp_min = SpinnerWidget(text='2', values=('0', '1', '2', '3', '4'), background_color=[0, 0.6, 1, 1])
        self.sp_max = SpinnerWidget(text='0', values=('0', '1', '2', '3', '4', '5'), background_color=[0, 0.6, 1, 1])

        try:
            with open("property.txt", "r") as f:
                temp = f.read()
                temp = temp.split('\n')
                self.n2 = dict(eval(temp[0]))
                self.cb_active = eval(temp[1])
                self.sp_min.text = temp[2]
                self.sp_max.text = temp[3]
        except:
            with open("property.txt", "w") as f:
                f.write(str({'0,25': 0.0491, '0,28': 0.0615, '0,315': 0.078, '0,355': 0.099, '0,4': 0.126, '0,45': 0.16,
                             '0,5': 0.196, '0,56': 0.247, '0,6': 0.283, '0,63': 0.313, '0,67': 0.352, '0,71': 0.398,
                             '0,75': 0.441, '0,8': 0.503, '0,85': 0.567, '0,9': 0.636, '0,95': 0.712, '1': 0.7854,
                             '1,06': 0.884, '1,12': 0.9852, '1,18': 1.092, '1,25': 1.2272, '1,32': 1.362,
                             '1,4': 1.5394}))
                f.write('\n')
                f.write(str([0]))
                f.write('\n')
                f.write('2')
                f.write('\n')
                f.write('0')

        # Модальное окно ошибки
        self.modal_er = ModalView(size_hint=(.9, .5), auto_dismiss=False, background_color=[0, 0.6, 1, 1])
        gl_modal_er = GridLayout(cols=1)
        self.lb_er = Label(text='', size_hint=(1, .4), text_size=(Window.width * 0.75, None))
        btn_close = Button(text='Закрыть', size_hint=(.5, .15), on_press=self.modal_er.dismiss,
                           background_color=[0, 0.6, 1, 1])
        gl_modal_er.add_widget(self.lb_er)
        gl_modal_er.add_widget(btn_close)
        self.modal_er.add_widget(gl_modal_er)

        # Модальное окно добавления проводников
        self.modal_add = ModalView(size_hint=(.9, .2), auto_dismiss=False, background_color=[0, 0.6, 1, 1])
        gl_modal_add = GridLayout(cols=2)
        lbl1 = Label(text='Введите сечение', size_hint=(1, .5))
        lbl2 = Label(text='Введите значение', size_hint=(1, .5))
        self.fi1 = FloatInput()
        self.fi2 = FloatInput()
        btn_close = Button(text='Закрыть', size_hint=(.5, .25), on_press=self.modal_add.dismiss,
                           background_color=[0, 0.6, 1, 1])
        btn_add = Button(text='Добавить', on_press=self.add, background_color=[0, 0.6, 1, 1])
        gl_modal_add.add_widget(lbl1)
        gl_modal_add.add_widget(self.fi1)
        gl_modal_add.add_widget(lbl2)
        gl_modal_add.add_widget(self.fi2)
        gl_modal_add.add_widget(btn_add)
        gl_modal_add.add_widget(btn_close)
        self.modal_add.add_widget(gl_modal_add)

        Window.clearcolor = (0, .1, .2, 1)

        self.vvod = ""

        # Модальное окно удаления проводников
        self.gl_page_remove = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[0, 0, 25, 0])
        self.gl_page_remove.bind(minimum_height=self.gl_page_remove.setter('height'))

        x = 0

        with open("property.txt", "r") as f:
            temp = f.read()
            temp = temp.split('\n')
            self.n2 = dict(eval(temp[0]))
            self.cb_active = eval(temp[1])

        self.sort = []
        for key in self.n2:
            x += 1
            globals()['self.gl_r' + str(x)] = GridLayout(cols=2, size_hint=(1, None))
            app_me = [globals()['self.gl_r' + str(x)], key]
            self.sort.append(app_me)
            globals()['self.btn_r' + str(x)] = Button(text='X', size_hint=(.1, None),
                                                      on_press=partial(self.remove, globals()['self.gl_r' + str(x)],
                                                                       key), background_color=[0, 0.6, 1, 1])
            lb = Label(text="Диаметр: " + key + "мм, площадь " + str(self.n2[key]) + 'мм[sup]2[/sup]',
                       text_size=(Window.width * 0.75, None), halign='left', markup=True)
            globals()['self.gl_r' + str(x)].add_widget(lb)
            globals()['self.gl_r' + str(x)].add_widget(globals()['self.btn_r' + str(x)])
            self.gl_page_remove.add_widget(globals()['self.gl_r' + str(x)])

        self.sb_remove = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.95))
        self.sb_remove.add_widget(self.gl_page_remove)

        gl_modal_r = GridLayout(cols=1)

        self.modal_remove = ModalView(size=(Window.width, Window.height), auto_dismiss=False,
                                      background_color=[0, 0.6, 1, 1])

        btn_close = Button(text='Закрыть', size_hint=(None, None), size=(Window.width, Window.height * 0.05),
                           on_press=self.modal_remove.dismiss, background_color=[0, 0.6, 1, 1])

        gl_modal_r.add_widget(self.sb_remove)
        gl_modal_r.add_widget(btn_close)

        self.modal_remove.add_widget(gl_modal_r)

        # Начало первой страницы, элементы распологаются сверху вниз
        self.lbl = Label(text='', size_hint=(1, 0.1), text_size=(Window.width * 0.75, Window.height * 0.05),
                         halign='center')
        gl_keybord3 = GridLayout(cols=3, spacing=5, size_hint=(1, .1))
        gl_keybord3.add_widget(
            Label(text='Sмм[sup]2[/sup]', size_hint=(None, None), size=(Window.width * 0.1, Window.height * 0.05),
                  markup=True))
        gl_keybord3.add_widget(self.lbl)
        gl_keybord3.add_widget(Button(text='?', on_press=self.about, size_hint=(None, None),
                                      size=(Window.width * 0.1, Window.height * 0.05), background_color=[0, 1, 1, 0]))

        gl_keybord = GridLayout(cols=3, spacing=5, size_hint=(1, .2), padding=[5, 5, 5, 5])

        gl_keybord.add_widget(Button(text="9", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="8", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="7", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))

        gl_keybord.add_widget(Button(text="6", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="5", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="4", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))

        gl_keybord.add_widget(Button(text="3", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="2", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="1", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))

        gl_keybord.add_widget(Button(text="+", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="0", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text=".", on_press=self.add_vvod, background_color=[0, 0.6, 1, 1]))

        gl_keybord.add_widget(Button(text="=", on_press=self.result, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="Очистить", on_press=self.clear, background_color=[0, 0.6, 1, 1]))
        gl_keybord.add_widget(Button(text="al", background_color=[0, 0.6, 1, 1]))

        gl_keybord2 = GridLayout(cols=1, spacing=5, size_hint=(1, .2), padding=[5, 5, 5, 5])

        gl_keybord2.add_widget(Button(text='Выбор сечений', on_press=self.provod, background_color=[0, 0.6, 1, 1]))
        gl_keybord2.add_widget(Button(text="Рассчитать", on_press=self.generate, background_color=[0, 0.6, 1, 1]))

        # Слайдер
        self.s = Slider(min=2, max=8, value=3, cursor_size=(Window.width * .05, Window.width * .05))
        self.lbl3 = Label(text=str(int(self.s.value)))
        self.s.bind(value=self.slid)
        label = Label(text='провода')

        gl_keybord.add_widget(self.lbl3)
        gl_keybord.add_widget(self.s)
        gl_keybord.add_widget(label)

        global res
        res = []

        self.gl_res = GridLayout(cols=1, size_hint_y=None)
        self.gl_res.bind(minimum_height=self.gl_res.setter('height'))

        self.sv_result = ScrollView(size_hint=(1, None), size=(Window.width - 150, Window.height * 0.6))

        self.gl_page1 = GridLayout(cols=1, padding=[25], spacing=5,
                                   rows_minimum={0: Window.height * 0.05, 1: Window.height * 0.25,
                                                 2: Window.height * 0.1, 3: Window.height * 0.6},
                                   row_force_default=True)
        self.gl_page1.add_widget(gl_keybord3)
        self.gl_page1.add_widget(gl_keybord)
        self.gl_page1.add_widget(gl_keybord2)
        self.provod(1)

        return self.gl_page1

    # Подсчет результатов
    def generate(self, instance):
        self.result(instance)
        n = {}
        self.sv_result.clear_widgets()
        self.gl_res.clear_widgets()

        self.gl_page1.remove_widget(self.gl_modal2)

        self.gl_page1.remove_widget(self.sv_result)

        # Собираем значения из спика чекбоксов
        self.cb_active = []
        for i in self.sort:
            if i[0].active:
                n[i[1]] = i[2]
                self.cb_active.append(1)
            else:
                self.cb_active.append(0)

        with open("property.txt", "w") as f:
            f.write(str(self.n2))
            f.write('\n')
            f.write(str(self.cb_active))
            f.write('\n')
            f.write(self.sp_min.text)
            f.write('\n')
            f.write(self.sp_max.text)

        col = int(self.s.value)
        y = 0

        if self.lbl.text == '':
            self.gl_page1.add_widget(self.sv_result)
            return

        # Алгоритм для подсчета 8 проводников
        if col == 8:
            a6 = len(n) ** 6 * (-1) + 1
            for k8 in n:
                a6 += len(n) ** 6
                b6 = a6
                a5 = len(n) ** 5 * (-1) + 1
                for k7 in n:
                    a5 += len(n) ** 5
                    b5 = a5
                    b6 -= len(n) ** 6
                    if b6 > 0:
                        continue
                    a4 = len(n) ** 4 * (-1) + 1
                    for k6 in n:
                        a4 += len(n) ** 4
                        b4 = a4
                        b5 -= len(n) ** 5
                        if b5 > 0:
                            continue
                        a3 = len(n) ** 3 * (-1) + 1
                        for k5 in n:
                            a3 += len(n) ** 3
                            b3 = a3
                            b4 -= len(n) ** 4
                            if b4 > 0:
                                continue
                            a2 = len(n) ** 2 * (-1) + 1
                            for k4 in n:
                                a2 += len(n) ** 2
                                b2 = a2
                                b3 -= len(n) ** 3
                                if b3 > 0:
                                    continue
                                a1 = len(n) ** 1 * (-1) + 1
                                for k3 in n:
                                    a1 += len(n) ** 1
                                    b1 = a1
                                    b2 -= len(n) ** 2
                                    if b2 > 0:
                                        continue
                                    a0 = len(n) ** 0 * (-1) + 1
                                    for k2 in n:
                                        a0 += len(n) ** 0
                                        b0 = a0
                                        b1 -= len(n) ** 1
                                        if b1 > 0:
                                            continue
                                        for k1 in n:
                                            b0 -= len(n) ** 0
                                            if b0 > 0:
                                                continue
                                            if float(self.lbl.text) - 0.01 * (int(self.sp_min.text)) * float(
                                                    self.lbl.text) <= n[k1] + n[k2] + n[k3] + n[k4] + n[k5] + n[k6] + n[k7] + n[k8] <= float(self.lbl.text) + (int(self.sp_max.text) * 0.01):
                                                y += 1
                                                if y > 100:
                                                    self.lb_er.text = 'КОЛИЧЕСТВО ВАРИАНТОВ ПРЕВЫШАЕТ 100 РЕКОМЕНДУЕТСЯ УМЕНЬШИТЬ  КОЛИЧЕСТВО ВАРИАНТОВ ПРОВОДНИКОВ'
                                                    self.modal_er.open()
                                                    self.gl_res.clear_widgets()
                                                    self.gl_page1.add_widget(self.sv_result)
                                                    return
                                                x1 = str(y) + ".Диаметр"
                                                x2 = k1 + '+' + k2 + '+' + k3 + '+' + k4 + '+' + k5 + '+' + k6 + '+' + k7 + '+' + k8
                                                x3 = '\nПлощадь ' + str(round((n[k1] + n[k2] + n[k3] + n[k4] + n[k5] + n[k6] + n[k7] + n[k8]), 3)) + '\n'
                                                self.lb1 = Label(text=x1, size_hint=(1, None),
                                                                 text_size=(Window.width - 50, None), halign='left')
                                                self.lb2 = Label(text=x2, size_hint=(1, None),
                                                                 text_size=(Window.width - 50, None), halign='left')
                                                self.lb3 = Label(text=x3, size_hint=(1, None),
                                                                 text_size=(Window.width - 50, None), halign='left')
                                                self.gl_res.add_widget(self.lb1)
                                                self.gl_res.add_widget(self.lb2)
                                                self.gl_res.add_widget(self.lb3)

        # Алгоритм для подсчета 7 проводников
        if col == 7:
            a5 = len(n) ** 5 * (-1) + 1
            for k7 in n:
                a5 += len(n) ** 5
                b5 = a5
                a4 = len(n) ** 4 * (-1) + 1
                for k6 in n:
                    a4 += len(n) ** 4
                    b4 = a4
                    b5 -= len(n) ** 5
                    if b5 > 0:
                        continue
                    a3 = len(n) ** 3 * (-1) + 1
                    for k5 in n:
                        a3 += len(n) ** 3
                        b3 = a3
                        b4 -= len(n) ** 4
                        if b4 > 0:
                            continue
                        a2 = len(n) ** 2 * (-1) + 1
                        for k4 in n:
                            a2 += len(n) ** 2
                            b2 = a2
                            b3 -= len(n) ** 3
                            if b3 > 0:
                                continue
                            a1 = len(n) ** 1 * (-1) + 1
                            for k3 in n:
                                a1 += len(n) ** 1
                                b1 = a1
                                b2 -= len(n) ** 2
                                if b2 > 0:
                                    continue
                                a0 = len(n) ** 0 * (-1) + 1
                                for k2 in n:
                                    a0 += len(n) ** 0
                                    b0 = a0
                                    b1 -= len(n) ** 1
                                    if b1 > 0:
                                        continue
                                    for k1 in n:
                                        b0 -= len(n) ** 0
                                        if b0 > 0:
                                            continue
                                        if float(self.lbl.text) - (int(self.sp_min.text) * 0.01) * float(
                                                self.lbl.text) <= n[k1] + n[k2] + n[k3] + n[k4] + n[k5] + n[k6] + n[k7] <= float(self.lbl.text) + (int(self.sp_max.text) * 0.01):
                                            y += 1
                                            if y > 100:
                                                self.lb_er.text = 'КОЛИЧЕСТВО ВАРИАНТОВ ПРЕВЫШАЕТ 100 РЕКОМЕНДУЕТСЯ УМЕНЬШИТЬ  КОЛИЧЕСТВО ВАРИАНТОВ ПРОВОДНИКОВ'
                                                self.modal_er.open()
                                                self.gl_res.clear_widgets()
                                                self.gl_page1.add_widget(self.sv_result)
                                                return
                                            x1 = str(y) + ". Диаметр"
                                            x2 = k1 + '+' + k2 + '+' + k3 + '+' + k4 + '+' + k5 + '+' + k6 + '+' + k7
                                            x3 = '\nПлощадь ' + str(
                                                round((n[k1] + n[k2] + n[k3] + n[k4] + n[k5] + n[k6] + n[k7]),
                                                      3)) + '\n'
                                            self.lb1 = Label(text=x1, size_hint=(1, None),
                                                             text_size=(Window.width - 50, None), halign='left')
                                            self.lb2 = Label(text=x2, size_hint=(1, None),
                                                             text_size=(Window.width - 50, None), halign='left')
                                            self.lb3 = Label(text=x3, size_hint=(1, None),
                                                             text_size=(Window.width - 50, None), halign='left')
                                            self.gl_res.add_widget(self.lb1)
                                            self.gl_res.add_widget(self.lb2)
                                            self.gl_res.add_widget(self.lb3)

        # Алгоритм для подсчета 6 проводников
        if col == 6:
            a4 = len(n) ** 4 * (-1) + 1
            for k6 in n:
                a4 += len(n) ** 4
                b4 = a4
                a3 = len(n) ** 3 * (-1) + 1
                for k5 in n:
                    a3 += len(n) ** 3
                    b3 = a3
                    b4 -= len(n) ** 4
                    if b4 > 0:
                        continue
                    a2 = len(n) ** 2 * (-1) + 1
                    for k4 in n:
                        a2 += len(n) ** 2
                        b2 = a2
                        b3 -= len(n) ** 3
                        if b3 > 0:
                            continue
                        a1 = len(n) ** 1 * (-1) + 1
                        for k3 in n:
                            a1 += len(n) ** 1
                            b1 = a1
                            b2 -= len(n) ** 2
                            if b2 > 0:
                                continue
                            a0 = len(n) ** 0 * (-1) + 1
                            for k2 in n:
                                a0 += len(n) ** 0
                                b0 = a0
                                b1 -= len(n) ** 1
                                if b1 > 0:
                                    continue
                                for k1 in n:
                                    b0 -= len(n) ** 0
                                    if b0 > 0:
                                        continue
                                    if float(self.lbl.text) - (int(self.sp_min.text) * 0.01) * float(self.lbl.text) <= \
                                            n[k1] + n[k2] + n[k3] + n[k4] + n[k5] + n[k6] <= float(self.lbl.text) + (
                                            int(self.sp_max.text) * 0.01):
                                        y += 1
                                        if y > 100:
                                            self.lb_er.text = 'КОЛИЧЕСТВО ВАРИАНТОВ ПРЕВЫШАЕТ 100 РЕКОМЕНДУЕТСЯ УМЕНЬШИТЬ  КОЛИЧЕСТВО ВАРИАНТОВ ПРОВОДНИКОВ'
                                            self.modal_er.open()
                                            self.gl_res.clear_widgets()
                                            self.gl_page1.add_widget(self.sv_result)
                                            return
                                        x1 = str(
                                            y) + ". Диаметр " + k1 + '+' + k2 + '+' + k3 + '+' + k4 + '+' + k5 + '+' + k6
                                        x2 = 'Площадь ' + str(
                                            round((n[k1] + n[k2] + n[k3] + n[k4] + n[k5] + n[k6]), 3)) + '\n'
                                        self.lb1 = Label(text=x1, size_hint=(1, None),
                                                         text_size=(Window.width - 50, None), halign='left')
                                        self.lb2 = Label(text=x2, size_hint=(1, None),
                                                         text_size=(Window.width - 50, None), halign='left')
                                        self.gl_res.add_widget(self.lb1)
                                        self.gl_res.add_widget(self.lb2)

        # Алгоритм для подсчета 5 проводников
        if col == 5:
            a3 = len(n) ** 3 * (-1) + 1
            for k5 in n:
                a3 += len(n) ** 3
                b3 = a3
                a2 = len(n) ** 2 * (-1) + 1
                for k4 in n:
                    a2 += len(n) ** 2
                    b2 = a2
                    b3 -= len(n) ** 3
                    if b3 > 0:
                        continue
                    a1 = len(n) ** 1 * (-1) + 1
                    for k3 in n:
                        a1 += len(n) ** 1
                        b1 = a1
                        b2 -= len(n) ** 2
                        if b2 > 0:
                            continue
                        a0 = len(n) ** 0 * (-1) + 1
                        for k2 in n:
                            a0 += len(n) ** 0
                            b0 = a0
                            b1 -= len(n) ** 1
                            if b1 > 0:
                                continue
                            for k1 in n:
                                b0 -= len(n) ** 0
                                if b0 > 0:
                                    continue
                                if float(self.lbl.text) - (int(self.sp_min.text) * 0.01) * float(self.lbl.text) <= n[
                                    k1] + n[k2] + n[k3] + n[k4] + n[k5] <= float(self.lbl.text) + (
                                        int(self.sp_max.text) * 0.01):
                                    y += 1
                                    if y > 100:
                                        self.lb_er.text = 'КОЛИЧЕСТВО ВАРИАНТОВ ПРЕВЫШАЕТ 100 РЕКОМЕНДУЕТСЯ УМЕНЬШИТЬ  КОЛИЧЕСТВО ВАРИАНТОВ ПРОВОДНИКОВ'
                                        self.modal_er.open()
                                        self.gl_res.clear_widgets()
                                        self.gl_page1.add_widget(self.sv_result)
                                        return
                                    x1 = str(y) + ". Диаметр " + k1 + '+' + k2 + '+' + k3 + '+' + k4 + '+' + k5
                                    x2 = 'Площадь ' + str(round((n[k1] + n[k2] + n[k3] + n[k4] + n[k5]), 3)) + '\n'
                                    self.lb1 = Label(text=x1, size_hint=(1, None), text_size=(Window.width - 50, None),
                                                     halign='left')
                                    self.lb2 = Label(text=x2, size_hint=(1, None), text_size=(Window.width - 50, None),
                                                     halign='left')
                                    self.gl_res.add_widget(self.lb1)
                                    self.gl_res.add_widget(self.lb2)

        # Алгоритм для подсчета 4 проводников
        if col == 4:
            a2 = len(n) ** 2 * (-1) + 1
            for k4 in n:
                a2 += len(n) ** 2
                b2 = a2
                a1 = len(n) ** 1 * (-1) + 1
                for k3 in n:
                    a1 += len(n) ** 1
                    b1 = a1
                    b2 -= len(n) ** 2
                    if b2 > 0:
                        continue
                    a0 = len(n) ** 0 * (-1) + 1
                    for k2 in n:
                        a0 += len(n) ** 0
                        b0 = a0
                        b1 -= len(n) ** 1
                        if b1 > 0:
                            continue
                        for k1 in n:
                            b0 -= len(n) ** 0
                            if b0 > 0:
                                continue
                            if float(self.lbl.text) - (int(self.sp_min.text) * 0.01) * float(self.lbl.text) <= n[k1] + \
                                    n[k2] + n[k3] + n[k4] <= float(self.lbl.text) + (int(self.sp_max.text) * 0.01):
                                y += 1
                                if y > 100:
                                    self.lb_er.text = 'КОЛИЧЕСТВО ВАРИАНТОВ ПРЕВЫШАЕТ 100 РЕКОМЕНДУЕТСЯ УМЕНЬШИТЬ  КОЛИЧЕСТВО ВАРИАНТОВ ПРОВОДНИКОВ'
                                    self.modal_er.open()
                                    self.gl_res.clear_widgets()
                                    self.gl_page1.add_widget(self.sv_result)
                                    return
                                x1 = str(y) + ". Диаметр " + k1 + '+' + k2 + '+' + k3 + '+' + k4
                                x2 = 'Площадь ' + str(round((n[k1] + n[k2] + n[k3] + n[k4]), 3)) + '\n'
                                self.lb1 = Label(text=x1, size_hint=(1, None), text_size=(Window.width - 50, None),
                                                 halign='left')
                                self.lb2 = Label(text=x2, size_hint=(1, None), text_size=(Window.width - 50, None),
                                                 halign='left')
                                self.gl_res.add_widget(self.lb1)
                                self.gl_res.add_widget(self.lb2)

        # Алгоритм для подсчета 3 проводников
        elif col == 3:
            a1 = len(n) ** 1 * (-1) + 1
            for k3 in n:
                a1 += len(n) ** 1
                b1 = a1
                a0 = len(n) ** 0 * (-1) + 1
                for k2 in n:
                    a0 += len(n) ** 0
                    b0 = a0
                    b1 -= len(n) ** 1
                    if b1 > 0:
                        continue
                    for k1 in n:
                        b0 -= len(n) ** 0
                        if b0 > 0:
                            continue
                        if float(self.lbl.text) - (int(self.sp_min.text) * 0.01) * float(self.lbl.text) <= n[k1] + n[k2] + n[k3] <= float(self.lbl.text) + (int(self.sp_max.text) * 0.01):
                            y += 1
                            if y > 100:
                                self.lb_er.text = 'КОЛИЧЕСТВО ВАРИАНТОВ ПРЕВЫШАЕТ 100 РЕКОМЕНДУЕТСЯ УМЕНЬШИТЬ  КОЛИЧЕСТВО ВАРИАНТОВ ПРОВОДНИКОВ'
                                self.modal_er.open()
                                self.gl_res.clear_widgets()
                                self.gl_page1.add_widget(self.sv_result)
                                return
                            x = str(y) + ". Диаметр " + k1 + '+' + k2 + '+' + k3 + ';' + ' площадь ' + str(
                                round((n[k1] + n[k2] + n[k3]), 3)) + '\n'
                            self.lb = Label(text=x, size_hint=(1, None), text_size=(Window.width - 50, None),
                                            halign='left')
                            self.gl_res.add_widget(self.lb)

        # Алгоритм для подсчета 2 проводников
        elif col == 2:
            a0 = len(n) ** 0 * (-1) + 1
            for k2 in n:
                a0 += len(n) ** 0
                b0 = a0
                for k1 in n:
                    b0 -= len(n) ** 0
                    if b0 > 0:
                        continue
                    if float(self.lbl.text) - (int(self.sp_min.text) * 0.01) * float(self.lbl.text) <= n[k1] + n[k2] <= float(self.lbl.text) + (int(self.sp_max.text) * 0.01):
                        y += 1
                        if y > 100:
                            self.lb_er.text = 'КОЛИЧЕСТВО ВАРИАНТОВ ПРЕВЫШАЕТ 100 РЕКОМЕНДУЕТСЯ УМЕНЬШИТЬ  КОЛИЧЕСТВО ВАРИАНТОВ ПРОВОДНИКОВ'
                            self.modal_er.open()
                            self.gl_res.clear_widgets()
                            self.gl_page1.add_widget(self.sv_result)
                            return
                        x = str(y) + ". Диаметр " + k1 + '+' + k2 + ';' + ' площадь ' + str(
                            round((n[k1] + n[k2]), 3)) + '\n'
                        self.lb = Label(text=x, size_hint=(1, None), text_size=(Window.width - 50, None), halign='left')
                        self.gl_res.add_widget(self.lb)

        self.vvod = ""

        # Вывод результатов или вызов модального окна
        if y == 0:
            self.lb_er.text = 'НЕТ ВАРИАНТОВ. РЕКОМЕНДУЕТСЯ ИЗМЕНИТЬ КОЛИЧЕСТВО ПРОВОДНИКОВ  ИЛИ ВЫБРАТЬ БОЛЬШЕ ВАРИАНТОВ'
            self.modal_er.open()
            self.gl_res.clear_widgets()
        else:
            self.sv_result.add_widget(self.gl_res)
        self.gl_page1.add_widget(self.sv_result)


if __name__ == '__main__':
    app = CalculatorWiresApp()
    app.run()
