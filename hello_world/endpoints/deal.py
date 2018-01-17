import lime_webserver.webserver as webserver
import logging
import http.client
import webargs.fields as fields
from webargs.flaskparser import use_args
from ..endpoints import api


logger = logging.getLogger(__name__)

# This describes the schema for the payload when posting a new deal
# See https://webargs.readthedocs.io/en/latest/ for more info.
args = {
    "name": fields.String(required=True),
    "company": fields.Integer(required=True),
    "coworker": fields.Integer(required=True),
    "value": fields.Integer(missing=0),
    "probability": fields.Decimal(missing=0.0),
}


class Deal(webserver.LimeResource):
    """Resource for creating deals together with todos"""

    @use_args(args)
    def post(self, args):
        """Create a new deal, connect it to a company and a coworker
        and create a todo to follow up
        """
        uow = self.application.unit_of_work()

        deal = self.application.limetypes.deal()
        deal.properties.name.value = args.get('name')
        deal_idx = uow.add(deal)

        company = self.application.limetypes.company.get(args.get('company'))
        deal.properties.company.attach(company)
        uow.add(company)

        coworker = self.application.limetypes.coworker.get(
            args.get('coworker'))
        deal.properties.coworker.attach(coworker)
        uow.add(coworker)

        todo = self.application.limetypes.todo()
        todo.properties.note.value = 'Follow up {} with {}'.format(
            deal.properties.name.value, company.properties.name.value)
        todo.properties.deal.attach(deal)
        uow.add(todo)

        res = uow.commit()

        deal = res.get(deal_idx)

        return {'id': deal.id}, http.client.CREATED


api.add_resource(Deal,
                 '/deal/')
