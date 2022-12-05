class EnvConfig:
    player_num = 100
    player_ids = list(range(player_num))
    total_step = 10000
    trade_radius = 4
    visual_radius = 7
    personae = [
        'pepper_bro',
        'coral_hunter',
        'sand_collector',
        'pineapple_farmer',
        'peanut_collector',
        'stone_picker',
        'pumpkin_farmer',
    ]
    bag_volume = 100
    
    @classmethod
    def persona_num(cls, persona: str):
        return EnvConfig.persona_avg_num(persona)
    
    @classmethod
    def persona_avg_num(cls, persona: str):
        avg_num = EnvConfig.player_num // len(EnvConfig.personae)
        remainder = EnvConfig.player_num % len(EnvConfig.personae)
        if persona == EnvConfig.personae[-1]:
            return avg_num + remainder
        else:
            return avg_num


class MapSize:
    width = 32
    height = 32


class PlayerConfig:
    max_health = 100
    comsumption_per_step = 1


class RewardConfig:
    threshold = 0
    weight_coef = 0.1
    penalty = 10
    rho = 0.5