import pathlib


class EnvConfig:
    total_step = 1000
    trade_radius = 7
    visual_radius = 7
    num_person_type = 16
    personae = [
        *(['gold_digger'] * num_person_type),
        *(['hazelnut_farmer'] * num_person_type),
        *(['coral_collector'] * num_person_type),
        *(['sand_picker'] * num_person_type),
        *(['pineapple_farmer'] * num_person_type),
        *(['peanut_farmer'] * num_person_type),
        *(['stone_picker'] * num_person_type),
        *(['pumpkin_farmer'] * num_person_type),
    ]
    random_generate_map = False

    init_points = None

    use_move_solver = True


class MapConfig:
    width = 32
    height = 32

    generate_num_block_resource = 32


class PlayerConfig:
    bag_volume = 1000
    max_health = 100
    comsumption_per_step = 2


class RewardConfig:
    threshold = 0
    weight_coef = 0
    penalty = 0

    # d==for disposable, dur for durable; nec for necessity, lux for luxury
    alpha_nec, alpha_lux = 0.21, 0.21
    rho_nec, rho_lux = -0.21, -0.15
    eta_dis_nec, eta_dis_lux = 0.98, 1
    lambda_nec, lambda_lux = 200, 239
    eta_dur_nec, eta_dur_lux = 0.06, 0.08
    c_dis_nec, c_dis_lux, c_dur_nec, c_dur_lux = 0.41, 0.31, 100, 100


class DataPath:
    map_json = pathlib.Path(__file__).parent / "data" / "dense8.json"
