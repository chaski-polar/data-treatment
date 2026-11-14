"""Comprobaciones del diseño exploratorio y de su evaluación temporal."""
import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

path = Path(__file__).resolve().parents[1] / "scripts/19_investigate_ecosystem_relationships.py"
spec = importlib.util.spec_from_file_location("ecosystem_relationships", path)
analysis = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = analysis
spec.loader.exec_module(analysis)


class EcosystemRelationshipsTests(unittest.TestCase):
    def test_fixed_family_and_mixed_layer_coverage(self):
        data, _ = analysis.load_series()
        hypotheses = analysis.hypotheses()
        self.assertEqual(len(hypotheses), 33)
        self.assertEqual(len({h.id for h in hypotheses}), 33)
        for region in analysis.REGIONS:
            self.assertEqual(data[f"{region}:mlotst"].notna().sum(), 336)
        for h in hypotheses:
            self.assertIn(h.predictor, data)
            self.assertIn(h.response, data)
        for zone in ("paita", "chimbote"):
            self.assertEqual(data[f"modis:{zone}"].notna().sum(), 281)

    def test_pure_enso_association_is_removed_by_control(self):
        rng = np.random.default_rng(182)
        dates = pd.date_range("1998-01-01", periods=336, freq="MS")
        enso = rng.normal(size=336)
        frame = pd.DataFrame({"x": 2*enso + rng.normal(size=336),
                              "y": -3*enso + rng.normal(size=336),
                              "enso": enso, "enso_source": enso}, index=dates)
        h = analysis.Hypothesis("synthetic", "x", "y", 0, True, "test", "synthetic")
        result = analysis.fit(frame, h)
        self.assertEqual(result["status"], "ok")
        self.assertLess(abs(result["partial_r"]), .15)
        self.assertGreater(result["p_hac"], .05)
        h.control_enso = False
        self.assertLess(analysis.fit(frame, h)["partial_r"], -.7)

    def test_conditional_cv_uses_only_training_climatology(self):
        rng = np.random.default_rng(612)
        dates = pd.date_range("1998-01-01", periods=336, freq="MS")
        x = rng.normal(size=336)
        frame = pd.DataFrame({"x": x, "y": 2*x + .2*rng.normal(size=336),
                              "enso": rng.normal(size=336), "enso_source": rng.normal(size=336)}, index=dates)
        h = analysis.Hypothesis("synthetic", "x", "y", 0, False, "test", "synthetic")
        result = analysis.conditional_cv(frame, h)
        self.assertEqual(result["cv_n"], 168)
        self.assertGreater(result["cv_improvement_pct"], 70)
        # La relación de igual magnitud y signo opuesto en el futuro no debe
        # aprenderse antes de predecir el primer año de prueba.
        frame.loc["2012":, "y"] *= -1
        changed = analysis.conditional_cv(frame, h)
        self.assertLess(changed["cv_improvement_pct"], result["cv_improvement_pct"])


if __name__ == "__main__":
    unittest.main()
