# 4d-game
Математическая модель и реализация 4D-физики в интерактивной форме

*Алексеев П.В. Группа: 22ИТ-ПИ(б/о)ПИП-1*

![2jpg](file://C:\Users\2173\Desktop\game\2.jpg?msec=1776703004602)

### Краткое описание и цель данной программы-игры

В этой программе-игре реализована интерактивная симуляция четырёхмерной физики, где пользователь взаимодействует с гиперобъектами — тессерактами и гиперсферами — в четырёхмерном пространстве, спроекцией в трёхмерное. Многомерные объекты подчиняются гравитации, сталкиваются и обмениваются импульсом в четырёх измерениях, а игрок может перетаскивать их мышью с «броском» (при отпускании объект получает силу в зависимости от движения мыши). Также игрок может применять ко всем объектам случайный импульс одним нажатием клавиши, заставляя их разлетаться в случайных четырёхмерных направлениях, и сталкиваться друг с другом, порождая хаос.

Объекты располагаются на сцене — в четырёхмерном пространстве, трёхмерный срез которого мы видим. Движение сквозь четвёртое измерение изменяет то, как мы видим объекты (их проекции либо сжэимаются, либо растягиваются). Также объекты могут так расположиться в многомерном пространстве, что покажется, будто их проекция "проходит сквозь" сцену и её центр, что демонстрирует потенциально возможные свойства "нелокальности" многомерных объектов, что, кстати, очень сильно напоминает научно-фантастическую трилогию Лю Цысиня "Воспоминания о прошлом Земли" и её продолжение "Возрождение времени" Ли Жуя (Баошу).

**Целью этой игры было проиллюстрировать и воссоздать (насколько это возможно) четырёхмерную физику.**

*Данную программу можно расширять, уточняя её физическую модель. Можно также ввести искривлённую метрику пространства, чтобы имитировать геометрию, которую приобретает пространство, когда объект движется через него с околосветовой скоростью.*

*При создании программы использовались библиотеки: OpenGL (для графики), Numpy (для математических расчётов) и Pygame (для окна приложения).*

*Этот текстовый документ сконвертирован в PDF из MarkDown-файла со всеми вытекающими из этого положительными и отрицательными последствиями.*

![3jpg](file:///C:/Users/2173/Desktop/game/3.jpg?msec=1776703131801)

### Управление

| Клавиша | Действие |
| --- | --- |
| Правая кнопка мыши + движение | Вращение камеры |
| Левая кнопка на объекте + движение + отпустить | Перетаскивание и бросок |
| SPACE | Импульс всем объектам |
| R   | Сброс сцены |
| T   | Добавить гиперсферу |
| Y   | Добавить гиперкуб |
| ↑ / ↓ | Сдвиг по 4-му измерению |
| ESC | Выход |

![1jpg](file://C:\Users\2173\Desktop\game\1.jpg?msec=1776702974220)

### Математическая модель

Далее представлена математика того, что происходит в игре.

## 1. Проекция 4D → 3D

**Формула перспективной проекции вдоль оси w:**

$$
\operatorname{proj}_w(\mathbf{p}) = \left( \frac{x}{1 - w/d_w},\; \frac{y}{1 - w/d_w},\; \frac{z}{1 - w/d_w} \right)
$$

**Код:**

```python
def project_4d_to_3d(point_4d, w_distance=4.0):
    x, y, z, w = point_4d
    factor = w_distance / (w_distance - w + 0.001)
    return (x * factor, y * factor, z * factor)
```

---

## 2. Вращение в 4D

В $\mathbb{R}^4$ существует **6 независимых плоскостей вращения**: $XY,\; XZ,\; XW,\; YZ,\; YW,\; ZW$

**Матрица вращения в плоскости XW:**

$$
R_{xw}(\theta) =
\begin{pmatrix}
\cos\theta & 0 & 0 & -\sin\theta \\
0 & 1 & 0 & 0 \\
0 & 0 & 1 & 0 \\
\sin\theta & 0 & 0 & \cos\theta
\end{pmatrix}
$$

**Код:**

```python
def rotate_4d(point_4d, angles):
    x, y, z, w = point_4d
    xy, xz, xw, yz, yw, zw = angles

    # Вращение в плоскости XY
    x2 = x * math.cos(xy) - y * math.sin(xy)
    y2 = x * math.sin(xy) + y * math.cos(xy)
    x, y = x2, y2

    # Вращение в плоскости XW
    x2 = x * math.cos(xw) - w * math.sin(xw)
    w2 = x * math.sin(xw) + w * math.cos(xw)
    x, w = x2, w2

    return (x, y, z, w)
```

---

## 3. 4D-кинематика (метод Эйлера)

**Уравнения движения:**

$$
\begin{cases}
\mathbf{a}_4 = \mathbf{g}_4 + \frac{\mathbf{F}}{m} \\[2mm]
\mathbf{v}_4 \leftarrow \mathbf{v}_4 + \mathbf{a}_4 \cdot \Delta t \\[2mm]
\mathbf{p}_4 \leftarrow \mathbf{p}_4 + \mathbf{v}_4 \cdot \Delta t
\end{cases}
$$

**Код:**

```python
def update_physics(self, dt, objects_list, gravity_4d):
    self.vel_4d += gravity_4d * dt
    self.pos_4d += self.vel_4d * dt

    for i in range(6):
        self.angles_4d[i] += self.angular_vel[i] * dt

    self.vel_4d *= 0.995
```

---

## 4. 4D-гравитация

Гравитация задаётся постоянным 4D-вектором:

$$
\mathbf{g}_4 = (0,\; -g_y,\; 0,\; -g_w)
$$

**Код:**

```python
self.gravity_4d = np.array([0.0, -8.0, 0.0, -2.0])
```

---

## 5. Столкновения в 4D

### 5.1 Евклидово расстояние в $\mathbb{R}^4$

$$
d_{ij} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2 + (z_i - z_j)^2 + (w_i - w_j)^2}
$$

**Код:**

```python
delta = self.pos_4d - other.pos_4d
dist = np.linalg.norm(delta)
min_dist = self.size + other.size

if dist < min_dist:
    # Столкновение
```

### 5.2 Отталкивание (разведение объектов)

$$
\mathbf{n} = \frac{\mathbf{p}_j - \mathbf{p}_i}{d_{ij}}
$$$$
\Delta = R_i + R_j - d_{ij}
$$$$
\mathbf{p}_i \leftarrow \mathbf{p}_i - \frac{\Delta}{2} \mathbf{n}
$$

**Код:**

```python
overlap = min_dist - dist
direction = delta / (dist + 0.001)
self.pos_4d += direction * overlap * 0.5
other.pos_4d -= direction * overlap * 0.5
```

### 5.3 Обмен импульсами (упругое столкновение)

$$
\mathbf{v}_i' = \mathbf{v}_i + \frac{2m_j}{m_i + m_j} \cdot
\frac{\langle \mathbf{v}_j - \mathbf{v}_i,\; \mathbf{n} \rangle}{\|\mathbf{n}\|^2} \cdot \mathbf{n}
$$

**Код:**

```python
v1 = self.vel_4d.copy()
v2 = other.vel_4d.copy()
m1, m2 = self.mass, other.mass

self.vel_4d = (v1*(m1-m2) + 2*m2*v2) / (m1+m2)
other.vel_4d = (v2*(m2-m1) + 2*m1*v1) / (m1+m2)
```

---

## 6. Геометрия 4D-объектов

### 6.1 Тессеракт (гиперкуб)

Вершины: все комбинации $(\pm 1, \pm 1, \pm 1, \pm 1)$

```python
def generate_tesseract_vertices(self):
    verts = []
    for x in (-self.size, self.size):
        for y in (-self.size, self.size):
            for z in (-self.size, self.size):
                for w in (-self.size, self.size):
                    verts.append([x, y, z, w])
    return np.array(verts)
```

### 6.2 Гиперсфера ($S^3$)

Параметризация:

$$
\begin{cases}
x = R \sin\theta_3 \sin\theta_2 \cos\theta_1 \\
y = R \sin\theta_3 \sin\theta_2 \sin\theta_1 \\
z = R \sin\theta_3 \cos\theta_2 \\
w = R \cos\theta_3
\end{cases}
$$

```python
def generate_hypersphere_points(self, num_points=300):
    points = []
    for _ in range(num_points):
        u1, u2, u3 = random.random(), random.random(), random.random()
        r = self.size

        theta1 = 2 * math.pi * u1
        theta2 = math.acos(2*u2 - 1)
        theta3 = 2 * math.pi * u3

        x = r * math.sin(theta3) * math.sin(theta2) * math.cos(theta1)
        y = r * math.sin(theta3) * math.sin(theta2) * math.sin(theta1)
        z = r * math.sin(theta3) * math.cos(theta2)
        w = r * math.cos(theta3)
        points.append([x, y, z, w])
    return np.array(points)
```

---

## 7. Ray casting для выбора объекта

Луч из камеры: $\mathbf{r}(t) = \mathbf{o} + t \mathbf{d}$

Ближайшая точка луча к центру объекта:

$$
t_{\text{proj}} = \langle \mathbf{c}_{\text{3D}} - \mathbf{o},\; \mathbf{d} \rangle
$$$$
\mathbf{p}_{\text{close}} = \mathbf{o} + t_{\text{proj}} \mathbf{d}
$$$$
\text{dist} = \|\mathbf{c}_{\text{3D}} - \mathbf{p}_{\text{close}}\|
$$

---

## 8. Бросок объекта (преобразование 2D → 4D)

Вектор перетаскивания мышью: $\mathbf{drag} = (dx, dy) \in \mathbb{R}^2$

Преобразование в 4D-силу:

$$
\mathbf{F} = (k_x \cdot dx,\; -k_y \cdot dy,\; k_z \cdot dx,\; k_w \cdot dy)
$$

```python
def throw_object(self):
    drag_vector = (self.drag_start_mouse - mouse_end) * 0.1

    force = np.zeros(4)
    force[0] = drag_vector[0] * 5.0
    force[1] = -drag_vector[1] * 5.0
    force[2] = drag_vector[0] * 3.0
    force[3] = drag_vector[1] * 2.0

    self.dragged_obj.apply_force(force)
```

---

## 9. Камера (сферические координаты)

Позиция камеры в 3D:

$$
\mathbf{cam} = \rho \cdot
\begin{pmatrix}
\sin\theta_y \cos\theta_x \\
\sin\theta_x \\
\cos\theta_y \cos\theta_x
\end{pmatrix}
$$

```python
def setup_camera(self):
    cam_x = self.cam_dist * math.sin(math.radians(self.cam_angle_y)) * math.cos(math.radians(self.cam_angle_x))
    cam_y = self.cam_dist * math.sin(math.radians(self.cam_angle_x))
    cam_z = self.cam_dist * math.cos(math.radians(self.cam_angle_y)) * math.cos(math.radians(self.cam_angle_x))
    gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 1, 0)
```

---

## 10. Параметры модели

| Параметр | Значение | Описание |
| --- | --- | --- |
| $d_w$ | 4.0 | Расстояние проекции 4D→3D |
| $g_y$ | 8.0 | Гравитация по оси Y |
| $g_w$ | 2.0 | Гравитация по оси W |
| $\mu_v$ | 0.995 | Демпфирование скорости |
| $k_x, k_y$ | 5.0, 5.0 | Коэффициенты броска (XY) |
| $k_z, k_w$ | 3.0, 2.0 | Коэффициенты броска (ZW) |
| $\Delta t$ | 1/60 с | Шаг интегрирования |

---

## 📚 Источники для ознакомления с многомерной физикой

### Математические основы

- Фрид Д., Уленбек К. *Инстантоны и четырехмерные многообразия*. — М.: Мир, 1988. — 272 с. [citation:3][citation:6]
- Владимиров Ю. С. *Геометрофизика*. — М.: Бином. Лаборатория знаний, 2005. — 600 с. [citation:9]
- Samuelson G. *Math Moments – Finding Directions in 4-D* / Dr. Gary Samuelson (блог) [citation:4]

### Визуализация и программирование

- [Interactive 4D Hypercube Visualization](https://github.com/D4YonSoundcloud/Interactive-4D-Hypercube-Rotation-Projection-Visualization) — Three.js, WebGL [citation:5]
- [4d-visualizer](https://github.com/Sir-CussFreq/4d-visualizer) — Python, визуализация 4D-политопов [citation:8]
- [Tak4D](https://www.raktres.net/tak4d/) — инструмент для 4D-визуализации [citation:10]

### Физика высших измерений

- [4D Quantum Projection Theory](https://github.com/Mazen-zaino/4D-Quantum-Projection-Theory) (DOI: 10.5281/zenodo.15646962) [citation:1]
- Razamat S. *Aspects of 4d Supersymmetric Dynamics and Geometry* — лекция [citation:7]
