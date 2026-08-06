def validate_credit_card(card_number: str) -> bool:
    """
    Validate a credit card number using the Luhn algorithm.

    Rules:
    - The card number may contain spaces or hyphens.
    - After removing separators, it must contain only digits.
    - Length must be between 13 and 19 digits.
    """

    # Remove common separators
    card_number = card_number.replace(" ", "").replace("-", "")

    # Validate format
    if not card_number.isdigit():
        return False

    if not 13 <= len(card_number) <= 19:
        return False

    total = 0
    reverse_digits = card_number[::-1]

    for index, digit in enumerate(reverse_digits):
        value = int(digit)

        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9

        total += value

    return total % 10 == 0