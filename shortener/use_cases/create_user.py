from shortener.domain.services.password_hasher import PasswordHasher

from shortener.domain.plan import Plan, PlanRepository

from shortener.domain.user import User, UserRepository, UserValidator
from shortener.domain.user.fields import Email, Name, HashedPassword
from shortener.domain.user.exceptions import UserValidationError


class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        plan_repository: PlanRepository,
        password_hasher: PasswordHasher,
        validator: UserValidator
    ):
        """
        Args:
            user_repository (UserRepository): Repository to save the user.
            plan_repository (PlanRepository): Repository to get the User plan.
            password_hasher (PasswordHasher): PasswordHasher to hash the password.
            validator (UserValidator): Validator to validate the User object.
        """
        self.user_repository = user_repository
        self.plan_repository = plan_repository
        self.password_hasher = password_hasher
        self.validator = validator

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
            UserValidationError: If any part of the User is invalid.
        """
        plan = await self.plan_repository.get_by_id(plan_id)
        if plan is None:
            raise UserValidationError(
                "There is no user in the database with the given plan_id."
            )

        hashed_password = HashedPassword(self.password_hasher.hash(password))
        
        new_user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            plan=plan
        )
    
        await self.validator.validate(new_user)

        return await self.user_repository.add(new_user)
