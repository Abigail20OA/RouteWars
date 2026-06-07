import math
import os
import random

import pygame


WIDTH = 1000
HEIGHT = 650
TITLE = "ROUTE WARS"
FPS = 60
TOTAL_ROUNDS = 5
ASSETS_DIR = "assets"
MENU_BACKGROUND_PATH = os.path.join(ASSETS_DIR, "menu_background.png")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo_route_wars.png")
PAGO_MIN = 70
PAGO_MAX = 95
DIFERENCIA_MINIMA_PAGO = 6
PROB_EMPATE = 0.15

SKY = (122, 207, 244)
SKY_DARK = (80, 177, 226)
GRASS = (92, 186, 84)
GRASS_DARK = (61, 148, 67)
HILL = (83, 169, 86)
HILL_LIGHT = (116, 198, 99)
MOUNTAIN = (92, 125, 142)
MOUNTAIN_LIGHT = (133, 166, 177)
ROAD = (76, 78, 84)
ROAD_EDGE = (48, 50, 54)
ROAD_LINE = (244, 208, 64)
WHITE = (255, 255, 255)
INK = (37, 43, 52)
PANEL = (255, 248, 226)
PANEL_DARK = (226, 210, 170)
ORANGE = (242, 132, 45)
ORANGE_DARK = (190, 84, 36)
BLUE = (53, 132, 205)
BLUE_DARK = (31, 91, 151)
GREEN = (59, 177, 92)
GREEN_DARK = (32, 126, 66)
RED = (222, 74, 74)
YELLOW = (247, 204, 68)
PURPLE = (127, 95, 183)

ROUTE_NAMES = ["Ruta A", "Ruta B", "Ruta C"]
ROUTE_KEYS = ["A", "B", "C"]
ROUTE_Y = [250, 365, 480]
ROADS = {
    "A": ROUTE_Y[0],
    "B": ROUTE_Y[1],
    "C": ROUTE_Y[2],
}
MIN_TRAFFIC_DISTANCE = 120
TRAFFIC_X_MIN = 80
TRAFFIC_X_MAX = 850
CAR_COLORS = {
    "Verde": (45, 181, 90),
    "Amarillo": (246, 204, 67),
    "Azul": (50, 134, 220),
    "Rojo": (224, 69, 70),
}
AI_COLOR = (170, 94, 220)
TRAFFIC_COLORS = [
    (239, 92, 84),
    (64, 154, 223),
    (252, 196, 72),
    (72, 188, 120),
    (238, 128, 62),
    (137, 112, 212),
]
DIALOGS = [
    "Oh no! Trafico",
    "Voy ganando",
    "Mala eleccion...",
    "Buena ruta",
    "La IA se adelanto",
    "Esto se puso lento",
]


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def draw_text(surface, text, font, color, pos, anchor="topleft"):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    setattr(rect, anchor, pos)
    surface.blit(rendered, rect)
    return rect


def wrap_text(text, font, max_width):
    lines = []
    for raw_line in text.split("\n"):
        words = raw_line.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            test = line + " " + word
            if font.size(test)[0] <= max_width:
                line = test
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_paragraph(surface, text, font, color, x, y, max_width, line_height):
    for line in wrap_text(text, font, max_width):
        draw_text(surface, line, font, color, (x, y))
        y += line_height
    return y


def brighten(color, amount):
    return tuple(clamp(channel + amount, 0, 255) for channel in color)


def draw_button(surface, rect, text, color, hover=False, font=None, shadow=None):
    rect = pygame.Rect(rect)
    if font is None:
        font = pygame.font.SysFont("arial", 26, bold=True)
    if shadow is None:
        shadow = tuple(max(0, channel - 55) for channel in color)

    draw_rect = rect.inflate(8, 6) if hover else rect.copy()
    draw_rect.center = rect.center
    body_color = brighten(color, 26) if hover else color
    shadow_rect = draw_rect.move(0, 8)

    pygame.draw.rect(surface, shadow, shadow_rect, border_radius=18)
    pygame.draw.rect(surface, body_color, draw_rect, border_radius=18)
    pygame.draw.rect(surface, WHITE, draw_rect, 4, border_radius=18)
    pygame.draw.line(surface, brighten(body_color, 42), (draw_rect.left + 18, draw_rect.top + 11), (draw_rect.right - 18, draw_rect.top + 11), 3)

    text_shadow = font.render(text, True, (40, 54, 68))
    text_rect = text_shadow.get_rect(center=(draw_rect.centerx + 2, draw_rect.centery + 3))
    surface.blit(text_shadow, text_rect)
    draw_text(surface, text, font, WHITE, draw_rect.center, "center")


class Button:
    def __init__(self, rect, text, action, color=ORANGE, shadow=ORANGE_DARK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.color = color
        self.shadow = shadow

    def draw(self, surface, font, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        y_offset = -2 if hovered else 0
        shadow_rect = self.rect.move(0, 6)
        body_rect = self.rect.move(0, y_offset)
        pygame.draw.rect(surface, self.shadow, shadow_rect, border_radius=14)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=14)
        pygame.draw.rect(surface, WHITE, body_rect, 3, border_radius=14)
        draw_text(surface, self.text, font, WHITE, body_rect.center, "center")

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class RouteWars:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arial", 70, bold=True)
        self.font_logo = pygame.font.SysFont("arialblack", 72, bold=True)
        self.font_big = pygame.font.SysFont("arial", 38, bold=True)
        self.font_mid = pygame.font.SysFont("arial", 26, bold=True)
        self.font_body = pygame.font.SysFont("arial", 20)
        self.font_small = pygame.font.SysFont("arial", 16)
        self.font_tiny = pygame.font.SysFont("arial", 14)
        self.menu_button_font = pygame.font.SysFont("arialblack", 30, bold=True)
        self.menu_background = self.load_menu_background()
        self.logo_image = self.load_logo_image()
        self.menu_background_warning_shown = self.menu_background is not None

        self.state = "start"
        self.previous_state = "start"
        self.running = True
        self.player_style = "Libre"
        self.player_color_name = "Verde"
        self.player_color = CAR_COLORS[self.player_color_name]
        self.buttons = []
        self.message = random.choice(DIALOGS)
        self.reset_match()

    def reset_match(self):
        self.ronda_actual = 0
        self.puntos_jugador = 0
        self.puntos_ia = 0
        self.victorias_jugador = 0
        self.victorias_ia = 0
        self.empates = 0
        self.resultado_ronda_contado = False
        self.round_number = self.ronda_actual
        self.player_score = self.puntos_jugador
        self.ai_score = self.puntos_ia
        self.wins = self.victorias_jugador
        self.draws = self.empates
        self.losses = self.victorias_ia
        self.round_history = []
        self.current_conditions = None
        self.current_matrix = None
        self.current_player_route = None
        self.current_ai_route = None
        self.current_player_time = 0
        self.current_ai_time = 0
        self.current_result = ""
        self.current_points = (0, 0)
        self.sim_start = 0
        self.sim_duration = 4300
        self.traffic_cars = []

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.handle_event(event)

            self.update(dt)
            self.draw(mouse_pos)
            pygame.display.flip()

        pygame.quit()

    def handle_event(self, event):
        for button in self.buttons:
            if button.clicked(event):
                self.handle_action(button.action)
                break

    def handle_action(self, action):
        if action == "quit":
            self.running = False
        elif action == "play":
            self.state = "intro"
        elif action == "how":
            self.previous_state = self.state
            self.state = "how"
        elif action == "theory":
            self.previous_state = self.state
            self.state = "theory"
        elif action == "back":
            self.state = self.previous_state
        elif action == "setup":
            self.state = "setup"
        elif action.startswith("style:"):
            self.player_style = action.split(":", 1)[1]
        elif action.startswith("color:"):
            self.player_color_name = action.split(":", 1)[1]
            self.player_color = CAR_COLORS[self.player_color_name]
        elif action == "start_match":
            self.reset_match()
            self.start_round()
        elif action.startswith("route:"):
            route_index = int(action.split(":", 1)[1])
            self.choose_route(route_index)
        elif action == "next_round":
            if self.round_number >= TOTAL_ROUNDS:
                self.state = "final"
            else:
                self.start_round()
        elif action == "report":
            self.previous_state = self.state
            self.state = "report"
        elif action == "restart":
            self.reset_match()
            self.state = "setup"

    def start_round(self):
        self.ronda_actual += 1
        self.round_number = self.ronda_actual
        self.resultado_ronda_contado = False
        self.current_conditions = self.generate_conditions()
        self.current_matrix = self.build_payoff_matrix(self.current_conditions)
        self.current_player_route = None
        self.current_ai_route = None
        self.current_result = ""
        self.current_points = (0, 0)
        self.traffic_cars = []
        self.message = self.recommendation_message()
        self.state = "round"

    def generate_conditions(self):
        base_values = [random.uniform(8.0, 14.0) for _ in ROUTE_NAMES]
        random.shuffle(base_values)
        capacities = [random.randint(3, 6) for _ in ROUTE_NAMES]
        random.shuffle(capacities)
        congestion = [random.randint(1, 5) for _ in ROUTE_NAMES]
        random.shuffle(congestion)
        ambient = [random.randint(3, 8) for _ in ROUTE_NAMES]
        random.shuffle(ambient)
        incident = [random.uniform(-0.4, 0.9) for _ in ROUTE_NAMES]
        random.shuffle(incident)
        return {
            "base": base_values,
            "capacity": capacities,
            "congestion": congestion,
            "ambient": ambient,
            "incident": incident,
        }

    def calculate_time(self, conditions, route_index, player_route, ai_route):
        count = 0
        if player_route == route_index:
            count += 1
        if ai_route == route_index:
            count += 1
        load = conditions["congestion"][route_index] + count
        capacity = conditions["capacity"][route_index]
        ambient = conditions["ambient"][route_index]
        overload = max(0, load - capacity)
        traffic_pressure = (load / capacity) * 1.25
        ambient_pressure = ambient * 0.16
        shared_penalty = 0.85 if player_route == ai_route == route_index else 0
        time_value = (
            conditions["base"][route_index]
            + traffic_pressure
            + ambient_pressure
            + overload * 1.15
            + shared_penalty
            + conditions["incident"][route_index]
        )
        return round(clamp(time_value, 8.0, 18.0), 1)

    def build_payoff_matrix(self, conditions):
        matrix = []
        for player_route in range(3):
            row = []
            for ai_route in range(3):
                player_payoff, ai_payoff = self.generar_par_pago()
                row.append(
                    {
                        "player_time": round(100 - player_payoff, 1),
                        "ai_time": round(100 - ai_payoff, 1),
                        "player_payoff": player_payoff,
                        "ai_payoff": ai_payoff,
                    }
                )
            matrix.append(row)
        return matrix

    def generar_par_pago(self):
        if random.random() < PROB_EMPATE:
            pago = random.randint(PAGO_MIN, PAGO_MAX)
            return pago, pago

        for _ in range(80):
            pago_jugador = random.randint(PAGO_MIN, PAGO_MAX)
            pago_ia = random.randint(PAGO_MIN, PAGO_MAX)
            if abs(pago_jugador - pago_ia) >= DIFERENCIA_MINIMA_PAGO:
                return pago_jugador, pago_ia

        if random.random() < 0.5:
            pago_jugador = random.randint(PAGO_MIN + DIFERENCIA_MINIMA_PAGO, PAGO_MAX)
            pago_ia = random.randint(PAGO_MIN, pago_jugador - DIFERENCIA_MINIMA_PAGO)
        else:
            pago_ia = random.randint(PAGO_MIN + DIFERENCIA_MINIMA_PAGO, PAGO_MAX)
            pago_jugador = random.randint(PAGO_MIN, pago_ia - DIFERENCIA_MINIMA_PAGO)
        return pago_jugador, pago_ia

    def maximin_route(self):
        worst_values = []
        for row in self.current_matrix:
            worst_values.append(min(cell["player_payoff"] for cell in row))
        return worst_values.index(max(worst_values))

    def minimax_route(self):
        regret_by_route = []
        for player_route in range(3):
            worst_regret = 0
            for ai_route in range(3):
                best_payoff = max(self.current_matrix[row][ai_route]["player_payoff"] for row in range(3))
                actual_payoff = self.current_matrix[player_route][ai_route]["player_payoff"]
                worst_regret = max(worst_regret, best_payoff - actual_payoff)
            regret_by_route.append(worst_regret)
        return regret_by_route.index(min(regret_by_route))

    def nash_routes(self):
        equilibria = []
        for player_route in range(3):
            for ai_route in range(3):
                player_best = max(self.current_matrix[row][ai_route]["player_payoff"] for row in range(3))
                ai_best = max(self.current_matrix[player_route][col]["ai_payoff"] for col in range(3))
                cell = self.current_matrix[player_route][ai_route]
                if cell["player_payoff"] == player_best and cell["ai_payoff"] == ai_best:
                    equilibria.append((player_route, ai_route))
        return equilibria

    def nash_recommendation(self):
        equilibria = self.nash_routes()
        if equilibria:
            random.shuffle(equilibria)
            return equilibria[0][0]
        return self.maximin_route()

    def recommendation_message(self):
        if self.player_style == "Conservador":
            route = ROUTE_NAMES[self.maximin_route()]
            return "Pensamiento Maximin: protege tu peor escenario. Considera " + route + "."
        if self.player_style == "Estrategico":
            route = ROUTE_NAMES[self.minimax_route()]
            return "Pensamiento Minimax: reduce la mayor perdida posible. Considera " + route + "."
        if self.player_style == "Equilibrado":
            route = ROUTE_NAMES[self.nash_recommendation()]
            return "Pensamiento Nash: busca estabilidad estrategica. Considera " + route + "."
        return "Elige libremente: aqui no hay pistas, solo intuicion y riesgo."

    def choose_route(self, player_route):
        self.current_player_route = player_route
        self.current_ai_route = self.choose_ai_route(player_route)
        cell = self.current_matrix[player_route][self.current_ai_route]
        self.current_player_time = cell["player_time"]
        self.current_ai_time = cell["ai_time"]
        self.current_result = self.determine_round_result()
        self.message = self.simulation_message()
        self.prepare_simulation_cars()
        self.sim_start = pygame.time.get_ticks()
        self.state = "simulation"

    def choose_ai_route(self, player_route):
        roll = random.random()
        if roll < 0.58:
            row = self.current_matrix[player_route]
            best = max(cell["ai_payoff"] for cell in row)
            choices = [i for i, cell in enumerate(row) if cell["ai_payoff"] == best]
            return random.choice(choices)
        if roll < 0.82:
            expected = []
            for ai_route in range(3):
                expected.append(sum(self.current_matrix[p][ai_route]["ai_payoff"] for p in range(3)) / 3)
            return expected.index(max(expected))
        return random.randint(0, 2)

    def determine_round_result(self):
        if abs(self.current_player_time - self.current_ai_time) <= 0.3:
            return "Empate"
        if self.current_player_time < self.current_ai_time:
            return "Gano el jugador"
        return "Gano la IA"

    def resolve_points(self):
        if self.resultado_ronda_contado:
            return

        if self.current_result == "Gano el jugador":
            self.puntos_jugador += 3
            self.victorias_jugador += 1
            self.current_points = (3, 0)
        elif self.current_result == "Gano la IA":
            self.puntos_ia += 3
            self.victorias_ia += 1
            self.current_points = (0, 3)
        else:
            self.puntos_jugador += 1
            self.puntos_ia += 1
            self.empates += 1
            self.current_points = (1, 1)

        self.player_score = self.puntos_jugador
        self.ai_score = self.puntos_ia
        self.wins = self.victorias_jugador
        self.losses = self.victorias_ia
        self.draws = self.empates
        self.resultado_ronda_contado = True

        self.round_history.append(
            {
                "round": self.round_number,
                "player_route": self.current_player_route,
                "ai_route": self.current_ai_route,
                "player_time": self.current_player_time,
                "ai_time": self.current_ai_time,
                "result": self.current_result,
                "points": self.current_points,
                "matrix": self.current_matrix,
                "conditions": self.current_conditions,
                "maximin": self.maximin_route(),
                "minimax": self.minimax_route(),
                "nash": self.nash_routes(),
            }
        )
        self.print_score_debug()

    def print_score_debug(self):
        print(
            "DEBUG RONDA | "
            f"resultado={self.current_result} | "
            f"puntos_jugador={self.puntos_jugador} | "
            f"puntos_ia={self.puntos_ia} | "
            f"victorias_jugador={self.victorias_jugador} | "
            f"victorias_ia={self.victorias_ia} | "
            f"empates={self.empates} | "
            f"ronda_actual={self.ronda_actual}"
        )

    def simulation_message(self):
        congested_route = self.most_congested_route(self.current_conditions)
        if self.current_player_route == congested_route:
            return random.choice(["Oh no! Trafico", "Esto se puso lento", "Mala eleccion..."])
        if self.current_player_time < self.current_ai_time:
            return random.choice(["Voy ganando", "Buena ruta"])
        if self.current_player_time > self.current_ai_time:
            return "La IA se adelanto"
        return "Final cerrado"

    def prepare_simulation_cars(self):
        total_cars = sum(self.current_conditions["ambient"])
        total_cars += 2 if self.current_player_route is not None else 0
        total_cars += 2 if self.current_ai_route is not None else 0
        self.traffic_cars = self.generar_autos(total_cars)

    def posicion_valida(self, x, y, autos, distancia_minima):
        for auto in autos:
            if abs(auto["road_y"] - y) < 10 and abs(auto["x"] - x) < distancia_minima:
                return False
        return True

    def generar_autos(self, cantidad):
        autos = []
        rutas = self.distribuir_rutas_para_autos(cantidad)

        for route_key in rutas:
            y = ROADS[route_key]
            route_index = ROUTE_KEYS.index(route_key)
            x = self.buscar_x_libre(y, autos, TRAFFIC_X_MIN, TRAFFIC_X_MAX, MIN_TRAFFIC_DISTANCE)
            autos.append(
                {
                    "route": route_index,
                    "road": route_key,
                    "road_y": y,
                    "x": x,
                    "offset": random.choice([-18, 18]),
                    "speed": random.uniform(35, 75)
                    / (1 + self.current_conditions["congestion"][route_index] * 0.18),
                    "color": random.choice(TRAFFIC_COLORS),
                    "size": random.randint(22, 31),
                }
            )

        return autos

    def distribuir_rutas_para_autos(self, cantidad):
        rutas_disponibles = list(ROADS.keys())
        random.shuffle(rutas_disponibles)
        if cantidad <= len(rutas_disponibles):
            return rutas_disponibles[:cantidad]

        max_por_ruta = self.max_autos_por_carretera(TRAFFIC_X_MIN, TRAFFIC_X_MAX, MIN_TRAFFIC_DISTANCE)
        conteo = {route_key: 0 for route_key in rutas_disponibles}
        rutas = rutas_disponibles[:]
        for route_key in rutas:
            conteo[route_key] += 1

        pesos = []
        for index, route_key in enumerate(ROUTE_KEYS):
            peso = self.current_conditions["ambient"][index]
            if index == self.current_player_route:
                peso += 2
            if index == self.current_ai_route:
                peso += 2
            pesos.extend([route_key] * max(1, peso))

        while len(rutas) < cantidad:
            candidatos = [route_key for route_key in pesos if conteo[route_key] < max_por_ruta]
            if not candidatos:
                break
            route_key = random.choice(candidatos)
            rutas.append(route_key)
            conteo[route_key] += 1

        random.shuffle(rutas)
        return rutas

    def buscar_x_libre(self, y, autos, x_min, x_max, distancia_minima):
        posiciones = list(range(x_min, x_max + 1, distancia_minima + 8))
        random.shuffle(posiciones)
        for x in posiciones:
            x = clamp(x + random.randint(-4, 4), x_min, x_max)
            if self.posicion_valida(x, y, autos, distancia_minima):
                return x

        for _ in range(80):
            x = random.randint(x_min, x_max)
            if self.posicion_valida(x, y, autos, distancia_minima):
                return x

        ocupados = [auto["x"] for auto in autos if auto["road_y"] == y]
        for x in range(x_min, x_max + 1, distancia_minima):
            if all(abs(x - ocupado) >= distancia_minima for ocupado in ocupados):
                return x

        return random.randint(x_min, x_max)

    def max_autos_por_carretera(self, x_min, x_max, distancia_minima):
        return ((x_max - x_min) // (distancia_minima + 8)) + 1

    def reciclar_auto(self, car):
        y = car["road_y"]
        others = [auto for auto in self.traffic_cars if auto is not car]
        car["x"] = self.buscar_x_libre(y, others, -900, 60, MIN_TRAFFIC_DISTANCE)

    def update(self, dt):
        if self.state == "simulation":
            for car in self.traffic_cars:
                car["x"] += car["speed"] * dt
                if car["x"] > 920:
                    self.reciclar_auto(car)
            elapsed = pygame.time.get_ticks() - self.sim_start
            if elapsed >= self.sim_duration:
                self.resolve_points()
                self.state = "round_result"

    def draw(self, mouse_pos):
        self.buttons = []
        if self.state == "start":
            self.draw_start(mouse_pos)
        elif self.state == "intro":
            self.draw_intro(mouse_pos)
        elif self.state == "setup":
            self.draw_setup(mouse_pos)
        elif self.state == "round":
            self.draw_round(mouse_pos)
        elif self.state == "simulation":
            self.draw_simulation(mouse_pos)
        elif self.state == "round_result":
            self.draw_round_result(mouse_pos)
        elif self.state == "final":
            self.draw_final(mouse_pos)
        elif self.state == "report":
            self.draw_report(mouse_pos)
        elif self.state == "how":
            self.draw_how(mouse_pos)
        elif self.state == "theory":
            self.draw_theory(mouse_pos)

    def add_button(self, rect, text, action, color=ORANGE, shadow=ORANGE_DARK):
        button = Button(rect, text, action, color, shadow)
        self.buttons.append(button)
        return button

    def draw_buttons(self, mouse_pos):
        for button in self.buttons:
            button.draw(self.screen, self.font_mid, mouse_pos)

    def draw_world(self):
        self.screen.fill(SKY)
        pygame.draw.rect(self.screen, SKY_DARK, (0, 0, WIDTH, 160))
        pygame.draw.circle(self.screen, (255, 219, 93), (850, 86), 48)
        self.draw_cloud(170, 85, 1.05)
        self.draw_cloud(430, 120, 0.75)
        self.draw_cloud(690, 72, 0.9)

        pygame.draw.polygon(self.screen, MOUNTAIN, [(0, 285), (145, 120), (310, 285)])
        pygame.draw.polygon(self.screen, MOUNTAIN_LIGHT, [(95, 180), (145, 120), (197, 180)])
        pygame.draw.polygon(self.screen, (82, 114, 130), [(230, 295), (395, 115), (590, 295)])
        pygame.draw.polygon(self.screen, MOUNTAIN_LIGHT, [(340, 175), (395, 115), (458, 180)])
        pygame.draw.polygon(self.screen, MOUNTAIN, [(530, 290), (725, 130), (980, 290)])
        pygame.draw.polygon(self.screen, MOUNTAIN_LIGHT, [(665, 178), (725, 130), (794, 182)])

        pygame.draw.ellipse(self.screen, HILL_LIGHT, (-120, 245, 560, 210))
        pygame.draw.ellipse(self.screen, HILL, (360, 230, 760, 230))
        pygame.draw.rect(self.screen, GRASS, (0, 332, WIDTH, 318))
        pygame.draw.ellipse(self.screen, GRASS_DARK, (-80, 545, 460, 130))
        pygame.draw.ellipse(self.screen, (72, 164, 74), (580, 545, 560, 130))

        for x, y, scale in [(75, 335, 0.9), (905, 325, 0.95), (32, 515, 0.65), (940, 516, 0.7)]:
            self.draw_tree(x, y, scale)

    def draw_cloud(self, x, y, scale):
        color = (255, 255, 255)
        shade = (225, 241, 248)
        parts = [
            (0, 20, 34),
            (34, 0, 42),
            (78, 18, 36),
            (45, 28, 45),
        ]
        for dx, dy, radius in parts:
            pygame.draw.circle(self.screen, shade, (int(x + dx * scale), int(y + (dy + 5) * scale)), int(radius * scale))
        for dx, dy, radius in parts:
            pygame.draw.circle(self.screen, color, (int(x + dx * scale), int(y + dy * scale)), int(radius * scale))

    def draw_tree(self, x, y, scale):
        trunk = pygame.Rect(x - 9 * scale, y + 35 * scale, 18 * scale, 55 * scale)
        pygame.draw.rect(self.screen, (126, 86, 47), trunk, border_radius=5)
        for dx, dy, radius in [(-22, 22, 34), (0, 0, 40), (25, 24, 32), (2, 33, 35)]:
            pygame.draw.circle(self.screen, (36, 143, 75), (int(x + dx * scale), int(y + dy * scale)), int(radius * scale))
        pygame.draw.circle(self.screen, (70, 180, 95), (int(x - 8 * scale), int(y - 6 * scale)), int(18 * scale))

    def draw_roads(self):
        for index, y in enumerate(ROUTE_Y):
            points = [(85, y), (310, y - 12 + index * 7), (570, y + 12 - index * 8), (915, y)]
            pygame.draw.lines(self.screen, ROAD_EDGE, False, points, 82)
            pygame.draw.lines(self.screen, ROAD, False, points, 68)
            for x in range(130, 850, 84):
                pygame.draw.line(self.screen, ROAD_LINE, (x, y), (x + 38, y), 5)
            draw_text(self.screen, ROUTE_KEYS[index], self.font_big, WHITE, (48, y - 20))

        pygame.draw.rect(self.screen, (65, 112, 174), (28, 204, 92, 45), border_radius=9)
        draw_text(self.screen, "SALIDA", self.font_small, WHITE, (74, 226), "center")
        self.draw_finish_line()

    def draw_finish_line(self):
        x = 884
        y_top = ROUTE_Y[0] - 58
        height = (ROUTE_Y[-1] - ROUTE_Y[0]) + 116
        width = 58
        square = 14

        pygame.draw.rect(self.screen, (34, 38, 42), (x - 6, y_top - 8, width + 12, height + 16), border_radius=8)
        for row in range(math.ceil(height / square)):
            for col in range(math.ceil(width / square)):
                color = WHITE if (row + col) % 2 == 0 else INK
                pygame.draw.rect(self.screen, color, (x + col * square, y_top + row * square, square, square))
        pygame.draw.rect(self.screen, INK, (x, y_top, width, height), 3)

        meta_rect = pygame.Rect(x - 26, y_top + height // 2 - 28, 110, 56)
        pygame.draw.rect(self.screen, (67, 154, 81), meta_rect.move(0, 5), border_radius=12)
        pygame.draw.rect(self.screen, GREEN, meta_rect, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, meta_rect, 3, border_radius=12)
        draw_text(self.screen, "META", self.font_mid, WHITE, meta_rect.center, "center")

    def draw_car(self, x, y, color, scale=1.0, label=None):
        w = int(56 * scale)
        h = int(30 * scale)
        body = pygame.Rect(0, 0, w, h)
        body.center = (int(x), int(y))
        roof = pygame.Rect(0, 0, int(31 * scale), int(18 * scale))
        roof.midbottom = (body.centerx, body.top + int(8 * scale))
        pygame.draw.rect(self.screen, color, body, border_radius=int(9 * scale))
        pygame.draw.rect(self.screen, tuple(max(0, c - 35) for c in color), body, 3, border_radius=int(9 * scale))
        pygame.draw.rect(self.screen, (182, 229, 248), roof, border_radius=int(5 * scale))
        pygame.draw.circle(self.screen, INK, (body.left + int(13 * scale), body.bottom), int(6 * scale))
        pygame.draw.circle(self.screen, INK, (body.right - int(13 * scale), body.bottom), int(6 * scale))
        pygame.draw.circle(self.screen, (230, 232, 232), (body.left + int(13 * scale), body.bottom), int(3 * scale))
        pygame.draw.circle(self.screen, (230, 232, 232), (body.right - int(13 * scale), body.bottom), int(3 * scale))
        if label:
            tag = pygame.Rect(0, 0, int(46 * scale), int(22 * scale))
            tag.midbottom = (body.centerx, body.top - int(4 * scale))
            pygame.draw.rect(self.screen, WHITE, tag, border_radius=8)
            pygame.draw.rect(self.screen, INK, tag, 2, border_radius=8)
            draw_text(self.screen, label, self.font_tiny, INK, tag.center, "center")

    def draw_speech(self, text, x, y):
        lines = wrap_text(text, self.font_small, 210)
        width = max(160, max(self.font_small.size(line)[0] for line in lines) + 28)
        height = 28 + len(lines) * 19
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=16)
        pygame.draw.rect(self.screen, INK, rect, 2, border_radius=16)
        pygame.draw.polygon(self.screen, WHITE, [(x + 34, y + height - 2), (x + 54, y + height - 2), (x + 40, y + height + 18)])
        pygame.draw.line(self.screen, INK, (x + 34, y + height - 2), (x + 40, y + height + 18), 2)
        text_y = y + 12
        for line in lines:
            draw_text(self.screen, line, self.font_small, INK, (x + 14, text_y))
            text_y += 19

    def draw_panel(self, rect, title=None):
        pygame.draw.rect(self.screen, (150, 126, 82), pygame.Rect(rect).move(0, 6), border_radius=16)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=16)
        pygame.draw.rect(self.screen, PANEL_DARK, rect, 3, border_radius=16)
        if title:
            draw_text(self.screen, title, self.font_mid, INK, (rect.centerx, rect.y + 26), "center")

    def load_menu_background(self):
        if not os.path.exists(MENU_BACKGROUND_PATH):
            return None
        try:
            image = pygame.image.load(MENU_BACKGROUND_PATH).convert()
            return pygame.transform.smoothscale(image, (WIDTH, HEIGHT))
        except pygame.error:
            return None

    def load_logo_image(self):
        if not os.path.exists(LOGO_PATH):
            return None
        try:
            image = pygame.image.load(LOGO_PATH).convert_alpha()
            width = 520
            ratio = width / image.get_width()
            height = int(image.get_height() * ratio)
            return pygame.transform.smoothscale(image, (width, height))
        except pygame.error:
            return None

    def draw_menu_background(self, screen=None):
        screen = screen or self.screen
        if self.menu_background:
            screen.blit(self.menu_background, (0, 0))
            return

        if not self.menu_background_warning_shown:
            print("No se encontró menu_background.png, usando fondo simple.")
            self.menu_background_warning_shown = True

        screen.fill(SKY)
        pygame.draw.rect(self.screen, (31, 169, 231), (0, 0, WIDTH, 185))
        pygame.draw.circle(self.screen, (255, 224, 88), (858, 78), 48)
        pygame.draw.circle(self.screen, (255, 235, 134), (858, 78), 62, 4)
        self.draw_cloud(96, 70, 1.0)
        self.draw_cloud(710, 86, 0.75)
        self.draw_cloud(275, 145, 0.58)

        pygame.draw.polygon(self.screen, (86, 139, 160), [(0, 280), (120, 145), (255, 280)])
        pygame.draw.polygon(self.screen, (235, 246, 250), [(86, 185), (120, 145), (158, 185)])
        pygame.draw.polygon(self.screen, (99, 157, 176), [(188, 292), (350, 125), (535, 292)])
        pygame.draw.polygon(self.screen, (238, 249, 252), [(292, 185), (350, 125), (414, 188)])
        pygame.draw.polygon(self.screen, (83, 138, 157), [(602, 285), (735, 145), (940, 285)])
        pygame.draw.polygon(self.screen, (235, 246, 250), [(690, 190), (735, 145), (795, 195)])

        pygame.draw.rect(self.screen, (99, 188, 89), (0, 260, WIDTH, 390))
        pygame.draw.ellipse(self.screen, (129, 211, 94), (-100, 218, 560, 180))
        pygame.draw.ellipse(self.screen, (94, 177, 82), (545, 218, 590, 180))
        pygame.draw.ellipse(self.screen, (58, 151, 75), (-70, 548, 420, 130))
        pygame.draw.ellipse(self.screen, (58, 151, 75), (690, 548, 430, 130))

        self.draw_menu_map()
        self.draw_route_signpost(116, 252)
        self.draw_traffic_light(816, 214)
        self.draw_warning_sign(884, 405)
        self.draw_tree(63, 458, 0.55)
        self.draw_tree(912, 506, 0.52)
        self.draw_tree(845, 522, 0.44)

        self.draw_car(202, 604, CAR_COLORS["Verde"], 1.85, "TU")
        self.draw_car(790, 604, AI_COLOR, 1.85, "IA")

    def draw_menu_map(self):
        map_rect = pygame.Rect(204, 250, 592, 350)
        pygame.draw.rect(self.screen, (188, 150, 91), map_rect.move(0, 8), border_radius=34)
        pygame.draw.rect(self.screen, (238, 217, 171), map_rect, border_radius=34)
        pygame.draw.rect(self.screen, (214, 187, 136), map_rect, 4, border_radius=34)

        for x in range(245, 775, 58):
            pygame.draw.line(self.screen, (220, 194, 149), (x, 270), (x - 150, 590), 2)
            pygame.draw.line(self.screen, (220, 194, 149), (x - 80, 270), (x + 92, 590), 2)

        routes = [
            ([(258, 528), (350, 438), (445, 450), (542, 350), (728, 384)], BLUE),
            ([(270, 376), (380, 328), (492, 382), (604, 306), (736, 316)], GREEN),
            ([(290, 570), (390, 515), (516, 550), (610, 480), (742, 500)], PURPLE),
        ]
        for points, color in routes:
            pygame.draw.lines(self.screen, (170, 151, 118), False, points, 14)
            pygame.draw.lines(self.screen, color, False, points, 7)
            for point in points:
                pygame.draw.circle(self.screen, WHITE, point, 13)
                pygame.draw.circle(self.screen, color, point, 9)

    def draw_route_signpost(self, x, y):
        pygame.draw.rect(self.screen, (69, 73, 79), (x + 44, y + 32, 16, 230), border_radius=7)
        signs = [("A", BLUE), ("B", GREEN), ("C", PURPLE)]
        for index, (label, color) in enumerate(signs):
            top = y + index * 62
            sign = [(x, top), (x + 100, top), (x + 132, top + 28), (x + 100, top + 56), (x, top + 56), (x - 22, top + 28)]
            pygame.draw.polygon(self.screen, tuple(max(0, c - 42) for c in color), [(px, py + 5) for px, py in sign])
            pygame.draw.polygon(self.screen, color, sign)
            pygame.draw.lines(self.screen, WHITE, True, sign, 4)
            draw_text(self.screen, label, self.font_big, WHITE, (x + 54, top + 28), "center")

    def draw_traffic_light(self, x, y):
        pygame.draw.rect(self.screen, (54, 58, 64), (x + 31, y + 170, 14, 150), border_radius=7)
        pygame.draw.rect(self.screen, (41, 45, 50), (x, y, 76, 180), border_radius=26)
        pygame.draw.rect(self.screen, (91, 96, 103), (x, y, 76, 180), 5, border_radius=26)
        for index, color in enumerate([RED, YELLOW, GREEN]):
            cy = y + 38 + index * 52
            pygame.draw.circle(self.screen, tuple(max(0, c - 55) for c in color), (x + 38, cy + 3), 19)
            pygame.draw.circle(self.screen, color, (x + 38, cy), 17)
            pygame.draw.circle(self.screen, (255, 255, 255), (x + 31, cy - 7), 5)

    def draw_warning_sign(self, x, y):
        pole = pygame.Rect(x + 48, y + 80, 12, 112)
        pygame.draw.rect(self.screen, (76, 80, 86), pole, border_radius=5)
        triangle = [(x + 54, y), (x, y + 96), (x + 110, y + 96)]
        pygame.draw.polygon(self.screen, RED, triangle)
        pygame.draw.polygon(self.screen, WHITE, [(x + 54, y + 18), (x + 20, y + 84), (x + 90, y + 84)])
        pygame.draw.lines(self.screen, (142, 45, 45), True, triangle, 4)
        self.draw_car(x + 54, y + 66, INK, 0.45)

    def draw_menu_title(self):
        if self.logo_image:
            rect = self.logo_image.get_rect(center=(WIDTH // 2, 90))
            self.screen.blit(self.logo_image, rect)
            return

        for word, y, color in [("ROUTE", 82, (255, 218, 63)), ("WARS", 136, WHITE)]:
            for dx, dy in [(-5, 6), (5, 6), (-6, 0), (6, 0), (0, -5), (0, 7)]:
                draw_text(self.screen, word, self.font_logo, (13, 66, 137), (WIDTH // 2 + dx, y + dy), "center")
            draw_text(self.screen, word, self.font_logo, (5, 39, 92), (WIDTH // 2 + 3, y + 5), "center")
            draw_text(self.screen, word, self.font_logo, color, (WIDTH // 2, y), "center")

    def draw_main_menu(self, mouse_pos):
        self.draw_menu_background(self.screen)

        overlay = pygame.Surface((420, 544), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (18, 44, 74, 72), (0, 0, 420, 544), border_radius=26)
        pygame.draw.rect(overlay, (255, 255, 255, 74), (0, 0, 420, 544), 2, border_radius=26)
        self.screen.blit(overlay, (290, 24))

        self.draw_menu_title()

        subtitle_rect = pygame.Rect(326, 184, 348, 42)
        pygame.draw.rect(self.screen, (180, 126, 35), subtitle_rect.move(0, 5), border_radius=18)
        pygame.draw.rect(self.screen, (255, 214, 68), subtitle_rect, border_radius=18)
        pygame.draw.rect(self.screen, WHITE, subtitle_rect, 3, border_radius=18)
        draw_text(self.screen, "Cada decision crea trafico", self.font_body, INK, subtitle_rect.center, "center")

        self.add_button((330, 252, 340, 62), "PLAY", "play", GREEN, GREEN_DARK)
        self.add_button((330, 331, 340, 60), "Como jugar", "how", BLUE, BLUE_DARK)
        self.add_button((330, 408, 340, 60), "Teoria de Juegos", "theory", PURPLE, (88, 62, 137))
        self.add_button((330, 485, 340, 60), "Salir", "quit", RED, (162, 46, 48))

        for button in self.buttons:
            hover = button.rect.collidepoint(mouse_pos)
            draw_button(self.screen, button.rect, button.text, button.color, hover, self.menu_button_font, button.shadow)

    def draw_start(self, mouse_pos):
        self.draw_main_menu(mouse_pos)

    def draw_intro(self, mouse_pos):
        self.draw_world()
        self.draw_panel(pygame.Rect(110, 92, 780, 430), "Bienvenido a Route Wars")
        text = (
            "En este juego competiras contra una IA eligiendo rutas para llegar a la meta "
            "en el menor tiempo posible.\n\n"
            "Pero cuidado: si muchos autos eligen la misma ruta, aumenta la congestion y "
            "el tiempo de viaje.\n\n"
            "Cada ronda genera condiciones distintas, por lo que no existe una ruta siempre ganadora. "
            "Tu objetivo es tomar mejores decisiones que la IA durante 5 rondas.\n\n"
            "Sistema de puntos:\nVictoria = 3 pts\nEmpate = 1 pt\nDerrota = 0 pts"
        )
        draw_paragraph(self.screen, text, self.font_body, INK, 160, 152, 690, 25)
        self.add_button((390, 548, 220, 56), "CONTINUAR", "setup", GREEN, GREEN_DARK)
        self.draw_buttons(mouse_pos)

    def draw_setup(self, mouse_pos):
        self.draw_world()
        self.draw_panel(pygame.Rect(72, 70, 856, 500), "Seleccion de jugador")

        draw_text(self.screen, "Tipo de estrategia", self.font_mid, INK, (140, 130))
        styles = [
            ("Libre", "Libre"),
            ("Conservador", "Conservador"),
            ("Estrategico", "Estrategico"),
            ("Equilibrado", "Equilibrado"),
        ]
        y = 174
        for label, value in styles:
            selected = value == self.player_style
            color = GREEN if selected else BLUE
            shadow = GREEN_DARK if selected else BLUE_DARK
            self.add_button((130, y, 230, 48), label, "style:" + value, color, shadow)
            y += 60

        info = (
            "Libre: decides sin ayuda.\n"
            "Conservador: sugiere una ruta con pensamiento Maximin.\n"
            "Estrategico: sugiere una ruta con pensamiento Minimax.\n"
            "Equilibrado: sugiere una ruta con pensamiento Nash.\n\n"
            "Las recomendaciones no muestran tiempos ni garantizan una ruta segura."
        )
        draw_paragraph(self.screen, info, self.font_small, INK, 394, 166, 240, 20)

        draw_text(self.screen, "Color del auto", self.font_mid, INK, (680, 130))
        y = 178
        for name, color in CAR_COLORS.items():
            selected = name == self.player_color_name
            pygame.draw.circle(self.screen, color, (690, y + 24), 18)
            pygame.draw.circle(self.screen, INK if selected else WHITE, (690, y + 24), 21, 3)
            self.add_button((720, y, 125, 46), name, "color:" + name, color, tuple(max(0, c - 50) for c in color))
            y += 62

        self.draw_car(728, 465, self.player_color, 1.5, "TU")
        self.add_button((374, 590, 252, 48), "INICIAR PARTIDA", "start_match", GREEN, GREEN_DARK)
        self.draw_buttons(mouse_pos)

    def draw_round_header(self):
        pygame.draw.rect(self.screen, (255, 255, 255), (18, 18, 964, 58), border_radius=16)
        pygame.draw.rect(self.screen, (207, 221, 235), (18, 18, 964, 58), 3, border_radius=16)
        draw_text(self.screen, f"Ronda {self.round_number}/{TOTAL_ROUNDS}", self.font_mid, INK, (42, 47), "center")
        draw_text(self.screen, f"Tu: {self.player_score} pts", self.font_mid, GREEN_DARK, (440, 47), "center")
        draw_text(self.screen, f"IA: {self.ai_score} pts", self.font_mid, PURPLE, (575, 47), "center")
        draw_text(self.screen, "Victoria = 3 pts | Empate = 1 pt | Derrota = 0 pts", self.font_small, INK, (760, 48), "center")

    def draw_round(self, mouse_pos):
        self.draw_world()
        self.draw_roads()
        self.draw_round_header()

        for index, y in enumerate(ROUTE_Y):
            self.add_button((390, y - 31, 220, 56), ROUTE_NAMES[index], "route:" + str(index), ORANGE, ORANGE_DARK)

        if self.player_style != "Libre":
            self.draw_speech(self.message, 640, 104)
        else:
            self.draw_speech("Elige una ruta. La IA decidira despues.", 640, 104)

        self.add_button((806, 92, 130, 42), "Teoria", "theory", PURPLE, (88, 62, 137))
        draw_text(self.screen, "No se muestran tiempos ni pistas antes de elegir.", self.font_small, WHITE, (500, 610), "center")
        self.draw_buttons(mouse_pos)

    def draw_simulation(self, mouse_pos):
        self.draw_world()
        self.draw_roads()
        self.draw_round_header()
        elapsed = pygame.time.get_ticks() - self.sim_start
        progress = clamp(elapsed / self.sim_duration, 0, 1)

        for car in self.traffic_cars:
            self.draw_car(car["x"], car["road_y"] + car["offset"], car["color"], car["size"] / 56)

        player_finish = self.progress_from_time(self.current_player_time, progress)
        ai_finish = self.progress_from_time(self.current_ai_time, progress)
        px = 95 + player_finish * 805
        ax = 95 + ai_finish * 805
        py = ROUTE_Y[self.current_player_route] - 18
        ay = ROUTE_Y[self.current_ai_route] + 20
        self.draw_car(px, py, self.player_color, 1.05, "TU")
        self.draw_car(ax, ay, AI_COLOR, 1.0, "IA")

        congested = self.most_congested_route(self.current_conditions)
        self.draw_congestion_effect(congested)
        self.draw_speech(self.message, 650, 102)

    def progress_from_time(self, time_value, visual_progress):
        speed_factor = 1.18 - (time_value - 8.0) / 24.0
        eased = 1 - pow(1 - visual_progress, 2.0)
        return clamp(eased * speed_factor, 0, 1)

    def draw_congestion_effect(self, route_index):
        y = ROUTE_Y[route_index]
        for i in range(4):
            x = 330 + i * 45
            radius = 9 + int(5 * math.sin(pygame.time.get_ticks() / 300 + i))
            pygame.draw.circle(self.screen, (210, 210, 210), (x, y - 58 - i * 4), radius)
            pygame.draw.circle(self.screen, (160, 160, 160), (x + 7, y - 62 - i * 4), max(4, radius - 5))
        draw_text(self.screen, "TRAFICO", self.font_small, RED, (405, y - 84), "center")

    def most_congested_route(self, conditions):
        values = []
        for index in range(3):
            values.append(conditions["congestion"][index] + conditions["ambient"][index] * 0.4)
        return values.index(max(values))

    def draw_round_result(self, mouse_pos):
        self.draw_world()
        self.draw_panel(pygame.Rect(58, 82, 420, 490), "Resultado de la ronda")
        y = 145
        lines = [
            f"Tu elegiste: {ROUTE_NAMES[self.current_player_route]}",
            f"IA eligio: {ROUTE_NAMES[self.current_ai_route]}",
            f"Tiempo del jugador: {self.current_player_time:.1f} min",
            f"Tiempo de la IA: {self.current_ai_time:.1f} min",
            f"Ganador: {self.current_result}",
            f"Puntos: Tu +{self.current_points[0]} | IA +{self.current_points[1]}",
        ]
        for line in lines:
            draw_text(self.screen, line, self.font_body, INK, (92, y))
            y += 38
        draw_text(self.screen, f"Marcador: Tu {self.player_score} - IA {self.ai_score}", self.font_mid, BLUE_DARK, (92, y + 10))

        self.draw_matrix_panel(pygame.Rect(510, 82, 432, 490), self.current_matrix)

        label = "Ver final" if self.round_number >= TOTAL_ROUNDS else "Siguiente ronda"
        self.add_button((165, 590, 230, 48), label, "next_round", GREEN, GREEN_DARK)
        self.add_button((607, 590, 155, 48), "Teoria", "theory", PURPLE, (88, 62, 137))
        self.draw_buttons(mouse_pos)

    def draw_matrix_panel(self, rect, matrix):
        self.draw_panel(rect, "Matriz de pagos")
        draw_text(self.screen, "Primer valor = jugador | Segundo valor = IA", self.font_small, INK, (rect.centerx, rect.y + 62), "center")
        start_x = rect.x + 92
        start_y = rect.y + 125
        cell_w = 92
        cell_h = 58

        draw_text(self.screen, "IA", self.font_small, PURPLE, (rect.x + 54, start_y - 38), "center")
        for col in range(3):
            draw_text(self.screen, ROUTE_KEYS[col], self.font_mid, INK, (start_x + col * cell_w + cell_w // 2, start_y - 30), "center")
        for row in range(3):
            draw_text(self.screen, ROUTE_KEYS[row], self.font_mid, INK, (start_x - 36, start_y + row * cell_h + cell_h // 2), "center")
            for col in range(3):
                cell = pygame.Rect(start_x + col * cell_w, start_y + row * cell_h, cell_w - 6, cell_h - 6)
                pygame.draw.rect(self.screen, WHITE, cell, border_radius=8)
                pygame.draw.rect(self.screen, (198, 183, 143), cell, 2, border_radius=8)
                text = f"({matrix[row][col]['player_payoff']}, {matrix[row][col]['ai_payoff']})"
                draw_text(self.screen, text, self.font_small, INK, cell.center, "center")

        maximin = ROUTE_NAMES[self.maximin_route()]
        minimax = ROUTE_NAMES[self.minimax_route()]
        nash = self.nash_routes()
        if nash:
            nash_text = ", ".join(ROUTE_KEYS[p] + "/" + ROUTE_KEYS[a] for p, a in nash)
        else:
            nash_text = "No exacto"
        footer = f"Maximin: {maximin} | Minimax: {minimax} | Nash: {nash_text}"
        draw_paragraph(self.screen, footer, self.font_small, INK, rect.x + 36, rect.y + 350, rect.w - 72, 20)

    def draw_final(self, mouse_pos):
        self.draw_world()
        self.draw_roads()
        self.draw_panel(pygame.Rect(130, 92, 740, 410))
        draw_text(self.screen, "Resultado final", self.font_big, INK, (WIDTH // 2, 138), "center")
        if self.player_score > self.ai_score:
            self.draw_trophy(500, 265)
            message = "Campeon de Route Wars!"
        elif self.player_score < self.ai_score:
            self.draw_car(500, 260, AI_COLOR, 1.7, "IA")
            message = "La IA gano esta vez. La revancha esta servida!"
        else:
            self.draw_car(455, 260, self.player_color, 1.35, "TU")
            self.draw_car(545, 260, AI_COLOR, 1.35, "IA")
            message = "Empate estrategico. Nadie cedio terreno."
        draw_text(self.screen, message, self.font_mid, BLUE_DARK, (WIDTH // 2, 360), "center")
        draw_text(self.screen, f"Tu {self.player_score} pts  |  IA {self.ai_score} pts", self.font_big, INK, (WIDTH // 2, 420), "center")

        self.add_button((210, 548, 190, 52), "Jugar de nuevo", "restart", GREEN, GREEN_DARK)
        self.add_button((430, 548, 160, 52), "Ver reporte", "report", BLUE, BLUE_DARK)
        self.add_button((620, 548, 160, 52), "Salir", "quit", RED, (162, 46, 48))
        self.draw_buttons(mouse_pos)

    def draw_trophy(self, x, y):
        gold = (246, 190, 58)
        dark = (190, 126, 37)
        pygame.draw.rect(self.screen, dark, (x - 48, y + 52, 96, 18), border_radius=6)
        pygame.draw.rect(self.screen, dark, (x - 22, y + 5, 44, 60), border_radius=8)
        pygame.draw.rect(self.screen, gold, (x - 55, y - 55, 110, 72), border_radius=12)
        pygame.draw.rect(self.screen, dark, (x - 55, y - 55, 110, 72), 4, border_radius=12)
        pygame.draw.arc(self.screen, gold, (x - 100, y - 45, 58, 62), math.radians(90), math.radians(270), 10)
        pygame.draw.arc(self.screen, gold, (x + 42, y - 45, 58, 62), math.radians(-90), math.radians(90), 10)
        draw_text(self.screen, "1", self.font_big, WHITE, (x, y - 18), "center")

    def draw_report(self, mouse_pos):
        self.draw_world()
        self.draw_panel(pygame.Rect(24, 24, 952, 580))
        metrics = self.report_metrics()

        draw_text(self.screen, "Reporte final", self.font_big, INK, (58, 55))
        result_text, result_color = self.report_result_label(metrics["winner"])
        result_rect = pygame.Rect(690, 42, 245, 48)
        pygame.draw.rect(self.screen, tuple(max(0, c - 45) for c in result_color), result_rect.move(0, 5), border_radius=14)
        pygame.draw.rect(self.screen, result_color, result_rect, border_radius=14)
        pygame.draw.rect(self.screen, WHITE, result_rect, 3, border_radius=14)
        draw_text(self.screen, result_text, self.font_mid, WHITE, result_rect.center, "center")

        cards = [
            ("Puntaje", f"Tu {self.player_score} | IA {self.ai_score}", BLUE),
            ("Victorias", str(self.wins), GREEN),
            ("Empates", str(self.draws), BLUE),
            ("Derrotas", str(self.losses), RED),
            ("Ruta más elegida", metrics["player_route"], GREEN),
            ("Ruta IA", metrics["ai_route"], PURPLE),
            ("Mejor ruta promedio", metrics["best_route"], BLUE),
            ("Congestión alta", metrics["congestion_route"], ORANGE),
            ("Promedio jugador", f"{metrics['avg_player_time']:.1f} min", GREEN),
            ("Promedio IA", f"{metrics['avg_ai_time']:.1f} min", PURPLE),
            ("Maximin", metrics["maximin_route"], BLUE),
            ("Minimax", metrics["minimax_route"], PURPLE),
        ]
        for index, (title, value, color) in enumerate(cards):
            col = index % 4
            row = index // 4
            self.draw_report_card(pygame.Rect(50 + col * 226, 104 + row * 58, 204, 48), title, value, color)

        draw_text(self.screen, "Resumen por ronda", self.font_mid, INK, (58, 300))
        self.draw_rounds_table(50, 330)

        analysis_rect = pygame.Rect(50, 466, 900, 112)
        pygame.draw.rect(self.screen, (255, 255, 255), analysis_rect, border_radius=14)
        pygame.draw.rect(self.screen, (191, 207, 223), analysis_rect, 2, border_radius=14)
        draw_text(self.screen, "Análisis de Teoría de Juegos", self.font_small, BLUE_DARK, (70, 486))
        analysis = (
            "Durante la partida no existió una ruta siempre ganadora. Las mejores decisiones cambiaron "
            "según la congestión de cada ronda. Esto muestra que Route Wars funciona como un sistema "
            "estratégico, donde cada elección afecta el resultado final."
        )
        draw_paragraph(self.screen, analysis, self.font_tiny, INK, 70, 510, 850, 17)
        draw_text(self.screen, "Recomendación: " + self.report_recommendation(metrics), self.font_tiny, ORANGE_DARK, (70, 558))

        self.add_button((212, 608, 170, 38), "Jugar de nuevo", "restart", GREEN, GREEN_DARK)
        self.add_button((414, 608, 150, 38), "Volver", "back", BLUE, BLUE_DARK)
        self.add_button((596, 608, 140, 38), "Salir", "quit", RED, (162, 46, 48))
        self.draw_buttons(mouse_pos)

    def draw_report_card(self, rect, title, value, color):
        pygame.draw.rect(self.screen, tuple(max(0, c - 42) for c in color), rect.move(0, 4), border_radius=12)
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=12)
        pygame.draw.rect(self.screen, color, rect, 3, border_radius=12)
        draw_text(self.screen, title, self.font_tiny, (83, 91, 101), (rect.x + 12, rect.y + 9))
        draw_text(self.screen, value, self.font_small, color, (rect.x + 12, rect.y + 29))

    def draw_rounds_table(self, x, y):
        headers = ["Ronda", "Tú elegiste", "IA eligió", "Tiempo Tú", "Tiempo IA", "Resultado"]
        widths = [70, 155, 150, 125, 120, 165]
        table_width = sum(widths)
        row_h = 25
        pygame.draw.rect(self.screen, (226, 238, 249), (x, y, table_width, row_h), border_radius=8)
        current_x = x
        for header, width in zip(headers, widths):
            draw_text(self.screen, header, self.font_tiny, BLUE_DARK, (current_x + 8, y + 7))
            current_x += width

        for index, record in enumerate(self.round_history):
            row_y = y + row_h + index * row_h
            row_color = (255, 255, 255) if index % 2 == 0 else (244, 248, 252)
            pygame.draw.rect(self.screen, row_color, (x, row_y, table_width, row_h))
            values = [
                str(record["round"]),
                ROUTE_NAMES[record["player_route"]],
                ROUTE_NAMES[record["ai_route"]],
                f"{record['player_time']:.1f} min",
                f"{record['ai_time']:.1f} min",
                self.pretty_result(record["result"]),
            ]
            current_x = x
            for value, width in zip(values, widths):
                color = GREEN_DARK if value == "Ganó jugador" else PURPLE if value == "Ganó IA" else INK
                draw_text(self.screen, value, self.font_tiny, color, (current_x + 8, row_y + 7))
                current_x += width
        pygame.draw.rect(self.screen, (191, 207, 223), (x, y, table_width, row_h * (len(self.round_history) + 1)), 2, border_radius=8)

    def pretty_result(self, result):
        if result == "Gano el jugador":
            return "Ganó jugador"
        if result == "Gano la IA":
            return "Ganó IA"
        return "Empate"

    def report_result_label(self, winner):
        if winner == "Jugador":
            return "Ganó el jugador", GREEN
        if winner == "IA":
            return "Ganó la IA", PURPLE
        return "Empate general", BLUE

    def report_recommendation(self, metrics):
        if metrics["player_route"] == metrics["congestion_route"]:
            return "evita repetir siempre la ruta más congestionada; cambia de estrategia cuando se sature."
        return "evita elegir siempre la misma ruta y observa cómo cambia la congestión entre rondas."

    def report_metrics(self):
        player_counts = [0, 0, 0]
        ai_counts = [0, 0, 0]
        congestion_sum = [0, 0, 0]
        performance_sum = [0, 0, 0]
        maximin_counts = [0, 0, 0]
        minimax_counts = [0, 0, 0]
        nash_rounds = 0
        for record in self.round_history:
            player_counts[record["player_route"]] += 1
            ai_counts[record["ai_route"]] += 1
            maximin_counts[record["maximin"]] += 1
            minimax_counts[record["minimax"]] += 1
            if record["nash"]:
                nash_rounds += 1
            for route in range(3):
                conditions = record["conditions"]
                congestion_sum[route] += conditions["congestion"][route] + conditions["ambient"][route] * 0.4
                route_times = [record["matrix"][route][col]["player_time"] for col in range(3)]
                performance_sum[route] += sum(route_times) / len(route_times)

        rounds = max(1, len(self.round_history))
        avg_player = sum(record["player_time"] for record in self.round_history) / rounds
        avg_ai = sum(record["ai_time"] for record in self.round_history) / rounds
        winner = "Jugador" if self.player_score > self.ai_score else "IA" if self.ai_score > self.player_score else "Empate"
        dominant = self.detect_dominant_strategy()
        dominance_text = "No existio una estrategia dominante fija."
        if dominant is not None:
            dominance_text = "Aparecio una tendencia dominante hacia " + ROUTE_NAMES[dominant] + "."
        if nash_rounds:
            nash_text = f"{nash_rounds} ronda(s) presentaron equilibrio de Nash o comportamiento cercano."
        else:
            nash_text = "No se observo un equilibrio de Nash exacto."

        return {
            "winner": winner,
            "player_route": ROUTE_NAMES[player_counts.index(max(player_counts))],
            "ai_route": ROUTE_NAMES[ai_counts.index(max(ai_counts))],
            "congestion_route": ROUTE_NAMES[congestion_sum.index(max(congestion_sum))],
            "best_route": ROUTE_NAMES[performance_sum.index(min(performance_sum))],
            "avg_player_time": avg_player,
            "avg_ai_time": avg_ai,
            "maximin_route": ROUTE_NAMES[maximin_counts.index(max(maximin_counts))],
            "minimax_route": ROUTE_NAMES[minimax_counts.index(max(minimax_counts))],
            "dominance_text": dominance_text,
            "nash_text": nash_text,
        }

    def detect_dominant_strategy(self):
        if not self.round_history:
            return None
        dominant_counts = [0, 0, 0]
        for record in self.round_history:
            for route in range(3):
                is_best_all_columns = True
                for col in range(3):
                    payoff = record["matrix"][route][col]["player_payoff"]
                    best = max(record["matrix"][row][col]["player_payoff"] for row in range(3))
                    if payoff < best:
                        is_best_all_columns = False
                        break
                if is_best_all_columns:
                    dominant_counts[route] += 1
        best_count = max(dominant_counts)
        if best_count >= 4:
            return dominant_counts.index(best_count)
        return None

    def draw_how(self, mouse_pos):
        self.draw_world()
        self.draw_panel(pygame.Rect(105, 85, 790, 455), "Como jugar")
        text = (
            "1. Elige tu tipo de jugador y el color de tu auto.\n"
            "2. En cada ronda selecciona Ruta A, Ruta B o Ruta C.\n"
            "3. La IA elige su ruta despues de tu decision.\n"
            "4. Los autos avanzan hacia la meta y la congestion se ve en pantalla.\n"
            "5. Ganas la ronda si tu tiempo es menor que el de la IA.\n\n"
            "No hay una ruta siempre ganadora. Las condiciones cambian en cada ronda y "
            "la congestion puede convertir una buena idea en una decision costosa."
        )
        draw_paragraph(self.screen, text, self.font_body, INK, 160, 150, 675, 28)
        self.add_button((410, 565, 180, 50), "Volver", "back", BLUE, BLUE_DARK)
        self.draw_buttons(mouse_pos)

    def draw_theory(self, mouse_pos):
        self.draw_world()
        self.draw_panel(pygame.Rect(96, 74, 808, 500), "Teoria")
        text = (
            "Route Wars aplica Teoria de Juegos porque cada jugador toma decisiones "
            "estrategicas. La mejor ruta no depende solo de su distancia, sino tambien "
            "de cuantos autos la eligen. Por eso, las decisiones individuales afectan "
            "el resultado colectivo.\n\n"
            "Jugadores: usuario e IA.\n"
            "Estrategias: Ruta A, Ruta B y Ruta C.\n"
            "Pagos: 100 - tiempo.\n"
            "Matriz de pagos: muestra (pago jugador, pago IA) para cada combinacion.\n\n"
            "Maximin: elegir el mejor de los peores casos.\n"
            "Minimax: minimizar la mayor perdida posible.\n"
            "Equilibrio de Nash: situacion donde ningun jugador mejora cambiando solo de ruta."
        )
        draw_paragraph(self.screen, text, self.font_body, INK, 150, 140, 710, 25)
        self.add_button((410, 592, 180, 46), "Volver", "back", BLUE, BLUE_DARK)
        self.draw_buttons(mouse_pos)


def main():
    game = RouteWars()
    game.run()


if __name__ == "__main__":
    main()
