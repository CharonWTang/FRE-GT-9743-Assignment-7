import math
from enum import Enum
from typing import Optional, Dict
from scipy.stats import norm


class CallOrPut(Enum):

    CALL = "call"
    PUT = "put"
    INVALID = "invalid"

    @classmethod
    def from_string(cls, value: str) -> "CallOrPut":
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid token: {value}")

    def to_string(self) -> str:
        return self.value


class SimpleMetrics(Enum):

    ## valuations
    PV = "pv"
    ## vol
    IMPLIED_NORMAL_VOL = "implied_normal_vol"
    IMPLIED_LOG_NORMAL_VOL = "implied_log_normal_vol"
    ## pv sensitivities
    DELTA = "delta"
    GAMMA = "gamma"
    VEGA = "vega"
    TTE_RISK = "tte_risk"
    STRIKE_RISK = "strike_risk"
    STRIKE_RISK_2 = "strike_risk_2"
    THETA = "theta"

    ## vol sensitivities
    # nv = f(ln_vol, f, k, tte)
    D_N_VOL_D_LN_VOL = "d_n_vol_d_ln_vol"
    D_N_VOL_D_FORWARD = "d_n_vol_d_forward"
    D_N_VOL_D_TTE = "d_n_vol_d_tte"
    D_N_VOL_D_STRIKE = "d_n_vol_d_strike"
    # ln_vol = f^-1(nv, f, k, tte)
    D_LN_VOL_D_N_VOL = "d_ln_vol_d_n_vol"
    D_LN_VOL_D_FORWARD = "d_ln_vol_d_forward"
    D_LN_VOL_D_TTE = "d_ln_vol_d_tte"
    D_LN_VOL_D_STRIKE = "d_ln_vol_d_strike"

    @classmethod
    def from_string(cls, value: str) -> "SimpleMetrics":
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid token: {value}")

    def to_string(self) -> str:
        return self.value


class EuropeanOptionAnalytics:

    @staticmethod
    def european_option_log_normal(
        forward: float,
        strike: float,
        time_to_expiry: float,
        log_normal_sigma: float,
        option_type: Optional[CallOrPut] = CallOrPut.CALL,
        calc_risk: Optional[bool] = False,
    ) -> Dict[SimpleMetrics, float]:
        """
        Computes the Black-76 price and analytic Greeks of a European call or put option
        in the forward measure, using lognormal implied volatility.

        res should include
        - SimpleMetrics.PV: present value
        - SimpleMetrics.DELTA: delta
        - SimpleMetrics.GAMMA: gamma
        - SimpleMetrics.VEGA: vega
        - SimpleMetrics.THETA: theta
        - SimpleMetrics.TTE_RISK: time to expiry risk
        - SimpleMetrics.STRIKE_RISK: strike risk

        use calc_risk to control whether to compute the risk metrics or not
        """

        if time_to_expiry <= 0 or log_normal_sigma <= 0:
            raise ValueError("Time to expiry and implied log-normal sigma must be positive")

        res: Dict[SimpleMetrics, float] = {}

        # pricing
        # get d1, d2
        d1 = (math.log(forward / strike) + 0.5 * log_normal_sigma**2 * time_to_expiry) / (  log_normal_sigma * math.sqrt(time_to_expiry))
        d2 = d1 - log_normal_sigma * math.sqrt(time_to_expiry)  
        if option_type == CallOrPut.CALL:
            res[SimpleMetrics.PV] = norm.cdf(d1) * forward - norm.cdf(d2) * strike
            res[SimpleMetrics.DELTA] = norm.cdf(d1)
            # get gamma, vega, theta
            res[SimpleMetrics.GAMMA] = norm.pdf(d1) / (forward * log_normal_sigma * math.sqrt(time_to_expiry))
            res[SimpleMetrics.VEGA] = forward * norm.pdf(d1) * math.sqrt(time_to_expiry)
            res[SimpleMetrics.THETA] = - forward * norm.pdf(d1) * log_normal_sigma / (2 * math.sqrt(time_to_expiry))
        else:
            res[SimpleMetrics.PV] = norm.cdf(-d2) * strike - norm.cdf(-d1) * forward
            res[SimpleMetrics.DELTA] = norm.cdf(d1) - 1
            # get gamma, vega, theta
            res[SimpleMetrics.GAMMA] = norm.pdf(d1) / (forward * log_normal_sigma * math.sqrt(time_to_expiry))
            res[SimpleMetrics.VEGA] = forward * norm.pdf(d1) * math.sqrt(time_to_expiry)
            res[SimpleMetrics.THETA] = - forward * norm.pdf(d1) * log_normal_sigma / (2 * math.sqrt(time_to_expiry))   
        
        # risk
        # TTE_RISK is dPV/dT where T is time-to-expiry; THETA here is dPV/dt (calendar time), so dPV/dT = -THETA.
        res[SimpleMetrics.TTE_RISK] = - res[SimpleMetrics.THETA]
        # strike sensitivity dPV/dK under Black-76
        res[SimpleMetrics.STRIKE_RISK] = - norm.cdf(d2) if option_type == CallOrPut.CALL else norm.cdf(-d2)

        return res

    @staticmethod
    def european_option_normal(
        forward: float,
        strike: float,
        time_to_expiry: float,
        normal_sigma: float,
        option_type: Optional[CallOrPut] = CallOrPut.CALL,
        calc_risk: Optional[bool] = False,
    ) -> Dict[SimpleMetrics, float]:
        """
        Computes the Bachelier (normal) price and analytic Greeks of a European call or put option
        in the forward measure, using normal implied volatility.

        res should include
        - SimpleMetrics.PV: present value
        - SimpleMetrics.DELTA: delta
        - SimpleMetrics.GAMMA: gamma
        - SimpleMetrics.VEGA: vega
        - SimpleMetrics.THETA: theta
        - SimpleMetrics.TTE_RISK: time to expiry risk
        - SimpleMetrics.STRIKE_RISK: strike risk

        use calc_risk to control whether to compute the risk metrics or not
        """

        if time_to_expiry <= 0 or normal_sigma <= 0:
            raise ValueError("Time to expiry and implied normal sigma must be positive")

        res: Dict[SimpleMetrics, float] = {}

        # pricing
        d = (forward - strike) / (normal_sigma * math.sqrt(time_to_expiry))
        if option_type == CallOrPut.CALL:
            res[SimpleMetrics.PV] = (forward - strike) * norm.cdf(d) + normal_sigma * math.sqrt(time_to_expiry) * norm.pdf(d)
            res[SimpleMetrics.DELTA] = norm.cdf(d)
            # get gamma, vega, theta
            res[SimpleMetrics.GAMMA] = norm.pdf(d) / (normal_sigma * math.sqrt(time_to_expiry))
            res[SimpleMetrics.VEGA] = math.sqrt(time_to_expiry) * norm.pdf(d)
            res[SimpleMetrics.THETA] = - normal_sigma * norm.pdf(d) / (2 * math.sqrt(time_to_expiry))
            res[SimpleMetrics.STRIKE_RISK] = - norm.cdf(d)
        else:
            res[SimpleMetrics.PV] = (strike - forward) * norm.cdf(-d) + normal_sigma * math.sqrt(time_to_expiry) * norm.pdf(d)
            res[SimpleMetrics.DELTA] = norm.cdf(d) - 1
            # get gamma, vega, theta
            res[SimpleMetrics.GAMMA] = norm.pdf(d) / (normal_sigma * math.sqrt(time_to_expiry))
            res[SimpleMetrics.VEGA] = math.sqrt(time_to_expiry) * norm.pdf(d)
            res[SimpleMetrics.THETA] = - normal_sigma * norm.pdf(d) / (2 * math.sqrt(time_to_expiry))
            res[SimpleMetrics.STRIKE_RISK] = norm.cdf(-d)
        # risk
        # TTE_RISK is dPV/dT where T is time-to-expiry; THETA here is dPV/dt (calendar time), so dPV/dT = -THETA.
        res[SimpleMetrics.TTE_RISK] = - res[SimpleMetrics.THETA]
        # strike sensitivity 
        return res

    @staticmethod
    def implied_lognormal_vol_sensitivities(
        pv: float,
        forward: float,
        strike: float,
        time_to_expiry: float,
        option_type: Optional[CallOrPut] = CallOrPut.CALL,
        calc_risk: Optional[bool] = False,
        tol: Optional[float] = 1e-8,
    ) -> Dict[SimpleMetrics, float]:
        """
        Computes the implied lognormal volatility from option PV under the Black-76 model and its sensitivities.

        res should include
        - SimpleMetrics.IMPLIED_LOG_NORMAL_VOL: implied lognormal volatility
        - SimpleMetrics.D_LN_VOL_D_FORWARD: sensitivity of implied lognormal volatility to forward
        - SimpleMetrics.D_LN_VOL_D_TTE: sensitivity of implied lognormal volatility to time to expiry
        - SimpleMetrics.D_LN_VOL_D_STRIKE: sensitivity of implied lognormal volatility to strike

        use calc_risk to control whether to compute the risk metrics or not

        """
        res: Dict[SimpleMetrics, float] = {}

        # 1) compute implied vol

        # 2) compute greeks at implied vol

        # 3) compute sensitivities of implied vol using implicit function theorem
        # G(\sigma_imp(f, k, tte, pv), f, k, tte) = pv, where G is the pricing function
        # For instance, for f risk, we have
        # dG/dsigma * dsigma / df = - dG/df => - dG/df / dG/dsigma

        res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL] = EuropeanOptionAnalytics._implied_lognormal_vol_black(
            pv, forward, strike, time_to_expiry, option_type, tol)
        res[SimpleMetrics.D_LN_VOL_D_FORWARD] = - EuropeanOptionAnalytics.european_option_log_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL], option_type, calc_risk)[SimpleMetrics.DELTA] / EuropeanOptionAnalytics.european_option_log_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL], option_type, calc_risk)[SimpleMetrics.VEGA]

        res[SimpleMetrics.D_LN_VOL_D_TTE] = EuropeanOptionAnalytics.european_option_log_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.THETA] / EuropeanOptionAnalytics.european_option_log_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_LN_VOL_D_STRIKE] = - EuropeanOptionAnalytics.european_option_log_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.STRIKE_RISK] / EuropeanOptionAnalytics.european_option_log_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.VEGA]

        return res

    @staticmethod
    def implied_normal_vol_sensitivities(
        pv: float,
        forward: float,
        strike: float,
        time_to_expiry: float,
        option_type: Optional[CallOrPut] = CallOrPut.CALL,
        calc_risk: Optional[bool] = False,
        tol: Optional[float] = 1e-8,
    ) -> Dict[SimpleMetrics, float]:
        """
        Computes the implied normal volatility from option PV under the Bachelier model and,
        optionally, its sensitivities using the implicit function theorem.

        res should include
        - SimpleMetrics.IMPLIED_NORMAL_VOL: implied normal volatility
        - SimpleMetrics.D_N_VOL_D_FORWARD: sensitivity of implied normal volatility to forward
        - SimpleMetrics.D_N_VOL_D_TTE: sensitivity of implied normal volatility to time to expiry
        - SimpleMetrics.D_N_VOL_D_STRIKE: sensitivity of implied normal volatility to strike

        use calc_risk to control whether to compute the risk metrics or not
        """

        res = {}

        # 1) Compute implied normal vol

        # 2) Compute Greeks at implied vol

        # 3) Compute sensitivities of implied vol
        # G(\sigma_imp(f, k, tte), f, k, tte) = pv, where G is the pricing function
        # For instance, for f risk, we have
        # dG/dsigma * dsigma / df = - dG/df => - dG/df / dG/dsigma
        res[SimpleMetrics.IMPLIED_NORMAL_VOL] = EuropeanOptionAnalytics._implied_normal_vol_bachelier(
            pv, forward, strike, time_to_expiry, option_type, tol)
        res[SimpleMetrics.D_N_VOL_D_FORWARD] = - EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.DELTA] / EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_N_VOL_D_TTE] = EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.THETA] / EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_N_VOL_D_STRIKE] = - EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.STRIKE_RISK] / EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_NORMAL_VOL], option_type, calc_risk
        )[SimpleMetrics.VEGA]


        return res

    @staticmethod
    def lognormal_vol_to_normal_vol(
        forward: float,
        strike: float,
        time_to_expiry: float,
        log_normal_sigma: float,
        calc_risk: Optional[bool] = False,
        shift: Optional[float] = 0.0,
        tol: Optional[float] = 1e-8,
    ) -> Dict[SimpleMetrics, float]:
        """
        Converts lognormal implied volatility into normal (Bachelier) implied volatility
        via price equivalence, and compute sensitivities.

        res should include
        - SimpleMetrics.IMPLIED_NORMAL_VOL: equivalent normal implied volatility
        - SimpleMetrics.D_N_VOL_D_LN_VOL: sensitivity of normal vol to lognormal vol
        - SimpleMetrics.D_N_VOL_D_FORWARD: sensitivity of normal vol to forward
        - SimpleMetrics.D_N_VOL_D_STRIKE: sensitivity of normal vol to strike
        - SimpleMetrics.D_N_VOL_D_TTE: sensitivity of normal vol to time to expiry
        """

        res: Dict[SimpleMetrics, float] = {}

        f_shifted = forward + shift
        k_shifted = strike + shift
        if f_shifted <= 0 or k_shifted <= 0:
            raise ValueError("forward + shift and strike + shift must be positive")

        option_type = CallOrPut.PUT if forward > strike else CallOrPut.CALL

        # 1) black price (BS'76)
        # V = BS(f, k, tte, log_normal_sigma)

        # 2) implied normal vol (Bachelier)
        # nv = Imp(f, k, tte, V)
        # notice dnv/dV = 1 / vega
        V = EuropeanOptionAnalytics.european_option_log_normal(
            f_shifted, k_shifted, time_to_expiry, log_normal_sigma, option_type, calc_risk
        )[SimpleMetrics.PV]
        res[SimpleMetrics.IMPLIED_NORMAL_VOL] = EuropeanOptionAnalytics._implied_normal_vol_bachelier(
            V, forward, strike, time_to_expiry, option_type, tol)
        black = EuropeanOptionAnalytics.european_option_log_normal(
            f_shifted, k_shifted, time_to_expiry, log_normal_sigma, option_type, calc_risk
        )
        normal = EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, res[SimpleMetrics.IMPLIED_NORMAL_VOL], option_type, calc_risk
        )
        res[SimpleMetrics.D_N_VOL_D_LN_VOL] = black[SimpleMetrics.VEGA] / normal[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_N_VOL_D_FORWARD] = (
            black[SimpleMetrics.DELTA] - normal[SimpleMetrics.DELTA]
        ) / normal[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_N_VOL_D_TTE] = (
            black[SimpleMetrics.TTE_RISK] - normal[SimpleMetrics.TTE_RISK]
        ) / normal[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_N_VOL_D_STRIKE] = (
            black[SimpleMetrics.STRIKE_RISK] - normal[SimpleMetrics.STRIKE_RISK]
        ) / normal[SimpleMetrics.VEGA]
        

        return res

    @staticmethod
    def normal_vol_to_lognormal_vol(
        forward: float,
        strike: float,
        time_to_expiry: float,
        normal_sigma: float,
        calc_risk: Optional[bool] = False,
        shift: Optional[float] = 0.0,
        tol: Optional[float] = 1e-8,
    ) -> Dict[SimpleMetrics, float]:
        """
        Converts normal implied volatility into lognormal implied volatility
        via price equivalence, and computes sensitivities.

        res should include
        - SimpleMetrics.IMPLIED_LOG_NORMAL_VOL: equivalent lognormal implied volatility
        - SimpleMetrics.D_LN_VOL_D_N_VOL: sensitivity of lognormal vol to normal vol
        - SimpleMetrics.D_LN_VOL_D_FORWARD: sensitivity of lognormal vol to forward
        - SimpleMetrics.D_LN_VOL_D_STRIKE: sensitivity of lognormal vol to strike
        - SimpleMetrics.D_LN_VOL_D_TTE: sensitivity of lognormal vol to time to expiry
        """

        res: Dict[SimpleMetrics, float] = {}

        f_shifted = forward + shift
        k_shifted = strike + shift
        if f_shifted <= 0 or k_shifted <= 0:
            raise ValueError("forward + shift and strike + shift must be positive")

        option_type = CallOrPut.PUT if forward > strike else CallOrPut.CALL

        # 1) bachelier
        # V = Bachelier(f, k, tte, normal_sigma)

        # 2) implied log normal vol (BS'76)
        # ln_nv = Imp(f, k, tte, V)
        # notice dln_nv/dV = 1 / vega

        # risk
        V = EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, normal_sigma, option_type, calc_risk)
        res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL] = EuropeanOptionAnalytics._implied_lognormal_vol_black(
            V[SimpleMetrics.PV], f_shifted, k_shifted, time_to_expiry, option_type, tol)
        normal = EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, normal_sigma, option_type, calc_risk
        )
        black = EuropeanOptionAnalytics.european_option_log_normal(
            f_shifted,
            k_shifted,
            time_to_expiry,
            res[SimpleMetrics.IMPLIED_LOG_NORMAL_VOL],
            option_type,
            calc_risk,
        )
        res[SimpleMetrics.D_LN_VOL_D_N_VOL] = normal[SimpleMetrics.VEGA] / black[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_LN_VOL_D_FORWARD] = (
            normal[SimpleMetrics.DELTA] - black[SimpleMetrics.DELTA]
        ) / black[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_LN_VOL_D_TTE] = (
            normal[SimpleMetrics.TTE_RISK] - black[SimpleMetrics.TTE_RISK]
        ) / black[SimpleMetrics.VEGA]
        res[SimpleMetrics.D_LN_VOL_D_STRIKE] = (
            normal[SimpleMetrics.STRIKE_RISK] - black[SimpleMetrics.STRIKE_RISK]
        ) / black[SimpleMetrics.VEGA]

        return res

    ### utilities below

    @staticmethod
    def _implied_lognormal_vol_black(
        pv: float,
        forward: float,
        strike: float,
        time_to_expiry: float,
        option_type: Optional[CallOrPut] = CallOrPut.CALL,
        tol: Optional[float] = 1e-8,
        vol_min: Optional[float] = 1e-12,
        vol_max: Optional[float] = 10.0,
        max_iter: Optional[int] = 1000,
    ) -> float:
        """
        Solves for the Black-76 implied lognormal volatility from a European option price using a
        hybrid Newton-Raphson and bisection method, subject to arbitrage bounds and convergence
        controls.

        Return "sigma" implied lognormal volatility
        """
        if time_to_expiry <= 0:
            raise ValueError("time_to_expiry must be positive")
        if forward <= 0 or strike <= 0:
            raise ValueError("forward and strike must be positive for Black implied vol")

        intrinsic = max(forward - strike, 0.0) if option_type == CallOrPut.CALL else max(strike - forward, 0.0)
        upper_bound = forward if option_type == CallOrPut.CALL else strike
        if pv < intrinsic - tol or pv > upper_bound + tol:
            raise ValueError("Option PV is outside arbitrage bounds")

        lower = max(vol_min, 1e-12)
        upper = max(vol_max, lower * 2.0)

        low_res = EuropeanOptionAnalytics.european_option_log_normal(
            forward, strike, time_to_expiry, lower, option_type, calc_risk=True
        )
        if pv <= low_res[SimpleMetrics.PV] + tol:
            return lower

        high_res = EuropeanOptionAnalytics.european_option_log_normal(
            forward, strike, time_to_expiry, upper, option_type, calc_risk=True
        )
        while high_res[SimpleMetrics.PV] < pv and upper < 100.0:
            upper *= 2.0
            high_res = EuropeanOptionAnalytics.european_option_log_normal(
                forward, strike, time_to_expiry, upper, option_type, calc_risk=True
            )
        if high_res[SimpleMetrics.PV] < pv:
            raise ValueError("Could not bracket implied log-normal volatility")

        sigma = min(max(EuropeanOptionAnalytics._initial_log_normal_implied_vol_guess(forward, time_to_expiry, pv), lower), upper)
        for _ in range(max_iter):
            res = EuropeanOptionAnalytics.european_option_log_normal(
                forward, strike, time_to_expiry, sigma, option_type, calc_risk=True
            )
            price = res[SimpleMetrics.PV]
            vega = res[SimpleMetrics.VEGA]
            diff = price - pv

            if abs(diff) < tol:
                return sigma

            if diff > 0:
                upper = sigma
            else:
                lower = sigma

            if vega > tol:
                sigma_newton = sigma - diff / vega
            else:
                sigma_newton = 0.5 * (lower + upper)

            if sigma_newton <= lower or sigma_newton >= upper:
                sigma = 0.5 * (lower + upper)
            else:
                sigma = sigma_newton

        return sigma

    @staticmethod
    def _implied_normal_vol_bachelier(
        pv: float,
        forward: float,
        strike: float,
        time_to_expiry: float,
        option_type: Optional[CallOrPut] = CallOrPut.CALL,
        tol: Optional[float] = 1e-8,
        vol_min: Optional[float] = 1e-12,
        vol_max: Optional[float] = 0.1,
        max_iter: Optional[int] = 100,
    ) -> float:
        """
        Solves for the Bachelier implied normal volatility from a European option price using a
        hybrid Newton-Raphson and bisection method, subject to arbitrage bounds and convergence
        controls.

        Return "sigma" implied lognormal volatility
        """
        if time_to_expiry <= 0:
            raise ValueError("time_to_expiry must be positive")

        intrinsic = max(forward - strike, 0.0) if option_type == CallOrPut.CALL else max(strike - forward, 0.0)
        if pv < intrinsic - tol:
            raise ValueError("Option PV is outside arbitrage bounds")

        lower = max(vol_min, 1e-12)
        upper = max(vol_max, lower * 2.0)

        low_res = EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, lower, option_type, calc_risk=True
        )
        if pv <= low_res[SimpleMetrics.PV] + tol:
            return lower

        high_res = EuropeanOptionAnalytics.european_option_normal(
            forward, strike, time_to_expiry, upper, option_type, calc_risk=True
        )
        while high_res[SimpleMetrics.PV] < pv and upper < 1e4:
            upper *= 2.0
            high_res = EuropeanOptionAnalytics.european_option_normal(
                forward, strike, time_to_expiry, upper, option_type, calc_risk=True
            )
        if high_res[SimpleMetrics.PV] < pv:
            raise ValueError("Could not bracket implied normal volatility")

        sigma = min(max(EuropeanOptionAnalytics._initial_normal_implied_vol_guess(time_to_expiry, pv), lower), upper)
        for _ in range(max_iter):
            res = EuropeanOptionAnalytics.european_option_normal(
                forward, strike, time_to_expiry, sigma, option_type, calc_risk=True
            )
            price = res[SimpleMetrics.PV]
            vega = res[SimpleMetrics.VEGA]
            diff = price - pv

            if abs(diff) < tol:
                return sigma

            if diff > 0:
                upper = sigma
            else:
                lower = sigma

            if vega > tol:
                sigma_newton = sigma - diff / vega
            else:
                sigma_newton = 0.5 * (lower + upper)

            if sigma_newton <= lower or sigma_newton >= upper:
                sigma = 0.5 * (lower + upper)
            else:
                sigma = sigma_newton

        return sigma

    @staticmethod
    def _initial_log_normal_implied_vol_guess(forward: float, time_to_expiry: float, pv: float):
        return math.sqrt(2 * math.pi / time_to_expiry) * pv / forward

    @staticmethod
    def _initial_normal_implied_vol_guess(time_to_expiry: float, pv: float):
        return pv * math.sqrt(2 * math.pi / time_to_expiry)
