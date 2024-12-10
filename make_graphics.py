import matplotlib.pyplot as plt
from math import *

# Константы
H = 5600  # характерестическая высота (м)
A = 19.625  # площадь поперечного сечения ракеты (м^2)
d = 2.32  # безразмерный коэффициент сопротивления формы
p0 = 1.225  # плотность воздуха (кг/м^3)
tanks_fuel_of_L110 = 116800  # количество топлива в баках L110 (кг)
tanks_fuel_of_S200 = 207000  # количество топлива в баках S200 (кг)
fuel_consumption_of_L110 = 558  # расход топлива двигателей Vikas (кг/с)
fuel_consumption_of_S200 = 1820  # расход топлива ускорителей S200 (кг/с)
fuel_combustion_time_of_L110 = round(tanks_fuel_of_L110 / fuel_consumption_of_L110, 1)
fuel_combustion_time_of_S200 = round(tanks_fuel_of_S200 / fuel_consumption_of_S200, 1)
thrust_L110 = 863200 * 2  # тяга ступени L110 (Н)
thrust_S200 = 4942300 * 2  # суммарная тяга ускорителей S200 (Н)
time_start_L110 = fuel_combustion_time_of_S200  # момент запуска двигателей L110
time_end_L110 = time_start_L110 + fuel_combustion_time_of_L110  # конец работы L110
mass_L110 = 9670 + tanks_fuel_of_L110  # масса первой ступени L110 с топливом
mass_S200 = (30760 + tanks_fuel_of_S200) * 2  # масса ускорителей S200 с топливом
other_mass = 44538  # масса других компонентов ракеты
mass = other_mass + mass_L110 + mass_S200  # начальная масса ракеты

# Переменные для моделирования
dt = 1  # шаг времени (1 секунда)
time_points = [i for i in range(1, int(time_end_L110) + 1)]

mass_changes_list = [mass]
vx = [0]  # горизонтальная скорость
vy = [0]  # вертикальная скорость
x = [0]  # координата x
y = [15]  # координата y (начальная высота 15 м)
pitch = [90]  # угол наклона (градусы)

# Чтение данных о высоте и скорости
height_list = []
velocity_list = []
with open("file_altitude.txt", 'r') as altitude_file, open("file_velocity.txt", 'r') as velocity_file:
    for alt_line, vel_line in zip(altitude_file, velocity_file):
        height_data = alt_line.split()
        velocity_data = vel_line.split()
        height_list.append(float(height_data[1]))  # высота
        pitch.append(round(float(height_data[2]), 2))  # угол наклона
        velocity_list.append(float(velocity_data[2]))  # скорость

# Убедимся, что списки синхронизированы
min_length = min(len(height_list), len(velocity_list))
height_list = height_list[:min_length]
velocity_list = velocity_list[:min_length]
time_points = time_points[:min_length]

# Рассчёт изменения массы во времени
default_time = 1
since_start_L110 = 1  # время работы L110

while default_time <= time_end_L110:
    if default_time < time_start_L110:
        mass_changes_list.append(mass - 2 * fuel_consumption_of_S200 * default_time)
    elif time_start_L110 <= default_time < time_end_L110:
        mass_changes_list.append(mass - mass_S200 - fuel_consumption_of_L110 * since_start_L110)
        since_start_L110 += dt
    else:
        mass_changes_list.append(mass - mass_S200 - mass_L110)
    default_time += dt


# Моделирование высоты
default_time = 1
for i in range(1, len(time_points)):
    j = i - 1

    if default_time < time_start_L110:
        thrust = thrust_S200
    elif time_start_L110 <= default_time <= time_end_L110:
        thrust = thrust_L110
    else:
        thrust = 0

    vy.append(vy[j] + dt * (thrust * sin(pitch[j] * pi / 180) - mass_changes_list[j] * 9.81 -
                            0.5 * p0 * exp(-y[j] / H) * d * A * vy[j] ** 2 * sin(pitch[j] * pi / 180)) /
              mass_changes_list[j])
    y.append(y[j] + vy[i] * dt)
    default_time += dt

# Построение графика высоты
plt.figure(figsize=(10, 6))
plt.title("График зависимости высоты от времени")
plt.plot(time_points, height_list, color='#32CD32', label="Высота (KSP)")
plt.plot(time_points[:len(y)], y, color='#CD5C5C', linewidth=2, label="Высота (модель)")
plt.xlabel("Время, с")
plt.ylabel("Высота, м")
plt.grid()
plt.legend()
plt.savefig("rocket_height.png")
plt.close()

# Построение графика скорости
plt.figure(figsize=(10, 6))
plt.title("График зависимости скорости от времени")
plt.plot(time_points, velocity_list, color='#1E90FF', label="Скорость (KSP)")
plt.plot(time_points[:len(vy)], vy, color='#FF4500', linewidth=2, label="Скорость (модель)")
plt.xlabel("Время, с")
plt.ylabel("Скорость, м/с")
plt.grid()
plt.legend()
plt.savefig("rocket_velocity.png")
plt.close()
