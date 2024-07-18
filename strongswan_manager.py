class StrongSwan:
    def __init__(self, carol_conf_path, moon_conf_path):
        self.carol_conf_path = carol_conf_path
        self.moon_conf_path = moon_conf_path

    def _update_proposal(self, conf_path, proposals):
        with open(conf_path, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.strip().startswith("proposals ="):
                lines[i] = f"      proposals = {proposals}\n"
                break

        with open(conf_path, "w") as f:
            f.writelines(lines)

    def update_proposals(self, proposals):
        self._update_proposal(self.carol_conf_path, proposals)
        self._update_proposal(self.moon_conf_path, proposals)
