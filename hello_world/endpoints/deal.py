import http.client
import lime_config
import lime_webserver.webserver as webserver
import logging
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

        # Create a unit of work that will handle creating, updating, and
        # connecting objects within a database transaction.
        uow = self.application.unit_of_work()

        # Create a new limeobject of type 'deal' and give it the name
        # passed in the request.
        deal = self.application.limetypes.deal(name=args.get('name'))

        # Add the deal object to our unit of work so that it will be part
        # of the transaction later on.
        # We save the index the deal gets within the unit of work so that we
        # can retrieve the updated object later on.
        deal_idx = uow.add(deal)

        # Get the company from the id supplied in the request
        company = self.application.limetypes.company.get(args.get('company'))

        # Attach the company to the deal
        deal.properties.company.attach(company)

        # Add the company to our unit of work so that the relation between
        # our new deal and that company can be saved in the transaction later.
        uow.add(company)

        # I think you get it by now...
        coworker = self.application.limetypes.coworker.get(
            args.get('coworker'))
        deal.properties.coworker.attach(coworker)
        uow.add(coworker)

        todo = self.application.limetypes.todo()
        note = lime_config.config['plugins']['hello_world']['todo_note_text']
        todo.properties.note.value = note.format(deal=deal, company=company)
        todo.properties.deal.attach(deal)
        uow.add(todo)

        # Commit all the changes we've added to our unit of work
        res = uow.commit()

        # Retrieve the updated deal so we can get its ID.
        deal = res.get(deal_idx)

        # Send a custom event, notifying the world about this deal
        self.application.publish(identifier='hello-world.deal.created',
                                 message={
                                     'deal': {
                                         'id': deal.id,
                                         'name': deal.properties.name.value,
                                         'value': deal.properties.value.value
                                     },
                                     'company': {
                                         'id': company.id,
                                         'name': company.properties.name.value
                                     }
                                 })

        # Return a json response with the id of our new deal and a HTTP code
        # indicating that the objects were created successfully.
        return {'id': deal.id}, http.client.CREATED


api.add_resource(Deal,
                 '/deal/')
