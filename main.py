from __future__ import annotations

import os


def _configure_qtwebengine_env() -> None:
    """QtWebEngine（地図表示に使用）のネットワーク関連の挙動を、importより前に設定する。

    QtWebEngineの内部Chromiumエンジンは初期化のタイミングが早く、モジュールを
    import した後に環境変数を設定しても反映されない。そのため、
    `from PyQt6.QtWidgets import QApplication` より前にここで設定する。

    - HTTPS_PROXY/HTTP_PROXY 等が設定されている場合、QtWebEngineのChromium
      エンジンにも明示的に伝える。QtWebEngineは通常のブラウザ(Chrome/Edgeなど)と
      異なり、環境変数のプロキシ設定を自動的には利用しないことがあるため、
      これを補う（「ブラウザでは地図タイルが見えるのにアプリでは真っ白」という
      症状の典型的な原因の一つ）。
    - 地図タイルが表示されないときのトラブルシューティング用に、Chromiumの
      リモートデバッグポートを有効化する。ローカルホストのみで待ち受け、
      外部には公開されない。ブラウザで http://127.0.0.1:<port> を開くと、
      地図パネル内部の通信状況（プロキシ/証明書/DNSエラー等の実際の理由）を
      Chrome DevToolsのNetworkタブで直接確認できる。
      MDLA_MAP_DEBUG_PORT=0 を設定すると無効化できる。
    """
    proxy = (
        os.environ.get("HTTPS_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("http_proxy")
    )
    if proxy and "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = f"--proxy-server={proxy}"

    debug_port = os.environ.get("MDLA_MAP_DEBUG_PORT", "9223")
    if debug_port != "0":
        os.environ.setdefault("QTWEBENGINE_REMOTE_DEBUGGING", debug_port)


_configure_qtwebengine_env()

import sys  # noqa: E402  (環境変数設定後でも問題ない標準ライブラリ)

from PyQt6.QtWidgets import QApplication  # noqa: E402  (環境変数設定後にimportする必要がある)

from app.gui.main_window import MainWindow  # noqa: E402


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
