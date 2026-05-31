import numpy as np

def compute_mu_sigma(api_forecast, P0):
    mus, variances = [], []
    for t, data in api_forecast.items():
        mean_P, lower, upper = data["mean"], data["lower"], data["upper"]
        if lower <= 0 or upper <= 0 or mean_P <= 0: continue
        sigma_t = (np.log(upper) - np.log(lower)) / (2 * 1.96)
        r_t     = np.log(mean_P) - np.log(P0)
        mus.append(r_t)
        variances.append(sigma_t ** 2)
    mu    = np.sum(mus)
    sigma = np.sqrt(np.sum(variances))
    return mu, sigma

def compute_shock(G, P, M, beta_G, beta_P, beta_M):
    return beta_G * G + beta_P * P + beta_M * M

def compute_r_star(mu, shock):
    return mu + shock

def compute_utility(r_star, sigma, lam=1.0):
    return r_star - (lam / 2) * sigma ** 2

def build_inputs(api_forecast, P0, G, P, M, beta_G, beta_P, beta_M, lam=1.0):
    mu, sigma = compute_mu_sigma(api_forecast, P0)
    shock     = compute_shock(G, P, M, beta_G, beta_P, beta_M)
    r_star    = compute_r_star(mu, shock)
    U         = compute_utility(r_star, sigma, lam)
    snr       = r_star / max(sigma, 1e-8)
    return {"mu": mu, "sigma": sigma, "shock": shock, "r_star": r_star, "utility": U, "snr": snr}

def apply_shock_to_forecast(p50_base, p10_base, p90_base, shock_log):
    factor  = np.exp(np.clip(shock_log, -3.0, 3.0))
    adj_p50 = [round(v * factor, 4) for v in p50_base]
    adj_p10 = [round(v * factor, 4) for v in p10_base]
    adj_p90 = [round(v * factor, 4) for v in p90_base]
    return adj_p50, adj_p10, adj_p90