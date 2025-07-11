from types import CoroutineType

from shortener.domain.shared.validator import ValidatorMap

from shortener.domain.user.validators import EmailAlreadyExistsValidator


class RegisterUserValidators(ValidatorMap):
    email_validators = [
        EmailAlreadyExistsValidator()
    ]

    async def validate(self, **items):
        email = items.get("email")
        name = items.get("name")
        pwd = items.get("password")

        validations: list[CoroutineType] = []

        validations.append(Em)

        email_validators = self.validators["email"]
        name_validators = self.validators["name"]
        pwd_validators = self.validators["password"]

        validations.extend([v.validate(email) for v in email_validators])
        validations.extend([v.validate(name) for v in name_validators])
        validations.extend([v.validate(password) for v in pwd_validators])
            
        return validations
        


validators={
    "email": [EmailAlreadyExistsValidator(repository=user_repository)],
    "password": [PasswordStrengthValidator()],
    "name": []
}
