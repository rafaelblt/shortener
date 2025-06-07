import asyncio

from types import CoroutineType

from shortener.domain.shared.validator import Validator

from shortener.domain.services.password_hasher import PasswordHasherService
from shortener.domain.services.auth_token import AuthTokenService
from shortener.domain.services.send_email import SendEmailService
from shortener.domain.services.email_template_renderer import EmailTemplateRenderer

from shortener.domain.plan import Plan, PlanRepository
from shortener.domain.plan.exceptions import PlanNotFoundError

from shortener.domain.user import User, UserRepository
from shortener.domain.user.fields import Email, Name, HashedPassword, UserStatus


class RegisterUserUseCase:
    """Use case for registering a new user in the system."""

    def __init__(
        self,
        user_repository: UserRepository,
        plan_repository: PlanRepository,
        auth_token_service: AuthTokenService,
        send_email_service: SendEmailService,
        password_hasher: PasswordHasherService,
        email_template_renderer: EmailTemplateRenderer,
        validators: dict[str, list[Validator]]
    ):
        """
        Args:
            user_repository (UserRepository): Repository to save the user.
            plan_repository (PlanRepository): Repository to get the user plan.
            auth_token_service (AuthTokenService): Service to generate the 
                verification token.
            send_email_service (SendEmailService): Service to send the 
                verification email.
            password_hasher (PasswordHasherService): Service to hash the password.
            validators (dict[str, list[Validator]]): Dictionary with validations
                list for each field.
        
        Examples:
            ```
            validations = {
                "email": [ValidatorX, ValidatorY],
                "name": [ValidatorZ],
                "password": []
            }
            ```
        """
        self.user_repository = user_repository
        self.plan_repository = plan_repository
        self.auth_token_service = auth_token_service
        self.send_email_service = send_email_service
        self.password_hasher = password_hasher
        self.email_template = email_template_renderer
        self.validators = validators

    async def execute(
        self,
        email: Email,
        name: Name,
        plan_id: int,
        password: str,
    ) -> User:
        """
        It performs the validations, creates the user, saves with the 
        UNVERIFIED_EMAIL status and sends the verification token to the email 
        address provided.

        Args:
            email (Email): The email of user.
            name (Name): The name of user.
            plan_id (int): Plan ID of the user.
            password (str): Plain password of the user.
        
        Returns:
            User: The object created.
        
        Raises: 
            PlanNotFoundError: If the plan_id is not found in repository.
            ValidationError: If any of the data provided is invalid.
        """
        validations_coro = self._get_validations_coro(
            email=email, name=name, password=password
        )
        results = await asyncio.gather(self._get_plan(plan_id), *validations_coro)

        plan = results[0]
        new_user = await self._create_user(email, name, password, plan)
        await self._send_verification_email(email, name)

        return new_user

    async def _get_plan(self, plan_id: int) -> Plan:
        plan = await self.plan_repository.get_by_id(plan_id)
        if plan is None:
            raise PlanNotFoundError(plan_id=plan_id)
        return plan

    def _get_validations_coro(self, email: Email, name: Name, password: str):
        validations: list[CoroutineType] = []

        for field, validators in self.validators.items():
            match field:
                case "email": 
                    validations.extend([v.validate(email) for v in validators])
                case "name": 
                    validations.extend([v.validate(name) for v in validators])
                case "password": 
                    validations.extend([v.validate(password) for v in validators])
            
        return validations

    async def _create_user(
        self, email: Email, name: Name, password: str, plan: Plan
    ) -> User:
        hashed_password = HashedPassword(self.password_hasher.hash(password))
        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            plan=plan,
            status=UserStatus.UNVERIFIED_EMAIL
        )
        return await self.user_repository.add(user)

    async def _send_verification_email(self, email: Email, name: Name):
        token = self.auth_token_service.generate_token(email)
        template_data = {
            "name": name,
            "token": token,
            "expires_minutes": self.auth_token_service.expires_minutes
        }

        subject = self.email_template.render_subject()
        plain_body = self.email_template.render_plain_body(**template_data)
        html_body = self.email_template.render_html_body(**template_data)

        await self.send_email_service.send_email(
            to=email, subject=subject, plain_body=plain_body, html_body=html_body
        )
