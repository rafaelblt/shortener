from typing import Annotated

from shortener.adapters.api.v1.interfaces.uow import UnitOfWork

from shortener.infra.dependencies import fastapi_deps


UnitOfWorkDependency = Annotated[UnitOfWork, fastapi_deps.unit_of_work]
