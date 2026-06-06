import math
import random

import pygame


WIDTH = 1000
HEIGHT = 650
TITLE = "ROUTE WARS"
FPS = 60
TOTAL_ROUNDS = 5

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
        self.font_big = pygame.font.SysFont("arial", 38, bold=True)
        self.font_mid = pygame.font.SysFont("arial", 26, bold=True)
        self.font_body = pygame.font.SysFont("arial", 20)
        self.font_small = pygame.font.SysFont("arial", 16)
        self.font_tiny = pygame.font.SysFont("arial", 14)

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
        self.round_number = 0
        self.player_score = 0
        self.ai_score = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
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
        self.round_number += 1
        self.current_conditions = self.generate_conditions()
        self.current_matrix = self.build_payoff_matrix(self.current_conditions)
        self.current_player_route = None
        self.current_ai_route = None
        self.current_result = ""
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
                player_time = self.calculate_time(conditions, player_route, player_route, ai_route)
                ai_time = self.calculate_time(conditions, ai_route, player_route, ai_route)
                row.append(
                    {
                        "player_time": player_time,
                        "ai_time": ai_time,
                        "player_payoff": int(round(100 - player_time)),
                        "ai_payoff": int(round(100 - ai_time)),
                    }
                )
            matrix.append(row)
        return matrix

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
        self.resolve_points()
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

    def resolve_points(self):
        if abs(self.current_player_time - self.current_ai_time) <= 0.3:
            self.player_score += 1
            self.ai_score += 1
            self.draws += 1
            self.current_result = "Empate"
            self.current_points = (1, 1)
        elif self.current_player_time < self.current_ai_time:
            self.player_score += 3
            self.wins += 1
            self.current_result = "Gano el jugador"
            self.current_points = (3, 0)
        else:
            self.ai_score += 3
            self.losses += 1
            self.current_result = "Gano la IA"
            self.current_points = (0, 3)

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
        self.traffic_cars = []
        for route_index, y in enumerate(ROUTE_Y):
            count = self.current_conditions["ambient"][route_index]
            if route_index == self.current_player_route:
                count += 2
            if route_index == self.current_ai_route:
                count += 2
            for i in range(count):
                self.traffic_cars.append(
                    {
                        "route": route_index,
                        "x": random.randint(70, 850),
                        "offset": random.choice([-18, 18]),
                        "speed": random.uniform(35, 75) / (1 + self.current_conditions["congestion"][route_index] * 0.18),
                        "color": random.choice(TRAFFIC_COLORS),
                        "size": random.randint(22, 31),
                    }
                )

    def update(self, dt):
        if self.state == "simulation":
            for car in self.traffic_cars:
                car["x"] += car["speed"] * dt
                if car["x"] > 920:
                    car["x"] = random.randint(60, 130)
            elapsed = pygame.time.get_ticks() - self.sim_start
            if elapsed >= self.sim_duration:
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
        pygame.draw.rect(self.screen, (67, 154, 81), (880, 204, 92, 45), border_radius=9)
        draw_text(self.screen, "META", self.font_small, WHITE, (926, 226), "center")

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

    def draw_start(self, mouse_pos):
        self.draw_world()
        self.draw_roads()
        self.draw_car(260, ROUTE_Y[1] - 18, self.player_color, 1.15, "TU")
        self.draw_car(175, ROUTE_Y[0] - 18, AI_COLOR, 1.0, "IA")
        self.draw_speech("Cada decision crea trafico", 650, 205)

        draw_text(self.screen, "ROUTE WARS", self.font_title, WHITE, (WIDTH // 2 + 4, 104), "center")
        draw_text(self.screen, "ROUTE WARS", self.font_title, (255, 236, 92), (WIDTH // 2, 100), "center")
        draw_text(self.screen, "Cada decision crea trafico", self.font_mid, WHITE, (WIDTH // 2, 165), "center")

        self.add_button((390, 235, 220, 56), "PLAY", "play", GREEN, GREEN_DARK)
        self.add_button((360, 307, 280, 54), "Como jugar", "how", BLUE, BLUE_DARK)
        self.add_button((340, 377, 320, 54), "Teoria de Juegos", "theory", PURPLE, (88, 62, 137))
        self.add_button((390, 447, 220, 54), "Salir", "quit", RED, (162, 46, 48))
        self.draw_buttons(mouse_pos)

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
            self.draw_car(car["x"], ROUTE_Y[car["route"]] + car["offset"], car["color"], car["size"] / 56)

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
        self.draw_panel(pygame.Rect(30, 35, 940, 565), "Reporte final")

        metrics = self.report_metrics()
        left_x = 66
        y = 92
        draw_text(self.screen, "Resumen", self.font_mid, INK, (left_x, y))
        y += 38
        summary_lines = [
            f"Puntaje final: Tu {self.player_score} | IA {self.ai_score}",
            f"Ganador: {metrics['winner']}",
            f"Victorias: {self.wins}",
            f"Empates: {self.draws}",
            f"Derrotas: {self.losses}",
            f"Ruta mas elegida por ti: {metrics['player_route']}",
            f"Ruta mas elegida por IA: {metrics['ai_route']}",
            f"Mayor congestion promedio: {metrics['congestion_route']}",
            f"Mejor desempeno promedio: {metrics['best_route']}",
            f"Tiempo promedio jugador: {metrics['avg_player_time']:.1f} min",
            f"Tiempo promedio IA: {metrics['avg_ai_time']:.1f} min",
        ]
        for line in summary_lines:
            draw_text(self.screen, line, self.font_small, INK, (left_x, y))
            y += 22

        right_x = 525
        y = 92
        draw_text(self.screen, "Rondas", self.font_mid, INK, (right_x, y))
        y += 36
        for record in self.round_history:
            result = record["result"].replace("Gano", "gano")
            block = (
                f"Ronda {record['round']}: Tu -> {ROUTE_NAMES[record['player_route']]}, "
                f"{record['player_time']:.1f} min | IA -> {ROUTE_NAMES[record['ai_route']]}, "
                f"{record['ai_time']:.1f} min | Resultado: {result}"
            )
            y = draw_paragraph(self.screen, block, self.font_tiny, INK, right_x, y, 388, 17)
            y += 8

        analysis = (
            "Analisis de Teoria de Juegos: Los jugadores fueron el usuario y la IA. "
            "Las estrategias fueron Ruta A, Ruta B y Ruta C. El pago se calculo como 100 - tiempo. "
            "La matriz de pagos cambio en cada ronda por la congestion aleatoria. "
            f"{metrics['dominance_text']} Maximin recomendo con mas frecuencia {metrics['maximin_route']}. "
            f"Minimax recomendo con mas frecuencia {metrics['minimax_route']}. "
            f"{metrics['nash_text']} Durante la partida no existio una estrategia dominante fija, porque las "
            "condiciones de trafico cambiaron en cada ronda."
        )
        draw_text(self.screen, "Analisis de Teoria de Juegos", self.font_mid, INK, (66, 392))
        draw_paragraph(self.screen, analysis, self.font_small, INK, 66, 430, 850, 20)

        self.add_button((212, 608, 170, 38), "Jugar de nuevo", "restart", GREEN, GREEN_DARK)
        self.add_button((414, 608, 150, 38), "Volver", "back", BLUE, BLUE_DARK)
        self.add_button((596, 608, 140, 38), "Salir", "quit", RED, (162, 46, 48))
        self.draw_buttons(mouse_pos)

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
