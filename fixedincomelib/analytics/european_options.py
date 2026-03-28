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

        # risk

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

        # risk

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

        option_type = CallOrPut.PUT if forward > strike else CallOrPut.CALL

        # 1) black price (BS'76)
        # V = BS(f, k, tte, log_normal_sigma)

        # 2) implied normal vol (Bachelier)
        # nv = Imp(f, k, tte, V)
        # notice dnv/dV = 1 / vega

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

        option_type = CallOrPut.PUT if forward > strike else CallOrPut.CALL

        # 1) bachelier
        # V = Bachelier(f, k, tte, normal_sigma)

        # 2) implied log normal vol (BS'76)
        # ln_nv = Imp(f, k, tte, V)
        # notice dln_nv/dV = 1 / vega

        # risk

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
        vol_min: Optional[float] = 0.0,
        vol_max: Optional[float] = 10.0,
        max_iter: Optional[int] = 1000,
    ) -> float:
        """
        Solves for the Black-76 implied lognormal volatility from a European option price using a
        hybrid Newton-Raphson and bisection method, subject to arbitrage bounds and convergence
        controls.

        Return "sigma" implied lognormal volatility
        """

    @staticmethod
    def _implied_normal_vol_bachelier(
        pv: float,
        forward: float,
        strike: float,
        time_to_expiry: float,
        option_type: Optional[CallOrPut] = CallOrPut.CALL,
        tol: Optional[float] = 1e-8,
        vol_min: Optional[float] = 1e-8,
        vol_max: Optional[float] = 0.1,
        max_iter: Optional[int] = 100,
    ) -> float:
        """
        Solves for the Bachelier implied normal volatility from a European option price using a
        hybrid Newton-Raphson and bisection method, subject to arbitrage bounds and convergence
        controls.

        Return "sigma" implied lognormal volatility
        """

    @staticmethod
    def _initial_log_normal_implied_vol_guess(forward: float, time_to_expiry: float, pv: float):
        return math.sqrt(2 * math.pi / time_to_expiry) * pv / forward

    @staticmethod
    def _initial_normal_implied_vol_guess(time_to_expiry: float, pv: float):
        return pv * math.sqrt(2 * math.pi / time_to_expiry)
