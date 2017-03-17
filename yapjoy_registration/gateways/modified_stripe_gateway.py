from billing import GatewayNotConfigured
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from billing.utils.credit_card import InvalidCard, Visa, MasterCard, \
     AmericanExpress, Discover, CreditCard
from billing.gateways.stripe_gateway import StripeGateway
import stripe
from django.conf import settings

class ModifiedStripeGateway(StripeGateway):
    def purchase(self, amount, credit_card, options=None):
        card = credit_card
        if isinstance(credit_card, CreditCard):
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")
            name = options.get("name", None)
            card = {
                'name': name,
                'number': credit_card.number,
                'exp_month': credit_card.month,
                'exp_year': credit_card.year,
                'cvc': credit_card.verification_value
                }
        try:
            description = options.get("description", None)
            response = self.stripe.Charge.create(
                amount=int(amount * 100),
                currency=self.default_currency.lower(),
                card=card, description=description)
        except self.stripe.CardError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="purchase",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}
