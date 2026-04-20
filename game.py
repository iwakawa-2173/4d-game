import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random

# ========== 4D Математика ==========
def project_4d_to_3d(point_4d, w_distance=4.0):
    x, y, z, w = point_4d
    factor = w_distance / (w_distance - w + 0.001)
    return (x * factor, y * factor, z * factor)

def rotate_4d(point_4d, angles):
    x, y, z, w = point_4d
    xy, xz, xw, yz, yw, zw = angles
    
    x2 = x * math.cos(xy) - y * math.sin(xy)
    y2 = x * math.sin(xy) + y * math.cos(xy)
    x, y = x2, y2
    
    x2 = x * math.cos(xz) - z * math.sin(xz)
    z2 = x * math.sin(xz) + z * math.cos(xz)
    x, z = x2, z2
    
    x2 = x * math.cos(xw) - w * math.sin(xw)
    w2 = x * math.sin(xw) + w * math.cos(xw)
    x, w = x2, w2
    
    y2 = y * math.cos(yz) - z * math.sin(yz)
    z2 = y * math.sin(yz) + z * math.cos(yz)
    y, z = y2, z2
    
    y2 = y * math.cos(yw) - w * math.sin(yw)
    w2 = y * math.sin(yw) + w * math.cos(yw)
    y, w = y2, w2
    
    z2 = z * math.cos(zw) - w * math.sin(zw)
    w2 = z * math.sin(zw) + w * math.cos(zw)
    z, w = z2, w2
    
    return (x, y, z, w)

# ========== 4D Объекты ==========
class HyperObject4D:
    def __init__(self, obj_type, pos_4d, color, size=1.0):
        self.obj_type = obj_type
        self.pos_4d = np.array(pos_4d, dtype=float)
        self.vel_4d = np.zeros(4)
        self.color = color
        self.size = size
        self.mass = 1.0
        self.angles_4d = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.angular_vel = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        if obj_type == 'cube':
            self.vertices_4d = self.generate_tesseract_vertices()
            self.edges = self.generate_tesseract_edges()
        else:
            self.vertices_4d = self.generate_hypersphere_points()
    
    def generate_tesseract_vertices(self):
        verts = []
        for x in (-self.size, self.size):
            for y in (-self.size, self.size):
                for z in (-self.size, self.size):
                    for w in (-self.size, self.size):
                        verts.append([x, y, z, w])
        return np.array(verts)
    
    def generate_tesseract_edges(self):
        edges = []
        verts = self.vertices_4d
        for i in range(len(verts)):
            for j in range(i+1, len(verts)):
                diff = 0
                for k in range(4):
                    if abs(verts[i][k] - verts[j][k]) > 0.01:
                        diff += 1
                if diff == 1:
                    edges.append((i, j))
        return edges
    
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
    
    def apply_force(self, force):
        self.vel_4d += force / self.mass
    
    def update_physics(self, dt, objects_list, gravity_4d):
        self.vel_4d += gravity_4d * dt
        self.pos_4d += self.vel_4d * dt
        
        for i in range(6):
            self.angles_4d[i] += self.angular_vel[i] * dt
        
        self.vel_4d *= 0.995
        for i in range(6):
            self.angular_vel[i] *= 0.99
        
        boundary = 7.0
        for i in range(4):
            if abs(self.pos_4d[i]) > boundary:
                self.pos_4d[i] = math.copysign(boundary, self.pos_4d[i])
                self.vel_4d[i] *= -0.7
        
        for other in objects_list:
            if other is self:
                continue
            
            delta = self.pos_4d - other.pos_4d
            dist = np.linalg.norm(delta)
            min_dist = self.size + other.size
            
            if dist < min_dist:
                overlap = min_dist - dist
                direction = delta / (dist + 0.001)
                self.pos_4d += direction * overlap * 0.5
                other.pos_4d -= direction * overlap * 0.5
                
                v1 = self.vel_4d.copy()
                v2 = other.vel_4d.copy()
                m1, m2 = self.mass, other.mass
                
                self.vel_4d = (v1*(m1-m2) + 2*m2*v2) / (m1+m2)
                other.vel_4d = (v2*(m2-m1) + 2*m1*v1) / (m1+m2)
                
                torque = [random.uniform(-0.3, 0.3) for _ in range(6)]
                for i in range(6):
                    self.angular_vel[i] += torque[i] * 0.2
                    other.angular_vel[i] += torque[i] * 0.2
    
    def get_transformed_vertices(self, w_offset=0.0):
        transformed = []
        for vert in self.vertices_4d:
            rotated = rotate_4d(vert, self.angles_4d)
            world = (rotated[0] + self.pos_4d[0],
                    rotated[1] + self.pos_4d[1],
                    rotated[2] + self.pos_4d[2],
                    rotated[3] + self.pos_4d[3] + w_offset)
            proj = project_4d_to_3d(world)
            transformed.append(proj)
        return transformed
    
    def render(self, w_offset=0.0):
        verts_3d = self.get_transformed_vertices(w_offset)
        
        if self.obj_type == 'cube':
            glLineWidth(2.5)
            glColor4f(self.color[0], self.color[1], self.color[2], 1.0)
            glBegin(GL_LINES)
            for edge in self.edges:
                glVertex3f(*verts_3d[edge[0]])
                glVertex3f(*verts_3d[edge[1]])
            glEnd()
            
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(self.color[0], self.color[1], self.color[2], 0.1)
            for i in range(0, len(verts_3d), 4):
                if i+3 < len(verts_3d):
                    glBegin(GL_QUADS)
                    glVertex3f(*verts_3d[i])
                    glVertex3f(*verts_3d[i+1])
                    glVertex3f(*verts_3d[i+2])
                    glVertex3f(*verts_3d[i+3])
                    glEnd()
            glDisable(GL_BLEND)
        else:
            glPointSize(3.0)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(self.color[0], self.color[1], self.color[2], 0.8)
            glBegin(GL_POINTS)
            for vert in verts_3d:
                glVertex3f(*vert)
            glEnd()
            glDisable(GL_BLEND)

# ========== Основная игра (без UI полос) ==========
class FourDPhysics:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("4D Physics")
        self.clock = pygame.time.Clock()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.05, 0.05, 0.1, 1.0)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, 1024/768, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        self.objects = []
        self.objects.append(HyperObject4D('cube', (-2, 0, -2, 0), (0.2, 0.6, 1.0, 1.0), size=0.8))
        self.objects.append(HyperObject4D('sphere', (2, 1, -1, 0.5), (1.0, 0.3, 0.7, 1.0), size=0.7))
        self.objects.append(HyperObject4D('cube', (0, -1, 2, -0.5), (0.3, 1.0, 0.4, 1.0), size=0.7))
        
        self.gravity_4d = np.array([0.0, -8.0, 0.0, -2.0])
        self.w_offset = 0.0
        
        self.cam_dist = 12.0
        self.cam_angle_x = 30.0
        self.cam_angle_y = 45.0
        self.mouse_down = False
        self.mouse_last = (0, 0)
        
        self.dragged_obj = None
        self.drag_start_mouse = None
        self.is_dragging = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                elif event.key == K_SPACE:
                    for obj in self.objects:
                        force = np.random.uniform(-15, 15, 4)
                        obj.apply_force(force)
                elif event.key == K_r:
                    self.reset_scene()
                elif event.key == K_t:
                    self.objects.append(HyperObject4D('sphere', 
                        (random.uniform(-3,3), random.uniform(0,3), random.uniform(-2,2), random.uniform(-2,2)),
                        (random.random(), random.random(), random.random(), 1.0), size=0.6))
                elif event.key == K_y:
                    self.objects.append(HyperObject4D('cube',
                        (random.uniform(-3,3), random.uniform(0,3), random.uniform(-2,2), random.uniform(-2,2)),
                        (random.random(), random.random(), random.random(), 1.0), size=0.7))
                elif event.key == K_UP:
                    self.w_offset += 0.2
                elif event.key == K_DOWN:
                    self.w_offset -= 0.2
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.start_drag()
                elif event.button == 3:
                    self.mouse_down = True
                    self.mouse_last = event.pos
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and self.is_dragging:
                    self.throw_object()
                elif event.button == 3:
                    self.mouse_down = False
            elif event.type == MOUSEMOTION:
                if self.is_dragging:
                    self.update_drag()
                elif self.mouse_down:
                    dx, dy = event.pos[0] - self.mouse_last[0], event.pos[1] - self.mouse_last[1]
                    self.cam_angle_y += dx * 0.5
                    self.cam_angle_x += dy * 0.5
                    self.cam_angle_x = max(10, min(80, self.cam_angle_x))
                    self.mouse_last = event.pos
        
        return True
    
    def start_drag(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        ray_origin, ray_dir = self.get_mouse_ray(mouse_x, mouse_y)
        
        best_obj = None
        best_dist = 1.0
        
        for obj in self.objects:
            center_3d = project_4d_to_3d((obj.pos_4d[0], obj.pos_4d[1], obj.pos_4d[2], obj.pos_4d[3] + self.w_offset))
            to_center = np.array(center_3d) - ray_origin
            proj_len = np.dot(to_center, ray_dir)
            if proj_len < 0:
                continue
            closest = ray_origin + ray_dir * proj_len
            dist = np.linalg.norm(np.array(center_3d) - closest)
            
            if dist < best_dist:
                best_dist = dist
                best_obj = obj
        
        if best_obj:
            self.dragged_obj = best_obj
            self.drag_start_mouse = np.array(pygame.mouse.get_pos())
            self.is_dragging = True
            best_obj.vel_4d *= 0
    
    def throw_object(self):
        if self.dragged_obj and self.drag_start_mouse is not None:
            mouse_end = np.array(pygame.mouse.get_pos())
            drag_vector = (self.drag_start_mouse - mouse_end) * 0.1
            
            force = np.zeros(4)
            force[0] = drag_vector[0] * 5.0
            force[1] = -drag_vector[1] * 5.0
            force[2] = drag_vector[0] * 3.0
            force[3] = drag_vector[1] * 2.0
            
            self.dragged_obj.apply_force(force)
            
            torque = [random.uniform(-0.3, 0.3) * np.linalg.norm(drag_vector) for _ in range(6)]
            for i in range(6):
                self.dragged_obj.angular_vel[i] += torque[i]
        
        self.dragged_obj = None
        self.is_dragging = False
        self.drag_start_mouse = None
    
    def update_drag(self):
        if self.is_dragging and self.dragged_obj:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            ray_origin, ray_dir = self.get_mouse_ray(mouse_x, mouse_y)
            
            obj_center = project_4d_to_3d((self.dragged_obj.pos_4d[0], self.dragged_obj.pos_4d[1],
                                          self.dragged_obj.pos_4d[2], self.dragged_obj.pos_4d[3] + self.w_offset))
            
            to_center = np.array(obj_center) - ray_origin
            t = np.dot(to_center, ray_dir)
            hit_point = ray_origin + ray_dir * t
            
            self.dragged_obj.pos_4d[0] = hit_point[0]
            self.dragged_obj.pos_4d[1] = hit_point[1]
            self.dragged_obj.pos_4d[2] = hit_point[2]
            self.dragged_obj.vel_4d[:3] = 0
    
    def get_mouse_ray(self, mouse_x, mouse_y):
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        pos_near = gluUnProject(mouse_x, viewport[3] - mouse_y, 0.0, modelview, projection, viewport)
        pos_far = gluUnProject(mouse_x, viewport[3] - mouse_y, 1.0, modelview, projection, viewport)
        origin = np.array(pos_near)
        direction = np.array(pos_far) - origin
        direction = direction / np.linalg.norm(direction)
        return origin, direction
    
    def reset_scene(self):
        self.objects.clear()
        self.objects.append(HyperObject4D('cube', (-2, 0, -2, 0), (0.2, 0.6, 1.0, 1.0), size=0.8))
        self.objects.append(HyperObject4D('sphere', (2, 1, -1, 0.5), (1.0, 0.3, 0.7, 1.0), size=0.7))
        self.objects.append(HyperObject4D('cube', (0, -1, 2, -0.5), (0.3, 1.0, 0.4, 1.0), size=0.7))
        self.w_offset = 0.0
    
    def update(self, dt):
        for obj in self.objects:
            obj.update_physics(dt, self.objects, self.gravity_4d)
    
    def setup_camera(self):
        glLoadIdentity()
        cam_x = self.cam_dist * math.sin(math.radians(self.cam_angle_y)) * math.cos(math.radians(self.cam_angle_x))
        cam_y = self.cam_dist * math.sin(math.radians(self.cam_angle_x))
        cam_z = self.cam_dist * math.cos(math.radians(self.cam_angle_y)) * math.cos(math.radians(self.cam_angle_x))
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 1, 0)
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.setup_camera()
        
        # Сетка пола
        glColor4f(0.3, 0.3, 0.5, 0.5)
        glBegin(GL_LINES)
        for i in range(-8, 9):
            glVertex3f(i, -2.5, -8)
            glVertex3f(i, -2.5, 8)
            glVertex3f(-8, -2.5, i)
            glVertex3f(8, -2.5, i)
        glEnd()
        
        # Оси координат
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex3f(-6, 0, 0)
        glVertex3f(6, 0, 0)
        glColor3f(0, 1, 0)
        glVertex3f(0, -3, 0)
        glVertex3f(0, 5, 0)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, -6)
        glVertex3f(0, 0, 6)
        glEnd()
        glLineWidth(1.0)
        
        # Объекты
        for obj in self.objects:
            obj.render(self.w_offset)
        
        # Визуализация оси W
        glPointSize(5)
        glColor4f(1.0, 0.5, 1.0, 0.8)
        glBegin(GL_POINTS)
        for w in np.arange(-3, 4, 0.5):
            proj = project_4d_to_3d((0, 0, 0, w + self.w_offset))
            glVertex3f(*proj)
        glEnd()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        dt = 1/60.0
        while running:
            running = self.handle_events()
            self.update(dt)
            self.render()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = FourDPhysics()
    game.run()