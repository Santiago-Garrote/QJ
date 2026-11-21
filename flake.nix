{
  description = "QuantumJam 2026: H4 VQE";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      lib = nixpkgs.lib;
      forAllSystems = lib.genAttrs [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      # requirements.txt is the single source of truth: [ { name; version|null; } ]
      parseReq = line:
        let parts = lib.splitString "==" line;
        in { name = builtins.head parts; version = if builtins.length parts == 2 then builtins.elemAt parts 1 else null; };
      requirementLines = builtins.filter (l: l != "" && !lib.hasPrefix "#" l)
        (map lib.trim (lib.splitString "\n" (builtins.readFile ./requirements.txt)));
      requirements = map parseReq requirementLines;

      # The notebook's `%pip install -q ...` line, as a list of requirement specs.
      notebook = builtins.fromJSON (builtins.readFile ./notebooks/h4_vqe.ipynb);
      pipLine = lib.findFirst (lib.hasPrefix "%pip install") (throw "notebook has no %pip install cell")
        (lib.concatMap (c: map lib.trim c.source) (builtins.filter (c: c.cell_type == "code") notebook.cells));
      notebookReqs = builtins.filter (t: t != "" && !lib.hasPrefix "-" t)
        (lib.drop 2 (lib.splitString " " pipLine));
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pinned = r: ps:
            let pkg = ps.${r.name}; in
            if r.version == null || pkg.version == r.version then pkg
            else throw "requirements.txt pins ${r.name}==${r.version} but nixpkgs has ${pkg.version}: update the pin (and the notebook)";
          python = pkgs.python3.withPackages (ps:
            map (r: pinned r ps) requirements ++ [ ps.jupyter ps.ipykernel ]);
        in
        {
          default = pkgs.mkShell { packages = [ python ]; };
        });

      checks = forAllSystems (system: {
        notebook-deps =
          assert lib.assertMsg (lib.sort lib.lessThan notebookReqs == lib.sort lib.lessThan requirementLines)
            "notebook %pip line [${toString notebookReqs}] != requirements.txt [${toString requirementLines}]";
          nixpkgs.legacyPackages.${system}.runCommand "notebook-deps" { } "touch $out";
      });
    };
}
