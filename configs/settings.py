from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
# local only: if running in CI, you may skip loading .env by setting DOTENV=0
root = Path.cwd()
if os.getenv("DOTENV", "1") == "1":
    load_dotenv(root / ".env", override=False)


@dataclass(frozen=True)
class UrlConfig:
    """各產品的站台網址，來源 configs/env_{env}.yml。新增產品就在 yml 與這裡各加一個欄位。"""

    TRAVEL_BASE_URL: str


@dataclass(frozen=True)
class TravelAccount:
    """旅遊險帳號資料。個資（身分證、生日）放 .account_{env}.yml（gitignore）；密碼只從 env var 讀。"""

    PROPOSER_ID: str = ""
    PROPOSER_BIRTHDAY: str = ""  # 西元 YYYY/MM/DD
    MEMBER_ACCOUNT: str = ""
    MEMBER_PWD: str = field(default_factory=lambda: os.getenv("TRAVEL_MEMBER_PWD", ""), repr=False)

    @classmethod
    def from_dict(cls, cfg: dict) -> TravelAccount:
        proposer = cfg.get("proposer", {})
        member = cfg.get("member", {})
        return cls(
            PROPOSER_ID=proposer.get("id", ""),
            PROPOSER_BIRTHDAY=proposer.get("birthday", ""),
            MEMBER_ACCOUNT=member.get("account", ""),
        )


@dataclass(frozen=True)
class AccountConfig:
    TRAVEL: TravelAccount = field(default_factory=TravelAccount)

    @classmethod
    def from_yaml(cls, path: Path) -> AccountConfig:
        cfg: dict = {}
        if not path.exists():
            logger.warning("Account yaml not found: %s（範本見 %s.sample）", path, path.with_name(path.name.lstrip(".")))
        else:
            with path.open("r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        return cls(TRAVEL=TravelAccount.from_dict(cfg.get("travel", {})))


@dataclass(frozen=True)
class Settings:
    env: str
    urls: UrlConfig
    account: AccountConfig

    @property
    def is_prod(self) -> bool:
        return self.env.lower() == "prod"


def _load_yaml(env: str, base_dir: Path) -> dict:
    path = base_dir / "configs" / f"env_{env}.yml"
    if not path.exists():
        raise ValueError(f"Env yaml not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_settings(env: str, project_root: str | None = None) -> Settings:
    """
    Precedence:
      1) Real environment variables (CI secret injected)
      2) .env (local dev convenience)
      3) YAML for non-secret URLs / account data
    """
    base = Path(project_root) if project_root else Path.cwd()
    return Settings(
        env=env,
        urls=UrlConfig(**_load_yaml(env, base)),
        account=AccountConfig.from_yaml(base / "configs" / f".account_{env}.yml"),
    )
