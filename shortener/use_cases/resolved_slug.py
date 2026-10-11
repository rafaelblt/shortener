from dataclasses import dataclass

from shortener.domain import TargetURL


@dataclass(frozen=True)
class ResolvedSlug:
    target_url: str

    @classmethod
    def from_target_url(cls, target_url: TargetURL) -> "ResolvedSlug":
        return cls(target_url=str(target_url))
