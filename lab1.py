import tkinter as tk
from tkinter import ttk
from random import randint
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def flip_coin():
    return randint(0, 1)  # 0 для "орла", 1 для "решки"


def experiment(N):
    result = np.zeros(N)
    counter = 0
    for i in range(N):
        fc = flip_coin()
        if fc == 0:  # Успех, если выпал "орел"
            counter += 1
        result[i] = counter / (i + 1)  # Частота успеха
    return result


def exp_series(M, N):
    result = np.zeros((M, N))
    for i in range(M):
        result[i,] = experiment(N)
    return result


def mean(vs):
    return np.mean(vs, axis=0)


def conf_interval(vs, alpha):
    m = vs.shape[0]
    a = (1 - alpha) / 2
    m_down = int(m * a)
    m_up = m - m_down - 1
    sorted_vs = np.sort(vs, axis=0)
    return np.apply_along_axis(lambda x: np.array([x[m_down], x[m_up]]), 0, sorted_vs)


def normal_quantile(p):
    return 4.91 * (p ** 0.14 - (1 - p) ** 0.14)

def hide_error_label():
    error_label.config(text="")


def run_experiment():
    try:
        N = int(entry_N.get())
        M = int(entry_M.get())
        ALPHA = float(entry_ALPHA.get())

        if N <= 1 or M <= 1:
            raise ValueError("Серия и количество должны быть больше 1.")

        if ALPHA > 1 or ALPHA < 0:
            raise ValueError("Уровень доверия должен быть больше 0 и меньше 2.")

        vs = exp_series(M, N)
        mean_values = mean(vs)

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 6))

        axes[0].set_title('Частота результатов подбрасывания монеты')
        axes[0].set_xscale('log')
        for i in range(M):
            axes[0].plot(range(1, N + 1), vs[i], color='black')

        confidence_interval = conf_interval(vs, ALPHA)

        axes[0].plot(range(1, N + 1), confidence_interval[0,], color="blue")
        axes[0].plot(range(1, N + 1), confidence_interval[1,], color="blue")
        axes[0].plot(range(1, N + 1), mean_values, color="red")
        axes[0].legend()
        axes[0].set_ylabel('Частота успеха (орел)')

        axes[1].set_title('Ошибки')
        axes[1].set_xscale('log')

        exp_error = (confidence_interval[1,] - confidence_interval[0,]) / 2

        coef = normal_quantile((1 + ALPHA) / 2)

        theory_error = np.zeros(N)
        for i in range(1, N + 1):
            theory_error[i - 1] = coef * math.sqrt((1 / 3) * (2 / 3) / i)

        axes[1].plot(range(1, N + 1), theory_error, color="blue")
        axes[1].plot(range(1, N + 1), exp_error, "r--")

        axes[0].set_xlim(1, N)
        axes[1].set_xlim(1, N)

        # Очистка Canvas перед выводом новых данных
        for widget in frame_graph.winfo_children():
            widget.destroy()

        # Создание Canvas и отображение графиков
        canvas = FigureCanvasTkAgg(fig, master=frame_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Запуск таймера для скрытия ошибки
        root.after(5000, hide_error_label)

    except ValueError as e:
        error_label.config(text=str(e))
        # Запуск таймера для скрытия ошибки
        root.after(5000, hide_error_label)



# Создание основного окна
root = tk.Tk()
root.title("Эксперимент с подбрасыванием монеты")

# Создание и размещение виджетов
frame_input = ttk.Frame(root)
frame_input.pack(side=tk.LEFT, padx=10, pady=10)

label_N = ttk.Label(frame_input, text="Введите N:")
label_N.pack()
entry_N = ttk.Entry(frame_input)
entry_N.pack()

label_M = ttk.Label(frame_input, text="Введите M:")
label_M.pack()
entry_M = ttk.Entry(frame_input)
entry_M.pack()

label_ALPHA =ttk.Label(frame_input, text="Введите ALPHA:")
label_ALPHA.pack()
entry_ALPHA = ttk.Entry(frame_input)
entry_ALPHA.pack()


btn_run = ttk.Button(frame_input, text="Пуск", command=run_experiment)
btn_run.pack()

# Фрейм для отображения графиков
frame_graph = ttk.Frame(root)
frame_graph.pack(side=tk.RIGHT, padx=10, pady=10)

# Метка для отображения ошибок
error_label = ttk.Label(frame_input, text="", foreground="red")
error_label.pack()

# Запуск главного цикла
root.mainloop()
