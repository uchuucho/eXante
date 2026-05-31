import numpy as np
from utils import compute_mu_sigma, compute_shock, compute_r_star, compute_utility

ACTION_COLORS = {
    "Buy now": "var(--accent)", "Buy partial": "var(--accent)",
    "Hold": "var(--amber)",     "Wait": "var(--red)",
}

def make_decision(api_forecast, P0, G, P, M, beta, lam=1.0, snr_buy=0.3, snr_hold=0.0):
    mu, sigma = compute_mu_sigma(api_forecast, P0)
    shock     = compute_shock(G, P, M, beta.get("G",0), beta.get("P",0), beta.get("M",0))
    r_star    = compute_r_star(mu, shock)
    U         = compute_utility(r_star, sigma, lam)
    snr       = r_star / max(sigma, 1e-8)
    high_uncert = sigma > 0.4
    shock_intensity = (G + P + M) / 3

    if   snr >= snr_buy and not high_uncert: action, sub, base_pct = "Buy now",     "Full allocation",       88
    elif snr >= snr_buy and     high_uncert: action, sub, base_pct = "Buy partial", "Split across time",     65
    elif snr >= snr_hold:                    action, sub, base_pct = "Hold",        "Wait for better entry", 40
    else:                                    action, sub, base_pct = "Wait",        "Downtrend in progress", 20

    conviction = max(5, round(base_pct * (1 - shock_intensity * 0.4)))

    ret_pct   = round(mu * 100, 1)
    sigma_pct = round(sigma * 100, 1)
    shocks    = []
    if G > 0.05: shocks.append(f"geopolitical ({round(G*100)}%)")
    if P > 0.05: shocks.append(f"policy ({round(P*100)}%)")
    if M > 0.05: shocks.append(f"mining ({round(M*100)}%)")
    shock_str = f" Active shocks: {', '.join(shocks)}." if shocks else ""

    if   action == "Buy now":     desc = f"Expected log return {ret_pct}% with risk {sigma_pct}%. Strong signal.{shock_str}"
    elif action == "Buy partial": desc = f"Expected return {ret_pct}% but uncertainty is wide ({sigma_pct}%). Stagger purchases.{shock_str}"
    elif action == "Hold":        desc = f"Return signal is weak ({ret_pct}%). Hold and revisit in 4–6 weeks.{shock_str}"
    else:                         desc = f"Negative expected return ({ret_pct}%). Wait for a clearer floor.{shock_str}"

    return {"action": action, "sub": sub, "pct": conviction, "color": ACTION_COLORS[action], "desc": desc,
            "mu": round(mu,4), "sigma": round(sigma,4), "shock": round(shock,4),
            "r_star": round(r_star,4), "utility": round(U,4), "snr": round(snr,4)}