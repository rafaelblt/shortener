from shortener.domain.services.password_hasher import PasswordHasherService
from shortener.domain.services.password_validator import PasswordValidatorService

from shortener.domain.plan import PlanRepository
from shortener.domain.plan.exceptions import PlanNotFoundInDatabaseError

from shortener.domain.user import User, UserRepository, UserValidator
from shortener.domain.user.fields import Email, Name, HashedPassword


class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        plan_repository: PlanRepository,
        password_hasher: PasswordHasherService,
        password_validator: PasswordValidatorService,
        user_validator: UserValidator
    ):
        """
        Args:
            user_repository (UserRepository): Repository to save the user.
            plan_repository (PlanRepository): Repository to get the User plan.
            password_hasher (PasswordHasherService): Hasher to hash the password.
            password_validator (PasswordValidatorService): Validator to validate 
                the password security.
            user_validator (UserValidator): Validator to validate the User object.
        """
        self.user_repository = user_repository
        self.plan_repository = plan_repository
        self.password_hasher = password_hasher
        self.password_validator = password_validator
        self.user_validator = user_validator

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
            PasswordValidationError: If the provided password is invalid.
            UserValidationError: If any part of the User is invalid.
        """
        plan = await self.plan_repository.get_by_id(plan_id)
        if plan is None:
            raise PlanNotFoundInDatabaseError(plan_id=plan_id)
        
        self.password_validator.validate(password)
        hashed_password = HashedPassword(self.password_hasher.hash(password))
        
        new_user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            plan=plan
        )
    
        await self.user_validator.validate(new_user)

        return await self.user_repository.add(new_user)
