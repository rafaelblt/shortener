from shortener.domain.shorturl import ShortURL, ShortURLRepository


class GetShortURLUseCase:
    def __init__(self, repository: ShortURLRepository):
        self.repository = repository

    def get_by_id(self, id: int) -> ShortURL | None:
        return self.repository.get_by_id(id)
