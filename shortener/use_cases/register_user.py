import asyncio
from types import CoroutineType

from shortener.domain.shared.validator import Validator

from shortener.domain.services.password_hasher import PasswordHasherService

from shortener.domain.plan import PlanRepository
from shortener.domain.plan.exceptions import PlanNotFoundInDatabaseError

from shortener.domain.user import User, UserRepository
from shortener.domain.user.fields import Email, Name, HashedPassword, UserStatus


class CustomValidator(Validator):
    async def validate(self, value: object) -> None:
        return None


class RegisterUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        plan_repository: PlanRepository,
        password_hasher: PasswordHasherService,
        validators: dict[str, list[Validator]]
    ):
        """
        Args:
            user_repository (UserRepository): Repository to save the user.
            plan_repository (PlanRepository): Repository to get the User plan.
            password_hasher (PasswordHasherService): Hasher to hash the password.
        """
        self.user_repository = user_repository
        self.plan_repository = plan_repository
        self.password_hasher = password_hasher
        self.validators = validators

    async def execute(
        self,
        email: Email,
        name: Name,
        plan_id: int,
        password: str,
    ) -> User:
        """
        Executes the Use Case with the provided data.

        Args:
            email (Email): The email of user.
            name (Name): The name of user.
            plan_id (int): Plan ID of the user.
            password (str): Plain password of the user.
        
        Returns:
            User: The object created.
        
        Raises: 
            PlanNotFoundInDatabaseError: If the plan_id is not found in repository.
            ValidationError: If any of the data provided is invalid.
        """
        plan = await self.plan_repository.get_by_id(plan_id)
        if plan is None:
            raise PlanNotFoundInDatabaseError(plan_id=plan_id)
        
        validations: list[CoroutineType] = []

        for field, validators in self.validators.items():
            match field:
                case "email": 
                    validations.extend([v.validate(email) for v in validators])
                case "name": 
                    validations.extend([v.validate(name) for v in validators])
                case "password": 
                    validations.extend([v.validate(password) for v in validators])
        
        await asyncio.gather(*validations)

        hashed_password = HashedPassword(self.password_hasher.hash(password))

        new_user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            plan=plan,
            status=UserStatus.EMAIL_UNVERIFIED
        )

        return await self.user_repository.add(new_user)
