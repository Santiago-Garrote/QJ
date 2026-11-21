"""Repeat the #22 hardware point N times (separate back-to-back jobs) with the SAME ISA circuits and groups as the
reference run, plus N emulations with different seeds. Then average and test whether the hardware spread matches sigma.

    python scripts/ibm_hardware_repeat.py submit [N]   # needs results/ibm_hardware.json from `ibm_hardware.py submit/fetch`
    python scripts/ibm_hardware_repeat.py fetch        # waits for the jobs, writes results/ibm_repeats.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ibm_hardware as ih  # noqa: E402

REF = os.path.join(ROOT, "results", "ibm_hardware.json")
OUT = os.path.join(ROOT, "results", "ibm_repeats.json")


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as RuntimeSampler
    service = QiskitRuntimeService()
    ref = json.load(open(REF, encoding="utf-8"))
    groups = ih.groups_from_json(ref["groups"])
    if sys.argv[1] == "submit":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        isa = service.job(ref["job_id"]).inputs["pubs"]  # the exact circuits of the reference run
        circs = [p[0] for p in isa]
        backend = service.backend(ref["backend"])
        from qiskit_aer import AerSimulator
        from qiskit_aer.primitives import SamplerV2 as AerSampler
        nm = AerSimulator.from_backend(backend).options.noise_model
        emu = []
        for k in range(n + 1):
            res = AerSampler(seed=1000 + k, options={"backend_options": {"method": "density_matrix", "noise_model": nm}}).run(
                [(c, None, ih.SHOTS_PER_GROUP) for c in circs]).result()
            e, s = ih.energy_from_counts(groups, [ih.counts_of(r) for r in res])
            emu.append([e, s])
            print(f"emulated seed {k}: {(e - ref['e_fci']) * 1e3:+.1f} ± {s * 1e3:.1f} mHa", flush=True)
        jobs = [RuntimeSampler(mode=backend).run([(c, None, ih.SHOTS_PER_GROUP) for c in circs]).job_id() for _ in range(n)]
        print("JOBS", jobs, flush=True)
        json.dump(dict(reference_job=ref["job_id"], backend=ref["backend"], jobs=jobs, emulated=emu), open(OUT, "w"), indent=1)
        return
    data = json.load(open(OUT, encoding="utf-8"))
    hw = [[ref["energy"], ref["sigma"], ref["job_id"]]]
    for jid in data["jobs"]:
        res = service.job(jid).result()
        e, s = ih.energy_from_counts(groups, [ih.counts_of(r) for r in res])
        hw.append([e, s, jid])
        print(f"hardware {jid}: {(e - ref['e_fci']) * 1e3:+.1f} ± {s * 1e3:.1f} mHa", flush=True)
    def summary(rows):
        e, s = np.array([r[0] for r in rows]), np.array([r[1] for r in rows])
        w = 1 / s ** 2
        mean, err = float((w * e).sum() / w.sum()), float(w.sum() ** -0.5)
        chi2 = float((((e - mean) / s) ** 2).sum())
        return dict(mean=mean, sigma_mean=err, err_vs_fci_mHa=(mean - ref["e_fci"]) * 1e3, spread_mHa=float(e.std(ddof=1) * 1e3),
                    chi2=chi2, dof=len(e) - 1)
    data.update(hardware=hw, hw_summary=summary(hw), emu_summary=summary(data["emulated"]), e_fci=ref["e_fci"], e_hf=ref["e_hf"])
    json.dump(data, open(OUT, "w"), indent=1)
    for k in ("hw_summary", "emu_summary"):
        s = data[k]
        print(f"{k}: mean {s['err_vs_fci_mHa']:+.1f} ± {s['sigma_mean'] * 1e3:.1f} mHa | run-to-run spread {s['spread_mHa']:.1f} mHa | chi2 {s['chi2']:.1f}/{s['dof']}")


if __name__ == "__main__":
    main()
