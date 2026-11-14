"""Verificación temporal y numérica del contraste de carbono."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_hac

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/18_test_phytoplankton_carbon_connectivity.py"
spec = importlib.util.spec_from_file_location("carbon_connectivity", SCRIPT)
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


class CarbonConnectivityTests(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(431)
        self.dates = pd.date_range("1998-01-01", periods=336, freq="MS")

    def test_calendar_hac_matches_reference_and_preserves_gaps(self):
        x = np.c_[np.ones(336), self.rng.normal(size=336)]
        y = x @ np.array([1.0, 0.7]) + self.rng.normal(size=336)
        fit = sm.OLS(y, x).fit()
        actual = analysis.calendar_hac(x, fit.resid, self.dates, 12)
        np.testing.assert_allclose(actual, cov_hac(fit, nlags=12), rtol=1e-10, atol=1e-12)
        keep = np.arange(336) % 4 != 0
        dates, xx = self.dates[keep], x[keep]
        fit = sm.OLS(y[keep], xx).fit()
        actual = analysis.calendar_hac(xx, fit.resid, dates, 12)
        # Referencia independiente: sumar parejas por distancia real en meses.
        scores = xx * fit.resid[:, None]
        ordinals = dates.year.to_numpy() * 12 + dates.month.to_numpy()
        meat = scores.T @ scores
        for i in range(len(xx)):
            for j in range(i):
                lag = ordinals[i] - ordinals[j]
                if lag <= 12:
                    cross = np.outer(scores[i], scores[j])
                    meat += (1 - lag / 13) * (cross + cross.T)
        bread = np.linalg.inv(xx.T @ xx)
        expected = bread @ meat @ bread * len(xx) / (len(xx) - xx.shape[1])
        np.testing.assert_allclose(actual, expected, rtol=1e-10, atol=1e-12)

    def test_known_lag_and_unit_invariance(self):
        x = self.rng.normal(size=336)
        y = np.roll(x, 3) + 0.2 * self.rng.normal(size=336)
        data = pd.DataFrame({"peru_humboldt": y,
                             "peninsula_antarctica": x, "bellingshausen": x}, index=self.dates)
        enso = pd.Series(self.rng.normal(size=336), index=self.dates)
        frames = analysis.make_frames(data, enso, self.dates)
        fit = analysis.fit_contrast(frames["peninsula_antarctica", 3], 3, 12)
        self.assertEqual(fit["status"], "ok")
        self.assertGreater(fit["partial_r"], 0.9)
        self.assertLess(fit["p_hac"], 1e-8)
        changed = frames["peninsula_antarctica", 3].copy()
        changed[["x", "y"]] *= 12.0107
        converted = analysis.fit_contrast(changed, 3, 12)
        self.assertAlmostEqual(fit["partial_r"], converted["partial_r"], places=12)
        self.assertAlmostEqual(fit["p_hac"], converted["p_hac"], places=12)
        # Un hueco en el mes fuente invalida exactamente el mes destino correcto.
        data.loc["2010-06-01", "peninsula_antarctica"] = np.nan
        frames = analysis.make_frames(data, enso, self.dates)
        self.assertTrue(np.isnan(frames["peninsula_antarctica", 3].loc["2010-09-01", "x"]))
        self.assertAlmostEqual(frames["peninsula_antarctica", 3].loc["2010-10-01", "x"],
                               data.loc["2010-07-01", "peninsula_antarctica"])

    def test_constant_and_duplicate_data_fail_explicitly(self):
        frame = pd.DataFrame({"y": self.rng.normal(size=336), "x": 1.0,
                              "enso": self.rng.normal(size=336),
                              "enso_lag": self.rng.normal(size=336)}, index=self.dates)
        self.assertEqual(analysis.fit_contrast(frame, 3, 12)["status"], "not_estimable")
        with tempfile.TemporaryDirectory() as directory:
            panel = Path(directory) / "panel.csv"
            pd.DataFrame({"date": ["2000-01-01"] * 2,
                          "region": ["peru_humboldt"] * 2,
                          "depth_band": [analysis.BAND] * 2,
                          "phyc": [1, 2], "chl": [1, 2]}).to_csv(panel, index=False)
            with self.assertRaisesRegex(ValueError, "duplicados"):
                analysis.load_inputs(panel, Path(directory) / "unused.csv", 1998, 2025)

    def test_failed_contrasts_still_count_in_fdr_family(self):
        rows = [{"status": "ok", "p_hac": 0.01},
                {"status": "ok", "p_hac": 0.04}, {"status": "not_estimable"}]
        result = analysis.adjust_family(rows, "example")
        np.testing.assert_allclose(result.p_fdr.iloc[:2], [0.03, 0.06])
        self.assertTrue(np.isnan(result.p_fdr.iloc[2]))


if __name__ == "__main__":
    unittest.main()
