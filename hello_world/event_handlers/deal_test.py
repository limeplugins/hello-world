import lime_test.core_db.dsl as dsl
import lime_test.app
import lime_test.db
import lime_type
import lime_event_handler.worker
import kombu
import pytest
import requests
import unittest.mock


@pytest.fixture
def limetypes():
    """The limetypes of the core database
    You can change these, or create your own by twiddling with the YAML based
    DSL format for limetypes.
    """
    return lime_type.create_limetypes_from_dsl(dsl.dsl)


@pytest.fixture
def database(limetypes, monkeypatch):
    """An in-memory empty Lime database with the core database limetypes"""
    database = lime_test.db.create_database_with_limetypes(monkeypatch,
                                                           limetypes=limetypes,
                                                           limename='myapp',
                                                           sqlname='myapp')
    return database


@pytest.fixture
def limeapp(database, limetypes, monkeypatch):
    """A Lime application with a user/coworker defined"""
    app = lime_test.app.create_app(monkeypatch, database, limetypes)
    user = lime_test.db.create_and_add_user(database=database,
                                            fullname='Kenny Starfighter',
                                            username='kenny',
                                            password='kenny')
    app.unit_of_work()

    # TODO: Make it possible to create a coworker with this hack
    coworker = app.limetypes.coworker(
        firstname='Kenny',
        lastname='Starfighter',
        name='Kenny Starfighter',
        username=user.id,
        _from_row=True
    )

    uow = app.unit_of_work()
    idx = uow.add(coworker)
    res = uow.commit()

    app._coworker = res.get(idx)

    return app


@pytest.fixture
def message_queue_connection():
    """A connection to an in-memory message queue"""
    return kombu.Connection('memory://')


@pytest.fixture
def publisher(limeapp, message_queue_connection):
    """A publisher function that posts to the in-memory queue"""
    exchange = kombu.Exchange(
        'lime.{}'.format(limeapp.identifier), type='topic')
    producer = kombu.Producer(message_queue_connection, exchange)

    def publish(routing_key, body):
        producer.publish(body, routing_key)

    return publish


@pytest.fixture
def limeapp_with_events(limeapp, publisher):
    """A Lime application that will post events to the in-memory queue"""
    limeapp._publisher = publisher
    return limeapp


@pytest.fixture
def worker(limeapp, message_queue_connection):
    """A event-handler-worker with plugins loaded, connected to the
    in-memory queue"""
    worker = lime_event_handler.worker.Worker(
        connection=message_queue_connection,
        applications=[limeapp.identifier])
    config = {}
    worker.load_plugins(config=config)
    worker.step()
    return worker


@pytest.fixture
def acme_company(limeapp):
    """A company that gets added to `limeapp`"""
    uow = limeapp.unit_of_work()
    acme = limeapp.limetypes.company(name='Acme Inc.')
    acme_idx = uow.add(acme)
    res = uow.commit()
    return res.get(acme_idx)


def test_calls_external_api_on_company_rename(
        limeapp_with_events, worker, acme_company, monkeypatch):
    monkeypatch.setattr('requests.post', unittest.mock.MagicMock())

    message = {
        'deal': {
            'id': 1001,
            'name': 'a deal',
            'value': 10000
        },
        'company': {
            'id': 1001,
            'name': 'Acme Inc.'
        }
    }

    limeapp_with_events.publish(identifier='hello-world.deal.created',
                                message=message)
    worker.step()

    requests.post.assert_called_once_with(
        'https://some.api/company_renamed',
        json={'old_name': 'Acme Inc.', 'new_name': 'Updated acme'})
