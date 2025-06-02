import math
import random

def alpha_thorp(f_khz: float) -> float:
    """
    Compute absorption coefficient α(f) in dB per meter via Thorp's formula.
    """
    alpha_db_per_km = (
        0.11 * (f_khz ** 2) / (1 + f_khz ** 2)
        + 44 * (f_khz ** 2) / (4100 + f_khz ** 2)
        + 2.75e-4 * (f_khz ** 2)
        + 0.003
    )
    return alpha_db_per_km / 1000.0


def transmission_loss(d_m: float, f_khz: float, spreading_exp: float = 1.5, anomaly_db: float = 0.0) -> float:
    """
    Compute total transmission loss TL(d,f) in dB.
    """
    spreading_loss = 10.0 * spreading_exp * math.log10(d_m)
    alpha_db_per_m = alpha_thorp(f_khz)
    absorption_loss = alpha_db_per_m * d_m
    return spreading_loss + absorption_loss + anomaly_db


def linear_attenuation(TL_db: float) -> float:
    """
    Convert transmission loss in dB to a unitless power‐ratio factor.
    """
    return 10.0 ** (TL_db / 10.0)


def compute_gamma_mean(
    d_m: float,
    P0: float,
    N: float,
    f_khz: float,
    spreading_exp: float = 1.5,
    anomaly_db: float = 0.0
) -> float:
    """
    Compute large‐scale mean SNR at range d and frequency f.
    """
    gamma_0 = P0 / N
    TL_db = transmission_loss(d_m, f_khz, spreading_exp, anomaly_db)
    L_lin = linear_attenuation(TL_db)
    return gamma_0 / L_lin


def packet_loss_probability(
    d_m: float,
    P0: float,
    N: float,
    f_khz: float,
    gamma_req: float,
    spreading_exp: float = 1.5,
    anomaly_db: float = 0.0
) -> float:
    """
    Compute packet‐loss probability under Rayleigh fading.
    """
    gamma_mean = compute_gamma_mean(d_m, P0, N, f_khz, spreading_exp, anomaly_db)
    exponent = gamma_req / gamma_mean
    return 1.0 - math.exp(-exponent) 