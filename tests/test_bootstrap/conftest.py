from tests.fixtures.consumer import *
from tests.fixtures.domain import *

# Only what the tests of bootstrap use, since the uow of infra and the one of
# use_cases, a double, would have the same name.
from tests.fixtures.infra.database import database_url, empty_database_url, engine
from tests.fixtures.infra.silent_server import silent_server
from tests.fixtures.use_cases import *
