import krpc
import time


def skip(t):
    start = current_time()
    time.sleep(1.5)
    while current_time() - start <= t:
        pass


def next_stage():
    vessel.control.activate_next_stage()


conn = krpc.connect(name="Autopilot")

ascent = conn.mech_jeb.ascent_autopilot
vessel = conn.space_center.active_vessel
maneuver = conn.mech_jeb.maneuver_planner
engines = vessel.parts.engines

start_mission = conn.add_stream(getattr, engines[5], "active")


conn.space_center.target_body = conn.space_center.bodies["Moon"]
ascent.autostage = False
ascent.desired_or_altitude = 176000
ascent.ascent_path_pvg.desired_apoapsis = 36500000
ascent.ascent_path_pvg.pitch_start_velocity = 200
time.sleep(1)
ascent.launch_to_target_plane()
ascent.enabled = True
time.sleep(1)


while start_mission() != True:
    pass
mission_start_time = conn.space_center.ut

current_time = conn.add_stream(getattr, conn.space_center, "ut")

# Выход на орбиту Земли с отделением ступеней согласно отделению ступеней в реальной миссии
skip(108)

next_stage()  # включение L110
skip(19)

next_stage()  # отделение S200
skip(68)

next_stage()  # отделение защиты носа
skip(124)

next_stage()

skip(2.5)
next_stage()

# Ускорение физического времени до выхода на первую орбиту
conn.space_center.physics_warp_factor = 3
while ascent.enabled != False:
    pass
conn.space_center.physics_warp_factor = 0

# Отделение l110 и включение c25
next_stage()
next_stage()

vessel.control.rcs = True

executor = conn.mech_jeb.node_executor

change_apoapsis = maneuver.operation_apoapsis

skip(7000)
