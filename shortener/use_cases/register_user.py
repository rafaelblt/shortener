from shortener.domain.shared.validator import MultiFieldValidator, Validator
from shortener.domain.shared.language import Language

from shortener.domain.services.password_hasher import PasswordHasherService
from shortener.domain.services.auth_token import AuthTokenService
from shortener.domain.services.send_email import SendEmailService
from shortener.domain.services.email_template import EmailTemplate

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
        email_template: EmailTemplate,
        validators_map: dict[str, list[Validator]]
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
            validators_map (ValidatorsMap): Dictionary with validations list for 
                each field.
        """
        self.user_repository = user_repository
        self.plan_repository = plan_repository
        self.auth_token_service = auth_token_service
        self.send_email_service = send_email_service
        self.password_hasher = password_hasher
        self.email_template = email_template
        self.validators_map = validators_map

    async def execute(
        self,
        email: Email,
        name: Name,
        plan_id: int,
        password: str,
        lang: Language
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
            lang (Language): The language for translation.
        
        Returns:
            User: The object created.
        
        Raises: 
            PlanNotFoundError: If the plan_id is not found in repository.
            MultiValidationError: If any of the data provided is invalid.
        """
        multi_validator = MultiFieldValidator(self.validators_map)
        await multi_validator.validate(
            email=email, name=name, password=password, plan_id=plan_id
        )
        plan = await self._get_plan(plan_id)
        new_user = await self._create_user(email, name, password, plan)
        await self._send_verification_email(email, name, lang)

        return new_user

    async def _get_plan(self, plan_id: int) -> Plan:
        plan = await self.plan_repository.get_by_id(plan_id)
        if plan is None:
            raise PlanNotFoundError(plan_id=plan_id)
        return plan

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

    async def _send_verification_email(
        self, email: Email, name: Name, lang: Language
    ):
        token = self.auth_token_service.generate_token(email)
        context = {
            "user_name": name,
            "token": token,
            "expires_minutes": self.auth_token_service.expires_minutes
        }

        result = self.email_template.render(lang=lang, context=context)

        await self.send_email_service.send_email(
            to=email,
            subject=result["subject"],
            plain_body=result["plain_body"],
            html_body=result["html_body"]
        )
