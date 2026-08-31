# PELIN SÄÄNNÖT JA KUVAUS:
# Tavoite: Laukaise raketti tykillä ja saavuta kaikki 3 planeettaa (Mars, Saturnus, Neptunus) avaruudessa.
# Aloitus: Paina mitä tahansa näppäintä tai ohjaimen nappia introssa päästäksesi peliin.
# Ohjaimet:
#   - UP / W / SPACE / D-PAD UP / A-nappi = laukaise raketti / työntövoima
#   - LEFT/RIGHT / A/D / D-PAD LEFT/RIGHT = sivuttaisliike
#   - R / Y-nappi = aloita alusta / palaa Maahan
#   - 1/2/3 / B/X/Y-napit = osta päivityksiä
# Planeetat:
#   - Kuu (2 000m): Avaruuden raja
#   - Mars (6 000m): +300 kolikkoa
#   - Saturnus (30 000m): +1 000 kolikkoa
#   - Neptunus (60 000m): +3 000 kolikkoa -> Käynnistää laskeutumisen Neptunuksen pinnalle!

import random
import pyxel

UPGRADE_COSTS = [50, 150, 400, 1000, 2500]


class Rocket:

    def __init__(self, ground_y=110.0, fuel=100.0, thrust=0.12):
        self.x = 80.0
        self.ground_y = ground_y
        self.y = ground_y
        self.altitude = 0.0
        self.max_altitude = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.max_fuel = fuel
        self.fuel = fuel
        self.thrust = thrust
        self.state = "aiming"  # aiming, flying, landing_neptune, landed_neptune, stopped
        self.has_taken_off = False
        self.boost_timer = 0

    def apply_gravity(self, base_gravity=0.05):
        if self.vy >= 0:
            self.boost_timer = 0
            gravity = base_gravity * 22
        elif self.fuel <= 0:
            gravity = base_gravity * 6
        else:
            gravity = base_gravity

        self.vy += gravity

    def apply_thrust(self, up=False, left=False, right=False):
        if up and self.fuel > 0:
            self.vy -= self.thrust
            self.fuel -= 1.0

        if self.boost_timer > 0 and self.vy < 0:
            self.vy -= 0.15
            self.boost_timer -= 1
        elif self.vy >= 0:
            self.boost_timer = 0

        speed = 1.5
        if left:
            self.vx = -speed
        elif right:
            self.vx = speed
        else:
            self.vx = 0.0

        self.fuel = max(0.0, self.fuel)

    def move(self, min_y=40.0, min_x=6.0, max_x=154.0):
        self.x += self.vx
        self.altitude -= self.vy

        if self.altitude > self.max_altitude:
            self.max_altitude = self.altitude

        if self.altitude > 2.0:
            self.has_taken_off = True

        if self.altitude <= 0:
            self.altitude = 0.0
            if not self.has_taken_off:
                self.vy = min(0.0, self.vy)

        self.y = max(min_y, self.ground_y - self.altitude)

        if self.x < min_x:
            self.x = min_x
            self.vx = 0
        elif self.x > max_x:
            self.x = max_x
            self.vx = 0


class RocketGame:

    def __init__(
        self,
        ground_y=110,
        high_score=0,
        cannon_lvl=0,
        engine_lvl=0,
        fuel_lvl=0,
    ):
        fuel_amount = 100.0 + (fuel_lvl * 50.0)
        thrust_amount = 0.12 + (engine_lvl * 0.06)
        self.rocket = Rocket(
            ground_y=ground_y, fuel=fuel_amount, thrust=thrust_amount
        )
        self.ground_y = ground_y
        self.high_score = high_score
        self.cannon_lvl = cannon_lvl

        self.meter_x = 50.0
        self.meter_dir = 1
        self.meter_speed = 1.8

    @property
    def score(self):
        return int(self.rocket.max_altitude)

    def update_meter(self):
        self.meter_x += self.meter_speed * self.meter_dir
        if self.meter_x >= 110.0:
            self.meter_x = 110.0
            self.meter_dir = -1
        elif self.meter_x <= 50.0:
            self.meter_x = 50.0
            self.meter_dir = 1

    def launch_rocket(self):
        x = self.meter_x
        bonus = self.cannon_lvl * 1.5
        if 74 <= x <= 86:
            launch_speed = -(4.5 + bonus)
        elif (62 <= x < 74) or (86 < x <= 98):
            launch_speed = -(3.0 + bonus * 0.7)
        else:
            launch_speed = -(1.5 + bonus * 0.5)

        self.rocket.vy = launch_speed
        self.rocket.state = "flying"

    def step(self, thrust_up=False, thrust_left=False, thrust_right=False):
        if self.rocket.state == "aiming":
            self.update_meter()
            return

        if self.rocket.state != "flying":
            return

        self.rocket.apply_gravity()
        self.rocket.apply_thrust(
            up=thrust_up, left=thrust_left, right=thrust_right
        )
        self.rocket.move(min_y=40.0)

        if self.score > self.high_score:
            self.high_score = self.score

        if self.rocket.has_taken_off and self.rocket.altitude <= 0:
            self.rocket.state = "stopped"


class App:

    def __init__(self):
        self.show_intro = True
        self.high_score = 0
        self.total_coins = 0
        self.coins_from_score = 0

        self.cannon_lvl = 0
        self.engine_lvl = 0
        self.fuel_lvl = 0

        self.unlocked_planets = set()
        self.planet_distances = {
            "Mars": (6000, 300),
            "Saturnus": (30000, 1000),
            "Neptunus": (60000, 3000),
        }

        self.game = RocketGame(
            high_score=self.high_score,
            cannon_lvl=self.cannon_lvl,
            engine_lvl=self.engine_lvl,
            fuel_lvl=self.fuel_lvl,
        )

        rng = random.Random(42)
        self.clouds = [
            (
                rng.randint(5, 130),
                rng.randint(20, 750),
                rng.randint(14, 24),
                rng.randint(6, 10),
            )
            for _ in range(45)
        ]
        self.stars = [
            (
                rng.randint(2, 158),
                rng.randint(950, 64000),
                rng.choice([6, 7, 10]),
            )
            for _ in range(800)
        ]

        self.coins = self.generate_coins()
        self.boosters = self.generate_boosters()

        pyxel.init(160, 120, title="Rocket Ascent")
        pyxel.run(self.update, self.draw)

    def generate_coins(self):
        rng = random.Random()
        return [
            [rng.randint(15, 145), rng.randint(50, 62000), False]
            for _ in range(350)
        ]

    def generate_boosters(self):
        rng = random.Random()
        return [
            [rng.randint(20, 140), rng.randint(200, 60000), False]
            for _ in range(75)
        ]

    def get_background_color(self, alt):
        if alt < 700:
            return 12
        elif alt < 900:
            return 1
        elif alt < 1100:
            return 5
        else:
            return 0

    def buy_upgrade(self, upgrade_type):
        if upgrade_type == "cannon" and self.cannon_lvl < 5:
            cost = UPGRADE_COSTS[self.cannon_lvl]
            if self.total_coins >= cost:
                self.total_coins -= cost
                self.cannon_lvl += 1
        elif upgrade_type == "engine" and self.engine_lvl < 5:
            cost = UPGRADE_COSTS[self.engine_lvl]
            if self.total_coins >= cost:
                self.total_coins -= cost
                self.engine_lvl += 1
        elif upgrade_type == "fuel" and self.fuel_lvl < 5:
            cost = UPGRADE_COSTS[self.fuel_lvl]
            if self.total_coins >= cost:
                self.total_coins -= cost
                self.fuel_lvl += 1

        self.game = RocketGame(
            high_score=self.high_score,
            cannon_lvl=self.cannon_lvl,
            engine_lvl=self.engine_lvl,
            fuel_lvl=self.fuel_lvl,
        )

    def update(self):
        if self.show_intro:
            for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1):
                if pyxel.btnp(key):
                    self.show_intro = False
                    return

            gamepad_buttons = [
                pyxel.GAMEPAD1_BUTTON_A,
                pyxel.GAMEPAD1_BUTTON_B,
                pyxel.GAMEPAD1_BUTTON_X,
                pyxel.GAMEPAD1_BUTTON_Y,
                pyxel.GAMEPAD1_BUTTON_DPAD_UP,
                pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,
                pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
            ]
            for btn in gamepad_buttons:
                if pyxel.btnp(btn):
                    self.show_intro = False
                    return

            if (
                pyxel.btnp(pyxel.KEY_SPACE)
                or pyxel.btnp(pyxel.KEY_RETURN)
                or pyxel.btnp(pyxel.KEY_UP)
                or pyxel.btnp(pyxel.KEY_DOWN)
                or pyxel.btnp(pyxel.KEY_LEFT)
                or pyxel.btnp(pyxel.KEY_RIGHT)
                or pyxel.btnp(pyxel.KEY_1)
                or pyxel.btnp(pyxel.KEY_2)
                or pyxel.btnp(pyxel.KEY_3)
            ):
                self.show_intro = False
                return
            return

        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            self.high_score = max(self.high_score, self.game.high_score)
            self.game = RocketGame(
                high_score=self.high_score,
                cannon_lvl=self.cannon_lvl,
                engine_lvl=self.engine_lvl,
                fuel_lvl=self.fuel_lvl,
            )
            self.coins_from_score = 0
            self.coins = self.generate_coins()
            self.boosters = self.generate_boosters()
            return

        rocket = self.game.rocket

        if rocket.state in ["aiming", "stopped", "landed_neptune"]:
            if pyxel.btnp(pyxel.KEY_1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
                self.buy_upgrade("cannon")
            elif pyxel.btnp(pyxel.KEY_2) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.buy_upgrade("engine")
            elif pyxel.btnp(pyxel.KEY_3) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
                self.buy_upgrade("fuel")

        if rocket.state == "aiming":
            launch_pressed = (
                pyxel.btnp(pyxel.KEY_UP)
                or pyxel.btnp(pyxel.KEY_W)
                or pyxel.btnp(pyxel.KEY_SPACE)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
            )
            if launch_pressed:
                self.game.launch_rocket()
            else:
                self.game.step()
            return

        if rocket.state == "landing_neptune":
            speed = 1.5
            move_left = (
                pyxel.btn(pyxel.KEY_LEFT)
                or pyxel.btn(pyxel.KEY_A)
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
            )
            move_right = (
                pyxel.btn(pyxel.KEY_RIGHT)
                or pyxel.btn(pyxel.KEY_D)
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
            )
            if move_left:
                rocket.x = max(6.0, rocket.x - speed)
            elif move_right:
                rocket.x = min(154.0, rocket.x + speed)

            rocket.y += 0.6

            if rocket.y >= 110.0:
                rocket.y = 110.0
                rocket.state = "landed_neptune"
            return

        if rocket.state != "flying":
            return

        thrust_up = (
            pyxel.btn(pyxel.KEY_UP)
            or pyxel.btn(pyxel.KEY_W)
            or pyxel.btn(pyxel.KEY_SPACE)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)
        )
        thrust_left = (
            pyxel.btn(pyxel.KEY_LEFT)
            or pyxel.btn(pyxel.KEY_A)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
        )
        thrust_right = (
            pyxel.btn(pyxel.KEY_RIGHT)
            or pyxel.btn(pyxel.KEY_D)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        )

        self.game.step(
            thrust_up=thrust_up,
            thrust_left=thrust_left,
            thrust_right=thrust_right,
        )

        curr_alt = rocket.altitude
        for name, (dist, reward) in self.planet_distances.items():
            if curr_alt >= dist and name not in self.unlocked_planets:
                self.unlocked_planets.add(name)
                self.total_coins += reward

        if curr_alt >= 60000 and rocket.state == "flying":
            rocket.state = "landing_neptune"
            rocket.y = 20.0
            rocket.vy = 0
            rocket.vx = 0
            return

        current_score = self.game.score
        coins_due = current_score // 10
        if coins_due > self.coins_from_score:
            self.total_coins += coins_due - self.coins_from_score
            self.coins_from_score = coins_due

        item_scale = 0.25

        for coin in self.coins:
            cx, c_alt, collected = coin
            if not collected:
                cy = rocket.y - (c_alt - rocket.altitude) * item_scale
                if abs(rocket.x - cx) < 9 and abs(rocket.y - cy) < 9:
                    coin[2] = True
                    self.total_coins += 25

        if rocket.vy < 0 and rocket.boost_timer == 0:
            for booster in self.boosters:
                bx, b_alt, collected = booster
                if not collected:
                    by = rocket.y - (b_alt - rocket.altitude) * item_scale
                    if abs(rocket.x - bx) < 10 and abs(rocket.y - by) < 10:
                        booster[2] = True
                        rocket.boost_timer = 25
                        rocket.vy = min(rocket.vy - 2.0, -4.5)

        if self.game.high_score > self.high_score:
            self.high_score = self.game.high_score

    def draw_intro(self):
        pyxel.cls(0)

        # "LEHTISAARI STUDIOS PRESENTS:"
        pyxel.text(28, 16, "LEHTISAARI STUDIOS", 11)
        pyxel.text(48, 26, "PRESENTS:", 11)

        # Pelin raketti ja liekki introssa
        self.draw_rocket(80, 54)
        pyxel.tri(78, 58, 82, 58, 80, 64, 10)

        # "RAKETTIPELI"
        pyxel.text(58, 80, "RAKETTIPELI", 7)

        # Vilkkuva teksti
        if (pyxel.frame_count // 20) % 2 == 0:
            pyxel.text(26, 102, "PRESS ANY BUTTON TO CONTINUE", 6)

    def draw_rocket(self, x, y):
        pyxel.tri(x, y - 8, x - 3, y - 3, x + 3, y - 3, 8)
        pyxel.rect(x - 3, y - 3, 7, 7, 7)
        pyxel.rect(x - 1, y - 1, 3, 3, 6)
        pyxel.pset(x, y, 12)
        pyxel.tri(x - 3, y + 1, x - 6, y + 4, x - 3, y + 4, 8)
        pyxel.tri(x + 3, y + 1, x + 6, y + 4, x + 3, y + 4, 8)

    def draw_booster_icon(self, x, y):
        for offset_y in [-4, 0, 4]:
            pyxel.tri(
                x,
                y + offset_y - 2,
                x - 3,
                y + offset_y + 1,
                x + 3,
                y + offset_y + 1,
                11,
            )

    def draw_planets(self):
        rocket = self.game.rocket

        if rocket.altitude < 2000:
            moon_cy = 40 - (2000 - rocket.altitude) * 0.12
        else:
            moon_cy = max(20.0, 40.0 - (rocket.altitude - 2000) * 0.002)

        if -30 <= moon_cy <= 140:
            pyxel.circ(120, moon_cy, 10, 7)
            pyxel.circ(117, moon_cy - 2, 2, 6)
            pyxel.circ(122, moon_cy + 3, 3, 6)

        if rocket.altitude < 6000:
            mars_cy = 40 - (6000 - rocket.altitude) * 0.12
        else:
            mars_cy = max(30.0, 40.0 - (rocket.altitude - 6000) * 0.002)

        if -30 <= mars_cy <= 140:
            pyxel.circ(130, mars_cy, 12, 8)
            pyxel.circ(127, mars_cy - 3, 8, 9)

        if rocket.altitude < 30000:
            sat_cy = 40 - (30000 - rocket.altitude) * 0.12
        else:
            sat_cy = max(40.0, 40.0 - (rocket.altitude - 30000) * 0.002)

        if -30 <= sat_cy <= 140:
            pyxel.elli(12, sat_cy - 4, 48, 10, 10)
            pyxel.circ(36, sat_cy, 11, 15)
            pyxel.circ(36, sat_cy, 9, 10)

        if rocket.state not in ["landing_neptune", "landed_neptune"]:
            if rocket.altitude < 60000:
                nep_cy = 40 - (60000 - rocket.altitude) * 0.12
            else:
                nep_cy = max(35.0, 40.0 - (rocket.altitude - 60000) * 0.002)

            if -30 <= nep_cy <= 140:
                pyxel.circ(80, nep_cy, 15, 1)
                pyxel.circ(78, nep_cy - 2, 12, 12)
                pyxel.rect(70, nep_cy - 1, 18, 2, 7)

    def draw_neptune_ground(self):
        pyxel.rect(0, 112, 160, 8, 1)
        pyxel.rect(0, 110, 160, 2, 12)

        for x in range(0, 160, 16):
            pyxel.elli(x, 111, 12, 4, 6)
            pyxel.pset(x + 4, 111, 7)

        pyxel.line(0, 110, 160, 110, 6)
        pyxel.pset(20, 113, 7)
        pyxel.pset(80, 114, 7)
        pyxel.pset(140, 112, 7)

    def draw_cannon_meter(self):
        pyxel.rect(50, 95, 12, 4, 8)
        pyxel.rect(98, 95, 12, 4, 8)
        pyxel.rect(62, 95, 12, 4, 10)
        pyxel.rect(86, 95, 12, 4, 10)
        pyxel.rect(74, 95, 12, 4, 11)

        mx = int(self.game.meter_x)
        pyxel.tri(mx - 2, 89, mx + 2, 89, mx, 93, 7)

    def draw_upgrades_menu(self):
        c_cost = (
            f"{UPGRADE_COSTS[self.cannon_lvl]}c"
            if self.cannon_lvl < 5
            else "MAX"
        )
        e_cost = (
            f"{UPGRADE_COSTS[self.engine_lvl]}c"
            if self.engine_lvl < 5
            else "MAX"
        )
        f_cost = (
            f"{UPGRADE_COSTS[self.fuel_lvl]}c"
            if self.fuel_lvl < 5
            else "MAX"
        )

        pyxel.text(4, 26, f"[1/B]Cannon:{self.cannon_lvl}/5 ({c_cost})", 7)
        pyxel.text(4, 34, f"[2/X]Engine:{self.engine_lvl}/5 ({e_cost})", 7)
        pyxel.text(4, 42, f"[3/Y]Fuel:  {self.fuel_lvl}/5 ({f_cost})", 7)

    def draw(self):
        if self.show_intro:
            self.draw_intro()
            return

        rocket = self.game.rocket

        if rocket.state in ["landing_neptune", "landed_neptune"]:
            pyxel.cls(0)
            for sx, s_alt, color in self.stars[:300]:
                pyxel.pset(sx, (s_alt % 100) + 5, color)

            self.draw_neptune_ground()
            self.draw_rocket(rocket.x, rocket.y)

            if rocket.state == "landing_neptune":
                pyxel.text(42, 10, "LANDING ON NEPTUNE...", 10)
            elif rocket.state == "landed_neptune":
                pyxel.text(4, 4, f"High Score: {self.high_score}", 11)
                pyxel.circ(6, 16, 2, 10)
                pyxel.pset(6, 16, 9)
                pyxel.text(12, 14, str(self.total_coins), 10)

                pyxel.text(70, 14, "Planets Unlocked: (3/3)", 11)

                pyxel.text(50, 50, "NEPTUNE LANDED!", 10)
                pyxel.text(48, 60, "GAME COMPLETED!", 10)
                pyxel.text(34, 72, "Press R / Y to return Earth", 7)

                self.draw_upgrades_menu()
            return

        bg_color = self.get_background_color(rocket.altitude)
        pyxel.cls(bg_color)

        if rocket.state == "flying":
            for cx, c_alt, cw, ch in self.clouds:
                cy = rocket.y - (c_alt - rocket.altitude)
                if -15 <= cy <= 125 and rocket.altitude < 900:
                    pyxel.rect(cx, cy, cw, ch, 7)
                    pyxel.rect(cx + 2, cy - 2, cw - 4, ch + 4, 7)

        for sx, s_alt, color in self.stars:
            sy = rocket.y - (s_alt - rocket.altitude)
            if 0 <= sy <= 120 and rocket.altitude > 800:
                pyxel.pset(sx, sy, color)

        self.draw_planets()

        item_scale = 0.25

        if rocket.state == "flying":
            for cx, c_alt, collected in self.coins:
                if not collected:
                    cy = rocket.y - (c_alt - rocket.altitude) * item_scale
                    if -5 <= cy <= 125:
                        pyxel.circ(cx, cy, 2, 10)
                        pyxel.pset(cx, cy, 9)

        if rocket.vy < 0:
            for bx, b_alt, collected in self.boosters:
                if not collected:
                    by = rocket.y - (b_alt - rocket.altitude) * item_scale
                    if -10 <= by <= 130:
                        self.draw_booster_icon(bx, by)

        ground_screen_y = rocket.y + rocket.altitude
        if ground_screen_y <= 125:
            pyxel.rect(0, ground_screen_y + 4, 160, 20, 4)
            pyxel.rect(60, ground_screen_y + 2, 40, 2, 11)

        if rocket.state == "flying":
            thrust_up_active = (
                pyxel.btn(pyxel.KEY_UP)
                or pyxel.btn(pyxel.KEY_W)
                or pyxel.btn(pyxel.KEY_SPACE)
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)
            )
            if rocket.boost_timer > 0 and rocket.vy < 0:
                pyxel.tri(
                    rocket.x - 3,
                    rocket.y + 4,
                    rocket.x + 3,
                    rocket.y + 4,
                    rocket.x,
                    rocket.y + 13,
                    11,
                )
            elif thrust_up_active and rocket.fuel > 0:
                pyxel.tri(
                    rocket.x - 2,
                    rocket.y + 4,
                    rocket.x + 2,
                    rocket.y + 4,
                    rocket.x,
                    rocket.y + 9,
                    10,
                )

        self.draw_rocket(rocket.x, rocket.y)

        if rocket.state == "aiming":
            self.draw_cannon_meter()

        in_air = rocket.altitude > 0 and rocket.state == "flying"

        if in_air:
            pyxel.text(4, 4, f"Fuel: {int(rocket.fuel)}", 10)
            pyxel.text(4, 12, f"Score: {self.game.score}", 7)
            if rocket.boost_timer > 0 and rocket.vy < 0:
                pyxel.text(110, 4, "BOOST!", 11)
        else:
            pyxel.text(4, 4, f"High Score: {self.high_score}", 11)

            pyxel.circ(6, 16, 2, 10)
            pyxel.pset(6, 16, 9)
            pyxel.text(12, 14, str(self.total_coins), 10)

            unlocked_count = len(self.unlocked_planets)
            pyxel.text(70, 14, f"Planets Unlocked: ({unlocked_count}/3)", 11)

            self.draw_upgrades_menu()

            if rocket.state == "stopped":
                pyxel.text(40, 62, "Press R / Y to restart", 7)


if __name__ == "__main__":
    App()
