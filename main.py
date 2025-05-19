import math
import random
import csv
import logging

# Progress bar support
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None
    print("Warning: tqdm not installed, progress bar disabled. Install it with: pip install tqdm")

from protocol.packet_formatter import PacketFormatter, CommandCode

# Suppress INFO logs for a clean progress bar
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MAX_RADIUS = 500.0  # meters

class Submarine:
    """Maintains submarine state: x, y, z, heading."""
    def __init__(self, x=0.0, y=0.0, z=0.0, heading=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.heading = heading  # degrees: 0=east, +CCW

    def execute_command(self, cmd: CommandCode, param: int):
        if cmd == CommandCode.MOVE:
            rad = math.radians(self.heading)
            self.x += param * math.cos(rad)
            self.y += param * math.sin(rad)
        elif cmd == CommandCode.TURN:
            self.heading = (self.heading + param) % 360
        # STOP: no movement
        return (self.x, self.y, self.z)

    def distance_to_ship(self) -> float:
        return math.hypot(self.x, self.y)  # ignoring z for loss calc

def exp_loss(distance: float, decay: float = 300.0) -> float:
    return 1 - math.exp(-distance / decay)

def simulate_and_log(n_iters: int, output_path: str):
    sub = Submarine()
    segment_remaining = 0
    awaiting_stop = False

    fieldnames = [
        'iteration','type','isLost',
        'cmd_code','cmd_param','cmd_crc_valid',
        'status_code','depth_m','pressure',
        'pos_x','pos_y','pos_z','heading','status_crc_valid'
    ]

    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # configure tqdm with elapsed & remaining
        if tqdm:
            bar_format = '{l_bar}{bar}| {n_fmt}/{total_fmt} [Elapsed: {elapsed} | Remaining: {remaining}]'
            iterator = tqdm(range(1, n_iters+1),
                            desc="Simulating",
                            unit="it",
                            ncols=100,
                            bar_format=bar_format)
        else:
            iterator = range(1, n_iters+1)

        for i in iterator:
            # --- pick next realistic command ---
            if segment_remaining > 0:
                cmd = CommandCode.MOVE
                # proposed step
                if segment_remaining >= 10:
                    step = random.randint(10, min(100, int(segment_remaining)))
                else:
                    step = int(segment_remaining)

                # boundary check: solve for max p in sqrt((x+p cos)^2+(y+p sin)^2) <= MAX_RADIUS
                rad = math.radians(sub.heading)
                ux, uy = math.cos(rad), math.sin(rad)
                x0, y0 = sub.x, sub.y
                # quadratic: p^2 + 2*(x0*ux + y0*uy)*p + (x0^2+y0^2 - R^2) <=0
                b = 2*(x0*ux + y0*uy)
                c = x0*x0 + y0*y0 - MAX_RADIUS*MAX_RADIUS
                D = b*b - 4*c
                if D < 0:
                    # already outside or no real solution: force a turn
                    cmd = CommandCode.TURN
                    param = random.randint(-90, 90)
                    segment_remaining = 0
                    awaiting_stop = True
                else:
                    p_max = (-b + math.sqrt(D)) / 2
                    if p_max <= 0:
                        # cannot move further out: force a turn
                        cmd = CommandCode.TURN
                        param = random.randint(-90, 90)
                        segment_remaining = 0
                        awaiting_stop = True
                    else:
                        # cap step to p_max
                        param = min(step, int(p_max))
            elif awaiting_stop:
                cmd, param = CommandCode.STOP, 0
            else:
                cmd = CommandCode.TURN
                param = random.randint(-90, 90)

            # update segment planning
            if cmd == CommandCode.MOVE:
                segment_remaining -= param
            elif cmd == CommandCode.TURN:
                awaiting_stop = True
            else:  # STOP
                awaiting_stop = False
                segment_remaining = random.randint(200, 1000)

            # --- build & optionally parse command ---
            loss_cmd = random.random() < exp_loss(sub.distance_to_ship())
            raw_cmd = PacketFormatter.build_cmd_packet(cmd, param)
            info_cmd = PacketFormatter.parse_cmd_packet(raw_cmd) if not loss_cmd else {}

            writer.writerow({
                'iteration':     i,
                'type':          'Command',
                'isLost':        loss_cmd,
                'cmd_code':      info_cmd.get('command').name  if info_cmd else cmd.name,
                'cmd_param':     info_cmd.get('param')         if info_cmd else param,
                'cmd_crc_valid': info_cmd.get('crc_valid')     if info_cmd else False,
            })

            # apply the command state change
            if not loss_cmd and cmd != CommandCode.STOP:
                sub.execute_command(cmd, param)

            # --- build & optionally parse status (with heading) ---
            loss_stat = random.random() < exp_loss(sub.distance_to_ship())
            raw_stat = PacketFormatter.build_status_packet(
                status=0x00,
                depth=0,
                pressure=0,
                missing_cmd_seqs=[],
                x=int(sub.x), y=int(sub.y), z=int(sub.z),
                heading=int(sub.heading)
            )
            info_stat = PacketFormatter.parse_status_packet(raw_stat) if not loss_stat else {}

            writer.writerow({
                'iteration':         i,
                'type':              'Response',
                'isLost':            loss_stat,
                'status_code':       f"0x{info_stat.get('status',0):02X}" if info_stat else '',
                'depth_m':           info_stat.get('depth')    if info_stat else None,
                'pressure':          info_stat.get('pressure') if info_stat else None,
                'pos_x':             sub.x,
                'pos_y':             sub.y,
                'pos_z':             sub.z,
                'heading':           info_stat.get('heading') if info_stat else sub.heading,
                'status_crc_valid':  info_stat.get('crc_valid') if info_stat else False,
            })

            # blank row
            writer.writerow({})

if __name__ == "__main__":
    simulate_and_log(500_000, "uuv_packet_log.csv")