from __future__ import annotations

from sinine_kapp.config import load_config
from sinine_kapp.data.database import initialize_database
from sinine_kapp.ui.main_window import MainWindow


def main() -> None:
    config = load_config()
    conn = initialize_database(config.database_path)
    app = MainWindow(config, conn)
    app.mainloop()


if __name__ == "__main__":
    main()
