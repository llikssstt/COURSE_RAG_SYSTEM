from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import BGE_LOCAL_MODEL_DIR, DATA_DIR  # noqa: E402


def main() -> None:
    from modelscope.hub.api import ModelScopeConfig
    from modelscope import snapshot_download

    credential_dir = DATA_DIR / "modelscope_home" / "credentials"
    credential_dir.mkdir(parents=True, exist_ok=True)
    ModelScopeConfig.path_credential = str(credential_dir)

    path = snapshot_download(
        "BAAI/bge-small-zh-v1.5",
        local_dir=str(BGE_LOCAL_MODEL_DIR),
        max_workers=4,
    )
    print(f"BGE model downloaded to: {path}")


if __name__ == "__main__":
    main()
