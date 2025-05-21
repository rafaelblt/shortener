import pytest

from shortener.domain.services.password_validator import (
    PasswordValidatorService,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_SPECIAL_CHARS
)
from shortener.domain.services.exceptions import (
    PasswordTooShortError,
    PasswordTooLongError,
    PasswordMissingUppercaseError,
    PasswordMissingLowercaseError,
    PasswordMissingDigitError,
    PasswordMissingSpecialCharError
)


@pytest.fixture
def validator():
    return PasswordValidatorService()


def test_default_min_length(validator: PasswordValidatorService):
    assert validator.min_length == PASSWORD_MIN_LENGTH


def test_default_max_length(validator: PasswordValidatorService):
    assert validator.max_length == PASSWORD_MAX_LENGTH


def test_default_special_chars(validator: PasswordValidatorService):
    assert validator.special_chars == PASSWORD_SPECIAL_CHARS


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "password",
    [
        "P4ssw@rd",
        "G7v!p9#K",
        "mZ4^Qe!t39L&Yw",
        "X@8rTb%2KzL9vG#",
        "R@7vLp#9kS3!XmZtW2^yqEoBc+NjDdTfGp",
        "Mj!0eXz@3vPrLb#7N^cyGKW+HtFo24RdAmQY9suV",
        "Xf4^qG@K92Wtz#bMvNpE+LdUC3YohTFRj!7sXmLrwAyZ09&BkTJcevSnQglp*d8",
        "jMZrQx*V78yW@gc0PNf!doBL#5zUqKAXp2LvYehnm+TCsF4EtRbw39iJHl^Gk6ODfaXYc@q",
        "u$9WTXp3ZgKQv@JMdYAF2N+ct!HRozEnfL#7slX40Brmw^CUejOi5xLPdkgVbhqNaYRM*vwTz"
    ]
)
async def test_valid_passwords(validator: PasswordValidatorService, password: str):
    await validator.validate(password)


@pytest.mark.asyncio
async def test_raises_password_too_short(validator: PasswordValidatorService):
    invalid_password = "12aB@"
    with pytest.raises(PasswordTooShortError) as error:
        await validator.validate(invalid_password)
    assert error.value.value == invalid_password


@pytest.mark.asyncio
async def test_raises_password_too_long(validator: PasswordValidatorService):
    invalid_password = "Ab1@" * (PASSWORD_MAX_LENGTH)
    with pytest.raises(PasswordTooLongError) as error:
        await validator.validate(invalid_password)
    assert error.value.value == invalid_password


@pytest.mark.asyncio
async def test_raises_password_missing_uppercase(validator: PasswordValidatorService):
    invalid_password = "123!@#$invalid"
    with pytest.raises(PasswordMissingUppercaseError) as error:
        await validator.validate(invalid_password)
    assert error.value.value == invalid_password


@pytest.mark.asyncio
async def test_raises_password_missing_lowercase(validator: PasswordValidatorService):
    invalid_password = "123!@#$INVALID"
    with pytest.raises(PasswordMissingLowercaseError) as error:
        await validator.validate(invalid_password)
    assert error.value.value == invalid_password


@pytest.mark.asyncio
async def test_raises_password_missing_digit(validator: PasswordValidatorService):
    invalid_password = "!@#$InVaLiD"
    with pytest.raises(PasswordMissingDigitError) as error:
        await validator.validate(invalid_password)
    assert error.value.value == invalid_password


@pytest.mark.asyncio
async def test_raises_password_missing_special_char(validator: PasswordValidatorService):
    invalid_password = "1234565InVaLiD"
    with pytest.raises(PasswordMissingSpecialCharError) as error:
        await validator.validate(invalid_password)
    assert error.value.value == invalid_password
